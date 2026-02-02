# 配置OpenAI API密钥

## 问题
API服务器返回错误：`invalid_api_key`，说明OpenAI API密钥未正确配置。

## 解决方案

### 方法1：使用环境变量文件（推荐）

在服务器上执行：

```bash
# 1. 进入项目目录
cd /home/admin/SoraMiniProgram/api_server

# 2. 创建.env文件
nano .env

# 3. 添加以下内容（替换为你的真实API密钥）
OPENAI_API_KEY=sk-proj-你的真实密钥
OPENAI_BASE_URL=https://api.openai.com/v1

# 4. 保存文件（Ctrl+X，然后Y，然后Enter）

# 5. 修改文件权限（保护密钥安全）
chmod 600 .env
chown admin:admin .env

# 6. 重启服务
sudo systemctl restart sora-api

# 7. 验证
sudo systemctl status sora-api
```

### 方法2：在systemd服务中配置

```bash
# 1. 编辑服务文件
sudo nano /etc/systemd/system/sora-api.service

# 2. 在[Service]部分添加环境变量
[Service]
Environment="OPENAI_API_KEY=sk-proj-你的真实密钥"
Environment="OPENAI_BASE_URL=https://api.openai.com/v1"

# 3. 重新加载并重启
sudo systemctl daemon-reload
sudo systemctl restart sora-api
```

## 获取OpenAI API密钥

1. 访问：https://platform.openai.com/api-keys
2. 登录你的OpenAI账号
3. 点击 "Create new secret key"
4. 复制密钥（格式：sk-proj-...）
5. 将密钥粘贴到上述配置中

## 验证配置

```bash
# 测试API密钥是否生效
curl -X POST http://localhost:5000/api/optimize-prompt \
  -H "Content-Type: application/json" \
  -d '{"userDescription":"测试","styleTemplate":"test","duration":"4秒"}'
```

成功的话会返回优化后的提示词。

## 注意事项

⚠️ **安全提醒**：
- 永远不要将`.env`文件提交到Git
- 已经在`.gitignore`中排除了`.env`文件
- 建议定期更换API密钥
- 使用`chmod 600 .env`限制文件权限

## 当前网络状态

✅ 服务器公网IP：8.211.175.227
✅ 端口5000已开放
✅ API健康检查通过
❌ OpenAI API密钥需要配置
