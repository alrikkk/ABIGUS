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