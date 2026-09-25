import pandas as pd
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()


INPUT_FILE = "data/clean_customers.csv"

df = pd.read_csv(INPUT_FILE)

print("=" * 50)
print("MYSQL DATA LOADING")
print("=" * 50)

print(f"\nCleaned records found: {len(df)}")


connection = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE")
)

cursor = connection.cursor()

print("MySQL connection successful!")


cursor.execute("TRUNCATE TABLE customers")

print("Existing customer data cleared.")


insert_query = """
INSERT INTO customers
(
    customer_id,
    name,
    age,
    city,
    email,
    total_purchase
)
VALUES (%s, %s, %s, %s, %s, %s)
"""


for _, row in df.iterrows():

    cursor.execute(
        insert_query,
        (
            row["customer_id"],
            row["name"],
            None if pd.isna(row["age"]) else int(row["age"]),
            row["city"],
            None if pd.isna(row["email"]) else row["email"],
            float(row["total_purchase"])
        )
    )


connection.commit()

print(
    f"{len(df)} customer records loaded into MySQL."
)


cursor.execute(
    "SELECT COUNT(*) FROM customers"
)

count = cursor.fetchone()[0]

print(f"MySQL customer count: {count}")


cursor.close()
connection.close()

print("\nMySQL connection closed.")

print("\nData loading completed successfully!")