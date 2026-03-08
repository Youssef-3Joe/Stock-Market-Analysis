import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
st.set_page_config(layout="wide")
# ===============================
# DATA LOADING
# ===============================

portfolio_prices = pd.read_csv("portfolio_prices.csv")
raw_data = pd.read_csv('all_stocks_raw.csv')

# ===============================
# DASHBOARD TITLE
# ===============================

st.title("📊 Portfolio Performance & Risk Intelligence Dashboard")

st.markdown("""
This interactive dashboard analyzes the **performance, growth, and risk profile** of a diversified portfolio of financial assets.

Inside this dashboard you will find:

• **Daily Market Snapshot** – latest price movements  
• **Sector & Market Behavior Analysis** – price trends and volatility  
• **Cumulative Return Analysis** – long-term investment growth  
• **Risk vs Return Visualization** – investment efficiency  
• **Sharpe Ratio Ranking** – risk-adjusted performance comparison

The goal is to help investors understand **which assets deliver the strongest returns relative to the risk taken**.
""")

# ===============================
# SIDEBAR
# ===============================

stock_list = [col for col in portfolio_prices.columns if col != 'Date']
selected_stock = st.sidebar.selectbox("Select a Stock to Analyze", stock_list)

# ===============================
# DATA PREPARATION
# ===============================

portfolio_prices['Date'] = pd.to_datetime(portfolio_prices['Date'])
portfolio_prices = portfolio_prices.sort_values('Date')

df_final = portfolio_prices.set_index('Date')
daily_returns = df_final.pct_change().dropna()

# ===============================
# DAILY MARKET SNAPSHOT
# ===============================

st.header("📅 Daily Market Snapshot")

st.markdown("""
This section displays the **latest price for each asset** along with the **daily return**.

**Daily Return** represents the **percentage change in price compared to the previous trading day**.

• Positive values indicate **daily gains**  
• Negative values indicate **daily losses**
""")

cols = st.columns(len(stock_list))

for i, stock in enumerate(stock_list):

    current_price = portfolio_prices[stock].iloc[-1]
    previous_price = portfolio_prices[stock].iloc[-2]

    daily_return = ((current_price - previous_price) / previous_price) * 100

    with cols[i]:
        st.metric(
            label=stock.upper(),
            value=f"${current_price:,.2f}",
            delta=f"{daily_return:+.2f}%"
        )

# ===============================
# MARKET DEEP DIVE
# ===============================

st.header("🔍 Market Behavior & Sector Analysis")

st.markdown("""
This section explores how different assets behave over time.

Each asset includes two charts:

• **Daily Returns** → highlights short-term volatility and market reactions  
• **Price Trend** → shows the long-term growth trajectory

These views allow investors to compare **stability versus growth potential** across assets and sectors.
""")

tab_safe, tab_tech = st.tabs(["🛡️ Safe Havens & Index", "🚀 Tech Sector Analysis"])

# ===============================
# SAFE HAVEN TAB
# ===============================

with tab_safe:

    st.subheader("Market Reliability vs Volatility")

    plt.style.use('dark_background')

    fig1, ax1 = plt.subplots(2, 3, figsize=(18,10), sharex=True)
    fig1.patch.set_facecolor('#0E1117')

    colors1 = {'gold':'orange','spy':'skyblue','tsla':'darkred'}
    stocks1 = ['gold','spy','tsla']

    for i,stock in enumerate(stocks1):

        daily_returns[stock].plot(ax=ax1[0][i],color=colors1[stock])
        ax1[0][i].set_title(f'{stock.upper()} Daily Returns',fontweight='bold')
        ax1[0][i].set_ylabel('Daily Return (%)')

        df_final[stock].plot(ax=ax1[1][i],color=colors1[stock])
        ax1[1][i].set_title(f'{stock.upper()} Price Trend',fontweight='bold')
        ax1[1][i].set_ylabel('Price (USD)')

    plt.tight_layout()
    st.pyplot(fig1)

    with st.expander("📖 Interpretation"):

        st.markdown("""
**Gold**  
Traditionally considered a **safe-haven asset**. It tends to move more steadily and is often used as protection during economic uncertainty.

**SPY**  
Represents the **S&P 500 index**, which reflects the overall performance of the US stock market.

**Tesla (TSLA)**  
A **high-growth but high-volatility stock**. Large daily movements indicate greater risk but also higher return potential.
""")

