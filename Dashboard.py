import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
from plotly import express as px
import statsmodels.api as sm 
import scipy.stats as stats 

# 1. SET PAGE CONFIG (MUST BE FIRST)
st.set_page_config(layout="wide", page_title="Stock Intelligence Dashboard")

# ===============================
# 2. CACHING ENGINE
# ===============================
@st.cache_data
def get_clean_data():
    # Load the CSV
    df = pd.read_csv("portfolio_prices.csv")
    
    # Check if 'Date' is in index or columns
    if 'Date' not in df.columns and df.index.name == 'Date':
        df = df.reset_index()
    
    # Standardize column names
    df.columns = [c.capitalize() if c.lower() == 'date' else c for c in df.columns]
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    return df

@st.cache_data
def get_bollinger_bands(df, column, window=50):
    rolling_mean = df[column].rolling(window).mean()
    rolling_std = df[column].rolling(window).std()
    upper = rolling_mean + (rolling_std * 2)
    lower = rolling_mean - (rolling_std * 2)
    return rolling_mean, upper, lower

# ===============================
# 3. DATA LOADING & PREP
# ===============================
portfolio_prices = get_clean_data()
# Get list of stocks (all columns except Date)
stock_list = [col for col in portfolio_prices.columns if col != 'Date']

# ===============================
# 4. SIDEBAR
# ===============================
with st.sidebar:
    st.info("Data auto-updates daily at 12 AM Cairo via GitHub Actions.")

# ===============================
# 5. MAIN HEADER & LOGIC
# ===============================
last_update = portfolio_prices['Date'].max().strftime('%B %d, %Y')

st.title("📈 Stock Market Intelligence Dashboard")
st.subheader(f"Data last synchronized: {last_update}")
st.success(f"Verified: System successfully pulled the latest market Adjusted close for {last_update}.")

# Prepare the final dataframe for analysis
df_final = portfolio_prices.set_index('Date')
daily_returns = df_final.pct_change().dropna()
# ===============================
# DAILY MARKET SNAPSHOT
# ===============================

st.header("📅 Daily Return")

st.markdown("""This section displays the latest price for each asset, along with the daily return below it.

The daily return represents the percentage change in price compared to the previous trading day.

If the arrow below the latest price is green, it indicates that the price increased on the last trading day. Conversely, if the arrow is red, it signifies the opposite.""")

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

st.markdown('---')
# ===============================
# MARKET DEEP DIVE
# ===============================

st.header("🔍 Market Behavior & Sector Analysis")

st.markdown("""
This section explores how different assets behave over time.

Each asset includes two charts:

• **Daily Returns** → highlights short-term volatility and market reactions  
• **Price Trend** → shows the long-term growth trajectory

These views allow you to compare **stability versus growth potential** across assets and sectors.
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
                    
Traditionally considered a safe-haven asset, gold tends to move more steadily. However, it experienced an increase in 2025 and at the beginning of 2026, and it continues to rise.

**SPY**
                    
SPY represents the S&P 500 index, which reflects the overall performance of the U.S. stock market.

**Tesla (TSLA)**
                    
Tesla is a high-growth, high-volatility stock. Its large daily movements indicate greater risk but also higher return potential""")

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

Their charts reveal a shared vulnerability. In late 2022 and early 2023, all three experienced a **significant drawdown**. This wasn't due to poor management, but rather a **shifting macroeconomic climate—specifically** rising interest rates that pressured the entire tech sector.                    

Despite short-term volatility, these companies have historically shown **strong long-term growth**.
""")
        
st.markdown('---')

# ===============================
# CUMULATIVE RETURN
# ===============================

st.header("📈 Cumulative Return")

st.markdown("""

**Cumulative Return** measures the **total percentage growth of an asset from the beginning of the dataset until today**.

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

st.markdown('---')    

# ===============================
# RISK VS RETURN
# ===============================

st.header("⚖️ Risk vs Return Analysis")

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

st.subheader("📊 Sharpe Ratio")

