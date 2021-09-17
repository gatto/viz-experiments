import streamlit as st
import numpy as np
import pandas as pd

"""
# Car sale

## Here are the attributes of my car.

| Hack | Maker | Model | Year | Km | Color |
|---|---|
| | Honda | Civic | 2009 | 270°000 | black |


## An image of the car

![](https://s.sbito.it/img/86/866cdbc3-555c-4fc5-addd-f2f1f1840ba3/gallery-mobile-1x)

## Initial request

According by [Quattroruote](https://sure) the car's fair price is **700 Euro**.
"""

with st.expander('Quattroruote said…'):
    st.write("«According to calculations on year and km and some secret sauce we concluded the car's fair price is 700 EUR»")

"""
## The negotiation log
"""

# hack to not display index
st.markdown("""
<style>
table td:nth-child(1) {
    display: none
}
table th:nth-child(1) {
    display: none
}
</style>
""", unsafe_allow_html=True)

# choosing the dates, same for every scenario
dates = pd.Series(pd.to_datetime(["2021/8/20", "2021/8/24", "2021/8/25", "2021/8/26"]))
dates2 = pd.Series(pd.to_datetime(["2021/8/20", "2021/8/24", "2021/8/25", "2021/8/26", "2021/8/26"]))


# inputting the data
scenario1 = pd.DataFrame({"date": dates, "Emily": ["€ 700", "", "€ 660", ""], "Eric": ["", "€ 500", "", "✅"]})
scenario2 = pd.DataFrame({"date": dates2, "Emily": ["€ 700", "", "€ 700", "", "❌"], "Eric": ["", "€ 300", "", "€ 350", ""]})
scenario3 = pd.DataFrame({"date": dates, "Emily": ["", "€ 750", "", "✅"], "Eric": ["€ 680", "", "€ 680", ""]})
scenarios = [scenario1, scenario2, scenario3]

# styling the dates
for i, _ in enumerate(scenarios):
    scenarios[i] = scenarios[i].style.format({"date": lambda t: t.strftime("%d-%m-%Y"),})

# display the goods
st.sidebar.write("This is a representation of a car sale. Emily wants to sell, Eric wants to buy. You can choose one of three scenarios.")
choice = st.sidebar.radio("Please select a scenario", ('one', 'two', 'three'))
if choice == 'one':
    st.table(scenarios[0])
elif choice=="two":
    st.table(scenarios[1])
elif choice=="three":
    st.table(scenarios[2])

st.caption("You can look at the Python code in the github repository: `https://github.com/gatto/viz-experiments/` :heart:")