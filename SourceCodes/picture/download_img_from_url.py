import requests
import os

def download_image_from_url(image_url, save_path="downloaded_image.jpg"):
    """
    从URL下载图片并保存到本地
    :param image_url: 图片的直接URL（如 https://xxx.com/xxx.jpg）
    :param save_path: 本地保存路径（默认当前目录下 downloaded_image.jpg）
    :return: 布尔值，下载成功返回True，失败返回False
    """
    # 请求头：模拟浏览器访问，避免被防盗链拦截
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        # 发送GET请求，获取图片二进制数据（stream=True 避免大文件占用过多内存）
        response = requests.get(image_url, headers=headers, stream=True, timeout=10)
        # 检查请求是否成功（状态码200表示成功）
        response.raise_for_status()

        # 确保保存目录存在
        save_dir = os.path.dirname(save_path)
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # 写入本地文件（二进制模式）
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print(f"✅ 图片下载成功！保存路径：{save_path}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ 下载失败：{str(e)}")
        return False
    except IOError as e:
        print(f"❌ 文件保存失败：{str(e)}")
        return False

# ===================== 调用示例 =====================
if __name__ == "__main__":
    # 替换为你的图片URL（必须是直接的图片链接，不是网页链接）
    IMAGE_URL = "https://example.com/your_image.jpg"
    # 自定义保存路径（可选）
    SAVE_PATH = "my_image.png"
    download_image_from_url(IMAGE_URL, SAVE_PATH)