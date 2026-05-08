
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# --------------------------------------------------
# Page setup
# --------------------------------------------------

st.set_page_config(
    page_title="Infectious Disease Surveillance Dashboard",
    page_icon="🦠",
    layout="wide"
)

st.title("🦠 Infectious Disease Surveillance Dashboard")

st.markdown(
    """
    This dashboard analyzes reported weekly cases of infectious diseases in California using CDC NNDSS surveillance data.
    The goal is to connect microbial biology, public health, and data science by exploring year-over-year trends,
    rolling averages, and unusually high reporting weeks.
    """
)

# --------------------------------------------------
# Load data locally
# --------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("california_nndss_data.csv")

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    df.columns = df.columns.str.replace("_", "", regex=False)

    return df

df = load_data()

# --------------------------------------------------
# Column setup
# --------------------------------------------------

state_col = "states"
year_col = "year"
week_col = "week"
disease_col = "label"
cases_col = "m1"

df[year_col] = pd.to_numeric(df[year_col], errors="coerce")
df[week_col] = pd.to_numeric(df[week_col], errors="coerce")

df[cases_col] = (
    df[cases_col]
    .astype(str)
    .str.replace(",", "", regex=False)
)

df[cases_col] = pd.to_numeric(df[cases_col], errors="coerce")

df = df.dropna(subset=[year_col, week_col, disease_col, cases_col])

# --------------------------------------------------
# Sidebar filters
# --------------------------------------------------

st.sidebar.header("Dashboard Filters")

available_diseases = sorted(
    df[disease_col]
    .dropna()
    .unique()
)

default_disease = "Campylobacteriosis"

if default_disease in available_diseases:
    default_index = available_diseases.index(default_disease)
else:
    default_index = 0

selected_disease = st.sidebar.selectbox(
    "Select disease",
    available_diseases,
    index=default_index
)

disease_df = df[df[disease_col] == selected_disease].copy()
disease_df = disease_df.sort_values([year_col, week_col])

available_years = sorted(disease_df[year_col].dropna().unique().astype(int))

selected_years = st.sidebar.multiselect(
    "Select years to compare",
    available_years,
    default=available_years[-2:] if len(available_years) >= 2 else available_years
)

rolling_window = st.sidebar.slider(
    "Rolling average window",
    min_value=2,
    max_value=8,
    value=4,
    step=1
)

# --------------------------------------------------
# Dynamic heading
# --------------------------------------------------

st.subheader(f"{selected_disease} Trends in California Using CDC NNDSS Weekly Data")

st.markdown(
    f"""
    This dashboard is currently displaying reported weekly cases of **{selected_disease}** in California.
    Use the sidebar filters to compare available years and adjust the rolling average window.
    """
)

if len(selected_years) == 0:
    st.warning("Please select at least one year to display the dashboard.")
    st.stop()

filtered_df = disease_df[disease_df[year_col].isin(selected_years)].copy()

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# --------------------------------------------------
# Summary metrics
# --------------------------------------------------

yearly_summary = filtered_df.groupby(year_col)[cases_col].agg(
    total_reported_cases="sum",
    average_weekly_cases="mean",
    median_weekly_cases="median",
    max_weekly_cases="max",
    min_weekly_cases="min",
    weeks_reported="count"
).reset_index()

yearly_summary["total_reported_cases"] = yearly_summary["total_reported_cases"].round(0).astype(int)
yearly_summary["average_weekly_cases"] = yearly_summary["average_weekly_cases"].round(2)
yearly_summary["median_weekly_cases"] = yearly_summary["median_weekly_cases"].round(2)
yearly_summary["max_weekly_cases"] = yearly_summary["max_weekly_cases"].round(0).astype(int)
yearly_summary["min_weekly_cases"] = yearly_summary["min_weekly_cases"].round(0).astype(int)

st.markdown("## Key Summary Metrics")

total_cases_all = yearly_summary["total_reported_cases"].sum()
avg_weekly_all = filtered_df[cases_col].mean()
max_cases_all = filtered_df[cases_col].max()

col1, col2, col3 = st.columns(3)

col1.metric("Total Reported Cases", f"{total_cases_all:,}")
col2.metric("Average Weekly Cases", f"{avg_weekly_all:.2f}")
col3.metric("Highest Weekly Count", f"{int(max_cases_all):,}")

# --------------------------------------------------
# Weekly trend chart
# --------------------------------------------------

