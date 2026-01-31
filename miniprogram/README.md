# Sora视频生成微信小程序

## 项目结构

```
LuckyTalk/
├── miniprogram/           # 微信小程序前端
│   ├── pages/
│   │   └── index/        # 主页面
│   ├── app.js
│   ├── app.json
│   ├── app.wxss
│   └── project.config.json
├── cloudfunctions/       # 微信云函数（可选）
│   └── generateVideo/    # 生成视频的云函数
└── api_server/           # Flask API服务（推荐）
    ├── sora_api.py       # API服务主文件
    └── requirements.txt  # Python依赖
```

## 方案选择

### 方案一：使用Flask API服务（推荐）

1. **安装Python依赖**
   ```bash
   cd api_server
   pip install -r requirements.txt
   ```

2. **配置OpenAI API密钥**
   - 在 `sora_api.py` 中，确保已正确设置OpenAI API密钥
   - 可以通过环境变量设置：`export OPENAI_API_KEY=your_api_key`

3. **启动API服务**
   ```bash
   cd api_server
   python sora_api.py
   ```
   服务将在 `http://localhost:5000` 启动

4. **配置小程序**
   - 在微信开发者工具中打开 `miniprogram` 目录
   - 确保小程序已配置正确的域名白名单（如果是本地开发，可以在开发工具中关闭域名校验）
   - 修改 `miniprogram/pages/index/index.js` 中的 `apiBaseUrl` 为你的API服务地址

5. **运行小程序**
   - 使用微信开发者工具打开小程序
   - 输入关键词，点击"生成视频"按钮

### 方案二：使用微信云开发

1. **创建云开发环境**
   - 在微信开发者工具中创建云开发环境
   - 记录云环境ID

2. **上传云函数**
   - 在开发者工具中右键 `cloudfunctions/generateVideo` 文件夹
   - 选择"上传并部署：云端安装依赖"

3. **配置云函数**
   - 在 `cloudfunctions/generateVideo/index.js` 中设置你的OpenAI API密钥
   ```javascript
   const client = new OpenAI({
     apiKey: 'your_openai_api_key_here'
   })
   ```

4. **修改小程序代码**
   - 将 `index_cloud.js` 的内容复制到 `index.js`
   - 修改云环境ID为你的实际环境ID

## 使用说明

### 小程序功能

1. **输入视频描述**
   - 在文本框中输入你想要生成的视频描述
   - 最多500个字符

2. **选择视频时长**
   - 可选择8秒、12秒或16秒
   - 默认为12秒

3. **生成视频**
   - 点击"生成视频"按钮
   - 等待视频生成完成
   - 生成完成后可在线播放

## 注意事项

1. **API密钥安全**
   - 不要将OpenAI API密钥直接提交到代码仓库
   - 建议使用环境变量或配置管理服务

2. **网络请求**
   - 微信小程序需要配置合法域名
   - 开发阶段可以在开发者工具中关闭域名校验

3. **视频生成时间**
   - Sora视频生成可能需要较长时间
   - 建议添加loading状态和超时处理

4. **费用控制**
   - Sora API按使用量计费
   - 建议添加使用量监控和限制

## 故障排查

### API服务无法启动
- 检查Python版本（需要3.7+）
- 确认所有依赖已安装
- 检查端口5000是否被占用

### 小程序无法连接API
- 确认API服务正在运行
- 检查小程序域名校验设置
- 确认API地址配置正确

### 视频生成失败
- 检查OpenAI API密钥是否有效
- 确认账户有足够的额度
- 查看API服务日志获取详细错误信息

## 开发建议

1. **增强功能**
   - 添加视频历史记录
   - 支持视频下载
   - 添加视频分享功能
   - 优化提示词生成

2. **性能优化**
   - 添加视频缓存
   - 实现异步轮询获取视频状态
   - 优化网络请求

3. **用户体验**
   - 添加生成进度提示
   - 提供更多视频样式选项
   - 添加示例prompt
