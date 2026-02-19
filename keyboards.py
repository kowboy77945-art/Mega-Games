# keyboards.py

from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, 
    ReplyKeyboardMarkup, KeyboardButton
)
from config import SHOP_ITEMS


def main_menu_keyboard():
    """Главное меню"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
            InlineKeyboardButton(text="💰 Баланс", callback_data="balance")
        ],
        [
            InlineKeyboardButton(text="🛒 Магазин", callback_data="shop"),
            InlineKeyboardButton(text="🎮 Игры", callback_data="games")
        ],
        [
            InlineKeyboardButton(text="🎁 Промокод", callback_data="promo"),
            InlineKeyboardButton(text="📅 Бонус", callback_data="daily")
        ],
        [
            InlineKeyboardButton(text="👥 Рефералы", callback_data="referral"),
            InlineKeyboardButton(text="🏆 Топ", callback_data="leaderboard")
        ],
        [
            InlineKeyboardButton(text="🎒 Инвентарь", callback_data="inventory"),
            InlineKeyboardButton(text="📜 История", callback_data="transactions")
        ],
        [
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings"),
            InlineKeyboardButton(text="💬 Поддержка", callback_data="support")
        ],
        [
            InlineKeyboardButton(text="ℹ️ О боте", callback_data="about")
        ]
    ])
    return keyboard


def back_to_menu_keyboard():
    """Кнопка назад в меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="menu")]
    ])


def profile_keyboard():
    """Клавиатура профиля"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💰 Баланс", callback_data="balance"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="stats")
        ],
        [
            InlineKeyboardButton(text="🎒 Инвентарь", callback_data="inventory"),
            InlineKeyboardButton(text="📜 Транзакции", callback_data="transactions")
        ],
        [
            InlineKeyboardButton(text="🔙 Главное меню", callback_data="menu")
        ]
    ])


def shop_keyboard():
    """Клавиатура магазина"""
    buttons = []
    for item_id, item in SHOP_ITEMS.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"{item['emoji']} {item['name']} — {item['price']} 💰",
                callback_data=f"buy_{item_id}"
            )
        ])
    buttons.append([
        InlineKeyboardButton(text="🔙 Главное меню", callback_data="menu")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def buy_confirm_keyboard(item_id: str):
    """Подтверждение покупки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Купить",
                callback_data=f"confirm_buy_{item_id}"
            ),
            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data="shop"
            )
        ]
    ])


def games_keyboard():
    """Клавиатура игр"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🎲 Кости", callback_data="game_dice"
            ),
            InlineKeyboardButton(
                text="🪙 Монетка", callback_data="game_coin"
            )
        ],
        [
            InlineKeyboardButton(
                text="🎰 Слоты", callback_data="game_slots"
            ),
            InlineKeyboardButton(
                text="🔢 Угадай число", callback_data="game_number"
            )
        ],
        [
            InlineKeyboardButton(
                text="🎯 Дартс", callback_data="game_darts"
            ),
            InlineKeyboardButton(
                text="⚽ Футбол", callback_data="game_football"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏀 Баскетбол", callback_data="game_basketball"
            ),
            InlineKeyboardButton(
                text="🎳 Боулинг", callback_data="game_bowling"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 Главное меню", callback_data="menu"
            )
        ]
    ])


def game_bet_keyboard(game: str):
    """Клавиатура ставок"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="10 💰", callback_data=f"bet_{game}_10"
            ),
            InlineKeyboardButton(
                text="50 💰", callback_data=f"bet_{game}_50"
            ),
            InlineKeyboardButton(
                text="100 💰", callback_data=f"bet_{game}_100"
            )
        ],
        [
            InlineKeyboardButton(
                text="250 💰", callback_data=f"bet_{game}_250"
            ),
            InlineKeyboardButton(
                text="500 💰", callback_data=f"bet_{game}_500"
            ),
            InlineKeyboardButton(
                text="1000 💰", callback_data=f"bet_{game}_1000"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 К играм", callback_data="games"
            )
        ]
    ])


