# -*- coding: utf-8 -*-
"""Untitled18.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/143LN4CV64qd-OQpBHVGUXAjG1WIy0IaW
"""

!pip install streamlit
!pip install scipy
import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog

st.set_page_config(page_title="Smart Transportation Route Optimization", layout="wide")

st.title("🚚 Smart Transportation Route Optimization")
st.markdown("""
This tool helps businesses minimize transportation costs from multiple warehouses to various customer locations using **Operations Research** techniques.

- Upload cost matrix, supply, and demand.
- See optimal delivery plan and total cost.
""")

# Example data
def example_data():
    cost_df = pd.DataFrame(
        [[8, 6, 10, 9], [9, 12, 13, 7], [14, 9, 16, 5]],
        columns=["C1", "C2", "C3", "C4"],
        index=["W1", "W2", "W3"]
    )
    supply = [100, 120, 80]
    demand = [60, 70, 90, 80]
    return cost_df, supply, demand

# Upload or use example
data_option = st.radio("Select Input Method:", ["Use Example Data", "Upload CSV Files"])

if data_option == "Use Example Data":
    cost_df, supply, demand = example_data()
    st.subheader("Cost Matrix")
    st.dataframe(cost_df)
else:
    st.subheader("Upload Cost Matrix CSV")
    cost_file = st.file_uploader("Upload Cost Matrix", type=["csv"])
    supply_file = st.file_uploader("Upload Supply CSV", type=["csv"])
    demand_file = st.file_uploader("Upload Demand CSV", type=["csv"])

    if cost_file and supply_file and demand_file:
        cost_df = pd.read_csv(cost_file, index_col=0)
        supply = pd.read_csv(supply_file).iloc[:, 1].tolist()
        demand = pd.read_csv(demand_file).iloc[:, 1].tolist()
        st.dataframe(cost_df)
    else:
        st.warning("Please upload all three files.")
        st.stop()

# Prepare linear programming inputs
cost_matrix = cost_df.values
num_sources, num_destinations = cost_matrix.shape

c = cost_matrix.flatten()
A_eq = []
b_eq = []

# Supply constraints
for i in range(num_sources):
    row = [0] * num_sources * num_destinations
    for j in range(num_destinations):
        row[i * num_destinations + j] = 1
    A_eq.append(row)
    b_eq.append(supply[i])

# Demand constraints
for j in range(num_destinations):
    row = [0] * num_sources * num_destinations
    for i in range(num_sources):
        row[i * num_destinations + j] = 1
    A_eq.append(row)
    b_eq.append(demand[j])

bounds = [(0, None) for _ in range(num_sources * num_destinations)]

res = linprog(c=c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

if res.success:
    st.success("✅ Optimization Successful!")
    st.subheader("📊 Optimal Allocation Table")
    result = np.array(res.x).reshape((num_sources, num_destinations))
    result_df = pd.DataFrame(result, index=cost_df.index, columns=cost_df.columns)
    st.dataframe(result_df.style.format("{:.2f}"))
    st.subheader("💰 Total Minimum Transportation Cost")
    st.metric("Cost", f"₹ {res.fun:.2f}")
else:
    st.error("Optimization failed. Please check your input data.")