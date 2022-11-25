from aiogram.dispatcher.filters.state import StatesGroup, State

class Chose(StatesGroup):
    playerID = State()
    playerID_showdata = State()
    matchID = State()
    matchID_showdata = State()
    matchID_finish = State()



    