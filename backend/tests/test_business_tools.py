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

def test_calculate_total(sample_sales_df):
    res = calculate_total(sample_sales_df, column="Revenue")
    assert res["status"] == "success"
    assert res["total"] == 4765.0

def test_calculate_average(sample_sales_df):
    res = calculate_average(sample_sales_df, column="Profit")
    assert res["status"] == "success"
    # sum = 300 + 70 + 150 - 20 + 45 + 12 + 450 + 90 = 1097. Avg = 1097 / 8 = 137.12
    assert abs(res["average"] - 137.12) < 0.1

def test_group_by_analysis(sample_sales_df):
    res = group_by_analysis(
        df=sample_sales_df,
        group_by_column="Category",
        metric_column="Revenue",
        aggregation="sum",
        sort_descending=True
    )
    assert res["status"] == "success"
    assert res["total_groups"] == 3
    # Technology should be top group: 1200+350+1500+400 = 3450
    top_group = res["results"][0]
    assert top_group["group"] == "Technology"
    assert top_group["value"] == 3450.0

def test_compare_categories(sample_sales_df):
    res = compare_categories(
        df=sample_sales_df,
        category_column="Region",
        metric_column="Revenue"
    )
    assert res["status"] == "success"
    assert res["categories_count"] == 4
    # West has highest revenue: 1200 + 850 + 1500 = 3550
    assert res["comparisons"][0]["category"] == "West"
    assert res["comparisons"][0]["sum"] == 3550.0

def test_identify_top_performers(sample_sales_df):
    res = identify_top_performers(sample_sales_df, entity_column="Category", metric_column="Revenue", limit=2)
    assert res["status"] == "success"
    assert len(res["results"]) == 2
    assert res["results"][0]["group"] == "Technology"

def test_identify_bottom_performers(sample_sales_df):
    res = identify_bottom_performers(sample_sales_df, entity_column="Category", metric_column="Revenue", limit=1)
    assert res["status"] == "success"
    assert len(res["results"]) == 1
    # Office supplies lowest: 220 + 55 = 275
    assert res["results"][0]["group"] == "Office Supplies"

def test_detect_outliers(sample_df_with_issues):
    res = detect_outliers(sample_df_with_issues, column="Col_C", method="iqr")
    assert res["status"] == "success"
    assert res["outlier_count"] >= 1
    assert 1000.0 in res["sample_outliers"]
