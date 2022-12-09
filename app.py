#!/usr/bin/env python

import io
import uvicorn

from fastapi import FastAPI, UploadFile, Response, status, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
import ocrmypdf

import app

app = FastAPI()

# Available languages depend on the system installations
available_languages = ["chi_sim", "deu", "eng", "fra", "osd", "por", "spa"]


def language_supported(langs: str) -> bool:
    for l in langs.split("+"):
        if l not in available_languages:
            return False
    return True


@app.post("/ocr/pdf")
async def create_upload_file(
    file: UploadFile, force_ocr: bool = False, language: str = None
):

    if language is not None and not language_supported(language):
        raise HTTPException(
            detail="a selected language is not supported by the system",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    target = io.BytesIO()

    try:
        # ocr is not happy with the file object returned by UploadFile,
        # so we create a new BytesIO object to pass it to ocr.
        ocrmypdf.ocr(
            input_file=io.BytesIO(file.file.read()),
            output_file=target,
            force_ocr=force_ocr,
            language=language,
        )
    except ocrmypdf.PriorOcrFoundError as ex:
        raise HTTPException(
            detail="page already has text! Set force-ocr to continue",
            status_code=status.HTTP_409_CONFLICT,
        ) from ex
    except ocrmypdf.PdfMergeFailedError as ex:
        raise HTTPException(
            detail="input PDF is malformed, preventing merging",
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from ex
    except ocrmypdf.UnsupportedImageFormatError as ex:
        raise HTTPException(
            detail="input file type was an image that could not be read, or some other file type that is not a PDF.",
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from ex
    except ocrmypdf.DpiError as ex:
        raise HTTPException(
            detail="input file is an image, but the resolution of the image is not credible (allowing it to proceed would cause poor OCR).",
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from ex
    except ocrmypdf.EncryptedPdfError as ex:
        raise HTTPException(
            detail="password protected", status_code=status.HTTP_400_BAD_REQUEST
        ) from ex
    except ocrmypdf.MissingDependencyError as ex:
        raise HTTPException(
            detail="required dependency program is missing or was not found on PATH.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from ex
    except ocrmypdf.TesseractConfigError as ex:
        raise HTTPException(
            detail="tesseract configuration error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from ex
    except Exception as ex:
        raise HTTPException(
            detail="unknown error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) from ex

    return Response(
        content=target.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="' + file.filename + '"'},
    )


Instrumentator().instrument(app).expose(app, include_in_schema=False)