# ===============================
# TECH SECTOR TAB
# ===============================

with tab_tech:

    st.subheader("Technology Sector Leaders")

    fig2, ax2 = plt.subplots(2,3,figsize=(18,10),sharex=True)
    fig2.patch.set_facecolor('#0E1117')

    colors2={'msft':"#7E1679",'amzn':"#518207",'aapl':"#16567E"}
    stocks2=['msft','amzn','aapl']

    for i,stock in enumerate(stocks2):

        daily_returns[stock].plot(ax=ax2[0][i],color=colors2[stock])
        ax2[0][i].set_title(f'{stock.upper()} Daily Returns',fontweight='bold')
        ax2[0][i].set_ylabel('Daily Return (%)')

        df_final[stock].plot(ax=ax2[1][i],color=colors2[stock])
        ax2[1][i].set_title(f'{stock.upper()} Price Trend',fontweight='bold')
        ax2[1][i].set_ylabel('Price (USD)')

    plt.tight_layout()
    st.pyplot(fig2)

    with st.expander("📖 Interpretation"):

        st.markdown("""
**Microsoft, Amazon, and Apple** are three of the largest technology companies in the world.

They often move in similar directions because they are affected by:

• Interest rate changes  
• Global economic growth  
• Technology sector trends

Despite short-term volatility, these companies have historically shown **strong long-term growth**.
""")

# ===============================
# CUMULATIVE RETURN
# ===============================

st.header("📈 Long-Term Portfolio Growth")

st.markdown("""
### Cumulative Return

**Cumulative Return** measures the **total percentage growth of an asset from the beginning of the dataset until today**.

Formula:

Cumulative Return = (Current Price − Initial Price) / Initial Price

This answers an important investment question:

➡️ **If I invested at the start, how much would my investment be worth today?**
""")

cols_total = st.columns(len(stock_list))

for i,stock in enumerate(stock_list):

    initial_price = portfolio_prices[stock].iloc[0]
    current_price = portfolio_prices[stock].iloc[-1]

    total_growth=((current_price-initial_price)/initial_price)*100

    with cols_total[i]:

        st.metric(
            label=f"{stock.upper()} Total Return",
            value=f"{total_growth:+.1f}%",
            help=f"From ${initial_price:,.2f} to ${current_price:,.2f}"
        )

# ===============================
# CUMULATIVE BAR CHART
# ===============================

returns_dict={}

for stock in df_final.columns:
    ret=((df_final[stock].iloc[-1]/df_final[stock].iloc[0])-1)*100
    returns_dict[stock.upper()]=round(ret,2)

returns_series=pd.Series(returns_dict).sort_values(ascending=False)

left_gap,mid_col,right_gap=st.columns([1,3,1])

with mid_col:

    plt.style.use('dark_background')

    fig_bar,ax_bar=plt.subplots(figsize=(8,5))
    fig_bar.patch.set_facecolor('#0E1117')
    ax_bar.set_facecolor('#0E1117')

    # Custom colors for each asset
    colors = [
        '#FFD700' if x == 'GOLD'
        else '#E31937' if x == 'TSLA'
        else '#00A4EF' if x == 'MSFT'
        else '#555555' if x == 'AAPL'
        else '#4CAF50' if x == 'SPY'
        else '#FF9900'
        for x in returns_series.index
    ]

    bars=ax_bar.bar(returns_series.index,returns_series.values,color=colors)

    for bar in bars:

        yval=bar.get_height()

        ax_bar.text(
            bar.get_x()+bar.get_width()/2,
            yval+(yval*0.01),
            f'{yval}%',
            ha='center',
            va='bottom',
            fontweight='bold',
            color='white'
        )

    ax_bar.set_title('Total Portfolio Growth by Asset (%)',fontsize=14,fontweight='bold')

    ax_bar.spines['top'].set_visible(False)
    ax_bar.spines['right'].set_visible(False)

    st.pyplot(fig_bar)
