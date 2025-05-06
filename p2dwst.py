import os

config_dir = os.path.join(os.getcwd(), ".streamlit")
os.makedirs(config_dir, exist_ok=True)

config_path = os.path.join(config_dir, "config.toml")

config_contents = """
[theme]
primaryColor = "#001e44"
backgroundColor = "#e4e9f2"
secondaryBackgroundColor = "#ffffff"
textColor = "#001e44"
font = "sans serif"
"""

with open(config_path, "w") as f:
    f.write(config_contents)

import os
import urllib.request
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime
import plotly.graph_objects as go
import numpy as np

# Download database
db_url = "https://github.com/dr-adsalas/datawran/raw/main/KOXR_2000-2024_data.db"
db_path = "KOXR_2000-2024_data.db"
if not os.path.exists(db_path):
    urllib.request.urlretrieve(db_url, db_path)

@st.cache_data
def load_data():
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM weather", conn)
    conn.close()
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()
variables = ['air_temp', 'relative_humidity', 'wind_speed', 'wind_direction',
             'altimeter', 'sea_level_pressure', 'Atmospheric Pressure']
default_start = pd.to_datetime(df['Date'].min())
default_end = pd.to_datetime(df['Date'].max())

#Initialize session states for Tabs 1–6
date_state_keys = {
    "start1": default_start, "end1": default_end,
    "start2": default_start, "end2": default_end,
    "start3": default_start, "end3": default_end,
    "start4": default_start, "end4": default_end,
    "start5": default_start, "end5": default_end,
    "start6": default_start, "end6": default_end
}

for key, default in date_state_keys.items():
    if key not in st.session_state:
        st.session_state[key] = default

#App Layout
st.title("KOXR (Oxnard Airport) Weather Dashboard (2000–2024)")
st.markdown("#### Created by Anthony Delgadillo Salas de la Tierra using National Weather Service historical observations")
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📈 Overview", "🌡️ Extreme Temps", "🔥 Fire Conditions", 
    "🚩 Red Flag Warnings", "💨 Santa Ana Winds", "📊 Multivariate Explorer", "📘 Index"
])

# -------- Tab 1: Overview --------
with tab1:
    st.header("📈 Overview")
    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("Start Date", st.session_state["start1"], key="input_start1",
                              min_value=default_start, max_value=default_end)
    with col2:
        end = st.date_input("End Date", st.session_state["end1"], key="input_end1",
                            min_value=default_start, max_value=default_end)
    if st.button("🔄 Reset Overview"):
        st.session_state["start1"] = default_start
        st.session_state["end1"] = default_end
        start, end = default_start, default_end
    st.session_state["start1"] = start
    st.session_state["end1"] = end

    var = st.selectbox("Choose Variable", variables, key="var1")
    agg = st.radio("Aggregation", ["Daily", "Monthly", "Yearly"], key="agg1")

    df_plot = df[(df["Date"] >= pd.to_datetime(start)) & (df["Date"] <= pd.to_datetime(end))].copy()
    if agg == "Monthly":
        df_plot = df_plot.resample("ME", on="Date").mean(numeric_only=True)
    elif agg == "Yearly":
        df_plot = df_plot.resample("YE", on="Date").mean(numeric_only=True)

    fig = px.line(df_plot, x=df_plot.index, y=var, title=f"{agg} Trend: {var.replace('_', ' ').title()}")
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# ----- Tab 2: Extreme Temps -----
with tab2:
    st.header("🌡️ Extreme Temperature Days")
    col1, col2 = st.columns(2)
    with col1:
        start2 = st.date_input("Start Date", value=st.session_state["start2"], key="input_start2",
                               min_value=default_start, max_value=default_end)
    with col2:
        end2 = st.date_input("End Date", value=st.session_state["end2"], key="input_end2",
                             min_value=default_start, max_value=default_end)

    if st.button("🔄 Reset Extreme Dates"):
        st.session_state["start2"] = default_start
        st.session_state["end2"] = default_end
        start2, end2 = default_start, default_end

    st.session_state["start2"] = start2
    st.session_state["end2"] = end2

    df2 = df[(df['Date'] >= pd.to_datetime(start2)) & (df['Date'] <= pd.to_datetime(end2))].copy()
    temp_extreme = st.slider("Temperature Threshold (°F)", 80, 110, 95)

    df_extreme = df2[df2['air_temp'] > temp_extreme].copy()
    df_extreme['Date_only'] = df_extreme['Date'].dt.normalize()
    unique_days = df_extreme['Date_only'].nunique()
    st.metric("Days Above Threshold", unique_days)

    if not df_extreme.empty:
        fig_ext = px.scatter(
            df_extreme,
            x='Date',
            y='air_temp',
            title="Extreme Temperature Events",
            hover_data={'air_temp': True}
        )
        fig_ext.update_traces(marker=dict(size=8))
        fig_ext.update_layout(
            template="plotly_dark",
            hovermode='x unified',
            xaxis_tickformat="%Y-%m-%d",
            xaxis_title="Date",
            yaxis_title="Air Temperature (°F)"
        )
        st.plotly_chart(fig_ext, use_container_width=True)

        st.subheader(f"📋 Daily Max Temps > {temp_extreme}°F")
        df_hot_days = (
            df_extreme.groupby('Date_only')
            .agg(Max_Temperature_F=('air_temp', 'max'))
            .reset_index()
            .rename(columns={'Date_only': 'Calendar Day'})
        )
        df_hot_days['Calendar Day'] = pd.to_datetime(df_hot_days['Calendar Day']).dt.strftime("%Y-%m-%d")
        st.dataframe(df_hot_days)

        st.download_button(
            label=f"📥 Download Max Temps > {temp_extreme}°F",
            data=df_hot_days.to_csv(index=False),
            file_name=f"extreme_days_over_{temp_extreme}F.csv"
        )
    else:
        st.info("No days found above the selected threshold in this date range.")

