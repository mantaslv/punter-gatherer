import pandas as pd
import psycopg2
from psycopg2 import extras

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    database="punter_gatherer",
)

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Define your table structure here
table_name = "game_data"
table_columns = "Comp TEXT, HomeTeam TEXT, AwayTeam TEXT, Date TEXT, HProb INTEGER, DProb INTEGER, AProb INTEGER, XG FLOAT, AllOdds TEXT, Score TEXT, HOdds FLOAT, DOdds FLOAT, AOdds FLOAT, HScore INTEGER, AScore INTEGER, Result TEXT"

# Generate the CREATE TABLE query
create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({table_columns});"

# Execute the CREATE TABLE query
cursor.execute(create_table_query)

# Read the CSV file into a pandas DataFrame, skipping the first row
data = pd.read_csv('./ForebetDatabase.csv', skiprows=1)

# Iterate over each row in the DataFrame
for row in data.itertuples(index=False):
    # Insert the values into the PostgreSQL database
    cursor.execute(
        f"INSERT INTO {table_name} VALUES %s",
        (row,)
    )

# Commit the changes to the database
conn.commit()

# Close the cursor and database connection
cursor.close()
conn.close()
