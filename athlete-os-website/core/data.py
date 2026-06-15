"""
AthleteOS - Synthetic data layer.

Generates deterministic, realistic mock data for athletes so the demo is
fully self-contained and works on Streamlit Community Cloud with no database.

Key domain rules:
- Every athlete belongs to exactly one SPORT and one COACH.
- A coach only ever manages athletes from their OWN sport.
- Each athlete has ~45 days of daily records combining physical + mental data.
"""

from __future__ import annotations

import datetime as dt
import hashlib
from dataclasses import dataclass

import numpy as np
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Roster definition
# ---------------------------------------------------------------------------
# Each coach is tied to a single sport. Athletes inherit that sport, which
# guarantees a coach's squad is always same-sport.

SPORTS = {
    "Track & Field": {
        "icon": "Track",
        "coach": {
            "id": "coach_maria",
            "name": "Coach Maria",
            "password": "coach123",
        },
        "athletes": [
            {"id": "alex", "name": "Alex Rivera", "password": "alex123", "event": "100m Sprint"},
            {"id": "jordan", "name": "Jordan Blake", "password": "jordan123", "event": "400m"},
            {"id": "maya", "name": "Maya Okafor", "password": "maya123", "event": "Long Jump"},
            {"id": "sam", "name": "Sam Carter", "password": "sam123", "event": "1500m"},
        ],
    },
    "Swimming": {
        "icon": "Swim",
        "coach": {
            "id": "coach_david",
            "name": "Coach David",
            "password": "coach123",
        },
        "athletes": [
            {"id": "lena", "name": "Lena Park", "password": "lena123", "event": "200m Freestyle"},
            {"id": "tom", "name": "Tom Hughes", "password": "tom123", "event": "100m Butterfly"},
            {"id": "nina", "name": "Nina Costa", "password": "nina123", "event": "400m IM"},
        ],
    },
    "Basketball": {
        "icon": "Hoops",
        "coach": {
            "id": "coach_tara",
            "name": "Coach Tara",
            "password": "coach123",
        },
        "athletes": [
            {"id": "marcus", "name": "Marcus Lee", "password": "marcus123", "event": "Point Guard"},
            {"id": "chris", "name": "Chris Vo", "password": "chris123", "event": "Shooting Guard"},
            {"id": "andre", "name": "Andre Dixon", "password": "andre123", "event": "Center"},
        ],
    },
}

SESSION_TYPES = ["Endurance", "Speed", "Strength", "Technical", "Recovery", "Rest"]


@dataclass
class Account:
    user_id: str
    name: str
    role: str  # "athlete" or "coach"
    sport: str
    password: str
    event: str | None = None


def build_accounts() -> dict[str, Account]:
    """Flat lookup of every login account keyed by user_id."""
    accounts: dict[str, Account] = {}
    for sport, cfg in SPORTS.items():
        c = cfg["coach"]
        accounts[c["id"]] = Account(
            user_id=c["id"], name=c["name"], role="coach", sport=sport, password=c["password"]
        )
        for a in cfg["athletes"]:
            accounts[a["id"]] = Account(
                user_id=a["id"],
                name=a["name"],
                role="athlete",
                sport=sport,
                password=a["password"],
                event=a["event"],
            )
    return accounts


def authenticate(user_id: str, password: str) -> Account | None:
    accounts = build_accounts()
    acct = accounts.get(user_id.strip().lower())
    if acct and acct.password == password:
        return acct
    return None


def athletes_for_sport(sport: str) -> list[dict]:
    return SPORTS[sport]["athletes"]


def coach_for_sport(sport: str) -> dict:
    return SPORTS[sport]["coach"]


# ---------------------------------------------------------------------------
# Time-series generation
# ---------------------------------------------------------------------------

def _seed_for(athlete_id: str) -> int:
    # Use a stable hash so data is identical across processes / restarts
    # (Python's built-in hash() is salted per-process and not deterministic).
    digest = hashlib.md5(athlete_id.encode("utf-8")).hexdigest()
    return int(digest, 16) % (2**31)


def _clip(value, low, high):
    return float(np.clip(value, low, high))


