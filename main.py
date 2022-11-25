from urllib import response
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import json


URL_WINRATE = "https://www.dotabuff.com/heroes/played"
URL_KDA = "https://www.dotabuff.com/heroes/impact"
URL_FARM = "https://www.dotabuff.com/heroes/farm"
URL_DAMAGE = "https://www.dotabuff.com/heroes/damage"
URL_MATCH = "https://www.dotabuff.com/matches/{match_id}"
URL_PLAYER = "https://www.dotabuff.com/players/{player_id}"


def to_seconds(timestr):
    seconds = 0
    for part in timestr.split(':'):
        seconds = seconds*60 + int(part, 10)
    return seconds

# собираем винрейт каждого героя
def collect_winrate():
  r = requests.get(
    url=URL_WINRATE,
    headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
  )
  parse = bs(r.text, "html.parser")
  data = []

  trs = parse.find_all('tr')
  for tr in trs:
    tds = tr.find_all('td')
    for td in tds:
      data.append({
        'name': tds[1].text,
        'winrate': tds[4].text.replace('%','')
      })
  data_sorted = []
  for i in data:
    if i not in data_sorted:
      data_sorted.append(i)
  with open('winrate.json', 'w') as file:
    json.dump(data_sorted, file, indent=4, ensure_ascii=False)

# собираем кда каждого героя
def collect_kda():
  r = requests.get(
    url=URL_KDA,
    headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
  )
  parse = bs(r.text, "html.parser")
  data = []
  trs = parse.find_all('tr')
  for tr in trs:
    tds = tr.find_all('td')
    for td in tds:
      data.append({
        'name': tds[1].text,
        'kills': tds[3].text,
        'deaths': tds[4].text,
        'assists': tds[5].text
      })
  data_sorted = []
  for i in data:
    if i not in data_sorted:
      data_sorted.append(i)
  with open('kda.json', 'w') as file:
    json.dump(data_sorted, file, indent=4, ensure_ascii=False)


# собираем фарм каждого героя
def collect_farm():
  r = requests.get(
    url=URL_FARM,
    headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
  )
  parse = bs(r.text, "html.parser")
  data = []
  trs = parse.find_all('tr')
  for tr in trs:
    tds = tr.find_all('td')
    for td in tds:
      data.append({
        'name': tds[1].text,
        'lashits': tds[2].text,
        'denies': tds[3].text
      })
  data_sorted = []
  for i in data:
    if i not in data_sorted:
      data_sorted.append(i)
  with open('farming.json', 'w') as file:
    json.dump(data_sorted, file, indent=4, ensure_ascii=False)


# собираем урон каждого героя
def collect_damage():
  r = requests.get(
    url=URL_DAMAGE,
    headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
  )
  parse = bs(r.text, "html.parser")
  data = []
  trs = parse.find_all('tr')
  for tr in trs:
    tds = tr.find_all('td')
    for td in tds:
      data.append({
        'name': tds[1].text,
        'hero_damage': tds[2].text.replace(',',''),
        'tower_damage': tds[3].text.replace(',',''),
        'heal': tds[4].text.replace(',','')
      })
  data_sorted = []
  for i in data:
    if i not in data_sorted:
      data_sorted.append(i)
  with open('damage.json', 'w') as file:
    json.dump(data_sorted, file, indent=4, ensure_ascii=False)

def collect_player_matches(player_id):
  r = requests.get(
    url=f'https://www.dotabuff.com/players/{player_id}',
    headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
  )
  parse = bs(r.text, "html.parser")
  data = []
  item_text = ''
  temp_url = ''
  temp_text = ''

  tables = parse.findAll('div', class_="performances-overview")
  for table in tables:
    rRows = table.findAll('div', class_="r-row")
    for rRow in rRows:
      rFluids = rRow.findAll('div', class_="r-fluid")
      for  rFluid in rFluids:
        rBodies = rFluid.findAll('div', class_="r-body")
        for rBodie in rBodies:
          links = rBodie.find_all('a', href=True)
          for a in links:
            item_url = a.get("href")
            item_text = a.text.strip()
            if (item_text != '') and (item_text != 'Lost Match' and item_text != 'Won Match'):
              temp_text = item_text
              temp_url = item_url
            elif (item_text != temp_text) and (item_url == temp_url):
              data.append({
                'link': item_url.replace('/matches/', ''),
                'hero': temp_text,
                'result': item_text
              })
              item_text = ''
    with open('player_stats.json', 'w') as file:
      json.dump(data, file, indent=4, ensure_ascii=False)

