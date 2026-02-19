# handlers/referral.py

from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import get_user
from keyboards import referral_keyboard, back_to_menu_keyboard
from config import REFERRAL_BONUS_INVITER, REFERRAL_BONUS_INVITED

router = Router()


@router.callback_query(F.data == "referral")
async def callback_referral(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    bot_info = await callback.bot.get_me()
    bot_username = bot_info.username

    ref_link = (
        f"https://t.me/{bot_username}"
        f"?start=ref_{callback.from_user.id}"
    )

    text = (
        f"👥 <b>Реферальная система</b>\n\n"
        f"Приглашай друзей и получай бонусы!\n\n"
        f"💰 Ты получаешь: <b>{REFERRAL_BONUS_INVITER}</b> монет\n"
        f"💰 Друг получает: <b>{REFERRAL_BONUS_INVITED}</b> монет\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Приглашено друзей: <b>{user['referral_count']}</b>\n"
        f"💵 Заработано с рефералов: "
        f"<b>{user['referral_count'] * REFERRAL_BONUS_INVITER}</b> 💰\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"🔗 Ваша ссылка:\n"
        f"<code>{ref_link}</code>\n\n"
        f"<i>Нажмите на ссылку, чтобы скопировать</i>"
    )

    await callback.message.edit_text(
        text,
        reply_markup=referral_keyboard(
            callback.from_user.id, bot_username
        ),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "copy_ref_link")
async def callback_copy_ref(callback: CallbackQuery):
    await callback.answer(
        "📋 Нажмите на ссылку в сообщении, чтобы скопировать!",
        show_alert=True
    )
