from pathlib import Path

from app.core.container_format import build_container, parse_container
from app.engines.png_engine import encode_to_png, decode_from_png
def store_file_as_png(
    source_path: str,
    output_path: str
) -> None:

    source = Path(source_path)
    output = Path(output_path)

    # Read the original file
    original_data = source.read_bytes()

    # Create metadata
    metadata = {
        "filename": source.name,
        "size": len(original_data),
        "format": source.suffix.lstrip(".").lower() or "bin"
    }

    # Build the ABIGUS container
    container = build_container(metadata, original_data)

    # Encode the container into PNG
    png_data = encode_to_png(container)

    # Save the PNG
    output.write_bytes(png_data)


def recover_file_from_png(
    png_path: str,
    output_directory: str
) -> Path:
    # Read the PNG carrier
    png_file = Path(png_path)
    output_dir = Path(output_directory)

    png_data = png_file.read_bytes()

    # Decode the PNG to recover the ABIGUS container
    container = decode_from_png(png_data)

    # Extract metadata and original file bytes
    metadata, original_data = parse_container(container)

    # Create the output directory if needed
    output_dir.mkdir(parents=True, exist_ok=True)

    # Reconstruct the original filename
    output_file = output_dir / metadata["filename"]

    # Write the original file bytes
    output_file.write_bytes(original_data)

    return output_file
