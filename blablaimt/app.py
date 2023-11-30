import pandas as pd
import streamlit as st
from gsheetsdb import connect

SELECT_FILTERS = ("Name",)
MULTIPLE_FILTERS = ("Genre",)
BOOL_FILTERS = ("Loved", "OneShottable", "Campaignable", "Physical")
RADIO_FILTERS = ("Masterless", "Language")
SHEET_URL = st.secrets["public_gsheets_url"] + "#gid=0"
Q_ALL_GAMES = f'SELECT Name, Genre, Loved, Format, PlayersMin, PlayersMax, OneShottable, Campaignable, Masterless, Language, Expansions FROM "{SHEET_URL}"'
Q_SOME_GAMES = f'SELECT Name, Genre, Loved, Format, PlayersMin, PlayersMax, OneShottable, Campaignable, Masterless, Language, Expansions, ManualIn, MaterialsIn, ExpansionIn FROM "{SHEET_URL}"'
st.set_page_config(page_title="blablaimt", page_icon="🚙", layout="centered")
st.title("blabla imt?")
conn = connect()


@st.cache(ttl=600)
def query(my_query):
    return conn.execute(my_query, headers=1)


# compose the filtering interface
all_proposals = pd.DataFrame(
    query(
        f'SELECT id, departure, startdatedeparture, enddatedeparture, return, startdatereturn, enddatereturn, name, surname, candrive FROM "{SHEET_URL}"'
    )
)
## get unique options for SELECT_FILTERS, MULTIPLE_FILTERS and RADIO_FILTERS columns (for other columns, I provide options myself)
cols = {}
for column in SELECT_FILTERS + MULTIPLE_FILTERS + RADIO_FILTERS:
    cols[column] = pd.concat(
        (
            pd.Series(("all")),
            all_proposals[column].drop_duplicates().dropna().sort_values(),
        ),
        ignore_index=True,
    )
## UI input widgets for all filters
filters = {}
st.sidebar.subheader("Refine your search")
for key in SELECT_FILTERS:
    filters[key] = st.sidebar.selectbox(f"Filter by {key}…", cols[key])
for key in MULTIPLE_FILTERS:
    if key == "Genre":
        filters[key] = st.sidebar.multiselect(f"Filter by {key}…", cols[key][1:])
num_players = st.sidebar.select_slider(
    "Filter by Number of Players…", options=["all", 1, 2, 3, 4, 5, 6, 7, 8]
)
for key in BOOL_FILTERS:
    if key == "Loved":
        filters[key] = st.sidebar.checkbox(
            f"Filter by {key}…", help="Personal favourites."
        )
    elif key == "OneShottable":
        filters[key] = st.sidebar.checkbox(
            f"Filter by {key}…", help="Ok to be played only once."
        )
    elif key == "Campaignable":
        filters[key] = st.sidebar.checkbox(
            f"Filter by {key}…", help="Ok to be played in multiple sessions."
        )
    elif key == "Physical":
        filters[key] = st.sidebar.checkbox(
            f"Filter by {key}…", help="If I have the physical book."
        )
    else:
        filters[key] = st.sidebar.checkbox(f"Filter by {key}…")
for key in RADIO_FILTERS:
    if key == "Masterless":
        filters[key] = st.sidebar.radio(f"Filter by {key}…", ("all", True, False))
    elif key == "Language":
        filters[key] = st.sidebar.radio(f"Filter by {key}…", cols[key])

# condition  # this is fantastic to debug query problems

# composing the query
condition = ""
filtering_on_cols = []
for key, filter in filters.items():
    if key in SELECT_FILTERS and filter != "all":
        condition = f"{condition} and {key} = '{filter}'"
        filtering_on_cols.append(key)
    elif key == "Genre" and filter:
        working_cond = ""
        for genre in filter:
            working_cond = f"{working_cond} or {key} = '{genre}'"
        condition = f"{condition} and ({working_cond[4:]})"
        if len(filter) == 1:
            filtering_on_cols.append(key)
    elif key in RADIO_FILTERS and filter != "all":
        if key == "Masterless":
            condition = f"{condition} and {key} = {filter}"
        elif key == "Language":
            condition = f"{condition} and {key} = '{filter}'"
        filtering_on_cols.append(key)
    elif key in BOOL_FILTERS and filter:
        condition = f"{condition} and {key} = {filter}"
        if key != "Physical":
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
        st.caption(f"1 game.")
    else:  # I got more than one game
        if len(results) > 1:
            results = results.drop(columns=filtering_on_cols)
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
