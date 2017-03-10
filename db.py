import sqlite3
from functools import partial

sql = '''
CREATE TABLE games (
  id text NOT NULL PRIMARY KEY,
  fragment text NOT NULL,
  away_abbrv text NOT NULL,
  home_abbrv text NOT NULL,
  season int NOT NULL,
  year int NOT NULL,
  month int NOT NULL,
  day int NOT NULL,
  preview int,
  away_score int,
  home_score int,
  vegas_line int,
  over_under int
);

CREATE TABLE players (
  id text NOT NULL PRIMARY KEY,
  game_id text NOT NULL REFERENCES games(id),
  first text NOT NULL,
  last text NOT NULL,
  position text NOT NULL,
  dob int NOT NULL
);

CREATE TABLE events (
  id integer PRIMARY KEY AUTOINCREMENT,
  game_id int NOT NULL REFERENCES games(id),
  detail text NOT NULL,
  away_score int,
  home_score int,
  inning int,
  side int,
  outs int,
  num_pitches int,
  batter_player_id text NOT NULL REFERENCES players(id),
  pitcher_player_id text NOT NULL REFERENCES players(id),

  runner_1 int,
  runner_2 int,
  runner_3 int,

  po_1 int,
  po_2 int,
  po_3 int,

  sb_attempt_1 int,
  sb_attempt_2 int,
  sb_attempt_3 int,

  sb_success_1 int,
  sb_success_2 int,
  sb_success_3 int,

  strikeout_swinging int,

  ab_type int NOT NULL,
  num_bases_hit int,
  contact_to_position int,
  walk int,
  hr int,
  contact_type int,
  wild_pitch int
);
'''

def with_retries(f, retries=30):
    while True:
        try:
            return f()
            break
        except sqlite3.OperationalError as e:
            if 'database is locked' in e.args[0] and retries > 0:
                print(e.args[0], 'retrying soon... (%s left)' % (retries,))
                time.sleep(2 * random())
                retries -= 1
            else:
                raise

def insert_row(table, d):
    columns = ', '.join(d.keys())
    placeholders = ', '.join(['?' for i in range(len(d.keys()))])
    cur = conn.cursor()
    with_retries(partial(
        cur.execute,
        'INSERT INTO {table} ({columns})'
        'VALUES ({placeholders})'.format(**locals()),
        list(d.values())))
    return cur

def drop_table(table):
    cur = conn.cursor()

    q = 'DROP TABLE {table}'.format(**locals())

    with_retries(partial(cur.execute, q))

def get_rows(table, **kwargs):
    cur = conn.cursor()

    q = 'SELECT * FROM {table}'.format(**locals())
    if len(kwargs) > 0:
        placeholders = ' AND '.join([k + ' = ?' for k in kwargs.keys()])
        q = '{q} WHERE {placeholders}'.format(**locals())

    with_retries(partial(cur.execute, q, list(kwargs.values())))
    return cur

def exists(table, **kwargs):
    return len(get_rows(table, **kwargs)) > 0

def commit_with_retries():
    with_retries(partial(conn.commit))

def init_db():
    cur = conn.cursor()
    cur.executescript(sql)
    conn.commit()
