# handlers/settings.py

from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import get_user, update_user, get_top_users
from keyboards import (
    settings_keyboard, confirm_reset_keyboard,
    leaderboard_keyboard, back_to_menu_keyboard
)
from config import CURRENCY_EMOJI

router = Router()


# ==================== НАСТРОЙКИ ====================

@router.callback_query(F.data == "settings")
async def callback_settings(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        return

    text = (
        f"⚙️ <b>Настройки</b>\n\n"
        f"Управляйте настройками вашего аккаунта:"
    )

    await callback.message.edit_text(
        text,
        reply_markup=settings_keyboard(user),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "toggle_notifications")
async def callback_toggle_notifications(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    new_value = 0 if user["notifications"] else 1

    await update_user(
        callback.from_user.id, notifications=new_value
    )

    status = "включены ✅" if new_value else "выключены ❌"
    await callback.answer(
        f"🔔 Уведомления {status}", show_alert=True
    )

    # Обновляем клавиатуру
    updated_user = await get_user(callback.from_user.id)
    await callback.message.edit_reply_markup(
        reply_markup=settings_keyboard(updated_user)
    )


@router.callback_query(F.data == "reset_game_stats")
async def callback_reset_stats(callback: CallbackQuery):
    text = (
        f"🗑 <b>Сброс статистики</b>\n\n"
        f"⚠️ Это действие сбросит:\n"
        f"• Количество игр\n"
        f"• Количество побед\n\n"
        f"<b>Баланс и уровень НЕ изменятся!</b>\n\n"
        f"Вы уверены?"
    )

    await callback.message.edit_text(
        text,
        reply_markup=confirm_reset_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "confirm_reset_stats")
async def callback_confirm_reset(callback: CallbackQuery):
    await update_user(
        callback.from_user.id,
        games_played=0,
        games_won=0
    )

    await callback.answer(
        "✅ Статистика игр сброшена!", show_alert=True
    )

    user = await get_user(callback.from_user.id)
    await callback.message.edit_text(
        f"⚙️ <b>Настройки</b>\n\n"
        f"✅ Статистика успешно сброшена!",
        reply_markup=settings_keyboard(user),
        parse_mode="HTML"
    )


# ==================== ЛИДЕРБОРД ====================

@router.callback_query(F.data == "leaderboard")
async def callback_leaderboard(callback: CallbackQuery):
    text = (
        f"🏆 <b>Таблица лидеров</b>\n\n"
        f"Выберите категорию рейтинга:"
    )

    await callback.message.edit_text(
        text,
        reply_markup=leaderboard_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("top_"))
async def callback_top(callback: CallbackQuery):
    category = callback.data.replace("top_", "")

    category_map = {
        "balance": ("balance", "💰 По балансу", CURRENCY_EMOJI),
        "level": ("level", "⭐ По уровню", "уровень"),
        "games": ("games_won", "🎮 По победам", "побед"),
        "referrals": ("referral_count", "👥 По рефералам", "рефералов")
    }

    if category not in category_map:
        return

    order_by, title, unit = category_map[category]
    users = await get_top_users(limit=10, order_by=order_by)

    medals = ["🥇", "🥈", "🥉"]

    text = f"🏆 <b>Топ-10 {title}</b>\n\n"

    for i, user in enumerate(users):
        medal = medals[i] if i < 3 else f"  {i + 1}."
        value = user[order_by]

        name = user["first_name"]
        if user["is_premium"]:
            name = f"💎 {name}"
        elif user["is_vip"]:
            name = f"👑 {name}"

        is_me = " ← Вы" if user["user_id"] == callback.from_user.id else ""
        text += f"{medal} <b>{name}</b> — {value} {unit}{is_me}\n"

    if not users:
        text += "<i>Пока никого нет</i>"

    await callback.message.edit_text(
        text,
        reply_markup=leaderboard_keyboard(),
        parse_mode="HTML"
    )
