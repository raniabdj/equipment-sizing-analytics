-- Q1: What's the average oversizing rate by building type?
-- Demonstrates: CTE, aggregation, derived percentage calculation

WITH sizing_delta AS (
    SELECT
        p.project_id,
        b.building_type,
        p.specified_capacity_kw,
        p.measured_peak_demand_kw,
        (p.specified_capacity_kw - p.measured_peak_demand_kw) / p.measured_peak_demand_kw * 100.0
            AS oversizing_pct
    FROM sizing_projects p
    JOIN buildings b ON b.building_id = p.building_id
)
SELECT
    building_type,
    COUNT(*)                           AS project_count,
    ROUND(AVG(oversizing_pct), 1)      AS avg_oversizing_pct,
    ROUND(MIN(oversizing_pct), 1)      AS min_oversizing_pct,
    ROUND(MAX(oversizing_pct), 1)      AS max_oversizing_pct
FROM sizing_delta
GROUP BY building_type
ORDER BY avg_oversizing_pct DESC;
