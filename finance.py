
import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

# =====================================================
# 1. APPLICATION CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="S&P 500 Financial Analysis",
    page_icon="📈",
    layout="wide"
)

st.title("📈 S&P 500 Financial Data Analysis")

st.markdown("""
### Stock Market Performance and Statistical Analysis

This application analyzes the historical performance of the
S&P 500 index and calculates the relative frequency of
daily upward and downward movements.
""")

st.divider()

# =====================================================
# 2. SIDEBAR PARAMETERS
# =====================================================

st.sidebar.title("⚙️ Analysis Settings")

ticker = st.sidebar.text_input(
    "Stock Market Ticker",
    value="^GSPC"
)

start_date = st.sidebar.date_input(
    "Start Date",
    value=pd.to_datetime("2020-01-01")
)

end_date = st.sidebar.date_input(
    "End Date",
    value=pd.to_datetime("2020-04-01")
)

run_analysis = st.sidebar.button(
    "🚀 Run Analysis",
    use_container_width=True
)

# =====================================================
# 3. DATA DOWNLOAD AND ANALYSIS
# =====================================================

if run_analysis:

    if start_date >= end_date:
        st.error("The end date must be later than the start date.")
        st.stop()

    try:

        with st.spinner("Downloading S&P 500 financial data..."):

            sp500 = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                auto_adjust=False,
                progress=False
            )

        if sp500.empty:
            st.error("No data found. Please check the ticker or dates.")
            st.stop()

        # Handle MultiIndex columns
        if isinstance(sp500.columns, pd.MultiIndex):
            sp500.columns = sp500.columns.get_level_values(0)

        if "Close" not in sp500.columns:
            st.error("Closing price data is unavailable.")
            st.stop()

        sp500 = sp500.dropna(subset=["Close"]).copy()

        # =================================================
        # 4. DAILY PRICE CHANGE
        # =================================================

        sp500["Daily Change"] = sp500["Close"].diff()

        sp500["Daily Percentage Change"] = (
            sp500["Close"].pct_change() * 100
        )

        daily_changes = sp500["Daily Change"].dropna()

        total_days = len(daily_changes)

        if total_days == 0:
            st.error("Insufficient data for statistical analysis.")
            st.stop()

        up_days = (daily_changes > 0).sum()

        down_days = (daily_changes < 0).sum()

        unchanged_days = (daily_changes == 0).sum()

        up_frequency = up_days / total_days

        down_frequency = down_days / total_days

        unchanged_frequency = unchanged_days / total_days

        # =================================================
        # 5. KEY PERFORMANCE INDICATORS
        # =================================================

        st.header("1. Key Performance Indicators")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Trading Observations",
            f"{total_days}"
        )

        col2.metric(
            "Up Days",
            f"{up_days}"
        )

        col3.metric(
            "Down Days",
            f"{down_days}"
        )

        col4.metric(
            "Unchanged Days",
            f"{unchanged_days}"
        )

        st.divider()

        # =================================================
        # 6. S&P 500 CLOSING PRICE
        # =================================================

        st.header("2. S&P 500 Performance")

        fig1, ax1 = plt.subplots(figsize=(12, 5))

        ax1.plot(
            sp500.index,
            sp500["Close"],
            label="S&P 500",
            color="blue",
            linewidth=2
        )

        ax1.set_title(
            "S&P 500 Performance (Jan - Mar 2020)"
        )

        ax1.set_xlabel("Date")

        ax1.set_ylabel("Closing Price (USD)")

        ax1.legend()

        ax1.grid(True, alpha=0.3)

        plt.xticks(rotation=45)

        plt.tight_layout()

        st.pyplot(fig1)

        plt.close(fig1)

        # =================================================
        # 7. DAILY PRICE CHANGES
        # =================================================

        st.header("3. Daily Price Changes")

        fig2, ax2 = plt.subplots(figsize=(12, 5))

        ax2.plot(
            sp500.index,
            sp500["Daily Change"],
            color="orange",
            label="Daily Change"
        )

        ax2.axhline(
            y=0,
            color="black",
            linestyle="--"
        )

        ax2.set_title(
            "Daily Changes in S&P 500 Closing Prices"
        )

        ax2.set_xlabel("Date")

        ax2.set_ylabel("Daily Change (USD)")

        ax2.legend()

        ax2.grid(True, alpha=0.3)

        plt.xticks(rotation=45)

        plt.tight_layout()

        st.pyplot(fig2)

        plt.close(fig2)

        # =================================================
        # 8. RELATIVE FREQUENCY BAR CHART
        # =================================================

        st.header("4. Relative Frequency Analysis")

        categories = [
            "Up Days",
            "Down Days",
            "Unchanged Days"
        ]

        frequencies = [
            up_frequency,
            down_frequency,
            unchanged_frequency
        ]

        fig3, ax3 = plt.subplots(figsize=(8, 5))

        bars = ax3.bar(
            categories,
            frequencies,
            color=["green", "red", "gray"]
        )

        ax3.set_title(
            "Relative Frequency of S&P 500 Daily Changes"
        )

        ax3.set_ylabel("Relative Frequency")

        ax3.set_ylim(0, 1)

        ax3.grid(
            axis="y",
            linestyle="--",
            alpha=0.7
        )

        for bar, freq in zip(bars, frequencies):

            ax3.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.02,
                f"{freq:.2f}",
                ha="center",
                va="bottom",
                fontsize=10
            )

        plt.tight_layout()

        st.pyplot(fig3)

        plt.close(fig3)

        # =================================================
        # 9. STATISTICAL SUMMARY
        # =================================================

        st.header("5. Statistical Summary")

        summary = pd.DataFrame({

            "Category": categories,

            "Number of Days": [
                up_days,
                down_days,
                unchanged_days
            ],

            "Relative Frequency": [
                up_frequency,
                down_frequency,
                unchanged_frequency
            ],

            "Percentage (%)": [
                up_frequency * 100,
                down_frequency * 100,
                unchanged_frequency * 100
            ]

        })

        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True
        )

        # =================================================
        # 10. HISTORICAL DATA
        # =================================================

        st.header("6. Historical Financial Data")

        with st.expander("View Complete Dataset"):

            st.dataframe(
                sp500,
                use_container_width=True
            )

        # =================================================
        # 11. DOWNLOAD CSV
        # =================================================

        csv_data = sp500.to_csv().encode("utf-8")

        st.download_button(
            label="📥 Download Financial Data (CSV)",
            data=csv_data,
            file_name="SP500_Financial_Analysis.csv",
            mime="text/csv"
        )

        # =================================================
        # 12. INTERPRETATION
        # =================================================

        st.divider()

        st.header("7. Statistical Interpretation")

        st.write(
            f"During the selected period, the S&P 500 recorded "
            f"{up_days} upward trading days, "
            f"{down_days} downward trading days and "
            f"{unchanged_days} unchanged trading days."
        )

        st.write(
            f"The relative frequency of upward movements was "
            f"{up_frequency:.2%}."
        )

        st.write(
            f"The relative frequency of downward movements was "
            f"{down_frequency:.2%}."
        )

        st.success("Financial analysis completed successfully!")

    except Exception as e:

        st.error(f"An error occurred: {str(e)}")

else:

    st.info(
        "Choose your analysis parameters in the sidebar "
        "and click on Run Analysis."
    )

    st.subheader("About this application")

    st.write(
        "This application uses Yahoo Finance data to study "
        "the historical movements of the S&P 500 index."
    )

# =====================================================
# 13. FOOTER
# =====================================================

st.divider()

st.caption(
    "S&P 500 Financial Data Analysis | "
    "Developed with Python, Streamlit, Pandas and Matplotlib."
)
