# handlers/daily.py

import time
import random
from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import get_user, update_balance, update_user, add_xp
from keyboards import back_to_menu_keyboard
from config import DAILY_BONUS_MIN, DAILY_BONUS_MAX, CURRENCY_EMOJI

router = Router()

DAILY_COOLDOWN = 24 * 3600  # 24 часа


@router.callback_query(F.data == "daily")
async def callback_daily(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        return

    current_time = int(time.time())
    last_daily = user["last_daily"]
    time_diff = current_time - last_daily

    if time_diff < DAILY_COOLDOWN:
        remaining = DAILY_COOLDOWN - time_diff
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        seconds = remaining % 60

        text = (
            f"📅 <b>Ежедневный бонус</b>\n\n"
            f"⏳ Вы уже получали бонус сегодня!\n\n"
            f"⏰ Следующий бонус через:\n"
            f"<b>{hours}ч {minutes}м {seconds}с</b>\n\n"
            f"💡 <i>Возвращайтесь каждый день за бонусом!</i>"
        )

        await callback.message.edit_text(
            text,
            reply_markup=back_to_menu_keyboard(),
            parse_mode="HTML"
        )
        return

    # Генерируем бонус
    bonus = random.randint(DAILY_BONUS_MIN, DAILY_BONUS_MAX)

    # Проверяем двойной бонус
    if user["has_double_daily"] and \
            user["double_daily_until"] > current_time:
        bonus *= 2
        double_text = "\n⚡ <b>Двойной бонус активен!</b>"
    else:
        double_text = ""

    # VIP бонус +50%
    if user["is_vip"] and user["vip_until"] > current_time:
        bonus = int(bonus * 1.5)
        double_text += "\n👑 <b>VIP бонус +50%!</b>"

    # Premium бонус +100%
    if user["is_premium"] and user["premium_until"] > current_time:
        bonus *= 2
        double_text += "\n💎 <b>Premium бонус x2!</b>"

    # Начисляем бонус
    await update_balance(
        callback.from_user.id, bonus, "Ежедневный бонус"
    )
    await update_user(
        callback.from_user.id, last_daily=current_time
    )

    # XP за ежедневный бонус
    leveled_up, new_level = await add_xp(callback.from_user.id, 20)
    level_text = ""
    if leveled_up:
        level_text = (
            f"\n\n🎉 Уровень повышен до <b>{new_level}</b>!"
        )

    updated_user = await get_user(callback.from_user.id)

    text = (
        f"📅 <b>Ежедневный бонус</b>\n\n"
        f"🎁 Вы получили: <b>+{bonus}</b> {CURRENCY_EMOJI}\n"
        f"{double_text}\n\n"
        f"💰 Баланс: <b>{updated_user['balance']}</b> {CURRENCY_EMOJI}"
        f"{level_text}\n\n"
        f"⏰ Следующий бонус через 24 часа"
    )

    await callback.message.edit_text(
        text,
        reply_markup=back_to_menu_keyboard(),
        parse_mode="HTML"
      )
