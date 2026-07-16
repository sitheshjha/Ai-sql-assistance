import sqlparse # for formatting the generated SQL query
from models.ollama_model import ask_ai
from models.prompts import SQL_PROMPT

# to run use this command: python -m sql_engine.sql_generator in the terminal
def generate_sql(question):

    prompt = SQL_PROMPT.format(
        question=question
    )

    sql_query = ask_ai(prompt)
    # Format the SQL query using sqlparse
    # Remove markdown
    sql_query = sql_query.replace(
        "```sql",
        ""
    )

    sql_query = sql_query.replace(
        "```",
        ""
    )

    sql_query = sql_query.strip()
    print("\nCleaned SQL:\n")
    print(sql_query)

    return sql_query