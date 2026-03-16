from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from openai import OpenAI
import time
import os
import logging
import threading
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
# 允许跨域请求，支持所有来源和请求头
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 配置 - 使用绝对路径避免路径问题
VIDEOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_videos")
print(f"[配置] 视频存储目录: {VIDEOS_DIR}")
Path(VIDEOS_DIR).mkdir(exist_ok=True)

# 存储视频任务状态
video_tasks = {}  # {video_id: {status, progress, local_path, error}}

# 初始化OpenAI客户端
# 从环境变量读取API Key
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("未设置 OPENAI_API_KEY 环境变量！请在 .env 文件中配置")

base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')

client = OpenAI(
    api_key=api_key,
    timeout=300.0,  # 设置5分钟超时
    max_retries=3,  # 最大重试次数
    base_url=base_url
)

print(f"[配置] OpenAI客户端已初始化")
print(f"[配置] API基础URL: {client.base_url}")
print(f"[配置] 超时时间: {client.timeout}秒")

def process_video_async(video_id, local_filename):
    """异步处理视频生成和下载"""
    try:
        print(f"[异步处理] 开始处理视频: {video_id}")

        # 轮询查询视频状态
        bar_length = 30
        while True:
            video = client.videos.retrieve(video_id)
            progress = getattr(video, "progress", 0)

            filled_length = int((progress / 100) * bar_length)
            bar = "=" * filled_length + "-" * (bar_length - filled_length)

            status_map = {
                'queued': '排队中',
                'in_progress': '处理中',
                'completed': '已完成',
                'failed': '失败'
            }
            status_text = status_map.get(video.status, video.status)

            # 更新任务状态
            video_tasks[video_id].update({
                'status': video.status,
                'progress': progress
            })
            print(f"[进度] {status_text}: [{bar}] {progress:.1f}%")

            if video.status in ("in_progress", "queued"):
                time.sleep(3)
            else:
                break

        if video.status == "failed":
            error_message = getattr(
                getattr(video, "error", None), "message", "视频生成失败"
            )
            print(f"[失败] {error_message}")
            video_tasks[video_id].update({
                'status': 'failed',
                'error': error_message
            })
            return

        # 视频生成完成，下载视频
        print(f"[完成] 视频生成完成，开始下载...")
        print(f"[下载] 视频ID: {video_id}")
        print(f"[下载] 目标路径: {os.path.join(VIDEOS_DIR, local_filename)}")

        try:
            # 开始下载
            print(f"[下载] 正在从 OpenAI 下载视频...")
            content = client.videos.download_content(video.id, variant="video")
            local_path = os.path.join(VIDEOS_DIR, local_filename)

            # 写入文件
            print(f"[下载] 正在写入本地文件...")
            content.write_to_file(local_path)

            # 验证文件是否存在
            if not os.path.exists(local_path):
                print(f"[错误] ❌ 文件未成功创建: {local_path}")
                video_tasks[video_id].update({
                    'status': 'failed',
                    'error': '视频文件下载失败'
                })
                return

            # 验证文件大小
            file_size = os.path.getsize(local_path)
            print(f"[下载] ✅ 视频已保存到: {local_path}")
            print(f"[下载] ✅ 文件大小: {file_size} 字节 ({file_size / 1024 / 1024:.2f} MB)")

            if file_size == 0:
                print(f"[错误] ❌ 文件大小为0: {local_path}")
                video_tasks[video_id].update({
                    'status': 'failed',
                    'error': '视频文件损坏（大小为0）'
                })
                return

            # 更新任务状态为完成
            video_tasks[video_id].update({
                'status': 'completed',
                'progress': 100,
                'local_path': local_path,
                'file_size': file_size
            })
            print(f"[完成] ✅ 视频处理完成: {video_id}")

        except Exception as download_error:
            print(f"[错误] ❌ 视频下载失败: {str(download_error)}")
            import traceback
            traceback.print_exc()
            video_tasks[video_id].update({
                'status': 'failed',
                'error': f'视频下载失败: {str(download_error)}'
            })

    except Exception as e:
        print(f"[错误] 异步处理异常: {str(e)}")
        import traceback
        traceback.print_exc()
        video_tasks[video_id].update({
            'status': 'failed',
            'error': str(e)
        })


