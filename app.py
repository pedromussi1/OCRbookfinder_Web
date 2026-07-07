"""Flask app: upload a book photo, get the identified title.

Deployed live at https://huggingface.co/spaces/Zao0531/ocr-bookfinder
(auto-synced from this repo's main branch via .github/workflows/sync-hf-space.yml).

Rewritten to use the ``bookfinder`` pipeline (cross-platform Tesseract, OpenCV
preprocessing, and a real ranker) instead of the original grayscale-only OCR with the
broken ``max(..., key=lambda x: x.get('relevance', 0))`` ranking that always returned
Google's first hit.
"""

import os
import uuid

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from bookfinder import BookFinder, PipelineConfig

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB cap on uploads

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# Ensure the upload dir exists at import time (so it works under gunicorn, not just __main__).
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Default to the fuzzy ranker (fast, no torch); set BOOKFINDER_RANKER to override.
finder = BookFinder(PipelineConfig(ranker=os.environ.get("BOOKFINDER_RANKER", "fuzzy")))


def _allowed(filename: str) -> bool:
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or not file.filename:
            return render_template("index.html", error="Please choose an image to upload.")
        if not _allowed(file.filename):
            return render_template("index.html", error="Unsupported file type.")

        # Unique, safe name so concurrent uploads never collide or overwrite.
        ext = os.path.splitext(secure_filename(file.filename))[1].lower()
        stored_name = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], stored_name)
        file.save(file_path)

        result = finder.identify(file_path)
        best = result.ranked[0].candidate if result.ranked else None
        return render_template(
            "result.html",
            image=stored_name,
            raw_text=result.raw_text,
            found=best is not None,
            title=best.title if best else None,
            authors=(", ".join(best.authors) if best and best.authors else "Unknown author"),
        )

    return render_template("index.html")


if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    # debug defaults OFF; enable explicitly with FLASK_DEBUG=1 for local dev only.
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
