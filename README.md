# 🚀 InsightFlow AI

## AI-Powered Customer Intelligence & Data Engineering Platform

InsightFlow AI is an AI-powered customer intelligence platform that combines **data engineering, SQL analytics, RAG, and generative AI** to turn raw customer data into useful business insights.

The platform processes customer data through an ETL workflow, stores structured data in MySQL, provides analytics through FastAPI APIs, and allows users to ask natural-language questions about customer data and business policies through an AI assistant.

---

## 🚀 Key Features

### 🔹 Data Engineering & ETL

* Ingests raw customer data from CSV files
* Performs data cleaning and transformation
* Detects missing values, duplicates, invalid ages, and data inconsistencies
* Generates an automated data-quality report
* Loads cleaned customer data into MySQL

### 🔹 Customer Analytics

* Total customer count
* Total customer purchases
* Average customer purchase
* Highest-value customer
* Premium customer identification
* City-level customer analytics
* Customer search and filtering
* Server-side pagination

### 🔹 AI Customer Assistant

Users can ask natural-language questions such as:

> Who is the highest-value customer?

> How many customers are in Chennai?

> What is the total purchase amount?

> Identify our high-value customers.

The system converts relevant questions into SQL queries, validates the generated SQL, executes safe queries against MySQL, and returns a human-readable response.

### 🔹 RAG-Based Business Policy Assistant

InsightFlow AI also supports questions about business policies using **Retrieval-Augmented Generation (RAG)**.

Example:

> What is the refund policy?

> How long does a refund take?

> What benefits do premium customers receive?

Relevant policy information is retrieved from the knowledge base and provided to the Gemini-powered answer generation system.

### 🔹 Mixed Data + Policy Questions

The platform can combine structured customer data with business-policy information.

For example:

> Is Ravi Kumar a premium customer and what benefits does he receive?

The system can retrieve customer information from MySQL and policy information through RAG before generating the final response.

### 🔹 Interactive Dashboard

The React dashboard provides:

* Business overview
* Customer statistics
* Purchase analytics
* Premium customer metrics
* AI assistant
* Customer search and filtering
* City analytics
* Loading states
* Error handling
* Retry functionality
* API connection status

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │   Raw Customer CSV  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    ETL Pipeline     │
                    │ Cleaning & Quality  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    MySQL Database   │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
             ┌──────────────┐      ┌──────────────┐
             │ SQL Analytics│      │ Schema       │
             │ & Queries    │      │ Inspection   │
             └──────┬───────┘      └──────┬───────┘
                    │                     │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ SQL Generator       │
                    │ Gemini              │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ SQL Validator       │
                    │ Safe SELECT Only    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Query Engine        │
                    └──────────┬──────────┘
                               │
                               ▼
        ┌──────────────────────────────────────────┐
        │              AI Answer Layer             │
        │                                          │
        │  Structured Data + RAG Policy Context    │
        └──────────────────────┬───────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     FastAPI API     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   React Dashboard   │
                    └─────────────────────┘
```

---

## 🧠 AI Architecture

InsightFlow AI uses different processing paths depending on the user's question.

```text
User Question
      │
      ▼
Question Router
      │
      ├── DATA ──────► SQL Generation ──► SQL Validation
      │                                      │
      │                                      ▼
      │                                  MySQL Query
      │                                      │
      │                                      ▼
      │                              Natural Language Answer
      │
      ├── POLICY ────► RAG Retrieval ──► Gemini
      │                                      │
      │                                      ▼
      │                              Natural Language Answer
      │
      └── MIXED ─────► SQL + RAG ─────► Gemini
                                             │
                                             ▼
                                     Final Answer
