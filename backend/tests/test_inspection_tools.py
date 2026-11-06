from app.tools.inspection import (
    get_dataset_overview,
    get_column_information,
    get_data_types,
    get_missing_values,
    get_duplicate_records,
    get_unique_values
)

def test_get_dataset_overview(sample_sales_df):
    res = get_dataset_overview(sample_sales_df)
    assert res["status"] == "success"
    assert res["row_count"] == 8
    assert res["column_count"] == 7
    assert res["missing_cells"] == 0
    assert "Revenue" in res["columns"]

def test_get_column_information(sample_sales_df):
    res = get_column_information(sample_sales_df, column="Revenue")
    assert res["status"] == "success"
    assert len(res["column_details"]) == 1
    col_info = res["column_details"][0]
    assert col_info["name"] == "Revenue"
    assert col_info["non_null_count"] == 8
    assert col_info["null_count"] == 0

def test_get_data_types(sample_sales_df):
    res = get_data_types(sample_sales_df)
    assert res["status"] == "success"
    assert "Revenue" in res["column_data_types"]
    assert "Category" in res["column_data_types"]

def test_get_missing_values(sample_df_with_issues):
    res = get_missing_values(sample_df_with_issues)
    assert res["status"] == "success"
    assert res["has_missing_values"] is True
    assert "Col_A" in res["missing_by_column"]
    assert res["missing_by_column"]["Col_A"]["missing_count"] == 1

def test_get_duplicate_records(sample_df_with_issues):
    res = get_duplicate_records(sample_df_with_issues)
    assert res["status"] == "success"
    assert "duplicate_count" in res

def test_get_unique_values(sample_sales_df):
    res = get_unique_values(sample_sales_df, column="Region")
    assert res["status"] == "success"
    assert res["column"] == "Region"
    assert res["total_unique_values"] == 4
    # West should have count 3
    west_item = next(item for item in res["frequencies"] if item["value"] == "West")
    assert west_item["count"] == 3
