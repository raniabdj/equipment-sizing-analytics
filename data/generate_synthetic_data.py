"""
Generates a synthetic dataset for the Equipment Sizing Analytics project.

This is entirely made-up data for portfolio/demonstration purposes — no real
client data, formulas, or methodology from any company is used here. Sizing
"correctness" is simulated using simple randomised noise around a plausible
industry rule-of-thumb (kW per m² by building type), not a real proprietary
calculation method.
"""
import random
import sqlite3
import os
from datetime import date, timedelta

random.seed(42)  # reproducible output

DB_PATH = os.path.join(os.path.dirname(__file__), "equipment_sizing.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

BUILDING_TYPES = {
    # illustrative, publicly-known-style rule-of-thumb kW per m² — NOT a real
    # proprietary formula, just plausible figures for a synthetic dataset
    "office": 0.12,
    "retail": 0.15,
    "residential": 0.08,
    "warehouse": 0.05,
    "healthcare": 0.20,
}
REGIONS = ["North West", "North East", "Yorkshire", "Midlands", "London", "South West", "Scotland"]
EQUIPMENT_TYPES = ["chiller", "boiler", "AHU", "heat_pump"]
FIRMS = ["Beverston Engineering", "Northline Consulting", "Alder & Pryce", "Meridian Building Services", "Carrow Associates"]
FIRST_NAMES = ["Sam", "Priya", "Tom", "Aisha", "Ben", "Chloe", "Rav", "Erin", "Jak", "Nia"]
LAST_NAMES = ["Whitfield", "Okafor", "Marsh", "Dunmore", "Reilly", "Szymanski", "Haines", "Osei"]


def generate_buildings(n=60):
    buildings = []
    for i in range(1, n + 1):
        btype = random.choice(list(BUILDING_TYPES.keys()))
        buildings.append((
            i, btype,
            round(random.uniform(200, 15000), 1),
            random.choice(REGIONS),
            random.randint(1985, 2024),
        ))
    return buildings


def generate_consultants(n=12):
    consultants = []
    for i in range(1, n + 1):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        consultants.append((i, name, random.randint(1, 25), random.choice(FIRMS)))
    return consultants


def generate_equipment(n=20):
    equipment = []
    for i in range(1, n + 1):
        etype = random.choice(EQUIPMENT_TYPES)
        equipment.append((i, etype, round(random.uniform(20, 800), 1)))
    return equipment


def generate_projects(buildings, consultants, equipment, n=400):
    projects = []
    start = date(2021, 1, 1)
    for i in range(1, n + 1):
        b = random.choice(buildings)
        c = random.choice(consultants)
        e = random.choice(equipment)

        building_id, btype, floor_area, _, _ = b
        consultant_id = c[0]
        consultant_experience = c[2]
        equipment_id = e[0]

        true_demand = floor_area * BUILDING_TYPES[btype] * random.uniform(0.9, 1.1)

        # More experienced consultants size closer to true demand, on average —
        # this is a simulated relationship for the synthetic dataset, not a
        # finding from real data.
        skill_noise = max(0.05, 0.35 - (consultant_experience * 0.01))
        specified = true_demand * random.uniform(1 - skill_noise, 1 + skill_noise * 1.5)

        project_date = start + timedelta(days=random.randint(0, 1460))
        cost = round(specified * random.uniform(180, 420), 2)

        projects.append((
            i, building_id, consultant_id, equipment_id,
            project_date.isoformat(),
            round(specified, 2), round(true_demand, 2), cost,
        ))
    return projects


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())

    buildings = generate_buildings()
    consultants = generate_consultants()
    equipment = generate_equipment()
    projects = generate_projects(buildings, consultants, equipment)

    conn.executemany("INSERT INTO buildings VALUES (?,?,?,?,?)", buildings)
    conn.executemany("INSERT INTO consultants VALUES (?,?,?,?)", consultants)
    conn.executemany("INSERT INTO equipment_specs VALUES (?,?,?)", equipment)
    conn.executemany("INSERT INTO sizing_projects VALUES (?,?,?,?,?,?,?,?)", projects)
    conn.commit()
    conn.close()

    print(f"Generated {len(buildings)} buildings, {len(consultants)} consultants, "
          f"{len(equipment)} equipment specs, {len(projects)} sizing projects.")
    print(f"Database written to {DB_PATH}")


if __name__ == "__main__":
    main()
