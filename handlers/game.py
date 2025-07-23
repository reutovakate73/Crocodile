
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states import GameState
from words import WORDS
import asyncio, random
router = Router()
timers = {}
@router.callback_query(F.data == "start_game", GameState.waiting_for_start)
async def start_game(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    players = data.get("players", [])
    index = data.get("current_index", 0)
    category = data.get("category")
    used = set(data.get("used_words", []))
    word_list = WORDS.get(category, [])
    available = [w for w in word_list if w not in used]
    if not available:
        await callback.message.answer("🔚 Слова в этой категории закончились.")
        return
    word = random.choice(available)
    used.add(word)
    await state.update_data(current_word=word, used_words=used)
    await callback.message.answer(
        f"Слово показывает <b>{players[index]['name']}</b>\n📦 Слово: <b>{word}</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Отгадали", callback_data="guessed"),
             InlineKeyboardButton(text="❌ Не отгадали", callback_data="not_guessed")]
        ])
    )
    await state.set_state(GameState.word_in_play)
    timer = await callback.message.answer("⏱ Осталось: <b>60</b>", parse_mode="HTML")
    async def countdown():
        for t in range(59, 0, -1):
            await asyncio.sleep(1)
            try:
                await timer.edit_text(f"⏱ Осталось: <b>{t}</b>", parse_mode="HTML")
            except:
                break
        await timer.edit_text("⏰ Время вышло!", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Отгадали", callback_data="guessed"),
             InlineKeyboardButton(text="❌ Не отгадали", callback_data="not_guessed")]
        ]))
    timers[callback.message.chat.id] = asyncio.create_task(countdown())
@router.callback_query(F.data.in_(["guessed", "not_guessed"]), GameState.word_in_play)
async def answer(callback: CallbackQuery, state: FSMContext):
    task = timers.pop(callback.message.chat.id, None)
    if task:
        task.cancel()
    data = await state.get_data()
    players = data.get("players", [])
    index = data.get("current_index", 0)
    if callback.data == "guessed":
        players[index]["score"] += 1
        await callback.message.answer(f"🎉 {players[index]['name']} получает 1 очко.")
    else:
        await callback.message.answer("😔 Очки не начислены.")
    index = (index + 1) % len(players)
    await state.update_data(players=players, current_index=index)
    await callback.message.answer(
        f"Следующий ход: <b>{players[index]['name']}</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📦 Показать слово", callback_data="start_game")]
        ])
    )
    await state.set_state(GameState.waiting_for_start)
from aiogram.types import Message

@router.message(F.text == "/end_game")
async def end_game(message: Message, state: FSMContext):
    data = await state.get_data()
    players = data.get("players", [])

    if not players:
        await message.answer("❌ Игра ещё не началась или игроков нет.")
        return

    text = "🏁 <b>Игра завершена!</b>\n\n🏆 Итоги:\n\n"
    for p in sorted(players, key=lambda x: x['score'], reverse=True):
        text += f"👤 <b>{p['name']}</b>: {p['score']} очков\n"

    await message.answer(text, parse_mode="HTML")
    await state.clear()

