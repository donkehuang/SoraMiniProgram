#!/usr/bin/env python3
"""
测试视频URL是否可访问
"""

import requests
import os

def test_video_url(video_url):
    """测试视频URL"""
    print("="*60)
    print("测试视频URL访问")
    print("="*60)

    print(f"\n[请求] URL: {video_url}")

    try:
        # 发送HEAD请求（不下载整个文件）
        response = requests.head(video_url, timeout=5)

        print(f"\n[响应] 状态码: {response.status_code}")
        print(f"[响应] Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"[响应] Content-Length: {response.headers.get('Content-Length', 'N/A')} 字节")

        # 检查是否成功
        if response.status_code == 200:
            print("\n✅ 视频URL可以访问！")

            # 尝试下载前100字节验证
            print("\n[验证] 下载前100字节...")
            response = requests.get(video_url, timeout=5, stream=True)
            data = next(response.iter_content(100))
            print(f"[验证] 下载成功，文件前几字节: {data[:20]}")

            return True
        else:
            print(f"\n❌ HTTP错误: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败: 无法连接到服务器")
        print("[建议] 检查:")
        print("  1. API服务器是否正在运行")
        print("  2. URL是否正确")
        print("  3. 网络连接是否正常")
        return False

    except requests.exceptions.Timeout:
        print("\n❌ 超时: 请求超时")
        print("[建议] 检查网络连接或增加超时时间")
        return False

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def check_video_file(file_path):
    """检查本地视频文件"""
    print("\n" + "="*60)
    print("检查本地视频文件")
    print("="*60)

    print(f"\n[文件] 路径: {file_path}")

    if not os.path.exists(file_path):
        print(f"\n❌ 文件不存在")
        return False

    file_size = os.path.getsize(file_path)
    print(f"[文件] 大小: {file_size} 字节 ({file_size / 1024 / 1024:.2f} MB)")

    if file_size < 1000:
        print(f"\n⚠️  文件大小异常（小于1KB）")
        return False

    print(f"\n✅ 文件正常")

    # 检查文件前几个字节（MP4文件头）
    with open(file_path, 'rb') as f:
        header = f.read(12)
        print(f"[文件] 文件头: {header.hex()}")

        # MP4文件通常以00 00 00开头，或者ftyp
        if header.startswith(b'\x00\x00\x00') or b'ftyp' in header:
            print(f"[文件] 看起来是有效的MP4文件")
        else:
            print(f"[警告] 文件头不是标准的MP4格式")

    return True


if __name__ == '__main__':
    import sys

    # 检查参数
    if len(sys.argv) > 1:
        video_id = sys.argv[1]
    else:
        # 使用最近的视频
        videos_dir = "generated_videos"
        if not os.path.exists(videos_dir):
            print(f"错误: 找不到 {videos_dir} 目录")
            sys.exit(1)

        # 获取最新的视频文件
        video_files = [f for f in os.listdir(videos_dir) if f.endswith('.mp4')]
        if not video_files:
            print("错误: 找不到任何视频文件")
            sys.exit(1)

        video_files.sort(key=lambda x: os.path.getmtime(os.path.join(videos_dir, x)), reverse=True)
        latest_video = video_files[0]
        video_id = latest_video.replace('.mp4', '')

    print(f"\n[选择] 视频ID: {video_id}")

    # 检查本地文件
    file_path = os.path.join("generated_videos", f"{video_id}.mp4")
    check_video_file(file_path)

    # 测试URL访问
    video_url = f"http://localhost:5000/videos/{video_id}.mp4"
    test_video_url(video_url)

    print("\n" + "="*60)
    print("测试完成")
    print("="*60)
