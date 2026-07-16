from sql_engine.sql_generator import generate_sql
from sql_engine.query_executor import execute_query


question = input(
    "Ask a question: "
)


sql_query = generate_sql(
    question
)


print("\nGenerated SQL:\n")
print(sql_query)


result = execute_query(
    sql_query
)


print("\nResult:\n")
print(result)