from app.tools.visualization import (
    generate_bar_chart,
    generate_line_chart,
    generate_pie_chart,
    generate_histogram,
    generate_scatter_plot
)

def test_generate_bar_chart(sample_sales_df):
    res = generate_bar_chart(
        df=sample_sales_df,
        x_column="Category",
        y_column="Revenue",
        title="Revenue by Category"
    )
    assert res["status"] == "success"
    cfg = res["chart_config"]
    assert cfg["chart_type"] == "bar"
    assert cfg["x_key"] == "Category"
    assert "Revenue" in cfg["y_keys"]
    assert len(cfg["data"]) == 3

def test_generate_pie_chart(sample_sales_df):
    res = generate_pie_chart(
        df=sample_sales_df,
        category_column="Region",
        metric_column="Revenue",
        title="Revenue by Region"
    )
    assert res["status"] == "success"
    cfg = res["chart_config"]
    assert cfg["chart_type"] == "pie"
    assert len(cfg["data"]) == 4

def test_generate_histogram(sample_sales_df):
    res = generate_histogram(
        df=sample_sales_df,
        column="Revenue",
        title="Revenue Distribution",
        bins=4
    )
    assert res["status"] == "success"
    cfg = res["chart_config"]
    assert cfg["chart_type"] == "bar"
    assert len(cfg["data"]) == 4

def test_generate_scatter_plot(sample_sales_df):
    res = generate_scatter_plot(
        df=sample_sales_df,
        x_column="Quantity",
        y_column="Revenue",
        title="Revenue vs Quantity"
    )
    assert res["status"] == "success"
    cfg = res["chart_config"]
    assert cfg["chart_type"] == "scatter"
    assert len(cfg["data"]) == 8
