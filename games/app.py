import pandas as pd
import psycopg2
import streamlit as st


# Initialize connection, Uses st.experimental_singleton to only run once
@st.experimental_singleton
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])


# Perform query, Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


@st.experimental_memo(ttl=600)
def get_columns(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.description


# Page setup
st.set_page_config(page_title="Game Library", page_icon="🎲", layout="centered")
st.title("🎲 Game Library")
conn = init_connection()

# viz start
columns = [col.name for col in get_columns("SELECT * from games;")]
all_games = pd.DataFrame(run_query("SELECT * from games;"), columns=columns)
all_games = all_games.loc[~all_games["Hide"]]
all_games

st.write(len(all_games))