@app.route('/api/optimize-prompt', methods=['POST', 'OPTIONS'])
def optimize_prompt():
    """使用GPT优化提示词"""
    
    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        print(f"[GPT优化] 收到提示词优化请求")
        
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据格式错误'
            }), 400
        
        user_description = data.get('userDescription', '')
        style_template = data.get('styleTemplate', '')
        duration = data.get('duration', '4秒')
        
        print(f"[GPT优化] 用户描述: {user_description}")
        print(f"[GPT优化] 风格模板: {style_template[:50]}...")
        print(f"[GPT优化] 时长: {duration}")
        
        if not user_description or not style_template:
            return jsonify({
                'success': False,
                'error': '缺少必要参数'
            }), 400
        
        # 构建GPT优化提示
        system_prompt = """You are a professional video script optimizer specialized in creating viral TikTok-style short videos. 
Your task is to combine user's video description with a specific style template to generate an optimized, detailed video prompt for AI video generation.

Guidelines:
1. Maintain the style template's structure and key elements (timing, effects, transitions)
2. Replace placeholder keywords in [brackets] with user's specific content
3. Keep all technical specifications (duration, camera movements, effects)
4. Ensure the output is cinematic, detailed, and generation-ready
5. Output ONLY the optimized prompt, no explanations"""

        user_prompt = f"""Style Template ({duration}):
{style_template}

User's Video Description:
{user_description}

Please generate an optimized video generation prompt by combining the style template with the user's description. Replace all [placeholders] with specific content from the user's description while maintaining the template's structure and technical specifications."""

        print(f"[GPT优化] 开始调用GPT-4...")
        
        # 调用GPT进行优化
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        optimized_prompt = response.choices[0].message.content.strip()
        
        print(f"[GPT优化] 优化完成: {optimized_prompt[:100]}...")
        
        return jsonify({
            'success': True,
            'optimizedPrompt': optimized_prompt,
            'originalDescription': user_description
        }), 200
        
    except Exception as e:
        print(f"[GPT优化] 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'优化失败: {str(e)}'
        }), 500


