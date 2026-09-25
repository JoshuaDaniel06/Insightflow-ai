import pandas as pd
import json
import re
import os


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "data/customer.csv"
OUTPUT_FILE = "data/clean_customers.csv"
REPORT_FILE = "data/quality_report.json"


# ============================================================
# REQUIRED COLUMNS
# ============================================================

REQUIRED_COLUMNS = [
    "customer_id",
    "name",
    "age",
    "city",
    "email",
    "total_purchase"
]


# ============================================================
# EMAIL VALIDATION FUNCTION
# ============================================================

def is_valid_email(email):
    """
    Validate email format.
    Missing emails are allowed.
    """

    if pd.isna(email):
        return True

    email = str(email).strip()

    if email == "":
        return True

    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    return bool(re.match(pattern, email))


# ============================================================
# MAIN ETL FUNCTION
# ============================================================

def main():

    print("=" * 60)
    print("AI CUSTOMER DATA INTELLIGENCE - ETL PIPELINE")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. EXTRACT
    # --------------------------------------------------------

    print("\n[1] EXTRACTING DATA...")

    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: Input file not found: {INPUT_FILE}")
        return

    df = pd.read_csv(INPUT_FILE)

    original_count = len(df)

    print(f"Input file      : {INPUT_FILE}")
    print(f"Records loaded  : {original_count}")

    print("\nCustomer IDs loaded:")

    for customer_id in df["customer_id"]:
        print(customer_id)


    # --------------------------------------------------------
    # 2. VALIDATE COLUMNS
    # --------------------------------------------------------

    print("\n[2] VALIDATING COLUMNS...")

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:

        print("ERROR: Missing required columns:")

        for column in missing_columns:
            print(f" - {column}")

        return

    print("All required columns are present.")


    # --------------------------------------------------------
    # 3. STANDARDIZE TEXT DATA
    # --------------------------------------------------------

    print("\n[3] STANDARDIZING DATA...")

    # Remove unnecessary spaces from column names
    df.columns = df.columns.str.strip()

    # Clean text columns
    text_columns = [
        "customer_id",
        "name",
        "city",
        "email"
    ]

    for column in text_columns:

        df[column] = df[column].apply(
            lambda x: x.strip()
            if isinstance(x, str)
            else x
        )


    # --------------------------------------------------------
    # 4. NORMALIZE CITY NAMES
    # --------------------------------------------------------

    print("\n[4] NORMALIZING CITY NAMES...")

    if "city" in df.columns:

        df["city"] = df["city"].apply(
            lambda x: x.strip().title()
            if isinstance(x, str)
            else x
        )

    print("City names normalized.")


    # --------------------------------------------------------
    # 5. CONVERT NUMERIC COLUMNS
    # --------------------------------------------------------

    print("\n[5] VALIDATING NUMERIC DATA...")

    df["age"] = pd.to_numeric(
        df["age"],
        errors="coerce"
    )

    df["total_purchase"] = pd.to_numeric(
        df["total_purchase"],
        errors="coerce"
    )


    # --------------------------------------------------------
    # 6. HANDLE INVALID AGE
    # --------------------------------------------------------

    print("\n[6] CHECKING INVALID AGES...")

    invalid_age_mask = (
        (df["age"] < 0) |
        (df["age"] > 120)
    )

    invalid_age_count = invalid_age_mask.sum()

    if invalid_age_count > 0:

        print(f"Invalid age records found: {invalid_age_count}")

        print("\nInvalid age records:")

        print(
            df.loc[
                invalid_age_mask,
                ["customer_id", "name", "age"]
            ]
        )

        # Convert invalid ages to NULL
        df.loc[invalid_age_mask, "age"] = None

    else:

        print("No invalid ages found.")


    # --------------------------------------------------------
    # 7. EMAIL VALIDATION
    # --------------------------------------------------------

    print("\n[7] VALIDATING EMAIL ADDRESSES...")

    invalid_email_mask = ~df["email"].apply(
        is_valid_email
    )

    invalid_email_count = invalid_email_mask.sum()

    if invalid_email_count > 0:

        print(
            f"Invalid email records found: "
            f"{invalid_email_count}"
        )

        print(
            df.loc[
                invalid_email_mask,
                ["customer_id", "email"]
            ]
        )

        # Invalid emails become NULL
        df.loc[invalid_email_mask, "email"] = None

    else:

        print("No invalid email addresses found.")


    # --------------------------------------------------------
    # 8. CHECK MISSING VALUES
    # --------------------------------------------------------

    print("\n[8] CHECKING MISSING VALUES...")

    missing_values = df.isnull().sum()

    print(missing_values)


    # --------------------------------------------------------
    # 9. DUPLICATE RECORD DETECTION
    # --------------------------------------------------------

    print("\n[9] CHECKING DUPLICATE RECORDS...")

    # Business-level duplicate detection.
    #
    # We don't use only customer_id because the source system
    # may assign different IDs to the same customer.
    #
    # Example:
    #
    # C001 Arun Kumar ...
    # C010 Arun Kumar ...
    #
    # Same customer details but different IDs.
    #
    # Therefore, we use customer attributes.

    duplicate_columns = [
        "name",
        "age",
        "city",
        "email",
        "total_purchase"
    ]

    duplicate_mask = df.duplicated(
        subset=duplicate_columns,
        keep="first"
    )

    duplicate_count = duplicate_mask.sum()

    print(
        f"Duplicate records found: "
        f"{duplicate_count}"
    )

    if duplicate_count > 0:

        print("\nDuplicate records:")

        print(
            df.loc[
                duplicate_mask,
                [
                    "customer_id",
                    "name",
                    "age",
                    "city",
                    "email",
                    "total_purchase"
                ]
            ]
        )

        # Remove duplicate records
        df = df[
            ~duplicate_mask
        ].copy()

        print(
            f"\nRecords after duplicate removal: "
            f"{len(df)}"
        )

    else:

        print("No duplicate records found.")


    # --------------------------------------------------------
    # 10. RESET INDEX
    # --------------------------------------------------------

    df.reset_index(
        drop=True,
        inplace=True
    )


    # --------------------------------------------------------
    # 11. ROUND PURCHASE VALUES
    # --------------------------------------------------------

    print("\n[10] FORMATTING PURCHASE VALUES...")

    df["total_purchase"] = df[
        "total_purchase"
    ].round(2)


    # --------------------------------------------------------
    # 12. GENERATE DATA QUALITY REPORT
    # --------------------------------------------------------

    print("\n[11] GENERATING QUALITY REPORT...")

    final_count = len(df)

    records_removed = original_count - final_count

    quality_report = {

        "pipeline": "AI Customer Data Intelligence",

        "input_file": INPUT_FILE,

        "output_file": OUTPUT_FILE,

        "statistics": {

            "records_before_cleaning":
                int(original_count),

            "records_after_cleaning":
                int(final_count),

            "records_removed":
                int(records_removed),

            "duplicate_records_removed":
                int(duplicate_count),

            "invalid_age_records":
                int(invalid_age_count),

            "invalid_email_records":
                int(invalid_email_count)
        },

        "missing_values": {
            column: int(count)
            for column, count
            in df.isnull().sum().items()
        },

        "duplicate_detection": {

            "method":
                "Composite business key",

            "columns":
                duplicate_columns
        }
    }


    # --------------------------------------------------------
    # 13. SAVE CLEAN CSV
    # --------------------------------------------------------

    print("\n[12] SAVING CLEAN DATA...")

    os.makedirs(
        "data",
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"Clean data saved to: "
        f"{OUTPUT_FILE}"
    )


    # --------------------------------------------------------
    # 14. SAVE QUALITY REPORT
    # --------------------------------------------------------

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            quality_report,
            file,
            indent=4
        )

    print(
        f"Quality report saved to: "
        f"{REPORT_FILE}"
    )


    # --------------------------------------------------------
    # 15. DISPLAY FINAL DATA
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("ETL PIPELINE COMPLETED")
    print("=" * 60)

    print(
        f"\nRecords before cleaning : "
        f"{original_count}"
    )

    print(
        f"Records after cleaning  : "
        f"{final_count}"
    )

    print(
        f"Records removed         : "
        f"{records_removed}"
    )

    print(
        f"Duplicates removed      : "
        f"{duplicate_count}"
    )

    print(
        f"Invalid ages            : "
        f"{invalid_age_count}"
    )

    print(
        f"Invalid emails          : "
        f"{invalid_email_count}"
    )

    print("\nFINAL CLEAN DATA:")

    print(df.to_string(index=False))

    print("\n" + "=" * 60)
    print("ETL SUCCESS")
    print("=" * 60)


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":
    main()