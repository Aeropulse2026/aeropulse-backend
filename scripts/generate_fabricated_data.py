"""Generate deterministic, non-sensitive AeroPulse demo data.

Creates 30 aircraft x 6 subsystems x 180 daily observations (32,400 telemetry
rows). Several component windows deteriorate before a simulated repair, then
return to their normal baseline.
"""
import csv
import math
import random
from datetime import date, datetime, timedelta
from pathlib import Path

RNG = random.Random(20261005)
OUT = Path(__file__).resolve().parents[1] / "data" / "fabricated"
START = date(2026, 1, 1)
DAYS = 180
SUBSYSTEMS = {
    "hydraulic_pump": {"vibration": 2.2, "temperature": 58, "pressure": 2500, "oil": 82, "part": "P-HYD-22"},
    "engine": {"vibration": 1.8, "temperature": 510, "pressure": 110, "oil": 86, "part": "P-ENG-11"},
    "avionics": {"vibration": 0.6, "temperature": 43, "pressure": 14, "oil": 100, "part": "P-AVN-08"},
    "landing_gear": {"vibration": 1.1, "temperature": 35, "pressure": 3000, "oil": 90, "part": "P-LDG-15"},
    "fuel_system": {"vibration": 0.9, "temperature": 39, "pressure": 45, "oil": 100, "part": "P-FUL-04"},
    "electrical": {"vibration": 0.4, "temperature": 47, "pressure": 28, "oil": 100, "part": "P-ELC-19"},
}
PARTS = [
    ("P-HYD-22", "Hydraulic pump kit", "hydraulic_pump", 2, 4, 10),
    ("P-ENG-11", "Engine bearing set", "engine", 6, 3, 21),
    ("P-AVN-08", "Avionics cooling module", "avionics", 9, 3, 14),
    ("P-LDG-15", "Landing gear seal kit", "landing_gear", 5, 4, 18),
    ("P-FUL-04", "Fuel pressure regulator", "fuel_system", 7, 3, 12),
    ("P-ELC-19", "Generator brush pack", "electrical", 11, 4, 9),
]


def write_csv(name, columns, rows):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main():
    aircraft = []
    for index in range(1, 31):
        aircraft.append({
            "aircraft_id": f"AF-{100 + index:03d}",
            "aircraft_type": "Trainer-X" if index % 2 else "Fighter-Y",
            "age_years": 3 + index % 12,
            "total_flight_hours": 1800 + index * 145,
            "total_cycles": 2300 + index * 190,
            "base": f"Base-{'ABC'[index % 3]}",
        })
    write_csv("aircraft.csv", list(aircraft[0]), aircraft)

    write_csv("inventory.csv", ["part_id", "part_name", "compatible_subsystem", "stock_on_hand", "reorder_point", "lead_days"], [
        {"part_id": part_id, "part_name": name, "compatible_subsystem": system, "stock_on_hand": stock,
         "reorder_point": reorder, "lead_days": lead}
        for part_id, name, system, stock, reorder, lead in PARTS
    ])

    # An event is (aircraft index, subsystem, repair day). Its 12 preceding days deteriorate.
    events = [(17, "hydraulic_pump", 110), (8, "engine", 76), (23, "landing_gear", 142), (4, "fuel_system", 159)]
    event_map = {(aircraft_index, subsystem): repair_day for aircraft_index, subsystem, repair_day in events}
    telemetry, labels, faults, maintenance = [], [], [], []
    for aircraft_index, aircraft_row in enumerate(aircraft, start=1):
        for subsystem, baseline in SUBSYSTEMS.items():
            repair_day = event_map.get((aircraft_index, subsystem))
            for day_number in range(DAYS):
                progress = 0.0
                if repair_day and repair_day - 12 <= day_number < repair_day:
                    progress = (day_number - (repair_day - 12) + 1) / 12
                usage = math.sin(day_number / 12) * 0.04
                vibration = baseline["vibration"] * (1 + usage) + RNG.gauss(0, baseline["vibration"] * 0.06) + progress * 5.2
                temperature = baseline["temperature"] + RNG.gauss(0, max(1, baseline["temperature"] * 0.025)) + progress * 18
                pressure = baseline["pressure"] + RNG.gauss(0, baseline["pressure"] * 0.02) - progress * baseline["pressure"] * 0.18
                oil = baseline["oil"] + RNG.gauss(0, 1.2) - progress * 26
                observed_at = datetime.combine(START + timedelta(days=day_number), datetime.min.time()).replace(hour=12)
                telemetry.append({
                    "timestamp": observed_at.isoformat(), "aircraft_id": aircraft_row["aircraft_id"], "subsystem": subsystem,
                    "vibration_mm_s": round(max(vibration, 0.05), 2), "temperature_c": round(temperature, 1),
                    "pressure_psi": round(max(pressure, 0), 1), "oil_level_pct": round(min(max(oil, 0), 100), 1),
                })
                days_to_repair = repair_day - day_number if repair_day is not None else None
                labels.append({
                    "date": (START + timedelta(days=day_number)).isoformat(),
                    "aircraft_id": aircraft_row["aircraft_id"], "subsystem": subsystem,
                    "corrective_maintenance_next_15d": int(days_to_repair is not None and 1 <= days_to_repair <= 15),
                    "corrective_maintenance_next_30d": int(days_to_repair is not None and 1 <= days_to_repair <= 30),
                })
                if progress >= 0.55 and day_number % 3 == 0:
                    faults.append({"event_id": f"FE-{aircraft_index:03d}-{subsystem[:3].upper()}-{day_number:03d}",
                                   "aircraft_id": aircraft_row["aircraft_id"], "fault_code": f"{subsystem[:3].upper()}-TREND-01",
                                   "subsystem": subsystem, "severity": "high" if progress > 0.8 else "medium",
                                   "timestamp": observed_at.isoformat(), "resolved_at": ""})
            if repair_day:
                repaired_at = START + timedelta(days=repair_day)
                for fault in faults:
                    if fault["aircraft_id"] == aircraft_row["aircraft_id"] and fault["subsystem"] == subsystem:
                        fault["resolved_at"] = repaired_at.isoformat()
                maintenance.append({"work_order_id": f"WO-{aircraft_index:03d}-{subsystem[:3].upper()}",
                                    "aircraft_id": aircraft_row["aircraft_id"], "component": subsystem,
                                    "action": "bearing replacement" if subsystem in {"hydraulic_pump", "engine"} else "inspection and seal replacement",
                                    "downtime_hours": 18 if subsystem == "engine" else 12, "outcome": "resolved",
                                    "completed_at": repaired_at.isoformat()})
    write_csv("telemetry.csv", ["timestamp", "aircraft_id", "subsystem", "vibration_mm_s", "temperature_c", "pressure_psi", "oil_level_pct"], telemetry)
    write_csv("risk_labels.csv", ["date", "aircraft_id", "subsystem", "corrective_maintenance_next_15d", "corrective_maintenance_next_30d"], labels)
    write_csv("fault_events.csv", ["event_id", "aircraft_id", "fault_code", "subsystem", "severity", "timestamp", "resolved_at"], faults)
    write_csv("maintenance.csv", ["work_order_id", "aircraft_id", "component", "action", "downtime_hours", "outcome", "completed_at"], maintenance)
    print(f"Wrote {len(telemetry):,} telemetry rows to {OUT}")


if __name__ == "__main__":
    main()