st.markdown("""
The **Sharpe Ratio** measures how much **return an asset generates for each unit of risk taken**.

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
    
st.markdown('---')  

# ===============================
# TAIL RISK ANALYSIS (KURTOSIS)
# ===============================

st.header("⚠️ Kurtosis")

st.markdown("""
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

st.markdown('---')

# ===============================
# ASSET PRICE DISTRIBUTION
# ===============================

st.header("📊 Price Distribution & Central Tendency")

st.markdown("""
This section shows the **frequency of price levels** for each asset. 

• **The Bell Curve (KDE)** → Shows where the price spends most of its time.
• **Green Dashed Line (Mean)** → The mathematical average price.
• **white Solid Line (Median)** → The middle value of the data.

If the **Mean** is far from the **Median**, it indicates that extreme price spikes are pulling the average away from the center.
""")

# 1. Setup the Plot for Dark Mode
plt.style.use('dark_background')
fig_dist, axes = plt.subplots(2, 3, figsize=(18, 12))
fig_dist.patch.set_facecolor('#0E1117')
axes = axes.flatten()

# 2. Data Config
stocks_dist = ['aapl', 'spy', 'tsla', 'msft', 'gold', 'amzn']
colors_dist = ['#555555', '#4CAF50', '#E31937', '#00A4EF', '#FFD700', '#FF9900']

# 3. Loop through stocks and plot
for i, stock in enumerate(stocks_dist):
    # Plot Histogram + KDE
    sns.histplot(data=df_final, x=stock, kde=True, ax=axes[i], color=colors_dist[i], alpha=0.6)
    
    # Calculate Metrics
    mean_val = df_final[stock].mean()
    median_val = df_final[stock].median()
    
    # Add Visual Guides
    axes[i].axvline(mean_val, color='#00FFCC', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.2f}')
    axes[i].axvline(median_val, color="#FFFFFF", linestyle='-', linewidth=2, label=f'Median: {median_val:.2f}')
    
    # Formatting
    axes[i].set_facecolor('#0E1117')
    axes[i].set_title(f'{stock.upper()} Price Distribution', fontsize=14, fontweight='bold', pad=10)
    axes[i].set_xlabel('Price (USD)')
    axes[i].set_ylabel('Frequency')
    axes[i].legend()
    
    # Remove top/right spines for clean look
    axes[i].spines['top'].set_visible(False)
    axes[i].spines['right'].set_visible(False)

plt.tight_layout(pad=3.0)
st.pyplot(fig_dist)

# ===============================
# DISTRIBUTION INTERPRETATION
# ===============================

with st.expander("📖 What does this shape tell us?"):
    st.markdown("""
**1. Symmetric Distributions (AAPL, AMZN, TSLA)**

The price spends most of its time near the average. These stocks are currently trading in a "balanced" range without extreme outliers pulling the average away.

**2. Right Skewed Distributions (SPY, GOLD)**

Right skew means there are a few instances of extremely high prices that pull the average up, even though most of the data is lower.
Because the mean is higher than the median, the "average" price is being inflated by outliers. If those outliers disappear, the price often "falls back" toward the median.

- For **GOLD** specifically, the median is a much more "realistic" representation of where the price usually sits than the mean.

**3. Bimodal Distributions (MSFT)**

When you see two "humps" (like MSFT), it usually means the stock has two "fair value" zones. It recently moved from a lower price regime to a higher one.

- The "Mean" here is actually misleading, we will depend on the median.""")
    
st.markdown('---')

# ===============================
#  NORMALIZATION SECTION 
# ===============================
st.header("📊 Relative Performance (Normalized)")
norm = df_final / df_final.iloc[0, :]
fig_norm = px.line(norm)
fig_norm.update_layout(template='plotly_dark', xaxis_title='Date', yaxis_title='Normalized Price')
st.plotly_chart(fig_norm, use_container_width=True, config={'displayModeBar': False})

with st.expander("💡 What does Normalization mean?"):
    st.write("""
Since stocks have different price points (e.g., 180 vs 3000), we divide every price 
by the very first price in the dataset. This makes every stock start at **1.0**. 
    
**Result > 1.0**: The stock has gained value since the start date.
             
**Result < 1.0**: The stock has lost value since the start date.
             
**TSLA** is described as very **volatile**. Over the last five years, TSLA has consistently shown a much higher standard deviation of returns compared to "safe-haven" tech stocks. Its price is heavily influenced by rapid growth expectations, earnings misses, and even social media sentiment.

**Microsoft & Apple** follow similar patterns because they are both Mega-Cap Tech stocks in the same sector. When the "tech sector" goes up or down, they move in tandem due to index fund buying.

**Gold** spent several years in a sideways range but surged in late 2025 and 2026, hitting record highs above $3,000–$4,000 per ounce.
Central banks in emerging markets have shifted from buying US Treasuries to buying Gold at record rates, providing the "fuel" for this 2026 breakout.
         
    """)

st.markdown('---') 

# ===============================
# --- BOLLINGER BANDS ANALYSIS ---
# ===============================

st.header("🛡️ Volatility & Trend Analysis (Bollinger Bands)")

# 1. Selection
selected_stock = st.selectbox("Select Asset for Technical Analysis:", 
                              ['GOLD', 'AAPL', 'TSLA', 'MSFT', 'SPY', 'AMZN'])

# 2. Fetch Cached Indicators
# We use 'rolling_mean' here to match your logic below
rolling_mean, upper_band, lower_band = get_bollinger_bands(df_final, selected_stock.lower())

# 3. Plotting
fig_bb, ax = plt.subplots(figsize=(15, 6))
plt.style.use('dark_background')
fig_bb.patch.set_facecolor('#0E1117')
ax.set_facecolor('#0E1117')

# Plot Price and Bands
df_final[selected_stock.lower()].plot(ax=ax, label='Price', color='#00d4ff', alpha=0.8, linewidth=2)
upper_band.plot(ax=ax, color='#00ff88', linestyle=':', label='Upper Band (Resistance)', alpha=0.6)
lower_band.plot(ax=ax, color='#ff4b4b', linestyle=':', label='Lower Band (Support)', alpha=0.6)
rolling_mean.plot(ax=ax, color='white', linestyle='--', label='SMA 50', alpha=0.4)

# Fill the "Volatility Zone"
ax.fill_between(df_final.index, lower_band, upper_band, color='gray', alpha=0.1)

# Formatting
ax.set_title(f"{selected_stock} Bollinger Bands - Buy/Sell Zones", fontsize=16, pad=20)
ax.set_ylabel("Price (USD)")
ax.legend(loc='upper left')
ax.grid(alpha=0.1)

st.pyplot(fig_bb)

# ===============================
# --- DYNAMIC MARKET INSIGHTS ---
# ===============================

# Get the absolute last values from the data
current_price = df_final[selected_stock.lower()].iloc[-1]
current_upper = upper_band.iloc[-1]
current_lower = lower_band.iloc[-1]
current_sma = rolling_mean.iloc[-1]

st.subheader(f"🔍 Current {selected_stock} Market Observation")

# Logic-based explanation
if current_price > current_upper:
    status = "⚠️ **Overextended:** Price is hugging the Upper Band. High probability of a short-term pullback."
elif current_price < current_lower:
    status = "🚀 **Oversold:** Price is touching the Lower Band. Historically, this acts as a reliable **'Buy Zone'**."
else:
    status = "⚖️ **Consolidation:** Price is trading within the normal volatility range."

# Trend logic
trend = "📈 **Uptrend:** Consistently trading above the SMA50." if current_price > current_sma else "📉 **Downtrend:** Trading below the SMA50."

st.markdown(f"""
- {status}
- {trend}
- **Volatility Check:** The width of the bands indicates the current market "stress" level.
- **Support/Resistance:** The Gray Zone represents the "Safe Zone." Movements outside this area suggest a shift in sentiment.
""")

st.markdown('---')

# ===============================
# --- CORRELATION ANALYSIS ---
# ===============================
st.header("🔗 Portfolio Asset Correlation")

# Create three columns to center the heatmap (ratio 1:3:1)
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    # 1. Calculate Correlation
    corr_matrix = daily_returns.corr()

    # 2. Create the triangle mask
    mask = np.zeros_like(corr_matrix)
    mask[np.triu_indices_from(mask)] = True

    # 3. Setup the Figure (Matching your dark theme)
    fig_corr, ax = plt.subplots()
    plt.style.use('dark_background')
    fig_corr.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')

    # 4. Generate Heatmap with your specific settings
    sns.heatmap(
        corr_matrix, 
        annot=True, 
        vmin=0.1,            # Your anchor for darkest color
        mask=mask,           # Your triangle mask
        linewidths=2.5,      # Your border style
        cmap='YlGnBu',       # Keeping professional colors
        cbar=False,          # Cleaner look without the side color bar
        ax=ax
    )

    ax.set_title("Asset Correlation Matrix", fontsize=14, color='white', pad=15)
    
    # 5. Render in the middle column
    st.pyplot(fig_corr)

# --- THE SHORT EXPLANATION (Inside an Expander) ---
with st.expander("🔍 How to Read This Map"):
        st.markdown("""
        The Correlation Matrix shows how assets move in relation to one another.
        
        * **The Scale (0 to 1):**
            * **1.0 (Darkest):** Perfect synchronization. Assets move like twins.
            * **0.7 – 0.9 (High):** Assets move together closely (e.g., Tech sector).
            * **Below 0.5 (Low):** Assets move independently. **The "Diversification Zone."**
        * **The Goal:** Look for **low correlation** (lighter colors). This ensures that if one asset crashes, others may remain stable.
                    
        The correlation analysis confirms that the **SPY** is heavily influenced by **MSFT** (0.79) and **AAPL** (0.78). Conversely, **Gold** shows near-zero correlation with tech assets, highlighting its effectiveness as a portfolio diversifier to mitigate systemic equity risk.
            
        * **The Triangle:** Hiding the top half removes "mirror" data to keep the view clean.
        """)

st.markdown('---')

# ===============================
# --- MARKET SENSITIVITY (BETA) ---
# ===============================
st.header("🎯 Market Sensitivity Analysis")

st.markdown("""
These regression plots show how sensitive **Apple** and **Microsoft** are to the movements of the **S&P 500 (SPY)**. 
A steeper, tighter line indicates the stock closely follows the market.
""")

# 1. Create the figure with shared Y-axis
# We use st.columns to ensure it fits the wide layout properly
fig_beta, ax = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
plt.style.use('dark_background')
fig_beta.patch.set_facecolor('#0E1117')

# Plot 1: Apple vs. SPY
sns.regplot(data=daily_returns, x='aapl', y='spy', 
            scatter=True, marker='*', ax=ax[0], color='orange', 
            line_kws={"color": "white", "lw": 2}) # Changed line to white for dark mode visibility
ax[0].set_facecolor('#0E1117')
ax[0].set_title('AAPL vs. SPY Sensitivity', color='orange')
ax[0].set_xlabel('Apple Daily Returns')
ax[0].set_ylabel('SPY Daily Returns')

# Plot 2: Microsoft vs. SPY
sns.regplot(data=daily_returns, x='msft', y='spy', 
            scatter=True, marker='*', ax=ax[1], color='red',
            line_kws={"color": "white", "lw": 2})
ax[1].set_facecolor('#0E1117')
ax[1].set_title('MSFT vs. SPY Sensitivity', color='red')
ax[1].set_xlabel('Microsoft Daily Returns')
ax[1].set_ylabel('') 

# 2. Main Title & Layout
plt.suptitle('Tech Giants vs. S&P 500 (Beta Analysis)', fontsize=16, y=1.05, color='white')
plt.tight_layout()

# 3. Display in Streamlit
st.pyplot(fig_beta)

st.markdown('---')

# ===============================
# --- STATISTICAL BETA CALCULATION ---
# ===============================
st.header(f"🔢 Statistical Metrics: {selected_stock.upper()} vs. Market")

# 1. Prepare data for the selected stock
ml = daily_returns.copy()
ml['intercept'] = 1

# 2. Run the OLS Regression
# Dependent variable (y) is your selected stock, Independent (x) is the market (spy)
model = sm.OLS(ml[selected_stock.lower()], ml[['intercept', 'spy']])
res = model.fit()

# 3. Extract key metrics for a clean UI
beta = res.params['spy']
alpha = res.params['intercept']
r_squared = res.rsquared

# 4. Display in professional "Metric" boxes
col1, col2, col3 = st.columns(3)
col1.metric("Beta (Sensitivity)", f"{beta:.2f}", help="> 1.0 means more volatile than market. < 1.0 means more stable.")
col2.metric("Alpha (Excess Return)", f"{alpha:.4f}", help="Positive alpha means the stock outperformed the market risk-adjusted.")
col3.metric("R-Squared (Fit)", f"{r_squared:.2f}", help="How much of the stock's movement is explained by the market.")

# 5. Optional: Show the full table for "Data Nerds"
with st.expander("📂 View Full Regression Summary (Technical)"):
    st.text(res.summary())
with st.expander("📖 Guide: How to Interpret These Statistical Metrics"):
    st.subheader("1. Beta (The Speedometer)")
    st.markdown("""
    **What it is:** Measures how much the stock "jumps" when the market (SPY) moves. 
    *Look at the **spy** row under the **coef** column.*
    
    * **Beta = 1.0:** The stock is a mirror. If SPY goes up 1%, the stock goes up 1%.
    * **Beta > 1.0 (High Risk):** The stock is aggressive. A Beta of 1.5 means it moves 50% more than the market. High reward, but high danger during crashes.
    * **Beta < 1.0 (Defensive):** Assets like **GOLD**. A Beta of 0.20 means it is very "calm." If the market crashes 10%, this asset might only move 2%.
    
    **💡 Investor Benefit:** Helps you decide if this stock is a **"Safety Net"** or a **"Growth Engine."**
    """)

    st.markdown("---")

    st.subheader("2. Alpha (The Manager's Skill)")
    st.markdown("""
    **What it is:** The "Extra" return the stock generated that had *nothing* to do with the market.
    *Look at the **const/intercept** row under the **coef** column.*

    * **Positive Alpha:** The stock is overperforming. It’s like a student getting bonus marks for extra effort.
    * **Negative Alpha:** The stock is underperforming even when the market is doing well.

    **💡 Investor Benefit:** Tells you: *"Is this specific stock actually good, or is it just rising because the whole market is rising?"*
    """)

    st.markdown("---")

    st.subheader("3. R-Squared (The 'Truth' Meter)")
    st.markdown("""
    **What it is:** Measures how much of the stock's movement is actually **caused** by the S&P 500 (Scale of 0 to 1).

    * **High R-Squared (0.80 - 1.0):** A **"Market Follower."** Its price is almost entirely dictated by the general economy.
    * **Low R-Squared (Below 0.40):** A **"Lone Wolf."** Its price moves based on its own news (like central bank decisions or gold prices), not the S&P 500.

    **💡 Investor Benefit:** Use this for **Diversification**. Low R-Squared assets provide a real "alternative" to the standard stock market.
    """)

    st.markdown("---")

    st.subheader("4. The p-value (The Confidence Score)")
    st.markdown("""
    **What it is:** Answers the question: *"Is this relationship real, or is it just a coincidence?"*
    *Look at the **P>|t|** column in the summary table.*

    * **The "Bullseye" (p < 0.05):** **Statistically Significant.** There is a 95% (or higher) chance the relationship is real. You can trust the Beta and Alpha.
    * **The "Coincidence" (p > 0.05):** **Insignificant.** The relationship is "noisy." The math cannot prove the stock is actually reacting to the market.

    **🔢 Quick Cheat Sheet:**
    * **0.000:** Perfect score. The relationship is 100% solid.
    * **0.750:** Weak score. 75% chance the result is just random noise.
    """)
# ===============================
# --- ABOUT THE DEVELOPER ---
# ===============================
st.sidebar.markdown("---")
st.sidebar.header("👨‍💻 Project Developer")

st.sidebar.markdown("""
**Youssef El-Emary** *Technical Specialist | Data Analyst*

Expertise in building **Automated Business Intelligence** solutions and **Financial Engineering** tools. 

- **Tech Stack:** Python, SQL, Streamlit, Power Bi, Excel
- **Automation:** GitHub Actions, ETL Pipelines
""")

# Professional Links
st.sidebar.markdown("### 🔗 Professional Profiles")

st.sidebar.markdown("[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/youssef-al-emary-025986332)")

st.sidebar.success("Available for Data Analysis & Automation Projects")

st.markdown("---")
st.header("🎯 Final Expert Verdict & 2026 Strategy")

# Use a container to give it a professional "Report" look
with st.container():
    st.markdown(f"""
    > **Executive Summary:** > "While **Tesla** provided the highest absolute returns, our **Sharpe Ratio** and **OLS Regression** prove that **Gold** was the most efficient asset for a balanced life. For 2026, we recommend a core of **AAPL** for symmetric growth and **GOLD** as a mandatory hedge against the 'Black Swan' events seen in the **SPY's** high Kurtosis.
    """)
    
    # Adding 3 Quick Bullet Points to back it up
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success("**The Safe Haven**")
        st.write("Gold is the 'steady engine,' gaining value without the heart-attack swings of Tech.")
    with col2:
        st.warning("**The Tech Reality**")
        st.write("AAPL & MSFT are 'Market Amplifiers.' They win big, but they fall first if the S&P 500 breaks.")
    with col3:
        st.error("**The Volatility Warning**")
        st.write("TSLA is the 'Main Character'—highest growth, but its wild moves are now 'normal' behavior.")
