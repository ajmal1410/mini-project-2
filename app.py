import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Stock Market Dashboard",
    layout="wide"
)

st.title("📈 Stock Market Analysis Dashboard")

# ---------------------------------------------------
# LOAD ALL CSV FILES
# ---------------------------------------------------

files = glob.glob("data/csv_files/*.csv")

all_dfs = []

for file in files:

    df = pd.read_csv(file)

    stock_name = os.path.basename(file).replace(".csv", "")

    df['Ticker'] = stock_name

    all_dfs.append(df)

# ---------------------------------------------------
# MASTER DATAFRAME
# ---------------------------------------------------

master_df = pd.concat(all_dfs)

# ---------------------------------------------------
# DATE FORMAT
# ---------------------------------------------------

master_df['date'] = pd.to_datetime(master_df['date'])

# ---------------------------------------------------
# CREATE SUMMARY DATA
# ---------------------------------------------------

summary = []

for ticker in master_df['Ticker'].unique():

    stock_df = master_df[
        master_df['Ticker'] == ticker
    ].sort_values('date')

    yearly_return = (
        (
            stock_df['close'].iloc[-1]
            -
            stock_df['close'].iloc[0]
        )
        /
        stock_df['close'].iloc[0]
    ) * 100

    stock_df['Daily_Return'] = stock_df[
        'close'
    ].pct_change()

    volatility = stock_df[
        'Daily_Return'
    ].std()

    avg_price = stock_df['close'].mean()

    avg_volume = stock_df['volume'].mean()

    summary.append({

        'Ticker': ticker,
        'Yearly_Return': yearly_return,
        'Volatility': volatility,
        'Average_Price': avg_price,
        'Average_Volume': avg_volume

    })

summary_df = pd.DataFrame(summary)

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.title("📌 Dashboard Menu")

menu = st.sidebar.selectbox(

    "Select Analysis",

    [

        "Market Summary",
        "Top 10 Green Stocks",
        "Top 10 Red Stocks",
        "Volatility Analysis",
        "Sector Performance",
        "Correlation Heatmap",
        "Cumulative Return",
        "Monthly Gainers & Losers",
        "Individual Stock Analysis"

    ]

)

# ---------------------------------------------------
# MARKET SUMMARY
# ---------------------------------------------------

if menu == "Market Summary":

    st.subheader("📊 Market Summary")

    green = (
        summary_df['Yearly_Return'] > 0
    ).sum()

    red = (
        summary_df['Yearly_Return'] < 0
    ).sum()

    avg_price = summary_df[
        'Average_Price'
    ].mean()

    avg_volume = summary_df[
        'Average_Volume'
    ].mean()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Green Stocks", green)

    col2.metric("Red Stocks", red)

    col3.metric(
        "Average Price",
        round(avg_price,2)
    )

    col4.metric(
        "Average Volume",
        round(avg_volume,2)
    )

# ---------------------------------------------------
# TOP 10 GREEN STOCKS
# ---------------------------------------------------

elif menu == "Top 10 Green Stocks":

    st.subheader("📈 Top 10 Green Stocks")

    top_green = summary_df.sort_values(

        by='Yearly_Return',
        ascending=False

    ).head(10)

    st.dataframe(top_green)

    fig, ax = plt.subplots(figsize=(12,5))

    ax.bar(

        top_green['Ticker'],
        top_green['Yearly_Return']

    )

    ax.set_title("Top 10 Green Stocks")

    plt.xticks(rotation=45)

    st.pyplot(fig)

# ---------------------------------------------------
# TOP 10 RED STOCKS
# ---------------------------------------------------

elif menu == "Top 10 Red Stocks":

    st.subheader("📉 Top 10 Red Stocks")

    top_red = summary_df.sort_values(

        by='Yearly_Return'

    ).head(10)

    st.dataframe(top_red)

    fig, ax = plt.subplots(figsize=(12,5))

    ax.bar(

        top_red['Ticker'],
        top_red['Yearly_Return']

    )

    ax.set_title("Top 10 Red Stocks")

    plt.xticks(rotation=45)

    st.pyplot(fig)

# ---------------------------------------------------
# VOLATILITY ANALYSIS
# ---------------------------------------------------

elif menu == "Volatility Analysis":

    st.subheader("📊 Top 10 Volatile Stocks")

    volatility_top10 = summary_df.sort_values(

        by='Volatility',
        ascending=False

    ).head(10)

    st.dataframe(volatility_top10)

    fig, ax = plt.subplots(figsize=(12,5))

    ax.bar(

        volatility_top10['Ticker'],
        volatility_top10['Volatility']

    )

    ax.set_title("Top 10 Volatile Stocks")

    plt.xticks(rotation=45)

    st.pyplot(fig)

# ---------------------------------------------------
# SECTOR PERFORMANCE
# ---------------------------------------------------

