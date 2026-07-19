# SproutingTECH
ET-GEO Hackathon 2026 – irrigation dashboard for wine growers using TerraClim's daily 10m vine water-use data

# ET-GEO Hackathon 2026 – Vineyard Irrigation Dashboard

**Team:** SproutingTECH  
**Dates:** 16–19 July 2026  
**Submission:** 20 July 2026  

## Contributors
-Risana Kelly Siweya
-Nikelwa Sophazi
-
-

## The Problem
Growers have access to satellite and weather data, but no simple, actionable tool that tells them *exactly how much water each vineyard block needs today*. This prototype bridges that gap.

## What We Built
- Field-level irrigation dashboard  
- Daily ETo (reference evapotranspiration) and ETa (actual evapotranspiration) per block  
- Irrigation recommendations: irrigate / hold / how much (mm)  
- Water-stress flags and alerts  
- Validation layer comparing against FruitLook and pressure-bomb readings

## Tech Stack
- **Backend:** Python (FastAPI) – data processing & API  
- **Frontend:** React – interactive dashboard  
- **Data:** GIS / Remote Sensing (raster processing, GeoJSON)  
- **ML:** Simple thresholds 

## Data Sources
- TerraClim ET-GEO science data (daily 10m vine-specific water use)  
- FruitLook validation data  
- Weather station inputs  
- Pressure-bomb reference readings

## How to Run Locally
1. Clone this repo: `git clone ...`  
2. Install dependencies: `pip install -r requirements.txt` (or `npm install` if frontend)  
3. Run the app: `python app.py` or `npm start`  
4. Open `localhost:8000` (or your configured port)

## What We Learned
- Translating complex ET-GEO science into a grower-friendly interface is harder than it sounds – but doable.  
- Validation is key; growers trust tools that match their field readings.  
- AI-assisted dev is a game-changer for rapid prototyping.

## Credits
Built for the Stellenbosch University LaunchLab / SA Wine / TerraClim ET-GEO Hackathon. Mentors and data provided by TerraClim and viticulture experts.

---

**Status:** NOT DONE
