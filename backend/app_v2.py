"""
横纵分析研究工具 - 后端 API v2
接收网站提交的研究请求，保存到队列，由 Claude Code 执行 hv-analysis skill
"""
import os
import json
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)

# 配置
QUEUE_DIR = Path('/Users/zhaowanting/zwt-Project/Projects_and_Repos/wentystudio-website/backend/research_queue')
QUEUE_DIR.mkdir(exist_ok=True)

@app.route('/api/research', methods=['POST'])
def create_research_task():
    """接收研究请求，保存到队列"""
    try:
        data = request.json
        subject = data.get('subject')
        focus = data.get('focus', '')
        feishu_app_id = data.get('feishu_app_id')
        feishu_app_secret = data.get('feishu_app_secret')
        feishu_folder_token = data.get('feishu_folder_token', '')

        if not subject:
            return jsonify({'error': '缺少必填参数: subject'}), 400

        if not feishu_app_id or not feishu_app_secret:
            return jsonify({'error': '缺少必填参数: feishu_app_id 或 feishu_app_secret'}), 400

        # 生成任务 ID
        task_id = str(uuid.uuid4())[:8]

        # 保存到队列
        task_data = {
            'task_id': task_id,
            'subject': subject,
            'focus': focus,
            'feishu_app_id': feishu_app_id,
            'feishu_app_secret': feishu_app_secret,
            'feishu_folder_token': feishu_folder_token,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'feishu_url': None,
            'error': None
        }

        task_file = QUEUE_DIR / f'{task_id}.json'
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task_data, f, ensure_ascii=False, indent=2)

        print(f"[{task_id}] 新任务已加入队列: {subject}")

        return jsonify({
            'status': 'queued',
            'task_id': task_id,
            'message': '任务已加入队列，Claude Code 将执行 hv-analysis skill'
        })

    except Exception as e:
        print(f"创建任务失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/research/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """查询任务状态"""
    try:
        task_file = QUEUE_DIR / f'{task_id}.json'

        if not task_file.exists():
            return jsonify({'error': '任务不存在'}), 404

        with open(task_file, 'r', encoding='utf-8') as f:
            task_data = json.load(f)

        return jsonify(task_data)

    except Exception as e:
        print(f"查询任务失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("横纵分析研究工具 API v2 服务启动")
    print(f"队列目录: {QUEUE_DIR}")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=True)
