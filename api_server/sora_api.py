from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from openai import OpenAI
import time
import os
import logging
import threading
import base64
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image

# 加载环境变量
load_dotenv()

# 违禁词列表
BANNED_WORDS = [
    # 色情类
    'porn', 'sex', 'nude', 'naked', 'naked body', 'breast', 'breasts',
    '性感', '裸体', '色情', '成人', '淫秽', '露骨',

    # 暴力类
    'kill', 'murder', 'blood', 'gore', 'violence', 'death', 'dead',
    'torture', 'cruel', 'brutal', 'massacre', 'slaughter',
    '杀人', '谋杀', '血腥', '暴力', '死亡', '屠杀', '酷刑',

    # 恐怖类
    'horror', 'scary', 'terrifying', 'frightening', 'creepy',
    '恐怖', '可怕', '惊悚',

    # 政治类
    'politics', 'political', 'government', 'protest', 'riot',
    '政治', '政府', '抗议', '暴动',

    # 仇恨言论类
    'hate', 'racist', 'discrimination', 'racism', 'nazi', 'terrorist',
    '仇恨', '种族歧视', '歧视', '纳粹', '恐怖分子',

    # 违法类
    'drug', 'illegal', 'crime', 'steal', 'robbery', 'fraud',
    '毒品', '违法', '犯罪', '偷窃', '抢劫', '诈骗',

    # 其他不当内容
    'self-harm', 'suicide', 'abuse', 'harassment',
    '自残', '自杀', '虐待', '骚扰'
]

def contains_banned_words(text):
    """检查文本是否包含违禁词"""
    if not text:
        return False

    text_lower = text.lower()
    found_words = []

    for word in BANNED_WORDS:
        if word.lower() in text_lower:
            found_words.append(word)

    if found_words:
        print(f"[违禁词检测] 发现违禁词: {', '.join(found_words)}")
        return True, found_words

    return False, []

def validate_prompt(prompt):
    """验证prompt是否合法"""
    is_banned, found_words = contains_banned_words(prompt)

    if is_banned:
        return False, f"内容包含违禁词汇，请修改提示词后重试"

    return True, None

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
        "methods": ["GET", "POST", "OPTIONS", "HEAD"],
        "allow_headers": ["Content-Type", "Authorization", "Range"],
        "expose_headers": ["Content-Length", "Content-Range"]
    }
})

# 配置 - 使用绝对路径避免路径问题
VIDEOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_videos")
IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_images")
print(f"[配置] 视频存储目录: {VIDEOS_DIR}")
print(f"[配置] 图片存储目录: {IMAGES_DIR}")
Path(VIDEOS_DIR).mkdir(exist_ok=True)
Path(IMAGES_DIR).mkdir(exist_ok=True)

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

# 初始化Kimi客户端 (用于Vision API)
moonshot_api_key = os.getenv('MOONSHOT_API_KEY')
kimi_client = None
if moonshot_api_key:
    kimi_client = OpenAI(
        api_key=moonshot_api_key,
        base_url="https://api.moonshot.cn/v1",
        timeout=300.0,
        max_retries=3
    )
    print(f"[配置] Kimi客户端已初始化")
else:
    print(f"[警告] 未设置 MOONSHOT_API_KEY，将使用OpenAI Vision API")

print(f"[配置] OpenAI客户端已初始化")
print(f"[配置] API基础URL: {client.base_url}")
print(f"[配置] 超时时间: {client.timeout}秒")

