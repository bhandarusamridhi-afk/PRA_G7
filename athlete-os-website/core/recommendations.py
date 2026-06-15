"""
AthleteOS - Rule-based recommendation & alert engine.

Translates an athlete's latest readiness / recovery / stress / load signals
into plain-language, actionable guidance. No external API required.

Severity levels:
- "critical"  -> red    (immediate intervention)
- "warning"   -> amber  (monitor / adjust)
- "positive"  -> green  (green light)
- "info"      -> blue   (neutral guidance)
"""

from __future__ import annotations


def _status_from_readiness(readiness: float) -> tuple[str, str]:
    if readiness >= 75:
        return "Optimal", "positive"
    if readiness >= 60:
        return "Ready", "info"
    if readiness >= 45:
        return "Caution", "warning"
    return "Compromised", "critical"


def readiness_status(readiness: float) -> tuple[str, str]:
    """Public helper -> (label, severity)."""
    return _status_from_readiness(readiness)


def athlete_recommendations(snap: dict) -> list[dict]:
    """Build a prioritized list of recommendations for a single athlete."""
    recs: list[dict] = []
    readiness = snap["readiness"]
    recovery = snap["recovery"]
    stress = snap["stress"]
    sleep = snap["sleep_hours"]
    acwr = snap["acwr"]
    hrv = snap["hrv"]
    motivation = snap["motivation"]
    focus = snap["focus"]

    # --- Readiness headline ---
    label, sev = _status_from_readiness(readiness)
    if sev == "positive":
        recs.append({
            "severity": "positive",
            "title": "Green light for high intensity",
            "body": f"Readiness is {readiness:.0f}/100 ({label}). Your body is primed - this is an "
                    "ideal day for a key speed or strength session or to push a quality workout.",
        })
    elif sev == "info":
        recs.append({
            "severity": "info",
            "title": "Train as planned",
            "body": f"Readiness is {readiness:.0f}/100 ({label}). Proceed with your scheduled session "
                    "at moderate-to-high effort, but listen to your body during warm-up.",
        })
    elif sev == "warning":
        recs.append({
            "severity": "warning",
            "title": "Dial back intensity today",
            "body": f"Readiness is {readiness:.0f}/100 ({label}). Reduce session volume by ~20-30% and "
                    "favour technique over maximal output to avoid digging a deeper fatigue hole.",
        })
    else:
        recs.append({
            "severity": "critical",
            "title": "Prioritise recovery - skip hard training",
            "body": f"Readiness is {readiness:.0f}/100 ({label}). Swap today's session for active recovery "
                    "(mobility, light aerobic work) and re-check tomorrow before loading up again.",
        })

    # --- Sleep ---
    if sleep < 6.5:
        recs.append({
            "severity": "warning",
            "title": "Protect your sleep tonight",
            "body": f"You logged {sleep:.1f}h of sleep. Aim for 8h+ tonight - even one short night blunts "
                    "recovery and reaction time. Wind down 45 min earlier and cut late screens.",
        })

    # --- Stress / mental ---
    if stress >= 7:
        recs.append({
            "severity": "warning",
            "title": "Stress is running high",
            "body": f"Self-reported stress is {stress:.0f}/10. Add a 10-minute breathing or mobility "
                    "block before training and consider a short check-in with your coach.",
        })
    if motivation <= 4.5:
        recs.append({
            "severity": "info",
            "title": "Motivation dip detected",
            "body": f"Motivation is {motivation:.0f}/10. Set one small, specific goal for today's session - "
                    "small wins rebuild momentum better than big targets.",
        })

    # --- Load / overtraining ---
    if acwr >= 1.5:
        recs.append({
            "severity": "critical",
            "title": "Workload spike - injury risk elevated",
            "body": f"Your acute:chronic workload ratio is {acwr:.2f} (safe zone is 0.8-1.3). Ease off for "
                    "1-2 days to let chronic load catch up before the next hard block.",
        })
    elif acwr < 0.8:
        recs.append({
            "severity": "info",
            "title": "Room to build load",
            "body": f"Workload ratio is {acwr:.2f}, on the lighter side. If you feel fresh, you can safely "
                    "add a quality session this week to keep the training stimulus progressing.",
        })

    # --- HRV ---
    if hrv < 45:
        recs.append({
            "severity": "warning",
            "title": "HRV is suppressed",
            "body": f"HRV is {hrv:.0f} ms, below your typical range - a sign your nervous system is still "
                    "recovering. Keep effort conversational until it rebounds.",
        })

    # --- Positive reinforcement ---
    if focus >= 8 and readiness >= 70:
        recs.append({
            "severity": "positive",
            "title": "Sharp focus + strong readiness",
            "body": f"Focus is {focus:.0f}/10 with high readiness. Great window for technical or "
                    "skill-heavy work that needs concentration.",
        })

    return recs


def coach_alerts(squad_df) -> list[dict]:
    """Squad-level alerts a coach should action (US-07 overtraining alerts)."""
    alerts: list[dict] = []
    for _, row in squad_df.iterrows():
        name = row["name"]
        if row["acwr"] >= 1.5:
            alerts.append({
                "severity": "critical",
                "title": f"{name}: overtraining risk",
                "body": f"Workload ratio {row['acwr']:.2f} (spike). Recommend a deload or recovery day and "
                        "a quick wellness check before the next hard session.",
            })
        if row["readiness"] < 45:
            alerts.append({
                "severity": "critical",
                "title": f"{name}: compromised readiness",
                "body": f"Readiness {row['readiness']:.0f}/100. Pull back planned intensity and confirm "
                        "sleep / stress status directly.",
            })
        elif row["readiness"] < 60:
            alerts.append({
                "severity": "warning",
                "title": f"{name}: readiness trending low",
                "body": f"Readiness {row['readiness']:.0f}/100. Monitor today and have a lighter option ready.",
            })
        if row["stress"] >= 7.5:
            alerts.append({
                "severity": "warning",
                "title": f"{name}: elevated stress",
                "body": f"Stress {row['stress']:.0f}/10. A brief 1:1 could surface what's driving it.",
            })

    if not alerts:
        alerts.append({
            "severity": "positive",
            "title": "Squad is in good shape",
            "body": "No athletes are flagged for overtraining, low readiness, or high stress today. "
                    "Proceed with the planned program.",
        })

    # Critical first.
    order = {"critical": 0, "warning": 1, "info": 2, "positive": 3}
    alerts.sort(key=lambda a: order.get(a["severity"], 4))
    return alerts


def squad_coaching_tip(squad_df) -> dict:
    """A single squad-wide programming suggestion."""
    avg_readiness = squad_df["readiness"].mean()
    high_load = (squad_df["acwr"] >= 1.5).sum()

    if high_load >= max(1, len(squad_df) // 2):
        return {
            "severity": "warning",
            "title": "Consider a squad-wide deload",
            "body": f"{high_load} athletes are carrying spiked workloads. A lighter team block this week "
                    "could reset fatigue and reduce collective injury risk.",
        }
    if avg_readiness >= 72:
        return {
            "severity": "positive",
            "title": "Squad primed for a quality block",
            "body": f"Average readiness is {avg_readiness:.0f}/100. The group can handle a demanding, "
                    "high-quality session - capitalise on the freshness.",
        }
    return {
        "severity": "info",
        "title": "Balanced session recommended",
        "body": f"Average readiness is {avg_readiness:.0f}/100. Mix intensities: let flagged athletes "
                "recover while fresher athletes take on the harder work.",
    }
