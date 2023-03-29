from io import BytesIO

import aiohttp
from PIL import Image
import hashlib
from pathlib import Path
from image_resizer import ImageResizer


class RemoveBgApi:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.remove.bg/v1.0/removebg"
        self.cache_path = Path("cached_images")
        self.cache_path.mkdir(exist_ok=True)

    def _get_cache_key(self, img: Image):
        sha1_hash = hashlib.sha1(img.tobytes()).hexdigest()
        return f"{sha1_hash}_removebg"

    def _get_cache_file_path(self, cache_key):
        return self.cache_path / f"{cache_key}.png"

    async def remove_background_and_return_img_pair(self, img: Image, force_invalidate_cache=False) -> tuple[Image, Image]:
        cache_key = self._get_cache_key(img)
        cache_file_path = self._get_cache_file_path(cache_key)

        if not force_invalidate_cache and cache_file_path.exists():
            cached_image = Image.open(cache_file_path)
            return img, cached_image

        resizer = ImageResizer()

        async with aiohttp.ClientSession() as session:

            img_bytes = BytesIO()
            img.save(img_bytes, format="PNG")
            img_bytes.seek(0)

            form_data = aiohttp.FormData()
            form_data.add_field('image_file', img_bytes)
            form_data.add_field('size', 'preview')
            form_data.add_field('type', 'product')
            headers = {'X-Api-Key': self.api_key}
            async with session.post(self.api_url, data=form_data, headers=headers) as response:
                if response.status == 200:
                    image_data = await response.read()
                    image_bytes = BytesIO(image_data)
                    processed_image = Image.open(image_bytes)
                    processed_image = resizer.resize_to_square(processed_image)
                    processed_image.save(cache_file_path, format="PNG")

                    return img, processed_image
                else:
                    raise Exception(f"Error: {response.status} {await response.text()}")