# -------- Tab 3: Fire Weather Conditions --------
with tab3:
    st.header("🔥 Fire Weather Conditions")
    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("Start Date", st.session_state["start3"], min_value=default_start, max_value=default_end, key="input_start3")
    with col2:
        end = st.date_input("End Date", st.session_state["end3"], min_value=default_start, max_value=default_end, key="input_end3")
    if st.button("🔄 Reset Fire"):
        st.session_state["start3"] = default_start
        st.session_state["end3"] = default_end
        start, end = default_start, default_end
    st.session_state["start3"] = start
    st.session_state["end3"] = end

    df_fire = df[(df['Date'] >= pd.to_datetime(start)) & (df['Date'] <= pd.to_datetime(end))].copy()
    temp = st.slider("Temperature ≥ (°F)", 70, 110, 85)
    rh = st.slider("Relative Humidity ≤ (%)", 5, 50, 15)
    wind = st.slider("Wind Speed ≥ (mph)", 5, 40, 20)

    mask = (df_fire['air_temp'] >= temp) & (df_fire['relative_humidity'] <= rh) & (df_fire['wind_speed'] >= wind)
    df_fire = df_fire[mask]
    st.metric("Fire-Risk Hours", len(df_fire))

    if not df_fire.empty:
        df_fire["Date_str"] = df_fire["Date"].dt.strftime("%Y-%m-%d")  # Create string version for hover

        fig = px.scatter(
            df_fire,
            x="Date",
            y="air_temp",
            color="relative_humidity",
            size="wind_speed",
            title="Fire Weather Conditions",
            template="plotly_dark",
            hover_data={
                "Date_str": True,
                "Date": False,  # Hide raw datetime to avoid duplicates
                "air_temp": True,
                "relative_humidity": True,
                "wind_speed": True
            }
        )
        fig.update_traces(marker=dict(size=6))  # smaller circles
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Air Temperature (°F)",
            hovermode="x unified",
            coloraxis_colorbar_title="RH (%)"
        )
        st.plotly_chart(fig, use_container_width=True)

