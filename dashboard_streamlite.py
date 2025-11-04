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
def plot_growth_curve(params_df, region, user_data=None):
    row = params_df.loc[params_df["ID"] == region].iloc[0]
    b0, b1, b2 = row["b0"], row["b1"], row["b2"]
    x = np.linspace(0, 800, 200)
    y = gompertz(x, b0, b1, b2)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=f"Gompertz - {region}"))

    # Overlay observed user data
    if user_data is not None and not user_data.empty:
        fig.add_trace(go.Scatter(
            x=user_data["Age"],
            y=user_data["Weight"],
            mode="markers",
            name="Observed Data",
            marker=dict(size=8, color="red")
        ))

    fig.update_layout(
        title=f"Growth Curve for {region}",
        xaxis_title="Days",
        yaxis_title="Predicted Weight (kg)",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------
# User data input section (manual weight entry)
# -----------------------------------------------------------
st.sidebar.header("Animal Weight Data Input")
input_mode = st.sidebar.radio("Select input mode:", ["Birth–Weaning", "Weaning–Slaughter"])

# Place form inside an expander
with st.expander("Click to enter observed weights manually"):
    st.write(f"Enter observed weights for {input_mode.lower()} period.")
    with st.form("weights_form"):
        st.write("Enter age (days) and observed weight (kg):")
        user_data = []
        for i in range(1, 6):  # up to 5 entries
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input(f"Age {i} (days)", min_value=0, max_value=800, step=10, key=f"age_{i}")
            with col2:
                weight = st.number_input(f"Weight {i} (kg)", min_value=0.0, step=1.0, key=f"wt_{i}")
            if age > 0 and weight > 0:
                user_data.append((age, weight))
        submitted = st.form_submit_button("Add data")

df_obs = pd.DataFrame(user_data, columns=["Age", "Weight"]) if user_data else pd.DataFrame()


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

from scipy.optimize import curve_fit

# Optional: fit the model to user-entered data
if submitted and not df_obs.empty:
    xdata = df_obs["Age"].values
    ydata = df_obs["Weight"].values
    try:
        popt, _ = curve_fit(gompertz, xdata, ydata, p0=[400, 3, 0.01])
        st.sidebar.success(f"Fitted parameters: b0={popt[0]:.2f}, b1={popt[1]:.2f}, b2={popt[2]:.4f}")
        # Update current region’s parameters with fitted ones
        params.loc[params["ID"] == selected_region, ["b0", "b1", "b2"]] = popt
    except Exception as e:
        st.sidebar.error(f"Model fitting failed: {e}")


if st.sidebar.button("Show Growth Curve"):
    plot_growth_curve(params, selected_region, df_obs)
    st.success(f"Displayed curve for {selected_region}")

st.markdown("---")
st.caption("GrowthCurveApp — powered by Streamlit")