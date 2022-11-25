import json, time, os
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.filters import Text
from main import check_matchID,collect_player_matches,get_stats,collect_match,check_playerID
from aiogram.dispatcher import FSMContext
from cats import Chose
from aiogram.utils.markdown import hbold
from aiogram.contrib.fsm_storage.memory import MemoryStorage

TG_TOKEN = os.getenv("TOKEN")

bot = Bot(token=TG_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

# Обработка старта
@dp.message_handler(commands='start')
async def start(message: types.Message):
    start_buttons = ['🎮 Player ID', '🎬 Match ID', 'ℹ️ Info']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    await message.answer('Choose category from buttons bellow 👇', reply_markup=keyboard)



# Обработка кнопки меню
@dp.message_handler(Text(equals='⬅️ Menu'))
async def menu(message: types.Message):
    start_buttons = ['🎮 Player ID', '🎬 Match ID', 'ℹ️ Info']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    await message.answer('Choose category from buttons bellow 👇', reply_markup=keyboard)


# Обработка player id
@dp.message_handler(Text(equals='🎮 Player ID'))
async def player_id(message: types.Message):
    back_buttons = ['⬅️ Menu']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*back_buttons)

    await message.answer('Send player ID 👉', reply_markup=keyboard)
    await Chose.playerID.set()

# Состояние для меню PlayerID
@dp.message_handler(state=Chose.playerID)
async def matchid_state(message: types.Message,state: FSMContext):
    back_buttons = ['⬅️ Menu']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*back_buttons)

    player_id = message.text
    await state.update_data(playerID=player_id)
    data = await state.get_data()
    parsed_player_id = data.get('playerID')
    if check_playerID(parsed_player_id):
        await message.answer('Please wait..')
        collect_player_matches(parsed_player_id)

        with open('player_stats.json') as file:
            data = json.load(file)
        
        for index, item in enumerate(data):
            card = f'{("🎮 Game №: ")}{item.get("link")}\n' \
                f'{hbold("🎲 Hero: ")}{item.get("hero")}\n' \
                f'{hbold("Match result: ")}{item.get("result")}'             
            if index%20 == 0:
                time.sleep(3)
            await message.answer(card)

        await message.answer('Type in a match ID 👉')
        await Chose.matchID.set()

    elif parsed_player_id != '⬅️ Menu':
        await message.answer('❌ Wrong player ID - make sure you type it correctly')
        await Chose.playerID.set()

    elif parsed_player_id == '⬅️ Menu':
        await state.finish()
        start_buttons = ['🎮 Player ID', '🎬 Match ID', 'ℹ️ Info']
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*start_buttons)
        await message.answer('Choose category from buttons bellow 👇', reply_markup=keyboard)

# Обработка match id
@dp.message_handler(Text(equals='🎬 Match ID'))
async def match_id(message: types.Message):
    back_buttons = ['⬅️ Menu']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*back_buttons)

    await message.answer('Send match ID 👉', reply_markup=keyboard)
    await Chose.matchID.set()


# Состояние для поля MatchID
@dp.message_handler(state=Chose.matchID)
async def matchid_state(message: types.Message,state: FSMContext):
    back_buttons = ['⬅️ Menu']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*back_buttons)

    match_id = message.text
    await state.update_data(matchID=match_id)
    data = await state.get_data()
    parsed_match_id = data.get('matchID')
    if check_matchID(parsed_match_id):
        await message.answer('Please wait..')
        collect_match(parsed_match_id)

        with open('match_stats.json') as file:
            data = json.load(file)

        matchDuration = data[10]
        data.pop(10)

        for item in data:
            heroName = item.get("hero")
            card = comparing(heroName, matchDuration)
            await message.answer(card)
        await state.finish()

    elif parsed_match_id != '⬅️ Menu':
        await message.answer('❌ Wrong match ID - make sure you type it correctly')
        await Chose.matchID.set()

    elif parsed_match_id == '⬅️ Menu':
        await state.finish()
        start_buttons = ['🎮 Player ID', '🎬 Match ID', 'ℹ️ Info']
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*start_buttons)
        await message.answer('Choose category from buttons bellow 👇', reply_markup=keyboard)

