def validate_sql(sql_query):

    forbidden_words = [
        "DROP",
        "DELETE",
        "UPDATE",
        "ALTER",
        "INSERT"
    ]


    query = sql_query.upper()


    for word in forbidden_words:

        if word in query:
            return False


    return True



if __name__ == "__main__":

    test = "SELECT * FROM sales;"


    print(validate_sql(test))