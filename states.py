
from aiogram.fsm.state import StatesGroup, State
class Registration(StatesGroup):
    getting_name = State()
class CategorySelection(StatesGroup):
    choosing_category = State()
class GameState(StatesGroup):
    waiting_for_start = State()
    word_in_play = State()