# -------- Tab 4: Red Flag Warnings --------
with tab4:
    st.header("🚩 Red Flag Warning Conditions")
    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("Start Date", st.session_state["start4"], min_value=default_start, max_value=default_end, key="input_start4")
    with col2:
        end = st.date_input("End Date", st.session_state["end4"], min_value=default_start, max_value=default_end, key="input_end4")
    if st.button("🔄 Reset Red Flag"):
        st.session_state["start4"] = default_start
        st.session_state["end4"] = default_end
        start, end = default_start, default_end
    st.session_state["start4"] = start
    st.session_state["end4"] = end

    df_flag = df[(df['Date'] >= pd.to_datetime(start)) & (df['Date'] <= pd.to_datetime(end))].copy()
    mask = (df_flag['relative_humidity'] <= 15) & (df_flag['wind_speed'] >= 25)
    df_flag = df_flag[mask]
    st.metric("Red Flag Hours", len(df_flag))

    if not df_flag.empty:
        df_flag['Date_str'] = df_flag['Date'].dt.strftime('%Y-%m-%d')
        fig_flag = px.scatter(
            df_flag,
            x='Date',
            y='air_temp',
            color='wind_speed',
            title="Red Flag Conditions",
            hover_data={'Date_str': True, 'air_temp': True},
            template="plotly_dark"
        )
        fig_flag.update_traces(marker=dict(size=6))
        fig_flag.update_layout(
            xaxis_title="Date",
            yaxis_title="Air Temperature (°F)",
            coloraxis_colorbar_title="Wind Speed (mph)",
            hovermode='x unified',
            xaxis_tickformat="%Y-%m-%d"
        )
        st.plotly_chart(fig_flag, use_container_width=True)

