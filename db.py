import aiosqlite

DB_NAME = "data.sqlite"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            invoice_id TEXT,
            status TEXT DEFAULT 'pending'
        )
        """)

        await db.commit()


async def seed():
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT COUNT(*) FROM products")
        if (await cur.fetchone())[0] == 0:
            await db.executemany("""
            INSERT INTO products (name, description, price, file)
            VALUES (?, ?, ?, ?)
            """, [
                ("Prompt Pack SaaS", "Промпты для SaaS", 10, "FILE_ID"),
                ("Telegram Bot Kit", "Шаблоны ботов", 15, "FILE_ID"),
                ("Marketing Pack", "Маркетинг AI", 20, "FILE_ID"),
            ])
        await db.commit()


async def get_products():
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT id, name, price FROM products")
        return await cur.fetchall()


async def get_product(pid: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            "SELECT id, name, description, price, file FROM products WHERE id=?",
            (pid,)
        )
        return await cur.fetchone()