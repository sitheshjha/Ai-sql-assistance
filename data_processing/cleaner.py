import pandas as pd


def load_data(path):

    df = pd.read_csv(
        path,
        encoding="latin1"
    )

    return df



def clean_data(df):

    # Remove duplicate rows
    df = df.drop_duplicates()


    # Remove completely empty rows
    df = df.dropna(how="all")


    # Handle missing numerical values
    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    for col in numeric_columns:
        df[col] = df[col].fillna(
            df[col].median()
        )


    # Handle missing text values
    text_columns = df.select_dtypes(
        include="object"
    ).columns

    for col in text_columns:
        df[col] = df[col].fillna(
            "Unknown"
        )


    return df



if __name__ == "__main__":

    # Dataset location
    file_path = "data/ajio_sales.csv"


    # Load dataset
    df = load_data(file_path)


    # Clean dataset
    cleaned_df = clean_data(df)


    print(cleaned_df.head())


    print(
        "Dataset shape after cleaning:",
        cleaned_df.shape
    )