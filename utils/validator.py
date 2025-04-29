def validate_csv_row(row, required_fields):
    for field in required_fields:
        if not row.get(field):
            return False, f"缺少字段: {field}"
    # 可扩展更多校验
    return True, "" 