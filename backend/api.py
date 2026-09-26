from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated
from urllib.parse import quote

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from main import SUPPORTED_EXTENSIONS, merge_pdfs

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"

app = FastAPI(title="Merge Doc API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def safe_filename(filename: str | None) -> str:
    name = Path(filename or "document").name
    if not name or name in {".", ".."}:
        raise HTTPException(status_code=400, detail="Nom de fichier invalide.")
    return name


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/merge")
async def merge_documents(
    files: Annotated[list[UploadFile], File(...)],
    watermark: Annotated[str | None, Form()] = None,
    watermark_opacity: Annotated[float, Form()] = 0.15,
    watermark_size: Annotated[int, Form()] = 40,
    output_name: Annotated[str, Form()] = "merged.pdf",
):
    if not files:
        raise HTTPException(status_code=400, detail="Ajoute au moins un fichier.")
    if not 0 <= watermark_opacity <= 1:
        raise HTTPException(status_code=400, detail="L'opacite doit etre comprise entre 0 et 1.")
    if not 8 <= watermark_size <= 200:
        raise HTTPException(status_code=400, detail="La taille du watermark doit etre comprise entre 8 et 200.")

    upload_names = [safe_filename(file.filename) for file in files]
    unsupported = [
        name for name in upload_names
        if Path(name).suffix.lower() not in SUPPORTED_EXTENSIONS
    ]
    if unsupported:
        raise HTTPException(
            status_code=400,
            detail=f"Format non pris en charge : {', '.join(unsupported)}",
        )

    destination_name = safe_filename(output_name)
    if Path(destination_name).suffix.lower() != ".pdf":
        destination_name = f"{destination_name}.pdf"
    destination = OUTPUT_DIR / destination_name

    with TemporaryDirectory() as temp_dir:
        temp_paths = []
        for file, name in zip(files, upload_names):
            path = Path(temp_dir) / name
            path.write_bytes(await file.read())
            temp_paths.append(path)

        try:
            merge_pdfs(
                temp_paths,
                destination,
                watermark=watermark.strip() if watermark else None,
                watermark_opacity=watermark_opacity,
                watermark_size=watermark_size,
            )
        except SystemExit as error:
            raise HTTPException(
                status_code=422,
                detail="La conversion d'un des documents a echoue. Verifie LibreOffice et les fichiers.",
            ) from error
        except Exception as error:
            raise HTTPException(status_code=422, detail=f"Fusion impossible : {error}") from error

    return FileResponse(
        destination,
        media_type="application/pdf",
        filename=destination_name,
        headers={"X-Output-Name": quote(destination_name)},
    )
