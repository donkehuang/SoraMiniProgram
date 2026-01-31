#!/usr/bin/env python3
"""
测试OpenAI API连接
"""

from openai import OpenAI
import time

print("="*60)
print("测试OpenAI API连接")
print("="*60)

# 初始化客户端
client = OpenAI(
    api_key='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',
    timeout=300.0,
    max_retries=3,
    base_url="https://api.openai-proxy.com/v1"
)

print(f"\n[配置] API基础URL: {client.base_url}")
print(f"[配置] 超时时间: {client.timeout}秒")
print(f"[配置] 最大重试: {client.max_retries}")

# 测试1：简单的文本生成（快速验证连接）
print("\n" + "="*60)
print("测试1: 简单的文本生成（验证连接）")
print("="*60)

try:
    print("\n[测试] 发送请求...")
    start_time = time.time()

    response = client.responses.create(
        model="gpt-4o-mini",
        input="Say 'Hello World!' in one word."
    )

    elapsed = time.time() - start_time
    print(f"\n✅ 成功！响应: {response.output_text}")
    print(f"   耗时: {elapsed:.2f}秒")

except Exception as e:
    print(f"\n❌ 失败: {str(e)}")
    print(f"   建议:")
    print(f"   1. 检查网络连接")
    print(f"   2. 检查API密钥是否有效")
    print(f"   3. 检查代理服务是否可用")

# 测试2：创建视频任务（可能需要更长时间）
print("\n" + "="*60)
print("测试2: 创建视频任务（可能需要较长时间）")
print("="*60)

test_prompt = input("\n是否测试视频生成？(y/n): ").strip().lower()

if test_prompt == 'y':
    try:
        print("\n[测试] 创建视频任务...")
        print(f"[提示] prompt: '一只可爱的小猫'")
        print(f"[提示] 这可能需要30秒到2分钟...")

        start_time = time.time()

        video = client.videos.create(
            prompt="一只可爱的小猫在草地上奔跑",
            model="sora-2",
            seconds="8",
            size="720x1280"
        )

        elapsed = time.time() - start_time

        print(f"\n✅ 视频任务创建成功！")
        print(f"   视频ID: {video.id}")
        print(f"   耗时: {elapsed:.2f}秒")
        print(f"   状态: {video.status}")

    except Exception as e:
        print(f"\n❌ 失败: {str(e)}")
        print(f"\n[建议] 可能的原因:")
        print(f"   1. 网络连接不稳定")
        print(f"   2. API服务器响应慢")
        print(f"   3. 代理服务出现问题")

        print(f"\n[尝试] 检查网络:")
        print(f"   - ping api.openai-proxy.com")
        print(f"   - 检查防火墙设置")
        print(f"   - 尝试切换网络环境")

else:
    print("\n[跳过] 跳过视频生成测试")

print("\n" + "="*60)
print("测试完成")
print("="*60)
