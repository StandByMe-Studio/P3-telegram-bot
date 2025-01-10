import requests
import json
import os
from pathlib import Path

class ReplitDeployError(Exception):
    pass

def deploy_to_replit(api_token, repl_id=None):
    """
    部署项目到Replit
    
    Args:
        api_token: Replit API token
        repl_id: 现有Repl的ID (可选)
    """
    if not api_token:
        raise ReplitDeployError("Missing Replit API token")

    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }
    
    try:
        # 准备所有必要文件
        files = {
            'main.py': Path('bot.py').read_text(encoding='utf-8'),
            'config.yaml': Path('config.yaml').read_text(encoding='utf-8'),
            'requirements.txt': Path('requirements.txt').read_text(encoding='utf-8'),
            '.replit': 'run = "python main.py"\nlanguage = "python"\n',
            'pyproject.toml': '[tool.poetry]\nname = "TelegramStoryBot"\nversion = "0.1.0"\ndescription = ""\nauthors = []\n\n[tool.poetry.dependencies]\npython = "^3.8"\n\n[build-system]\nrequires = ["poetry-core"]\nbuild-backend = "poetry.core.masonry.api"'
        }

        base_url = 'https://replit.com/api/v2/repls'
        
        if not repl_id:
            # 创建新的 repl
            create_data = {
                'title': 'TelegramStoryBot',
                'language': 'python',
                'files': files,
                'isPrivate': True  # 设置为私有项目
            }
            response = requests.post(
                base_url,
                headers=headers,
                json=create_data
            )
            if response.status_code != 201:
                raise ReplitDeployError(f"Failed to create repl: {response.text}")
            print('✅ Repl created successfully!')
            
        else:
            # 更新现有的 repl
            update_data = {
                'files': files
            }
            response = requests.patch(
                f'{base_url}/{repl_id}',
                headers=headers,
                json=update_data
            )
            if response.status_code != 200:
                raise ReplitDeployError(f"Failed to update repl: {response.text}")
            print('✅ Repl updated successfully!')
        
        result = response.json()
        
        print('\n部署后续步骤:')
        print('1. 在Replit的Secrets标签页中添加以下环境变量:')
        print('   - TELEGRAM_BOT_TOKEN')
        print('2. 点击Run按钮启动bot')
        
        return result
        
    except requests.exceptions.RequestException as e:
        raise ReplitDeployError(f"Network error: {str(e)}")
    except Exception as e:
        raise ReplitDeployError(f"Deployment failed: {str(e)}")

if __name__ == '__main__':
    # 从环境变量获取token
    api_token = os.getenv('REPLIT_API_TOKEN')
    repl_id = os.getenv('REPLIT_ID')  # 可选
    
    try:
        result = deploy_to_replit(api_token, repl_id)
        print(f"Deployment URL: {result.get('url', 'N/A')}")
    except ReplitDeployError as e:
        print(f"❌ Error: {str(e)}") 