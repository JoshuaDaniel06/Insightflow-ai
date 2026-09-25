import re


FORBIDDEN_KEYWORDS = [
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "truncate",
    "create",
    "replace",
    "grant",
    "revoke"
]


def validate_sql(sql):
    """
    Allow only safe SELECT queries.
    """

    if not sql or not sql.strip():
        return False, "SQL query is empty."

    sql = sql.strip()

    # Must start with SELECT
    if not re.match(r"^select\b", sql, re.IGNORECASE):
        return False, "Only SELECT queries are allowed."

    # Remove trailing semicolon for checking
    normalized_sql = sql.rstrip(";").strip().lower()

    # Check dangerous SQL keywords
    for keyword in FORBIDDEN_KEYWORDS:
        pattern = rf"\b{keyword}\b"

        if re.search(pattern, normalized_sql):
            return False, f"Forbidden SQL operation detected: {keyword.upper()}"

    # Prevent multiple SQL statements
    if ";" in normalized_sql:
        return False, "Multiple SQL statements are not allowed."

    return True, "SQL query is safe."


if __name__ == "__main__":

    test_queries = [
        "SELECT * FROM customers;",
        "SELECT COUNT(*) FROM customers;",
        "DELETE FROM customers;",
        "UPDATE customers SET age = 30;",
        "DROP TABLE customers;",
        "INSERT INTO customers VALUES ('C011', 'Test');"
    ]

    for query in test_queries:

        valid, message = validate_sql(query)

        print("\nSQL:")
        print(query)

        if valid:
            print("✅ ALLOWED:", message)
        else:
            print("❌ BLOCKED:", message)