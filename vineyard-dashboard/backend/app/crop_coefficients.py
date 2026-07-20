"""
Grapevine crop coefficient (Kc) curve, Southern Hemisphere season.

TerraClim's API supplies ETo (reference evapotranspiration) only — it has
no vine-specific ETa layer. The standard approach (FAO-56 style) is:

    ETa_modeled = ETo * Kc(growth_stage)

These Kc bands are generic starting points for wine grapes under
deficit-irrigation management, not cultivar- or canopy-specific — treat
them as a first estimate. FruitLook exports and pressure-bomb readings
(see fruitlook_import.py and DailyReading.pressure_bomb_mpa) are how a
real deployment should calibrate these per block/cultivar, which is
exactly the validation step your README already calls for.

Southern Hemisphere phenology assumed (adjust for warmer/cooler sites):
  - Dormant:            Jun – Aug
  - Budbreak to bloom:  Sep – Oct
  - Bloom to veraison:  Nov – Dec  (peak canopy, highest water use)
  - Veraison to harvest: Jan – Mar (often deficit-irrigated on purpose)
  - Post-harvest:       Apr – May
"""
from datetime import date

# (month_start, month_end_inclusive) -> Kc
STAGE_KC = [
    ((6, 8), 0.20),    # dormant
    ((9, 10), 0.45),   # budbreak – bloom
    ((11, 12), 0.80),  # bloom – veraison, peak canopy
    ((1, 3), 0.65),    # veraison – harvest, typical deficit-irrigation target
    ((4, 5), 0.35),    # post-harvest
]


def kc_for_date(d: date) -> float:
    for (start_month, end_month), kc in STAGE_KC:
        if start_month <= d.month <= end_month:
            return kc
    return 0.5  # fallback, shouldn't be reached given full-year coverage


def model_eta(eto_mm: float, d: date, kc_override: float | None = None) -> float:
    kc = kc_override if kc_override is not None else kc_for_date(d)
    return round(eto_mm * kc, 2)
