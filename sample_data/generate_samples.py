import csv
import random
from datetime import datetime, timedelta

random.seed(42)

# 1. Generate ecommerce_sales.csv
ecommerce_file = "sample_data/ecommerce_sales.csv"
categories = {
    "Technology": [
        ("Smart Laptop Pro", 1200.0, 0.15),
        ("Wireless Noise-Cancelling Headphones", 180.0, 0.25),
        ("Ultra HD 4K Monitor", 350.0, 0.20),
        ("Mechanical Gaming Keyboard", 95.0, 0.30),
        ("Ergonomic Vertical Mouse", 45.0, 0.35),
        ("USB-C Multiport Dock", 75.0, 0.28)
    ],
    "Office Supplies": [
        ("Standing Desk Converter", 220.0, 0.18),
        ("Ergonomic Office Chair", 310.0, 0.22),
        ("Thermal Label Printer", 140.0, 0.20),
        ("Heavy-Duty Paper Shredder", 85.0, 0.15),
        ("Dry Erase Whiteboard 36x24", 55.0, 0.25),
        ("Gel Pens Pack (24ct)", 18.0, 0.40)
    ],
    "Furniture": [
        ("Executive Leather Chair", 450.0, 0.12),
        ("Solid Oak Conference Table", 850.0, 0.10),
        ("Modular Bookshelf", 190.0, 0.20),
        ("Adjustable LED Floor Lamp", 65.0, 0.30),
        ("Filing Cabinet 3-Drawer", 130.0, 0.18)
    ],
    "Industrial": [
        ("Heavy Duty Storage Rack", 280.0, 0.15),
        ("Digital Caliper Stainless", 40.0, 0.35),
        ("Laser Distance Meter", 90.0, 0.25),
        ("Industrial Grade Extension Cord", 35.0, 0.30)
    ]
}

regions = ["North", "South", "East", "West"]
segments = ["Consumer", "Corporate", "Small Business"]
start_date = datetime(2025, 1, 1)

with open(ecommerce_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Order_ID", "Order_Date", "Product", "Category", "Region",
        "Quantity", "Unit_Price", "Revenue", "Discount_Rate", "Profit", "Customer_Segment"
    ])
    
    for i in range(1, 1201):
        order_id = f"ORD-{2025000 + i}"
        days_offset = random.randint(0, 364)
        order_date = (start_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")
        
        # Introduce a few realistic missing category records (5 out of 1200)
        category_name = random.choice(list(categories.keys()))
        product_info = random.choice(categories[category_name])
        product_name = product_info[0]
        base_price = product_info[1]
        profit_margin = product_info[2]
        
        # Occasional missing values for data quality testing
        if i in [14, 88, 305]:
            category_val = ""
        else:
            category_val = category_name
            
        region = random.choice(regions)
        # Weight West & East higher for realistic regional variance
        if random.random() < 0.4:
            region = "West"
        elif random.random() < 0.3:
            region = "East"
            
        qty = random.choices([1, 2, 3, 4, 5, 8, 10], weights=[35, 25, 18, 10, 7, 3, 2])[0]
        unit_price = round(base_price * random.uniform(0.95, 1.05), 2)
        discount = round(random.choice([0.0, 0.05, 0.10, 0.15, 0.20]), 2)
        revenue = round(qty * unit_price * (1.0 - discount), 2)
        profit = round(revenue * profit_margin - (qty * unit_price * discount * 0.5), 2)
        
        segment = random.choice(segments)
        if i in [52, 412]:
            segment = "" # missing segment
            
        writer.writerow([
            order_id, order_date, product_name, category_val, region,
            qty, unit_price, revenue, discount, profit, segment
        ])

# 2. Generate supermarket_sales.csv
supermarket_file = "sample_data/supermarket_sales.csv"
branches = {
    "A": "Yangon",
    "B": "Mandalay",
    "C": "Naypyitaw"
}
product_lines = [
    "Health and beauty", "Electronic accessories", "Home and lifestyle",
    "Sports and travel", "Food and beverages", "Fashion accessories"
]
customer_types = ["Member", "Normal"]
genders = ["Female", "Male"]
payments = ["Ewallet", "Cash", "Credit card"]

with open(supermarket_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Invoice_ID", "Branch", "City", "Customer_Type", "Gender",
        "Product_Line", "Unit_Price", "Quantity", "Tax_5_Percent", "Total",
        "Date", "Time", "Payment_Method", "Rating"
    ])
    
    for i in range(1, 1001):
        invoice_id = f"INV-{100000 + i}"
        branch = random.choice(list(branches.keys()))
        city = branches[branch]
        cust_type = random.choice(customer_types)
        gender = random.choice(genders)
        prod_line = random.choice(product_lines)
        unit_price = round(random.uniform(10.0, 99.0), 2)
        qty = random.randint(1, 10)
        cogs = round(unit_price * qty, 2)
        tax = round(cogs * 0.05, 2)
        total = round(cogs + tax, 2)
        
        day_offset = random.randint(0, 90)
        dt = (datetime(2025, 1, 1) + timedelta(days=day_offset)).strftime("%Y-%m-%d")
        hour = random.randint(10, 20)
        minute = random.randint(0, 59)
        time_str = f"{hour:02d}:{minute:02d}"
        payment = random.choice(payments)
        rating = round(random.uniform(4.0, 10.0), 1)
        
        # introduce 2 null ratings for missing value detection
        if i in [23, 115]:
            rating_str = ""
        else:
            rating_str = str(rating)
            
        writer.writerow([
            invoice_id, branch, city, cust_type, gender,
            prod_line, unit_price, qty, tax, total,
            dt, time_str, payment, rating_str
        ])

print("Sample datasets generated successfully!")
