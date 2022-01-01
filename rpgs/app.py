import pandas as pd
import streamlit as st
from gsheetsdb import connect

conn = connect()


@st.cache(ttl=6)  # put it back to 6
def run_query(query):
    return conn.execute(query, headers=1)


st.set_page_config(page_title="RPGs Picker", page_icon="🐞", layout="centered")
st.title("🐞 Role Play Games Picker")

sheet_url = st.secrets["public_gsheets_url"] + "#gid=0"
all_games = pd.DataFrame(run_query(f'SELECT * FROM "{sheet_url}"'))
cols = {}
for column in all_games:
    cols[column] = (
        pd.Series(("all"))
        .append(all_games[column], ignore_index=True)
        .drop_duplicates()
    )
filters = {}
select_filters = [
    "Name",
    "Genre",
    "Players_Min",
    "Players_Max",
]
bool_filters = [
    "Format",
    "Loved",
    "One_Shottable",
    "Campaignable",
    "Masterless",
]
for key in select_filters:
    filters[key] = st.sidebar.selectbox(f"Filter by {key}…", cols[key])
for key in bool_filters:
    filters[key] = st.sidebar.radio(f"Filter by {key}…", ("all", "True", "False"))

# composing the query
condition = ""
for key, filter in filters.items():
    if filter != "all":
        condition = f"{condition} and {key} = '{filter}'"
if len(condition) > 5:
    st.dataframe(run_query(f'SELECT * FROM "{sheet_url}" WHERE {condition[5:]}'))

with st.expander("See all games…"):
    only_loved = st.checkbox(f"Only *loved* games…")
    if only_loved:
        st.dataframe(run_query(f'SELECT * FROM "{sheet_url}" WHERE Loved=TRUE'))
    else:
        st.dataframe(run_query(f'SELECT * FROM "{sheet_url}"'))
