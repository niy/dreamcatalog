from io import BytesIO

import openai
from PIL import Image


class OpenAiApi:
    def __init__(self, api_key):
        self.api_key = api_key

    async def __aenter__(self):
        openai.api_key = self.api_key
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @staticmethod
    async def generate_image_with_mask(img: Image, mask: Image, prompt) -> str:
        """
        Generate an image with the given mask using the DALL-E API.

        Args:
            img (PIL.Image.Image): The input image.
            mask (PIL.Image.Image): The mask to be used in the generated image.
            prompt (str): The prompt to be used in DALL-E API.

        Returns:
            str: The URL of the generated image.
        """
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        mask_bytes = BytesIO()
        mask.save(mask_bytes, format="PNG")
        mask_bytes.seek(0)

        response = openai.Image.create_edit(
            image=img_bytes,
            mask=mask_bytes,
            prompt=prompt,
            n=1,
            size="512x512"
        )
        return response['data'][0]['url']
