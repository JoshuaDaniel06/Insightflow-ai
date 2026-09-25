import os
from dotenv import load_dotenv

load_dotenv()


def classify_question(question):
    """
    Classifies a user question into:

    DATA
    POLICY
    MIXED
    SECURITY
    UNKNOWN

    The router is intentionally lightweight to reduce
    unnecessary Gemini/API calls.
    """

    if not question or not question.strip():
        return "UNKNOWN"

    q = question.lower().strip()

    # ---------------------------------------------------------
    # SECURITY / DESTRUCTIVE OPERATIONS
    # ---------------------------------------------------------

    security_keywords = [
        "drop table",
        "delete from",
        "truncate table",
        "alter table",
        "create table",
        "update customers",
        "delete customers",
        "insert into",
        "replace into",
        "drop database",
        "create database",
        "grant ",
        "revoke ",
        "shutdown",
        "execute procedure"
    ]

    for keyword in security_keywords:
        if keyword in q:
            return "SECURITY"

    # ---------------------------------------------------------
    # POLICY QUESTIONS
    # ---------------------------------------------------------

    policy_keywords = [
        "policy",
        "policies",
        "leave policy",
        "refund policy",
        "return policy",
        "privacy policy",
        "company policy",
        "employee policy",
        "terms and conditions",
        "rules",
        "guidelines",
        "compliance"
    ]

    has_policy_keyword = any(
        keyword in q
        for keyword in policy_keywords
    )

    # ---------------------------------------------------------
    # CUSTOMER / DATABASE QUESTIONS
    # ---------------------------------------------------------

    data_keywords = [
        "customer",
        "customers",
        "purchase",
        "purchases",
        "spent",
        "spending",
        "revenue",
        "sales",
        "city",
        "cities",
        "email",
        "age",
        "top customer",
        "highest customer",
        "lowest customer",
        "premium customer",
        "premium customers",
        "high-value",
        "high value",
        "total",
        "average",
        "count",
        "number of",
        "database",
        "data",
        "customer base",
        "business insight",
        "business insights",
        "insight",
        "insights",
        "summary",
        "summarize"
    ]

    has_data_keyword = any(
        keyword in q
        for keyword in data_keywords
    )

    # ---------------------------------------------------------
    # MIXED QUESTION
    # ---------------------------------------------------------

    if has_policy_keyword and has_data_keyword:
        return "MIXED"

    # ---------------------------------------------------------
    # POLICY ONLY
    # ---------------------------------------------------------

    if has_policy_keyword:
        return "POLICY"

    # ---------------------------------------------------------
    # DATA ONLY
    # ---------------------------------------------------------

    if has_data_keyword:
        return "DATA"

    # ---------------------------------------------------------
    # GENERAL BUSINESS QUESTIONS
    # ---------------------------------------------------------

    business_keywords = [
        "business",
        "performance",
        "growth",
        "retention",
        "recommendation",
        "recommendations",
        "important customers",
        "valuable customers",
        "what should we",
        "what can we",
        "what do you recommend",
        "analyze",
        "analysis"
    ]

    if any(
        keyword in q
        for keyword in business_keywords
    ):
        return "DATA"

    # ---------------------------------------------------------
    # UNKNOWN
    # ---------------------------------------------------------

    return "UNKNOWN"