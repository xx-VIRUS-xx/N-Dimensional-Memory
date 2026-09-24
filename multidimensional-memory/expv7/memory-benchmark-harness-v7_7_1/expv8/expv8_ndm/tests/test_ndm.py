from ndm.schema import empty_memory, validate_memory


def test_empty_schema():
    m = empty_memory("x")
    assert validate_memory(m) == []