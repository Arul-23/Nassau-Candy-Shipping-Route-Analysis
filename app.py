import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Nassau Candy Shipping Dashboard",
    page_icon="📦",
    layout="wide"
)

# Load dataset
df = pd.read_csv("Nassau Candy Distributor.csv")

# Convert dates
df["Order Date"] = pd.to_datetime(
    df["Order Date"],
    dayfirst=True,
    errors="coerce"
)

df["Ship Date"] = pd.to_datetime(
    df["Ship Date"],
    dayfirst=True,
    errors="coerce"
)

# Calculate Shipping Lead Time
df["Shipping Lead Time"] = (
    df["Ship Date"] - df["Order Date"]
).dt.days

# Factory mapping
factory_mapping = {
    "Wonka Bar - Nutty Crunch Surprise": "Lot's O' Nuts",
    "Wonka Bar - Fudge Mallows": "Lot's O' Nuts",
    "Wonka Bar -Scrumdiddlyumptious": "Lot's O' Nuts",
    "Wonka Bar - Milk Chocolate": "Wicked Choccy's",
    "Wonka Bar - Triple Dazzle Caramel": "Wicked Choccy's",
    "Laffy Taffy": "Sugar Shack",
    "SweeTARTS": "Sugar Shack",
    "Nerds": "Sugar Shack",
    "Fun Dip": "Sugar Shack",
    "Fizzy Lifting Drinks": "Sugar Shack",
    "Everlasting Gobstopper": "Secret Factory",
    "Hair Toffee": "The Other Factory",
    "Lickable Wallpaper": "Secret Factory",
    "Wonka Gum": "Secret Factory",
    "Kazookles": "The Other Factory"
}

df["Factory"] = df["Product Name"].map(factory_mapping)

# Route
df["Route"] = df["Factory"] + " → " + df["State/Province"]

# Title
st.title("📦 Nassau Candy Shipping Route Efficiency Dashboard")
st.markdown(
    "Analysis of shipping routes, lead times, delays, regions, and ship modes."
)

# Sidebar filters
st.sidebar.header("Filters")

# Date Range Filter

# State Filter

# Lead Time Threshold Filter
lead_time_threshold = st.sidebar.number_input(
    "Lead-Time Threshold (Days)",
    min_value=0,
    max_value=2000,
    value=1400,
    step=50
)
states = ["All"] + sorted(df["State/Province"].dropna().unique().tolist())

selected_state = st.sidebar.selectbox(
    "Select State",
    states
)
min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

regions = ["All"] + sorted(df["Region"].dropna().unique().tolist())
selected_region = st.sidebar.selectbox("Select Region", regions)

ship_modes = ["All"] + sorted(df["Ship Mode"].dropna().unique().tolist())
selected_ship_mode = st.sidebar.selectbox("Select Ship Mode", ship_modes)

# Apply filters
filtered_df = df.copy()

if len(selected_dates) == 2:
    filtered_df = filtered_df[
        (filtered_df["Order Date"].dt.date >= selected_dates[0]) &
        (filtered_df["Order Date"].dt.date <= selected_dates[1])
    ]

if selected_state != "All":
    filtered_df = filtered_df[
        filtered_df["State/Province"] == selected_state
    ]

if selected_region != "All":
    filtered_df = filtered_df[
        filtered_df["Region"] == selected_region
    ]

if selected_ship_mode != "All":
    filtered_df = filtered_df[
        filtered_df["Ship Mode"] == selected_ship_mode
    ]

# KPI section
col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Shipments",
    f"{len(filtered_df):,}"
)

col2.metric(
    "Average Lead Time",
    f"{filtered_df['Shipping Lead Time'].mean():.2f} days"
)

delay_frequency = (
    filtered_df["Shipping Lead Time"] > 1400
).mean() * 100

col3.metric(
    "Delay Frequency",
    f"{delay_frequency:.2f}%"
)

st.divider()

# Route Efficiency
st.subheader("🚚 Route Efficiency")

route_summary = filtered_df.groupby("Route").agg(
    Total_Shipments=("Order ID", "count"),
    Average_Lead_Time=("Shipping Lead Time", "mean")
).reset_index()

top_routes = route_summary.sort_values(
    "Average_Lead_Time"
).head(10)

fig1 = px.bar(
    top_routes,
    x="Average_Lead_Time",
    y="Route",
    orientation="h",
    title="Top 10 Efficient Shipping Routes",
    labels={
        "Average_Lead_Time": "Average Lead Time (Days)",
        "Route": "Route"
    }
)

