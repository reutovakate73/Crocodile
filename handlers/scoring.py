from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(lambda message: message.text == "/score")
async def show_score(message: Message, state: FSMContext):
    data = await state.get_data()
    players = data.get("players", [])
    if not players:
        await message.answer("❌ Игра ещё не началась или нет игроков.")
        return

    score_text = "🏆 <b>Текущий счёт:</b>\n\n"
    for player in players:
        score_text += f"👤 <b>{player['name']}</b>: {player['score']} очков\n"

    await message.answer(score_text, parse_mode="HTML")
