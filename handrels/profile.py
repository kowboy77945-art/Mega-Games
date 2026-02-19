# handlers/profile.py

from aiogram import Router, F
from aiogram.types import CallbackQuery
import time
from datetime import datetime

from database import (
    get_user, add_user, get_transactions, get_inventory
)
from keyboards import (
    profile_keyboard, back_to_menu_keyboard
)
from config import CURRENCY_EMOJI

router = Router()


def get_level_bar(xp: int, level: int):
    """Прогресс-бар уровня"""
    needed = level * 100
    progress = int((xp / needed) * 10) if needed > 0 else 0
    bar = "▓" * progress + "░" * (10 - progress)
    return f"[{bar}] {xp}/{needed} XP"


def get_rank(level: int):
    """Получить ранг по уровню"""
    ranks = {
        1: "🌱 Новичок",
        5: "⚔️ Воин",
        10: "🛡️ Рыцарь",
        20: "👑 Король",
        30: "🏆 Легенда",
        50: "🌟 Мифический",
        75: "💫 Божественный",
        100: "🔱 Создатель"
    }
    current_rank = "🌱 Новичок"
    for min_level, rank in ranks.items():
        if level >= min_level:
            current_rank = rank
    return current_rank


@router.callback_query(F.data == "profile")
async def callback_profile(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await add_user(
            callback.from_user.id,
            callback.from_user.username or "Нет",
            callback.from_user.first_name or "Пользователь",
            callback.from_user.last_name or ""
        )
        user = await get_user(callback.from_user.id)

    # Формируем статус
    status_parts = []
    if user["is_premium"]:
        status_parts.append("💎 Premium")
    if user["is_vip"]:
        status_parts.append("👑 VIP")
    if user["has_color_nick"]:
        status_parts.append("🎨 Цветной ник")
    if user["has_double_daily"]:
        status_parts.append("⚡ x2 бонус")
    status = " | ".join(status_parts) if status_parts else "Нет"

    # Ранг
    rank = get_rank(user["level"])
    level_bar = get_level_bar(user["xp"], user["level"])

    # Дата регистрации
    reg_date = datetime.fromtimestamp(
        user["registered_at"]
    ).strftime("%d.%m.%Y") if user["registered_at"] else "Неизвестно"

    # Винрейт
    winrate = 0
    if user["games_played"] > 0:
        winrate = round(
            (user["games_won"] / user["games_played"]) * 100, 1
        )

    text = (
        f"👤 <b>Профиль</b>\n\n"
        f"📛 Имя: <b>{user['first_name']}</b>\n"
        f"🔗 Username: @{user['username']}\n"
        f"🆔 ID: <code>{user['user_id']}</code>\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 Баланс: <b>{user['balance']}</b> {CURRENCY_EMOJI}\n"
        f"📈 Заработано всего: {user['total_earned']} {CURRENCY_EMOJI}\n"
        f"📉 Потрачено всего: {user['total_spent']} {CURRENCY_EMOJI}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"⭐ Уровень: <b>{user['level']}</b>\n"
        f"🏅 Ранг: {rank}\n"
        f"📊 {level_bar}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"🎮 Игр сыграно: {user['games_played']}\n"
        f"🏆 Игр выиграно: {user['games_won']}\n"
        f"📊 Винрейт: {winrate}%\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Рефералов: {user['referral_count']}\n"
        f"🏷 Статусы: {status}\n"
        f"📅 Регистрация: {reg_date}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=profile_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "balance")
async def callback_balance(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("❌ Профиль не найден!", show_alert=True)
        return

    text = (
        f"💰 <b>Баланс</b>\n\n"
        f"💵 Текущий баланс: <b>{user['balance']}</b> {CURRENCY_EMOJI}\n\n"
        f"📈 Всего заработано: {user['total_earned']} {CURRENCY_EMOJI}\n"
        f"📉 Всего потрачено: {user['total_spent']} {CURRENCY_EMOJI}\n\n"
        f"<i>Зарабатывайте монеты играя в игры, "
        f"приглашая друзей и получая ежедневные бонусы!</i>"
    )

    await callback.message.edit_text(
        text,
        reply_markup=back_to_menu_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "stats")
async def callback_stats(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        return

    winrate = 0
    if user["games_played"] > 0:
        winrate = round(
            (user["games_won"] / user["games_played"]) * 100, 1
        )

    text = (
        f"📊 <b>Статистика</b>\n\n"
        f"🎮 <b>Игры:</b>\n"
        f"├ Сыграно: {user['games_played']}\n"
        f"├ Побед: {user['games_won']}\n"
        f"├ Поражений: {user['games_played'] - user['games_won']}\n"
        f"└ Винрейт: {winrate}%\n\n"
        f"💰 <b>Финансы:</b>\n"
        f"├ Баланс: {user['balance']} {CURRENCY_EMOJI}\n"
        f"├ Заработано: {user['total_earned']} {CURRENCY_EMOJI}\n"
        f"└ Потрачено: {user['total_spent']} {CURRENCY_EMOJI}\n\n"
        f"⭐ <b>Прогресс:</b>\n"
        f"├ Уровень: {user['level']}\n"
        f"├ Опыт: {user['xp']}\n"
        f"└ Рефералов: {user['referral_count']}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=back_to_menu_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "inventory")
async def callback_inventory(callback: CallbackQuery):
    items = await get_inventory(callback.from_user.id)

    if not items:
        text = (
            f"🎒 <b>Инвентарь</b>\n\n"
            f"<i>Пусто... Загляни в магазин!</i> 🛒"
        )
    else:
        text = f"🎒 <b>Инвентарь</b>\n\n"
        for item in items:
            purchase_date = datetime.fromtimestamp(
                item["purchased_at"]
            ).strftime("%d.%m.%Y %H:%M")
            text += (
                f"• {item['item_name']}\n"
                f"  📅 Куплено: {purchase_date}\n\n"
            )

    await callback.message.edit_text(
        text,
        reply_markup=back_to_menu_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "transactions")
async def callback_transactions(callback: CallbackQuery):
    txns = await get_transactions(callback.from_user.id, limit=10)

    if not txns:
        text = (
            f"📜 <b>История транзакций</b>\n\n"
            f"<i>Пока транзакций нет</i>"
        )
    else:
        text = f"📜 <b>Последние 10 транзакций</b>\n\n"
        for txn in txns:
            emoji = "📈" if txn["amount"] > 0 else "📉"
            sign = "+" if txn["amount"] > 0 else ""
            txn_date = datetime.fromtimestamp(
                txn["created_at"]
            ).strftime("%d.%m %H:%M")
            text += (
                f"{emoji} {sign}{txn['amount']} {CURRENCY_EMOJI}"
                f" — {txn['description']}\n"
                f"   🕐 {txn_date}\n\n"
            )

    await callback.message.edit_text(
        text,
        reply_markup=back_to_menu_keyboard(),
        parse_mode="HTML"
  )
