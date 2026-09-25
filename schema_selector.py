def select_relevant_schema(question, schema):

    question_lower = (
        question
        .lower()
        .replace("?", "")
        .replace(",", "")
        .replace("-", " ")
    )

    question_words = set(
        question_lower.split()
    )

    selected_schema = {}

    mappings = {

        # -------------------------
        # Purchase-related questions
        # -------------------------
        "purchase": ["total_purchase"],
        "purchases": ["total_purchase"],
        "spent": ["total_purchase"],
        "spending": ["total_purchase"],
        "amount": ["total_purchase"],
        "total": ["total_purchase"],
        "average": ["total_purchase"],
        "highest": ["total_purchase"],
        "lowest": ["total_purchase"],
        "most": ["total_purchase"],
        "least": ["total_purchase"],
        "top": ["total_purchase"],
        "premium": ["total_purchase"],
        "eligible": ["total_purchase"],
        "classification": ["total_purchase"],
        "segment": ["total_purchase"],

        # Business/customer-value language
        "high": ["total_purchase"],
        "value": ["total_purchase"],
        "important": ["total_purchase"],
        "valuable": ["total_purchase"],
        "revenue": ["total_purchase"],
        "income": ["total_purchase"],
        "spend": ["total_purchase"],

        # -------------------------
        # Customer-related questions
        # -------------------------
        "customer": ["customer_id", "name"],
        "customers": ["customer_id", "name"],
        "client": ["customer_id", "name"],
        "clients": ["customer_id", "name"],

        # -------------------------
        # Location-related questions
        # -------------------------
        "city": ["city"],
        "cities": ["city"],
        "chennai": ["city"],
        "madurai": ["city"],
        "coimbatore": ["city"],

        # -------------------------
        # Other fields
        # -------------------------
        "age": ["age"],
        "email": ["email"],

        # -------------------------
        # Aggregation
        # -------------------------
        "count": ["customer_id"],
        "number": ["customer_id"],
        "percentage": ["total_purchase"],
        "percent": ["total_purchase"]
    }

    for table_name, columns in schema.items():

        relevant_columns = []

        for column in columns:

            column_name = column["name"].lower()

            # Direct column-name match
            if column_name in question_words:

                if column not in relevant_columns:
                    relevant_columns.append(column)

                continue

            # Keyword mapping
            for keyword, mapped_columns in mappings.items():

                if keyword in question_words:

                    if column_name in mapped_columns:

                        if column not in relevant_columns:
                            relevant_columns.append(column)

                        break

        if relevant_columns:
            selected_schema[table_name] = relevant_columns

    # ------------------------------------------------
    # Business-value questions need purchase information
    # ------------------------------------------------
    business_value_phrases = [
        "high value",
        "high-value",
        "premium customer",
        "premium customers",
        "valuable customer",
        "valuable customers",
        "important customer",
        "important customers",
        "top customer",
        "top customers"
    ]

    if any(
        phrase in question.lower()
        for phrase in business_value_phrases
    ):

        for table_name, columns in schema.items():

            required_columns = [
                "customer_id",
                "name",
                "total_purchase"
            ]

            relevant_columns = [
                column
                for column in columns
                if column["name"].lower()
                in required_columns
            ]

            if relevant_columns:
                selected_schema[table_name] = relevant_columns

    # ------------------------------------------------
    # If nothing relevant was detected,
    # provide the complete schema.
    # ------------------------------------------------
    if not selected_schema:
        return schema

    return selected_schema


if __name__ == "__main__":

    from schema_inspector import get_database_schema

    schema = get_database_schema()

    question = input("\nAsk a database question: ")

    selected = select_relevant_schema(
        question,
        schema
    )

    print("\nRELEVANT SCHEMA")
    print("================")

    print(selected)