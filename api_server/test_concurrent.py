#!/usr/bin/env python3
"""
Sora API 并发压力测试
测试单worker配置下的并发处理能力
"""

import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

API_BASE_URL = "http://8.211.175.227:5000"

def test_health_check():
    """测试健康检查接口"""
    print("\n" + "="*60)
    print("测试1: 健康检查")
    print("="*60)
    
    start = time.time()
    response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
    elapsed = time.time() - start
    
    print(f"✅ 响应时间: {elapsed:.3f}秒")
    print(f"响应内容: {response.json()}")
    return response.status_code == 200

def test_concurrent_health_checks(num_requests=10):
    """测试并发健康检查"""
    print("\n" + "="*60)
    print(f"测试2: 并发健康检查 ({num_requests}个并发请求)")
    print("="*60)
    
    def single_request(index):
        start = time.time()
        try:
            response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
            elapsed = time.time() - start
            return {
                'index': index,
                'success': True,
                'elapsed': elapsed,
                'status': response.status_code
            }
        except Exception as e:
            return {
                'index': index,
                'success': False,
                'error': str(e)
            }
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        futures = [executor.submit(single_request, i) for i in range(num_requests)]
        results = [f.result() for f in as_completed(futures)]
    
    total_time = time.time() - start_time
    
    success_count = sum(1 for r in results if r.get('success'))
    avg_response_time = sum(r.get('elapsed', 0) for r in results if r.get('success')) / success_count if success_count > 0 else 0
    
    print(f"\n总耗时: {total_time:.3f}秒")
    print(f"成功请求: {success_count}/{num_requests}")
    print(f"平均响应时间: {avg_response_time:.3f}秒")
    print(f"并发处理能力: ✅ 良好" if success_count == num_requests else f"⚠️ 部分失败")
    
    return success_count == num_requests

def test_optimize_prompt_concurrent(num_requests=3):
    """测试并发GPT优化（较重的请求）"""
    print("\n" + "="*60)
    print(f"测试3: 并发GPT优化 ({num_requests}个并发请求)")
    print("="*60)
    
    def optimize_request(index):
        start = time.time()
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/optimize-prompt",
                json={
                    "userDescription": f"测试描述{index}",
                    "styleTemplate": "test template",
                    "duration": "4秒"
                },
                timeout=30
            )
            elapsed = time.time() - start
            return {
                'index': index,
                'success': response.status_code == 200,
                'elapsed': elapsed,
                'status': response.status_code
            }
        except Exception as e:
            return {
                'index': index,
                'success': False,
                'error': str(e)
            }
    
    print("⚠️  这个测试会调用OpenAI API，可能产生费用")
    confirm = input("是否继续？(y/n): ").strip().lower()
    
    if confirm != 'y':
        print("已跳过")
        return True
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        futures = [executor.submit(optimize_request, i) for i in range(num_requests)]
        results = [f.result() for f in as_completed(futures)]
    
    total_time = time.time() - start_time
    
    success_count = sum(1 for r in results if r.get('success'))
    
    print(f"\n总耗时: {total_time:.3f}秒")
    print(f"成功请求: {success_count}/{num_requests}")
    
    for r in sorted(results, key=lambda x: x['index']):
        status = "✅" if r.get('success') else "❌"
        print(f"  请求{r['index']}: {status} {r.get('elapsed', 0):.3f}秒")
    
    return success_count == num_requests

def analyze_architecture():
    """分析当前架构的并发能力"""
    print("\n" + "="*60)
    print("架构分析")
    print("="*60)
    
    print("\n当前配置:")
    print("  - Worker数量: 1")
    print("  - Worker类型: sync")
    print("  - 超时时间: 600秒")
    print("  - 后台处理: threading.Thread")
    
    print("\n并发能力:")
    print("  ✅ 轻量请求（health check）: 可以并发处理")
    print("  ✅ 视频生成请求: 可以同时接收多个（立即返回）")
    print("  ✅ 后台线程: 可以同时处理多个视频生成")
    print("  ⚠️  重量请求（GPT优化）: 可能排队等待")
    
    print("\n推荐并发数:")
    print("  - 轻量请求: 10-50个并发")
    print("  - 视频生成: 5-10个同时生成（受OpenAI限制）")
    print("  - GPT优化: 3-5个并发（避免排队）")
    
    print("\n优化建议:")
    print("  1. 如果用户量大（>100），考虑增加到2-4个worker")
    print("  2. 如果需要更高并发，使用gevent或eventlet worker")
    print("  3. 添加Redis缓存，共享video_tasks状态")
    print("  4. 添加请求队列（Celery）处理耗时任务")

if __name__ == "__main__":
    print("="*60)
    print("Sora API 并发压力测试")
    print("="*60)
    
    # 测试1: 基础健康检查
    if not test_health_check():
        print("❌ 健康检查失败，请检查服务是否运行")
        exit(1)
    
    # 测试2: 并发健康检查
    test_concurrent_health_checks(10)
    
    # 测试3: 并发GPT优化（可选）
    test_optimize_prompt_concurrent(3)
    
    # 架构分析
    analyze_architecture()
    
    print("\n" + "="*60)
    print("✅ 测试完成")
    print("="*60)