@dp.message_handler(state=Chose.matchID)
async def matchid_state(message: types.Message,state: FSMContext):
    back_buttons = ['⬅️ Menu']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*back_buttons)

@dp.message_handler(Text(equals='ℹ️ Info'))
async def info(message: types.Message):
    back_buttons = ['⬅️ Menu']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*back_buttons)

    card = f'{hbold("Hello! You are on the info page 🌀")}\n\n' \
            f'{hbold("This bot was made for course work 📃")}\n' \
            f'{hbold("Bot is made by Danil Morozov 👨‍💻")}\n\n{hbold("VYATSU 2022 🏫")}\n\n' \
            f'{("You can navigate by using menu bellow 👇")}'

    await message.answer(card, reply_markup=keyboard)


def comparing(heroName, duration):
    with open('match_stats.json') as file:
        matchData = json.load(file)
    with open('merged_data.json') as file:
        statsData = json.load(file)
    # matchDuration = matchData[10]
    # matchData.pop(10)
    for stats in statsData:
        for match in matchData:
            if stats.get('name') == match.get('hero') == heroName:
                return f'{hbold("🧚‍♀️ Hero: ")}{heroName}\n\n' \
                    f'{kdaCompare(stats,match)}' \
                    f'{dmgCompare(stats, match, duration)}' \
                    f'{tmgCompare(stats, match, duration)}' \
                    f'{healCompare(stats,match,duration)}' \
                    f'{lasthitsCompare(stats,match,duration)}' \
                    f'{deniesCompare(stats,match,duration)}' \
                    f'{networth(match)}' \
                    f'{gmpExpm(match)}' \
                    f'{winrateCompare(stats)}'
                


    # Супер топ
    # f'{hbold("🧚‍♀️ Hero: ")}{matchItem.get("hero")}\n' \
    # f'{hbold("🔪 K/D/A: ")}{matchItem.get("kills")}/{matchItem.get("deaths")}/{matchItem.get("assists")}{hbold(" You have good KDA! ✔️")}\n' \
    # f'{hbold("🏹 Damage: ")}{matchItem.get("dmg")}{hbold(" ")}\n' \
    # f'{hbold("🗼 Tower Damage: ")}{matchItem.get("tmg")}{hbold(" Towers is not a problem! ✔️")}\n' \
    # f'{hbold("🩺 Heal: ")}{matchItem.get("heal")}{hbold(" Thank you doctor! ✔️")}\n' \
    # f'{hbold("💰 Lashits: ")}{matchItem.get("lasthits")}{hbold(" Not a single creep lost! ✔️")}\n' \
    # f'{hbold("🦠 Denies: ")}{matchItem.get("denies")}{hbold(" Denie and denie! ✔️")}\n' \
    # f'{hbold("💸 Networth: ")}{matchItem.get("networth")}\n' \
    # f'{hbold("📊 GPM/EXPM: ")}{matchItem.get("gmp")}/{matchItem.get("exp")}\n' \
    # f'{hbold("🏆 Hero winrate: ")}{statsData[index].get("winrate")}{hbold(" This hero have a good winrate! ✔️")}\n'

    # Плохо
    # f'{hbold("🧚‍♀️ Hero: ")}{matchData[i].get("hero")}\n' \
    # f'{hbold("🔪 K/D/A: ")}{matchData[i].get("kills")}/{matchData[i].get("deaths")}/{matchData[i].get("assists")}{hbold(" You have good KDA! ✔️")}\n' \
    # f'{hbold("🏹 Damage: ")}{matchData[i].get("dmg")}{hbold(" ❌ If you are support - ignore, others make damage!")}\n' \
    # f'{hbold("🗼 Tower Damage: ")}{matchData[i].get("tmg")}{hbold(" ❌ You need to pushing with your team!")}\n' \
    # f'{hbold("🩺 Heal: ")}{matchData[i].get("heal")}{hbold(" ❌ If you are carry - ignore, others heal your team!")}\n' \
    # f'{hbold("💰 Lashits: ")}{matchData[i].get("lasthits")}{hbold(" ❌ Train your lasthits!")}\n' \
    # f'{hbold("🦠 Denies: ")}{matchData[i].get("denies")}{hbold(" ❌ Train your denie skill!")}\n' \
    # f'{hbold("💸 Networth: ")}{matchData[i].get("networth")}\n' \
    # f'{hbold("📊 GPM/EXPM: ")}{matchData[i].get("gmp")}/{matchData[i].get("exp")}\n' \
    # f'{hbold("🏆 Hero winrate: ")}{statsData[i].get("winrate")}{hbold(" This hero have a good winrate! ✔️")}\n'

