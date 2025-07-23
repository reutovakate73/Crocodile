# main.py

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import registration, category_selection, game, scoring

async def main():
    # Создаём бота с HTML-режимом разметки
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))

    # FSM-хранилище
    dp = Dispatcher(storage=MemoryStorage())

    # Подключаем все обработчики
    dp.include_router(registration.router)
    dp.include_router(category_selection.router)
    dp.include_router(game.router)
    dp.include_router(scoring.router)

    # Меню команд бота
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="new_game", description="Новая игра"),
        BotCommand(command="score", description="Показать текущий счёт"),
        BotCommand(command="end_game", description="Завершить игру")
    ])

    print("Бот запущен и слушает команды...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
