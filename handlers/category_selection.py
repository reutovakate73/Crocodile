
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states import CategorySelection, GameState
router = Router()
@router.callback_query(F.data.in_(["Стандартный набор", "Продвинутый набор", "Крылатые выражения"]), CategorySelection.choosing_category)
async def set_category(callback: CallbackQuery, state: FSMContext):
    await state.update_data(category=callback.data)
    await state.set_state(GameState.waiting_for_start)
    await callback.message.answer(
        f"✅ Категория выбрана: <b>{callback.data}</b>\nНажмите кнопку 'Начать игру', чтобы получить первое слово.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Начать игру", callback_data="start_game")]
        ])
    )
