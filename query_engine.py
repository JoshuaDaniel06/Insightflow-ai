from schema_inspector import get_database_schema
from schema_selector import select_relevant_schema
from sql_generator import generate_sql
from sql_validator import validate_sql
from question_router import classify_question
from answer_generator import generate_final_answer
from rag import retrieve_documents

import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()


def get_db_connection():

    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )


def execute_sql(sql):

    connection = get_db_connection()
    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(sql)

        results = cursor.fetchall()

        return results

    finally:

        cursor.close()
        connection.close()


# =========================================================
# FIXED ANALYTICS FUNCTIONS
# =========================================================

def get_top_customer():

    sql = """
        SELECT
            customer_id,
            name,
            total_purchase
        FROM customers
        ORDER BY total_purchase DESC
        LIMIT 1
    """

    results = execute_sql(sql)

    if results:
        return results[0]

    return None


def get_customer_count():

    sql = """
        SELECT COUNT(*) AS customer_count
        FROM customers
    """

    results = execute_sql(sql)

    if results:
        return results[0]["customer_count"]

    return 0


def get_dashboard_summary():

    sql = """
        SELECT
            COUNT(*) AS customer_count,
            COALESCE(SUM(total_purchase), 0)
                AS total_purchase,
            COALESCE(AVG(total_purchase), 0)
                AS average_purchase
        FROM customers
    """

    summary = execute_sql(sql)

    top_customer = get_top_customer()

    premium_sql = """
        SELECT COUNT(*) AS premium_customer_count
        FROM customers
        WHERE total_purchase BETWEEN 10000 AND 14999
    """

    premium_result = execute_sql(
        premium_sql
    )

    return {
        "customer_count":
            summary[0]["customer_count"],

        "total_purchase":
            float(summary[0]["total_purchase"]),

        "average_purchase":
            float(summary[0]["average_purchase"]),

        "premium_customer_count":
            premium_result[0][
                "premium_customer_count"
            ],

        "top_customer":
            top_customer
    }


def get_city_analytics():

    sql = """
        SELECT
            city,
            COUNT(*) AS customer_count,
            COALESCE(SUM(total_purchase), 0)
                AS total_purchase,
            COALESCE(AVG(total_purchase), 0)
                AS average_purchase
        FROM customers
        WHERE city IS NOT NULL
          AND TRIM(city) <> ''
        GROUP BY city
        ORDER BY total_purchase DESC
    """

    results = execute_sql(sql)

    for row in results:

        row["total_purchase"] = float(
            row["total_purchase"]
        )

        row["average_purchase"] = float(
            row["average_purchase"]
        )

    return results


# =========================================================
# NATURAL LANGUAGE FORMATTER
# =========================================================

