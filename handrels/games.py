# handlers/games.py

import random
import asyncio
from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import (
    get_user, update_balance, update_user, add_xp
)
from keyboards import (
    games_keyboard, game_bet_keyboard,
    coin_side_keyboard, number_guess_keyboard,
    back_to_menu_keyboard
)
from config import CURRENCY_EMOJI

router = Router()


@router.callback_query(F.data == "games")
async def callback_games(callback: CallbackQuery):
    text = (
        f"🎮 <b>Мини-игры</b>\n\n"
        f"Выбери игру и делай ставку!\n\n"
        f"🎲 <b>Кости</b> — Кинь кости, 4+ побеждает\n"
        f"🪙 <b>Монетка</b> — Угадай сторону\n"
        f"🎰 <b>Слоты</b> — Крути барабаны\n"
        f"🔢 <b>Угадай число</b> — Угадай от 1 до 10\n"
        f"🎯 <b>Дартс</b> — Попади в цель\n"
        f"⚽ <b>Футбол</b> — Забей гол\n"
        f"🏀 <b>Баскетбол</b> — Забрось мяч\n"
        f"🎳 <b>Боулинг</b> — Сбей кегли\n"
    )

    await callback.message.edit_text(
        text,
        reply_markup=games_keyboard(),
        parse_mode="HTML"
    )


# ============== Выбор ставки ==============

@router.callback_query(F.data.startswith("game_"))
async def callback_game_select(callback: CallbackQuery):
    game = callback.data.replace("game_", "")
    user = await get_user(callback.from_user.id)

    game_names = {
        "dice": "🎲 Кости",
        "coin": "🪙 Монетка",
        "slots": "🎰 Слоты",
        "number": "🔢 Угадай число",
        "darts": "🎯 Дартс",
        "football": "⚽ Футбол",
        "basketball": "🏀 Баскетбол",
        "bowling": "🎳 Боулинг"
    }

    text = (
        f"{game_names.get(game, '🎮 Игра')}\n\n"
        f"💰 Ваш баланс: <b>{user['balance']}</b> {CURRENCY_EMOJI}\n\n"
        f"Выберите ставку:"
    )

    await callback.message.edit_text(
        text,
        reply_markup=game_bet_keyboard(game),
        parse_mode="HTML"
    )


# ============== Обработка ставок ==============

@router.callback_query(F.data.startswith("bet_"))
async def callback_bet(callback: CallbackQuery):
    parts = callback.data.split("_")
    game = parts[1]
    bet = int(parts[2])

    user = await get_user(callback.from_user.id)

    if user["balance"] < bet:
        await callback.answer(
            "❌ Недостаточно средств!", show_alert=True
        )
        return

    if game == "coin":
        await callback.message.edit_text(
            f"🪙 <b>Монетка</b>\n\n"
            f"Ставка: {bet} {CURRENCY_EMOJI}\n"
            f"Выберите сторону:",
            reply_markup=coin_side_keyboard(bet),
            parse_mode="HTML"
        )
        return

    if game == "number":
        await callback.message.edit_text(
            f"🔢 <b>Угадай число</b>\n\n"
            f"Ставка: {bet} {CURRENCY_EMOJI}\n"
            f"Угадайте число от 1 до 10:\n"
            f"(Выигрыш x5!)",
            reply_markup=number_guess_keyboard(bet),
            parse_mode="HTML"
        )
        return

    # Для остальных игр — используем Telegram анимации
    await play_animated_game(callback, game, bet)


async def play_animated_game(callback: CallbackQuery, 
                              game: str, bet: int):
    """Игры с анимациями Telegram"""
    user = await get_user(callback.from_user.id)
    if user["balance"] < bet:
        await callback.answer("❌ Недостаточно средств!", show_alert=True)
        return

    # Списываем ставку
    await update_balance(
        callback.from_user.id, -bet, f"Ставка: {game}"
    )

    emoji_map = {
        "dice": "🎲",
        "slots": "🎰",
        "darts": "🎯",
        "football": "⚽",
        "basketball": "🏀",
        "bowling": "🎳"
    }

    emoji = emoji_map.get(game, "🎲")

    # Отправляем анимацию
    msg = await callback.message.answer_dice(emoji=emoji)
    value = msg.dice.value

    # Ждём анимацию
    await asyncio.sleep(4)

    # Определяем результат
    won = False
    multiplier = 2

    if game == "dice":
        won = value >= 4
        multiplier = 2
    elif game == "slots":
        if value == 64:
            won = True
            multiplier = 10  # Джекпот
        elif value in [1, 22, 43]:
            won = True
            multiplier = 5
        else:
            won = False
    elif game == "darts":
        won = value == 6  # Центр
        multiplier = 5 if value == 6 else 0
        if value >= 4:
            won = True
            multiplier = 2
    elif game == "football":
        won = value in [3, 4, 5]
        multiplier = 2
    elif game == "basketball":
        won = value in [4, 5]
        multiplier = 2
    elif game == "bowling":
        won = value == 6  # Страйк
        multiplier = 3 if value == 6 else 0
        if value >= 4:
            won = True
            multiplier = 2

    # Обработка результата
    await process_game_result(
        callback, game, bet, won, multiplier, value
    )


