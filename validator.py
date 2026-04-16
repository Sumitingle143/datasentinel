def data_quality_report(df):
    total_cells = df.size
    missing = df.isnull().sum().sum()
    duplicates = df.duplicated().sum()

    negative = df.select_dtypes(include=['number']).lt(0).sum().sum()

    clean_score = 100 - ((missing + duplicates) / total_cells * 100)

    return {
        "Missing %": round((missing/total_cells)*100,2),
        "Duplicate Rows %": round((duplicates/len(df))*100,2),
        "Negative Values %": round((negative/total_cells)*100,2),
        "Clean Data Score %": round(clean_score,2)
    }