def format_data_result(
    question,
    results
):

    if not results:
        return (
            "No matching customer data was found."
        )

    q = question.lower().strip()

    result = results[0]

    # -----------------------------------------------------
    # TOP CUSTOMER
    # -----------------------------------------------------

    if (
        "top customer" in q
        or "highest customer" in q
        or "highest spending customer" in q
        or "highest purchase" in q
        or "most spending" in q
        or "spent the most" in q
    ):

        if (
            "name" in result
            and "total_purchase" in result
        ):

            name = result["name"]

            amount = float(
                result["total_purchase"]
            )

            return (
                f"{name} is the top customer, "
                f"with a total purchase of "
                f"₹{amount:,.2f}."
            )

    # -----------------------------------------------------
    # HIGHEST REVENUE CITY
    # -----------------------------------------------------

    if (
        (
            "highest revenue" in q
            or "most revenue" in q
            or "generates the most revenue" in q
        )
        and "city" in result
    ):

        city = result["city"]

        if "total_revenue" in result:

            amount = float(
                result["total_revenue"]
            )

        elif "total_purchase" in result:

            amount = float(
                result["total_purchase"]
            )

        else:

            amount = None

        if amount is not None:

            return (
                f"{city} generates the highest "
                f"revenue, with total customer "
                f"purchases of ₹{amount:,.2f}."
            )

    # -----------------------------------------------------
    # CUSTOMER COUNT
    # -----------------------------------------------------

    if (
        "how many customers" in q
        or "number of customers" in q
        or "customer count" in q
        or q == "how many"
    ):

        if "customer_count" in result:

            count = result["customer_count"]

            if "chennai" in q:

                return (
                    f"There are {count} "
                    f"customers from Chennai."
                )

            if "madurai" in q:

                return (
                    f"There are {count} "
                    f"customers from Madurai."
                )

            if "coimbatore" in q:

                return (
                    f"There are {count} "
                    f"customers from Coimbatore."
                )

            return (
                f"There are {count} customers."
            )

    # -----------------------------------------------------
    # AVERAGE PURCHASE
    # -----------------------------------------------------

    if "average" in q:

        if "average_purchase" in result:

            amount = float(
                result["average_purchase"]
            )

            return (
                f"The average customer "
                f"purchase is ₹{amount:,.2f}."
            )

        if "AVG(total_purchase)" in result:

            amount = float(
                result["AVG(total_purchase)"]
            )

            return (
                f"The average customer "
                f"purchase is ₹{amount:,.2f}."
            )

    # -----------------------------------------------------
    # TOTAL PURCHASE
    # -----------------------------------------------------

    if (
        "total purchase" in q
        or "total spent" in q
        or "total spending" in q
        or "total revenue" in q
    ):

        if "total_purchase" in result:

            amount = float(
                result["total_purchase"]
            )

            return (
                f"The total purchase amount is "
                f"₹{amount:,.2f}."
            )

        if "total_revenue" in result:

            amount = float(
                result["total_revenue"]
            )

            return (
                f"The total revenue is "
                f"₹{amount:,.2f}."
            )

    # -----------------------------------------------------
    # CITY RESULT
    # -----------------------------------------------------

    if "city" in result:

        city = result["city"]

        if "customer_count" in result:

            count = result["customer_count"]

            if "total_purchase" in result:

                amount = float(
                    result["total_purchase"]
                )

                return (
                    f"{city} has {count} customers "
                    f"with total purchases of "
                    f"₹{amount:,.2f}."
                )

            return (
                f"{city} has {count} customers."
            )

    # -----------------------------------------------------
    # SINGLE CUSTOMER
    # -----------------------------------------------------

    if (
        "name" in result
        and "total_purchase" in result
    ):

        name = result["name"]

        amount = float(
            result["total_purchase"]
        )

        return (
            f"{name} has a total purchase of "
            f"₹{amount:,.2f}."
        )

    # -----------------------------------------------------
    # GENERIC CUSTOMER COUNT
    # -----------------------------------------------------

    if "customer_count" in result:

        return (
            f"There are "
            f"{result['customer_count']} customers."
        )

    # -----------------------------------------------------
    # SIMPLE TOTAL
    # -----------------------------------------------------

    if "total_purchase" in result:

        amount = float(
            result["total_purchase"]
        )

        return (
            f"The total purchase amount is "
            f"₹{amount:,.2f}."
        )

    # -----------------------------------------------------
    # NO SIMPLE FORMATTER MATCH
    # -----------------------------------------------------

    return None


# =========================================================
# DATA QUESTION HANDLER
# =========================================================

def handle_data_question(question):

    schema = get_database_schema()

    relevant_schema = select_relevant_schema(
        question,
        schema
    )

    print("\nRELEVANT SCHEMA")
    print(relevant_schema)

    print("\nGenerating SQL...")

    sql = generate_sql(
        question,
        relevant_schema
    )

    print("\nGENERATED SQL")
    print("=============")
    print(sql)

    print("\nValidating SQL...")

    valid, message = validate_sql(sql)

    if not valid:

        print("SQL BLOCKED")

        return message

    print("SQL SAFE")

    print("\nExecuting SQL...")

    try:

        results = execute_sql(sql)

        print("\nQUERY RESULT")
        print("============")
        print(results)

        # -------------------------------------------------
        # FIRST: TRY LOCAL FORMATTER
        # -------------------------------------------------

        formatted_answer = format_data_result(
            question,
            results
        )

        if formatted_answer:

            print(
                "\nFINAL ANSWER "
                "(NO GEMINI USED)"
            )

            return formatted_answer

        # -------------------------------------------------
        # SECOND: USE GEMINI ONLY FOR COMPLEX QUESTIONS
        # -------------------------------------------------

        print(
            "\nComplex question detected."
        )

        print(
            "Sending database result to Gemini..."
        )

        return generate_final_answer(
            question=question,
            database_result=results,
            policy_context=None
        )

    except Exception as e:

        print(
            "Database error:",
            e
        )

        return (
            "I couldn't retrieve the requested "
            "customer data."
        )


