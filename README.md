# KOXR (Oxnard Airport) Weather Dashboard (2000–2024)

## Link to KOXR Weather Dashboard

Access the full interactive dashboard here:  
[https://datawran-koxr.streamlit.app](https://datawran-koxr.streamlit.app)

## Project Goals

To design an interactive tool for researchers, policymakers, and the public that provides insight into meteorological patterns in Oxnard, CA.  
This dashboard operates on Streamlit and enables users to view trends from 2000–2024 and explore climate patterns specific to Oxnard.

---

## Multi-Tab Dashboard with Interactive Visualizations

- **Overview**: Basic stats and trends  
- **Extreme Temperature Days**: Identify days with unusually high temperatures. Users have the ability to filter to a certain range of dates and utlize a slider to shift temperature thresholds to see how many days in Oxnard are above a certain temperature. Users can also download a table with findings that will include the date and maximum temperature recorded for that day.
- **Fire Weather Conditions**: Analyze temperature, relative humidity, and wind on fire vs. non-fire days. Users are able to filter to certain dates and change thresholds between Temperature, Relative Humidity, and Wind Speed to see how many hours in Oxnard, CA was considered to be in "Fire-Risk Hours" by the National Weather Service.  
- **Red Flag Warning Criteria**: This tab identifies and visualizes periods that meet the National Weather Service's Red Flag Warning criteria: relative humidity at or below 15% and sustained wind speeds of 25 mph or greater. A scatter plot displays air temperature over time for each qualifying observation, with wind speed encoded as a continuous color scale. This allows users to assess the thermal and wind characteristics during fire-critical weather conditions across the selected date range. The total number of Red Flag Warning hours is also calculated and displayed.
- **Santa Ana Winds**: This tab isolates and visualizes Santa Ana wind events, defined here as hours with sustained wind speeds ≥ 20 mph and wind directions from 30° to 120°, indicative of downslope flow from inland deserts toward the coast. Two visualizations are provided: (1) a scatter plot showing wind speed over time with relative humidity encoded as a color scale, allowing for assessment of dryness during Santa Ana events, and (2) a polar bar chart (wind rose) summarizing the average wind speed by wind direction, binned into 15° sectors. Together, these plots enable users to evaluate both the temporal and directional characteristics of Santa Ana winds across the selected date range. The total number of qualifying hours is also reported.  
- **Multivariate Explorer**: This tab enables users to explore temporal trends in up to three weather variables simultaneously. Data can be aggregated at monthly or yearly scales, with options to normalize values (scaling each variable to a 0–1 range) and apply a rolling average to highlight smoothed patterns. Users can dynamically select variables such as air temperature, wind speed, humidity, or pressure to generate comparative line plots. The resulting visualization helps assess covariation among meteorological parameters across the selected date range, making it useful for identifying seasonal patterns, long-term trends, or anomalies.
- **Index**: This tab serves as the reference section for interpreting the dashboard's metrics, definitions, and analytical tools. It includes expandable explanations of key meteorological terms (e.g., Red Flag Warnings, Santa Ana Winds, fire weather) and guides to interpreting normalized values, rolling averages, and data aggregation. A glossary defines all plotted variables, and source information is provided for transparency and reproducibility. Users can return to this tab for contextual understanding and clarification while navigating other parts of the dashboard.

---
## Data Sources

- Historical weather data obtained from the [National Weather Service - Los Angeles/Oxnard (NWS LOX)](https://www.weather.gov/lox/observations_historical)
- Download the KOXR SQLite database directly from the GitHub repository:  
  [KOXR_2000–2024_data.db](https://github.com/dr-adsalas/datawran/blob/main/KOXR_2000-2024_data.db)
