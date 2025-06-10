# Economic Indicator Dashboard

This project is an interactive web application built with Streamlit that visualizes key economic indicators for major economies. It fetches real-time data from the Federal Reserve Economic Data (FRED) database, providing a tool for economic analysis and comparison.

## Features

  - **Two Dashboard Modes**:
    1.  **Single Country Deep Dive**: Allows users to select a country and view detailed plots for multiple key economic indicators, including CPI, Real GDP, Nominal GDP, and Unemployment Rate. Both raw values and Year-over-Year (YoY) percentage changes are displayed.
    2.  **Multi-Country Comparison**: Enables users to compare a single economic indicator (e.g., Real GDP) across multiple countries on a single chart.
  - **Interactive Visualizations**: Utilizes Plotly to create interactive and easy-to-understand charts.
  - **Dynamic Data Fetching**: Retrieves up-to-date economic data directly from the FRED API.
  - **Performance Optimized**: Caches API results to ensure a fast and responsive user experience.
  - **Supported Economies**: Includes data for the United States, Euro Area, Japan, United Kingdom, Canada, Australia, Switzerland, and New Zealand.

## Data Source

All economic data is sourced from the [Federal Reserve Economic Data (FRED)](https://fred.stlouisfed.org/) provided by the Federal Reserve Bank of St. Louis.

## Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

  - Python 3.7+
  - A FRED API Key

### Installation & Setup

1.  **Clone the Repository**

    ```bash
    git clone https://github.com/aryamuda/economic-dashboard.git
    cd economic-dashboard
    ```

2.  **Install Dependencies**
    Install the required Python packages using the `requirements.txt` file.

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set Up Your FRED API Key**
    This application requires a FRED API key to function. You can obtain a free key from the [FRED website](https://fred.stlouisfed.org/docs/api/api_key.html).

    Once you have your key, create a file named `.env` in the root of the project directory and add your API key to it as follows:

    ```
    FRED_API_KEY="YOUR_API_KEY_HERE"
    ```

    The application will automatically load the key from this file.

4.  **Run the Application**
    Launch the Streamlit app with the following command:

    ```bash
    streamlit run app.py
    ```

    The application will open in your default web browser.

## Usage

  - Upon launching, you will be prompted to select a dashboard mode from the sidebar.
  - **For the Single Country Deep Dive**: Choose a country from the dropdown menu to see its economic indicators.
  - **For the Multi-Country Comparison**: Select an indicator and then choose the countries you wish to compare using the multiselect box.

## Technologies Used

  - **Streamlit**: For building the interactive web application.
  - **Pandas**: For data manipulation and analysis.
  - **Plotly**: For creating interactive data visualizations.
  - **FredAPI**: A Python wrapper for the FRED API.
  - **Python-Dotenv**: For managing environment variables.
