from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import math
import os

import mysql.connector
from dotenv import load_dotenv

from query_engine import (
    answer_question,
    get_top_customer,
    get_customer_count,
    get_dashboard_summary,
    get_city_analytics
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AI Customer Intelligence API",
    description=(
        "Customer analytics and RAG-powered AI assistant "
        "using MySQL, FAISS, Gemini and FastAPI."
    ),
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================================
# REQUEST MODELS
# ============================================================

class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Customer intelligence question"
    )


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "application": "AI Customer Intelligence API",
        "version": "1.0.0",
        "status": "running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    connection = None

    try:
        connection = get_db_connection()

        return {
            "status": "healthy",
            "database": "connected",
            "rag": "available"
        }

    except Exception as e:
        print("Health check error:", e)

        return {
            "status": "unhealthy",
            "database": "disconnected",
            "rag": "unknown"
        }

    finally:
        if connection:
            connection.close()


# ============================================================
# AI ASSISTANT
# ============================================================

@app.post("/ask")
def ask_question(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        answer = answer_question(question)

        return {
            "status": "success",
            "question": question,
            "answer": answer
        }

    except Exception as e:
        print("AI assistant error:", e)

        raise HTTPException(
            status_code=500,
            detail="Failed to process AI question"
        )


# ============================================================
# SINGLE CUSTOMER
# ============================================================

@app.get("/customer/{customer_id}")
def get_customer(customer_id: str):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                customer_id,
                name,
                age,
                city,
                email,
                total_purchase
            FROM customers
            WHERE customer_id = %s
        """

        cursor.execute(query, (customer_id,))

        customer = cursor.fetchone()

        if not customer:
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        if customer.get("total_purchase") is not None:
            customer["total_purchase"] = float(
                customer["total_purchase"]
            )

        return {
            "status": "success",
            "customer": customer
        }

    except HTTPException:
        raise

    except Exception as e:
        print(
            "Customer details error:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to fetch customer details"
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# TOP CUSTOMER
# ============================================================

@app.get("/analytics/top-customer")
def top_customer():
    try:
        customer = get_top_customer()

        if not customer:
            raise HTTPException(
                status_code=404,
                detail="No customers found"
            )

        return {
            "status": "success",
            "data": customer
        }

    except HTTPException:
        raise

    except Exception as e:
        print(
            "Top customer error:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to fetch top customer"
        )


# ============================================================
# CUSTOMER COUNT
# ============================================================

@app.get("/analytics/customer-count")
def customer_count():
    try:
        count = get_customer_count()

        return {
            "status": "success",
            "customer_count": count
        }

    except Exception as e:
        print(
            "Customer count error:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to fetch customer count"
        )


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

@app.get("/analytics/summary")
def dashboard_summary():
    try:
        summary = get_dashboard_summary()

        return {
            "status": "success",
            "data": summary
        }

    except Exception as e:
        print(
            "Dashboard summary error:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to fetch dashboard summary"
        )


# ============================================================
# SINGLE CITY ANALYTICS
# ============================================================

@app.get("/analytics/city/{city}")
def city_analytics_by_name(city: str):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                city,
                COUNT(*) AS customer_count,
                SUM(total_purchase) AS total_purchase,
                AVG(total_purchase) AS average_purchase
            FROM customers
            WHERE LOWER(TRIM(city)) =
                  LOWER(TRIM(%s))
            GROUP BY city
        """

        cursor.execute(
            query,
            (city,)
        )

        result = cursor.fetchone()

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No customers found in {city}"
            )

        if result.get("total_purchase") is not None:
            result["total_purchase"] = float(
                result["total_purchase"]
            )

        if result.get("average_purchase") is not None:
            result["average_purchase"] = float(
                result["average_purchase"]
            )

        if result.get("customer_count") is not None:
            result["customer_count"] = int(
                result["customer_count"]
            )

        return {
            "status": "success",
            "data": result
        }

    except HTTPException:
        raise

    except Exception as e:
        print(
            "City analytics error:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to fetch city analytics"
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# ALL CITY ANALYTICS
# ============================================================

@app.get("/analytics/cities")
def city_analytics():
    try:
        cities = get_city_analytics()

        return {
            "status": "success",
            "data": cities
        }

    except Exception as e:
        print(
            "City analytics list error:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to fetch city analytics"
        )


# ============================================================
# PREMIUM CUSTOMERS
# ============================================================

@app.get("/analytics/premium-customers")
def premium_customers():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                customer_id,
                name,
                city,
                total_purchase
            FROM customers
            WHERE total_purchase BETWEEN 10000 AND 14999
            ORDER BY total_purchase DESC
        """

        cursor.execute(query)

        customers = cursor.fetchall()

        for customer in customers:
            if customer.get("total_purchase") is not None:
                customer["total_purchase"] = float(
                    customer["total_purchase"]
                )

        return {
            "status": "success",
            "count": len(customers),
            "customers": customers
        }

    except Exception as e:
        print(
            "Premium customer error:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to fetch premium customers"
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# CUSTOMER LIST
# SERVER-SIDE SEARCH + FILTER + PAGINATION
# ============================================================

@app.get("/customers")
def get_customers(
    search: str = "",
    city: str = "",
    segment: str = "",
    page: int = Query(
        1,
        ge=1
    ),
    page_size: int = Query(
        5,
        ge=1,
        le=100
    )
):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(
            dictionary=True
        )

        # ----------------------------------------------------
        # Build filters
        # ----------------------------------------------------

        where_conditions = []
        filter_values = []

        # Search
        if search.strip():
            search_value = (
                f"%{search.strip()}%"
            )

            where_conditions.append(
                """
                (
                    customer_id LIKE %s
                    OR name LIKE %s
                    OR email LIKE %s
                )
                """
            )

            filter_values.extend([
                search_value,
                search_value,
                search_value
            ])

        # City
        if city.strip():
            where_conditions.append(
                """
                LOWER(TRIM(city)) =
                LOWER(TRIM(%s))
                """
            )

            filter_values.append(
                city.strip()
            )

        # Segment
        if segment.strip():

            if segment == "Low Value":

                where_conditions.append(
                    "total_purchase < 5000"
                )

            elif segment == "Regular":

                where_conditions.append(
                    """
                    total_purchase >= 5000
                    AND total_purchase < 10000
                    """
                )

            elif segment == "Premium":

                where_conditions.append(
                    """
                    total_purchase >= 10000
                    AND total_purchase < 15000
                    """
                )

            elif segment == "High Value":

                where_conditions.append(
                    "total_purchase >= 15000"
                )

            else:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid customer segment"
                )

        # ----------------------------------------------------
        # WHERE clause
        # ----------------------------------------------------

        where_clause = ""

        if where_conditions:
            where_clause = (
                " WHERE "
                + " AND ".join(
                    where_conditions
                )
            )

        # ----------------------------------------------------
        # Count total matching records
        # ----------------------------------------------------

        count_query = f"""
            SELECT COUNT(*) AS total
            FROM customers
            {where_clause}
        """

        cursor.execute(
            count_query,
            tuple(filter_values)
        )

        count_result = cursor.fetchone()

        total_customers = int(
            count_result["total"]
        )

        # ----------------------------------------------------
        # Calculate pages
        # ----------------------------------------------------

        total_pages = max(
            1,
            math.ceil(
                total_customers / page_size
            )
        )

        # Prevent invalid page
        if page > total_pages:
            page = total_pages

        # ----------------------------------------------------
        # Calculate offset
        # ----------------------------------------------------

        offset = (
            (page - 1)
            * page_size
        )

        # ----------------------------------------------------
        # Fetch page
        # ----------------------------------------------------

        customers_query = f"""
            SELECT
                customer_id,
                name,
                age,
                city,
                email,
                total_purchase
            FROM customers
            {where_clause}
            ORDER BY customer_id ASC
            LIMIT %s OFFSET %s
        """

        customer_values = (
            filter_values
            + [
                page_size,
                offset
            ]
        )

        cursor.execute(
            customers_query,
            tuple(customer_values)
        )

        customers = cursor.fetchall()

        # ----------------------------------------------------
        # Convert Decimal values
        # ----------------------------------------------------

        for customer in customers:

            if customer.get(
                "total_purchase"
            ) is not None:

                customer[
                    "total_purchase"
                ] = float(
                    customer[
                        "total_purchase"
                    ]
                )

        # ----------------------------------------------------
        # Pagination state
        # ----------------------------------------------------

        has_next = (
            page < total_pages
        )

        has_previous = (
            page > 1
        )

        # ----------------------------------------------------
        # Response
        # ----------------------------------------------------

        return {
            "status": "success",
            "data": customers,
            "total": total_customers,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_previous": has_previous
        }

    except HTTPException:
        raise

    except Exception as e:
        print(
            "Error fetching customers:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to fetch customers"
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()