import base64
from openai import OpenAI
client = OpenAI()

prompt = """
Make the man smile.
"""

result = client.images.edit(
    model="gpt-image-1.5",
    image=[
        open("RawPictures\sad_man_test.jpg", "rb"),
    ],
    prompt=prompt
)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# Save the image to a file
with open("RawPictures\sad_man_test_result.jpg", "wb") as f:
    f.write(image_bytes)