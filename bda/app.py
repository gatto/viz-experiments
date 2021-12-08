import streamlit as st
import pandas as pd
import numpy as np

DATA_URL = "https://raw.githubusercontent.com/gatto/viz-experiments/main/bda/data/rf_shap_values.csv"
COLUMN_NAMES = [
    "yr",
    "mnth",
    "holiday",
    "weekday",
    "workingday",
    "temp",
    "atemp",
    "hum",
    "windspeed",
    "spring",
    "summer",
    "autumn",
    "z_Zone 10",
    "z_Zone 11",
    "z_Zone 12",
    "z_Zone 13",
    "z_Zone 14",
    "z_Zone 15",
    "z_Zone 16",
    "z_Zone 17",
    "z_Zone 18",
    "z_Zone 19",
    "z_Zone 2",
    "z_Zone 20",
    "z_Zone 21",
    "z_Zone 3",
    "z_Zone 4",
    "z_Zone 5",
    "z_Zone 6",
    "z_Zone 7",
    "z_Zone 8",
    "z_Zone 9",
    "w_cloudy",
    "w_rain",
]
MY_TYPES = [
    "date",
    "date",
    "date",
    "date",
    "date",
    "atmosphere",
    "atmosphere",
    "atmosphere",
    "atmosphere",
    "season",
    "season",
    "season",
    "geo-zone",
    "geo-zone",
    "geo-zone",
    "geo-zone",
    "geo-zone",
    "geo-zone",
    "geo-zone",
    "geo-zone",
    "geo-zone",
    "geo-zone",
    "geo-zone",
    "geo-zone",
    "geo-zone",
    "geo-zone",
    "geo-zone",
    "geo-zone",
    "geo-zone",
    "geo-zone",
    "geo-zone",
    "geo-zone",
    "weather",
    "weather",
]
BASE_VAL = 400

st.title("Bike Sharing: Visualization of Instances")

with st.expander("Details on the base data…"):
    st.write("Base value of the `cnt` prediction is ", BASE_VAL)

    st.write("Conditions of the graph buckets")
    with st.echo():

        def analyze_col(col):
            if col[:2] == "z_":
                return "geo-zone"
            elif col[:2] == "w_":
                return "weather"
            if col in ("spring", "summer", "autumn"):
                return "season"
            elif col in ("yr", "mnth", "holiday", "weekday", "workingday"):
                return "date"
            elif col in ("temp", "atemp", "hum", "windspeed"):
                return "atmosphere"


def characterize_columns(df):
    results = []
    for col in df:
        results.append(analyze_col(col))
    return results


@st.cache
def load_data(nrows):
    data = pd.read_csv(DATA_URL, names=COLUMN_NAMES, nrows=nrows, index_col=0, header=0)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    # data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data


data_load_state = st.text("Loading data...")
data = load_data(10000)
data_load_state.text("Loading done! (and cached)")

if st.checkbox("Show raw data"):
    st.subheader("Raw data")
    st.write(data)

row_to_explain = st.number_input(
    "Row # to explain", min_value=0, max_value=data.shape[0]
)

buckets = {}
my_row = data.iloc[row_to_explain, :]
for value, type_ in zip(my_row, MY_TYPES):
    try:
        buckets[type_] += value
    except KeyError:
        buckets[type_] = value

st.subheader("Aggregate effect of features")
hist_values = pd.Series(buckets, name=row_to_explain)
st.bar_chart(hist_values)

st.subheader("Prediction value")
st.write(
    "Base value",
    BASE_VAL,
    "+ effect of this instance",
    round(hist_values.sum(), 2),
    "=",
    round(hist_values.sum() + BASE_VAL),
)

if st.checkbox("Show raw data of instance"):
    st.subheader("Raw data of instance", row_to_explain)
    st.write(data.iloc[row_to_explain, :])
