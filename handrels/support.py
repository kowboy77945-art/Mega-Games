# handlers/support.py

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from database import create_ticket, get_user
from keyboards import support_keyboard, back_to_menu_keyboard
from config import ADMINS

router = Router()


class SupportStates(StatesGroup):
    waiting_for_message = State()


@router.callback_query(F.data == "support")
async def callback_support(callback: CallbackQuery):
    text = (
        f"💬 <b>Поддержка</b>\n\n"
        f"Если у вас есть вопросы или проблемы, "
        f"вы можете создать тикет.\n\n"
        f"Наша команда ответит вам в кратчайшие сроки!"
    )

    await callback.message.edit_text(
        text,
        reply_markup=support_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "create_ticket")
async def callback_create_ticket(callback: CallbackQuery,
                                  state: FSMContext):
    await callback.message.edit_text(
        "📝 <b>Создание тикета</b>\n\n"
        "Опишите вашу проблему или вопрос.\n"
        "Отправьте сообщение:",
        parse_mode="HTML"
    )
    await state.set_state(SupportStates.waiting_for_message)


@router.message(SupportStates.waiting_for_message)
async def process_ticket_message(message: Message, 
                                  state: FSMContext):
    await create_ticket(message.from_user.id, message.text)

    await message.answer(
        f"✅ <b>Тикет создан!</b>\n\n"
        f"Ваше обращение:\n"
        f"<i>{message.text}</i>\n\n"
        f"Мы ответим вам в ближайшее время!",
        reply_markup=back_to_menu_keyboard(),
        parse_mode="HTML"
    )

    # Уведомляем админов
    for admin_id in ADMINS:
        try:
            await message.bot.send_message(
                admin_id,
                f"📩 <b>Новый тикет!</b>\n\n"
                f"👤 От: {message.from_user.first_name} "
                f"(@{message.from_user.username})\n"
                f"🆔 ID: {message.from_user.id}\n\n"
                f"💬 Сообщение:\n{message.text}",
                parse_mode="HTML"
            )
        except Exception:
            pass

    await state.clear()


@router.callback_query(F.data == "faq")
async def callback_faq(callback: CallbackQuery):
    text = (
        f"❓ <b>FAQ — Частые вопросы</b>\n\n"
        f"<b>Q: Как заработать монеты?</b>\n"
        f"A: Играйте в мини-игры, получайте ежедневные "
        f"бонусы, приглашайте друзей!\n\n"
        f"<b>Q: Как активировать промокод?</b>\n"
        f"A: Нажмите «🎁 Промокод» → «🔑 Ввести промокод»\n\n"
        f"<b>Q: Как пригласить друга?</b>\n"
        f"A: Перейдите в раздел «👥 Рефералы» "
        f"и поделитесь ссылкой\n\n"
        f"<b>Q: Что даёт VIP/Premium?</b>\n"
        f"A: Увеличенные ежедневные бонусы "
        f"и особый статус в профиле\n\n"
        f"<b>Q: Как работают уровни?</b>\n"
        f"A: Выполняйте действия (игры, покупки, бонусы) "
        f"чтобы получать XP и повышать уровень"
    )

    await callback.message.edit_text(
        text,
        reply_markup=back_to_menu_keyboard(),
        parse_mode="HTML"
  )
