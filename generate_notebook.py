import nbformat as nbf

nb = nbf.v4.new_notebook()

text_cells = [
    """# Final Individual Project: Data Visualization
## Our World in Data - CO2 Emissions Analysis
This notebook performs exploratory data analysis and answers 10 multi-dimensional analytical questions regarding global CO2 emissions.

## 0. Setup and Data Loading""",
    
    """## 1. Regional Shifts
**Question:** How has the global share of CO2 emissions by region shifted over the last 50 years?""",

    """## 2. Decoupling Growth
**Question:** Which major economies have successfully decoupled economic growth (GDP per capita) from CO2 emissions per capita since 2000?""",

    """## 3. Emission Sources
**Question:** How does the primary source of CO2 emissions (coal, oil, gas) vary across the current top 10 emitting countries?""",

    """## 4. Consumption vs. Production
**Question:** Are wealthier nations offloading their carbon footprint? (Comparing consumption-based vs. production-based emissions across income groups).""",

    """## 5. Historical Responsibility
**Question:** How do cumulative CO2 emissions compare between developed and developing nations over the last century?""",

    """## 6. Emissions Intensity
**Question:** How does the CO2 emissions intensity (emissions per unit of GDP) vary globally, and which countries have improved the most?""",

    """## 7. Per Capita Disparities
**Question:** Which regions have the highest internal disparity in CO2 emissions per capita among their constituent countries?""",

    """## 8. Fuel Transitions
**Question:** Which countries have seen the fastest transition away from coal-based emissions, and what replaced them?""",

    """## 9. Rapid Developers
**Question:** How has the CO2 emission profile (source breakdown) of rapidly developing economies (e.g., BRICS) changed since 1990 compared to the G7?""",

    """## 10. Population vs Emissions
**Question:** What is the relationship between a country's population growth rate and its emissions growth rate over the last 20 years?"""
]

