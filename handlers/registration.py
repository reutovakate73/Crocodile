from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, BotCommand
from aiogram.fsm.context import FSMContext
from states import Registration, CategorySelection
from aiogram.exceptions import TelegramBadRequest

router = Router()

CHANNELS = [
    ("@infa_sotka_channel", "Инфа Сотка"),
]

async def is_user_subscribed(bot, user_id: int) -> bool:
    for channel, _ in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ("left", "kicked"):
                return False
        except TelegramBadRequest:
            return False
    return True

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await message.bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="new_game", description="Новая игра"),
        BotCommand(command="score", description="Показать текущий счёт"),
        BotCommand(command="end_game", description="Завершить игру")
    ])

    if not await is_user_subscribed(message.bot, message.from_user.id):
        buttons = [
            [InlineKeyboardButton(text=name, url=f"https://t.me/{channel[1:]}")]
            for channel, name in CHANNELS
        ]
        buttons.append([InlineKeyboardButton(text="🔄 Я подписался", callback_data="check_subs")])
        await message.answer(
            "❗ Чтобы играть, нужно подписаться на оба канала:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        return

    await state.clear()
    await message.answer(
        "🎉 Добро пожаловать в игру <b>Крокодил</b>!\n\nВведите имя первого игрока 👇",
        parse_mode="HTML"
    )
    await state.set_state(Registration.getting_name)

@router.callback_query(F.data == "check_subs")
async def recheck_subs(callback: CallbackQuery, state: FSMContext):
    if not await is_user_subscribed(callback.bot, callback.from_user.id):
        await callback.answer("❌ Вы ещё не подписались", show_alert=True)
        return

    await callback.message.answer("✅ Подписка подтверждена! Введите имя первого игрока 👇")
    await state.set_state(Registration.getting_name)

@router.message(F.text == "/new_game")
async def cmd_new_game(message: Message, state: FSMContext):
    if not await is_user_subscribed(message.bot, message.from_user.id):
        buttons = [
            [InlineKeyboardButton(text=name, url=f"https://t.me/{channel[1:]}")]
            for channel, name in CHANNELS
        ]
        buttons.append([InlineKeyboardButton(text="🔄 Я подписался", callback_data="check_subs")])
        await message.answer(
            "❗ Чтобы начать новую игру, подпишитесь на канал:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        return

    await state.clear()
    await message.answer(
        "🔄 <b>Новая игра!</b>\n\nВведите имя игрока 👇",
        parse_mode="HTML"
    )
    await state.set_state(Registration.getting_name)

@router.message(Registration.getting_name)
async def get_player_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("❌ Имя не может быть пустым. Попробуйте снова.")
        return

    data = await state.get_data()
    players = data.get("players", [])
    players.append({"name": name, "score": 0})
    await state.update_data(players=players)

    await message.answer(
        f"✅ Игрок <b>{name}</b> добавлен!",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить игрока", callback_data="add_more")],
            [InlineKeyboardButton(text="✅ Начать игру", callback_data="choose_category")]
        ])
    )

@router.callback_query(F.data == "add_more")
async def add_more_player(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите имя следующего игрока 👇")
    await state.set_state(Registration.getting_name)

@router.callback_query(F.data == "choose_category")
async def choose_category(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    players = data.get("players", [])
    if not players:
        await callback.message.answer("⚠️ Сначала нужно добавить хотя бы одного игрока.")
        return

    await state.set_state(CategorySelection.choosing_category)

    await callback.message.answer(
        "📂 Выберите категорию слов:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Стандартный набор", callback_data="Стандартный набор")],
            [InlineKeyboardButton(text="Продвинутый набор", callback_data="Продвинутый набор")],
            [InlineKeyboardButton(text="Крылатые выражения", callback_data="Крылатые выражения")]
        ])
    )
