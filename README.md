# PDF, Image, and Word Document Merger

A small Python application that merges PDF files, images, and Word/OpenDocument files into a single PDF. It provides both a command-line interface and a local React web interface.

Supported input formats:

- **PDF** (`.pdf`)
- **Images** (`.png`, `.jpg`, `.jpeg`)
- **Word/OpenDocument files** (`.docx`, `.doc`, `.odt`)

Images and documents are automatically converted to PDF before they are added to the final file.

## Project structure

```
merge_doc/
├── backend/
│   ├── main.py
│   ├── api.py
│   ├── requirements.txt
│   ├── input/
│   └── output/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── .gitignore        # node_modules/, dist/
├── .gitignore
└── README.md
```

When using the CLI, files are merged in alphabetical order by filename. To define a custom order, prefix filenames with numbers, for example:
`01_intro.pdf`, `02_photo.png`, `03_annex.docx`.

## Installation

You need Python 3 and the dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

To convert Word and OpenDocument files (`.docx`, `.doc`, `.odt`) to PDF, the application uses **LibreOffice** through the `soffice` command. LibreOffice must be installed and available in your system `PATH`.

- **Windows/macOS:** install [LibreOffice](https://www.libreoffice.org/download/download/).
- **Debian/Ubuntu:**

  ```bash
  sudo apt install libreoffice
  ```

> LibreOffice is not required when merging only PDFs and images.

## Command-line usage

### Merge files from the default source folder

Place the files to merge in `input/`, then run:

```bash
python main.py
```

The merged PDF is created at `output/merged.pdf`.

### Choose a different source folder

```bash
python main.py --folder path/to/another/folder
```

### Choose a different output path

```bash
python main.py -o output/my_final_document.pdf
```

### Merge specific files in a chosen order

You can pass files directly and mix supported formats:

```bash
python main.py file1.pdf photo.png report.docx -o output/result.pdf
```

## React web interface

The web interface uses the local Python API. Open two terminals from the project root.

### Terminal 1: start the Python API

```bash
python -m uvicorn api:app --reload --port 8000
```

### Terminal 2: start the React frontend

```bash
cd frontend
npm install
npm run dev
```

Open the URL shown by Vite, usually `http://localhost:5173`.

You can drop files into the interface, reorder them by dragging, configure an optional watermark, and click **Merge files**. The PDF is saved in `output/` and downloaded automatically.

## Command-line options

| Option | Description | Default |
|---|---|---|
| `files` | Specific files to merge, in the desired order | None |
| `--folder` | Source folder when no files are provided | `input/` |
| `-o`, `--output` | Destination PDF path | `output/merged.pdf` |
| `--watermark` | Text to apply to every page | None |
| `--watermark-opacity` | Watermark opacity from 0 (invisible) to 1 (opaque) | `0.15` |
| `--watermark-size` | Watermark font size in points | `40` |

## Supported formats

| Format | Extensions | Conversion required |
|---|---|---|
| PDF | `.pdf` | No |
| Images | `.png`, `.jpg`, `.jpeg` | Yes, via Pillow |
| Word/OpenDocument files | `.docx`, `.doc`, `.odt` | Yes, via LibreOffice |