code_cells = [
    # Setup
    """import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# CVD-safe palette and consistent styling
colors_seq = ["#0284c7", "#c2410c", "#0d9488", "#7c3aed", "#db2777", "#ea580c"]
pio_template = "plotly_white"

def apply_plotly_theme(fig, title_text, yaxis_title=""):
    fig.update_layout(
        title={
            'text': title_text,
            'font': {'family': 'Outfit, sans-serif', 'size': 16, 'color': '#0f172a'},
            'y': 0.95,
            'x': 0,
            'xanchor': 'left',
            'yanchor': 'top'
        },
        font=dict(family='Outfit, sans-serif', color="#334155"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=60, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="left",
            x=0
        ),
        yaxis_title=yaxis_title,
        xaxis_title=""
    )
    fig.update_xaxes(showgrid=False, linecolor='#cbd5e1')
    fig.update_yaxes(showgrid=False, linecolor='#cbd5e1')
    return fig

# Load the data
df = pd.read_csv('owid-co2-data.csv')
df.head()""",
    
    # 1. Regional Shifts
    """regions = ['Asia', 'Europe', 'North America', 'South America', 'Africa', 'Oceania']
df_regions = df[(df['country'].isin(regions)) & (df['year'] >= 1970)].copy()

fig = px.area(df_regions, x='year', y='co2', color='country', 
              color_discrete_sequence=colors_seq,
              labels={'co2': 'CO2 Emissions (million tonnes)', 'year': 'Year', 'country': 'Region'})
apply_plotly_theme(fig, "Asia Dominates Modern Emissions while Western Regions Stabilize", "CO2 Emissions (million tonnes)")
fig.add_annotation(
    x=2015, y=17000,
    text="Asian emissions surge past rest of world combined",
    showarrow=True, arrowhead=2, arrowcolor="#334155",
    ax=-100, ay=-40,
    font=dict(size=11, color="#334155")
)
fig.show()""",

    # 2. Decoupling Growth
    """# Filter for post-2000 data
df_2000s = df[(df['year'] >= 2000) & (df['gdp'].notnull()) & (df['co2_per_capita'].notnull())].copy()
df_2000s['gdp_per_capita'] = df_2000s['gdp'] / df_2000s['population']

# Let's take a few major economies as examples: US, UK, China, India, Germany
major_economies = ['United States', 'United Kingdom', 'China', 'India', 'Germany']
df_major = df_2000s[df_2000s['country'].isin(major_economies)].copy()

# Normalize to 2000 levels to see the decoupling clearly
for c in major_economies:
    base_gdp = df_major[(df_major['country'] == c) & (df_major['year'] == 2000)]['gdp_per_capita'].values[0]
    base_co2 = df_major[(df_major['country'] == c) & (df_major['year'] == 2000)]['co2_per_capita'].values[0]
    df_major.loc[df_major['country'] == c, 'gdp_pc_index'] = df_major['gdp_per_capita'] / base_gdp * 100
    df_major.loc[df_major['country'] == c, 'co2_pc_index'] = df_major['co2_per_capita'] / base_co2 * 100

fig = go.Figure()
for i, c in enumerate(major_economies):
    df_c = df_major[df_major['country'] == c]
    color = colors_seq[i % len(colors_seq)]
    fig.add_trace(go.Scatter(x=df_c['year'], y=df_c['gdp_pc_index'], mode='lines', name=f'{c} (GDP/Capita)', line=dict(color=color, width=1.5, dash='dot')))
    fig.add_trace(go.Scatter(x=df_c['year'], y=df_c['co2_pc_index'], mode='lines', name=f'{c} (CO2/Capita)', line=dict(color=color, width=3)))

apply_plotly_theme(fig, "Western Countries Decouple (Solid CO2 Drops, Dotted GDP Rises), Developers Rise in Tandem", "Index (2000 = 100)")
fig.show()""",

    # 3. Emission Sources
    """recent_year = 2021
df_recent = df[(df['year'] == recent_year) & (df['iso_code'].notnull())].copy()
top10_emitters = df_recent.nlargest(10, 'co2')['country'].tolist()
df_top10 = df_recent[df_recent['country'].isin(top10_emitters)]

sources = ['coal_co2', 'oil_co2', 'gas_co2', 'cement_co2', 'flaring_co2']
df_melted = df_top10.melt(id_vars='country', value_vars=sources, var_name='Source', value_name='Emissions')
df_melted['Source'] = df_melted['Source'].str.replace('_co2', '').str.capitalize()

source_colors = {
    'Coal': '#475569',
    'Oil': '#c2410c',
    'Gas': '#0284c7',
    'Cement': '#94a3b8',
    'Flaring': '#e2e8f0'
}

fig = px.bar(df_melted, x='country', y='Emissions', color='Source', 
             color_discrete_map=source_colors,
             category_orders={"Source": ["Coal", "Oil", "Gas", "Cement", "Flaring"]})
apply_plotly_theme(fig, f"Coal and Oil Remain Dominant Sources for the Largest Global Emitters in {recent_year}", "CO2 Emissions (million tonnes)")
fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})
fig.show()""",

    # 4. Consumption vs Production
    """income_groups = ['High-income countries', 'Upper-middle-income countries', 'Lower-middle-income countries', 'Low-income countries']
recent_year = 2021
df_income = df[(df['country'].isin(income_groups)) & (df['year'] == recent_year)].copy()

fig = go.Figure(data=[
    go.Bar(name='Production-based', x=df_income['country'], y=df_income['co2'], marker_color='#94a3b8'),
    go.Bar(name='Consumption-based', x=df_income['country'], y=df_income['consumption_co2'], marker_color='#c2410c')
])

apply_plotly_theme(fig, f"Wealthier Nations Consume More Carbon Than They Produce (Offloading Impact)", "CO2 Emissions (million tonnes)")
fig.update_layout(barmode='group')
fig.show()""",

    # 5. Historical Responsibility
    """df_hist = df[(df['country'].isin(income_groups)) & (df['year'] >= 1900)].copy()

fig = px.area(df_hist, x='year', y='cumulative_co2', color='country',
              color_discrete_sequence=colors_seq,
              labels={'cumulative_co2': 'Cumulative CO2 (million tonnes)', 'year': 'Year', 'country': 'Income Group'})
apply_plotly_theme(fig, "High and Upper-Middle Income Nations Bear Disproportionate Historical Responsibility", "Cumulative CO2 (million tonnes)")
fig.show()""",

    # 6. Emissions Intensity
    """df_intensity = df[(df['year'] >= 1990) & (df['gdp'].notnull()) & (df['co2'].notnull()) & (df['iso_code'].notnull())].copy()
df_intensity['co2_intensity'] = df_intensity['co2'] / df_intensity['gdp'] * 1e6 # tonnes per million $

selected_countries = ['United States', 'China', 'India', 'Russia', 'Japan', 'Germany']
df_sel = df_intensity[df_intensity['country'].isin(selected_countries)]

fig = px.line(df_sel, x='year', y='co2_intensity', color='country',
              color_discrete_sequence=colors_seq)
apply_plotly_theme(fig, "CO2 Emissions Intensity (Tonnes per Million $ GDP) Declining Globally", "CO2 Intensity")
fig.show()""",

    # 7. Per Capita Disparities
    """df_2019 = df[(df['year'] == 2019) & (df['iso_code'].notnull()) & (df['co2_per_capita'].notnull())].copy()

fig = px.choropleth(df_2019, locations="iso_code", color="co2_per_capita",
                    hover_name="country", color_continuous_scale=px.colors.sequential.YlOrRd,
                    labels={'co2_per_capita': 'CO2/Capita (tonnes)'})
apply_plotly_theme(fig, "Global Disparity: Vast Inequality in CO2 Emissions Per Capita (2019)")
fig.update_layout(geo=dict(showframe=False, showcoastlines=True))
fig.show()""",

    # 8. Fuel Transitions
    """eu_countries = ['Germany', 'United Kingdom', 'France', 'Poland']
df_eu = df[(df['country'].isin(eu_countries)) & (df['year'] >= 1990)].copy()

fig = px.line(df_eu, x='year', y='coal_co2', color='country',
              color_discrete_sequence=colors_seq,
              labels={'coal_co2': 'Coal CO2 Emissions (million tonnes)', 'year': 'Year'})
apply_plotly_theme(fig, "Transition from Coal: European Nations Steadily Cutting Coal Emissions", "Coal CO2 (million tonnes)")
fig.show()""",

    # 9. Rapid Developers
    """brics = ['Brazil', 'Russia', 'India', 'China', 'South Africa']
df_brics = df[(df['country'].isin(brics)) & (df['year'] >= 1990)].copy()
df_brics_agg = df_brics.groupby(['year'])[sources].sum().reset_index()

df_brics_melted = df_brics_agg.melt(id_vars='year', value_vars=sources, var_name='Source', value_name='Emissions')
df_brics_melted['Source'] = df_brics_melted['Source'].str.replace('_co2', '').str.capitalize()

source_colors = {
    'Coal': '#475569',
    'Oil': '#c2410c',
    'Gas': '#0284c7',
    'Cement': '#94a3b8',
    'Flaring': '#e2e8f0'
}

fig = px.area(df_brics_melted, x='year', y='Emissions', color='Source',
              color_discrete_map=source_colors,
              category_orders={"Source": ["Coal", "Oil", "Gas", "Cement", "Flaring"]})
apply_plotly_theme(fig, "CO2 Emission Sources for BRICS Nations (Coal-Heavy Expansion since 2000)", "CO2 Emissions (million tonnes)")
fig.show()""",

    # 10. Population vs Emissions
    """# Compare 2000 to 2020
df_00 = df[(df['year'] == 2000) & (df['iso_code'].notnull())][['country', 'population', 'co2']].set_index('country')
df_20 = df[(df['year'] == 2020) & (df['iso_code'].notnull())][['country', 'population', 'co2']].set_index('country')

df_growth = df_20.join(df_00, lsuffix='_20', rsuffix='_00', how='inner')
df_growth['pop_growth'] = (df_growth['population_20'] - df_growth['population_00']) / df_growth['population_00'] * 100
df_growth['co2_growth'] = (df_growth['co2_20'] - df_growth['co2_00']) / df_growth['co2_00'] * 100

# Remove outliers for better plotting
df_growth = df_growth[(df_growth['pop_growth'] < 200) & (df_growth['co2_growth'] < 500) & (df_growth['co2_growth'] > -100)]

fig = px.scatter(df_growth.reset_index(), x='pop_growth', y='co2_growth', hover_name='country',
                 labels={'pop_growth': 'Population Growth (%)', 'co2_growth': 'CO2 Emissions Growth (%)'},
                 color_discrete_sequence=[colors_seq[1]])

# Add quadrants
fig.add_hline(y=0, line_dash="dash", line_color="gray")
fig.add_vline(x=0, line_dash="dash", line_color="gray")

apply_plotly_theme(fig, "No Simple Correlation: Population Growth Does Not Guarantee Identical Emissions Growth", "CO2 Growth (%)")
fig.show()"""
]

cells = []
# Create interleaving cells
for i in range(len(text_cells)):
    cells.append(nbf.v4.new_markdown_cell(text_cells[i]))
    cells.append(nbf.v4.new_code_cell(code_cells[i]))

nb['cells'] = cells

with open('analysis.ipynb', 'w') as f:
    nbf.write(nb, f)
