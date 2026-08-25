# PDF, Image, and Word Document Merger

A small Python script that automatically merges the files found in the
`output/` folder into a single PDF:

- **PDF** (`.pdf`)
- **Images** (`.png`, `.jpg`, `.jpeg`)
- **Word / OpenDocument files** (`.docx`, `.doc`, `.odt`)

The result is saved in the `input/` folder. Images and documents are
automatically converted to PDF before being added to the final file.

## Project structure

```
pdf-merger/
├── merge_pdfs.py     # the script
├── output/           # ← place the PDFs to merge here
├── input/             # ← the merged PDF will be created here
└── README.md
```

> All files (PDF, images, documents) are merged in alphabetical order
> based on their file name, regardless of format. If you want a specific
> order, prefix them with numbers, for example:
> `01_intro.pdf`, `02_photo.png`, `03_annex.docx`...

## Installation

You need Python 3 and the following libraries:

```bash
pip install pypdf pillow
```

Additionally, to convert Word documents (`.docx`, `.doc`, `.odt`) to
PDF, the script uses **LibreOffice** from the command line (`soffice`).
It must be installed on your machine:

- **Windows / macOS**: install [LibreOffice](https://www.libreoffice.org/download/download/)
  (the `soffice` command must be available in your PATH).
- **Linux (Debian/Ubuntu)**:
  ```bash
  sudo apt install libreoffice
  ```

> If you're only merging PDFs and images, LibreOffice is not required.

## Usage

### 1. Basic usage (default)

1. Put all the files you want to merge (PDF, PNG, JPG/JPEG,
   DOCX...) in the `output/` folder.
2. Run:

```bash
python merge_pdfs.py
```

3. The result will automatically be created at `input/merged.pdf`.

### 2. Choose a different source folder

```bash
python merge_pdfs.py --folder path/to/another/folder
```

### 3. Choose the output file name/location

```bash
python merge_pdfs.py -o input/my_final_document.pdf
```

### 4. Merge specific files, in a chosen order

You can also skip the `output/` folder and pass the files directly,
in the desired order (formats can be mixed):

```bash
python merge_pdfs.py file1.pdf photo.png report.docx -o input/result.pdf
```

## Options summary

| Option           | Description                                              | Default value          |
|------------------|-----------------------------------------------------------|-------------------------|
| `files`          | List of specific files to merge (optional)                 | (none)                  |
| `--folder`       | Source folder containing the files to merge                | `output/`                |
| `-o`, `--output` | Output PDF file                                             | `input/merged.pdf`      |
| `--watermark`        | Watermark text to apply on each page (optional)         | (none)                   |
| `--watermark-opacity` | Watermark opacity, from 0 (invisible) to 1 (opaque)    | `0.15`                    |
| `--watermark-size`    | Watermark font size, in points                         | `40`                      |

## Supported formats

| Format                  | Extensions            | Conversion required |
|--------------------------|------------------------|-----------------------|
| PDF                      | `.pdf`                | No                    |
| Images                   | `.png`, `.jpg`, `.jpeg`| Yes (via Pillow)      |
| Word/OpenDoc documents   | `.docx`, `.doc`, `.odt`| Yes (via LibreOffice) |