```

This hybrid approach avoids unnecessarily sending simple database questions to the LLM while still using generative AI for complex reasoning and policy-based questions.

---

## 🛠️ Technology Stack

### Backend

* Python
* FastAPI
* MySQL
* Pandas
* MySQL Connector

### AI / GenAI

* Google Gemini
* Retrieval-Augmented Generation (RAG)
* FAISS
* Embeddings
* Natural-language question answering

### Frontend

* React
* Vite
* Axios
* Recharts
* CSS

### Data Engineering

* CSV ingestion
* ETL pipelines
* Data cleaning
* Data quality validation
* SQL analytics
* Server-side pagination

---

## 📁 Project Structure

```text
InsightFlow-AI/
│
├── .env
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
│
├── analytics.py
├── answer_generator.py
├── build_vector_store.py
├── database.py
├── etl.py
├── main.py
├── query_engine.py
├── question_router.py
├── rag.py
├── schema_inspector.py
├── schema_selector.py
├── sql_generator.py
├── sql_validator.py
├── test_gemini.py
│
├── data/
│   ├── clean_customer.csv
│   ├── clean_customers.csv
│   ├── customer.csv
│   ├── knowledge.txt
│   └── quality_report.json
│
└── frontend/
    ├── src/
    ├── package.json
    ├── package-lock.json
    ├── vite.config.js
    ├── index.html
    └── ...
```

> `node_modules` should not be committed to GitHub. It can be recreated using `npm install`.

---

## ⚙️ How It Works

### 1. Data Ingestion

Raw customer information is loaded from the CSV dataset.

```text
customer.csv
     │
     ▼
ETL Pipeline
```

### 2. Data Cleaning

The ETL process checks for:

* Missing values
* Duplicate records
* Invalid ages
* Invalid email addresses
* Inconsistent city names

The cleaned dataset and quality report are generated automatically.

```text
Raw Data
   │
   ├── Missing values
   ├── Duplicate checks
   ├── Age validation
   ├── Email validation
   └── City standardization
          │
          ▼
    Clean Customer Data
```

### 3. Database Loading

Clean customer data is loaded into MySQL.

```text
Clean CSV
    │
    ▼
MySQL
    │
    ▼
customers table
```

### 4. Natural-Language SQL

When a user asks a structured question, the system:

1. Inspects the database schema
2. Selects relevant schema information
3. Generates a SQL query using Gemini
4. Validates the generated SQL
5. Executes the query
6. Formats the result into a natural-language answer

For example:

```text
"Who is the highest-value customer?"
                │
                ▼
        Schema Selection
                │
                ▼
          SQL Generation
                │
                ▼
SELECT customer_id, name, total_purchase
FROM customers
ORDER BY total_purchase DESC
LIMIT 1;
                │
                ▼
            MySQL
                │
                ▼
        Natural Language
```

### 5. RAG Policy Retrieval

Policy-related questions use the RAG pipeline.

```text
User Question
     │
     ▼
Document Retrieval
     │
     ▼
Relevant Policy Documents
     │
     ▼
Gemini
     │
     ▼
Final Answer
```

---

## 📊 Customer Segmentation

The platform uses purchase value to categorize customers:

| Segment    |      Purchase Value |
| ---------- | ------------------: |
| Low Value  |          `< ₹5,000` |
| Regular    |   `₹5,000 – ₹9,999` |
| Premium    | `₹10,000 – ₹14,999` |
| High Value |         `≥ ₹15,000` |

These rules are used by the analytics and natural-language SQL generation components.

---

## 🔐 SQL Safety

The AI-generated SQL is passed through a validation layer before execution.

The system is designed to allow safe read-only queries and block destructive database operations such as:

```text
INSERT
UPDATE
DELETE
DROP
ALTER
TRUNCATE
CREATE
GRANT
REVOKE
```

Only safe `SELECT` queries should reach the database execution layer.

---

## 🔌 API Endpoints

The FastAPI backend provides endpoints for:

| Endpoint                       | Purpose                                        |
| ------------------------------ | ---------------------------------------------- |
| `/`                            | API information                                |
| `/health`                      | System and database health                     |
| `/ask`                         | AI customer assistant                          |
| `/customers`                   | Customer listing with search/filter/pagination |
| `/customer/{customer_id}`      | Individual customer details                    |
| `/analytics/top-customer`      | Highest-value customer                         |
| `/analytics/customer-count`    | Customer count                                 |
| `/analytics/summary`           | Dashboard summary                              |
| `/analytics/cities`            | City analytics                                 |
| `/analytics/city/{city}`       | Specific city analytics                        |
| `/analytics/premium-customers` | Premium customers                              |

---

## 💻 Installation

### Prerequisites

Install:

* Python 3.11+
* MySQL
* Node.js
* npm

---

### 1. Clone the Repository

```bash
git clone https://github.com/JoshuaDaniel06/InsightFlow-AI.git
cd InsightFlow-AI
```

---

### 2. Create a Python Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

---

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file in the project root.

Example:

```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=your_database_name

