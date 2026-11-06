import time
import json
import re
from typing import Dict, Any, List, Optional
import pandas as pd
from google.genai import types

from app.config import settings
from app.agents.llm_client import GeminiClientWrapper
from app.agents.tool_registry import execute_tool, TOOL_DESCRIPTIONS
from app.agents.prompts import SYSTEM_ANALYST_PROMPT, format_dataset_context
from app.agents.memory import ConversationMemory
from app.models.schemas import StructuredAnalysisResponse, ToolExecutionTraceItem, ChartConfig

class AgentExecutor:
    def __init__(self, llm_client: Optional[GeminiClientWrapper] = None):
        self.llm = llm_client or GeminiClientWrapper()

    def run_analysis(
        self,
        session_id: str,
        user_message: str,
        df: pd.DataFrame,
        dataset_meta: Dict[str, Any]
    ) -> StructuredAnalysisResponse:
        """
        Execute multi-step tool calling agent workflow on the dataset.
        """
        if not self.llm.is_configured():
            raise ValueError(
                "Gemini API key is not configured. Please enter your Gemini API key in Settings."
            )

        client = self.llm.get_client()
        model_name = self.llm.model
        config = self.llm.build_tools_config()
        
        # Build system and context instructions
        system_instructions = (
            SYSTEM_ANALYST_PROMPT + "\n\n" + format_dataset_context(dataset_meta)
        )
        
        # Build contents turn sequence
        contents: List[types.Content] = []
        
        # Add system context as the first user turn or system instruction
        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=f"[System Instructions and Active Dataset Context]:\n{system_instructions}")]
        ))
        contents.append(types.Content(
            role="model",
            parts=[types.Part.from_text(text="Understood. I am ready to analyze the dataset using validated Python tools. I will never fabricate figures.")]
        ))
        
        # Add past conversation turns from memory
        history_turns = ConversationMemory.get_history_contents_for_gemini(session_id, max_turns=4)
        contents.extend(history_turns)
        
        # Add current user question
        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)]
        ))
        
        execution_trace: List[ToolExecutionTraceItem] = []
        collected_numerical_results: Dict[str, Any] = {}
        detected_chart_config: Optional[ChartConfig] = None
        step_count = 0
        max_steps = settings.MAX_TOOL_STEPS
        
        # Multi-step Agent Loop
        while step_count < max_steps:
            step_count += 1
            
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config
                )
            except Exception as e:
                # Catch API rate limit, quota, or network errors
                raise RuntimeError(f"Gemini API invocation error: {str(e)}")
                
            candidate = response.candidates[0] if response.candidates else None
            if not candidate or not candidate.content:
                break
                
            model_content = candidate.content
            contents.append(model_content)
            
            # Check if model requested function calls
            function_calls = []
            if model_content.parts:
                for part in model_content.parts:
                    if part.function_call:
                        function_calls.append(part.function_call)
                        
            if not function_calls:
                # No more function calls requested; model provided final text answer
                break
                
            # Execute each function call and collect responses
            response_parts = []
            for fc in function_calls:
                fn_name = fc.name
                fn_args = dict(fc.args) if fc.args else {}
                
                t_start = time.perf_counter()
                tool_result = execute_tool(fn_name, fn_args, df)
                t_elapsed_ms = round((time.perf_counter() - t_start) * 1000, 2)
                
                # Check status
                status = tool_result.get("status", "success")
                desc = TOOL_DESCRIPTIONS.get(fn_name, fn_name)
                
                # Generate human-readable trace summary
                if status == "success":
                    if "chart_config" in tool_result:
                        detected_chart_config = ChartConfig(**tool_result["chart_config"])
                        summary = f"Generated {tool_result['chart_config'].get('chart_type')} chart: '{tool_result['chart_config'].get('title')}'"
                    elif "operation" in tool_result:
                        op = tool_result["operation"]
                        if "total" in tool_result:
                            summary = f"Calculated total for '{tool_result.get('column')}': {tool_result['total']:,}"
                            collected_numerical_results[f"total_{tool_result.get('column')}"] = tool_result['total']
                        elif "mean" in tool_result:
                            summary = f"Calculated mean for '{tool_result.get('column')}': {tool_result['mean']}"
                            collected_numerical_results[f"mean_{tool_result.get('column')}"] = tool_result['mean']
                        elif "median" in tool_result:
                            summary = f"Calculated median for '{tool_result.get('column')}': {tool_result['median']}"
                            collected_numerical_results[f"median_{tool_result.get('column')}"] = tool_result['median']
                        elif "results" in tool_result and isinstance(tool_result["results"], list):
                            top_item = tool_result["results"][0] if tool_result["results"] else {}
                            summary = f"Grouped by '{tool_result.get('group_by_column')}'. Top: {top_item.get('group')} ({top_item.get('value')})"
                            collected_numerical_results[f"grouped_{tool_result.get('group_by_column')}"] = tool_result["results"]
                        elif "correlation_coefficient" in tool_result:
                            summary = f"Correlation: {tool_result['correlation_coefficient']} ({tool_result['interpretation']})"
                            collected_numerical_results["correlation"] = tool_result['correlation_coefficient']
                        elif "outlier_count" in tool_result:
                            summary = f"Detected {tool_result['outlier_count']} outliers ({tool_result['outlier_percentage']}%) in '{tool_result['column']}'"
                            collected_numerical_results["outliers"] = tool_result['outlier_count']
                        else:
                            summary = f"Completed operation '{op}' on dataset."
                    else:
                        summary = f"Successfully executed tool '{fn_name}'."
                else:
                    summary = f"Tool '{fn_name}' reported issue: {tool_result.get('message', 'Execution error')}"
                    
                execution_trace.append(ToolExecutionTraceItem(
                    tool_name=fn_name,
                    description=desc,
                    parameters=fn_args,
                    status=status,
                    summary=summary
                ))
                
                # Format response back to Gemini
                response_parts.append(
                    types.Part.from_function_response(
                        name=fn_name,
                        response={"result": tool_result}
                    )
                )
                
            contents.append(types.Content(
                role="user",
                parts=response_parts
            ))
            
        # Extract the final answer text
        final_answer_text = ""
        if contents and contents[-1].role == "model" and contents[-1].parts:
            text_parts = [p.text for p in contents[-1].parts if p.text]
            final_answer_text = "\n".join(text_parts).strip()
            
        # If model ended without explicit text or truncated, synthesize answer
        if not final_answer_text:
            if execution_trace:
                final_answer_text = "I analyzed the dataset using the following operations:\n\n"
                for tr in execution_trace:
                    final_answer_text += f"- **{tr.tool_name}**: {tr.summary}\n"
            else:
                final_answer_text = "I inspected the dataset, but could not determine a specific operation. Please refine your query."

        # Extract structured key findings and suggested follow-ups
        key_findings = self._extract_key_findings(final_answer_text, execution_trace)
        suggested_follow_ups = self._generate_follow_ups(user_message, execution_trace, dataset_meta)
        
        return StructuredAnalysisResponse(
            answer=final_answer_text,
            key_findings=key_findings,
            numerical_results=collected_numerical_results,
            execution_trace=execution_trace,
            chart_config=detected_chart_config,
            suggested_follow_ups=suggested_follow_ups
        )

    def _extract_key_findings(self, text: str, trace: List[ToolExecutionTraceItem]) -> List[str]:
        findings = []
        # Check bullet points in answer text
        lines = text.split("\n")
        for line in lines:
            line_s = line.strip()
            if line_s.startswith(("- ", "* ", "• ")) and len(line_s) > 10:
                findings.append(line_s[2:].strip().replace("**", ""))
            elif re.match(r"^\d+\.\s+", line_s) and len(line_s) > 10:
                findings.append(re.sub(r"^\d+\.\s+", "", line_s).strip().replace("**", ""))
                
        # If no bullet points found in text, use tool trace summaries
        if not findings and trace:
            findings = [t.summary for t in trace if t.status == "success"][:4]
            
        return findings[:5]

    def _generate_follow_ups(
        self,
        query: str,
        trace: List[ToolExecutionTraceItem],
        dataset_meta: Dict[str, Any]
    ) -> List[str]:
        """Suggest intelligent contextual follow-up questions."""
        q_lower = query.lower()
        cols = [c["name"] for c in dataset_meta.get("columns", [])]
        
        follow_ups = []
        
        # If question was about revenue or sales
        if any(w in q_lower for w in ["revenue", "sales", "total"]):
            follow_ups.append("How does revenue compare across different regions?")
            follow_ups.append("What are the top 5 products by total sales?")
            follow_ups.append("Detect any unusual sales fluctuations or outliers.")
            
        # If question was about products or categories
        elif any(w in q_lower for w in ["product", "category", "performer"]):
            follow_ups.append("Show the monthly trend for the top performing category.")
            follow_ups.append("Compare average profit margins across all categories.")
            follow_ups.append("Create a pie chart showing category market share.")
            
        # If question was about data quality or overview
        elif any(w in q_lower for w in ["overview", "missing", "duplicate", "quality"]):
            follow_ups.append("Generate a comprehensive data quality report.")
            follow_ups.append("Calculate correlation between all numeric metrics.")
            follow_ups.append("Which category has the highest number of records?")
            
        else:
            follow_ups.append("Identify the top five performing categories.")
            follow_ups.append("Find missing values and duplicate records.")
            follow_ups.append("Generate a summary performance report.")
            
        return follow_ups[:3]
