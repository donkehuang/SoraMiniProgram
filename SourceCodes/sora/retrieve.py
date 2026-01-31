from openai import OpenAI

client = OpenAI()
video = client.videos.retrieve(
    "video_6978e985d2c481908830ad0336d2e46809de8abbe292c89a",
)
print(video)