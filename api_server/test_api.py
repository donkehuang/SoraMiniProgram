#!/usr/bin/env python3
"""
测试API服务器的脚本
运行前请确保: python sora_api.py 已启动
"""

import requests
import json

# API服务器地址
API_BASE_URL = "http://localhost:5000"

def test_health():
    """测试健康检查接口"""
    print("\n" + "="*50)
    print("测试健康检查接口...")
    print("="*50)

    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_generate_video():
    """测试视频生成接口"""
    print("\n" + "="*50)
    print("测试视频生成接口...")
    print("="*50)

    try:
        # 测试数据
        test_data = {
            "prompt": "一只可爱的小猫在草地上奔跑，阳光明媚",
            "seconds": "8"
        }

        print(f"发送请求: {json.dumps(test_data, ensure_ascii=False)}")

        response = requests.post(
            f"{API_BASE_URL}/api/generate-video",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )

        print(f"\n状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")

        try:
            response_data = response.json()
            print(f"\n响应数据:")
            print(json.dumps(response_data, ensure_ascii=False, indent=2))

            if response.status_code == 200 and response_data.get('success'):
                print("\n✅ 测试成功！")
                return True
            else:
                print(f"\n❌ 测试失败: {response_data.get('error', '未知错误')}")
                return False
        except:
            print(f"\n❌ 响应不是有效的JSON格式")
            print(f"原始响应: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到API服务器")
        print("请确认:")
        print("  1. python sora_api.py 已启动")
        print("  2. 服务器运行在 http://localhost:5000")
        print("  3. 防火墙没有阻止端口5000")
        return False
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*60)
    print("Sora API 服务器测试工具")
    print("="*60)

    # 测试健康检查
    health_ok = test_health()

    if not health_ok:
        print("\n⚠️  健康检查失败，请检查API服务器是否启动")
        return

    print("\n" + "✅"*30)
    print("API服务器运行正常")
    print("✅"*30)

    # 询问是否测试视频生成
    print("\n" + "="*60)
    print("是否测试视频生成接口？")
    print("注意: 这将实际调用Sora API，可能产生费用")
    print("="*60)

    choice = input("\n输入 'y' 继续测试，其他键跳过: ").strip().lower()

    if choice == 'y':
        test_generate_video()
    else:
        print("\n跳过视频生成测试")

    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    main()
