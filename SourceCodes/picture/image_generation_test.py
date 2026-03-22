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
    print(f"[DEBUG] ===== generate_first_frame 开始 =====")
    print(f"[DEBUG] 参数: reference_path={reference_path}, output_path={output_path}, prompt={prompt}, size={size}")

    # If no prompt provided, build it from DEFAULT_PROMPT + a GPT-generated description
    if prompt is None:
        print(f"[DEBUG] 提示词为空，开始生成自定义提示词...")
        # Try to read Time and Location from the suggestion CSV using time mapping
        try:
            row_idx = get_rowidx_from_time()
            print(f"[DEBUG] 从CSV读取行索引: {row_idx}")
            with open(suggestion_csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                print(f"[DEBUG] CSV总行数: {len(rows)}")
                if 0 <= row_idx < len(rows):
                    time_val = rows[row_idx].get("Time", "")
                    location_val = rows[row_idx].get("Location", "")
                    print(f"[DEBUG] 读取到时间: {time_val}, 地点: {location_val}")
                else:
                    time_val = ""
                    location_val = ""
                    print(f"[DEBUG] 行索引超出范围，使用空值")
        except Exception as e:
            print(f"[ERROR] 读取CSV失败: {e}")
            time_val = ""
            location_val = ""

        # Ask GPT to imagine a likely pet behavior given Time and Location
        try:
            user_msg = (
                f"Imagine a possible pet behavior scenario based on the following time and location, and describe it in one sentence to provide details for use as the first frame of an animation."
                f" Time: {time_val}; Location: {location_val}。"
            )
            print(f"[DEBUG] GPT提示词: {user_msg}")

            def _call_gpt():
                print(f"[DEBUG] 开始调用GPT-5模型...")
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
            print(f"[DEBUG] GPT生成结果: {gpt_part}")
        except Exception as e:
            print(f"[ERROR] GPT生成失败，使用回退描述: {e}")
            import traceback
            traceback.print_exc()
            gpt_part = "Specifically, the image shows the dog running on a playground track, with some people strolling slowly after their meal."

        prompt = DEFAULT_PROMPT.strip() + " " + gpt_part
        print(f"[DEBUG] 最终提示词: {prompt[:100]}...")
    if reference_path is None:
        reference_path = Path("VirtualPictures/cute_lucky_720P.png")
    else:
        reference_path = Path(reference_path)
    if output_path is None:
        output_path = Path("VirtualPictures/first_frame.png")
    else:
        output_path = Path(output_path)

    print(f"[DEBUG] 参考图片路径: {reference_path}")
    print(f"[DEBUG] 输出图片路径: {output_path}")
    print(f"[DEBUG] 检查参考图片是否存在: {reference_path.exists()}")

    # Call image edit with retries. On failure, fall back to copying the reference image.
    result = None
    last_exc = None
    for attempt in range(1, 4):
        try:
            print(f"[DEBUG] 第{attempt}次尝试编辑图片...")
            print(f"[DEBUG] 使用模型: gpt-image-1")
            print(f"[DEBUG] 打开参考图片: {reference_path}")
            with open(reference_path, "rb") as ref_file:
                ref_file_size = len(ref_file.read())
                ref_file.seek(0)
                print(f"[DEBUG] 参考图片大小: {ref_file_size} 字节")
                print(f"[DEBUG] 开始调用API...")
                result = client.images.edit(
                    model="gpt-image-1",
                    image=[ref_file],
                    prompt=prompt,
                    size=size,
                )
                print(f"[DEBUG] API调用成功!")
            break
        except (_openai.APIConnectionError, _openai.APITimeoutError, Exception) as e:
            last_exc = e
            print(f"[WARN] 图片编辑失败 (第{attempt}次尝试): {e}")
            import traceback
            traceback.print_exc()
            if attempt < 3:
                sleep_t = 2 ** (attempt - 1)
                print(f"[INFO] {sleep_t}秒后重试...")
                _time.sleep(sleep_t)

    if result is None:
        print(f"[ERROR] ===== 图片编辑重试后仍失败 =====")
        print(f"[ERROR] 错误信息: {last_exc}")
        print(f"[DEBUG] 开始回退方案: 复制参考图片")
        # Ensure output dir exists and copy reference image to output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copyfile(reference_path, output_path)
            print(f"[DEBUG] 回退成功: 已复制 {reference_path} -> {output_path}")
            return str(output_path)
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Failed to create fallback image: {e}")

    print(f"[DEBUG] ===== 图片编辑成功 =====")
    image_base64 = result.data[0].b64_json
    print(f"[DEBUG] base64编码长度: {len(image_base64)}")
    image_bytes = base64.b64decode(image_base64)
    print(f"[DEBUG] 解码后图片大小: {len(image_bytes)} 字节")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[DEBUG] 保存图片到: {output_path}")
    with open(output_path, "wb") as f:
        f.write(image_bytes)
    print(f"[DEBUG] 图片保存完成: {output_path}")
    print(f"[DEBUG] ===== generate_first_frame 完成 =====")
    return str(output_path)


if __name__ == "__main__":
    generate_first_frame()