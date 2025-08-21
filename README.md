# 🌍 Global CO₂ Emissions Dashboard

An interactive **Streamlit dashboard** for exploring global CO₂ emissions data.  
This project visualizes emission trends, top emitters, reductions, source breakdowns, geographic distribution, and future forecasts using **Prophet**.

---

## 🌐 Live Demo

👉 Try the dashboard here: [CO₂ Emissions Dashboard](https://tar-co2-emissions-dashboard.streamlit.app/)  

---

## ✨ Features

- **📈 Trends**: Track CO₂ emission trends over time by country and emission source.  
- **📊 Comparisons**: See the **Top 10 emitters** of all time and countries with the **biggest reductions** since 2002.  
- **🌍 Map**: Animated choropleth world map showing global CO₂ emissions by year.  
- **🥧 Breakdown**: Interactive pie chart of emission sources for any selected country and year.  
- **🔮 Forecasting**: Predict emissions up to **2030** using Facebook’s Prophet library.  

---

## 📂 Dataset

The dashboard uses the **Global Carbon Budget 2024 dataset**:  
- File: `data.csv`  
- Source: [Global Carbon Project](https://zenodo.org/records/7215364)  

Non-country entries such as *Global*, *International Transport*, *Kuwaiti Oil Fires*, and *Antarctica* are excluded for clarity.

---

## 🚀 Installation

Clone the repository:

```bash
git clone git@github.com:tarzahedi/co2-emissions-dashboard.git
cd co2-emissions-dashboard
