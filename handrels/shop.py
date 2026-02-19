# handlers/shop.py

import time
import random
from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import (
    get_user, update_balance, update_user,
    add_to_inventory, add_xp
)
from keyboards import shop_keyboard, buy_confirm_keyboard, back_to_menu_keyboard
from config import SHOP_ITEMS, CURRENCY_EMOJI

router = Router()


@router.callback_query(F.data == "shop")
async def callback_shop(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        return

    text = (
        f"🛒 <b>Магазин</b>\n\n"
        f"💰 Ваш баланс: <b>{user['balance']}</b> {CURRENCY_EMOJI}\n\n"
        f"Выберите товар для покупки:\n\n"
    )

    for item_id, item in SHOP_ITEMS.items():
        text += (
            f"{item['emoji']} <b>{item['name']}</b>\n"
            f"   📝 {item['description']}\n"
            f"   💵 Цена: {item['price']} {CURRENCY_EMOJI}\n\n"
        )

    await callback.message.edit_text(
        text,
        reply_markup=shop_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("buy_"))
async def callback_buy_item(callback: CallbackQuery):
    item_id = callback.data.replace("buy_", "")

    if item_id not in SHOP_ITEMS:
        await callback.answer("❌ Товар не найден!", show_alert=True)
        return

    item = SHOP_ITEMS[item_id]
    user = await get_user(callback.from_user.id)

    text = (
        f"🛒 <b>Подтверждение покупки</b>\n\n"
        f"{item['emoji']} <b>{item['name']}</b>\n"
        f"📝 {item['description']}\n"
        f"💵 Цена: {item['price']} {CURRENCY_EMOJI}\n\n"
        f"💰 Ваш баланс: {user['balance']} {CURRENCY_EMOJI}\n\n"
    )

    if user["balance"] < item["price"]:
        text += f"❌ <b>Недостаточно средств!</b>\n"
        text += (
            f"Не хватает: "
            f"{item['price'] - user['balance']} {CURRENCY_EMOJI}"
        )
        await callback.message.edit_text(
            text,
            reply_markup=back_to_menu_keyboard(),
            parse_mode="HTML"
        )
        return

    text += "Подтвердить покупку?"

    await callback.message.edit_text(
        text,
        reply_markup=buy_confirm_keyboard(item_id),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("confirm_buy_"))
async def callback_confirm_buy(callback: CallbackQuery):
    item_id = callback.data.replace("confirm_buy_", "")

    if item_id not in SHOP_ITEMS:
        await callback.answer("❌ Товар не найден!", show_alert=True)
        return

    item = SHOP_ITEMS[item_id]
    user = await get_user(callback.from_user.id)

    if user["balance"] < item["price"]:
        await callback.answer(
            "❌ Недостаточно средств!", show_alert=True
        )
        return

    # Списываем деньги
    await update_balance(
        callback.from_user.id,
        -item["price"],
        f"Покупка: {item['name']}"
    )

    # Применяем эффект
    result_text = ""

    if item_id == "vip":
        until = int(time.time()) + (30 * 24 * 3600)
        await update_user(
            callback.from_user.id, is_vip=1, vip_until=until
        )
        result_text = "👑 VIP статус активирован на 30 дней!"

    elif item_id == "premium":
        until = int(time.time()) + (30 * 24 * 3600)
        await update_user(
            callback.from_user.id, is_premium=1, premium_until=until
        )
        result_text = "💎 Premium статус активирован на 30 дней!"

    elif item_id == "lootbox":
        reward = random.randint(100, 1000)
        await update_balance(
            callback.from_user.id, reward, "Лутбокс"
        )
        result_text = f"📦 Вы открыли лутбокс и получили {reward} {CURRENCY_EMOJI}!"

    elif item_id == "nickname_color":
        await update_user(callback.from_user.id, has_color_nick=1)
        result_text = "🎨 Цветной никнейм активирован!"

    elif item_id == "double_daily":
        until = int(time.time()) + (7 * 24 * 3600)
        await update_user(
            callback.from_user.id,
            has_double_daily=1,
            double_daily_until=until
        )
        result_text = "⚡ Удвоенный бонус активирован на 7 дней!"

    # Добавляем в инвентарь
    await add_to_inventory(
        callback.from_user.id, item_id, item["name"]
    )

    # Даём XP за покупку
    leveled_up, new_level = await add_xp(callback.from_user.id, 25)
    level_text = ""
    if leveled_up:
        level_text = (
            f"\n\n🎉 Поздравляем! Вы достигли "
            f"<b>{new_level} уровня</b>!"
        )

    text = (
        f"✅ <b>Покупка совершена!</b>\n\n"
        f"{item['emoji']} {item['name']}\n\n"
        f"{result_text}{level_text}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=back_to_menu_keyboard(),
        parse_mode="HTML"
    )
