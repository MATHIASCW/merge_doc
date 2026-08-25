import argparse
import io
import subprocess
import sys
import tempfile
from pathlib import Path

from pypdf import PdfWriter, PdfReader
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color

BASE_DIR = Path(__file__).resolve().parent

DEFAULT_SOURCE_DIR = BASE_DIR / "input"
DEFAULT_DESTINATION_DIR = BASE_DIR / "output"
DEFAULT_FILENAME = "merged.pdf"

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
DOCUMENT_EXTENSIONS = {".docx", ".doc", ".odt"}
SUPPORTED_EXTENSIONS = {".pdf"} | IMAGE_EXTENSIONS | DOCUMENT_EXTENSIONS


def image_to_pdf(image_path, temp_dir):
    image_path = Path(image_path)
    pdf_path = Path(temp_dir) / (image_path.stem + ".pdf")

    with Image.open(image_path) as img:
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        img.save(pdf_path, "PDF")

    return pdf_path


def document_to_pdf(doc_path, temp_dir):
    doc_path = Path(doc_path)

    try:
        result = subprocess.run(
            [
                "soffice",
                "--headless",
                "--convert-to", "pdf",
                "--outdir", str(temp_dir),
                str(doc_path),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except FileNotFoundError:
        print(
            "Error: LibreOffice ('soffice') is not installed or could not be found.\n"
            "It is required to convert Word files (.docx) to PDF."
        )
        sys.exit(1)

    pdf_path = Path(temp_dir) / (doc_path.stem + ".pdf")

    if result.returncode != 0 or not pdf_path.exists():
        print(f"Error converting '{doc_path.name}' to PDF:")
        print(result.stderr)
        sys.exit(1)

    return pdf_path


def prepare_file(path, temp_dir):
    path = Path(path)
    extension = path.suffix.lower()

    if not path.exists():
        print(f"Error: file '{path}' does not exist.")
        sys.exit(1)

    if extension == ".pdf":
        return path
    elif extension in IMAGE_EXTENSIONS:
        print(f"Converting image to PDF: {path.name}")
        return image_to_pdf(path, temp_dir)
    elif extension in DOCUMENT_EXTENSIONS:
        print(f"Converting document to PDF: {path.name}")
        return document_to_pdf(path, temp_dir)
    else:
        print(f"Warning: '{path.name}' has an unsupported format, skipped.")
        return None


def create_watermark_page(width, height, text, opacity, font_size):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(width, height))

    c.setFont("Helvetica-Bold", font_size)
    c.setFillColor(Color(0.5, 0.5, 0.5, alpha=opacity))

    c.translate(width / 2, height / 2)
    c.rotate(45)

    step = font_size * 6
    span = int(max(width, height))
    for y in range(-span, span, step):
        c.drawCentredString(0, y, text)

    c.save()
    buffer.seek(0)

    return PdfReader(buffer).pages[0]


def apply_watermark(writer, text, opacity=0.15, font_size=40):
    print(f"Applying watermark: \"{text}\"")
    cache_by_size = {}

    for page in writer.pages:
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        key = (width, height)

        if key not in cache_by_size:
            cache_by_size[key] = create_watermark_page(
                width, height, text, opacity, font_size
            )

        page.merge_page(cache_by_size[key])


def merge_pdfs(files, output_path, watermark=None, watermark_opacity=0.15, watermark_size=40):
    writer = PdfWriter()

    with tempfile.TemporaryDirectory() as temp_dir:
        for file in files:
            pdf_path = prepare_file(file, temp_dir)
            if pdf_path is None:
                continue

            print(f"Adding: {Path(file).name}")
            writer.append(str(pdf_path))

        if watermark:
            apply_watermark(writer, watermark, watermark_opacity, watermark_size)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            writer.write(f)

    print(f"\n✅ Merged PDF created: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Merges files (PDF, PNG/JPEG images, Word .docx documents) "
            "from the project's 'input' folder and saves the result in the "
            "'output' folder."
        )
    )
    parser.add_argument(
        "files",
        nargs="*",
        help=(
            "Optional list of files to merge (pdf, png, jpg/jpeg, "
            "docx...), in the desired order. If not provided, all supported "
            "files in the --folder directory are used (alphabetical order)."
        ),
    )
    parser.add_argument(
        "--folder",
        default=str(DEFAULT_SOURCE_DIR),
        help=(
            "Folder containing the files to merge (alphabetical order). "
            f"Default: {DEFAULT_SOURCE_DIR}"
        ),
    )
    parser.add_argument(
        "-o", "--output",
        default=str(DEFAULT_DESTINATION_DIR / DEFAULT_FILENAME),
        help=(
            "Path of the output PDF file. "
            f"Default: {DEFAULT_DESTINATION_DIR / DEFAULT_FILENAME}"
        ),
    )
    parser.add_argument(
        "--watermark",
        default=None,
        help=(
            "Watermark text to apply on each page (optional). "
            'Example: --watermark "Doc for EDF"'
        ),
    )
    parser.add_argument(
        "--watermark-opacity",
        type=float,
        default=0.15,
        help="Watermark opacity, from 0 (invisible) to 1 (opaque). Default: 0.15",
    )
    parser.add_argument(
        "--watermark-size",
        type=int,
        default=40,
        help="Watermark font size, in points. Default: 40",
    )

    args = parser.parse_args()

    if args.files:
        files = args.files
    else:
        folder = Path(args.folder)
        if not folder.is_dir():
            print(f"Error: folder '{folder}' does not exist.")
            sys.exit(1)
        files = sorted(
            p for p in folder.iterdir()
            if p.suffix.lower() in SUPPORTED_EXTENSIONS
        )
        if not files:
            print(f"No supported files (pdf, png, jpg/jpeg, docx) found in '{folder}'.")
            sys.exit(1)

    merge_pdfs(
        files,
        args.output,
        watermark=args.watermark,
        watermark_opacity=args.watermark_opacity,
        watermark_size=args.watermark_size,
    )


if __name__ == "__main__":
    main()