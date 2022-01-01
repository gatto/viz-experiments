import pandas as pd
import streamlit as st
from gsheetsdb import connect

SELECT_FILTERS = [
    "Name",
    "Genre",
]
BOOL_FILTERS = [
    "Loved",
    "OneShottable",
    "Campaignable",
    "Physical",
]
RADIO_FILTERS = [
    "Masterless",
]
SHEET_URL = st.secrets["public_gsheets_url"] + "#gid=0"
Q_ALL_GAMES = f'SELECT Name, Genre, Loved, Format, PlayersMin, PlayersMax, OneShottable, Campaignable, Masterless, Expansions FROM "{SHEET_URL}"'
Q_SOME_GAMES = f'SELECT Name, Genre, Loved, Format, PlayersMin, PlayersMax, OneShottable, Campaignable, Masterless, Expansions, ManualIn, MaterialsIn, ExpansionIn FROM "{SHEET_URL}"'
conn = connect()
st.set_page_config(page_title="RPGs Picker", page_icon="🐞", layout="centered")
st.title("🐞 Role Play Games Picker")


@st.cache(ttl=600)
def query(my_query):
    return conn.execute(my_query, headers=1)


all_games = pd.DataFrame(query(f'SELECT * FROM "{SHEET_URL}"'))
cols = {}
for column in SELECT_FILTERS:
    cols[column] = (
        pd.Series(("all"))
        .append(all_games[column].sort_values(), ignore_index=True)
        .drop_duplicates()
    )
filters = {}
st.sidebar.subheader("Refine your search")
for key in SELECT_FILTERS:
    filters[key] = st.sidebar.selectbox(f"Filter by {key}…", cols[key])
num_players = st.sidebar.select_slider(
    "Filter by Number of Players…", options=["all", 1, 2, 3, 4, 5, 6, 7, 8]
)
for key in BOOL_FILTERS:
    if key == "Physical":
        filters[key] = st.sidebar.checkbox(
            f"Filter by {key}…", help="If I have the physical book."
        )
    else:
        filters[key] = st.sidebar.checkbox(f"Filter by {key}…")
for key in RADIO_FILTERS:
    if key == "Masterless":
        filters[key] = st.sidebar.radio(f"Filter by {key}…", ("all", True, False))

# composing the query
condition = ""
filtering_on_cols = []
for key, filter in filters.items():
    if key in SELECT_FILTERS and filter != "all":
        condition = f"{condition} and {key} = '{filter}'"
        filtering_on_cols.append(key)
    elif key in RADIO_FILTERS and filter != "all":
        if key == "Masterless":
            condition = f"{condition} and {key} = {filter}"
        filtering_on_cols.append(key)
    elif key in BOOL_FILTERS and filter:
        condition = f"{condition} and {key} = {filter}"
        filtering_on_cols.append(key)
if num_players != "all":
    condition = (
        f"{condition} and PlayersMin <= {num_players} and PlayersMax >= {num_players}"
    )

# show results, if I have filtered something
if condition:
    results = pd.DataFrame(
        query(f"{Q_SOME_GAMES} WHERE {condition[5:]}")
    ).convert_dtypes()
    st.subheader("Results of the search")
    if len(results) == 1:  # I got exactly one game
        results = results.astype("str").iloc[0]
        results = results.rename(results[0])
        results[1:]
    else:  # I got more than one game
        # results = results.drop(columns=filtering_on_cols)
        st.dataframe(results)
        st.caption(f"{len(results)} games.")
else:  # I have not filtered anything
    st.subheader("All my library")
    only_loved = st.checkbox(f"Only Loved games…")
    if only_loved:
        results = pd.DataFrame(
            query(Q_ALL_GAMES + " WHERE Loved=TRUE")
        ).convert_dtypes()
    else:
        results = pd.DataFrame(query(Q_ALL_GAMES)).convert_dtypes()
    st.dataframe(results)
    st.caption(f"{len(results)} games.")
