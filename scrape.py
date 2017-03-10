import db
import parse_detail
import re
import requests
from bs4 import BeautifulSoup
from common.domain import *
from datetime import datetime
from leagues import DomainContext, LeagueContext

def _team_abbrv_from_href(href):
    team_match = re.match('/teams/([^/]*)/', href)
    if team_match:
        return team_match.groups()[0]

def game_from_bs_row(row_bs, season):
    game_date_str = row_bs.parent.find('h3').text
    game_date = datetime.strptime(game_date_str, '%A, %B %d, %Y')
    links = row_bs.find_all('a')
    fragment = [l['href'] for l in links if l.text == 'Boxscore'][0]
    game_id = fragment
    team_abbrvs = [_team_abbrv_from_href(link['href']) for link in links if link['href'] != fragment]
    team_abbrvs = list(filter(None, team_abbrvs))
    assert(len(team_abbrvs) == 2)
    return {
        'id': game_id,
        'fragment': fragment,
        'away_abbrv': team_abbrvs[0],
        'home_abbrv': team_abbrvs[1],
        'season': season,
        'year': game_date.year,
        'month': game_date.month,
        'day': game_date.day,
    }

def scrape_schedule():
    for season in DomainContext.current().scraping.SEASONS_TO_SCRAPE:
        url = 'http://www.baseball-reference.com/leagues/MLB/%d-schedule.shtml' % season
        resp = requests.get(url)
        resp.raise_for_status()
        bs = BeautifulSoup(resp.text, 'html.parser')
        sched_rows = bs.find_all('p', {'class': 'game'})
        for row in sched_rows:
            game = game_from_bs_row(row, season)
            db.insert_row('games', game)

def _uncomment(text):
    return text.replace('<!--', '').replace('-->', '')

def _is_event(row):
    if row.attrs:
        return 'event_' in row.attrs.get('id', '')

def _pitches_pbp_to_num_pitches(pitches_pbp):
    pc = pitches_pbp.split(',')[0]
    return 0 if pc == '' else int(pc)

def _normalize_name(name):
    return ' '.join(name.split('\xa0'))

def event_from_row(tr):
    attr_values = {}
    for attr in ['inning', 'outs', 'runners_on_bases_pbp', 'score_batting_team', 'pitches_pbp', 'batter', 'pitcher', 'play_desc']:
        attr_values[attr] = tr.find('', {'data-stat': attr}).text

    side = AWAY if attr_values['inning'][:1] == 't' else HOME
    batting_team_score, def_team_score = attr_values['score_batting_team'].split('-')
    if side == AWAY:
        away_score, home_score = batting_team_score, def_team_score
    else:
        away_score, home_score = def_team_score, batting_team_score
    #import pdb; pdb.set_trace()
    result = {
        'side': side,
        'inning': int(attr_values['inning'][1:]),
        'outs': int(attr_values['outs']),
        'runner_1': '1' in attr_values['runners_on_bases_pbp'],
        'runner_2': '2' in attr_values['runners_on_bases_pbp'],
        'runner_3': '3' in attr_values['runners_on_bases_pbp'],
        'away_score': int(away_score),
        'home_score': int(home_score),
        'num_pitches': _pitches_pbp_to_num_pitches(attr_values['pitches_pbp']),
        'batter_player_name': _normalize_name(attr_values['batter']),
        'pitcher_player_name': _normalize_name(attr_values['pitcher']),
        'detail': attr_values['play_desc'],
    }

    detail_map = parse_detail.parse(attr_values['play_desc'])
    result.update(detail_map)
    return result

def replace_names_with_player_ids(event, all_links):
    for k, v in event.items():
        if k.endswith('_player_name'):
            player_id_key = k.replace('_player_name', '_player_id')
            event[player_id_key] = all_links[v]
            del event[k]
    return event

def all_links_from_bs(bs):
    all_placeholders = bs.find_all('div', class_='placeholder')
    all_placeholder_content = [BeautifulSoup(_uncomment(str(ph_bs.parent)), 'html.parser') for ph_bs in all_placeholders]

    all_links = {}
    for content in all_placeholder_content:
        for a in content.find_all('a'):
            if 'href' in a.attrs:
                all_links[a.text] = a.attrs['href']

    return all_links

def scrape_game(game):
    print(game['id'])
    url = 'http://www.baseball-reference.com%s' % game['fragment']
    resp = requests.get(url)
    resp.raise_for_status()
    bs = BeautifulSoup(resp.text, 'html.parser')

    all_links = all_links_from_bs(bs)
    pbp_bs = BeautifulSoup(_uncomment(str(bs.find(id='all_play_by_play'))), 'html.parser')
    all_trs = pbp_bs.find_all('tr')
    all_event_trs = [tr for tr in all_trs if _is_event(tr)]

    for tr in all_event_trs:
        event = event_from_row(tr)
        event['game_id'] = game['id']
        event = replace_names_with_player_ids(event, all_links)
        db.insert_row('events', event)
    db.commit_with_retries()

if __name__ == '__main__':
    with LeagueContext('mlb'):
        db.init_db()
        scrape_schedule()
        all_games = db.get_rows('games')
        for game in all_games:
            scrape_game(game)
        db.commit_with_retries()
