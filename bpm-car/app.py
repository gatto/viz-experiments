import streamlit as st
import numpy as np
import pandas as pd

"""
# Car sale
This is a representation of a car sale. Emily wants to sell, Eric wants to buy.
You can choose one of three scenarios. (xxx or enter the data yourself)

`/streamlit_app.py` to customize this app to your heart's desire :heart:
If you have any questions, checkout our [documentation](https://docs.streamlit.io) and [community
forums](https://discuss.streamlit.io).
"""
scenario1 = pd.DataFrame({"date": [1, 2, 3, 4], "Emily": [10, 20, 30, 40], "Eric": [0, 20]})

st.write(my_df)

st.table(data.iloc[0:10])

chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
st.line_chart(chart_data)

map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4], columns=["lat", "lon"]
)

# st.map(map_data)

from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st

with st.echo(code_location="below"):
    total_points = st.slider("Number of points in spiral", 1, 5000, 2000)
    num_turns = st.slider("Number of turns in spiral", 1, 100, 9)

    Point = namedtuple("Point", "x y")
    data = []

    points_per_turn = total_points / num_turns

    for curr_point_num in range(total_points):
        curr_turn, i = divmod(curr_point_num, points_per_turn)
        angle = (curr_turn + 1) * 2 * math.pi * i / points_per_turn
        radius = curr_point_num / total_points
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        data.append(Point(x, y))

    st.altair_chart(
        alt.Chart(pd.DataFrame(data), height=500, width=500)
        .mark_circle(color="#0068c9", opacity=0.5)
        .encode(x="x:Q", y="y:Q")
    )