elif menu == "Sector Performance":

    st.subheader("📊 Average Yearly Return by Sector")

    sector_df = pd.read_csv(
        "D:\stock_analysis_project\data\Sector_data - Sheet1.csv"
    )

    sector_df.columns = sector_df.columns.str.strip()

    sector_df['Symbol'] = (

        sector_df['Symbol']
        .astype(str)
        .str.split(':')
        .str[-1]
        .str.strip()

    )

    merged_df = pd.merge(

        summary_df,
        sector_df,

        left_on='Ticker',
        right_on='Symbol'

    )

    sector_performance = merged_df.groupby(

        'sector'

    )['Yearly_Return'].mean().reset_index()

    fig, ax = plt.subplots(figsize=(14,6))

    bars = ax.bar(

        sector_performance['sector'],
        sector_performance['Yearly_Return']

    )

    for bar in bars:

        yval = round(bar.get_height(),2)

        ax.text(

            bar.get_x() + bar.get_width()/2,
            yval,
            yval,

            ha='center',
            va='bottom'

        )

    plt.xticks(rotation=45)

    ax.set_title(
        "Average Yearly Return by Sector"
    )

    st.pyplot(fig)

# ---------------------------------------------------
# CORRELATION HEATMAP
# ---------------------------------------------------

elif menu == "Correlation Heatmap":

    st.subheader("🔥 Top 10 Stock Correlation Heatmap")

    top10_tickers = master_df[
        'Ticker'
    ].unique()[:10]

    heatmap_df = master_df[

        master_df['Ticker'].isin(
            top10_tickers
        )

    ]

    pivot_df = heatmap_df.pivot_table(

        index='date',
        columns='Ticker',
        values='close'

    )

    correlation_matrix = pivot_df.corr()

    fig, ax = plt.subplots(figsize=(10,6))

    sns.heatmap(

        correlation_matrix,
        annot=True,
        cmap='coolwarm',
        ax=ax

    )

    st.pyplot(fig)

# ---------------------------------------------------
# CUMULATIVE RETURN
# ---------------------------------------------------

elif menu == "Cumulative Return":

    st.subheader("📈 Top 5 Cumulative Returns")

    master_df['Daily_Return'] = master_df.groupby(
        'Ticker'
    )['close'].pct_change()

    master_df['Cumulative_Return'] = (

        1 + master_df['Daily_Return']

    ).groupby(master_df['Ticker']).cumprod()

    top5 = summary_df.sort_values(

        by='Yearly_Return',
        ascending=False

    ).head(5)['Ticker']

    fig, ax = plt.subplots(figsize=(14,6))

    for ticker in top5:

        temp_df = master_df[
            master_df['Ticker'] == ticker
        ]

        ax.plot(

            temp_df['date'],
            temp_df['Cumulative_Return'],

            label=ticker

        )

    ax.legend()

    ax.set_title("Top 5 Performing Stocks")

    st.pyplot(fig)

# ---------------------------------------------------
# MONTHLY GAINERS & LOSERS
# ---------------------------------------------------

elif menu == "Monthly Gainers & Losers":

    st.subheader("📅 Monthly Top Gainers & Losers")

    master_df['Month'] = master_df[
        'date'
    ].dt.month_name()

    monthly_returns = []

    for stock in master_df['Ticker'].unique():

        stock_df = master_df[
            master_df['Ticker'] == stock
        ].sort_values('date')

        monthly = stock_df.groupby(

            'Month'

        ).agg({

            'open':'first',
            'close':'last'

        }).reset_index()

        monthly['Return_%'] = (

            (
                monthly['close']
                -
                monthly['open']
            )

            /
            monthly['open']

        ) * 100

        monthly['Ticker'] = stock

        monthly_returns.append(monthly)

    monthly_return_df = pd.concat(
        monthly_returns
    )

    selected_month = st.selectbox(

        "Select Month",

        monthly_return_df['Month'].unique()

    )

    month_df = monthly_return_df[

        monthly_return_df['Month']
        == selected_month

    ]

    gainers = month_df.nlargest(
        5,
        'Return_%'
    )

    losers = month_df.nsmallest(
        5,
        'Return_%'
    )

    col1, col2 = st.columns(2)

    with col1:

        st.write("### Top 5 Gainers")

        st.dataframe(gainers)

    with col2:

        st.write("### Top 5 Losers")

        st.dataframe(losers)

# ---------------------------------------------------
# INDIVIDUAL STOCK ANALYSIS
# ---------------------------------------------------

elif menu == "Individual Stock Analysis":

    st.subheader("📌 Individual Stock Analysis")

    stock = st.selectbox(

        "Select Stock",

        master_df['Ticker'].unique()

    )

    stock_df = master_df[
        master_df['Ticker'] == stock
    ]

    st.dataframe(stock_df.head())

    fig, ax = plt.subplots(figsize=(14,5))

    ax.plot(

        stock_df['date'],
        stock_df['close']

    )

    ax.set_title(stock)

    ax.set_xlabel("Date")

    ax.set_ylabel("Close Price")

    st.pyplot(fig)

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.success("✅ Dashboard Loaded Successfully")