def kdaCompare(statData,matchData):
    if (float(statData.get('kills')) - float(matchData.get('kills'))) > 3:
        if float(statData.get('deaths')) < float(matchData.get('deaths')):
            if (float(statData.get('assists')) - float(matchData.get('assists'))) > 4:
                return f'{hbold("🔪 K/D/A: ")}{matchData.get("kills")}/{matchData.get("deaths")}/{matchData.get("assists")}{hbold(" You have bad KDA! Kill more, die less, help your team! ❌")}\n'
            elif (float(statData.get('assists')) - float(matchData.get('assists'))) < 4:
                return f'{hbold("🔪 K/D/A: ")}{matchData.get("kills")}/{matchData.get("deaths")}/{matchData.get("assists")}{hbold(" Kill more, die less! ❌")}\n'
        elif float(statData.get('deaths')) > float(matchData.get('deaths')):
            if (float(statData.get('assists')) - float(matchData.get('assists'))) > 4:
                return f'{hbold("🔪 K/D/A: ")}{matchData.get("kills")}/{matchData.get("deaths")}/{matchData.get("assists")}{hbold(" Kill more and help your team! ❌")}\n'
            elif (float(statData.get('assists')) - float(matchData.get('assists'))) < 4:
                return f'{hbold("🔪 K/D/A: ")}{matchData.get("kills")}/{matchData.get("deaths")}/{matchData.get("assists")}{hbold(" Try to find more kills! ❌")}\n'
    elif (float(statData.get('kills')) - float(matchData.get('kills'))) < 3:
        if float(statData.get('deaths')) < float(matchData.get('deaths')):
            if (float(statData.get('assists')) - float(matchData.get('assists'))) > 4:
                return f'{hbold("🔪 K/D/A: ")}{matchData.get("kills")}/{matchData.get("deaths")}/{matchData.get("assists")}{hbold(" Help your team and die less! ❌")}\n'
            elif (float(statData.get('assists')) - float(matchData.get('assists'))) < 4:
                return f'{hbold("🔪 K/D/A: ")}{matchData.get("kills")}/{matchData.get("deaths")}/{matchData.get("assists")}{hbold(" You have good KDA! But try to die less! ✔️")}\n'
        elif float(statData.get('deaths')) > float(matchData.get('deaths')):
            if (float(statData.get('assists')) - float(matchData.get('assists'))) > 4:
                return f'{hbold("🔪 K/D/A: ")}{matchData.get("kills")}/{matchData.get("deaths")}/{matchData.get("assists")}{hbold(" You have good KDA! But help you team more! ✔️")}\n'
            elif (float(statData.get('assists')) - float(matchData.get('assists'))) < 4:
                return f'{hbold("🔪 K/D/A: ")}{matchData.get("kills")}/{matchData.get("deaths")}/{matchData.get("assists")}{hbold(" You have the best KDA! ✔️")}\n'


