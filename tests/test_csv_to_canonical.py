from tools.csv_to_canonical import normalize_row, CANONICAL


def test_priority_mapping_high_medium_low():
    high = normalize_row({"Priority": "High", "ID": "T-100", "Task": "Do X"})
    assert high["priority"] == "P1"
    med = normalize_row({"Priority": "Medium", "ID": "T-101", "Task": "Do Y"})
    assert med["priority"] == "P2"
    low = normalize_row({"Priority": "Low", "ID": "T-102", "Task": "Do Z"})
    assert low["priority"] == "P3"


def test_priority_preserves_p_values():
    p2 = normalize_row({"Priority": "p2", "ID": "T-200", "Task": "Task"})
    assert p2["priority"] == "P2"


def test_convert_writes_header(tmp_path):
    # create a small input CSV
    csv_in = tmp_path / "in.csv"
    csv_out = tmp_path / "out.csv"
    csv_in.write_text("ID,Task,Priority\nT-1,Task1,High\n")
    # call convert
    from tools.csv_to_canonical import convert

    convert(str(csv_in), str(csv_out))
    content = csv_out.read_text()
    # ensure CANONICAL header is present
    assert ",".join(CANONICAL) in content
