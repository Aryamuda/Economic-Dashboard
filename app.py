import streamlit as st
import pandas as pd
import plotly.express as px
from fredapi import Fred
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv


load_dotenv()

SERIES_INFO = {
    'United States': {
        'CPI': 'CPIAUCSL',
        'Real GDP': 'GDPC1',
        'Nominal GDP': 'GDP',
        'Unemployment Rate': 'UNRATE',
        'label': 'United States',
        'gdp_frequency': 'Q',
        'cpi_frequency': 'M',
        'unemployment_frequency': 'M'
    },
    'Euro Area': {
        'CPI': 'CP0000EZ20M086NEST',
        'Real GDP': 'CLVMNACSCAB1GQEZ20',
        'Nominal GDP': 'CPMNACSCAB1GQEZ20',
        'Unemployment Rate': 'LRHUTTTTEZM156S',
        'label': 'Euro Area',
        'gdp_frequency': 'Q',
        'cpi_frequency': 'M',
        'unemployment_frequency': 'M'
    },
    'Japan': {
        'CPI': 'JPNCPIALLMINMEI',
        'Real GDP': 'JPNRGDPEXP',
        'Nominal GDP': 'JPNNGDPEXP',
        'Unemployment Rate': 'LRUNTTTTJPM156S',
        'label': 'Japan',
        'gdp_frequency': 'Q',
        'cpi_frequency': 'M',
        'unemployment_frequency': 'M'
    },
    'United Kingdom': {
        'CPI': 'GBRCPIALLMINMEI',
        'Real GDP': 'CLVMNACSCAB1GQGB',
        'Nominal GDP': 'CPMNACSCAB1GQGB',
        'Unemployment Rate': 'LMUNRRTTGBM156S',
        'label': 'United Kingdom',
        'gdp_frequency': 'Q',
        'cpi_frequency': 'M',
        'unemployment_frequency': 'M'
    },
    'Canada': {
        'CPI': 'CANCPIALLMINMEI',
        'Real GDP': 'NAEXKP01CAQ189S',
        'Nominal GDP': 'CANNGDPNQDSMEI',
        'Unemployment Rate': 'LRUNTTTTCAM156S',
        'label': 'Canada',
        'gdp_frequency': 'Q',
        'cpi_frequency': 'M',
        'unemployment_frequency': 'M'
    },
    'Australia': {
        'CPI': 'AUSCPIALLMINMEI',
        'Real GDP': 'RGDPMLAUA',
        'Nominal GDP': 'NGDPSAXDCAUQ',
        'Unemployment Rate': 'LRUNTTTTAUM156S',
        'label': 'Australia',
        'gdp_frequency': 'Q',
        'cpi_frequency': 'M',
        'unemployment_frequency': 'M'
    },
    'Switzerland': {
        'CPI': 'CHECPIALLMINMEI',
        'Real GDP': 'NAEXKP01CHQ189S',
        'Nominal GDP': 'CHENNGDPNQDSMEI',
        'Unemployment Rate': 'LRUNTTTTCHM156S',
        'label': 'Switzerland',
        'gdp_frequency': 'Q',
        'cpi_frequency': 'M',
        'unemployment_frequency': 'M'
    },
    'New Zealand': {
        'CPI': 'NZLCPIALLMINMEI',
        'Real GDP': 'MKTGDPRNZQ',
        'Nominal GDP': 'MKTGDPNZQ',
        'Unemployment Rate': 'LRUNTTTTNZM156S',
        'label': 'New Zealand',
        'gdp_frequency': 'Q',
        'cpi_frequency': 'M',
        'unemployment_frequency': 'M'
    }
}

@st.cache_data(ttl=3600)
def fetch_fred_data(api_key, series_id, series_name, frequency):
    try:
        fred = Fred(api_key=api_key)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=10 * 365 + 2 * 365)

        data = fred.get_series(series_id, observation_start=start_date, observation_end=end_date)
        df = pd.DataFrame(data, columns=[series_name]).dropna()

        if frequency == 'M':
            df[f'{series_name} YoY % Change'] = (df[series_name] / df[series_name].shift(12) - 1) * 100
        elif frequency == 'Q':
            df[f'{series_name} YoY % Change'] = (df[series_name] / df[series_name].shift(4) - 1) * 100
        else:
            df[f'{series_name} YoY % Change'] = (df[series_name] / df[series_name].shift(1) - 1) * 100

        final_start_date = datetime.now() - timedelta(days=10 * 365)
        df = df[df.index >= pd.to_datetime(final_start_date)]
        return df.dropna(subset=[f'{series_name} YoY % Change'], how='any')
    except Exception as e:
        st.error(f"Error fetching data for {series_name} ({series_id}): {e}")
        return pd.DataFrame()


def plot_data(df, value_col, yoy_col, title):
    if df.empty or value_col not in df.columns or yoy_col not in df.columns:
        st.warning(f"Not enough data to plot for {title}.")
        return

    fig_val = px.line(df, x=df.index, y=value_col, title=f'{title} - Values',
                      labels={'x': 'Date', value_col: value_col})
    st.plotly_chart(fig_val, use_container_width=True)

    fig_yoy = px.line(df, x=df.index, y=yoy_col, title=f'{title} - YoY % Change',
                      labels={'x': 'Date', yoy_col: 'YoY % Change'})
    st.plotly_chart(fig_yoy, use_container_width=True)