GEMINI_API_KEY=your_gemini_api_key
```

Do not commit `.env` to GitHub.

Use `.env.example` as the template for other developers.

---

### 5. Configure MySQL

Create your database and customers table in MySQL.

Then run the ETL process to load the cleaned customer data.

```bash
python etl.py
```

---

### 6. Build the RAG Vector Store

Run:

```bash
python build_vector_store.py
```

This prepares the policy knowledge for semantic retrieval.

---

## ▶️ Running the Application

### Start the Backend

From the project root:

```bash
uvicorn main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

You can also check:

```text
http://127.0.0.1:8000/health
```

---

### Start the Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

The Vite development server will provide the frontend URL shown in the terminal, typically:

```text
http://localhost:5173
```

---

## 💬 Example Questions

### Customer Analytics

```text
Who is the highest-value customer?
```

```text
How many customers are in Chennai?
```

```text
What is the average customer purchase?
```

```text
What is the total purchase amount?
```

```text
Show me the top 3 customers.
```

```text
Identify our high-value customers.
```

### Business Policy

```text
What is the refund policy?
```

```text
How long does a refund take?
```

```text
What benefits do premium customers receive?
```

### Mixed Questions

```text
Is Ravi Kumar a premium customer and what benefits does he receive?
```

```text
Which customers are premium and what support do they receive?
```

---

## 📈 Dashboard

The dashboard provides a centralized view of customer intelligence including:

* Customer base
* Total purchase value
* Average purchase
* Premium customers
* Highest-value customer
* Customer analytics
* City analytics
* AI-powered question answering

The frontend also displays API connection status so users can immediately identify whether the backend is available.

---

## 🎯 Project Goals

InsightFlow AI was built to demonstrate practical skills in:

* Data Engineering
* ETL development
* SQL
* MySQL
* Python
* Data quality
* REST APIs
* FastAPI
* Generative AI
* RAG
* Vector search
* Natural-language SQL
* React
* Data analytics

The project focuses on connecting **data engineering pipelines with GenAI-powered business intelligence** rather than using AI as a standalone chatbot.

---

## 🔮 Future Improvements

Potential future extensions include:

* Cloud deployment
* Authentication and role-based access
* Larger datasets
* Automated scheduled ETL jobs
* Data warehouse integration
* Advanced analytics
* Monitoring and logging
* CI/CD pipeline
* Automated testing
* Docker-based deployment

---

## 👨‍💻 Author

**Joshua Daniel S**

CSE | Aspiring Data Engineer

### Areas of Interest

* Data Engineering
* Python
* SQL
* ETL
* MySQL
* PySpark
* Generative AI
* RAG

---

## ⭐ Project Summary

**InsightFlow AI** demonstrates an end-to-end workflow where raw customer data is transformed into reliable structured data, stored in MySQL, analyzed through SQL, enriched with business-policy knowledge using RAG, and exposed through an interactive React dashboard.

The project combines **Data Engineering + SQL + GenAI + RAG + API Development + Frontend Analytics** into a single customer intelligence platform.