async def process_game_result(callback, game, bet, won, 
                                multiplier, value=None):
    """Обработка результата игры"""
    user_id = callback.from_user.id

    # Обновляем статистику
    user = await get_user(user_id)
    await update_user(
        user_id,
        games_played=user["games_played"] + 1
    )

    if won:
        winnings = bet * multiplier
        await update_balance(
            user_id, winnings, f"Выигрыш: {game}"
        )
        await update_user(
            user_id,
            games_won=user["games_won"] + 1
        )

        # XP за победу
        leveled_up, new_level = await add_xp(user_id, 15)
        level_text = ""
        if leveled_up:
            level_text = (
                f"\n🎉 Уровень повышен до <b>{new_level}</b>!"
            )

        text = (
            f"🎉 <b>ПОБЕДА!</b>\n\n"
            f"💰 Ставка: {bet} {CURRENCY_EMOJI}\n"
            f"🏆 Выигрыш: <b>+{winnings}</b> {CURRENCY_EMOJI}\n"
            f"📊 Множитель: x{multiplier}\n"
            f"{level_text}"
        )
    else:
        # XP за участие
        await add_xp(user_id, 5)

        text = (
            f"😔 <b>Проигрыш</b>\n\n"
            f"💸 Потеряно: {bet} {CURRENCY_EMOJI}\n"
            f"Попробуй ещё раз! 🍀"
        )

    updated_user = await get_user(user_id)
    text += f"\n\n💰 Баланс: {updated_user['balance']} {CURRENCY_EMOJI}"

    await callback.message.answer(
        text,
        reply_markup=games_keyboard(),
        parse_mode="HTML"
    )


# ============== Монетка ==============

@router.callback_query(F.data.startswith("coin_"))
async def callback_coin_flip(callback: CallbackQuery):
    parts = callback.data.split("_")
    choice = parts[1]  # heads or tails
    bet = int(parts[2])

    user = await get_user(callback.from_user.id)
    if user["balance"] < bet:
        await callback.answer(
            "❌ Недостаточно средств!", show_alert=True
        )
        return

    # Списываем ставку
    await update_balance(
        callback.from_user.id, -bet, "Ставка: Монетка"
    )

    # Бросаем монетку
    result = random.choice(["heads", "tails"])
    won = choice == result

    result_name = "🦅 Орёл" if result == "heads" else "🪙 Решка"
    choice_name = "🦅 Орёл" if choice == "heads" else "🪙 Решка"

    await callback.message.edit_text(
        f"🪙 <b>Подбрасываем монетку...</b>",
        parse_mode="HTML"
    )

    await asyncio.sleep(2)

    await process_game_result(
        callback, "Монетка", bet, won, 2
    )

    # Дополнительное сообщение о результате
    result_text = (
        f"\n🪙 Ваш выбор: {choice_name}\n"
        f"🎲 Результат: {result_name}"
    )
    await callback.message.answer(result_text)


# ============== Угадай число ==============

@router.callback_query(F.data.startswith("number_"))
async def callback_number_guess(callback: CallbackQuery):
    parts = callback.data.split("_")
    bet = int(parts[1])
    guess = int(parts[2])

    user = await get_user(callback.from_user.id)
    if user["balance"] < bet:
        await callback.answer(
            "❌ Недостаточно средств!", show_alert=True
        )
        return

    # Списываем ставку
    await update_balance(
        callback.from_user.id, -bet, "Ставка: Угадай число"
    )

    # Генерируем число
    correct = random.randint(1, 10)
    won = guess == correct

    await callback.message.edit_text(
        f"🔢 <b>Генерируем число...</b>",
        parse_mode="HTML"
    )

    await asyncio.sleep(2)

    await process_game_result(
        callback, "Угадай число", bet, won, 5
    )

    result_text = (
        f"\n🔢 Ваш выбор: {guess}\n"
        f"🎯 Загаданное число: {correct}"
    )
    await callback.message.answer(result_text)
