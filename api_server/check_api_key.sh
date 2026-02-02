#!/bin/bash

echo "=========================================="
echo "OpenAI API密钥诊断工具"
echo "=========================================="
echo ""

# 1. 检查.env文件是否存在
echo "1️⃣ 检查.env文件..."
if [ -f .env ]; then
    echo "✅ .env文件存在"
    echo "文件权限："
    ls -l .env
    echo ""
    echo "文件内容（隐藏密钥）："
    cat .env | sed 's/sk-proj-[^ ]*/sk-proj-***HIDDEN***/g'
else
    echo "❌ .env文件不存在"
    echo "需要创建.env文件"
fi
echo ""

# 2. 检查环境变量
echo "2️⃣ 检查当前环境变量..."
if [ -n "$OPENAI_API_KEY" ]; then
    echo "✅ OPENAI_API_KEY已设置"
    echo "密钥长度: ${#OPENAI_API_KEY} 字符"
    echo "密钥前缀: ${OPENAI_API_KEY:0:8}..."
else
    echo "❌ OPENAI_API_KEY未设置"
fi
echo ""

# 3. 检查systemd服务配置
echo "3️⃣ 检查systemd服务配置..."
SERVICE_FILE="/etc/systemd/system/sora-api.service"
if grep -q "Environment.*OPENAI_API_KEY" "$SERVICE_FILE"; then
    echo "⚠️  服务文件中定义了OPENAI_API_KEY"
    echo "这会覆盖.env文件中的配置"
    sudo grep "Environment.*OPENAI_API_KEY" "$SERVICE_FILE" | sed 's/sk-proj-[^ ]*/sk-proj-***HIDDEN***/g'
else
    echo "✅ 服务文件未定义OPENAI_API_KEY（将使用.env文件）"
fi
echo ""

# 4. 测试加载.env文件
echo "4️⃣ 测试加载.env文件..."
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    if [ -n "$OPENAI_API_KEY" ]; then
        echo "✅ 成功从.env加载密钥"
        echo "密钥长度: ${#OPENAI_API_KEY} 字符"
        echo "密钥格式: ${OPENAI_API_KEY:0:8}...${OPENAI_API_KEY: -4}"
        
        # 验证密钥格式
        if [[ "$OPENAI_API_KEY" =~ ^sk-proj- ]]; then
            echo "✅ 密钥格式正确（以sk-proj-开头）"
        else
            echo "❌ 密钥格式错误（应该以sk-proj-开头）"
        fi
    else
        echo "❌ 无法从.env加载密钥"
    fi
fi
echo ""

# 5. 检查Python是否能加载密钥
echo "5️⃣ 测试Python加载密钥..."
cd /home/admin/SoraMiniProgram/api_server
source venv/bin/activate
python3 << 'PYEOF'
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    print(f"✅ Python成功加载密钥")
    print(f"密钥长度: {len(api_key)} 字符")
    print(f"密钥格式: {api_key[:8]}...{api_key[-4:]}")
    if api_key.startswith('sk-proj-'):
        print("✅ 密钥格式正确")
    else:
        print("❌ 密钥格式错误")
else:
    print("❌ Python无法加载密钥")
PYEOF
echo ""

echo "=========================================="
echo "🔧 修复建议"
echo "=========================================="
echo ""
echo "如果密钥有问题，请按以下步骤操作："
echo ""
echo "1. 重新创建.env文件："
echo "   cd /home/admin/SoraMiniProgram/api_server"
echo "   rm -f .env"
echo "   nano .env"
echo ""
echo "2. 在nano中输入（单行，不要换行）："
echo "   OPENAI_API_KEY=sk-proj-你的完整密钥"
echo "   保存：Ctrl+X → Y → Enter"
echo ""
echo "3. 验证密钥（应该显示完整的一行）："
echo "   cat .env"
echo ""
echo "4. 删除systemd中的环境变量定义："
echo "   sudo nano /etc/systemd/system/sora-api.service"
echo "   删除或注释掉包含OPENAI_API_KEY的Environment行"
echo ""
echo "5. 重启服务："
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl restart sora-api"
echo ""
echo "6. 查看日志："
echo "   sudo journalctl -u sora-api -n 30"
echo ""
echo "=========================================="
echo "⚠️  常见问题"
echo "=========================================="
echo "1. 密钥被换行截断 - 确保密钥在.env文件中是单行"
echo "2. 密钥有多余空格 - 不要在等号前后加空格"
echo "3. 密钥过期或无效 - 在OpenAI平台生成新密钥"
echo "4. systemd覆盖了.env - 删除服务文件中的Environment定义"
echo "=========================================="