def plot_comparison_data(data_dict, series_name_to_plot, title):
    combined_df = pd.DataFrame()
    for country, df in data_dict.items():
        if not df.empty and series_name_to_plot in df.columns:
            temp_df = df[[series_name_to_plot]].copy()
            temp_df.rename(columns={series_name_to_plot: country}, inplace=True)
            if combined_df.empty:
                combined_df = temp_df
            else:
                combined_df = combined_df.join(temp_df, how='outer')

    if combined_df.empty:
        st.warning(f"No data available for the selected countries/indicator to plot {title}.")
        return

    fig = px.line(combined_df, x=combined_df.index, y=combined_df.columns,
                  title=title, labels={'x': 'Date', 'value': series_name_to_plot})
    st.plotly_chart(fig, use_container_width=True)

# --- Streamlit App UI ---
st.set_page_config(layout="wide")
st.title("Economic Indicator Dashboard")
st.markdown("Visualize key economic indicators for major economies.")

api_key = None
try:
    api_key = st.secrets["FRED_API_KEY"]
except (KeyError, FileNotFoundError):
    api_key = os.getenv("FRED_API_KEY")

app_mode = st.sidebar.radio(
    "Select Dashboard Mode:",
    ("Single Country Deep Dive", "Multi-Country Comparison")
)

if not api_key:
    st.error("FRED API Key not found!")
    st.stop()

if app_mode == "Single Country Deep Dive":
    st.header("Single Country Deep Dive")
    selected_country_label = st.selectbox(
        "Select Country:",
        options=list(SERIES_INFO.keys()),
        format_func=lambda x: SERIES_INFO[x]['label']
    )

    if selected_country_label:
        country_config = SERIES_INFO[selected_country_label]
        st.subheader(f"Indicators for {country_config['label']}")

        indicators_to_fetch = {
            "CPI": (country_config['CPI'], country_config['cpi_frequency']),
            "Real GDP": (country_config['Real GDP'], country_config['gdp_frequency']),
            "Nominal GDP": (country_config['Nominal GDP'], country_config['gdp_frequency']),
            "Unemployment Rate": (country_config['Unemployment Rate'], country_config['unemployment_frequency'])
        }

        for indicator_name, (series_id, freq) in indicators_to_fetch.items():
            with st.spinner(f"Fetching {indicator_name} data for {country_config['label']}..."):
                df_indicator = fetch_fred_data(api_key, series_id, indicator_name, freq)
            if not df_indicator.empty:
                plot_data(df_indicator, indicator_name, f'{indicator_name} YoY % Change',
                          f"{country_config['label']} - {indicator_name}")
            else:
                st.warning(f"Could not retrieve data for {indicator_name} for {country_config['label']}.")
            st.markdown("---")


elif app_mode == "Multi-Country Comparison":
    st.header("Multi-Country Comparison (Raw Values)") # Changed header slightly

    indicator_options_map = {
        "CPI": "CPI",
        "Real GDP": "Real GDP",
        "Nominal GDP": "Nominal GDP",
        "Unemployment Rate": "Unemployment Rate"
    }
    selected_indicator_display_name = st.selectbox(
        "Select Indicator to Compare:",
        options=list(indicator_options_map.keys())
    )
    series_name_to_plot = indicator_options_map[selected_indicator_display_name]

    selected_country_labels = st.multiselect(
        "Select Countries to Compare:",
        options=list(SERIES_INFO.keys()),
        format_func=lambda x: SERIES_INFO[x]['label'],
        default=list(SERIES_INFO.keys())[:2]
    )

    if selected_country_labels and selected_indicator_display_name:
        comparison_data = {}
        for country_label in selected_country_labels:
            country_config = SERIES_INFO[country_label]

            series_id_to_fetch = ""
            frequency_to_fetch = ""

            if series_name_to_plot == "CPI":
                series_id_to_fetch = country_config['CPI']
                frequency_to_fetch = country_config['cpi_frequency']
            elif series_name_to_plot == "Real GDP":
                series_id_to_fetch = country_config['Real GDP']
                frequency_to_fetch = country_config['gdp_frequency']
            elif series_name_to_plot == "Nominal GDP":
                series_id_to_fetch = country_config['Nominal GDP']
                frequency_to_fetch = country_config['gdp_frequency']
            elif series_name_to_plot == "Unemployment Rate":
                series_id_to_fetch = country_config['Unemployment Rate']
                frequency_to_fetch = country_config['unemployment_frequency']

            if series_id_to_fetch:
                with st.spinner(f"Fetching {series_name_to_plot} for {country_config['label']}..."):
                    df_country_indicator = fetch_fred_data(api_key, series_id_to_fetch, series_name_to_plot,
                                                           frequency_to_fetch)
                if not df_country_indicator.empty and series_name_to_plot in df_country_indicator.columns:
                    comparison_data[country_config['label']] = df_country_indicator[[series_name_to_plot]]
                else:
                    comparison_data[country_config['label']] = pd.DataFrame(columns=[series_name_to_plot])

        plot_comparison_data(comparison_data, series_name_to_plot,
                             f"Comparison: {selected_indicator_display_name} (Raw Values)")
    else:
        st.info("Please select an indicator and at least one country for comparison.")