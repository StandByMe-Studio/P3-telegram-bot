import os
import yaml
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# 创建 Flask 应用用于保活
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# 加载配置文件
def load_config():
    with open('config.yaml', 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

config = load_config()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    keyboard = [
        [
            InlineKeyboardButton("开始互动", callback_data='start_story'),
            InlineKeyboardButton("继续阅读", callback_data='continue_reading')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        config['bot']['first_chapter'],
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /help 命令"""
    await update.message.reply_text(config['bot']['help_message'])

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """当用户首次添加bot时发送欢迎消息"""
    await update.message.reply_text(config['bot']['welcome_message'])

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理按钮回调"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'start_story':
        await query.message.reply_text("你选择了开始互动！请做出你的选择：\nA. 立即打开信封\nB. 仔细检查信封")
    elif query.data == 'continue_reading':
        await query.message.reply_text("你选择继续阅读。更多内容即将推出...")

def main():
    """主函数"""
    # 直接从环境变量获取 token
    token = os.environ['TELEGRAM_BOT_TOKEN']
    
    # 创建应用
    application = Application.builder().token(token).build()

    # 添加处理程序
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    # 启动 Flask 线程
    Thread(target=run_flask).start()
    
    # 启动机器人
    application.run_polling()

if __name__ == '__main__':
    main() 