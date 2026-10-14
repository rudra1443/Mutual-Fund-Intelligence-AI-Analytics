Mutual Fund Intelligence — Performance, Return & Risk Analytics

An end-to-end financial data analytics project focused on mutual fund NAV trends, returns, volatility, and comparative analysis using Python, SQL, and Power BI.

Project Overview

Mutual Fund Intelligence transforms historical mutual fund Net Asset Value (NAV) data into an interactive analytics dashboard. The project explores fund performance over time, compares Asset Management Companies (AMCs), and helps identify data-quality issues that may affect financial conclusions.

Objectives

- Analyze historical NAV trends.
- Calculate and examine daily and monthly returns.
- Explore annualized volatility and other risk indicators.
- Compare AMC and scheme-level data.
- Identify missing, duplicate, or inconsistent records.
- Present insights through interactive Power BI visualizations.

Technology Stack

- Python: Data preparation, cleaning, and quality checks.
- MariaDB / SQL: Data storage, querying, and business analysis.
- Power BI: Interactive dashboards, KPI cards, line charts, AMC comparisons, donut chart, treemap, and monthly-return matrix.
- AI-assisted workflow: Used AI tools to support analysis planning, formula troubleshooting, documentation, and visualization ideas. AI-generated outputs are not treated as verified financial facts.

Project Workflow

1. Collect historical NAV data from AMFI.
2. Prepare and validate the dataset using Python.
3. Load structured data into MariaDB.
4. Analyze the data with SQL.
5. Build DAX measures and an interactive Power BI report.
6. Review data quality and validate financial calculations before publishing conclusions.

Dashboard Features

- Latest NAV KPI
- Daily and monthly return indicators
- Annualized volatility
- NAV trend over time
- AMC comparison
- Monthly-return matrix / heatmap
- Donut chart and treemap
- Interactive filtering and exploration

Data Source

Historical NAV data: "Association of Mutual Funds in India (AMFI)" (https://www.amfiindia.com/net-asset-value/nav-download)

Data coverage and fund availability depend on the source files collected for this project. The repository should document the exact period and schemes included in the final validated dataset.

Repository Structure

- "powerbi/" — Power BI report
- "python/" — Python preparation and audit scripts
- "sql/" — SQL analysis queries
- "screenshots/" — Dashboard images
- "docs/" — Methodology and validation notes

Only include folders and files that are actually present in the repository.

Data Quality & Limitations

NAV levels alone should not be used to rank investment performance across different funds. Comparisons should use consistent periods and suitable return measures.

Return and risk metrics must be validated for scheme identity, date ordering, duplicate records, missing values, and calculation assumptions. Any unresolved data-quality issues should be disclosed before presenting results as investment insights.

This project is for educational and analytical purposes only. It is not investment advice or a recommendation to buy or sell mutual funds.

Future Improvements

- Add a validated common-period growth comparison.
- Improve automated data-quality checks.
- Add a reproducible refresh pipeline.
- Integrate a real AI service for grounded insight generation, with appropriate validation and disclosure.
- Improve dashboard navigation and report documentation.

Author

Rudra Singh Kushwah
Data Analytics | Python | SQL | Power BI | AI-assisted Analytics

Connect with me on LinkedIn and GitHub. 
www.linkedin.com/in/rudra-s-thakur-1579a72aa
