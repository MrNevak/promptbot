import asyncio
import aiosqlite

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import BOT_TOKEN
from db import init_db, seed, get_products, get_product, DB_NAME
from payments import create_invoice

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(m: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="🛍 Каталог", callback_data="catalog")

    await m.answer(
        "AI Store\nВыбери продукт:",
        reply_markup=kb.as_markup()
    )


@dp.callback_query(F.data == "catalog")
async def catalog(c: CallbackQuery):
    products = await get_products()

    kb = InlineKeyboardBuilder()

    for p in products:
        kb.button(
            text=f"{p[1]} — {p[2]}$",
            callback_data=f"p_{p[0]}"
        )

    kb.adjust(1)

    await c.message.edit_text(
        "Каталог:",
        reply_markup=kb.as_markup()
    )


@dp.callback_query(F.data.startswith("p_"))
async def product(c: CallbackQuery):
    pid = int(c.data.split("_")[1])

    p = await get_product(pid)

    text = f"{p[1]}\n\n{p[2]}\n\nЦена: {p[3]}$"

    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Купить", callback_data=f"buy_{pid}")
    kb.button(text="⬅ Назад", callback_data="catalog")
    kb.adjust(1)

    await c.message.edit_text(
        text,
        reply_markup=kb.as_markup()
    )


@dp.callback_query(F.data.startswith("buy_"))
async def buy(c: CallbackQuery):
    pid = int(c.data.split("_")[1])

    p = await get_product(pid)

    invoice = await create_invoice(
        amount=p[3],
        name=p[1],
        payload=f"product_{pid}"
    )

    if not invoice.get("ok"):
        await c.message.answer("Ошибка создания счёта.")
        return

    invoice_id = invoice["result"]["invoice_id"]
    pay_url = invoice["result"]["pay_url"]

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT INTO orders (user_id, product_id, invoice_id, status)
            VALUES (?, ?, ?, ?)
            """,
            (c.from_user.id, pid, str(invoice_id), "pending")
        )
        await db.commit()

    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Оплатить", url=pay_url)

    await c.message.answer(
        f"Оплата: {p[1]}",
        reply_markup=kb.as_markup()
    )


async def main():
    await init_db()
    await seed()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())