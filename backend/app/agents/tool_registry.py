from typing import Callable, Any, Dict, List, Optional
import inspect
import pandas as pd
from pydantic import BaseModel, ValidationError

# Import all tool functions
from app.tools.inspection import (
    get_dataset_overview,
    get_column_information,
    get_data_types,
    get_missing_values,
    get_duplicate_records,
    get_unique_values
)
from app.tools.statistics import (
    calculate_mean,
    calculate_median,
    calculate_mode,
    calculate_standard_deviation,
    calculate_min_max,
    calculate_correlation
)
from app.tools.business_analysis import (
    calculate_total,
    calculate_average,
    group_by_analysis,
    compare_categories,
    calculate_percentage_change,
    identify_top_performers,
    identify_bottom_performers,
    detect_outliers
)
from app.tools.visualization import (
    generate_bar_chart,
    generate_line_chart,
    generate_pie_chart,
    generate_histogram,
    generate_scatter_plot
)
from app.tools.reporting import (
    generate_summary_report,
    generate_data_quality_report
)

# Tool argument schemas for validation
from app.models.tool_schemas import (
    ColumnSpecificArgs,
    UniqueValuesArgs,
    CorrelationArgs,
    GroupByArgs,
    CompareCategoriesArgs,
    PercentageChangeArgs,
    PerformersArgs,
    DetectOutliersArgs,
    BarChartArgs,
    LineChartArgs,
    PieChartArgs,
    HistogramArgs,
    ScatterPlotArgs
)

# Map tool names to their argument validation model (if any arguments required)
TOOL_ARG_MODELS: Dict[str, Optional[type[BaseModel]]] = {
    # Inspection
    "get_dataset_overview": None,
    "get_column_information": None, # Column is optional
    "get_data_types": None,
    "get_missing_values": None,
    "get_duplicate_records": None,
    "get_unique_values": UniqueValuesArgs,
    
    # Statistics
    "calculate_mean": ColumnSpecificArgs,
    "calculate_median": ColumnSpecificArgs,
    "calculate_mode": ColumnSpecificArgs,
    "calculate_standard_deviation": ColumnSpecificArgs,
    "calculate_min_max": ColumnSpecificArgs,
    "calculate_correlation": CorrelationArgs,
    
    # Business Analysis
    "calculate_total": ColumnSpecificArgs,
    "calculate_average": ColumnSpecificArgs,
    "group_by_analysis": GroupByArgs,
    "compare_categories": CompareCategoriesArgs,
    "calculate_percentage_change": PercentageChangeArgs,
    "identify_top_performers": PerformersArgs,
    "identify_bottom_performers": PerformersArgs,
    "detect_outliers": DetectOutliersArgs,
    
    # Visualization
    "generate_bar_chart": BarChartArgs,
    "generate_line_chart": LineChartArgs,
    "generate_pie_chart": PieChartArgs,
    "generate_histogram": HistogramArgs,
    "generate_scatter_plot": ScatterPlotArgs,
    
    # Reporting
    "generate_summary_report": None,
    "generate_data_quality_report": None
}

TOOL_CALLABLES: Dict[str, Callable] = {
    "get_dataset_overview": get_dataset_overview,
    "get_column_information": get_column_information,
    "get_data_types": get_data_types,
    "get_missing_values": get_missing_values,
    "get_duplicate_records": get_duplicate_records,
    "get_unique_values": get_unique_values,
    "calculate_mean": calculate_mean,
    "calculate_median": calculate_median,
    "calculate_mode": calculate_mode,
    "calculate_standard_deviation": calculate_standard_deviation,
    "calculate_min_max": calculate_min_max,
    "calculate_correlation": calculate_correlation,
    "calculate_total": calculate_total,
    "calculate_average": calculate_average,
    "group_by_analysis": group_by_analysis,
    "compare_categories": compare_categories,
    "calculate_percentage_change": calculate_percentage_change,
    "identify_top_performers": identify_top_performers,
    "identify_bottom_performers": identify_bottom_performers,
    "detect_outliers": detect_outliers,
    "generate_bar_chart": generate_bar_chart,
    "generate_line_chart": generate_line_chart,
    "generate_pie_chart": generate_pie_chart,
    "generate_histogram": generate_histogram,
    "generate_scatter_plot": generate_scatter_plot,
    "generate_summary_report": generate_summary_report,
    "generate_data_quality_report": generate_data_quality_report
}

