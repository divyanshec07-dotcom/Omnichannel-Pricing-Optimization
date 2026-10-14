import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Configure premium wide layout and dark theme compatibility
st.set_page_config(page_title="Pricing Engine", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.title("⚡ Omnichannel Pricing Optimization Engine")
st.markdown("Automated Markdown & Inventory Reallocation Interface | **Status:** Connected to CA_1 POS Node")

@st.cache_data
def load_data():
    # Load the pre-filtered lightweight sample
    df = pd.read_pickle('data/dashboard_sample.pkl')
    
    # Generate mock margin baseline for UI demonstration purposes
    df['margin_pct'] = np.random.uniform(0.12, 0.45, size=len(df)) 
    return df

df = load_data()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🎯 Optimization Parameters")
selected_category = st.sidebar.selectbox("Category Filter", df['cat_id'].unique())

# Add an interactive dual-slider for price filtering
min_price = float(df['sell_price'].min())
max_price = float(df['sell_price'].max())
price_range = st.sidebar.slider("Price Target Range ($)", min_price, max_price, (min_price, 30.0))

# Apply filters
filtered_df = df[(df['cat_id'] == selected_category) & 
                 (df['sell_price'] >= price_range[0]) & 
                 (df['sell_price'] <= price_range[1])]

# --- KPI METRICS ROW ---
col1, col2, col3, col4 = st.columns(4)
# Deltas represent mock week-over-week changes to simulate a live environment
col1.metric("Active SKUs Tracked", len(filtered_df['item_id'].unique()), delta="24 New SKUs")
col2.metric("Average Listed Price", f"${filtered_df['sell_price'].mean():.2f}", delta="-0.8% DoD", delta_color="inverse")
col3.metric("7-Day Sales Velocity", int(filtered_df['sales'].sum()), delta="12% YoY")
col4.metric("Avg Margin Projection", f"{filtered_df['margin_pct'].mean()*100:.1f}%", delta="1.2% Post-Optimization")

st.divider()

# --- TABBED NAVIGATION ---
tab1, tab2 = st.tabs(["📊 Demand Elasticity Model", "📋 Actionable Markdown Queue"])

with tab1:
    st.subheader(f"Interactive Price-to-Volume Elasticity: {selected_category}")
    # Plotly dynamic scatter plot (Allows zooming, panning, and hover-data)
    fig = px.scatter(
        filtered_df.head(2000), # Cap at 2k points for rendering speed
        x="sell_price", y="sales", color="dept_id", 
        hover_data=["item_id"],
        labels={"sell_price": "Retail Listing Price ($)", "sales": "Daily Sales Velocity"},
        template="plotly_dark",
        opacity=0.6
    )
    fig.update_layout(height=450, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Algorithmic Price Adjustments Pending Approval")
    st.markdown("Items below the 15% margin protection threshold are flagged automatically.")
    
    # Prepare the approval matrix
    display_df = filtered_df[['item_id', 'dept_id', 'sell_price', 'margin_pct']].head(15).copy()
    display_df['recommended_discount'] = np.random.choice(['10%', '15%', '20%'], len(display_df))
    display_df['new_price'] = (display_df['sell_price'] * 0.85).round(2)
    display_df['post_markdown_margin'] = display_df['margin_pct'] - 0.15
    
    # Apply conditional formatting gradients directly to the dataframe
    st.dataframe(
        display_df.style.format({
            'sell_price': '${:.2f}', 
            'new_price': '${:.2f}',
            'margin_pct': '{:.1%}',
            'post_markdown_margin': '{:.1%}'
        }).background_gradient(subset=['post_markdown_margin'], cmap='RdYlGn', vmin=0.05, vmax=0.30),
        use_container_width=True,
        height=400
    )