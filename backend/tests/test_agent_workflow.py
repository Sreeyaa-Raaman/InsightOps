from unittest.mock import MagicMock
from app.agents.tool_registry import execute_tool, get_gemini_tool_declarations
from app.agents.memory import ConversationMemory
from app.agents.agent_executor import AgentExecutor
from google.genai import types

def test_tool_declarations_valid():
    declarations = get_gemini_tool_declarations()
    assert len(declarations) == 27
    names = [d["name"] for d in declarations]
    assert "get_dataset_overview" in names
    assert "calculate_mean" in names
    assert "group_by_analysis" in names
    assert "generate_bar_chart" in names

def test_execute_tool_success(sample_sales_df):
    res = execute_tool("calculate_total", {"column": "Revenue"}, sample_sales_df)
    assert res["status"] == "success"
    assert res["total"] == 4765.0

def test_execute_tool_validation_error(sample_sales_df):
    # Missing required argument 'column'
    res = execute_tool("calculate_mean", {}, sample_sales_df)
    assert res["status"] == "error"
    assert "validation failed" in res["message"]

def test_conversation_memory_lifecycle():
    session_id = ConversationMemory.create_session(title="Unit Test Session")
    assert session_id is not None
    
    msg_id = ConversationMemory.save_message(
        session_id=session_id,
        role="user",
        content="What is the top product?"
    )
    assert msg_id is not None
    
    history = ConversationMemory.get_conversation_history(session_id)
    assert len(history) == 1
    assert history[0]["content"] == "What is the top product?"

def test_agent_executor_mock_workflow(sample_sales_df):
    # Mock the Gemini client to return a function call, then text
    mock_llm = MagicMock()
    mock_client = MagicMock()
    mock_llm.get_client.return_value = mock_client
    mock_llm.is_configured.return_value = True
    mock_llm.model = "gemini-2.5-flash"
    
    # 1st response: calls calculate_total(column='Revenue')
    fc_part = types.Part(function_call=types.FunctionCall(
        name="calculate_total",
        args={"column": "Revenue"}
    ))
    resp1 = MagicMock()
    resp1.candidates = [
        types.Candidate(content=types.Content(role="model", parts=[fc_part]))
    ]
    
    # 2nd response: final model answer
    text_part = types.Part(text="The total revenue across all orders is $4,765.00.\n- Technology generated the most revenue.")
    resp2 = MagicMock()
    resp2.candidates = [
        types.Candidate(content=types.Content(role="model", parts=[text_part]))
    ]
    
    mock_client.models.generate_content.side_effect = [resp1, resp2]
    
    executor = AgentExecutor(llm_client=mock_llm)
    dataset_meta = {
        "original_name": "test_sales.csv",
        "row_count": len(sample_sales_df),
        "column_count": len(sample_sales_df.columns),
        "columns": [{"name": c, "dtype": str(sample_sales_df[c].dtype)} for c in sample_sales_df.columns]
    }
    
    session_id = ConversationMemory.create_session(title="Mock Test Session")
    result = executor.run_analysis(
        session_id=session_id,
        user_message="What is the total revenue?",
        df=sample_sales_df,
        dataset_meta=dataset_meta
    )
    
    assert "4,765.00" in result.answer
    assert len(result.execution_trace) == 1
    assert result.execution_trace[0].tool_name == "calculate_total"
    assert result.execution_trace[0].status == "success"
    assert "total_Revenue" in result.numerical_results
    assert result.numerical_results["total_Revenue"] == 4765.0