TOOL_DESCRIPTIONS: Dict[str, str] = {
    "get_dataset_overview": "Inspect dataset shape, total cells, missing cells percentage, and duplicate counts.",
    "get_column_information": "Inspect detailed metadata (data types, null count, unique count, sample values) for all columns or a single column.",
    "get_data_types": "Get the detected data types for all columns in the dataset.",
    "get_missing_values": "Analyze missing or null records across all columns and percentage missing.",
    "get_duplicate_records": "Identify duplicate rows and view sample duplicate rows.",
    "get_unique_values": "Retrieve distinct unique values and their frequencies for a column.",
    "calculate_mean": "Calculate the arithmetic mean of a numeric column.",
    "calculate_median": "Calculate the median (50th percentile) of a numeric column.",
    "calculate_mode": "Find the most frequent value(s) in a column.",
    "calculate_standard_deviation": "Calculate sample standard deviation, variance, and coefficient of variation of a numeric column.",
    "calculate_min_max": "Calculate minimum, maximum, range, and interquartile ranges of a numeric column.",
    "calculate_correlation": "Calculate Pearson correlation coefficient between two numeric columns.",
    "calculate_total": "Calculate the sum total of a numeric column.",
    "calculate_average": "Calculate the average of a numeric column.",
    "group_by_analysis": "Group dataset by a categorical column and aggregate a numeric column (sum, mean, count, min, max, median).",
    "compare_categories": "Compare numerical metrics across specific categories or all categories.",
    "calculate_percentage_change": "Calculate period-over-period percentage change across dates or sequential records.",
    "identify_top_performers": "Rank top performing entities (e.g. Products, Regions, Branches) by a metric.",
    "identify_bottom_performers": "Rank lowest performing entities by a metric.",
    "detect_outliers": "Detect statistical outliers in a numeric column using IQR or Z-score.",
    "generate_bar_chart": "Generate a bar chart comparing categories by a metric.",
    "generate_line_chart": "Generate a line chart showing a metric over time or sequential ordering.",
    "generate_pie_chart": "Generate a pie/donut chart showing share/proportions of a metric across categories.",
    "generate_histogram": "Generate a histogram showing the distribution of a numeric column.",
    "generate_scatter_plot": "Generate a scatter plot showing relationship between two numeric columns.",
    "generate_summary_report": "Generate an executive statistical and business summary report across all attributes.",
    "generate_data_quality_report": "Generate a data quality score, hygiene issues, missing values, and recommendations."
}

def get_gemini_tool_declarations() -> List[Dict[str, Any]]:
    """
    Generate JSON Schema function declarations for Gemini API.
    Compatible with google.genai.types.FunctionDeclaration.
    """
    declarations = []
    for tool_name, model_cls in TOOL_ARG_MODELS.items():
        doc = TOOL_DESCRIPTIONS.get(tool_name, "")
        if model_cls:
            schema = model_cls.model_json_schema()
            # Clean up pydantic schema for Gemini function calling
            parameters = {
                "type": "OBJECT",
                "properties": {},
                "required": schema.get("required", [])
            }
            for prop_name, prop_data in schema.get("properties", {}).items():
                p_type = prop_data.get("type", "string").upper()
                if p_type == "INTEGER":
                    p_type = "INTEGER"
                elif p_type == "NUMBER":
                    p_type = "NUMBER"
                elif p_type == "BOOLEAN":
                    p_type = "BOOLEAN"
                elif p_type == "ARRAY":
                    p_type = "ARRAY"
                else:
                    p_type = "STRING"
                    
                prop_dict: Dict[str, Any] = {
                    "type": p_type,
                    "description": prop_data.get("description", "")
                }
                if "enum" in prop_data:
                    prop_dict["enum"] = prop_data["enum"]
                parameters["properties"][prop_name] = prop_dict
        else:
            parameters = {
                "type": "OBJECT",
                "properties": {},
                "required": []
            }
            if tool_name == "get_column_information":
                parameters["properties"]["column"] = {
                    "type": "STRING",
                    "description": "Optional column name to inspect. Omit to inspect all columns."
                }
                
        declarations.append({
            "name": tool_name,
            "description": doc,
            "parameters": parameters
        })
    return declarations

def execute_tool(tool_name: str, args: Dict[str, Any], df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate arguments with Pydantic and execute tool function against the DataFrame.
    Guarantees structured dict response and handles exceptions gracefully.
    """
    if tool_name not in TOOL_CALLABLES:
        return {
            "status": "error",
            "message": f"Unknown tool: '{tool_name}'. Available tools: {list(TOOL_CALLABLES.keys())}"
        }
        
    func = TOOL_CALLABLES[tool_name]
    arg_model = TOOL_ARG_MODELS.get(tool_name)
    
    # Validate arguments with Pydantic model if defined
    validated_args = {}
    if arg_model:
        try:
            model_instance = arg_model(**args)
            validated_args = model_instance.model_dump()
        except ValidationError as ve:
            errors = [f"{e['loc'][0]}: {e['msg']}" for e in ve.errors()]
            return {
                "status": "error",
                "message": f"Argument validation failed for tool '{tool_name}': {', '.join(errors)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to parse arguments for '{tool_name}': {str(e)}"
            }
    else:
        # No model or optional arguments
        validated_args = args or {}
        
    # Execute tool with DataFrame injected
    try:
        result = func(df=df, **validated_args)
        return result
    except TypeError as te:
        # In case function signature argument mismatch
        try:
            # Try passing only args that function accepts
            sig = inspect.signature(func)
            filtered = {k: v for k, v in validated_args.items() if k in sig.parameters}
            return func(df=df, **filtered)
        except Exception as inner_e:
            return {
                "status": "error",
                "message": f"Execution error in tool '{tool_name}': {str(inner_e)}"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Exception while executing tool '{tool_name}': {str(e)}"
        }
