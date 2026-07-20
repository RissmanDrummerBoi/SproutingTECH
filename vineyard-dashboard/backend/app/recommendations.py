"""
Rule-based irrigation recommendation engine.

Deliberately simple (thresholds, not ML) so it's transparent to growers and
easy to defend during judging. Swap in a learned model later without
touching the API surface.
"""
from typing import Optional

# Ratio of actual to reference evapotranspiration below which the vine is
# drawing less water than the atmosphere is demanding.
MILD_STRESS_RATIO = 0.85
SEVERE_STRESS_RATIO = 0.65

# Stem water potential (MPa, less negative = wetter). Below these, override
# to stress flags regardless of the ET ratio, since it's a direct field
# measurement.
PRESSURE_BOMB_MILD = -1.0
PRESSURE_BOMB_SEVERE = -1.4

# How much of the ET deficit to replace when irrigating (deficit irrigation
# strategy common in wine grapes — full replacement pushes vigor too hard).
REPLACEMENT_FACTOR = 0.7


def evaluate(
    eto_mm: float,
    eta_mm: float,
    pressure_bomb_mpa: Optional[float] = None,
) -> dict:
    """Return stress_ratio, stress_flag, action, recommended_mm for one reading."""
    ratio = round(eta_mm / eto_mm, 3) if eto_mm else None
    deficit = max(eto_mm - eta_mm, 0.0)

    if ratio is None:
        flag = "none"
    elif ratio <= SEVERE_STRESS_RATIO:
        flag = "severe"
    elif ratio <= MILD_STRESS_RATIO:
        flag = "mild"
    else:
        flag = "none"

    # Pressure-bomb reading is ground truth when available — let it
    # escalate (never downgrade) the ET-based flag.
    if pressure_bomb_mpa is not None:
        if pressure_bomb_mpa <= PRESSURE_BOMB_SEVERE:
            flag = "severe"
        elif pressure_bomb_mpa <= PRESSURE_BOMB_MILD and flag == "none":
            flag = "mild"

    if flag == "none":
        action = "hold"
        recommended_mm = 0.0
    else:
        action = "irrigate"
        recommended_mm = round(deficit * REPLACEMENT_FACTOR, 1)

    return {
        "stress_ratio": ratio,
        "stress_flag": flag,
        "action": action,
        "recommended_mm": recommended_mm,
    }
