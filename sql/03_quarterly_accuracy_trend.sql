-- Q3: Is sizing accuracy improving over time? Quarterly trend with a
-- rolling 2-quarter moving average to smooth noise.
-- Demonstrates: date bucketing, window functions (moving average with
-- ROWS BETWEEN), ordering by a derived time period

WITH quarterly AS (
    SELECT
        strftime('%Y', project_date) || '-Q' ||
            ((CAST(strftime('%m', project_date) AS INTEGER) - 1) / 3 + 1) AS year_quarter,
        ROUND(AVG(ABS(specified_capacity_kw - measured_peak_demand_kw)
                  / measured_peak_demand_kw * 100.0), 1) AS avg_abs_error_pct,
        COUNT(*) AS project_count
    FROM sizing_projects
    GROUP BY year_quarter
)
SELECT
    year_quarter,
    project_count,
    avg_abs_error_pct,
    ROUND(AVG(avg_abs_error_pct) OVER (
        ORDER BY year_quarter
        ROWS BETWEEN 1 PRECEDING AND CURRENT ROW
    ), 1) AS rolling_2q_avg_error_pct
FROM quarterly
ORDER BY year_quarter;
