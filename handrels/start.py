# handlers/start.py

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from database import add_user, get_user, update_balance, update_user
from keyboards import main_menu_keyboard
from config import (
    BOT_NAME, BOT_VERSION, REFERRAL_BONUS_INVITER,
    REFERRAL_BONUS_INVITED, ADMINS
)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    referrer_id = 0

    # Проверяем реферальную ссылку
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referrer_id = int(args[1].replace("ref_", ""))
            if referrer_id == user.id:
                referrer_id = 0
        except ValueError:
            referrer_id = 0

    # Регистрация пользователя
    is_new = await add_user(
        user_id=user.id,
        username=user.username or "Нет",
        first_name=user.first_name or "Пользователь",
        last_name=user.last_name or "",
        referrer_id=referrer_id
    )

    if is_new and referrer_id > 0:
        # Начисляем бонусы
        referrer = await get_user(referrer_id)
        if referrer:
            await update_balance(
                referrer_id, REFERRAL_BONUS_INVITER,
                "Реферальный бонус (пригласил)"
            )
            await update_balance(
                user.id, REFERRAL_BONUS_INVITED,
                "Реферальный бонус (приглашён)"
            )
            await update_user(
                referrer_id,
                referral_count=referrer["referral_count"] + 1
            )

            try:
                await message.bot.send_message(
                    referrer_id,
                    f"🎉 По вашей ссылке зарегистрировался "
                    f"<b>{user.first_name}</b>!\n"
                    f"💰 Вы получили {REFERRAL_BONUS_INVITER} монет!",
                    parse_mode="HTML"
                )
            except Exception:
                pass

    welcome_text = (
        f"{'🎉 Добро пожаловать' if is_new else '👋 С возвращением'}, "
        f"<b>{user.first_name}</b>!\n\n"
        f"{BOT_NAME} v{BOT_VERSION}\n\n"
        f"🎮 Играй в мини-игры\n"
        f"💰 Зарабатывай монеты\n"
        f"🛒 Покупай в магазине\n"
        f"🎁 Используй промокоды\n"
        f"👥 Приглашай друзей\n"
        f"🏆 Соревнуйся с другими\n\n"
        f"Выбери действие из меню ниже 👇"
    )

    await message.answer(
        welcome_text,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "menu")
async def callback_menu(callback: CallbackQuery):
    user = callback.from_user
    db_user = await get_user(user.id)

    if not db_user:
        await add_user(
            user.id, user.username or "Нет",
            user.first_name or "Пользователь",
            user.last_name or ""
        )

    await callback.message.edit_text(
        f"🏠 <b>Главное меню</b>\n\n"
        f"Привет, <b>{user.first_name}</b>!\n"
        f"Выбери действие 👇",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "about")
async def callback_about(callback: CallbackQuery):
    from database import get_all_users_count
    users_count = await get_all_users_count()

    text = (
        f"ℹ️ <b>О боте</b>\n\n"
        f"🤖 {BOT_NAME}\n"
        f"📌 Версия: {BOT_VERSION}\n"
        f"👥 Пользователей: {users_count}\n\n"
        f"<b>Возможности:</b>\n"
        f"• 🎮 8 мини-игр\n"
        f"• 🛒 Магазин предметов\n"
        f"• 🎁 Промокоды\n"
        f"• 📅 Ежедневные бонусы\n"
        f"• 👥 Реферальная система\n"
        f"• 🏆 Рейтинги игроков\n"
        f"• 💬 Система поддержки\n"
        f"• ⚙️ Настройки\n\n"
        f"Разработано с ❤️"
    )

    from keyboards import back_to_menu_keyboard
    await callback.message.edit_text(
        text,
        reply_markup=back_to_menu_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer(
        f"🏠 <b>Главное меню</b>\n\nВыбери действие 👇",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id not in ADMINS:
        await message.answer("❌ У вас нет доступа!")
        return

    from keyboards import admin_keyboard
    await message.answer(
        "🔧 <b>Админ-панель</b>\n\nВыберите действие:",
        reply_markup=admin_keyboard(),
        parse_mode="HTML"
                )
