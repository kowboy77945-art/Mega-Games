# database.py

import aiosqlite
import time
from config import START_BALANCE

DB_PATH = "bot_database.db"


async def init_db():
    """Инициализация базы данных"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Таблица пользователей
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                balance INTEGER DEFAULT 100,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                referrer_id INTEGER DEFAULT 0,
                referral_count INTEGER DEFAULT 0,
                games_played INTEGER DEFAULT 0,
                games_won INTEGER DEFAULT 0,
                total_earned INTEGER DEFAULT 0,
                total_spent INTEGER DEFAULT 0,
                is_vip INTEGER DEFAULT 0,
                is_premium INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                has_color_nick INTEGER DEFAULT 0,
                has_double_daily INTEGER DEFAULT 0,
                double_daily_until INTEGER DEFAULT 0,
                vip_until INTEGER DEFAULT 0,
                premium_until INTEGER DEFAULT 0,
                last_daily INTEGER DEFAULT 0,
                last_game INTEGER DEFAULT 0,
                notifications INTEGER DEFAULT 1,
                language TEXT DEFAULT 'ru',
                registered_at INTEGER DEFAULT 0
            )
        """)

        # Таблица промокодов
        await db.execute("""
            CREATE TABLE IF NOT EXISTS promo_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                reward INTEGER,
                max_uses INTEGER DEFAULT 1,
                current_uses INTEGER DEFAULT 0,
                created_by INTEGER,
                is_active INTEGER DEFAULT 1,
                created_at INTEGER DEFAULT 0,
                expires_at INTEGER DEFAULT 0
            )
        """)

        # Таблица использования промокодов
        await db.execute("""
            CREATE TABLE IF NOT EXISTS promo_uses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                promo_code TEXT,
                used_at INTEGER DEFAULT 0
            )
        """)

        # Таблица транзакций
        await db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT,
                amount INTEGER,
                description TEXT,
                created_at INTEGER DEFAULT 0
            )
        """)

        # Таблица инвентаря
        await db.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                item_id TEXT,
                item_name TEXT,
                purchased_at INTEGER DEFAULT 0
            )
        """)

        # Таблица тикетов поддержки
        await db.execute("""
            CREATE TABLE IF NOT EXISTS support_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message TEXT,
                status TEXT DEFAULT 'open',
                admin_reply TEXT,
                created_at INTEGER DEFAULT 0,
                replied_at INTEGER DEFAULT 0
            )
        """)

        await db.commit()


# ==================== USERS ====================

