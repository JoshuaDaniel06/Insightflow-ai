import mysql.connector
from dotenv import load_dotenv
import os


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# MYSQL CONNECTION
# ============================================================

connection = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE")
)

cursor = connection.cursor()


print("=" * 60)
print("CUSTOMER DATA ANALYTICS")
print("=" * 60)


# ============================================================
# 1. TOTAL CUSTOMERS
# ============================================================

cursor.execute("""
    SELECT COUNT(*)
    FROM customers
""")

total_customers = cursor.fetchone()[0]

print("\n1. TOTAL CUSTOMERS")
print(f"Total customers: {total_customers}")


# ============================================================
# 2. TOTAL PURCHASE VALUE
# ============================================================

cursor.execute("""
    SELECT SUM(total_purchase)
    FROM customers
""")

total_purchase = cursor.fetchone()[0]

print("\n2. TOTAL PURCHASE VALUE")
print(f"Total purchase value: ₹{total_purchase:,.2f}")


# ============================================================
# 3. AVERAGE PURCHASE VALUE
# ============================================================

cursor.execute("""
    SELECT AVG(total_purchase)
    FROM customers
""")

average_purchase = cursor.fetchone()[0]

print("\n3. AVERAGE PURCHASE VALUE")
print(f"Average purchase: ₹{average_purchase:,.2f}")


# ============================================================
# 4. HIGHEST VALUE CUSTOMER
# ============================================================

cursor.execute("""
    SELECT
        customer_id,
        name,
        total_purchase
    FROM customers
    ORDER BY total_purchase DESC
    LIMIT 1
""")

top_customer = cursor.fetchone()

print("\n4. HIGHEST VALUE CUSTOMER")

print(
    f"Customer ID: {top_customer[0]}"
)

print(
    f"Name: {top_customer[1]}"
)

print(
    f"Purchase: ₹{top_customer[2]:,.2f}"
)


# ============================================================
# 5. CITY-WISE PURCHASE ANALYSIS
# ============================================================

cursor.execute("""
    SELECT
        city,
        COUNT(*) AS customer_count,
        SUM(total_purchase) AS total_sales
    FROM customers
    GROUP BY city
    ORDER BY total_sales DESC
""")

city_results = cursor.fetchall()

print("\n5. CITY-WISE PURCHASE ANALYSIS")

print(
    f"{'City':<15}"
    f"{'Customers':<12}"
    f"{'Sales':>15}"
)

print("-" * 42)

for city, customer_count, total_sales in city_results:

    print(
        f"{city:<15}"
        f"{customer_count:<12}"
        f"₹{total_sales:>13,.2f}"
    )


# ============================================================
# 6. PREMIUM CUSTOMERS
# ============================================================

cursor.execute("""
    SELECT
        customer_id,
        name,
        city,
        total_purchase
    FROM customers
    WHERE total_purchase > 10000
    ORDER BY total_purchase DESC
""")

premium_customers = cursor.fetchall()

print("\n6. PREMIUM CUSTOMERS")
print("Customers with purchase value above ₹10,000")

print(
    f"\n{'ID':<8}"
    f"{'Name':<20}"
    f"{'City':<15}"
    f"{'Purchase':>15}"
)

print("-" * 60)

for customer in premium_customers:

    print(
        f"{customer[0]:<8}"
        f"{customer[1]:<20}"
        f"{customer[2]:<15}"
        f"₹{customer[3]:>13,.2f}"
    )


# ============================================================
# 7. TOP 3 CUSTOMERS
# ============================================================

cursor.execute("""
    SELECT
        customer_id,
        name,
        total_purchase
    FROM customers
    ORDER BY total_purchase DESC
    LIMIT 3
""")

top_three = cursor.fetchall()

print("\n7. TOP 3 CUSTOMERS")

for rank, customer in enumerate(top_three, start=1):

    print(
        f"{rank}. "
        f"{customer[1]} "
        f"({customer[0]}) - "
        f"₹{customer[2]:,.2f}"
    )


# ============================================================
# 8. CUSTOMER PURCHASE SEGMENTATION
# ============================================================

cursor.execute("""
    SELECT
        CASE
            WHEN total_purchase >= 15000
                THEN 'High Value'
            WHEN total_purchase >= 10000
                THEN 'Premium'
            WHEN total_purchase >= 5000
                THEN 'Regular'
            ELSE 'Low Value'
        END AS customer_segment,

        COUNT(*) AS customer_count

    FROM customers

    GROUP BY customer_segment

    ORDER BY customer_count DESC
""")

segments = cursor.fetchall()

print("\n8. CUSTOMER SEGMENTATION")

for segment, count in segments:

    print(
        f"{segment:<15} : {count} customers"
    )


# ============================================================
# CLOSE CONNECTION
# ============================================================

cursor.close()
connection.close()

print("\n" + "=" * 60)
print("ANALYTICS COMPLETED")
print("=" * 60)