@app.route('/api/generate-video', methods=['POST', 'OPTIONS'])
def generate_video():
    """生成视频的API接口"""

    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200

    try:
        print(f"[请求] 收到视频生成请求")

        data = request.json
        if not data:
            print("[错误] 请求数据为空")
            return jsonify({
                'success': False,
                'error': '请求数据格式错误'
            }), 400

        prompt = data.get('prompt', '')
        seconds = data.get('seconds', '12')
        size = data.get('size', '1280x720')

        print(f"[参数] prompt: {prompt[:50]}..., seconds: {seconds}, size: {size}")

        if not prompt:
            print("[错误] prompt为空")
            return jsonify({
                'success': False,
                'error': '请输入视频描述'
            }), 400

        print("[开始] 开始调用Sora API...")

        # 调用Sora API创建视频（立即返回）
        video = None
        last_exc = None
        for attempt in range(1, 4):
            try:
                video = client.videos.create(
                    prompt=prompt,
                    model="sora-2",
                    seconds=seconds,
                    size=size
                )
                print(f"[创建] 视频任务创建成功，视频ID: {video.id}")
                break
            except Exception as e:
                last_exc = e
                print(f"[警告] 视频创建失败 (尝试 {attempt}/3): {e}")
                if attempt < 3:
                    sleep_t = 2 ** (attempt - 1)
                    print(f"[信息] {sleep_t}秒后重试...")
                    time.sleep(sleep_t)

        if video is None:
            print(f"[失败] 视频创建失败: {str(last_exc)}")
            return jsonify({
                'success': False,
                'error': f'视频创建失败: {str(last_exc)}'
            }), 500

        # 初始化任务状态
        local_filename = f"{video.id}.mp4"
        video_tasks[video.id] = {
            'status': 'queued',
            'progress': 0,
            'local_path': None,
            'error': None
        }

        # 启动异步处理线程
        thread = threading.Thread(
            target=process_video_async,
            args=(video.id, local_filename),
            daemon=True
        )
        thread.start()

        # 立即返回任务ID（不等待完成）
        response_data = {
            'success': True,
            'videoId': video.id,
            'status': 'queued',
            'message': '视频生成任务已创建'
        }
        print(f"[响应] 返回任务信息: {response_data}")

        return jsonify(response_data), 200

    except Exception as e:
        print(f"[错误] 服务器异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@app.route('/api/video-status/<video_id>', methods=['GET'])
def get_video_status(video_id):
    """查询视频生成状态"""

    try:
        print(f"[查询] 查询视频状态: {video_id}")

        if video_id not in video_tasks:
            return jsonify({
                'success': False,
                'error': '视频任务不存在'
            }), 404

        task = video_tasks[video_id]

        response_data = {
            'success': True,
            'videoId': video_id,
            'status': task['status'],
            'progress': task['progress']
        }

        # 如果完成，提供本地URL
        if task['status'] == 'completed' and task['local_path']:
            # 返回相对路径供前端访问
            response_data['videoUrl'] = f'/videos/{video_id}.mp4'

        # 如果失败，返回错误信息
        if task['status'] == 'failed':
            response_data['error'] = task.get('error', '视频生成失败')

        print(f"[状态] 视频状态: {task['status']}, 进度: {task['progress']}%")
        return jsonify(response_data), 200

    except Exception as e:
        print(f"[错误] 查询状态异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        }), 500


@app.route('/videos/<filename>')
def serve_video(filename):
    """提供视频文件"""
    try:
        print(f"[视频服务] ============ 收到视频请求 ============")
        print(f"[视频服务] 请求视频: {filename}")
        print(f"[视频服务] 视频目录: {VIDEOS_DIR}")
        print(f"[视频服务] 视频目录绝对路径: {os.path.abspath(VIDEOS_DIR)}")

        # 列出目录中的所有文件
        try:
            all_files = os.listdir(VIDEOS_DIR)
            print(f"[视频服务] 目录中的文件数量: {len(all_files)}")
            if all_files:
                print(f"[视频服务] 文件列表: {all_files[:5]}...")  # 只显示前5个
        except Exception as e:
            print(f"[视频服务] 读取目录失败: {e}")

        # 检查文件是否存在
        file_path = os.path.join(VIDEOS_DIR, filename)
        file_path_abs = os.path.abspath(file_path)
        print(f"[视频服务] 检查文件路径: {file_path_abs}")
        print(f"[视频服务] 文件是否存在: {os.path.exists(file_path_abs)}")

        if not os.path.exists(file_path_abs):
            print(f"[视频服务] ❌ 文件不存在: {file_path_abs}")
            return jsonify({'error': '视频文件不存在', 'requested': filename}), 404

        file_size = os.path.getsize(file_path_abs)
        print(f"[视频服务] ✅ 找到文件，大小: {file_size} 字节 ({file_size / 1024 / 1024:.2f} MB)")
        print(f"[视频服务] 使用目录: {os.path.dirname(file_path_abs)}")

        # 发送视频文件，使用绝对路径避免路径问题
        try:
            response = send_from_directory(
                os.path.dirname(file_path_abs),
                filename,
                as_attachment=False,
                mimetype='video/mp4'
            )
            print(f"[视频服务] ✅ 返回视频文件")
            return response
        except Exception as send_error:
            print(f"[视频服务] send_from_directory失败: {send_error}")
            print(f"[视频服务] 尝试直接读取文件并发送...")
            # 备用方案：直接读取文件
            return send_file(
                file_path_abs,
                mimetype='video/mp4',
                as_attachment=False
            )

    except Exception as e:
        print(f"[视频服务] ❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'active_tasks': len(video_tasks)
    })


@app.route('/api/tasks', methods=['GET'])
def list_tasks():
    """列出所有任务（调试用）"""
    return jsonify({
        'success': True,
        'tasks': {k: {
            'status': v['status'],
            'progress': v['progress']
        } for k, v in video_tasks.items()}
    })


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 正在启动 Sora API 服务器...")
    print("=" * 60)

    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    domain = os.environ.get('DOMAIN', 'www.enfuri51.xyz')
    
    print(f"📍 服务端口: {port}")
    print(f"🌐 HTTPS域名: https://{domain}")
    print(f"📁 视频存储目录: {os.path.abspath(VIDEOS_DIR)}")
    print(f"🔧 调试模式: {debug_mode}")
    print("=" * 60)
    print(f"✅ API地址: https://{domain}/api/health")
    print("=" * 60)

    app.run(host='0.0.0.0', port=port, debug=debug_mode)
