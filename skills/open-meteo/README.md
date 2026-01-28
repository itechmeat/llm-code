# Open-Meteo Skill

Integrate Open-Meteo free weather APIs into your application.

## What it covers

- **Weather Forecast API** — hourly, daily, and current weather data
- **Air Quality API** — pollutants (PM10, PM2.5, O₃, NO₂, etc.) and AQI indices
- **Geocoding API** — resolve place names to coordinates and timezones

## Key topics

- Query parameter design (timezone, timeformat, units, variable selection)
- Multi-location batching via comma-separated coordinates
- Model selection (`models=auto` vs explicit provider models)
- Error handling (HTTP errors + JSON-level `{"error": true}`)
- WMO weather codes interpretation
- Attribution requirements (CAMS for air quality, GeoNames for geocoding)

## When to use

Use this skill when building weather-related features: forecasts, air quality reports, location search, or any Open-Meteo integration.

## Links

- Releases: https://github.com/open-meteo/open-meteo/releases
- Docs: https://open-meteo.com/en/docs
- Air Quality API: https://open-meteo.com/en/docs/air-quality-api
- Geocoding API: https://open-meteo.com/en/docs/geocoding-api