def coin_side_keyboard(bet: int):
    """Выбор стороны монетки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🦅 Орёл", callback_data=f"coin_heads_{bet}"
            ),
            InlineKeyboardButton(
                text="🪙 Решка", callback_data=f"coin_tails_{bet}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 К играм", callback_data="games"
            )
        ]
    ])


def number_guess_keyboard(bet: int):
    """Клавиатура угадай число"""
    buttons = []
    row = []
    for i in range(1, 11):
        row.append(
            InlineKeyboardButton(
                text=str(i), callback_data=f"number_{bet}_{i}"
            )
        )
        if len(row) == 5:
            buttons.append(row)
            row = []
    buttons.append([
        InlineKeyboardButton(text="🔙 К играм", callback_data="games")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def promo_keyboard():
    """Клавиатура промокодов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔑 Ввести промокод",
                callback_data="enter_promo"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 Главное меню", callback_data="menu"
            )
        ]
    ])


def referral_keyboard(user_id: int, bot_username: str):
    """Клавиатура рефералов"""
    ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📤 Поделиться ссылкой",
                switch_inline_query=f"Присоединяйся! {ref_link}"
            )
        ],
        [
            InlineKeyboardButton(
                text="📋 Копировать ссылку",
                callback_data="copy_ref_link"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 Главное меню", callback_data="menu"
            )
        ]
    ])


def leaderboard_keyboard():
    """Клавиатура лидерборда"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💰 По балансу",
                callback_data="top_balance"
            ),
            InlineKeyboardButton(
                text="⭐ По уровню",
                callback_data="top_level"
            )
        ],
        [
            InlineKeyboardButton(
                text="🎮 По играм",
                callback_data="top_games"
            ),
            InlineKeyboardButton(
                text="👥 По рефералам",
                callback_data="top_referrals"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 Главное меню", callback_data="menu"
            )
        ]
    ])


def settings_keyboard(user):
    """Клавиатура настроек"""
    notif_status = "🔔 Вкл" if user["notifications"] else "🔕 Выкл"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"Уведомления: {notif_status}",
                callback_data="toggle_notifications"
            )
        ],
        [
            InlineKeyboardButton(
                text="🗑 Сбросить статистику игр",
                callback_data="reset_game_stats"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 Главное меню", callback_data="menu"
            )
        ]
    ])


def confirm_reset_keyboard():
    """Подтверждение сброса"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Да, сбросить",
                callback_data="confirm_reset_stats"
            ),
            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data="settings"
            )
        ]
    ])


def support_keyboard():
    """Клавиатура поддержки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📝 Создать тикет",
                callback_data="create_ticket"
            )
        ],
        [
            InlineKeyboardButton(
                text="📋 Мои тикеты",
                callback_data="my_tickets"
            )
        ],
        [
            InlineKeyboardButton(
                text="❓ FAQ",
                callback_data="faq"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 Главное меню", callback_data="menu"
            )
        ]
    ])


# ==================== ADMIN ====================

def admin_keyboard():
    """Админ клавиатура"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📊 Статистика бота",
                callback_data="admin_stats"
            )
        ],
        [
            InlineKeyboardButton(
                text="➕ Создать промокод",
                callback_data="admin_create_promo"
            ),
            InlineKeyboardButton(
                text="📋 Промокоды",
                callback_data="admin_list_promos"
            )
        ],
        [
            InlineKeyboardButton(
                text="📨 Рассылка",
                callback_data="admin_broadcast"
            ),
            InlineKeyboardButton(
                text="👤 Найти юзера",
                callback_data="admin_find_user"
            )
        ],
        [
            InlineKeyboardButton(
                text="💰 Выдать монеты",
                callback_data="admin_give_coins"
            ),
            InlineKeyboardButton(
                text="🚫 Забанить",
                callback_data="admin_ban"
            )
        ],
        [
            InlineKeyboardButton(
                text="📋 Тикеты",
                callback_data="admin_tickets"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 Главное меню",
                callback_data="menu"
            )
        ]
    ])
