import pandas as pd
from sqlalchemy import create_engine


# Load dataset
df = pd.read_csv(
    "data/ajio_sales.csv",
    encoding="latin1"
)


# Clean column names
df.columns = (
    df.columns
    .str.strip()
    .str.replace(" ", "_")
    .str.replace("(", "", regex=False)
    .str.replace(")", "", regex=False)
    .str.replace(".", "", regex=False)
    .str.replace("/", "_", regex=False)
)


# Clean Original Price column
df["Original_Price_in_Rs"] = (
    df["Original_Price_in_Rs"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.replace("₹", "", regex=False)
    .str.replace("Rs.", "", regex=False)
    .str.strip()
)


# Clean Discount Price column
df["Discount_Price_in_Rs"] = (
    df["Discount_Price_in_Rs"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.replace("₹", "", regex=False)
    .str.replace("Rs.", "", regex=False)
    .str.strip()
)


# Convert to numeric
df["Original_Price_in_Rs"] = pd.to_numeric(
    df["Original_Price_in_Rs"],
    errors="coerce"
)

df["Discount_Price_in_Rs"] = pd.to_numeric(
    df["Discount_Price_in_Rs"],
    errors="coerce"
)


# Remove rows with invalid prices
df = df.dropna(
    subset=[
        "Original_Price_in_Rs",
        "Discount_Price_in_Rs"
    ]
)


# Convert to integer
df["Original_Price_in_Rs"] = (
    df["Original_Price_in_Rs"]
    .astype(int)
)

df["Discount_Price_in_Rs"] = (
    df["Discount_Price_in_Rs"]
    .astype(int)
)


# Create SQLite database
engine = create_engine(
    "sqlite:///database/sales.db"
)


# Save table
df.to_sql(
    "products",
    engine,
    if_exists="replace",
    index=False
)


print("Database created successfully!")
print(f"Total rows loaded: {len(df)}")