# ===============================
# RISK VS RETURN
# ===============================

st.header("⚖️ Risk vs Return Analysis")

st.markdown("""
Investors must always balance **risk and return**.

This section evaluates each asset using:

• **Annualized Return** – average yearly profit  
• **Volatility (Risk)** – price fluctuations  
• **Sharpe Ratio** – efficiency of return relative to risk
""")

# Annualized metrics for scatter plot
annual_return = daily_returns.mean() * 252
annual_risk = daily_returns.std() * np.sqrt(252)

# Sharpe Ratio (same formula used in your Jupyter notebook)
mean_ret = daily_returns.mean()
std_dev = daily_returns.std()

sharpe_ratio = (mean_ret / std_dev) * np.sqrt(252)
sharpe_series = sharpe_ratio.sort_values(ascending=False)


# ===============================
# SHARPE RATIO
# ===============================

st.subheader("📊 Sharpe Ratio — Risk Efficiency Score")

st.markdown("""
The **Sharpe Ratio** measures how much **return an asset generates for each unit of risk taken**.

In this dashboard the Sharpe Ratio is calculated using the classic formula:

Sharpe Ratio = (Average Return / Volatility) × √252

Where:

• **Average Return** = Mean daily return  
• **Volatility** = Standard deviation of daily returns  
• **252** = Average number of trading days in a year

Interpretation:

• **Above 2** → Excellent risk-adjusted performance  
• **1 – 2** → Good efficiency  
• **Below 1** → Lower efficiency relative to risk
""")

cols_sharpe = st.columns(len(stock_list))

for i, stock in enumerate(sharpe_series.index):

    val = sharpe_series[stock]

    with cols_sharpe[i]:

        if val > 2:
            status = "Excellent"
        elif val > 1:
            status = "Good"
        else:
            status = "Moderate"

        st.metric(
            label=stock.upper(),
            value=f"{val:.2f}",
            help=f"Risk-adjusted performance: {status}"
        )


# ===============================
# RISK VS RETURN SCATTER
# ===============================

left, mid, right = st.columns([1,4,1])

with mid:

    plt.style.use('dark_background')

    fig_scatter, ax_scatter = plt.subplots(figsize=(10,6))
    fig_scatter.patch.set_facecolor('#0E1117')
    ax_scatter.set_facecolor('#0E1117')

    risk_return_df = pd.DataFrame({
        'Risk': annual_risk,
        'Return': annual_return,
        'Asset': annual_risk.index
    })

    sns.scatterplot(
        data=risk_return_df,
        x='Risk',
        y='Return',
        hue='Asset',
        palette='viridis',
        s=300,
        alpha=0.9,
        ax=ax_scatter,
        legend=False
    )

    # Add labels to points
    for i in range(len(risk_return_df)):

        ax_scatter.text(
            risk_return_df['Risk'].iloc[i] + 0.01,
            risk_return_df['Return'].iloc[i] + 0.01,
            risk_return_df['Asset'].iloc[i].upper(),
            fontsize=12,
            fontweight='bold',
            color='white'
        )

    ax_scatter.set_title('Risk vs Return Profile', fontsize=18, fontweight='bold', pad=20)

    ax_scatter.set_xlabel('Annualized Risk (Volatility)', fontsize=12)
    ax_scatter.set_ylabel('Annualized Return', fontsize=12)

    ax_scatter.grid(True, linestyle='--', alpha=0.2)

    st.pyplot(fig_scatter)


# ===============================
# INTERPRETATION
# ===============================

