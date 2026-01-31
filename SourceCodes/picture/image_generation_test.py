import base64
import csv
import sys
import time as _time
import shutil
from pathlib import Path
from openai import OpenAI
import openai as _openai

# Allow running this file directly by fixing import path when needed
try:
    from dialogue.extract_prompt_from_time import get_rowidx_from_time
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from dialogue.extract_prompt_from_time import get_rowidx_from_time

client = OpenAI()


def _retry_call(func, desc="API call", max_retries=3, backoff=2):
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            return func()
        except (_openai.APIConnectionError, _openai.APITimeoutError, Exception) as e:
            last_exc = e
            print(f"[WARN] {desc} failed (attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                sleep_t = backoff ** (attempt - 1)
                print(f"[INFO] Retrying in {sleep_t}s...")
                _time.sleep(sleep_t)
    # re-raise last exception after exhausting retries
    raise last_exc

DEFAULT_PROMPT = """
Based on the puppy in the reference image, generate an animated image for it; this generated image will serve as the first frame of the animation.
"""


def generate_first_frame(reference_path=None, output_path=None, prompt=None, size="1024x1536", suggestion_csv_path="ScriptsLists/prompts.csv"):
    """Generate an edited image based on a reference and save it to `output_path`.
    Returns the output file path as a string.
    """
    # If no prompt provided, build it from DEFAULT_PROMPT + a GPT-generated description
    if prompt is None:
        # Try to read Time and Location from the suggestion CSV using time mapping
        try:
            row_idx = get_rowidx_from_time()
            with open(suggestion_csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                if 0 <= row_idx < len(rows):
                    time_val = rows[row_idx].get("Time", "")
                    location_val = rows[row_idx].get("Location", "")
                else:
                    time_val = ""
                    location_val = ""
        except Exception:
            time_val = ""
            location_val = ""

        # Ask GPT to imagine a likely pet behavior given Time and Location
        try:
            user_msg = (
                f"Imagine a possible pet behavior scenario based on the following time and location, and describe it in one sentence to provide details for use as the first frame of an animation."
                f" Time: {time_val}; Location: {location_val}。"
            )

            def _call_gpt():
                return client.responses.create(
                    model="gpt-5",
                    reasoning={"effort": "low"},
                    input=[
                        {"role": "developer", "content": "Generate a short, vivid scene description for an animated pet first-frame."},
                        {"role": "user", "content": user_msg},
                    ],
                )

            response = _retry_call(_call_gpt, desc="GPT scene generation")
            gpt_part = response.output_text.strip()
        except Exception as e:
            print(f"[ERROR] GPT generation failed, using fallback description: {e}")
            gpt_part = "Specifically, the image shows the dog running on a playground track, with some people strolling slowly after their meal."

        prompt = DEFAULT_PROMPT.strip() + " " + gpt_part
    if reference_path is None:
        reference_path = Path("VirtualPictures/cute_lucky_720P.png")
    else:
        reference_path = Path(reference_path)
    if output_path is None:
        output_path = Path("VirtualPictures/first_frame.png")
    else:
        output_path = Path(output_path)

    # Call image edit with retries. On failure, fall back to copying the reference image.
    result = None
    last_exc = None
    for attempt in range(1, 4):
        try:
            with open(reference_path, "rb") as ref_file:
                result = client.images.edit(
                    model="gpt-image-1",
                    image=[ref_file],
                    prompt=prompt,
                    size=size,
                )
            break
        except (_openai.APIConnectionError, _openai.APITimeoutError, Exception) as e:
            last_exc = e
            print(f"[WARN] Image edit failed (attempt {attempt}/3): {e}")
            if attempt < 3:
                sleep_t = 2 ** (attempt - 1)
                print(f"[INFO] Retrying image edit in {sleep_t}s...")
                _time.sleep(sleep_t)

    if result is None:
        print(f"[ERROR] Image edit failed after retries: {last_exc}. Falling back to copying reference image.")
        # Ensure output dir exists and copy reference image to output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copyfile(reference_path, output_path)
            return str(output_path)
        except Exception as e:
            raise RuntimeError(f"Failed to create fallback image: {e}")

    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(image_bytes)

    return str(output_path)


if __name__ == "__main__":
    generate_first_frame()