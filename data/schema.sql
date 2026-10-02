-- Equipment Sizing Analytics — schema
-- A synthetic dataset modeling building services equipment sizing projects:
-- consultants size HVAC/mechanical equipment for buildings, and we track
-- whether the equipment they specified was correctly sized, oversized, or
-- undersized relative to the building's actual measured demand.

CREATE TABLE buildings (
    building_id      INTEGER PRIMARY KEY,
    building_type    TEXT NOT NULL,      -- 'office', 'retail', 'residential', 'warehouse', 'healthcare'
    floor_area_sqm   REAL NOT NULL,
    region           TEXT NOT NULL,      -- UK region
    build_year       INTEGER NOT NULL
);

CREATE TABLE consultants (
    consultant_id    INTEGER PRIMARY KEY,
    consultant_name  TEXT NOT NULL,
    years_experience INTEGER NOT NULL,
    firm             TEXT NOT NULL
);

CREATE TABLE equipment_specs (
    equipment_id     INTEGER PRIMARY KEY,
    equipment_type   TEXT NOT NULL,      -- 'chiller', 'boiler', 'AHU', 'heat_pump'
    rated_capacity_kw REAL NOT NULL
);

CREATE TABLE sizing_projects (
    project_id         INTEGER PRIMARY KEY,
    building_id        INTEGER NOT NULL REFERENCES buildings(building_id),
    consultant_id       INTEGER NOT NULL REFERENCES consultants(consultant_id),
    equipment_id        INTEGER NOT NULL REFERENCES equipment_specs(equipment_id),
    project_date         TEXT NOT NULL,      -- ISO date
    specified_capacity_kw REAL NOT NULL,     -- what the consultant specified
    measured_peak_demand_kw REAL NOT NULL,   -- actual measured peak demand post-installation
    project_cost_gbp     REAL NOT NULL
);