with st.expander("💡 How to interpret the Risk vs Return chart"):

    st.markdown("""
Each point represents an asset positioned by its **risk (volatility)** and **expected return**.

Quadrants explanation:

**Top-Left → Efficient Assets**  
Higher return with relatively lower risk.

**Top-Right → High Growth / High Volatility**  
Strong return potential but with larger price swings.

**Bottom-Left → Conservative Assets**  
Lower risk but also lower expected returns.

**Bottom-Right → Inefficient Assets**  
Higher risk without sufficient return — generally avoided by investors.
""")
    
# ===============================
# TAIL RISK ANALYSIS (KURTOSIS)
# ===============================

st.header("⚠️ Tail Risk & Fat-Tail Analysis")

st.markdown("""
### What is Kurtosis?

While Volatility tells us how much a stock moves, **Kurtosis** tells us **how extreme those moves are**. 

In finance, high Kurtosis indicates **"Fat Tails"** — meaning the asset has a higher probability of experiencing **extreme, unexpected price spikes or crashes** (Black Swan events).

• **High Kurtosis (> 3)** → "Leptokurtic" — Higher risk of extreme outliers.
• **Low Kurtosis (< 3)** → "Platykurtic" — More stable, fewer extreme surprises.
""")

# 1. Calculation
kurt_values = daily_returns.kurtosis().sort_values(ascending=False)

# 2. Metrics Row
cols_kurt = st.columns(len(stock_list))

for i, stock in enumerate(kurt_values.index):
    val = kurt_values[stock]
    with cols_kurt[i]:
        # Professional Interpretation logic
        if val > 10:
            risk_level = "Extreme Outliers"
        elif val > 3:
            risk_level = "High Fat-Tail Risk"
        else:
            risk_level = "Normal Distribution"
            
        st.metric(
            label=f"{stock.upper()} Kurtosis",
            value=f"{val:.2f}",
            help=f"Distribution shape: {risk_level}"
        )

# 3. Kurtosis Bar Chart (Centered)
left_k, mid_k, right_k = st.columns([1,3,1])

with mid_k:
    plt.style.use('dark_background')
    fig_kurt, ax_kurt = plt.subplots(figsize=(8,5))
    fig_kurt.patch.set_facecolor('#0E1117')
    ax_kurt.set_facecolor('#0E1117')

    # Using a "Rocket" style palette to highlight high-risk assets
    kurt_colors = sns.color_palette("rocket", len(kurt_values))
    
    bars_k = ax_kurt.bar(kurt_values.index, kurt_values.values, color=kurt_colors)

    # Add data labels on top
    for bar in bars_k:
        yval = bar.get_height()
        ax_kurt.text(
            bar.get_x() + bar.get_width()/2, 
            yval + 0.1, 
            f'{yval:.2f}', 
            ha='center', 
            fontweight='bold', 
            color='white'
        )

    ax_kurt.set_title('Asset Kurtosis Comparison (Tail Risk)', fontsize=14, fontweight='bold', pad=15)
    ax_kurt.set_ylabel('Kurtosis Value')
    
    # Clean up spines
    ax_kurt.spines['top'].set_visible(False)
    ax_kurt.spines['right'].set_visible(False)
    ax_kurt.grid(axis='y', linestyle='--', alpha=0.2)

    st.pyplot(fig_kurt)

# ===============================
# KURTOSIS INTERPRETATION
# ===============================

with st.expander("📖 Why does Kurtosis matter for your Portfolio?"):

    st.markdown("""
Looking at the chart above, you can see which assets are the most "unpredictable":

1. **The 'Jump' Assets (High Kurtosis)** If an asset like **SPY** or **GOLD** shows very high Kurtosis, it means it is prone to massive one-day gains or losses that don't happen often but are huge when they do.

2. **The 'Stable' Assets (Low Kurtosis)** Assets like **TSLA** or **AMZN** usually have lower Kurtosis, meaning their returns follow a more "Normal" bell curve with fewer extreme shocks.

**Investor Tip:** High Kurtosis isn't always bad (it could mean a massive jump UP), but it represents **Uncertainty**. Diversifying with low-kurtosis assets helps "smooth out" your portfolio's performance.
""")
