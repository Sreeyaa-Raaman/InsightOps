import sys
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

# Ensure backend/app is importable
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.database.connection import init_db
from app.services.dataset_service import DatasetService

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    init_db()

@pytest.fixture
def sample_sales_df():
    data = {
        "Order_ID": ["ORD-1", "ORD-2", "ORD-3", "ORD-4", "ORD-5", "ORD-6", "ORD-7", "ORD-8"],
        "Category": ["Technology", "Technology", "Furniture", "Furniture", "Office Supplies", "Office Supplies", "Technology", "Technology"],
        "Region": ["West", "East", "West", "South", "East", "North", "West", "East"],
        "Revenue": [1200.0, 350.0, 850.0, 190.0, 220.0, 55.0, 1500.0, 400.0],
        "Quantity": [2, 1, 3, 2, 4, 5, 2, 1],
        "Profit": [300.0, 70.0, 150.0, -20.0, 45.0, 12.0, 450.0, 90.0],
        "Discount": [0.0, 0.1, 0.05, 0.2, 0.0, 0.15, 0.0, 0.05]
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_df_with_issues():
    data = {
        "Col_A": [10.0, 20.0, np.nan, 40.0, 50.0, 10.0],
        "Col_B": ["X", "Y", "Z", None, "X", "X"],
        "Col_C": [100.0, 105.0, 102.0, 99.0, 1000.0, 100.0], # 1000 is outlier
    }
    return pd.DataFrame(data)