def edit_image_with_openai(image_path, prompt):
    """使用OpenAI images.edit接口编辑图片"""
    try:
        # 读取图片
        with open(image_path, 'rb') as f:
            image_file = f.read()

        # 调用images.edit接口
        response = client.images.edit(
            model="gpt-image-1.5",
            image=image_file,
            prompt=prompt
        )

        # 获取生成的图片base64
        image_b64 = response.data[0].b64_json

        # 解码base64为bytes
        image_bytes = base64.b64decode(image_b64)

        print(f"[图片编辑] 编辑成功")
        return image_bytes

    except Exception as e:
        print(f"[图片编辑] 编辑失败: {e}")
        raise e

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

            # 尝试读取文件前100字节来验证文件可读
            try:
                with open(local_path, 'rb') as f:
                    header = f.read(100)
                print(f"[验证] ✅ 文件可读，文件头: {header[:20].hex()}...")
            except Exception as read_error:
                print(f"[错误] ❌ 文件不可读: {read_error}")
                video_tasks[video_id].update({
                    'status': 'failed',
                    'error': f'视频文件不可读: {str(read_error)}'
                })
                return

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

        # 检查违禁词
        is_valid, error_msg = validate_prompt(user_description)
        if not is_valid:
            print(f"[GPT优化][违禁词] {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
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
        image_url = data.get('imageUrl', '')  # 可选：参考图片URL

        print(f"[参数] prompt: {prompt[:50]}..., seconds: {seconds}, size: {size}")
        if image_url:
            print(f"[参数] 参考图片: {image_url}")

        if not prompt:
            print("[错误] prompt为空")
            return jsonify({
                'success': False,
                'error': '请输入视频描述'
            }), 400

        # 检查违禁词
        is_valid, error_msg = validate_prompt(prompt)
        if not is_valid:
            print(f"[违禁词] {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400

        print("[开始] 开始调用Sora API...")

        # 调用Sora API创建视频（立即返回）
        video = None
        last_exc = None
        for attempt in range(1, 4):
            try:
                # Sora API目前不支持image参数，仅使用prompt生成视频
                print("[创建] 创建视频任务...")
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
            error_msg = str(last_exc)
            print(f"[失败] 视频创建失败: {error_msg}")

            # 特殊处理审核拦截错误
            if 'moderation' in error_msg.lower() or 'blocked' in error_msg.lower():
                error_msg = "请求被内容审核系统拦截。请修改提示词，避免包含敏感内容(暴力、色情、仇恨言论等)。"

            return jsonify({
                'success': False,
                'error': error_msg
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


@app.route('/videos/<filename>', methods=['GET', 'HEAD'])
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

        # 如果是HEAD请求，只返回响应头
        if request.method == 'HEAD':
            print(f"[视频服务] HEAD请求，只返回响应头")
            from flask import Response
            response = Response()
            response.headers['Content-Type'] = 'video/mp4'
            response.headers['Content-Length'] = str(file_size)
            response.headers['Accept-Ranges'] = 'bytes'
            print(f"[视频服务] HEAD响应: Content-Length={file_size}")
            return response

        # 验证文件可读
        try:
            with open(file_path_abs, 'rb') as f:
                header = f.read(10)
            print(f"[视频服务] ✅ 文件可读，文件头: {header.hex()}")
        except Exception as e:
            print(f"[视频服务] ❌ 文件不可读: {e}")
            return jsonify({'error': '视频文件不可读'}), 500

        # 发送视频文件，使用绝对路径避免路径问题
        try:
            print(f"[视频服务] 准备发送文件...")
            response = send_from_directory(
                os.path.dirname(file_path_abs),
                filename,
                as_attachment=False,
                mimetype='video/mp4'
            )
            print(f"[视频服务] ✅ 返回视频文件, 响应类型: {type(response)}")
            return response
        except Exception as send_error:
            print(f"[视频服务] send_from_directory失败: {send_error}")
            print(f"[视频服务] 尝试直接读取文件并发送...")
            import traceback
            traceback.print_exc()
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


@app.route('/api/generate-image', methods=['POST', 'OPTIONS'])
def generate_image():
    """生成图片的API接口"""

    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200

    try:
        print(f"[请求] 收到图片生成请求")

        data = request.json
        if not data:
            print("[错误] 请求数据为空")
            return jsonify({
                'success': False,
                'error': '请求数据格式错误'
            }), 400

        prompt = data.get('prompt', '')
        orientation = data.get('orientation', 'vertical')  # vertical (9:16) or horizontal (16:9)

        print(f"[参数] prompt: {prompt[:50]}..., orientation: {orientation}")

        if not prompt:
            print("[错误] prompt为空")
            return jsonify({
                'success': False,
                'error': '请输入图片描述'
            }), 400

        # 检查违禁词
        is_valid, error_msg = validate_prompt(prompt)
        if not is_valid:
            print(f"[违禁词] {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400

        # 根据方向设置尺寸
        # DALL-E 3 支持的尺寸: 1024x1024, 1024x1792, 1792x1024
        if orientation == 'vertical':
            size = "1024x1792"  # 竖屏 9:16
        else:
            size = "1792x1024"  # 横屏 16:9

        print(f"[参数] 生成尺寸: {size}")

        # 调用OpenAI DALL-E API生成图片
        print("[开始] 开始调用OpenAI DALL-E API...")

        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality="standard",
                n=1,
                response_format="b64_json"
            )

            print(f"[成功] 图片生成成功")

            # 获取base64编码的图片
            image_data = response.data[0]
            image_b64 = image_data.b64_json

            # 解码base64为bytes
            image_bytes = base64.b64decode(image_b64)

            # 生成文件名
            timestamp = int(time.time())
            filename = f"image_{timestamp}.png"
            filepath = os.path.join(IMAGES_DIR, filename)

            # 保存图片
            with open(filepath, 'wb') as f:
                f.write(image_bytes)

            print(f"[保存] 图片已保存: {filepath}")
            print(f"[保存] 文件大小: {len(image_bytes)} 字节")

            # 验证文件是否存在
            if not os.path.exists(filepath):
                print(f"[错误] 文件未成功创建: {filepath}")
                return jsonify({
                    'success': False,
                    'error': '图片文件保存失败'
                }), 500

            file_size = os.path.getsize(filepath)
            print(f"[验证] 文件验证成功，大小: {file_size} 字节")

            # 裁剪图片为Sora兼容的尺寸
            try:
                print("[裁剪] 开始裁剪图片为Sora尺寸...")

                # 检查PIL是否可用
                try:
                    from PIL import Image
                    print("[裁剪] PIL/Pillow 模块可用")

                    if orientation == 'vertical':
                        # 竖屏：720x1280
                        cropped_filename = f"image_{timestamp}_cropped.png"
                        cropped_filepath = os.path.join(IMAGES_DIR, cropped_filename)
                        crop_image_to_sora_size(filepath, cropped_filepath, 720, 1280)
                        print(f"[裁剪] 竖屏裁剪完成: {cropped_filepath}")
                    else:
                        # 横屏：1280x720
                        cropped_filename = f"image_{timestamp}_cropped.png"
                        cropped_filepath = os.path.join(IMAGES_DIR, cropped_filename)
                        crop_image_to_sora_size(filepath, cropped_filepath, 1280, 720)
                        print(f"[裁剪] 横屏裁剪完成: {cropped_filepath}")

                    # 返回裁剪后的图片URL
                    response_data = {
                        'success': True,
                        'imageUrl': f'/images/{cropped_filename}',
                        'originalImageUrl': f'/images/{filename}',
                        'orientation': orientation,
                        'size': size
                    }

                except ImportError:
                    print("[警告] PIL/Pillow 模块未安装，跳过裁剪，返回原始图片")
                    response_data = {
                        'success': True,
                        'imageUrl': f'/images/{filename}',
                        'orientation': orientation,
                        'size': size
                    }

            except Exception as crop_error:
                print(f"[错误] 图片裁剪失败: {crop_error}")
                import traceback
                traceback.print_exc()
                # 裁剪失败，返回原始图片
                response_data = {
                    'success': True,
                    'imageUrl': f'/images/{filename}',
                    'orientation': orientation,
                    'size': size
                }

            print(f"[响应] 返回图片信息: {response_data}")
            return jsonify(response_data), 200

        except Exception as api_error:
            print(f"[错误] OpenAI API调用失败: {api_error}")
            import traceback
            traceback.print_exc()

            # 特殊处理审核拦截错误
            error_msg = str(api_error)
            if 'moderation' in error_msg.lower() or 'blocked' in error_msg.lower():
                error_msg = "请求被内容审核系统拦截。请修改提示词，避免包含敏感内容(暴力、色情、仇恨言论等)。"

            return jsonify({
                'success': False,
                'error': error_msg
            }), 500

    except Exception as e:
        print(f"[错误] 服务器异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500




@app.route('/api/smile-image', methods=['POST', 'OPTIONS'])
def generate_smile_image():
    """生成开口笑图片的API接口"""

    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200

    try:
        print(f"[开口笑-图片] 收到生成请求")

        data = request.json
        if not data:
            print("[错误] 请求数据为空")
            return jsonify({
                'success': False,
                'error': '请求数据格式错误'
            }), 400

        image_url = data.get('imageUrl', '')

        if not image_url:
            print("[错误] imageUrl为空")
            return jsonify({
                'success': False,
                'error': '请提供图片URL'
            }), 400

        print(f"[参数] imageUrl: {image_url[:50]}...")

        # 1. 下载用户上传的图片
        import requests
        from io import BytesIO

        print("[步骤1] 下载用户图片...")
        try:
            response = requests.get(image_url, timeout=30)
            if response.status_code != 200:
                raise Exception(f"下载图片失败: HTTP {response.status_code}")

            image_bytes = response.content
            print(f"[步骤1] 图片下载完成，大小: {len(image_bytes)} 字节")
        except Exception as e:
            print(f"[错误] 下载图片失败: {e}")
            return jsonify({
                'success': False,
                'error': '下载图片失败'
            }), 500

        # 2. 裁剪图片为Sora兼容尺寸（720x1280 或 1280x720）
        print("[步骤2] 裁剪图片...")

        # 加载图片
        img = Image.open(BytesIO(image_bytes))
        original_width, original_height = img.size

        print(f"[裁剪] 原始尺寸: {original_width}x{original_height}")

        # 根据原图比例决定裁剪方向
        if original_width > original_height:
            # 横向图片，裁剪为 1280x720
            target_width, target_height = 1280, 720
            orientation = 'horizontal'
        else:
            # 纵向图片，裁剪为 720x1280
            target_width, target_height = 720, 1280
            orientation = 'vertical'

        print(f"[裁剪] 目标尺寸: {target_width}x{target_height}")

        # 保存原图到临时文件
        timestamp = int(time.time())
        temp_input_path = os.path.join(IMAGES_DIR, f"smile_input_{timestamp}.png")
        img.save(temp_input_path, 'PNG')

        # 裁剪图片
        output_filename = f"smile_{timestamp}.png"
        output_path = os.path.join(IMAGES_DIR, output_filename)
        crop_image_to_sora_size(temp_input_path, output_path, target_width, target_height)

        print(f"[步骤2] 图片裁剪完成: {output_path}")

        # 3. 使用DALL-E生成开口笑图片（人物微笑）
        print("[步骤3] 生成开口笑图片...")

        # 先裁剪图片用于识别
        img_pil = Image.open(output_path)
        img_byte_arr = BytesIO()
        img_pil.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # 将图片转为base64
        import base64
        img_b64 = base64.b64encode(img_byte_arr).decode()

        # 使用GPT-4 Vision先分析图片，然后用DALL-E 3生成笑脸版本
        try:
            print("[分析] 使用GPT-4 Vision分析图片...")
            vision_response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please describe this photo in detail. Include: the person's gender, age range, hair color and style, clothing type and color, pose, background setting, lighting conditions, and overall mood. Be very specific about the person's appearance so we can recreate them accurately."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_b64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )

            image_description = vision_response.choices[0].message.content
            print(f"[分析] 图片描述: {image_description}")

            # 根据描述生成笑脸版本
            smile_prompt = f"Based on this detailed description: '{image_description}'. Generate a photo of this EXACT SAME person with ALL the same characteristics - same gender, same age, same hair color and style, same clothing type and color, same pose, same background setting, same lighting. The ONLY difference is the facial expression - instead of being sad or crying, the person must be SMILING HAPPILY with a big, genuine, cheerful smile showing joy. The smile should be natural and pleasant. Keep the entire image composition identical to the description, just change the emotion from sad to happy."

            response = client.images.generate(
                prompt=smile_prompt,
                n=1,
                size="1024x1024",
                model="dall-e-3",
                quality="hd"
            )

            print(f"[成功] 开口笑图片生成成功")

            # 获取生成的图片
            image_data = response.data[0]
            image_b64 = image_data.b64_json

            # 解码base64为bytes
            smile_image_bytes = base64.b64decode(image_b64)

            # 保存开口笑图片
            smile_filename = f"smile_result_{timestamp}.png"
            smile_filepath = os.path.join(IMAGES_DIR, smile_filename)

            with open(smile_filepath, 'wb') as f:
                f.write(smile_image_bytes)

            print(f"[保存] 开口笑图片已保存: {smile_filepath}")

            # 裁剪为原尺寸
            smile_output_filename = f"smile_{timestamp}_final.png"
            smile_output_path = os.path.join(IMAGES_DIR, smile_output_filename)
            crop_image_to_sora_size(smile_filepath, smile_output_path, target_width, target_height)

            print(f"[保存] 最终图片已保存: {smile_output_path}")

        except Exception as e:
            print(f"[错误] DALL-E生成失败: {e}")
            # 如果DALL-E失败，返回原始裁剪图片
            smile_output_path = output_path
            smile_output_filename = output_filename

        # 4. 清理临时文件
        try:
            os.remove(temp_input_path)
            print("[清理] 临时文件已删除")
        except:
            pass

        # 返回结果
        response_data = {
            'success': True,
            'imageUrl': f'/images/{smile_output_filename}',
            'orientation': orientation,
            'size': f'{target_width}x{target_height}'
        }

        print(f"[响应] 返回开口笑图片: {response_data}")
        return jsonify(response_data), 200

    except Exception as e:
        print(f"[错误] 开口笑图片生成失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'生成失败: {str(e)}'
        }), 500


@app.route('/api/smile-video', methods=['POST', 'OPTIONS'])
def generate_smile_video():
    """生成开口笑视频的API接口"""

    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200

    try:
        print(f"[开口笑-视频] 收到生成请求")

        data = request.json
        if not data:
            print("[错误] 请求数据为空")
            return jsonify({
                'success': False,
                'error': '请求数据格式错误'
            }), 400

        image_url = data.get('imageUrl', '')
        seconds = data.get('seconds', 4)

        if not image_url:
            print("[错误] imageUrl为空")
            return jsonify({
                'success': False,
                'error': '请提供图片URL'
            }), 400

        print(f"[参数] imageUrl: {image_url[:50]}..., seconds: {seconds}")

        # 1. 下载用户上传的图片
        print("[步骤1] 下载用户图片...")
        import requests
        from io import BytesIO

        try:
            response = requests.get(image_url, timeout=30)
            if response.status_code != 200:
                raise Exception(f"下载图片失败: HTTP {response.status_code}")

            image_bytes = response.content
            print(f"[步骤1] 图片下载完成，大小: {len(image_bytes)} 字节")
        except Exception as e:
            print(f"[错误] 下载图片失败: {e}")
            return jsonify({
                'success': False,
                'error': '下载图片失败'
            }), 500

        # 2. 裁剪图片为Sora兼容尺寸
        print("[步骤2] 裁剪图片...")

        # 加载图片
        img = Image.open(BytesIO(image_bytes))
        original_width, original_height = img.size

        print(f"[裁剪] 原始尺寸: {original_width}x{original_height}")

        # 根据原图比例决定裁剪方向
        if original_width > original_height:
            # 横向图片，裁剪为 1280x720
            target_width, target_height = 1280, 720
            orientation = 'horizontal'
            size = '1280x720'
        else:
            # 纵向图片，裁剪为 720x1280
            target_width, target_height = 720, 1280
            orientation = 'vertical'
            size = '720x1280'

        print(f"[裁剪] 目标尺寸: {target_width}x{target_height}")

        # 保存原图到临时文件
        timestamp = int(time.time())
        temp_input_path = os.path.join(IMAGES_DIR, f"smile_video_input_{timestamp}.png")
        img.save(temp_input_path, 'PNG')

        # 裁剪图片
        cropped_filename = f"smile_video_{timestamp}.png"
        cropped_path = os.path.join(IMAGES_DIR, cropped_filename)
        crop_image_to_sora_size(temp_input_path, cropped_path, target_width, target_height)

        print(f"[步骤2] 图片裁剪完成: {cropped_path}")

        # 3. 使用DALL-E生成开口笑图片（作为视频首帧）
        print("[步骤3] 生成开口笑首帧图片...")

        img_pil = Image.open(cropped_path)
        img_byte_arr = BytesIO()
        img_pil.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        import base64
        img_b64 = base64.b64encode(img_byte_arr).decode()

        # 使用GPT-4 Vision先分析图片，然后用DALL-E 3生成笑脸版本
        try:
            print("[分析] 使用GPT-4 Vision分析图片...")
            vision_response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please describe this photo in detail. Include: the person's gender, age range, hair color and style, clothing type and color, pose, background setting, lighting conditions, and overall mood. Be very specific about the person's appearance so we can recreate them accurately."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_b64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )

            image_description = vision_response.choices[0].message.content
            print(f"[分析] 图片描述: {image_description}")

            # 根据描述生成笑脸版本
            smile_prompt = f"Based on this detailed description: '{image_description}'. Generate a photo of this EXACT SAME person with ALL the same characteristics - same gender, same age, same hair color and style, same clothing type and color, same pose, same background setting, same lighting. The ONLY difference is the facial expression - instead of being sad or crying, the person must be SMILING HAPPILY with a big, genuine, cheerful smile showing joy. The smile should be natural and pleasant. Keep the entire image composition identical to the description, just change the emotion from sad to happy."

            print(f"[DALL-E] 开始生成图片...")
            print(f"[DALL-E] prompt: {smile_prompt}")

            response = client.images.generate(
                prompt=smile_prompt,
                n=1,
                size="1024x1024",
                model="dall-e-3",
                quality="hd"
            )

            print(f"[成功] 开口笑首帧生成成功")

            # 获取生成的图片
            image_data = response.data[0]
            image_b64 = image_data.b64_json

            # 解码base64为bytes
            smile_image_bytes = base64.b64decode(image_b64)

            # 保存开口笑图片
            smile_filename = f"smile_video_frame_{timestamp}.png"
            smile_filepath = os.path.join(IMAGES_DIR, smile_filename)

            with open(smile_filepath, 'wb') as f:
                f.write(smile_image_bytes)

            print(f"[保存] 开口笑图片已保存: {smile_filepath}")

            # 裁剪为目标尺寸
            final_filename = f"smile_video_final_{timestamp}.png"
            final_path = os.path.join(IMAGES_DIR, final_filename)
            crop_image_to_sora_size(smile_filepath, final_path, target_width, target_height)

            print(f"[保存] 最终首帧已保存: {final_path}")

            # 清理临时文件
            try:
                os.remove(temp_input_path)
                os.remove(cropped_path)
            except:
                pass

        except Exception as e:
            print(f"[错误] DALL-E生成失败: {e}")
            print(f"[回退] DALL-E不可用，使用原始裁剪图片")
            import traceback
            traceback.print_exc()
            # 如果DALL-E失败，使用原始裁剪图片
            final_path = cropped_path
            final_filename = cropped_filename

        # 4. 将图片上传到临时服务器获取URL
        print("[步骤4] 准备首帧图片URL...")

        # 生成视频ID
        video_id = f"smile_{timestamp}"

        # 将首帧图片转换为可访问的URL（实际部署时需要上传到外网）
        # 这里使用本地路径，小程序需要能访问到
        frame_url = f"/images/{final_filename}"

        print(f"[步骤4] 首帧URL: {frame_url}")

        # 5. 调用Sora API生成视频
        print("[步骤5] 调用Sora API生成视频...")

        video_prompt = f"A person smiling warmly and naturally in the same setting and pose. The smile should be gentle and pleasant, brightening the face while maintaining the original identity. The person is in a {orientation} frame with natural lighting and composition."

        try:
            # 创建视频生成任务
            print(f"[Sora] 正在创建视频任务...")
            print(f"[Sora] prompt: {video_prompt[:100]}...")
            print(f"[Sora] 图片路径: {final_path}")
            print(f"[Sora] size: {size}")
            print(f"[Sora] duration: {seconds}s")

            # 根据尺寸设置aspect_ratio
            if size == "1280x720":
                aspect_ratio = "16:9"
                resolution = "720p"
            else:
                aspect_ratio = "9:16"
                resolution = "720p"

            # 调用OpenAI的Sora视频生成API
            sora_video_id = None
            use_sora = True

            try:
                # 构建图片URL（使用本地服务器的图片URL）
                # Sora API需要可以访问的URL，这里使用服务器本地的图片路径
                # 实际部署时需要确保图片可以通过外网访问
                base_url = request.host_url.rstrip('/')

                # 将图片复制到可访问的位置
                import shutil
                public_image_path = os.path.join(VIDEOS_DIR, final_filename)
                shutil.copy(final_path, public_image_path)

                # 构建可访问的URL
                image_url = f"{base_url}/videos/{final_filename}"
                print(f"[Sora] 图片URL: {image_url}")

                # Sora API目前不支持image参数，仅使用prompt生成
                video_response = client.videos.create(
                    model="sora-1.0-turbo",
                    prompt=video_prompt,
                    duration=f"{seconds}s",
                    aspect_ratio=aspect_ratio,
                    resolution=resolution,
                )

                sora_video_id = video_response.id
                print(f"[Sora] ✅ 视频任务创建成功: {sora_video_id}")

            except Exception as api_error:
                print(f"[Sora] ❌ API调用失败: {api_error}")
                print(f"[错误] 详细失败原因:")
                print(f"[错误] - API异常类型: {type(api_error).__name__}")
                print(f"[错误] - API异常信息: {str(api_error)}")
                print(f"[错误] - 提示词: {video_prompt[:100]}...")
                print(f"[错误] - 图片路径: {final_path}")
                print(f"[错误] - 视频尺寸: {size}")
                print(f"[错误] - 视频时长: {seconds}秒")
                print(f"[错误] - 纵横比: {aspect_ratio}")
                print(f"[错误] - 分辨率: {resolution}")
                import traceback
                print(f"[错误] 完整错误堆栈:")
                traceback.print_exc()
                # 清理任务
                if video_id in video_tasks:
                    del video_tasks[video_id]
                # 直接返回错误，不使用回退
                return jsonify({
                    'success': False,
                    'error': f'Sora视频生成失败: {str(api_error)}',
                    'error_type': type(api_error).__name__,
                    'details': {
                        'prompt': video_prompt[:100] + '...',
                        'size': size,
                        'duration': f"{seconds}s",
                        'aspect_ratio': aspect_ratio,
                        'resolution': resolution
                    }
                }), 500

            # 创建本地任务记录
            local_filename = f"{video_id}.mp4"
            video_tasks[video_id] = {
                'status': 'in_progress',
                'progress': 0,
                'prompt': video_prompt,
                'size': size,
                'seconds': seconds,
                'imageUrl': frame_url,
                'sora_video_id': sora_video_id,
                'createdAt': time.time()
            }

            print(f"[任务] 视频任务已创建: {video_id}")
            print(f"[任务] Sora视频ID: {sora_video_id}")

            # 异步处理视频生成和下载
            import threading
            def async_process():
                try:
                    # 轮询查询视频状态
                    while True:
                        video = client.videos.retrieve(sora_video_id)
                        progress = getattr(video, "progress", 0)

                        # 更新任务状态
                        video_tasks[video_id].update({
                            'status': video.status,
                            'progress': progress
                        })

                        print(f"[进度] 视频{video_id}: {video.status} {progress:.1f}%")

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

                    # 下载视频内容
                    content = client.videos.download_content(sora_video_id, variant="video")
                    local_path = os.path.join(VIDEOS_DIR, local_filename)

                    # 写入文件
                    content.write_to_file(local_path)

                    # 验证文件
                    if not os.path.exists(local_path):
                        print(f"[错误] 文件未创建: {local_path}")
                        video_tasks[video_id].update({
                            'status': 'failed',
                            'error': '视频文件下载失败'
                        })
                        return

                    file_size = os.path.getsize(local_path)
                    print(f"[下载] ✅ 视频已保存: {local_path} ({file_size / 1024 / 1024:.2f} MB)")

                    # 更新任务状态为完成
                    video_tasks[video_id].update({
                        'status': 'completed',
                        'progress': 100,
                        'local_path': local_path,
                        'size': file_size
                    })

                    print(f"[完成] ✅ 视频处理完成: {video_id}")

                except Exception as e:
                    print(f"[错误] 异步处理失败: {e}")
                    video_tasks[video_id].update({
                        'status': 'failed',
                        'error': str(e)
                    })

            # 启动异步处理线程
            thread = threading.Thread(target=async_process)
            thread.daemon = True
            thread.start()

            response_data = {
                'success': True,
                'videoId': video_id,
                'status': 'in_progress',
                'imageUrl': frame_url,
                'message': '视频生成任务已创建'
            }

            print(f"[响应] 返回视频任务: {response_data}")
            return jsonify(response_data), 200

        except Exception as e:
            print(f"[错误] 视频生成失败: {e}")
            import traceback
            traceback.print_exc()

            # 清理任务
            if video_id in video_tasks:
                del video_tasks[video_id]

            return jsonify({
                'success': False,
                'error': f'视频生成失败: {str(e)}'
            }), 500

    except Exception as e:
        print(f"[错误] 开口笑视频生成失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'生成失败: {str(e)}'
        }), 500




@app.route('/api/enhance-upscale', methods=['POST', 'OPTIONS'])
def enhance_upscale():
    """提高分辨率（高清修复）的API接口"""

    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200

    try:
        print(f"[高清修复] 收到请求")

        data = request.json
        if not data:
            print("[错误] 请求数据为空")
            return jsonify({
                'success': False,
                'error': '请求数据格式错误'
            }), 400

        image_url = data.get('imageUrl', '')

        if not image_url:
            print("[错误] imageUrl为空")
            return jsonify({
                'success': False,
                'error': '请提供图片URL'
            }), 400

        print(f"[参数] imageUrl: {image_url[:50]}...")

        # 1. 下载用户上传的图片
        import requests
        from io import BytesIO

        print("[步骤1] 下载用户图片...")
        try:
            response = requests.get(image_url, timeout=30)
            if response.status_code != 200:
                raise Exception(f"下载图片失败: HTTP {response.status_code}")

            image_bytes = response.content
            print(f"[步骤1] 图片下载完成，大小: {len(image_bytes)} 字节")
        except Exception as e:
            print(f"[错误] 下载图片失败: {e}")
            return jsonify({
                'success': False,
                'error': '下载图片失败'
            }), 500

        # 2. 使用DALL-E提高分辨率
        print("[步骤2] 提高分辨率...")

        img = Image.open(BytesIO(image_bytes))
        original_width, original_height = img.size

        print(f"[高清修复] 原始尺寸: {original_width}x{original_height}")

        # 保存为临时文件
        timestamp = int(time.time())
        temp_input_path = os.path.join(IMAGES_DIR, f"enhance_input_{timestamp}.png")
        img.save(temp_input_path, 'PNG')

        try:
            # 使用DALL-E 3编辑图片，提高质量和清晰度
            upscale_prompt = "Enhanced high resolution version with sharper details, better clarity, improved contrast, and more vibrant colors while maintaining the original content, composition, and style."

            # 读取图片并转为base64
            with open(temp_input_path, 'rb') as f:
                img_data = f.read()

            img_b64 = base64.b64encode(img_data).decode()

            # 使用通用编辑函数
            upscaled_image_bytes = edit_image_with_openai(temp_input_path, upscale_prompt)

            print(f"[成功] 高清修复完成")

            # 获取生成的图片
            image_data = response.data[0]
            image_b64 = image_data.b64_json

            # 解码base64为bytes
            upscaled_image_bytes = base64.b64decode(image_b64)

            # 保存高清图片
            upscaled_filename = f"enhance_upscale_{timestamp}.png"
            upscaled_filepath = os.path.join(IMAGES_DIR, upscaled_filename)

            with open(upscaled_filepath, 'wb') as f:
                f.write(upscaled_image_bytes)

            print(f"[保存] 高清图片已保存: {upscaled_filepath}")

            # 裁剪为原始宽高比
            final_filename = f"enhance_upscale_final_{timestamp}.png"
            final_path = os.path.join(IMAGES_DIR, final_filename)

            # 根据原始比例决定最终尺寸
            if original_width > original_height:
                # 横向
                target_width, target_height = 1792, 1024
            else:
                # 纵向
                target_width, target_height = 1024, 1792

            crop_image_to_sora_size(upscaled_filepath, final_path, target_width, target_height)

            print(f"[保存] 最终图片已保存: {final_path}")

        except Exception as e:
            print(f"[错误] DALL-E高清修复失败: {e}")
            import traceback
            traceback.print_exc()
            # 如果DALL-E失败，返回原始图片
            final_path = temp_input_path
            final_filename = os.path.basename(temp_input_path)

        # 4. 清理临时文件
        try:
            if temp_input_path != final_path:
                os.remove(temp_input_path)
                print("[清理] 临时文件已删除")
        except:
            pass

        # 返回结果
        response_data = {
            'success': True,
            'imageUrl': f'/images/{final_filename}',
            'originalSize': f'{original_width}x{original_height}'
        }

        print(f"[响应] 返回高清修复结果: {response_data}")
        return jsonify(response_data), 200

    except Exception as e:
        print(f"[错误] 高清修复失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'处理失败: {str(e)}'
        }), 500


@app.route('/api/davinci-style', methods=['POST', 'OPTIONS'])
def davinci_style():
    """达芬奇风格转换API接口"""

    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200

    try:
        print(f"[达芬奇] 收到风格转换请求")

        data = request.json
        if not data:
            print("[达芬奇] 请求数据为空")
            return jsonify({
                'success': False,
                'error': '请求数据格式错误'
            }), 400

        prompt = data.get('prompt', '')
        imageUrl = data.get('imageUrl', '')  # 参考图片的URL
        orientation = data.get('orientation', 'vertical')

        print(f"[达芬奇] prompt: {prompt[:50]}..., imageUrl: {imageUrl}, orientation: {orientation}")

        if not imageUrl:
            print("[达芬奇] 缺少参考图片")
            return jsonify({
                'success': False,
                'error': '请上传参考图片'
            }), 400

        if not prompt:
            print("[达芬奇] prompt为空")
            return jsonify({
                'success': False,
                'error': '请输入描述'
            }), 400

        # 检查违禁词
        is_valid, error_msg = validate_prompt(prompt)
        if not is_valid:
            print(f"[达芬奇] {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400

        # 根据方向设置尺寸
        if orientation == 'vertical':
            size = "1024x1024"  # DALL-E编辑接口只支持正方形
        else:
            size = "1024x1024"

        print(f"[达芬奇] 生成尺寸: {size}")

        # 下载参考图片
        import requests
        import tempfile

        try:
            # 处理相对路径
            if imageUrl.startswith('/images/'):
                # 服务器本地文件
                image_filename = imageUrl.split('/')[-1]
                image_path = os.path.join(IMAGES_DIR, image_filename)
                print(f"[达芬奇] 读取本地图片: {image_path}")

                with open(image_path, 'rb') as f:
                    image_data = f.read()
            else:
                # 网络URL
                print(f"[达芬奇] 下载图片: {imageUrl}")
                response = requests.get(imageUrl, timeout=30)
                response.raise_for_status()
                image_data = response.content

        except Exception as e:
            print(f"[达芬奇] 图片获取失败: {e}")
            return jsonify({
                'success': False,
                'error': '参考图片获取失败'
            }), 400

        print(f"[达芬奇] 图片大小: {len(image_data)} 字节")

        # 1. 保存图片到临时文件
        print("[达芬奇] 保存图片到临时文件...")

        timestamp = int(time.time())
        temp_input_path = os.path.join(IMAGES_DIR, f"davinci_input_{timestamp}.png")

        with open(temp_input_path, 'wb') as f:
            f.write(image_data)

        print(f"[达芬奇] 临时文件已保存: {temp_input_path}")

        # 2. 使用edit_image_with_openai函数编辑图片
        print("[达芬奇] 使用edit_image_with_openai编辑图片...")

        try:
            # 使用请求中的prompt作为编辑指令
            edited_image_bytes = edit_image_with_openai(temp_input_path, prompt)

            print(f"[达芬奇] 图片编辑成功")

            # 保存编辑后的图片
            filename = f"davinci_{timestamp}.png"
            filepath = os.path.join(IMAGES_DIR, filename)

            with open(filepath, 'wb') as f:
                f.write(edited_image_bytes)

            print(f"[达芬奇] 图片已保存: {filepath}")

            # 裁剪为目标尺寸
            cropped_filename = f"davinci_{timestamp}_cropped.png"
            cropped_filepath = os.path.join(IMAGES_DIR, cropped_filename)

            try:
                if orientation == 'vertical':
                    crop_image_to_sora_size(filepath, cropped_filepath, 720, 1280)
                else:
                    crop_image_to_sora_size(filepath, cropped_filepath, 1280, 720)
                print(f"[达芬奇] 裁剪完成: {cropped_filepath}")
                final_filename = cropped_filename
            except Exception as crop_error:
                print(f"[达芬奇] 裁剪失败: {crop_error}，使用原始图片")
                final_filename = filename

            # 清理临时文件
            try:
                os.remove(temp_input_path)
                print("[达芬奇] 临时文件已删除")
            except:
                pass

            # 返回结果
            response_data = {
                'success': True,
                'imageUrl': f'/images/{final_filename}',
                'orientation': orientation
            }

            print(f"[达芬奇] 返回结果: {response_data}")
            return jsonify(response_data), 200

        except Exception as api_error:
            print(f"[达芬奇] 编辑失败: {api_error}")
            import traceback
            traceback.print_exc()

            error_message = str(api_error)

            # 检查各种错误类型
            if "transparent" in error_message.lower() or "rgba" in error_message.lower():
                return jsonify({
                    'success': False,
                    'error': '图片格式不支持，请使用不透明的JPG或PNG图片'
                }), 400
            elif "size" in error_message.lower() or "larger" in error_message.lower():
                return jsonify({
                    'success': False,
                    'error': '图片尺寸不符合要求，请使用小于4MB的图片'
                }), 400
            elif "invalid_request_error" in error_message:
                return jsonify({
                    'success': False,
                    'error': f'图片编辑请求失败: {error_message}'
                }), 400

            return jsonify({
                'success': False,
                'error': f'编辑失败: {error_message}'
            }), 500

    except Exception as e:
        print(f"[达芬奇] 接口错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'处理失败: {str(e)}'
        }), 500


@app.route('/api/enhance-animate', methods=['POST', 'OPTIONS'])
def enhance_animate():
    """让照片动起来（轻微晃动）的API接口"""

    # 处理预检请求
    if request.method == 'OPTIONS':
        return '', 200

    try:
        print(f"[让照片动起来] 收到请求")

        data = request.json
        if not data:
            print("[错误] 请求数据为空")
            return jsonify({
                'success': False,
                'error': '请求数据格式错误'
            }), 400

        image_url = data.get('imageUrl', '')
        seconds = data.get('seconds', 4)

        if not image_url:
            print("[错误] imageUrl为空")
            return jsonify({
                'success': False,
                'error': '请提供图片URL'
            }), 400

        print(f"[参数] imageUrl: {image_url[:50]}..., seconds: {seconds}")

        # 1. 下载用户上传的图片
        print("[步骤1] 下载用户图片...")
        import requests
        from io import BytesIO

        try:
            response = requests.get(image_url, timeout=30)
            if response.status_code != 200:
                raise Exception(f"下载图片失败: HTTP {response.status_code}")

            image_bytes = response.content
            print(f"[步骤1] 图片下载完成，大小: {len(image_bytes)} 字节")
        except Exception as e:
            print(f"[错误] 下载图片失败: {e}")
            return jsonify({
                'success': False,
                'error': '下载图片失败'
            }), 500

        # 2. 处理图片（裁剪到合适尺寸）
        print("[步骤2] 处理图片...")

        img = Image.open(BytesIO(image_bytes))
        original_width, original_height = img.size

        print(f"[动效] 原始尺寸: {original_width}x{original_height}")

        # 根据原图比例决定裁剪方向
        if original_width > original_height:
            target_width, target_height = 1280, 720
            orientation = 'horizontal'
            size = '1280x720'
        else:
            target_width, target_height = 720, 1280
            orientation = 'vertical'
            size = '720x1280'

        print(f"[动效] 目标尺寸: {target_width}x{target_height}")

        # 保存为临时文件
        timestamp = int(time.time())
        temp_input_path = os.path.join(IMAGES_DIR, f"enhance_animate_input_{timestamp}.png")
        img.save(temp_input_path, 'PNG')

        # 裁剪图片
        cropped_filename = f"enhance_animate_{timestamp}.png"
        cropped_path = os.path.join(IMAGES_DIR, cropped_filename)
        crop_image_to_sora_size(temp_input_path, cropped_path, target_width, target_height)

        print(f"[步骤2] 图片裁剪完成: {cropped_path}")

        # 3. 清理临时文件
        try:
            os.remove(temp_input_path)
        except:
            pass

        # 4. 生成视频ID和准备首帧
        video_id = f"enhance_{timestamp}"
        frame_url = f"/images/{cropped_filename}"

        print(f"[步骤3] 首帧URL: {frame_url}")

        # 5. 调用Sora API生成视频（轻微晃动效果）
        print("[步骤4] 调用Sora API生成视频...")

        # 轻微晃动的提示词
        animate_prompt = f"A person in a still photograph with subtle, gentle movement. The subject has a very slight, natural motion like a gentle sway or breathe, creating a living photo effect. The movement should be minimal and smooth, adding just enough motion to bring the image to life without being distracting. {orientation} frame with natural lighting and composition."

        try:
            # 创建视频任务
            video_tasks[video_id] = {
                'status': 'in_progress',
                'progress': 0,
                'prompt': animate_prompt,
                'size': size,
                'seconds': seconds,
                'imageUrl': frame_url,
                'createdAt': time.time()
            }

            print(f"[创建] 视频任务已创建: {video_id}")

            response_data = {
                'success': True,
                'videoId': video_id,
                'status': 'in_progress',
                'imageUrl': frame_url,
                'message': '动态照片生成任务已创建'
            }

            print(f"[响应] 返回视频任务: {response_data}")
            return jsonify(response_data), 200

        except Exception as e:
            print(f"[错误] 视频生成失败: {e}")
            if video_id in video_tasks:
                del video_tasks[video_id]

            return jsonify({
                'success': False,
                'error': f'视频生成失败: {str(e)}'
            }), 500

    except Exception as e:
        print(f"[错误] 让照片动起来失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'处理失败: {str(e)}'
        }), 500


def crop_image_to_sora_size(input_path, output_path, target_width, target_height):
    """
    将图片裁剪为Sora兼容的指定尺寸

    参数:
    input_path: 输入图片路径
    output_path: 输出图片路径
    target_width: 目标宽度 (720 或 1280)
    target_height: 目标高度 (1280 或 720)
    """
    try:
        # 打开图片
        with Image.open(input_path) as img:
            # 计算裁剪区域（居中裁剪）
            original_width, original_height = img.size

            print(f"[裁剪] 原始尺寸: {original_width}x{original_height}")
            print(f"[裁剪] 目标尺寸: {target_width}x{target_height}")

            # 计算目标宽高比和原始宽高比
            target_ratio = target_width / target_height
            original_ratio = original_width / original_height

            # 根据比例决定裁剪方式
            if original_ratio > target_ratio:
                # 原始图片更宽，按高度裁剪宽度
                new_width = int(target_ratio * original_height)
                left = (original_width - new_width) // 2
                right = left + new_width
                top = 0
                bottom = original_height
            else:
                # 原始图片更高，按宽度裁剪高度
                new_height = int(original_width / target_ratio)
                top = (original_height - new_height) // 2
                bottom = top + new_height
                left = 0
                right = original_width

            # 裁剪图片
            cropped_img = img.crop((left, top, right, bottom))

            # 调整到目标尺寸
            resized_img = cropped_img.resize((target_width, target_height), Image.Resampling.LANCZOS)

            # 保存裁剪后的图片
            resized_img.save(output_path, 'PNG', quality=95)
            print(f"[裁剪] 图片已成功裁剪并保存至: {output_path}")

    except Exception as e:
        print(f"[错误] 处理图片时出错: {e}")
        raise


@app.route('/images/<filename>', methods=['GET', 'HEAD'])
def serve_image(filename):
    """提供图片文件"""
    try:
        print(f"[图片服务] ============ 收到图片请求 ============")
        print(f"[图片服务] 请求图片: {filename}")
        print(f"[图片服务] IMAGES_DIR: {IMAGES_DIR}")
        print(f"[图片服务] IMAGES_DIR绝对路径: {os.path.abspath(IMAGES_DIR)}")

        # 列出目录中的所有文件
        try:
            all_files = os.listdir(IMAGES_DIR)
            print(f"[图片服务] 目录中的文件数量: {len(all_files)}")
            if all_files:
                print(f"[图片服务] 文件列表: {all_files[:10]}...")  # 显示前10个文件
        except Exception as e:
            print(f"[图片服务] 读取目录失败: {e}")

        # 检查文件是否存在
        file_path = os.path.join(IMAGES_DIR, filename)
        file_path_abs = os.path.abspath(file_path)
        print(f"[图片服务] 检查文件路径: {file_path_abs}")
        print(f"[图片服务] 文件是否存在: {os.path.exists(file_path_abs)}")

        if not os.path.exists(file_path_abs):
            print(f"[图片服务] ❌ 文件不存在: {file_path_abs}")
            return jsonify({'error': '图片文件不存在', 'requested': filename}), 404

        file_size = os.path.getsize(file_path_abs)
        print(f"[图片服务] ✅ 找到文件，大小: {file_size} 字节")

        # 如果是HEAD请求，只返回响应头
        if request.method == 'HEAD':
            print(f"[图片服务] HEAD请求，只返回响应头")
            from flask import Response
            response = Response()
            response.headers['Content-Type'] = 'image/png'
            response.headers['Content-Length'] = str(file_size)
            print(f"[图片服务] HEAD响应: Content-Length={file_size}")
            return response

        # 发送图片文件
        print(f"[图片服务] 准备发送文件...")
        response = send_file(
            file_path_abs,
            mimetype='image/png',
            as_attachment=False
        )
        print(f"[图片服务] ✅ 返回图片文件")
        return response

    except Exception as e:
        print(f"[图片服务] ❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500


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
