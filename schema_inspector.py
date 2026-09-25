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


def get_database_schema():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    schema = {}

    for table in tables:
        table_name = table[0]

        cursor.execute(f"DESCRIBE `{table_name}`")
        columns = cursor.fetchall()

        schema[table_name] = []

        for column in columns:
            schema[table_name].append({
                "name": column[0],
                "type": column[1],
                "nullable": column[2],
                "key": column[3]
            })

    cursor.close()
    connection.close()

    return schema


if __name__ == "__main__":
    schema = get_database_schema()

    print("\nDATABASE SCHEMA")
    print("================")

    for table, columns in schema.items():
        print(f"\nTable: {table}")

        for column in columns:
            print(
                f"  - {column['name']} "
                f"({column['type']})"
            )