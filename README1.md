# 🤖 AI SQL Assistant

An AI-powered SQL Assistant that allows users to query an AJIO sales dataset using natural language. The application converts plain English questions into SQL using Gemma 3 (running locally with Ollama), executes the generated query on an SQLite database, and displays the results with interactive visualizations in a modern Streamlit dashboard.

---

## 📌 Project Overview

Writing SQL queries can be challenging for many users. This project bridges that gap by allowing users to interact with a database using everyday language.

Simply type a question like:

> Show the top 5 brands with the most products.

The assistant will:

- Understand the question
- Generate the SQL query
- Execute it on the database
- Display the results
- Visualize the output automatically

---

## ✨ Features

- 🤖 Natural Language to SQL using Gemma 3
- 💻 Runs completely offline with Ollama
- 🗄 SQLite database backend
- 📊 Interactive Streamlit dashboard
- 📈 Automatic data visualizations
- 📥 Download query results as CSV
- 📝 Query history
- 🌙 Dark & Light mode
- ⚡ Fast query execution
- 📂 Clean project structure

---

## 🛠 Tech Stack

- Python
- Streamlit
- SQLite
- SQLAlchemy
- Pandas
- Ollama
- Gemma 3
- Matplotlib

---

## 📂 Project Structure

```
AI_SQL_Assistant/
│
├── data/
│   └── ajio_sales.csv
│
├── database/
│   ├── create_db.py
│   └── sales.db
│
├── Models/
│   ├── __init__.py
│   └── ollama_model.py
│
├── sql_engine/
│   ├── __init__.py
│   ├── sql_generator.py
│   └── query_executor.py
│
├── app.py
├── cleaner.py
├── requirements.txt
└── README.md

## ▶️ Run the Application

```bash
streamlit run app.py
```

---

## 💬 Example Questions

- Show top 5 brands with most products
- Which brand has the most expensive product?
- Show products above 50000 rupees
- Show average original price by brand
- Show products with black color
- Count products by color
- Show all products from Nike

---

## 📈 Future Improvements

- Support any uploaded CSV dataset
- AI-generated insights
- Multiple database support
- Export reports to PDF
- Authentication
- Chat-style interface
- Dashboard analytics
- Voice-based queries

---

## 🎯 Learning Outcomes

This project helped me learn:

- Prompt engineering for Text-to-SQL
- Working with Local LLMs
- SQLite database integration
- Streamlit dashboard development
- Data cleaning and preprocessing
- SQL query execution
- Project structuring in Python
