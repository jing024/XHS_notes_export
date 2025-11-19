from flask import Flask, render_template, request, jsonify, send_file, abort
import os
import json
from datetime import datetime
from note_sync import export_notes_to_excel

app = Flask(__name__)

# 配置
WORKFLOW_ID = "7573588596402225171"  # 固定的工作流ID
UPLOAD_FOLDER = 'downloads'
ALLOWED_EXTENSIONS = {'xlsx'}

# 确保下载文件夹存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/export', methods=['POST'])
def export_notes():
    """导出笔记数据API"""
    try:
        # 获取请求数据
        data = request.get_json()

        # 验证必需参数
        required_fields = ['note_count', 'user_URL', 'user_cookie', 'user_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'缺少必需参数: {field}',
                    'download_url': None,
                    'record_count': 0
                }), 400

        # 参数验证
        try:
            note_count = int(data['note_count'])
            if note_count < 1 or note_count > 1000:
                return jsonify({
                    'success': False,
                    'error': '笔记数量必须在1-1000之间',
                    'download_url': None,
                    'record_count': 0
                }), 400
        except ValueError:
            return jsonify({
                'success': False,
                'error': '笔记数量必须是数字',
                'download_url': None,
                'record_count': 0
            }), 400

        # URL验证
        user_URL = data['user_URL'].strip()
        if 'xiaohongshu.com/user/profile/' not in user_URL:
            return jsonify({
                'success': False,
                'error': '请输入正确的小红书用户主页URL',
                'download_url': None,
                'record_count': 0
            }), 400

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_user_name = "".join(c for c in data['user_name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_user_name}_notes_{timestamp}.xlsx"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # 调用导出函数
        result = export_notes_to_excel(
            workflow_id=WORKFLOW_ID,
            note_count=note_count,
            user_URL=user_URL,
            user_cookie=data['user_cookie'].strip(),
            user_name=data['user_name'].strip(),
            filename=filepath
        )

        if result['success']:
            # 移动文件到下载目录
            original_path = result['filename']
            if original_path != filepath:
                import shutil
                shutil.move(original_path, filepath)

            download_url = f"/download/{filename}"

            return jsonify({
                'success': True,
                'error': None,
                'download_url': download_url,
                'record_count': result['record_count']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error'],
                'download_url': None,
                'record_count': 0
            }), 500

    except Exception as e:
        print(f"导出过程中发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}',
            'download_url': None,
            'record_count': 0
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    """文件下载接口"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # 检查文件是否存在
        if not os.path.exists(filepath):
            abort(404)

        # 检查文件扩展名
        if not allowed_file(filename):
            abort(400)

        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        print(f"下载文件时发生错误: {str(e)}")
        abort(500)

@app.route('/health')
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': '文件未找到',
        'download_url': None,
        'record_count': 0
    }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': '请求参数错误',
        'download_url': None,
        'record_count': 0
    }), 400

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': '服务器内部错误',
        'download_url': None,
        'record_count': 0
    }), 500

if __name__ == '__main__':
    # 确保模板和下载目录存在
    if not os.path.exists('templates'):
        os.makedirs('templates')
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    print("🌸 小红书笔记数据导出工具启动中...")
    print("📱 前端地址: http://localhost:8080")
    print("🔧 API地址: http://localhost:8080/export")
    print("💾 下载文件夹: ./downloads")
    print("❤️ 健康检查: http://localhost:8080/health")

    app.run(debug=True, host='0.0.0.0', port=8080)