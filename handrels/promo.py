# handlers/promo.py

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from database import use_promo, add_xp
from keyboards import promo_keyboard, back_to_menu_keyboard

router = Router()


class PromoStates(StatesGroup):
    waiting_for_code = State()


@router.callback_query(F.data == "promo")
async def callback_promo(callback: CallbackQuery):
    text = (
        f"🎁 <b>Промокоды</b>\n\n"
        f"Введите промокод, чтобы получить награду!\n\n"
        f"💡 Промокоды можно найти:\n"
        f"• В нашем канале\n"
        f"• В розыгрышах\n"
        f"• У партнёров\n"
    )

    await callback.message.edit_text(
        text,
        reply_markup=promo_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "enter_promo")
async def callback_enter_promo(callback: CallbackQuery, 
                                state: FSMContext):
    await callback.message.edit_text(
        "🔑 <b>Введите промокод:</b>\n\n"
        "<i>Отправьте промокод сообщением</i>",
        parse_mode="HTML"
    )
    await state.set_state(PromoStates.waiting_for_code)


@router.message(PromoStates.waiting_for_code)
async def process_promo_code(message: Message, state: FSMContext):
    code = message.text.strip()

    reward, result_text = await use_promo(message.from_user.id, code)

    if reward:
        # XP за промокод
        leveled_up, new_level = await add_xp(
            message.from_user.id, 10
        )
        if leveled_up:
            result_text += (
                f"\n🎉 Уровень повышен до <b>{new_level}</b>!"
            )

    await message.answer(
        result_text,
        reply_markup=back_to_menu_keyboard(),
        parse_mode="HTML"
    )
    await state.clear()