def get_stats():
  collect_damage()
  collect_farm()
  collect_kda()
  collect_winrate()

  with open('damage.json') as damageFile:
    dmgData = json.load(damageFile)
  with open('farming.json') as farmingFile:
    gpmData = json.load(farmingFile)
  with open('kda.json') as killsFile:
    kdaData = json.load(killsFile)
  with open('winrate.json') as winrateFile:
    winData = json.load(winrateFile)

  merge = []

  for i in range(len(dmgData)):
    for j in range(len(gpmData)):
      for k in range(len(kdaData)):
        for l in range(len(winData)):
          if dmgData[i]['name'] == gpmData[j]['name'] == kdaData[k]['name'] == winData[l]['name']:
            merge.append({
              'name': dmgData[i]['name'],
              'heroDmg': dmgData[i]['hero_damage'],
              'towerDmg': dmgData[i]['tower_damage'],
              'heal': dmgData[i]['heal'],
              'lashits': gpmData[j]['lashits'],
              'denies': gpmData[j]['denies'],
              'kills': kdaData[k]['kills'],
              'deaths': kdaData[k]['deaths'],
              'assists': kdaData[k]['assists'],
              'winrate': winData[l]['winrate']
            })
  with open('merged_data.json', 'w') as file:
    json.dump(merge, file, indent=4, ensure_ascii=False)  

def collect_match(match_id):
  r = requests.get(
    url=f'https://www.dotabuff.com/matches/{match_id}',
    headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
  )
  parse = bs(r.text, "html.parser")
  data = []

  pre_data = []
  duration = to_seconds(parse.find('span', class_='duration').text)
  
  tables = parse.find_all("table",  {"class": ["match-team-table"]})
  for table in tables:
    trs = table.find_all("tr",  {"class": ["faction-dire", "faction-radiant"]})
    for tr in trs:
      hero_images = tr.find_all("img",{"class": ["image-hero"]}, src = True, title = True)
      # print(hero_image)
      texts = tr.find_all('td', {"class": ["r-group-1", "r-group-2", "r-group-3"]})
      for hero_image in hero_images:
        # print(hero_image['src'])
        pre_data.append(hero_image['src'])
        # print(hero_image['title'])
        pre_data.append(hero_image['title'])
        for hero_text in texts:
          if (hero_text.text != '') and (hero_text.text != '-') and ('k' in hero_text.text):
            number = hero_text.text.replace('k','').replace('.','')
            number = number+'00'
            pre_data.append(number)
            # print(number)
          elif (hero_text.text == '-'):
            # print('0')
            pre_data.append('0')
          elif (hero_text.text != ''):
            # print(hero_text.text)
            pre_data.append(hero_text.text)
        # print(pre_data)
        data.append({
          'imgSrc': pre_data[0],
          'hero': pre_data[1],
          'kills': pre_data[2],
          'deaths': pre_data[3],
          'assists': pre_data[4],
          'networth': pre_data[5],
          'lasthits': pre_data[6],
          'denies': pre_data[7],
          'gmp': pre_data[8],
          'exp': pre_data[9],
          'dmg': pre_data[10],
          'heal': pre_data[11],
          'tmg': pre_data[12],
        })
      pre_data = []
  data.append({
    'time': duration
  })
  with open('match_stats.json', 'w') as file:
    json.dump(data, file, indent=4, ensure_ascii=False)
  
  
def check_playerID(player_id):
  r = requests.get(
    url=f'https://www.dotabuff.com/players/{player_id}',
    headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
  )
  if not(r.status_code == 404):
    return True
  else:
    return False

def check_matchID(match_id):
  r = requests.get(
    url=f'https://www.dotabuff.com/matches/{match_id}',
    headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
  )
  if not(r.status_code == 404):
    return True
  else:
    return False




def main():
  get_stats()
  # collect_player_matches()
  # collect_match()
  # check_playerID()
  # check_matchID()

if __name__ == '__main__':
  main()

# <a class="link-type-hero" href="/heroes/pudge">Pudge</a> - пример героя в разметке
# https://www.dotabuff.com/matches/{match_id} - пример ссылки для матча
# https://www.dotabuff.com/players/{player_id} - пример ссылки для игрока
