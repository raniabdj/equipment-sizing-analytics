-- Q2: Rank consultants by sizing accuracy, and show each one's rank within
-- their own firm as well as overall.
-- Demonstrates: window functions (RANK, PARTITION BY), multiple ranking scopes

WITH consultant_accuracy AS (
    SELECT
        c.consultant_id,
        c.consultant_name,
        c.firm,
        c.years_experience,
        COUNT(*) AS project_count,
        ROUND(AVG(ABS(p.specified_capacity_kw - p.measured_peak_demand_kw)
                  / p.measured_peak_demand_kw * 100.0), 1) AS avg_abs_error_pct
    FROM sizing_projects p
    JOIN consultants c ON c.consultant_id = p.consultant_id
    GROUP BY c.consultant_id, c.consultant_name, c.firm, c.years_experience
    HAVING COUNT(*) >= 5   -- only consultants with a meaningful sample size
)
SELECT
    consultant_name,
    firm,
    years_experience,
    project_count,
    avg_abs_error_pct,
    RANK() OVER (ORDER BY avg_abs_error_pct ASC) AS overall_rank,
    RANK() OVER (PARTITION BY firm ORDER BY avg_abs_error_pct ASC) AS rank_within_firm
FROM consultant_accuracy
ORDER BY overall_rank;
