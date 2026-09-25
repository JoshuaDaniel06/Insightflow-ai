from google import genai
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_sql(question, schema):

    schema_text = json.dumps(
        schema,
        indent=2
    )

    prompt = f"""
You are an expert MySQL SQL query generator for a customer
data analytics system.

Convert the user's natural-language question into ONE safe
MySQL SELECT query.

DATABASE SCHEMA:
{schema_text}

USER QUESTION:
{question}

CUSTOMER BUSINESS RULES:

Customer segments are defined as:

Low Value:
total_purchase < 5000

Regular:
total_purchase >= 5000
AND total_purchase < 10000

Premium:
total_purchase >= 10000
AND total_purchase < 15000

High Value:
total_purchase >= 15000

IMPORTANT:

When the user asks about:

- high-value customers
- high value customers
- valuable customers
- most valuable customers
- top customers
- premium customers
- customers who spent the most
- highest spending customers

use the total_purchase column to determine customer value.

For "high-value customers", use:

total_purchase >= 15000

For "premium customers", use:

total_purchase >= 10000
AND total_purchase < 15000

For "top customers" or "most valuable customers",
sort by total_purchase DESC.

RULES:

1. Generate ONLY one SELECT query.

2. Use ONLY tables and columns present in the provided schema.

3. Never invent tables or columns.

4. Never use SELECT *.

5. Select only the columns required to answer the question.

6. Use meaningful aliases for calculated values.

7. Use correct MySQL syntax.

8. Never generate INSERT, UPDATE, DELETE, DROP, ALTER,
   TRUNCATE, CREATE, GRANT, REVOKE or any other modifying
   statement.

9. Never generate multiple SQL statements.

10. Do not explain the SQL.

11. Do not use markdown code blocks.

12. Return ONLY the SQL query.

13. If the question asks to identify customers based on
    purchase value, include customer_id, name and
    total_purchase when those columns are available.

14. If the question asks for a count, use COUNT(*).

15. If the question asks for an average, use AVG().

16. If the question asks for a total, use SUM().

17. If the question asks for the highest or lowest value,
    use ORDER BY with LIMIT 1 when appropriate.

18. For ranking questions such as top 3, use ORDER BY
    total_purchase DESC with LIMIT 3.

19. Do not select columns that are unavailable in the
    provided schema.

Examples:

For highest spending customer:

SELECT customer_id, name, total_purchase
FROM customers
ORDER BY total_purchase DESC
LIMIT 1;

For average purchase:

SELECT AVG(total_purchase) AS average_purchase
FROM customers;

For total purchase:

SELECT SUM(total_purchase) AS total_purchase
FROM customers;

For customer count:

SELECT COUNT(*) AS customer_count
FROM customers;

For top 3 customers:

SELECT customer_id, name, total_purchase
FROM customers
ORDER BY total_purchase DESC
LIMIT 3;

For high-value customers:

SELECT customer_id, name, total_purchase
FROM customers
WHERE total_purchase >= 15000
ORDER BY total_purchase DESC;

For premium customers:

SELECT customer_id, name, total_purchase
FROM customers
WHERE total_purchase >= 10000
AND total_purchase < 15000
ORDER BY total_purchase DESC;

For city totals:

SELECT city, SUM(total_purchase) AS total_purchase
FROM customers
GROUP BY city;

For highest city total:

SELECT city, SUM(total_purchase) AS total_purchase
FROM customers
GROUP BY city
ORDER BY total_purchase DESC
LIMIT 1;

Generate the SQL now.
"""

    response = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    sql = response.output_text.strip()

    # Remove markdown if Gemini accidentally adds it
    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")

    # Remove unnecessary whitespace
    sql = sql.strip()

    return sql


if __name__ == "__main__":

    from schema_inspector import get_database_schema

    schema = get_database_schema()

    print("\nSQL GENERATOR")
    print("================")
    print("Type 'exit' to stop.")

    while True:

        question = input("\nAsk a database question: ")

        if question.lower().strip() == "exit":
            print("\nExiting...")
            break

        try:

            sql = generate_sql(
                question,
                schema
            )

            print("\nGENERATED SQL")
            print("=============")
            print(sql)

        except Exception as e:

            print("\nSQL GENERATION ERROR")
            print("====================")
            print(e)