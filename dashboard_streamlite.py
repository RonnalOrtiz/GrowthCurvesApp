# dashboard_streamlit.py
# -----------------------------------------------------------
# Streamlit version of Growth Curve Dashboard
# -----------------------------------------------------------

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Growth Curve Dashboard", layout="wide")

# -----------------------------------------------------------
# Helper: Load parameter file (uploaded or default)
# -----------------------------------------------------------
def load_parameters(uploaded_file=None):
    if uploaded_file is not None:
        file_name = uploaded_file.name.lower()
        if file_name.endswith(".xlsx") or file_name.endswith(".xls"):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        st.success("Custom parameters file loaded successfully.")
    else:
        default_path = os.path.join(os.path.dirname(__file__), "default_parameters.xlsx")
        if not os.path.exists(default_path):
            st.error("Default parameter file not found. Please upload one.")
            st.stop()
        df = pd.read_excel(default_path)
        st.info("Using default parameters file.")
    return df

# -----------------------------------------------------------
# Gompertz growth function
# -----------------------------------------------------------
def gompertz(days, b0, b1, b2):
    return b0 * np.exp(-b1 * np.exp(-b2 * days))

# -----------------------------------------------------------
# Plotting function
# -----------------------------------------------------------
def plot_growth_curve(params_df, region):
    row = params_df.loc[params_df["ID"] == region].iloc[0]
    b0, b1, b2 = row["b0"], row["b1"], row["b2"]
    x = np.linspace(0, 800, 200)
    y = gompertz(x, b0, b1, b2)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=f"Gompertz - {region}"))
    fig.update_layout(
        title=f"Growth Curve for {region}",
        xaxis_title="Days",
        yaxis_title="Predicted Weight (kg)",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------
# Main Streamlit UI
# -----------------------------------------------------------
st.title("🐄 Growth Curve Dashboard")
st.write("Visualize and compare growth curves based on Gompertz parameters.")

uploaded_file = st.sidebar.file_uploader("Upload your parameter file", type=["csv", "xlsx"])
params = load_parameters(uploaded_file)

if not {"ID", "b0", "b1", "b2"}.issubset(params.columns):
    st.error("Parameter file must contain columns: ID, b0, b1, b2.")
    st.stop()

regions = params["ID"].dropna().unique().tolist()
selected_region = st.sidebar.selectbox("Select region", regions)

if st.sidebar.button("Show Growth Curve"):
    plot_growth_curve(params, selected_region)
    st.success(f"Displayed curve for {selected_region}")

st.markdown("---")
st.caption("GrowthCurveApp — powered by Streamlit")