import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

# Database connection using correct relative path
base_path = Path(__file__).resolve().parent.parent
db_path = base_path / "Database" / "sales.db"
engine = create_engine(f"sqlite:///{db_path.as_posix()}")


def execute_query(sql_query):

    try:
        result = pd.read_sql(
            sql_query,
            engine
        )
        return result
    except Exception as e:
        raise



if __name__ == "__main__":


    query = """
    SELECT *
    FROM sales
    LIMIT 5;
    """


    output = execute_query(query)


    print(output)