import pytest
from app.engines.png_engine import encode_to_png, decode_from_png

def test_png_round_trip():
    original_data = b"Hello ABIGUS! This is our first PNG storage test."

    #encoding the og bytes into the png
    png_data = encode_to_png(original_data)

    #decoding the png back into bytes
    decoded_data = decode_from_png(png_data)

    assert decoded_data == original_data

@pytest.mark.parametrize(
    "original_data",
    [
        b"\x00\x01\x02\x03\x04\x05",
        bytes(range(256)),
        b"%PDF-1.7\x00\xff\xfe binary PDF data",
        b"PK\x03\x04\x00\x00\xff\xfe ZIP-like data",
    ],
)

def test_png_binary_round_trip(original_data):
    png_data = encode_to_png(original_data)
    decoded_data = decode_from_png(png_data)

    assert decoded_data == original_data

def test_encode_rejects_non_bytes():
    with pytest.raises(TypeError, match="Container must be bytes"):
        encode_to_png("hello")

def test_encode_rejects_empty_data():
    with pytest.raises(ValueError, match="Container cannot be empty"):
        encode_to_png(b"")

def test_decode_rejects_non_bytes():
    with pytest.raises(TypeError, match="PNG data must be bytes"):
        decode_from_png("non bytes")

def test_decode_rejects_invalid_png():
    with pytest.raises(ValueError, match="Invalid or currupted PNG"):
        decode_from_png(b"not a png")

