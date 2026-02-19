# config.py
import os

# Берём токен из переменных окружения Render
BOT_TOKEN = os.getenv("BOT_TOKEN", "8272014510:AAFnMI-2ESaKnHygmrpr4OlRaL4AvwmPVew")

# Админы
ADMIN_ID = os.getenv("ADMIN_ID", "8272014510")
ADMINS = [int(x.strip()) for x in ADMIN_ID.split(",")]

# Настройки бота
BOT_NAME = "🤖 МегаБот"
BOT_VERSION = "2.0"

# Валюта
CURRENCY_NAME = "монет"
CURRENCY_EMOJI = "💰"

# Начальный баланс
START_BALANCE = 100

# Ежедневный бонус
DAILY_BONUS_MIN = 50
DAILY_BONUS_MAX = 200

# Реферальный бонус
REFERRAL_BONUS_INVITER = 150
REFERRAL_BONUS_INVITED = 100

# Магазин
SHOP_ITEMS = {
    "vip": {
        "name": "👑 VIP Статус",
        "description": "Получи VIP статус на 30 дней",
        "price": 5000,
        "emoji": "👑"
    },
    "premium": {
        "name": "💎 Premium Статус",
        "description": "Получи Premium статус на 30 дней",
        "price": 10000,
        "emoji": "💎"
    },
    "lootbox": {
        "name": "📦 Лутбокс",
        "description": "Случайный приз от 100 до 1000 монет",
        "price": 500,
        "emoji": "📦"
    },
    "nickname_color": {
        "name": "🎨 Цветной ник",
        "description": "Уникальный цветной никнейм в профиле",
        "price": 2000,
        "emoji": "🎨"
    },
    "double_daily": {
        "name": "⚡ Двойной бонус",
        "description": "Удвоенный ежедневный бонус на 7 дней",
        "price": 3000,
        "emoji": "⚡"
    }
}