@st.cache_data(show_spinner=False)
def generate_athlete_history(athlete_id: str, days: int = 45) -> pd.DataFrame:
    """Generate a deterministic daily history for one athlete."""
    rng = np.random.default_rng(_seed_for(athlete_id))

    # Per-athlete baselines so each athlete feels distinct.
    base_sleep = rng.uniform(6.5, 8.0)
    base_hrv = rng.uniform(55, 90)
    base_rhr = rng.uniform(46, 60)
    fitness_trend = rng.uniform(-0.05, 0.12)  # slow drift in readiness

    today = dt.date.today()
    rows = []

    # Carry-over fatigue accumulates with hard sessions.
    fatigue = rng.uniform(20, 35)

    for i in range(days):
        day = today - dt.timedelta(days=(days - 1 - i))
        weekday = day.weekday()

        # Training plan: harder mid-week, recovery weekends.
        if weekday == 6:
            session_type = "Rest"
            volume = 0
            intensity = 0
        elif weekday in (2, 4):
            session_type = rng.choice(["Speed", "Strength"])
            volume = int(rng.uniform(60, 110))
            intensity = int(rng.uniform(7, 10))
        elif weekday == 5:
            session_type = "Recovery"
            volume = int(rng.uniform(30, 50))
            intensity = int(rng.uniform(2, 4))
        else:
            session_type = rng.choice(["Endurance", "Technical"])
            volume = int(rng.uniform(45, 90))
            intensity = int(rng.uniform(4, 7))

        acute_load = volume * intensity

        # Fatigue dynamics: builds with load, recovers on easy days.
        fatigue += acute_load / 90.0
        fatigue *= 0.82
        fatigue = _clip(fatigue, 0, 100)

        # Sleep & recovery biometrics.
        sleep_hours = _clip(rng.normal(base_sleep, 0.7) - fatigue * 0.005, 4.5, 9.5)
        sleep_quality = _clip(rng.normal(78, 9) - fatigue * 0.25 + (sleep_hours - 7) * 5, 30, 100)
        hrv = _clip(rng.normal(base_hrv, 6) - fatigue * 0.30, 25, 120)
        resting_hr = _clip(rng.normal(base_rhr, 2.5) + fatigue * 0.10, 40, 80)

        # Recovery score from physiology.
        recovery = _clip(
            0.45 * sleep_quality
            + 0.30 * (hrv / 120 * 100)
            + 0.25 * (100 - fatigue),
            0,
            100,
        )

        # Mental check-in (1-10 scale). Stress rises with fatigue.
        stress = _clip(rng.normal(4.5, 1.3) + fatigue * 0.03, 1, 10)
        focus = _clip(rng.normal(7, 1.2) - (stress - 5) * 0.4, 1, 10)
        confidence = _clip(rng.normal(7, 1.1) + (recovery - 70) * 0.02, 1, 10)
        motivation = _clip(rng.normal(7.2, 1.2) - fatigue * 0.015, 1, 10)

        # Readiness = blend of recovery and mental state, plus slow fitness drift.
        mental_index = (focus + confidence + motivation) / 3 * 10
        readiness = _clip(
            0.50 * recovery
            + 0.25 * mental_index
            + 0.25 * (100 - stress * 10)
            + fitness_trend * i,
            0,
            100,
        )

        rows.append(
            {
                "date": day,
                "session_type": session_type,
                "volume_min": volume,
                "intensity": intensity,
                "acute_load": acute_load,
                "sleep_hours": round(sleep_hours, 1),
                "sleep_quality": round(sleep_quality, 1),
                "hrv": round(hrv, 1),
                "resting_hr": round(resting_hr, 1),
                "recovery": round(recovery, 1),
                "stress": round(stress, 1),
                "focus": round(focus, 1),
                "confidence": round(confidence, 1),
                "motivation": round(motivation, 1),
                "readiness": round(readiness, 1),
            }
        )

    df = pd.DataFrame(rows)
    # 7-day rolling acute:chronic workload ratio (overtraining signal).
    df["chronic_load"] = df["acute_load"].rolling(7, min_periods=1).mean()
    df["acwr"] = (df["acute_load"] / df["chronic_load"].replace(0, np.nan)).fillna(1.0).round(2)
    return df


def latest_snapshot(df: pd.DataFrame) -> dict:
    """Most recent day's metrics as a dict."""
    return df.iloc[-1].to_dict()


def squad_summary(sport: str) -> pd.DataFrame:
    """One row per athlete in a sport with their latest key metrics."""
    rows = []
    for a in athletes_for_sport(sport):
        df = generate_athlete_history(a["id"])
        snap = latest_snapshot(df)
        prev = df.iloc[-2] if len(df) > 1 else df.iloc[-1]
        rows.append(
            {
                "id": a["id"],
                "name": a["name"],
                "event": a["event"],
                "readiness": snap["readiness"],
                "readiness_delta": round(snap["readiness"] - prev["readiness"], 1),
                "recovery": snap["recovery"],
                "stress": snap["stress"],
                "sleep_hours": snap["sleep_hours"],
                "acwr": snap["acwr"],
                "hrv": snap["hrv"],
            }
        )
    return pd.DataFrame(rows)
