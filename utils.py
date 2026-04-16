def quality_score(report, total_rows):
    missing = sum(report['missing'].values())
    duplicates = report['duplicates']

    score = 100 - ((missing + duplicates) / (total_rows + 1e-5) * 100)
    return round(score, 2)