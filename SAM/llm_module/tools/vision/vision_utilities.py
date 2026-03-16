import asyncio
import os
import requests

from pathlib import Path
from urllib.parse import urlparse
from utility_scripts.system_logging import setup_logger

# configure logging
logger = setup_logger(__name__)

# set image directory
parent_dir = Path(__file__).resolve().parent
image_dir_path = parent_dir / 'images_temp' / ''


def vision_image_cleanup(image):
    path = image_dir_path / image

    if os.path.exists(path):
        os.remove(path)


def vision_download_image(url):
    dest_folder = image_dir_path

    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)  # create folder if it does not exist

    # extract filename safely without query params
    path = urlparse(url).path
    filename = os.path.basename(path).replace(" ", "_")
    file_path = os.path.join(dest_folder, filename)

    r = requests.get(url, stream=True)
    if r.ok:
        output_path = os.path.abspath(file_path)
        logger.info(f"saving to {output_path}")
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
        return filename
    else:  # HTTP status code 4XX/5XX
        logger.error("Download failed: status code {}\n{}".format(r.status_code, r.text))
        return None
