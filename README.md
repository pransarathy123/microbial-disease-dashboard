# Infectious Disease Surveillance Dashboard

An interactive public health data science dashboard analyzing reported infectious disease trends in California using CDC NNDSS weekly surveillance data.

## Project Overview

This project uses Python, pandas, matplotlib, and Streamlit to explore weekly reported cases of infectious diseases in California. The dashboard allows users to select a disease, compare available years, adjust the rolling average window, view yearly summary metrics, and identify unusually high reporting weeks using a z-score threshold.

The project was built to connect microbial biology, public health, and data science through real-world disease surveillance data.

## Features

- Interactive disease selector
- Multi-year comparison
- Adjustable 2–8 week rolling average
- Weekly case trend visualization
- Yearly summary table
- Total reported cases by year
- Unusually high reporting weeks flagged using z-scores
- Methods and limitations section

## Tools Used

- Python
- pandas
- matplotlib
- Streamlit
- CDC NNDSS weekly surveillance data

## Methods

The dataset was filtered to California and cleaned using pandas. Weekly case counts were converted into numeric values and grouped by disease, year, and MMWR week. A rolling average was calculated to smooth week-to-week reporting variation. Yearly summary metrics were generated using total reported cases, average weekly reported cases, median weekly reported cases, maximum weekly counts, and minimum weekly counts.

Unusually high reporting weeks were flagged using a z-score threshold greater than 2. This threshold was used as an exploratory signal and should not be interpreted as confirmation of an outbreak.

## Limitations

These data represent reported surveillance counts, not finalized population-adjusted incidence rates. Trends may be affected by reporting delays, testing behavior, healthcare access, and public health reporting practices. The dashboard does not adjust for population size, county-level differences, demographics, or confirmed outbreak investigations.

## Example Use Case

A user can select Campylobacteriosis, compare 2023 and 2024, adjust the rolling average window, and examine whether mid-year increases appear consistently across years.

## Resume Bullet

Built an interactive infectious disease surveillance dashboard using CDC NNDSS weekly data to analyze California disease trends; cleaned and analyzed public health case reports with pandas, visualized year-over-year patterns with matplotlib, and flagged unusually high reporting weeks using z-score thresholds.
