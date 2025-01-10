import requests
import json
import os

def deploy_to_replit(api_token, repl_id=None):
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }
    
    # 文件内容
    files = {
        'main.py': open('bot.py', 'r').read(),
        'config.yaml': open('config.yaml', 'r').read(),
        'requirements.txt': open('requirements.txt', 'r').read(),
    }
    
    if not repl_id:
        # 创建新的 repl
        create_data = {
            'title': 'TelegramStoryBot',
            'language': 'python',
            'files': files
        }
        response = requests.post(
            'https://replit.com/api/v1/repls',
            headers=headers,
            json=create_data
        )
        print('Repl created successfully!')
    else:
        # 更新现有的 repl
        update_data = {
            'files': files
        }
        response = requests.patch(
            f'https://replit.com/api/v1/repls/{repl_id}',
            headers=headers,
            json=update_data
        )
        print('Repl updated successfully!')
    
    return response.json() 