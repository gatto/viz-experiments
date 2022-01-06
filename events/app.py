from datetime import datetime

import pandas as pd
import streamlit as st
from gsheetsdb import connect

SELECT_FILTERS = ("Titolo", "Regione", "Provincia", "Comune")
RANGE_FILTERS = ("Data",)
MULTIPLE_FILTERS = ("Tipologia",)
RADIO_FILTERS = ("Online",)
# RADIO_FILTERS = ("Masterless", "Language")
SHEET_URL = st.secrets["public_gsheets_url"] + "#gid=0"
Q_ALL_DB = f'SELECT * FROM "{SHEET_URL}"'
Q_SOME_DB = f'SELECT * FROM "{SHEET_URL}"'
st.set_page_config(page_title="Eventi LGBTQIA+", page_icon="🏳️‍🌈", layout="wide")
st.title("🏳️‍🌈 Directory di Eventi LGBTQIA+")
conn = connect()


@st.cache(ttl=300)
def query(my_query):
    return conn.execute(my_query, headers=1)


def filter_on_date(df: pd.DataFrame, filter_) -> pd.DataFrame:
    return df.loc[df["Data"] >= filter_[0]].loc[df["Data"] <= filter_[1]]


# compose the filtering interface
all_db = pd.DataFrame(query(f'SELECT * FROM "{SHEET_URL}"'))

## get unique options for SELECT_FILTERS, MULTIPLE_FILTERS columns (for other columns, I provide options myself)
cols = {}
for column in SELECT_FILTERS + MULTIPLE_FILTERS:
    cols[column] = pd.Series(("tutti")).append(
        all_db[column].drop_duplicates().dropna().sort_values(), ignore_index=True
    )
cols["Data"] = all_db["Data"].drop_duplicates().dropna().sort_values()

## UI input widgets for all filters
filters = {}
st.sidebar.subheader("Ricerca fra gli eventi")
for key in SELECT_FILTERS:
    filters[key] = st.sidebar.selectbox(f"Filtra per {key}…", cols[key])
for key in RANGE_FILTERS:
    if key == "Data":
        filters["Data"] = st.sidebar.slider(
            f"Filtra per {key}…",
            cols[key].min(),
            cols[key].max(),
            value=(cols[key].min(), cols[key].max()),
            format="DD/MM/YY",
        )
for key in MULTIPLE_FILTERS:
    filters[key] = st.sidebar.multiselect(f"Filtra per {key}…", cols[key][1:])
for key in RADIO_FILTERS:
    if key == "Online":
        filters[key] = st.sidebar.radio(
            f"Filtra per {key}…",
            ("tutti", "Online", "In presenza"),
        )
    else:
        filters[key] = st.sidebar.checkbox(f"Filtra per {key}…")

# st.write(type(filters["Data"][0]))  ## this returns <class 'datetime.date'>

# composing the query
DATE_COND = (filters["Data"][0] > cols["Data"].min()) or (
    filters["Data"][1] < cols["Data"].max()
)
if filters["Online"] == "Online":
    filters["Online"] = True
elif filters["Online"] == "In presenza":
    filters["Online"] = False

condition = ""
filtering_on_cols = []
for key, filter in filters.items():
    if key in SELECT_FILTERS and filter != "tutti":
        condition = f"{condition} and {key} = '{filter}'"
        filtering_on_cols.append(key)
    elif key in MULTIPLE_FILTERS and filter:
        working_cond = ""
        for cond in filter:
            working_cond = f"{working_cond} or {key} = '{cond}'"
        condition = f"{condition} and ({working_cond[4:]})"
        if len(filter) == 1:
            filtering_on_cols.append(key)
    elif key in RADIO_FILTERS and filter != "tutti":
        condition = f"{condition} and {key} = {filter}"
        filtering_on_cols.append(key)

# st.write(condition)  # this is fantastic to debug query problems

# show results, if I have filtered something
if condition or DATE_COND:
    if condition:
        results = pd.DataFrame(
            query(f"{Q_SOME_DB} WHERE {condition[5:]}")
        ).convert_dtypes()
    else:
        results = pd.DataFrame(query(Q_SOME_DB)).convert_dtypes()

    # pandas filtering on dates because library not capable
    results = filter_on_date(results, filters["Data"])

    # display results
    st.subheader("Risultati della ricerca")
    if len(results) == 1:  # I got exactly one result
        results = results.astype("str").iloc[0]
        results = results.rename(results["Titolo"])
        results = results.drop("Titolo")
        results
        st.caption(f"1 evento.")
    else:  # I got zero or more than one result
        if len(results) > 1:
            results = results.drop(columns=filtering_on_cols)
            st.dataframe(results)
        st.caption(f"{len(results)} eventi.")
else:  # I have not filtered anything
    st.subheader("Tutti gli eventi")
    results = pd.DataFrame(query(Q_ALL_DB)).convert_dtypes()
    st.dataframe(results)
    st.caption(f"{len(results)} eventi.")
