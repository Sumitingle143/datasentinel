import pandas as pd
import numpy as np

def handle_outliers(df):
    num_df = df.select_dtypes(include=np.number)

    for col in num_df.columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        # ✅ CAPPING (no row deletion)
        df[col] = np.where(df[col] < lower, lower, df[col])
        df[col] = np.where(df[col] > upper, upper, df[col])

    return df


def auto_fix(df, remove_outlier=False):

    df = df.copy()

    # Replace garbage
    df.replace(["######", "####", "NA", "N/A", "null", "None", ""], np.nan, inplace=True)
    df.replace(r'^#+$', np.nan, regex=True, inplace=True)

    df.drop_duplicates(inplace=True)

    for col in df.columns:

        # SAFE numeric
        try:
            df[col] = pd.to_numeric(df[col])
        except:
            pass

        # DATE FIX
        if col.lower() in ["date", "orderdate", "date_added"]:
            converted = pd.to_datetime(df[col], errors='coerce')
            df[col] = converted.dt.strftime('%Y-%m-%d')
            df[col] = df[col].fillna("Unknown")
            continue

        # NUMERIC
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median())

        # CATEGORICAL ✅ FIXED
        else:
            if df[col].mode().empty:
                df[col] = df[col].fillna("Unknown")
            else:
                df[col] = df[col].fillna(df[col].mode()[0])

    if remove_outlier:
        df = handle_outliers(df)

    return df