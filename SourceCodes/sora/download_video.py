
from openai import OpenAI
import sys
import time

openai = OpenAI()


def download_video(video_id, vide_name="video.mp4"):
    video = openai.videos.retrieve(video_id)
    progress = getattr(video, "progress", 0)
    bar_length = 30
    while video.status in ("in_progress", "queued"):
        # Refresh status
        video = openai.videos.retrieve(video.id)
        progress = getattr(video, "progress", 0)

        filled_length = int((progress / 100) * bar_length)
        bar = "=" * filled_length + "-" * (bar_length - filled_length)
        status_text = "Queued" if video.status == "queued" else "Processing"

        sys.stdout.write(f"{status_text}: [{bar}] {progress:.1f}%")
        sys.stdout.flush()
        time.sleep(2)

    # Move to next line after progress loop
    sys.stdout.write("")

    if video.status == "failed":
        message = getattr(
            getattr(video, "error", None), "message", "Video generation failed"
        )
        print(message)
        return

    print("Video generation completed:", video)
    print("Downloading video content...")

    content = openai.videos.download_content(video.id, variant="video")

    content.write_to_file(vide_name)

    print("Wrote video.mp4")

if __name__ == "__main__":
    download_video("video_6978e985d2c481908830ad0336d2e46809de8abbe292c89a")
