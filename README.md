# Equipment Sizing Analytics

A SQL analytics project exploring a common building-services engineering question:
**how accurately do consultants size mechanical equipment (chillers, boilers, AHUs, heat
pumps) relative to a building's actual measured demand, and what patterns explain the
variance?**

Built with a synthetic dataset (400 sizing projects across 60 buildings, 12 consultants,
5 building types) and four analytical SQL queries covering CTEs, window functions,
correlated subqueries, and time-series bucketing.

## Why this project

Right-sizing decision support — helping building services consultants avoid over- or
under-specifying equipment — is a real problem domain I've worked in professionally. This
project is a self-built, from-scratch exploration of that problem space using entirely
synthetic data and generic, illustrative sizing logic (a simple kW-per-m² rule of thumb) —
**not** any company's proprietary methodology or real project data. It exists purely to
demonstrate SQL analytical technique and a small data pipeline, not to reproduce any real
client's work.

## Project structure

```
equipment-sizing-analytics/
├── data/
│   ├── schema.sql                  # table definitions
│   ├── generate_synthetic_data.py  # builds the SQLite database with fake data
│   └── extract_epc_buildings.py    # pulls REAL building data from the UK EPC Register
├── sql/
│   ├── 01_oversizing_rate_by_building_type.sql
│   ├── 02_consultant_accuracy_ranking.sql
│   ├── 03_quarterly_accuracy_trend.sql
│   └── 04_cost_outliers_by_region.sql
└── src/
    └── run_analysis.py             # runs all queries and prints results
```

## Real data: the UK EPC Register

The `buildings` table can be populated from the UK's
[Energy Performance Certificate Register](https://epc.opendatacommunities.org/) — a free,
public government open dataset covering the vast majority of UK properties, with real
floor areas, property types, and construction dates.

```bash
export EPC_API_KEY="your-bearer-token-here"   # free signup at the link above
cd data && python3 extract_epc_buildings.py --local-authority E08000012 --limit 500
```

The consultant/equipment-sizing layer (`generate_synthetic_data.py`) stays synthetic
regardless — no public dataset tracks how accurately consultants size mechanical
equipment, so that half is necessarily a demonstration construct. The real EPC data
replaces only the `buildings` table's floor areas and property types.

Parsing EPC's data surfaces real data-quality issues worth handling explicitly rather
than assuming clean input — e.g. `construction-age-band` arrives as `"1950-1966"`,
`"before 1900"`, or blank, not a single consistent format, and `total-floor-area` is
sometimes missing entirely.

## SQL techniques demonstrated

- **`01`** — CTE + `GROUP BY` aggregation: average oversizing rate by building type
- **`02`** — Window functions (`RANK() OVER (PARTITION BY ...)`): ranks consultants by
  sizing accuracy, both overall and within their firm
- **`03`** — Date bucketing + a rolling moving average (`ROWS BETWEEN ... PRECEDING`):
  is sizing accuracy improving quarter over quarter?
- **`04`** — Correlated subqueries: flags projects costing significantly more than their
  region's average cost-per-kW

## Running it

```bash
cd data && python3 generate_synthetic_data.py   # builds equipment_sizing.db
cd ../src && python3 run_analysis.py            # runs every query, prints results
```

No dependencies beyond Python's built-in `sqlite3` module — nothing to install.

## Sample finding (from the synthetic data)

Query `02` shows a believable (simulated) pattern: more experienced consultants tend to
size closer to actual demand. This relationship was built into the data generator on
purpose, to give the analytical queries something real to surface — it isn't a finding
from genuine industry data.

## Roadmap

- [ ] Deploy the database to Azure SQL Database (free tier) instead of local SQLite
- [ ] Add a small Power BI or web dashboard on top of the gold-layer query outputs
- [ ] Add dbt models instead of raw `.sql` files, for lineage and testing
