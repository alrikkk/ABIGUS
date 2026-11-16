import pytest
from app.core.container_format import build_container, parse_container

def test_container_round_trip():
    payload = b"This is my original file content"
    metadata= {
        "filename": "test.txt",
        "size": len(payload),
        "format": "txt"
    }



    container = build_container(metadata, payload)
    recovered_metadata, recovered_payload = parse_container(container)
    assert recovered_metadata == metadata
    assert recovered_payload == payload

def test_container_rejects_invalid_payload_type():
    metadata = {
        "filename": "test.txt",
        "size": 4,
        "format": "txt"
    }

    with pytest.raises(ValueError, match="Payload must be bytes"):
        build_container(metadata, "ABIG")

def test_parser_rejects_invalid_container_type():
    with pytest.raises(ValueError, match="Container must be bytes"):
        parse_container("ABIG")

def test_parser_rejects_truncated_container():
    with pytest.raises(ValueError, match="Container is too small"):
        parse_container(b"ABIG")