async def add_user(user_id: int, username: str, first_name: str,
                   last_name: str, referrer_id: int = 0):
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                """INSERT INTO users 
                (user_id, username, first_name, last_name, balance, 
                 referrer_id, registered_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (user_id, username, first_name, last_name,
                 START_BALANCE, referrer_id, int(time.time()))
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False


async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ) as cursor:
            return await cursor.fetchone()


async def update_user(user_id: int, **kwargs):
    async with aiosqlite.connect(DB_PATH) as db:
        for key, value in kwargs.items():
            await db.execute(
                f"UPDATE users SET {key} = ? WHERE user_id = ?",
                (value, user_id)
            )
        await db.commit()


async def update_balance(user_id: int, amount: int, 
                         description: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        if amount > 0:
            await db.execute(
                """UPDATE users 
                SET balance = balance + ?, total_earned = total_earned + ? 
                WHERE user_id = ?""",
                (amount, amount, user_id)
            )
        else:
            await db.execute(
                """UPDATE users 
                SET balance = balance + ?, total_spent = total_spent + ? 
                WHERE user_id = ?""",
                (amount, abs(amount), user_id)
            )

        # Логируем транзакцию
        await db.execute(
            """INSERT INTO transactions 
            (user_id, type, amount, description, created_at) 
            VALUES (?, ?, ?, ?, ?)""",
            (user_id, "credit" if amount > 0 else "debit",
             amount, description, int(time.time()))
        )
        await db.commit()


async def add_xp(user_id: int, xp: int):
    """Добавить опыт и проверить повышение уровня"""
    user = await get_user(user_id)
    if not user:
        return False, 0

    new_xp = user["xp"] + xp
    current_level = user["level"]
    new_level = current_level

    # Формула уровня: level * 100 XP для следующего уровня
    while new_xp >= new_level * 100:
        new_xp -= new_level * 100
        new_level += 1

    await update_user(user_id, xp=new_xp, level=new_level)

    leveled_up = new_level > current_level
    return leveled_up, new_level


async def get_top_users(limit: int = 10, order_by: str = "balance"):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            f"""SELECT * FROM users 
            WHERE is_banned = 0 
            ORDER BY {order_by} DESC LIMIT ?""",
            (limit,)
        ) as cursor:
            return await cursor.fetchall()


async def get_all_users_count():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            result = await cursor.fetchone()
            return result[0]


async def get_all_user_ids():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_id FROM users WHERE is_banned = 0"
        ) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]


# ==================== PROMO CODES ====================

async def create_promo(code: str, reward: int, max_uses: int,
                       created_by: int, expires_hours: int = 0):
    async with aiosqlite.connect(DB_PATH) as db:
        expires_at = 0
        if expires_hours > 0:
            expires_at = int(time.time()) + (expires_hours * 3600)

        try:
            await db.execute(
                """INSERT INTO promo_codes 
                (code, reward, max_uses, created_by, created_at, expires_at) 
                VALUES (?, ?, ?, ?, ?, ?)""",
                (code.upper(), reward, max_uses, created_by,
                 int(time.time()), expires_at)
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False


async def use_promo(user_id: int, code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Проверяем существование промокода
        async with db.execute(
            "SELECT * FROM promo_codes WHERE code = ? AND is_active = 1",
            (code.upper(),)
        ) as cursor:
            promo = await cursor.fetchone()

        if not promo:
            return None, "❌ Промокод не найден или неактивен"

        # Проверяем срок действия
        if promo["expires_at"] > 0 and \
                int(time.time()) > promo["expires_at"]:
            return None, "⏰ Срок действия промокода истёк"

        # Проверяем лимит использований
        if promo["current_uses"] >= promo["max_uses"]:
            return None, "📛 Промокод уже использован максимальное число раз"

        # Проверяем, не использовал ли пользователь
        async with db.execute(
            "SELECT * FROM promo_uses WHERE user_id = ? AND promo_code = ?",
            (user_id, code.upper())
        ) as cursor:
            used = await cursor.fetchone()

        if used:
            return None, "🚫 Вы уже использовали этот промокод"

        # Активируем промокод
        reward = promo["reward"]

        await db.execute(
            "UPDATE promo_codes SET current_uses = current_uses + 1 WHERE code = ?",
            (code.upper(),)
        )
        await db.execute(
            "INSERT INTO promo_uses (user_id, promo_code, used_at) VALUES (?, ?, ?)",
            (user_id, code.upper(), int(time.time()))
        )
        await db.commit()

    # Начисляем награду
    await update_balance(user_id, reward, f"Промокод: {code.upper()}")

    return reward, f"✅ Промокод активирован! Получено: {reward} 💰"


async def get_all_promos():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM promo_codes ORDER BY created_at DESC"
        ) as cursor:
            return await cursor.fetchall()


async def delete_promo(code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM promo_codes WHERE code = ?", (code.upper(),)
        )
        await db.commit()


# ==================== INVENTORY ====================

async def add_to_inventory(user_id: int, item_id: str, item_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO inventory 
            (user_id, item_id, item_name, purchased_at) 
            VALUES (?, ?, ?, ?)""",
            (user_id, item_id, item_name, int(time.time()))
        )
        await db.commit()


async def get_inventory(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM inventory WHERE user_id = ? ORDER BY purchased_at DESC",
            (user_id,)
        ) as cursor:
            return await cursor.fetchall()


# ==================== TRANSACTIONS ====================

async def get_transactions(user_id: int, limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT * FROM transactions 
            WHERE user_id = ? 
            ORDER BY created_at DESC LIMIT ?""",
            (user_id, limit)
        ) as cursor:
            return await cursor.fetchall()


# ==================== SUPPORT ====================

async def create_ticket(user_id: int, message: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO support_tickets 
            (user_id, message, created_at) 
            VALUES (?, ?, ?)""",
            (user_id, message, int(time.time()))
        )
        await db.commit()


async def get_open_tickets():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM support_tickets WHERE status = 'open' ORDER BY created_at DESC"
        ) as cursor:
            return await cursor.fetchall()


async def reply_ticket(ticket_id: int, reply: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """UPDATE support_tickets 
            SET status = 'closed', admin_reply = ?, replied_at = ? 
            WHERE id = ?""",
            (reply, int(time.time()), ticket_id)
        )
        await db.commit()


async def get_ticket(ticket_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM support_tickets WHERE id = ?", (ticket_id,)
        ) as cursor:
            return await cursor.fetchone()
