from flask import current_app
from werkzeug.datastructures import FileStorage
from pathlib import Path
from PIL import Image, ImageOps
import os
import stat
import shutil


def safe_rmtree(path: Path | str) -> None:
    def handle_remove_error(func, path, exc_info):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    if Path(path).exists():
        shutil.rmtree(path, onerror=handle_remove_error)


def upload_file(file: FileStorage, id: str) -> str | None:
    if not file \
        or not file.filename \
            or file.filename == '' \
            or not current_app.static_folder:
        return None
    ext = Path(file.filename).suffix
    filedir = Path(current_app.static_folder, current_app.config['IMAGE_FOLDER'], id)

    try:
        if Path(filedir).exists():
            safe_rmtree(filedir)
        filedir.mkdir(parents=True)
        filename = Path(filedir, f'image{ext}')
        file.seek(0)
        file.save(filename)
        if (not generate_thumbnail(filename, 'small', (250, 250))) \
                or (not generate_thumbnail(filename, 'large', (500, 500))):
            raise Exception('Thumbnail generation failed')
        return filename.name
    except Exception:
        if Path(filedir).exists():
            safe_rmtree(filedir)
        return None


def generate_thumbnail(image_path: Path, desc: str, size: tuple[int, int]) -> str | None:
    thumbnail_path = Path(image_path.parent, f'thumb_{desc}')
    try:
        with Image.open(image_path) as img:
            img = ImageOps.exif_transpose(img)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            if Path(thumbnail_path).exists():
                safe_rmtree(thumbnail_path)
            thumbnail_path.mkdir()
            thumbnail_path = Path(thumbnail_path, 'thumb.jpg')
            img.save(thumbnail_path, format="JPEG")
            return thumbnail_path.name
    except Exception:
        if Path(thumbnail_path).exists():
            safe_rmtree(thumbnail_path)
        return None
