import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

st.set_page_config(
    page_title="🌍 CO₂ Emissions Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌍 Global CO₂ Emissions Dashboard")
st.markdown("""
Welcome to the **CO₂ Emissions Dashboard**.

Explore trends, top emitters, source breakdowns, global maps, and forecasts up to 2030.

Use the tabs below to navigate through different visualizations and insights.
""")
st.markdown("---")

@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    non_countries = ['Global', 'International Transport', 'Kuwaiti Oil Fires', 'Antarctica']
    df = df[~df['Country'].isin(non_countries)]
    df['Country'] = df['Country'].replace({'USA': 'United States'})
    df = df[df['Year'] >= 2002]
    return df

df = load_data()

countries = sorted(df['Country'].unique())
sources = ['Total','Coal','Oil','Gas','Cement','Flaring','Other']
years = sorted(df['Year'].unique())

@st.cache_data
def filter_data(countries, start_year, end_year, source):
    return df[(df['Country'].isin(countries)) & (df['Year'].between(start_year, end_year))]

@st.cache_data
def get_top_emitters(source, n=10):
    return df.groupby('Country', as_index=False)[source].sum().sort_values(source, ascending=False).head(n)

def generate_color_map(items):
    return {item: px.colors.qualitative.Set2[i % 8] for i, item in enumerate(items)}

def display_kpis(selected_countries, start_year, end_year, source):
    global_total = df[df['Year'] == end_year][source].sum()
    cols = st.columns(len(selected_countries))
    for i, c in enumerate(selected_countries):
        subset = df[(df['Country'] == c) & (df['Year'].between(start_year, end_year))]
        start_val = subset[subset['Year'] == start_year][source].values[0]
        end_val = subset[subset['Year'] == end_year][source].values[0]
        change_pct = ((end_val - start_val) / start_val * 100) if start_val != 0 else 0
        contribution = (end_val / global_total * 100) if global_total != 0 else 0
        cols[i].metric(label=f"{c}", value=f"{end_val:.1f} MtCO₂", delta=f"{change_pct:.1f}%")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Trends", "📊 Comparisons", "🌍 Map", "🥧 Breakdown", "🔮 Forecasting"
])

with tab1:
    st.subheader("📈 Emission Trend Over Time")
    selected_countries = st.multiselect(
        "Select Countries", countries, default=['Germany','United States','China','India','Brazil']
    )
    selected_source = st.selectbox("Select Emission Source", sources)
    start_year, end_year = st.select_slider(
        "Select Year Range", options=years, value=(years[0], years[-1])
    )

    combined_df = filter_data(selected_countries, start_year, end_year, selected_source)

    if not combined_df.empty:
        display_kpis(selected_countries, start_year, end_year, selected_source)
        color_map = generate_color_map(selected_countries)

        fig_line = px.line(
            combined_df, x='Year', y=selected_source, color='Country', markers=True,
            color_discrete_map=color_map,
            title=f'{selected_source} Emission Trends ({start_year}-{end_year})'
        )
        fig_line.update_traces(
            mode='lines+markers',
            hovertemplate="%{x}: %{y:.2f} MtCO₂<extra>%{fullData.name}</extra>"
        )
        st.plotly_chart(fig_line, use_container_width=True)

with tab2:
    st.subheader("⚡ Top 10 Emitters of All Time")
    selected_source_tab2 = st.selectbox("Select Emission Source for Comparison", sources, index=0)

    top10_alltime = get_top_emitters(selected_source_tab2, n=10)
    color_map_top10 = generate_color_map(top10_alltime['Country'])
    fig_top10 = px.bar(
        top10_alltime, x=selected_source_tab2, y='Country', orientation='h',
        text=selected_source_tab2, color='Country', color_discrete_map=color_map_top10
    )
    fig_top10.update_traces(texttemplate='%{text:.2s}', textposition="outside")
    st.plotly_chart(fig_top10, use_container_width=True)

    st.subheader("📉 Biggest Reductions Since 2002")
    first_last = df[df["Year"].isin([df['Year'].min(), df['Year'].max()])]\
                     .pivot_table(index="Country", columns="Year", values=selected_source_tab2).dropna()
    if not first_last.empty:
        first_last["% Change"] = (first_last[df['Year'].max()] - first_last[df['Year'].min()]) / first_last[df['Year'].min()] * 100
        reductions = first_last.sort_values("% Change").head(10).reset_index()
        color_map_reductions = generate_color_map(reductions['Country'])
        fig_reduction = px.bar(
            reductions, x="% Change", y="Country", orientation="h",
            text="% Change", color='Country', color_discrete_map=color_map_reductions
        )
        fig_reduction.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig_reduction, use_container_width=True)
    else:
        st.info("No reduction data available for the selected source.")

