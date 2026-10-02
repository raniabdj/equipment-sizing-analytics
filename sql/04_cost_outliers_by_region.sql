-- Q4: Which regions have projects costing significantly more than their
-- region's median cost-per-kW? (Outlier detection using a subquery)
-- Demonstrates: correlated subquery, cost-per-unit derived metric, multi-table join

SELECT
    b.region,
    p.project_id,
    bl.building_type,
    ROUND(p.project_cost_gbp / p.specified_capacity_kw, 2) AS cost_per_kw,
    (
        SELECT ROUND(AVG(p2.project_cost_gbp / p2.specified_capacity_kw), 2)
        FROM sizing_projects p2
        JOIN buildings b2 ON b2.building_id = p2.building_id
        WHERE b2.region = b.region
    ) AS region_avg_cost_per_kw
FROM sizing_projects p
JOIN buildings b ON b.building_id = p.building_id
JOIN buildings bl ON bl.building_id = p.building_id
WHERE (p.project_cost_gbp / p.specified_capacity_kw) > (
    SELECT AVG(p3.project_cost_gbp / p3.specified_capacity_kw) * 1.3
    FROM sizing_projects p3
    JOIN buildings b3 ON b3.building_id = p3.building_id
    WHERE b3.region = b.region
)
ORDER BY cost_per_kw DESC
LIMIT 15;