st.markdown("## Weekly Case Trends")

fig, ax = plt.subplots(figsize=(12, 6))

for year in selected_years:
    year_data = disease_df[disease_df[year_col] == year].copy()
    year_data = year_data.sort_values(week_col)
    year_data["rolling_average"] = year_data[cases_col].rolling(window=rolling_window).mean()

    ax.plot(
        year_data[week_col],
        year_data[cases_col],
        marker="o",
        alpha=0.30,
        label=f"{year} weekly cases"
    )

    ax.plot(
        year_data[week_col],
        year_data["rolling_average"],
        linewidth=3,
        label=f"{year} {rolling_window}-week rolling average"
    )

ax.set_title(f"Weekly Reported Cases of {selected_disease} in California")
ax.set_xlabel("MMWR Week")
ax.set_ylabel("Reported Current Week Cases")
ax.grid(True)
ax.legend()

st.pyplot(fig)
plt.close(fig)

st.markdown(
    """
    The lighter lines show week-to-week reported cases, while the thicker lines show the rolling average.
    The rolling average helps reduce short-term reporting noise and makes broader seasonal patterns easier to see.
    """
)

# --------------------------------------------------
# Yearly summary table
# --------------------------------------------------

st.markdown("## Yearly Summary Table")
st.dataframe(yearly_summary, use_container_width=True)

# --------------------------------------------------
# Total cases by year
# --------------------------------------------------

st.markdown("## Total Reported Cases by Year")

fig2, ax2 = plt.subplots(figsize=(10, 5))

bars = ax2.bar(
    yearly_summary[year_col],
    yearly_summary["total_reported_cases"]
)

ax2.set_title(f"Total Reported {selected_disease} Cases in California")
ax2.set_xlabel("Year")
ax2.set_ylabel("Total Reported Cases")
ax2.grid(axis="y")

for bar in bars:
    height = bar.get_height()
    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{int(height):,}",
        ha="center",
        va="bottom"
    )

st.pyplot(fig2)
plt.close(fig2)

# --------------------------------------------------
# High reporting weeks
# --------------------------------------------------

st.markdown("## Unusually High Reporting Weeks")

analysis_df = disease_df.copy()

if analysis_df[cases_col].std() == 0:
    high_weeks_display = pd.DataFrame()
else:
    analysis_df["z_score"] = (
        analysis_df[cases_col] - analysis_df[cases_col].mean()
    ) / analysis_df[cases_col].std()

    high_weeks = analysis_df[
        (analysis_df["z_score"] > 2) &
        (analysis_df[year_col].isin(selected_years))
    ].copy()

    high_weeks_display = high_weeks[
        [year_col, week_col, disease_col, cases_col, "z_score"]
    ].sort_values("z_score", ascending=False)

    high_weeks_display["z_score"] = high_weeks_display["z_score"].round(2)

if high_weeks_display.empty:
    st.info("No unusually high reporting weeks were detected for the selected year range using a z-score > 2 threshold.")
else:
    st.dataframe(high_weeks_display, use_container_width=True)

st.markdown(
    """
    Weeks were flagged as unusually high if their reported case count was more than two standard deviations above the overall mean.
    This is an exploratory signal, not confirmation of an outbreak.
    """
)

# --------------------------------------------------
# Methods and limitations
# --------------------------------------------------

st.markdown("## Methods")

st.markdown(
    """
    This project uses CDC NNDSS weekly surveillance data to analyze reported infectious disease trends in California.
    The dataset was filtered by disease label, year, and reporting area. Weekly case counts were converted into numeric values,
    then analyzed using Python, pandas, and matplotlib.

    A rolling average was calculated to smooth short-term variation in weekly reporting. Yearly summaries were generated using
    total reported cases, average weekly reported cases, median weekly reported cases, maximum weekly case counts, and minimum weekly case counts.
    Unusually high reporting weeks were flagged using a z-score threshold greater than 2.
    """
)

st.markdown("## Limitations")

st.markdown(
    """
    These data represent reported surveillance counts, not finalized population-adjusted incidence rates.
    Trends may be affected by reporting delays, changes in testing behavior, healthcare access, and public health reporting practices.
    The dashboard does not adjust for population size, demographics, seasonality, or county-level differences.
    Flagged high-reporting weeks should not be interpreted as confirmed outbreaks without additional epidemiological context.
    """
)