# =========================================================
# POLICY QUESTION HANDLER
# =========================================================

def handle_policy_question(question):

    print(
        "\nRetrieving policy knowledge..."
    )

    documents = retrieve_documents(
        question
    )

    if not documents:

        return (
            "The requested policy information "
            "is not available."
        )

    policy_context = "\n\n".join(
        documents
    )

    return generate_final_answer(
        question=question,
        database_result=None,
        policy_context=policy_context
    )


# =========================================================
# MIXED QUESTION HANDLER
# =========================================================

def handle_mixed_question(question):

    print(
        "\nProcessing mixed "
        "database + policy question..."
    )

    schema = get_database_schema()

    relevant_schema = select_relevant_schema(
        question,
        schema
    )

    print("\nRELEVANT SCHEMA")
    print(relevant_schema)

    print("\nGenerating SQL...")

    sql = generate_sql(
        question,
        relevant_schema
    )

    print("\nGENERATED SQL")
    print("=============")
    print(sql)

    print("\nValidating SQL...")

    valid, message = validate_sql(sql)

    if not valid:

        print("SQL BLOCKED")

        return message

    print("SQL SAFE")

    print("\nExecuting SQL...")

    try:

        database_result = execute_sql(
            sql
        )

    except Exception as e:

        print(
            "Database error:",
            e
        )

        return (
            "I couldn't retrieve the "
            "requested customer data."
        )

    print("\nDATABASE RESULT")
    print("================")
    print(database_result)

    print(
        "\nRetrieving policy knowledge..."
    )

    documents = retrieve_documents(
        question
    )

    if not documents:

        policy_context = (
            "No relevant policy "
            "information was found."
        )

    else:

        policy_context = "\n\n".join(
            documents
        )

    print(
        "\nGenerating final answer..."
    )

    return generate_final_answer(
        question=question,
        database_result=database_result,
        policy_context=policy_context
    )


# =========================================================
# MAIN QUESTION HANDLER
# =========================================================

def answer_question(question):

    print(
        "\n===================================="
    )

    print("QUESTION:")
    print(question)

    print(
        "===================================="
    )

    question_type = classify_question(
        question
    )

    print(
        "\nQUESTION TYPE:",
        question_type
    )

    # -----------------------------------------------------
    # DATA
    # -----------------------------------------------------

    if question_type == "DATA":

        return handle_data_question(
            question
        )

    # -----------------------------------------------------
    # POLICY
    # -----------------------------------------------------

    elif question_type == "POLICY":

        return handle_policy_question(
            question
        )

    # -----------------------------------------------------
    # MIXED
    # -----------------------------------------------------

    elif question_type == "MIXED":

        return handle_mixed_question(
            question
        )

    # -----------------------------------------------------
    # SECURITY
    # -----------------------------------------------------

    elif question_type == "SECURITY":

        return (
            "This request was blocked because "
            "it contains a potentially destructive "
            "database operation."
        )

    # -----------------------------------------------------
    # UNKNOWN
    # -----------------------------------------------------

    elif question_type == "UNKNOWN":

        return (
            "I couldn't determine whether this "
            "question is related to customer data "
            "or company policies."
        )

    return (
        "Unable to process the question."
    )


# =========================================================
# TERMINAL TEST MODE
# =========================================================

if __name__ == "__main__":

    print(
        "\nAI CUSTOMER DATA INTELLIGENCE"
    )

    print(
        "=============================="
    )

    print(
        "Dynamic SQL + RAG Assistant"
    )

    print(
        "Type 'exit' to stop."
    )

    while True:

        question = input(
            "\nAsk a question: "
        )

        if (
            question.lower().strip()
            == "exit"
        ):

            print(
                "Exiting..."
            )

            break

        answer = answer_question(
            question
        )

        print(
            "\nFINAL ANSWER"
        )

        print(
            "============"
        )

        print(answer)