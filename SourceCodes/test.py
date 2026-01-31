from openai import OpenAI
import time
from sora.download_video import download_video
from datetime import datetime
import base64
from pathlib import Path
from picture.download_img_from_url import download_image_from_url
from utils.crop_image import crop_image_to_size

current_time = datetime.now().strftime("%Y-%m-%d %H_%M_%S")

client = OpenAI()

raw_story = client.responses.create(
  model="gpt-5",
  reasoning={"effort": "medium"},
  tools=[{ "type": "web_search", "external_web_access": False }],
  tool_choice="auto",
  input="Get me the biggest tech news of the day. The news can be summarized in just 3 sentences and each of the sentences is limited to 6 words. Only output the story, without the reference websites. The websites cited do not need to appear in the output.",
)
print(raw_story.output_text)
story = raw_story.output_text


img = client.images.generate(
    model="gpt-image-1.5",
    prompt="Design a comic book style video cover for the following news: " + story + ". And the title is limited to no more than 10 words. And no more other text except the title.",
    n=1,
    size="1024x1536",
    quality="low",
)
image_bytes = base64.b64decode(img.data[0].b64_json)
with open(f"VirtualPictures/cover_{current_time}.png", "wb") as f:
    f.write(image_bytes)
# download_image_from_url(img.data[0].url, save_path=f"VirtualPictures/cover_{current_time}.png")
image_path = Path(f"VirtualPictures/cover_{current_time}.png")
cropped_image_path = f"VirtualPictures/cover_{current_time}_720P.png"
crop_image_to_size(image_path, cropped_image_path, target_width=720, target_height=1280)
cropped_image_path = Path(cropped_image_path)

comic_book_script = client.responses.create(
    model="gpt-5",
    reasoning={"effort": "medium"},
    input=[
        {
            "role": "assistant",
            "content": "The user-provided stories are optimized and transformed into scripts for creating comic strips. The voice-over is limited to 3 sentences totally and each of the sentences is limited to 6 words."
            " The script is 12 seconds long, divided into 5 segments: The first segment displays a 1-second poster. The second segment, from 1 to 4 seconds, features the first line of voice-over. The third segment, from 4 to 8 seconds, features the second line of voice-over. The fourth segment, from 8 to 11 seconds, features the third line of voice-over. The fifth segment, from 11 to 12 seconds, only features the final scene for 1 seconds."
            " The artwork must be in comic book style. No subtitles. The voice-over is in Chinese. Make sure the news is finished. No subtitles.",
        },
        {
            "role": "user",
            "content": story,
        }
    ]
)


comic_script = comic_book_script.output_text
print("Generated Comic Book Script:\n", comic_script)


video = None
last_exc = None
for attempt in range(1, 4):
    try:
        video = client.videos.create(
            prompt=comic_script,
            model="sora-2",
            seconds="4",
            size="720x1280",
            input_reference=cropped_image_path,
        )
        print("Video creation initiated. Video ID:", video.id)
        break
    except Exception as e:
        last_exc = e
        print(f"[WARN] Video creation failed (attempt {attempt}/3): {e}")
        if attempt < 3:
            sleep_t = 2 ** (attempt - 1)
            print(f"[INFO] Retrying video creation in {sleep_t}s...")
            time.sleep(sleep_t)


download_video(video.id, f"GeneratedVideos/tech_news_{current_time}.mp4")
