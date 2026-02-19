# handlers/admin.py

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from database import (
    get_all_users_count, get_user, update_balance,
    update_user, create_promo, get_all_promos,
    delete_promo, get_open_tickets, reply_ticket,
    get_ticket, get_all_user_ids
)
from keyboards import admin_keyboard, back_to_menu_keyboard
from config import ADMINS, CURRENCY_EMOJI

router = Router()


class AdminStates(StatesGroup):
    waiting_promo_data = State()
    waiting_broadcast = State()
    waiting_user_id = State()
    waiting_give_coins_id = State()
    waiting_give_coins_amount = State()
    waiting_ban_id = State()
    waiting_ticket_reply_id = State()
    waiting_ticket_reply_text = State()


def is_admin(user_id: int) -> bool:
    return user_id in ADMINS


# ==================== Админ панель ====================

@router.callback_query(F.data == "admin_panel")
async def callback_admin_panel(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа!", show_alert=True)
        return

    await callback.message.edit_text(
        "🔧 <b>Админ-панель</b>\n\nВыберите действие:",
        reply_markup=admin_keyboard(),
        parse_mode="HTML"
    )


# ==================== Статистика ====================

@router.callback_query(F.data == "admin_stats")
async def callback_admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    total_users = await get_all_users_count()
    tickets = await get_open_tickets()
    promos = await get_all_promos()
    active_promos = len(
        [p for p in promos if p["is_active"]]
    )

    text = (
        f"📊 <b>Статистика бота</b>\n\n"
        f"👥 Всего пользователей: <b>{total_users}</b>\n"
        f"🎁 Активных промокодов: <b>{active_promos}</b>\n"
        f"📋 Открытых тикетов: <b>{len(tickets)}</b>\n"
    )

    await callback.message.edit_text(
        text,
        reply_markup=admin_keyboard(),
        parse_mode="HTML"
    )


# ==================== Создание промокода ====================

@router.callback_query(F.data == "admin_create_promo")
async def callback_admin_create_promo(callback: CallbackQuery,
                                       state: FSMContext):
    if not is_admin(callback.from_user.id):
        return

    await callback.message.edit_text(
        "➕ <b>Создание промокода</b>\n\n"
        "Отправьте данные в формате:\n"
        "<code>КОД НАГРАДА МАКС_ИСПОЛЬЗОВАНИЙ</code>\n\n"
        "Пример: <code>BONUS500 500 100</code>\n"
        "(промокод BONUS500 на 500 монет, 100 использований)",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_promo_data)


@router.message(AdminStates.waiting_promo_data)
async def process_promo_data(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    try:
        parts = message.text.split()
        code = parts[0]
        reward = int(parts[1])
        max_uses = int(parts[2])
    except (IndexError, ValueError):
        await message.answer(
            "❌ Неверный формат! Попробуйте снова.\n"
            "Формат: <code>КОД НАГРАДА МАКС_ИСПОЛЬЗОВАНИЙ</code>",
            parse_mode="HTML"
        )
        return

    success = await create_promo(
        code, reward, max_uses, message.from_user.id
    )

    if success:
        text = (
            f"✅ <b>Промокод создан!</b>\n\n"
            f"🔑 Код: <code>{code.upper()}</code>\n"
            f"💰 Награда: {reward} {CURRENCY_EMOJI}\n"
            f"👥 Макс. использований: {max_uses}"
        )
    else:
        text = "❌ Промокод с таким кодом уже существует!"

    await message.answer(
        text,
        reply_markup=admin_keyboard(),
        parse_mode="HTML"
    )
    await state.clear()


# ==================== Список промокодов ====================

@router.callback_query(F.data == "admin_list_promos")
async def callback_admin_list_promos(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    promos = await get_all_promos()

    if not promos:
        text = "📋 <b>Промокоды</b>\n\n<i>Нет промокодов</i>"
    else:
        text = "📋 <b>Промокоды</b>\n\n"
        for p in promos:
            status = "✅" if p["is_active"] else "❌"
            text += (
                f"{status} <code>{p['code']}</code>\n"
                f"   💰 {p['reward']} | "
                f"👥 {p['current_uses']}/{p['max_uses']}\n\n"
            )

    await callback.message.edit_text(
        text,
        reply_markup=admin_keyboard(),
        parse_mode="HTML"
    )


# ==================== Рассылка ====================

@router.callback_query(F.data == "admin_broadcast")
async def callback_admin_broadcast(callback: CallbackQuery,
                                    state: FSMContext):
    if not is_admin(callback.from_user.id):
        return

    await callback.message.edit_text(
        "📨 <b>Рассылка</b>\n\n"
        "Отправьте текст для рассылки всем пользователям:",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_broadcast)


@router.message(AdminStates.waiting_broadcast)
async def process_broadcast(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    user_ids = await get_all_user_ids()
    sent = 0
    failed = 0

    status_msg = await message.answer(
        f"📨 Рассылка запущена... 0/{len(user_ids)}"
    )

    for user_id in user_ids:
        try:
            await message.bot.send_message(
                user_id,
                f"📢 <b>Объявление</b>\n\n{message.text}",
                parse_mode="HTML"
            )
            sent += 1
        except Exception:
            failed += 1

        if (sent + failed) % 50 == 0:
            try:
                await status_msg.edit_text(
                    f"📨 Рассылка... {sent + failed}/{len(user_ids)}"
                )
            except Exception:
                pass

    await status_msg.edit_text(
        f"✅ <b>Рассылка завершена!</b>\n\n"
        f"📨 Отправлено: {sent}\n"
        f"❌ Ошибок: {failed}",
        parse_mode="HTML"
    )
    await state.clear()


# ==================== Найти юзера ====================

@router.callback_query(F.data == "admin_find_user")
async def callback_admin_find_user(callback: CallbackQuery,
                                    state: FSMContext):
    if not is_admin(callback.from_user.id):
        return

    await callback.message.edit_text(
        "👤 <b>Поиск пользователя</b>\n\n"
        "Отправьте ID пользователя:",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_user_id)


@router.message(AdminStates.waiting_user_id)
async def process_find_user(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    try:
        user_id = int(message.text)
    except ValueError:
        await message.answer("❌ Неверный ID!")
        return

    user = await get_user(user_id)
    if not user:
        await message.answer("❌ Пользователь не найден!")
        await state.clear()
        return

    banned_status = "🚫 Забанен" if user["is_banned"] else "✅ Активен"
    text = (
        f"👤 <b>Информация о пользователе</b>\n\n"
        f"🆔 ID: <code>{user['user_id']}</code>\n"
        f"📛 Имя: {user['first_name']} {user['last_name']}\n"
        f"🔗 Username: @{user['username']}\n"
        f"💰 Баланс: {user['balance']} {CURRENCY_EMOJI}\n"
        f"⭐ Уровень: {user['level']}\n"
        f"🎮 Игр: {user['games_played']}\n"
        f"🏆 Побед: {user['games_won']}\n"
        f"👥 Рефералов: {user['referral_count']}\n"
        f"📌 Статус: {banned_status}\n"
    )

    await message.answer(
        text,
        reply_markup=admin_keyboard(),
        parse_mode="HTML"
    )
    await state.clear()


# ==================== Выдать монеты ====================

@router.callback_query(F.data == "admin_give_coins")
async def callback_admin_give_coins(callback: CallbackQuery,
                                     state: FSMContext):
    if not is_admin(callback.from_user.id):
        return

    await callback.message.edit_text(
        "💰 <b>Выдача монет</b>\n\n"
        "Отправьте ID пользователя:",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_give_coins_id)


@router.message(AdminStates.waiting_give_coins_id)
async def process_give_coins_id(message: Message, 
                                 state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    try:
        user_id = int(message.text)
    except ValueError:
        await message.answer("❌ Неверный ID!")
        return

    user = await get_user(user_id)
    if not user:
        await message.answer("❌ Пользователь не найден!")
        await state.clear()
        return

    await state.update_data(target_user_id=user_id)
    await message.answer(
        f"Пользователь: {user['first_name']} "
        f"(ID: {user_id})\n\n"
        f"Введите количество монет "
        f"(отрицательное число для снятия):"
    )
    await state.set_state(AdminStates.waiting_give_coins_amount)


@router.message(AdminStates.waiting_give_coins_amount)
async def process_give_coins_amount(message: Message,
                                     state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    try:
        amount = int(message.text)
    except ValueError:
        await message.answer("❌ Неверная сумма!")
        return

    data = await state.get_data()
    target_user_id = data["target_user_id"]

    await update_balance(
        target_user_id, amount, "Начислено администратором"
    )

    sign = "+" if amount > 0 else ""
    await message.answer(
        f"✅ Пользователю {target_user_id} "
        f"начислено {sign}{amount} {CURRENCY_EMOJI}",
        reply_markup=admin_keyboard(),
    )

    # Уведомляем пользователя
    try:
        await message.bot.send_message(
            target_user_id,
            f"{'💰 Вам начислено' if amount > 0 else '💸 Списано'} "
            f"<b>{abs(amount)}</b> {CURRENCY_EMOJI} "
            f"администратором!",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await state.clear()


# ==================== Бан ====================

@router.callback_query(F.data == "admin_ban")
async def callback_admin_ban(callback: CallbackQuery,
                              state: FSMContext):
    if not is_admin(callback.from_user.id):
        return

    await callback.message.edit_text(
        "🚫 <b>Бан пользователя</b>\n\n"
        "Отправьте ID пользователя для бана/разбана:",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_ban_id)


@router.message(AdminStates.waiting_ban_id)
async def process_ban_user(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    try:
        user_id = int(message.text)
    except ValueError:
        await message.answer("❌ Неверный ID!")
        return

    user = await get_user(user_id)
    if not user:
        await message.answer("❌ Пользователь не найден!")
        await state.clear()
        return

    new_ban_status = 0 if user["is_banned"] else 1
    await update_user(user_id, is_banned=new_ban_status)

    action = "забанен 🚫" if new_ban_status else "разбанен ✅"
    await message.answer(
        f"Пользователь {user['first_name']} "
        f"(ID: {user_id}) {action}",
        reply_markup=admin_keyboard()
    )
    await state.clear()


# ==================== Тикеты ====================

@router.callback_query(F.data == "admin_tickets")
async def callback_admin_tickets(callback: CallbackQuery,
                                  state: FSMContext):
    if not is_admin(callback.from_user.id):
        return

    tickets = await get_open_tickets()

    if not tickets:
        text = (
            "📋 <b>Тикеты</b>\n\n"
            "<i>Нет открытых тикетов</i>"
        )
        await callback.message.edit_text(
            text,
            reply_markup=admin_keyboard(),
            parse_mode="HTML"
        )
        return

    text = "📋 <b>Открытые тикеты</b>\n\n"
    for t in tickets:
        text += (
            f"🔖 Тикет #{t['id']}\n"
            f"👤 User ID: {t['user_id']}\n"
            f"💬 {t['message'][:100]}...\n\n"
        )

    text += "\nОтправьте ID тикета для ответа:"

    await callback.message.edit_text(
        text, parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_ticket_reply_id)


@router.message(AdminStates.waiting_ticket_reply_id)
async def process_ticket_id(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    try:
        ticket_id = int(message.text)
    except ValueError:
        await message.answer("❌ Неверный ID тикета!")
        return

    ticket = await get_ticket(ticket_id)
    if not ticket:
        await message.answer("❌ Тикет не найден!")
        await state.clear()
        return

    await state.update_data(ticket_id=ticket_id)
    await message.answer(
        f"📋 Тикет #{ticket_id}\n"
        f"💬 Сообщение: {ticket['message']}\n\n"
        f"Введите ответ:"
    )
    await state.set_state(AdminStates.waiting_ticket_reply_text)


@router.message(AdminStates.waiting_ticket_reply_text)
async def process_ticket_reply(message: Message, 
                                state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    data = await state.get_data()
    ticket_id = data["ticket_id"]

    ticket = await get_ticket(ticket_id)
    await reply_ticket(ticket_id, message.text)

    await message.answer(
        f"✅ Ответ на тикет #{ticket_id} отправлен!",
        reply_markup=admin_keyboard()
    )

    # Уведомляем пользователя
    try:
        await message.bot.send_message(
            ticket["user_id"],
            f"💬 <b>Ответ от поддержки</b>\n\n"
            f"📋 Тикет #{ticket_id}\n"
            f"📝 Ваш вопрос: {ticket['message']}\n\n"
            f"💡 Ответ: {message.text}",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await state.clear()
