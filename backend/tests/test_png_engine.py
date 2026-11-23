from app.engines.png_engine import encode_to_png, decode_from_png

def test_png_round_trip():
    original_data = b"Hello ABIGUS! This is our first PNG storage test."

    #encoding the og bytes into the png
    png_data = encode_to_png(original_data)

    #decoding the png back into bytes
    decoded_data = decode_from_png(png_data)

    assert decoded_data == original_data