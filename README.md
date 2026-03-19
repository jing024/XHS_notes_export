# 小红书笔记数据导出工具

一个基于Web的小红书用户笔记数据导出工具，支持输入参数配置，一键生成Excel文件并提供下载。

## 功能特点

- 🌸 友好的Web界面，无需命令行操作
- 📊 支持导出笔记的各种数据字段（标题、内容、点赞数、评论数等）
- 🔒 参数验证和错误处理
- 💾 自动生成Excel文件并提供下载
- 🚀 基于Flask框架，部署简单

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置环境变量

### 1. 复制环境变量模板

```bash
cp .env.example .env
```

### 2. 编辑 .env 文件

打开 `.env` 文件，填写你的 Coze API Token：

```env
COZE_API_TOKEN=your_coze_api_token_here
```

**⚠️ 重要提示：Coze API Token 有效期只有一个月！**

- Token 过期后需要重新到 Coze 平台生成
- 生成路径：登录 Coze 平台 → 个人设置 → API Token
- 建议设置日历提醒，在到期前更新 Token

### 3. 启动应用

```bash
python app.py
```

应用启动后，访问 http://localhost:8080

### 2. 填写参数

- **笔记数量**: 要导出的笔记数量（1-1000）
- **用户名**: 目标用户的用户名
- **用户主页URL**: 小红书用户主页链接
- **用户Cookie**: 从浏览器开发者工具获取的Cookie字符串

### 3. 获取Cookie方法

1. 打开小红书网页版
2. 按F12打开开发者工具
3. 切换到Network标签页
4. 刷新页面或进行其他操作
5. 找到任意请求，在Request Headers中找到Cookie字段
6. 复制完整的Cookie字符串

### 4. 下载文件

程序执行完成后，会自动显示下载按钮，点击即可下载生成的Excel文件。

## 项目结构

```
xhs_notes/
├── app.py                 # Flask应用主文件
├── note_sync.py          # 核心业务逻辑
├── templates/
│   └── index.html        # 前端页面
├── downloads/            # Excel文件下载目录（自动创建）
├── requirements.txt      # Python依赖
└── README.md            # 说明文档
```

## API接口

### POST /export

导出笔记数据接口

**请求体:**
```json
{
    "note_count": 100,
    "user_URL": "https://www.xiaohongshu.com/user/profile/xxx",
    "user_cookie": "完整的cookie字符串",
    "user_name": "用户名"
}
```

**响应:**
```json
{
    "success": true,
    "error": null,
    "download_url": "/download/filename.xlsx",
    "record_count": 100
}
```

### GET /download/<filename>

文件下载接口

### GET /health

健康检查接口

## Excel文件字段

生成的Excel文件包含以下字段：

- `id`: 笔记ID
- `bstudio_create_time`: 创建时间
- `user_id`: 用户ID
- `user_name`: 用户名
- `posted_time`: 发布时间
- `note_title`: 笔记标题
- `note_content`: 笔记内容
- `liked_count`: 点赞数
- `comment_count`: 评论数
- `share_count`: 分享数
- `collect_count`: 收藏数

## 注意事项

1. **⚠️ API Token 有效期**：Coze API Token 只有一个月有效期，过期后需要重新生成并更新 `.env` 文件
2. 请确保Cookie的有效性，过期Cookie会导致数据获取失败
3. 笔记数量限制在1-1000之间，避免请求过大
4. 生成的Excel文件会保存在downloads目录中
5. 建议定期清理downloads目录中的旧文件
6. 请遵守小红书的使用条款和相关法律法规
7. **安全提醒**：`.env` 文件包含敏感信息，请勿提交到 Git 仓库（已添加到 .gitignore）

## 故障排除

1. **网络错误**: 检查网络连接和防火墙设置
2. **Cookie无效**: 重新获取最新的Cookie字符串
3. **参数错误**: 确保所有必需参数都已正确填写
4. **工作流失败**: 检查workflow_id是否正确，或API服务是否正常

## 技术栈

- **后端**: Flask (Python)
- **前端**: HTML5 + CSS3 + JavaScript
- **数据处理**: pandas + openpyxl
- **API请求**: requests

## 开发者

- 基于扣子(Coze)工作流API
- 支持本地部署和内网使用