def dmgCompare(statData,matchData,duration):
    # делим на 60 т.к в статистике за 10 минут берется
    dur_stats = (float(duration.get('time')) / 60) * float(statData.get('heroDmg')) 
    if (dur_stats - float(matchData.get('dmg'))) > 3000:
        return f'{hbold("🏹 Damage: ")}{matchData.get("dmg")}{hbold(" ❌ If you are support - ignore, others make damage!")}\n'
    else:
        return f'{hbold("🏹 Damage: ")}{matchData.get("dmg")}{hbold(" You made a good damage in this game! ✔️")}\n'

def tmgCompare(statData,matchData,duration):
    # делим на 60 т.к в статистике за 10 минут берется
    dur_stats = (float(duration.get('time')) / 60) * float(statData.get('towerDmg')) 
    if (dur_stats - float(matchData.get('tmg'))) > 3000:
        return f'{hbold("🗼 Tower Damage: ")}{matchData.get("tmg")}{hbold(" ❌ You need to push with your team!")}\n'
    else:
        return f'{hbold("🗼 Tower Damage: ")}{matchData.get("tmg")}{hbold(" Towers is not a problem! ✔️")}\n'

def healCompare(statData,matchData,duration):
    # делим на 60 т.к в статистике за 10 минут берется
    dur_stats = (float(duration.get('time')) / 60) * float(statData.get('heal'))
    if matchData.get('heal') == '0':
        return f'{hbold("🩺 Heal: ")}{matchData.get("heal")}{hbold(" Okay..")}\n'
    elif (dur_stats - float(matchData.get('heal'))) > 100:
        return f'{hbold("🩺 Heal: ")}{matchData.get("heal")}{hbold(" ❌ If you are carry - ignore, others heal your team!")}\n'
    else:
        return f'{hbold("🩺 Heal: ")}{matchData.get("heal")}{hbold(" Thank you doctor! ✔️")}\n'

def lasthitsCompare(statData,matchData,duration):
    # делим на 60 т.к в статистике за 10 минут берется
    dur_stats = (float(duration.get('time')) / 600) * float(statData.get('lashits')) 
    if (dur_stats - float(matchData.get('lasthits'))) > 40:
        return f'{hbold("💰 Lasthits: ")}{matchData.get("lasthits")}{hbold(" Train your lasthits! ❌")}\n'
    else:
        return f'{hbold("💰 Lasthits: ")}{matchData.get("lasthits")}{hbold(" Not a single creep lost! ✔️")}\n'

def deniesCompare(statData,matchData,duration):
    # делим на 60 т.к в статистике за 10 минут берется
    dur_stats = (float(duration.get('time')) / 600) * float(statData.get('denies')) 
    if (dur_stats - float(matchData.get('denies'))) > 40:
        return f'{hbold("🦠 Denies: ")}{matchData.get("denies")}{hbold(" ❌ Train your denie skill!")}\n'
    else:
        return f'{hbold("🦠 Denies: ")}{matchData.get("denies")}{hbold(" Denie and denie! ✔️")}\n' 

def networth(matchData):
    return f'{hbold("💸 Networth: ")}{matchData.get("networth")}\n'

def gmpExpm(matchData):
    return f'{hbold("📊 GPM/EXPM: ")}{matchData.get("gmp")}/{matchData.get("exp")}\n'

def winrateCompare(statData):
    if float(statData.get('winrate')) > 50:
        return f'{hbold("🏆 Hero winrate: ")}{statData.get("winrate")}%{hbold(" This hero have a good winrate! ✔️")}\n'
    else:
        return f'{hbold("🏆 Hero winrate: ")}{statData.get("winrate")}%{hbold(" Try to find another hero to play, winrate is too low")}\n'

def main():
    executor.start_polling(dp, skip_updates=True)

if __name__ == '__main__':
    main()


