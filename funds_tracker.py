import streamlit as st
import requests
from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd
import plotly.express as px

# Set up the page
st.set_page_config(layout="wide", page_title="Alipay Fund Performance Tracker")
st.title("Alipay Fund Performance Tracker")
st.markdown("---")

# --- Common Headers & Configuration ---
COMMON_HEADERS = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                  'Version/26.0.1 Safari/605.1.15',
    'X-Requested-With': 'XMLHttpRequest',
}

# Add inception dates as properties
FUND_CONFIG = {
    "000043": {
        "name": "嘉实美国成长股票",
        "inception_date": date(2013, 6, 14),  # 2013-06-14
        "url": "http://www.jsfund.cn/servlet/json",
        "method": "POST",
        "headers": {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': "http://www.jsfund.cn/main/fund/000043/fundManager.shtml",
        },
        "payload_keys": {"start": "start_date", "end": "end_date"},  # Keys used in payload
        "payload": {  # Base payload with dummy dates
            'sessionId': '2',
            'funcNo': '741012',
            'product_id': '410',
            'type': '2',
            'query_month': '',
            'is_page': '',
            'cur_page': '',
            'num_per_page': '',
            'is_trend': ''
        },
        "json_key": "results",
        "date_key": "nav_date",
        "unit_nav_key": "relate_price",
        "cumulative_nav_key": "cumulative_net"
    },
    "270023": {
        "name": "广发全球精选股票",
        "inception_date": date(2010, 8, 18),  # 2010-08-18
        "url": "http://www.gffunds.com.cn/apistore/JsonService",
        "method": "GET",
        "headers": {
            'Referer': "http://www.gffunds.com.cn/funds/?fundcode=270023",
        },
        "payload_keys": {"start": "startdate", "end": "enddate"},  # Keys used in payload
        "payload": {  # Base payload with dummy dates
            'service': 'MarketPerformance',
            'method': 'NAV',
            'op': 'queryNAVByFundcode',
            'fundcode': '270023',
            '_mode': 'all',
        },
        "json_key": "data",
        "date_key": "NAVDATE",
        "unit_nav_key": "NAVUNIT",
        "cumulative_nav_key": "NAVACCUMULATED"
    }
}


# --- Helper Function to Calculate Dates ---

def calculate_start_date(period_str, fund_id):
    today = date.today()
    config = FUND_CONFIG[fund_id]

    # Get the inception date from the config
    inception_date = config['inception_date']

    start_date = None

    if period_str == '近 1 月':
        start_date = today - relativedelta(months=1)
    elif period_str == '近 3 月':
        start_date = today - relativedelta(months=3)
    elif period_str == '近 6 月':
        start_date = today - relativedelta(months=6)
    elif period_str == '近 1 年':
        start_date = today - relativedelta(years=1)
    elif period_str == '近 3 年':
        start_date = today - relativedelta(years=3)
    elif period_str == '近 5 年':
        start_date = today - relativedelta(years=5)
    elif period_str == '今年以来':
        start_date = date(today.year, 1, 1)
    elif period_str == '成立以来':
        # Use the actual inception date of the fund
        start_date = inception_date

    # Ensure start date is not before inception date (except for '成立以来')
    if start_date and period_str != '成立以来':
        if start_date < inception_date:
            start_date = inception_date  # Clamp to inception if calculated date is too early

    # Default to '成立以来' if calculation fails or is not found (shouldn't happen with the options given)
    if not start_date:
        start_date = inception_date

    return start_date.strftime("%Y%m%d"), today.strftime("%Y%m%d")


# --- Combined Scraping Function ---

# Use Streamlit's cache but key it by the fund ID and the date range
@st.cache_data(show_spinner=False)
def get_fund_data(fund_id, start_date_str, end_date_str):
    """Fetches and processes data for a given fund ID and date range."""
    config = FUND_CONFIG[fund_id]

    try:
        # 1. Update Payload with selected dates
        payload = config['payload'].copy()  # Use a copy to avoid overwriting the original config
        payload[config['payload_keys']['start']] = start_date_str
        payload[config['payload_keys']['end']] = end_date_str

        # 2. Prepare Request
        session = requests.Session()
        session.headers.update(COMMON_HEADERS)
        session.headers.update(config['headers'])

        # 3. Execute Request
        if config['method'] == 'POST':
            response = session.post(config['url'], data=payload)
        else:
            response = session.get(config['url'], params=payload)

        response.raise_for_status()
        data = response.json()

        # 4. Process Data
        results_list = data.get(config['json_key'])
        if not results_list:
            raise ValueError(f"No data found under key '{config['json_key']}'")

        df = pd.DataFrame(results_list)

        if fund_id == '000043':
            df[config['date_key']] = pd.to_datetime(df[config['date_key']], format="%Y-%m-%d", errors='coerce')
        else:
            df[config['date_key']] = pd.to_datetime(df[config['date_key']], format="%Y%m%d", errors='coerce')

        df = df.sort_values(config['date_key'], ascending=False)
        return df[[config['date_key'], config['unit_nav_key'], config['cumulative_nav_key']]]

    except Exception as e:
        st.error(f"Failed to fetch or process data for {config['name']}: {e}")
        return pd.DataFrame()


# --- Reusable GUI Function ---

DATE_RANGES = ['近 1 月', '近 3 月', '近 6 月', '近 1 年', '近 3 年', '近 5 年', '今年以来', '成立以来']


def display_fund_section(fund_id):
    """Displays the GUI for a single fund."""
    fund_name = FUND_CONFIG[fund_id]['name']
    st.header(f"{fund_name} ({fund_id})")

    col_selector, col_button = st.columns([4, 1], gap="large")

    with col_selector:
        # 1. Date Range Selector
        selected_range = st.radio(
            "Select Date Range:",
            options=DATE_RANGES,
            index=len(DATE_RANGES) - 1,
            key=f'range_radio_{fund_id}',
            horizontal=True
        )

        # 2. Calculate Dates
        start_date_str, end_date_str = calculate_start_date(selected_range, fund_id)

        # 3. Data Fetching and Refresh Logic
        data = get_fund_data(fund_id, start_date_str, end_date_str)

    with col_button:
        st.write("")
        if st.button(f"Refresh Data (Current Range)", key=f"refresh_button_{fund_id}"):
            st.cache_data.clear()
            # Data will be re-fetched on the next Streamlit run

    st.info(f"Fetching {fund_name} ({fund_id}) data from {start_date_str} to {end_date_str}...")
    st.divider()

    # 4. Display Table and Chart
    col_table, col_chart = st.columns([1, 3], gap="large")
    with col_table:
        # Display the data table
        if not data.empty:
            data.columns = ['Date', 'Unit NAV', 'Cumulative NAV']
            data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')
            st.dataframe(data, width='stretch')
        else:
            st.warning("No data to display for this fund in the selected range.")

    with col_chart:
        # Display the line chart
        if not data.empty:
            df_long = data.melt(id_vars='Date', var_name='Metric', value_name='Value')
            df_long['Value'] = pd.to_numeric(df_long['Value'], errors='coerce')

            fig = px.line(
                df_long,
                x='Date',
                y='Value',
                color='Metric',
                title=f'{fund_name} Price Trends ({selected_range})',
                labels={'Date': 'Date', 'Value': 'Value', 'Metric': 'Metric'},
            )
            st.plotly_chart(fig, use_container_width=True)
        # Warning already shown in col1 if data is empty


# --- Main App Logic ---
display_fund_section("000043")
st.divider()
display_fund_section("270023")
st.divider()