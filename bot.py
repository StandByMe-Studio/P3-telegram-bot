import os
import yaml
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from pathlib import Path
from cachetools import TTLCache  # 添加缓存

# 创建缓存
config_cache = TTLCache(maxsize=100, ttl=3600)  # 1小时缓存
user_cache = TTLCache(maxsize=1000, ttl=300)    # 5分钟缓存

# 优化配置文件加载
def load_config():
    """带缓存的配置加载"""
    if 'config' in config_cache:
        return config_cache['config']
    
    with open('config.yaml', 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
        config_cache['config'] = config
        return config

# 简单的Flask服务用于保活
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    user_id = update.effective_user.id
    
    # 使用缓存避免频繁读取配置
    if user_id in user_cache:
        return
    
    keyboard = [
        [
            InlineKeyboardButton("开始互动", callback_data='start_story'),
            InlineKeyboardButton("继续阅读", callback_data='continue_reading')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    config = load_config()
    await update.message.reply_text(
        config['bot']['first_chapter'],
        reply_markup=reply_markup
    )
    user_cache[user_id] = True

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /help 命令"""
    config = load_config()
    await update.message.reply_text(config['bot']['help_message'])

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """当用户首次添加bot时发送欢迎消息"""
    config = load_config()
    await update.message.reply_text(config['bot']['welcome_message'])

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理按钮回调"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'start_story':
        await query.message.reply_text("你选择了开始互动！请做出你的选择：\nA. 立即打开信封\nB. 仔细检查信封")
    elif query.data == 'continue_reading':
        await query.message.reply_text("你选择继续阅读。更多内容即将推出...")

def load_token():
    """加载Telegram Bot Token"""
    # 优先从环境变量获取
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if token:
        return token
        
    # 如果环境变量没有,尝试从.env文件读取
    env_path = Path('.env')
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('TELEGRAM_BOT_TOKEN='):
                    return line.split('=')[1].strip()
    
    raise ValueError("Telegram Bot Token not found!")

def main():
    """主函数"""
    token = load_token()
    
    # 优化应用配置
    application = (
        Application.builder()
        .token(token)
        .concurrent_updates(True)  # 启用并发更新
        .connection_pool_size(100)  # 增加连接池大小
        .pool_timeout(30.0)        # 设置池超时
        .build()
    )

    # 添加处理程序
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    # 启动Flask线程
    Thread(target=run_flask).start()
    
    # 启动机器人
    application.run_polling(
        pool_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        drop_pending_updates=True
    )

if __name__ == '__main__':
    main() 