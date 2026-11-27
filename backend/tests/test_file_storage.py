from app.core.file_storage import store_file_as_png, recover_file_from_png

def test_file_storage_round_trip(tmp_path):
    #creating sone original binary data
    original_data = b"%PDF-1.7\nABIGUS storage test\n\x00\x01\x02"

    #creating paths inside pytests's temporary directory
    original_file = tmp_path / "sample.pdf"
    png_file = tmp_path / "sample.png"
    recovered_dir = tmp_path / "recovered"

    #write the original file
    original_file.write_bytes(original_data)

    #storing the file inside a PNG carrier
    store_file_as_png(str(original_file), str(png_file))

    #recovering the original file
    recovered_file = recover_file_from_png(
        str(png_file), 
        str(recovered_dir)
    )

    #verifying byte-for-byte recovery
    assert recovered_file.read_bytes() == original_data
    assert recovered_file.name == "sample.pdf"