with tab3:
    selected_source_trend = st.selectbox("Select Emission Source", sources, index=0, key="trend_source")
    st.subheader(f"🌍 Global {selected_source_trend} Emissions (Animated)")
    fig_map = px.choropleth(
        df, locations="Country", locationmode="country names",
        color=selected_source_trend, hover_name="Country",
        animation_frame="Year", color_continuous_scale="Reds", height=650
    )
    st.plotly_chart(fig_map, use_container_width=True)

with tab4:
    st.subheader("🥧 Emission Sources Breakdown")
    default_index = countries.index('Germany') if 'Germany' in countries else 0
    selected_country_pie = st.selectbox("Select Country", countries, index=default_index)
    selected_year_pie = st.selectbox("Select Year", years, index=len(years)-1)

    breakdown_df = df[(df['Country']==selected_country_pie) & (df['Year']==selected_year_pie)]
    if not breakdown_df.empty:
        melted = breakdown_df.melt(
            id_vars=['Country','Year'],
            value_vars=['Coal','Oil','Gas','Cement','Flaring','Other'],
            var_name='Source', value_name='Emissions'
        )
        fig_pie = px.pie(
            melted, values='Emissions', names='Source', hole=0.4,
            title=f'{selected_country_pie} Emission Sources in {selected_year_pie}'
        )
        st.plotly_chart(fig_pie, use_container_width=True)


with tab5:
    st.subheader("🔮 Forecasting Emissions to 2030")
    if not PROPHET_AVAILABLE:
        st.warning("⚠️ Prophet not installed. Run `pip install prophet` to enable forecasting.")
    else:
        selected_country_forecast = st.selectbox("Select Country for Forecasting", countries, index=default_index)
        selected_source_forecast = st.selectbox("Select Emission Source", sources, index=0, key="forecast_source")

        forecast_df = df[df['Country']==selected_country_forecast][['Year', selected_source_forecast]]\
                        .rename(columns={'Year':'Year', selected_source_forecast:'Emission'})
        forecast_df['Year'] = pd.to_datetime(forecast_df['Year'], format='%Y')

        m = Prophet()
        forecast_prophet_df = forecast_df.rename(columns={'Year':'ds','Emission':'y'})
        m.fit(forecast_prophet_df)

        future = m.make_future_dataframe(periods=9, freq='Y')
        forecast = m.predict(future)

        forecast.rename(columns={
            'ds':'Year',
            'yhat':'Forecasted Emission',
            'yhat_upper':'Upper CI',
            'yhat_lower':'Lower CI'
        }, inplace=True)

        fig_forecast = go.Figure()
        fig_forecast.add_trace(go.Scatter(x=forecast['Year'], y=forecast['Forecasted Emission'], mode='lines', name='Forecast'))
        fig_forecast.add_trace(go.Scatter(x=forecast_df['Year'], y=forecast_df['Emission'], mode='markers+lines', name='Actual'))
        fig_forecast.add_trace(go.Scatter(x=forecast['Year'], y=forecast['Upper CI'], line=dict(dash='dot', color='lightblue'), name='Upper CI'))
        fig_forecast.add_trace(go.Scatter(x=forecast['Year'], y=forecast['Lower CI'], line=dict(dash='dot', color='lightblue'), name='Lower CI', fill='tonexty'))

        fig_forecast.update_layout(
            title=f'{selected_country_forecast} Forecasted {selected_source_forecast} Emissions to 2030',
            yaxis_title='MtCO₂',
            xaxis_title='Year'
        )
        st.plotly_chart(fig_forecast, use_container_width=True)
