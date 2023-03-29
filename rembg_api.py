from PIL import Image
from rembg import remove
import hashlib
from pathlib import Path
from rembg.session_factory import new_session


class Rembg:
    def __init__(self):
        self.cache_path = Path("cached_images")
        self.cache_path.mkdir(exist_ok=True)
        self.model = "u2net"

    def _get_cache_key(self, img: Image):
        sha1_hash = hashlib.sha1(img.tobytes()).hexdigest()
        return f"{sha1_hash}_rembg"

    def _get_cache_file_path(self, cache_key):
        return self.cache_path / f"{cache_key}.png"

    async def remove_background_and_return_img_pair(self, img: Image, force_invalidate_cache=False) -> tuple[Image, Image]:
        cache_key = self._get_cache_key(img)
        cache_file_path = self._get_cache_file_path(cache_key)

        if not force_invalidate_cache and cache_file_path.exists():
            cached_image = Image.open(cache_file_path)
            return img, cached_image

        processed_image = remove(img, session=new_session(self.model))
        processed_image.save(cache_file_path, format="PNG")

        return img, processed_image
