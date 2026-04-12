import base64
from openai import OpenAI
from PIL import Image

client = OpenAI()

# 步骤1: 使用 gpt-image-1.5 编辑图片
prompt = """
Make the person in the image smile naturally and happily.
"""

print("步骤1: 使用 gpt-image-1.5 编辑图片...")
result = client.images.edit(
    model="gpt-image-1.5",
    image=[open("RawPictures\\sad_man_test.jpg", "rb")],
    size="1024x1024",
    prompt=prompt
)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# 保存编辑后的图片
edited_image_path = "RawPictures\\sad_man_test_edited.jpg"
with open(edited_image_path, "wb") as f:
    f.write(image_bytes)
print(f"✅ 编辑后的图片已保存: {edited_image_path}")

# 步骤2: 使用编辑后的图片作为首帧生成视频
print("\n步骤2: 使用编辑后的图片生成视频...")
video_prompt = "A calico cat playing a piano on stage"

# 使用编辑后的图片作为 input_reference 生成视频
video = client.videos.create(
    model="sora-2",
    prompt=video_prompt,
    input_reference=open(edited_image_path, "rb"),
    size="1024x1792",
    seconds="4"
)

print(f"✅ 视频任务创建成功")
print(f"Video ID: {video.id}")
print(f"Video status: {video.status}")