# -------- Tab 5: Santa Ana Winds --------
with tab5:
    st.header("💨 Santa Ana Wind Conditions")
    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("Start Date", st.session_state["start5"], min_value=default_start, max_value=default_end, key="input_start5")
    with col2:
        end = st.date_input("End Date", st.session_state["end5"], min_value=default_start, max_value=default_end, key="input_end5")
    if st.button("🔄 Reset Santa Ana"):
        st.session_state["start5"] = default_start
        st.session_state["end5"] = default_end
        start, end = default_start, default_end
    st.session_state["start5"] = start
    st.session_state["end5"] = end

    df_santa = df[(df['Date'] >= pd.to_datetime(start)) & (df['Date'] <= pd.to_datetime(end))].copy()
    mask = (df_santa['wind_direction'].between(30, 120)) & (df_santa['wind_speed'] >= 20)
    df_santa = df_santa[mask]
    st.metric("Santa Ana Hours", len(df_santa))

    if not df_santa.empty:
        # Existing scatter plot
        fig_santa = px.scatter(
            df_santa,
            x='Date',
            y='wind_speed',
            color='relative_humidity',
            title="Santa Ana Wind Conditions",
            template="plotly_dark",
            hover_data={"Date": True}
        )
        fig_santa.update_traces(marker=dict(size=7))
        fig_santa.update_layout(
            xaxis_title="Date",
            yaxis_title="Wind Speed (mph)",
            coloraxis_colorbar_title="RH (%)"
        )
        st.plotly_chart(fig_santa, use_container_width=True)

        # NEW: Wind Rose Plot – Wind Direction vs. Average Wind Speed
        st.subheader("Wind Direction vs. Average Wind Speed")
        
        # Bin wind directions into 15-degree sectors
        df_santa["wind_dir_bin"] = (df_santa["wind_direction"] // 15 * 15).astype(int)
        windrose_df = df_santa.groupby("wind_dir_bin")["wind_speed"].mean().reset_index()
        windrose_df = windrose_df.sort_values(by="wind_dir_bin")
        
        # Plot using plotly Barpolar
        fig_polar = go.Figure()
        fig_polar.add_trace(go.Barpolar(
            r=windrose_df["wind_speed"],
            theta=windrose_df["wind_dir_bin"],
            width=[15] * len(windrose_df),
            marker_color='rgb(255,127,14)',
            opacity=0.85,
            name="Avg Wind Speed (mph)"
        ))
        
        fig_polar.update_layout(
            title="Wind Rose: Avg Wind Speed by Direction (°)",
            height=600,
            polar=dict(
                angularaxis=dict(
                    direction="clockwise",
                    rotation=90,
                    tickmode='array',
                    tickvals=list(range(0, 360, 15)),  # now every 15 degrees
                    tickfont=dict(size=10)
                ),
                radialaxis=dict(
                    title="Wind Speed (mph)",
                    title_font=dict(color="white"),
                    tickfont=dict(color="white"),
                    gridcolor="gray"
                )
            ),
            template="plotly_dark",
            showlegend=False
        )
        
        st.plotly_chart(fig_polar, use_container_width=True)

# -------- Tab 6: Multivariate --------
with tab6:
    st.header("📊 Multivariate Explorer")
    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("Start Date", st.session_state["start6"], min_value=default_start, max_value=default_end, key="input_start6")
    with col2:
        end = st.date_input("End Date", st.session_state["end6"], min_value=default_start, max_value=default_end, key="input_end6")

    if st.button("🔄 Reset Multivariate"):
        st.session_state["start6"] = default_start
        st.session_state["end6"] = default_end
        start, end = default_start, default_end

    st.session_state["start6"] = start
    st.session_state["end6"] = end

    df_multi = df[(df["Date"] >= pd.to_datetime(start)) & (df["Date"] <= pd.to_datetime(end))].copy()

    var_choices = st.multiselect("Select up to 3 variables", variables, default=["air_temp", "relative_humidity"])
    normalize = st.checkbox("Normalize (0–1 scale)", value=False)
    smooth = st.checkbox("Apply Rolling Average", value=True)
    agg = st.radio("Aggregation Level", ["Monthly", "Yearly"], horizontal=True)

    if df_multi.empty or not var_choices:
        st.warning("Check date range or select at least one variable.")
    else:
        if agg == "Monthly":
            df_resampled = df_multi.resample("ME", on="Date").mean(numeric_only=True)
            window = 3
        else:
            df_resampled = df_multi.resample("YE", on="Date").mean(numeric_only=True)
            window = 2

        df_plot = df_resampled[var_choices].copy()

        if normalize:
            for col in df_plot.columns:
                min_val, max_val = df_plot[col].min(), df_plot[col].max()
                if max_val > min_val:
                    df_plot[col] = (df_plot[col] - min_val) / (max_val - min_val)

        if smooth:
            df_plot = df_plot.rolling(window=window, min_periods=1).mean()

        df_plot["Date"] = df_resampled.index

        fig = px.line(
            df_plot,
            x="Date",
            y=var_choices,
            template="plotly_dark",
            title=f"{agg} Trends" +
                  (" (Normalized)" if normalize else "") +
                  (" with Rolling Avg" if smooth else "")
        )

        # Smart y-axis label
        if normalize:
            y_label = "Normalized Value (0–1)"
        else:
            unit_map = {
                "air_temp": "°F",
                "relative_humidity": "%",
                "wind_speed": "mph",
                "wind_direction": "°",
                "altimeter": "inHg",
                "sea_level_pressure": "hPa",
                "Atmospheric Pressure": "hPa"
            }
            units = [unit_map.get(v, "") for v in var_choices]
            units_cleaned = sorted(set(u for u in units if u))
            y_label = f"Raw Value ({' / '.join(units_cleaned)})" if units_cleaned else "Raw Value"

        fig.update_layout(
            yaxis_title=y_label,
            xaxis_title="Date",
            legend_title="Variable"
        )
        st.plotly_chart(fig, use_container_width=True)

# -------------------- Tab 7: Definitions --------------------
with tab7:
    st.header("📘 Index")
    with st.expander("🧠 How to Interpret the Dashboard"):
        st.markdown("""
        This dashboard shows **weather conditions** at Oxnard Airport (KOXR) between 1999 and 2024.  
        Here's how to get the most out of it:

        - 🔄 **Click on the Reset button twice** to fully reset both the plot and date filter!
        - Use **date filters** to zoom in on specific time periods
        - Toggle **aggregation levels** to smooth out or highlight trends
        - The **Multivariate Explorer** is ideal for comparing 2–3 variables over time
        - Tabs like **Fire Conditions** or **Red Flag Warnings** help identify high-risk weather periods
        """)
    with st.expander("🔥 What is Fire Weather?"):
        st.markdown("""
        **Fire weather** refers to atmospheric conditions that promote the ignition and rapid spread of wildfires.

        These include:
        - High temperatures
        - Low relative humidity
        - Strong winds
        - Dry fuels or drought conditions

        Fire weather does **not** cause fire, but it makes existing fire much more dangerous.
        """)
    with st.expander("🚩 What is a Red Flag Warning?"):
        st.markdown("""
        A **Red Flag Warning** is issued when critical fire weather conditions are occurring or imminent.
        For Southern California, this usually means:
        - **Relative humidity ≤ 15%**
        - **Sustained wind ≥ 25 mph or gusts ≥ 35 mph**
        - **Critically dry fuels**
        """)
    with st.expander("🌡️ What Defines an 'Extreme Temperature Day'?"):
        st.markdown("""
        An **extreme temperature day** refers to a calendar day where the **air temperature exceeds a specified threshold**, typically associated with:
        
        - Increased heat stress for people and ecosystems
        - Heightened wildfire risk
        - Strain on energy infrastructure (like air conditioning usage)
        
        In this dashboard, you can dynamically adjust the threshold using the slider and observe how frequently such days occur.
        """)
    with st.expander("💨 What Are Santa Ana Winds?"):
        st.markdown("""
        **Santa Ana Winds** are strong, dry downslope winds that originate inland and affect coastal Southern California and northern Baja California. They are most common in the fall and winter months.
    
        They contribute significantly to wildfire risk due to:
        - **Very low humidity**
        - **High wind speeds**
        - **Rapid drying of fuels**
    
        These winds typically blow **from the northeast to the southwest**, and are modeled in this dashboard using a wind direction of **30°–120°** and wind speed ≥ 20 mph.
        """)
    with st.expander("📊 What Does Aggregation Mean?"):
        st.markdown("""
        **Aggregation** is the process of summarizing data over a specific time period.
        
        In this dashboard, you can view:
    
        - **Daily:** Raw measurements for each day  
        - **Monthly:** Averaged values for each calendar month  
        - **Yearly:** Averaged values across each year
    
        This helps identify patterns or trends over longer periods and smooth out day-to-day variability.
        """)
    with st.expander("📈 What Is Normalization?"):
        st.markdown("""
        **Normalization** scales variables to a 0–1 range so they can be compared directly, even if they have different units.
    
        For example:
        - Temperature (°F) → scaled to 0–1  
        - Relative humidity (%) → scaled to 0–1  
    
        This is especially useful in the **Multivariate Explorer** to visualize trends across variables on the same y-axis.
        """)
    with st.expander("🧮 Why Use Rolling Averages?"):
        st.markdown("""
        A **rolling average** smooths out short-term fluctuations by averaging data points over a moving window.
    
        Benefits:
        - Highlights longer-term trends  
        - Reduces noise from daily weather fluctuations  
        - Helps reveal climate signals in the data
    
        You can toggle this in the **Multivariate Explorer** tab.
        """)
    with st.expander("🔍 Glossary of Key Variables"):
        st.markdown("""
        - **Air Temp (°F):** Surface air temperature  
        - **Relative Humidity (%):** Moisture content in the air  
        - **Wind Speed (mph):** Horizontal wind strength  
        - **Wind Direction (°):** Compass direction the wind is coming from  
        - **Altimeter (inHg):** Atmospheric pressure at station level  
        - **Sea Level Pressure (hPa):** Pressure adjusted to sea level  
        - **Atmospheric Pressure (hPa):** Station-measured air pressure
        """)
    with st.expander("📚 Sources"):
        st.markdown("""
        The primary dataset comes from the **National Weather Service's historic observations** at KOXR (Oxnard Airport).
        
        Data was cleaned and compiled into a structured SQLite database for this dashboard.  

        📥 [Download the dataset (KOXR_2000–2024)](https://github.com/dr-adsalas/datawran/raw/main/KOXR_2000-2024_data.db)
        """)

streamlit run app.py