st.plotly_chart(fig1, use_container_width=True)

# Ship Mode Comparison
st.subheader("🚢 Ship Mode Comparison")

ship_mode_summary = filtered_df.groupby("Ship Mode").agg(
    Total_Shipments=("Order ID", "count"),
    Average_Lead_Time=("Shipping Lead Time", "mean")
).reset_index()

fig2 = px.bar(
    ship_mode_summary,
    x="Ship Mode",
    y="Average_Lead_Time",
    title="Average Shipping Lead Time by Ship Mode",
    labels={
        "Average_Lead_Time": "Average Lead Time (Days)"
    }
)

st.plotly_chart(fig2, use_container_width=True)

# Regional Analysis

# Geographic Bottleneck Analysis
# Delay Frequency Analysis
st.subheader("⚠️ Delay Frequency by Route")

delay_route_summary = filtered_df.groupby("Route").agg(
    Total_Shipments=("Order ID", "count"),
    Delay_Frequency=(
        "Shipping Lead Time",
        lambda x: (x > lead_time_threshold).mean() * 100
    )
).reset_index()

delay_route_summary = delay_route_summary[
    delay_route_summary["Total_Shipments"] >= 5
]

top_delay_routes = delay_route_summary.sort_values(
    "Delay_Frequency",
    ascending=False
).head(10)

fig5 = px.bar(
    top_delay_routes,
    x="Delay_Frequency",
    y="Route",
    orientation="h",
    title="Top 10 Routes by Delay Frequency",
    labels={
        "Delay_Frequency": "Delay Frequency (%)",
        "Route": "Route"
    }
)

st.plotly_chart(fig5, use_container_width=True)

# Delay Frequency Analysis
# Route Drill-Down
# Geographic Shipping Map
st.subheader("🗺️ Geographic Shipping Map")

map_data = filtered_df.groupby("State/Province").agg(
    Total_Shipments=("Order ID", "count"),
    Average_Lead_Time=("Shipping Lead Time", "mean")
).reset_index()

fig6 = px.choropleth(
    map_data,
    locations="State/Province",
    locationmode="USA-states",
    color="Average_Lead_Time",
    scope="usa",
    title="Average Shipping Lead Time by State",
    color_continuous_scale="Reds"
)

st.plotly_chart(fig6, use_container_width=True)
st.subheader("🔎 Route Drill-Down")

available_routes = sorted(filtered_df["Route"].dropna().unique().tolist())

selected_route = st.selectbox(
    "Select a Route",
    available_routes
)

route_details = filtered_df[
    filtered_df["Route"] == selected_route
][[
    "Order ID",
    "Order Date",
    "Ship Date",
    "Ship Mode",
    "Factory",
    "State/Province",
    "Shipping Lead Time",
    "Sales",
    "Cost"
]]

st.dataframe(
    route_details.sort_values("Order Date"),
    use_container_width=True
)
st.subheader("📍 Geographic Bottlenecks")

state_summary = filtered_df.groupby("State/Province").agg(
    Total_Shipments=("Order ID", "count"),
    Average_Lead_Time=("Shipping Lead Time", "mean")
).reset_index()

bottleneck_states = state_summary.sort_values(
    "Average_Lead_Time",
    ascending=False
).head(10)

fig4 = px.bar(
    bottleneck_states,
    x="Average_Lead_Time",
    y="State/Province",
    orientation="h",
    title="Top 10 States by Average Shipping Lead Time",
    labels={
        "Average_Lead_Time": "Average Lead Time (Days)",
        "State/Province": "State / Province"
    }
)

st.plotly_chart(fig4, use_container_width=True)
st.subheader("🌎 Regional Shipping Performance")

region_summary = filtered_df.groupby("Region").agg(
    Total_Shipments=("Order ID", "count"),
    Average_Lead_Time=("Shipping Lead Time", "mean")
).reset_index()

fig3 = px.bar(
    region_summary,
    x="Region",
    y="Average_Lead_Time",
    title="Average Shipping Lead Time by Region",
    labels={
        "Average_Lead_Time": "Average Lead Time (Days)"
    }
)

st.plotly_chart(fig3, use_container_width=True)

# Route table
st.subheader("📊 Route Performance Details")

st.dataframe(
    route_summary.sort_values(
        "Average_Lead_Time"
    ),
    use_container_width=True
)