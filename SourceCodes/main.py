from openai import OpenAI
from sora.save_video import save_video_to_csv
import sys
import time
from datetime import datetime
from pathlib import Path
from sora.download_video import download_video
from utils.read_csv import read_csv_by_row_and_title, read_csv_by_row
from dialogue.extract_prompt_from_time import read_prompt_by_time, get_rowidx_from_time
from dialogue.line_generation import generate_and_save_line
from sora.prompt_opt import optimize_scrpits
from picture.image_generation_test import generate_first_frame
from utils.crop_image import crop_image_to_size
client = OpenAI()

# Step 1: Define paths and generate dialogue line
image_path = None
generated_lines_path = "ScriptsLists/generated_logs.csv"
suggestion_prompt_path = "ScriptsLists/prompts.csv"

# Step 2: Prepare timestamp
current_time = datetime.now().strftime("%Y-%m-%d %H_%M_%S")
print(f"[STEP 2] ✓ Timestamp prepared: {current_time}")

# Step 3: Generate first-frame image
print("[STEP 3] Starting first-frame image generation...")
generated_image = generate_first_frame(output_path=f"VirtualPictures/lucky_talk_show_{current_time}.png")
print(f"[STEP 3] ✓ First-frame image generated: {generated_image}")
# Crop the generated image to the expected 720x1280 size for the video
print("[STEP 3B] Starting image cropping to 720x1280...")
cropped_image_path = f"VirtualPictures/lucky_talk_show_{current_time}_720x1280.png"
crop_image_to_size(generated_image, cropped_image_path, target_width=720, target_height=1280)
print(f"[STEP 3B] ✓ Image cropped: {cropped_image_path}")

# Step 4: Generate dialogue line and save to CSV (record first-frame image path)
print("[STEP 4] Starting dialogue generation...")
generate_and_save_line(current_time, suggestion_prompt_path, generated_lines_path, first_frame_image=cropped_image_path)
print(f"[STEP 4] ✓ Dialogue generated and saved to CSV")

# Step 5: Read the latest generated lines and other info for video prompt
print("[STEP 5] Reading generated lines from CSV...")
generated_lines = read_csv_by_row_and_title(generated_lines_path, rows=-1, title="LineGeneration")
print(f"[STEP 5] ✓ Generated lines read: {generated_lines[:100] if len(str(generated_lines)) > 100 else generated_lines}")

row_idx = get_rowidx_from_time()
ScenarioTime = read_csv_by_row(suggestion_prompt_path, target_row=row_idx, title="Time")
print(f"[STEP 5] ✓ Scenario time read: {ScenarioTime}")
ScenarioLocation = read_csv_by_row(suggestion_prompt_path, target_row=row_idx, title="Location")
print(f"[STEP 5] ✓ Scenario location read: {ScenarioLocation}")
main_prompt = f"This is a funny scene where pet cats and dogs are complaining about their owner.. It's {ScenarioTime} now. The dialogue is as follows: {generated_lines}. Chinese subtitles are needed, and the dubbing should be in Mandarin Chinese.  Control the length of the dialogue; the dog and the cat each say one sentence."
print("Generated Main Prompt for Video Creation:")
print(main_prompt)

# Optimize the script using Sora's prompt optimizatio
print("[STEP 6] Starting script optimization...")
optimized_scripts = optimize_scrpits(main_prompt)
print(f"[STEP 6] ✓ Script optimized: {optimized_scripts[:100] if len(str(optimized_scripts)) > 100 else optimized_scripts}")

# Use the cropped image as the video's first frame
image_path = Path(cropped_image_path)

print("[STEP 7] Starting video creation with Sora API...")
video = None
last_exc = None
for attempt in range(1, 4):
    try:
        video = client.videos.create(
            prompt=optimized_scripts,
            model="sora-2",
            seconds="8",
            size="720x1280",
            input_reference=image_path,
        )
        print("Video creation initiated. Video ID:", video.id)
        print("[STEP 7] ✓ Video creation initiated")
        break
    except Exception as e:
        last_exc = e
        print(f"[WARN] Video creation failed (attempt {attempt}/3): {e}")
        if attempt < 3:
            sleep_t = 2 ** (attempt - 1)
            print(f"[INFO] Retrying video creation in {sleep_t}s...")
            time.sleep(sleep_t)

if video is None:
    print(f"[ERROR] Video creation failed after retries: {last_exc}")
    sys.exit(1)

# Step 5: Save video info to CSV
print("[STEP 8] Saving video info to CSV...")
save_video_to_csv(video, current_time=current_time, filename=generated_lines_path)
print("[STEP 8] ✓ Video info saved to CSV")

# Step 6: Optionally download the video file
print("[STEP 9] Starting video download...")
download_video(video.id, f"GeneratedVideos/{current_time}.mp4")
print("[STEP 9] ✓ Video download initiated")