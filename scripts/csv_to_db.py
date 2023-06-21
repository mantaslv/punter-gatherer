import pandas as pd
import psycopg2

conn = psycopg2.connect(database="punter_gatherer")

cursor = conn.cursor()

table_name = "game_data"
table_columns = (
    "ID SERIAL PRIMARY KEY, "
    "Comp TEXT, "
    "HomeTeam TEXT, "
    "AwayTeam TEXT, "
    "Date TIMESTAMP, "
    "HProb INTEGER, "
    "DProb INTEGER, "
    "AProb INTEGER, "
    "XG FLOAT, "
    "AllOdds TEXT, "
    "Score TEXT, "
    "HOdds FLOAT, "
    "DOdds FLOAT, "
    "AOdds FLOAT, "
    "HScore INTEGER, "
    "AScore INTEGER, "
    "Result TEXT"
)

create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({table_columns});"

cursor.execute(create_table_query)

data = pd.read_csv('./ForebetDatabase.csv')

data['Date'] = pd.to_datetime(data['Date'], format='%d/%m/%Y %H:%M')

data = data.sort_values(by='Date').reset_index(drop=True)

for index, row in data.iterrows():
    cursor.execute(f"INSERT INTO {table_name} VALUES %s", (tuple([index + 1] + list(row)),))

conn.commit()

cursor.close()
conn.close()
