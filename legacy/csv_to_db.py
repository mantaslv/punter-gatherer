import pandas as pd
import psycopg2

conn = psycopg2.connect(database="punter_gatherer")

cursor = conn.cursor()

table_name = "game_data"
table_columns = (
    "id SERIAL PRIMARY KEY, "
    "competition TEXT, "
    "home_team TEXT, "
    "away_team TEXT, "
    "game_date TIMESTAMP, "
    "home_prob INTEGER, "
    "draw_prob INTEGER, "
    "away_prob INTEGER, "
    "xg FLOAT, "
    "raw_odds TEXT, "
    "raw_score TEXT, "
    "home_odds FLOAT, "
    "draw_odds FLOAT, "
    "away_odds FLOAT, "
    "home_score INTEGER, "
    "away_score INTEGER, "
    "result TEXT"
)

create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({table_columns});"

cursor.execute(create_table_query)

data = pd.read_csv('./legacy/ForebetDatabase.csv')

data['Date'] = pd.to_datetime(data['Date'], format='%d/%m/%Y %H:%M')

data = data.where((pd.notnull(data)), None)

data = data.sort_values(by='Date').reset_index(drop=True)

for index, row in data.iterrows():
    cursor.execute(f"INSERT INTO {table_name} VALUES %s", (tuple([index + 1] + list(row)),))

conn.commit()

cursor.close()
conn.close()
