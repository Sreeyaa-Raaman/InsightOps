from app.tools.statistics import (
    calculate_mean,
    calculate_median,
    calculate_mode,
    calculate_standard_deviation,
    calculate_min_max,
    calculate_correlation
)

def test_calculate_mean(sample_sales_df):
    res = calculate_mean(sample_sales_df, column="Revenue")
    assert res["status"] == "success"
    # sum = 1200+350+850+190+220+55+1500+400 = 4765. Mean = 4765/8 = 595.625
    assert res["mean"] == 595.625
    assert res["count"] == 8

def test_calculate_mean_invalid_column(sample_sales_df):
    res = calculate_mean(sample_sales_df, column="NonExistentColumn")
    assert res["status"] == "error"
    assert "not found" in res["message"]

def test_calculate_mean_non_numeric(sample_sales_df):
    res = calculate_mean(sample_sales_df, column="Region")
    assert res["status"] == "error"
    assert "non-numeric" in res["message"]

def test_calculate_median(sample_sales_df):
    res = calculate_median(sample_sales_df, column="Quantity")
    assert res["status"] == "success"
    # Quantities: [1, 1, 2, 2, 2, 3, 4, 5] -> median is 2.0
    assert res["median"] == 2.0

def test_calculate_mode(sample_sales_df):
    res = calculate_mode(sample_sales_df, column="Region")
    assert res["status"] == "success"
    assert "West" in res["mode_values"]
    assert res["frequency"] == 3

def test_calculate_standard_deviation(sample_sales_df):
    res = calculate_standard_deviation(sample_sales_df, column="Revenue")
    assert res["status"] == "success"
    assert res["standard_deviation"] > 0
    assert res["sample_size"] == 8

def test_calculate_min_max(sample_sales_df):
    res = calculate_min_max(sample_sales_df, column="Revenue")
    assert res["status"] == "success"
    assert res["min"] == 55.0
    assert res["max"] == 1500.0
    assert res["range"] == 1445.0

def test_calculate_correlation(sample_sales_df):
    res = calculate_correlation(sample_sales_df, column1="Revenue", column2="Profit")
    assert res["status"] == "success"
    # High positive correlation between revenue and profit in sample
    assert res["correlation_coefficient"] > 0.8
    assert res["direction"] == "positive"
