import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Zomato Delivery Analytics Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 5px solid #ff6b6b;
}
.stMetric > label {
    font-size: 14px !important;
}
</style>
""", unsafe_allow_html=True)

# Title and header
st.title(" Zomato Delivery Analytics Dashboard")
st.markdown("---")

# Load data
@st.cache_data
def load_data():
    try:
        # Assuming the CSV file is uploaded or available
        df = pd.read_csv('zomato_delivery_clean_tableau.csv')
        return df
    except FileNotFoundError:
        st.error("Dataset not found. Please upload the CSV file.")
        return None

# File uploader as fallback
uploaded_file = st.file_uploader("Upload your Zomato delivery dataset", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    df = load_data()

if df is not None:
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # City filter
    cities = ['All'] + list(df['City'].unique()) if 'City' in df.columns else ['All']
    selected_city = st.sidebar.selectbox("Select City", cities)
    
    # Weather filter
    weather_options = ['All'] + list(df['Weather_conditions'].unique()) if 'Weather_conditions' in df.columns else ['All']
    selected_weather = st.sidebar.selectbox("Select Weather", weather_options)
    
    # Vehicle type filter
    vehicle_options = ['All'] + list(df['Type_of_vehicle'].unique()) if 'Type_of_vehicle' in df.columns else ['All']
    selected_vehicle = st.sidebar.selectbox("Select Vehicle Type", vehicle_options)
    
    # Festival filter
    festival_options = ['All'] + list(df['Festival'].unique()) if 'Festival' in df.columns else ['All']
    selected_festival = st.sidebar.selectbox("Select Festival", festival_options)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_city != 'All' and 'City' in df.columns:
        filtered_df = filtered_df[filtered_df['City'] == selected_city]
    if selected_weather != 'All' and 'Weather_conditions' in df.columns:
        filtered_df = filtered_df[filtered_df['Weather_conditions'] == selected_weather]
    if selected_vehicle != 'All' and 'Type_of_vehicle' in df.columns:
        filtered_df = filtered_df[filtered_df['Type_of_vehicle'] == selected_vehicle]
    if selected_festival != 'All' and 'Festival' in df.columns:
        filtered_df = filtered_df[filtered_df['Festival'] == selected_festival]
    
    # Key metrics
    st.header("📊 Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_deliveries = len(filtered_df)
        st.metric("Total Deliveries", f"{total_deliveries:,}")
    
    with col2:
        avg_time = filtered_df['Time_taken (min)'].mean() if 'Time_taken (min)' in filtered_df.columns else 0
        st.metric("Avg Delivery Time", f"{avg_time:.1f} min")
    
    with col3:
        avg_rating = filtered_df['Delivery_person_Ratings'].mean() if 'Delivery_person_Ratings' in filtered_df.columns else 0
        st.metric("Avg Rating", f"{avg_rating:.2f}")
    
    with col4:
        excellent_deliveries = (filtered_df['delivery_performance'] == 'Excellent').sum() if 'delivery_performance' in filtered_df.columns else 0
        excellent_pct = (excellent_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
        st.metric("Excellent Deliveries", f"{excellent_pct:.1f}%")
    
    with col5:
        high_satisfaction = (filtered_df['customer_satisfaction'] == 'High').sum() if 'customer_satisfaction' in filtered_df.columns else 0
        satisfaction_pct = (high_satisfaction / total_deliveries * 100) if total_deliveries > 0 else 0
        st.metric("High Satisfaction", f"{satisfaction_pct:.1f}%")
    
    st.markdown("---")
    
    # Main dashboard content
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Performance Analysis", "🌍 Geographic Analysis", "⏰ Time Analysis", "🎯 Business Intelligence"])
    
    with tab1:
        st.header("Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Delivery performance distribution
            if 'delivery_performance' in filtered_df.columns:
                fig = px.pie(filtered_df, names='delivery_performance', 
                           title='Delivery Performance Distribution',
                           color_discrete_map={'Excellent': '#00CC96', 'Good': '#19D3F3', 
                                             'Average': '#FFA15A', 'Poor': '#EF553B'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Rating distribution
            if 'Delivery_person_Ratings' in filtered_df.columns:
                fig = px.histogram(filtered_df, x='Delivery_person_Ratings', 
                                 title='Rating Distribution', nbins=20,
                                 color_discrete_sequence=['#636EFA'])
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            # Time distribution
            if 'Time_taken (min)' in filtered_df.columns:
                fig = px.histogram(filtered_df, x='Time_taken (min)', 
                                 title='Delivery Time Distribution', nbins=30,
                                 color_discrete_sequence=['#FF6692'])
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            # Efficiency tier
            if 'efficiency_tier' in filtered_df.columns:
                efficiency_counts = filtered_df['efficiency_tier'].value_counts()
                fig = px.bar(x=efficiency_counts.index, y=efficiency_counts.values,
                           title='Delivery Efficiency Tiers',
                           color=efficiency_counts.values,
                           color_continuous_scale='Viridis')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("Geographic Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # City performance
            if 'City' in filtered_df.columns and 'Time_taken (min)' in filtered_df.columns:
                city_performance = filtered_df.groupby('City')['Time_taken (min)'].mean().sort_values()
                fig = px.bar(x=city_performance.values, y=city_performance.index,
                           title='Average Delivery Time by City',
                           orientation='h',
                           color=city_performance.values,
                           color_continuous_scale='RdYlBu_r')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Distance category analysis
            if 'distance_category' in filtered_df.columns and 'Time_taken (min)' in filtered_df.columns:
                distance_performance = filtered_df.groupby('distance_category')['Time_taken (min)'].mean()
                fig = px.bar(x=distance_performance.index, y=distance_performance.values,
                           title='Average Delivery Time by Distance',
                           color=distance_performance.values,
                           color_continuous_scale='Blues')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Weather and traffic impact
        col3, col4 = st.columns(2)
        
        with col3:
            if 'Weather_conditions' in filtered_df.columns and 'Time_taken (min)' in filtered_df.columns:
                weather_impact = filtered_df.groupby('Weather_conditions')['Time_taken (min)'].mean().sort_values(ascending=False)
                fig = px.bar(x=weather_impact.index, y=weather_impact.values,
                           title='Weather Impact on Delivery Time',
                           color=weather_impact.values,
                           color_continuous_scale='Reds')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            if 'Road_traffic_density' in filtered_df.columns and 'Time_taken (min)' in filtered_df.columns:
                traffic_impact = filtered_df.groupby('Road_traffic_density')['Time_taken (min)'].mean().sort_values(ascending=False)
                fig = px.bar(x=traffic_impact.index, y=traffic_impact.values,
                           title='Traffic Impact on Delivery Time',
                           color=traffic_impact.values,
                           color_continuous_scale='Oranges')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.header("Time Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Meal period analysis
            if 'meal_period' in filtered_df.columns and 'Time_taken (min)' in filtered_df.columns:
                meal_performance = filtered_df.groupby('meal_period')['Time_taken (min)'].mean()
                fig = px.bar(x=meal_performance.index, y=meal_performance.values,
                           title='Average Delivery Time by Meal Period',
                           color=meal_performance.values,
                           color_continuous_scale='Sunset')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Peak hours analysis
            if 'order_hour' in filtered_df.columns and 'Time_taken (min)' in filtered_df.columns:
                hourly_performance = filtered_df.groupby('order_hour')['Time_taken (min)'].mean()
                fig = px.line(x=hourly_performance.index, y=hourly_performance.values,
                            title='Average Delivery Time by Hour',
                            markers=True)
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            # Weekend vs Weekday
            if 'is_weekend' in filtered_df.columns and 'Time_taken (min)' in filtered_df.columns:
                weekend_performance = filtered_df.groupby('is_weekend')['Time_taken (min)'].mean()
                weekend_performance.index = ['Weekday', 'Weekend']
                fig = px.bar(x=weekend_performance.index, y=weekend_performance.values,
                           title='Weekend vs Weekday Performance',
                           color=['#636EFA', '#EF553B'])
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            # Day of week analysis
            if 'day_type' in filtered_df.columns and 'Time_taken (min)' in filtered_df.columns:
                day_performance = filtered_df.groupby('day_type')['Time_taken (min)'].mean()
                days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                day_performance = day_performance.reindex([day for day in days_order if day in day_performance.index])
                fig = px.bar(x=day_performance.index, y=day_performance.values,
                           title='Performance by Day of Week',
                           color=day_performance.values,
                           color_continuous_scale='Viridis')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.header("Business Intelligence")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Customer satisfaction
            if 'customer_satisfaction' in filtered_df.columns:
                satisfaction_counts = filtered_df['customer_satisfaction'].value_counts()
                fig = px.pie(values=satisfaction_counts.values, names=satisfaction_counts.index,
                           title='Customer Satisfaction Levels',
                           color_discrete_map={'High': '#00CC96', 'Medium': '#FFA15A', 'Low': '#EF553B'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Service quality
            if 'service_quality' in filtered_df.columns:
                service_counts = filtered_df['service_quality'].value_counts()
                fig = px.pie(values=service_counts.values, names=service_counts.index,
                           title='Service Quality Distribution',
                           color_discrete_map={'Premium': '#FFD700', 'Standard': '#87CEEB', 'Below Standard': '#FFA07A'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            # Order complexity
            if 'order_complexity' in filtered_df.columns:
                complexity_counts = filtered_df['order_complexity'].value_counts()
                fig = px.bar(x=complexity_counts.index, y=complexity_counts.values,
                           title='Order Complexity Distribution',
                           color=complexity_counts.values,
                           color_continuous_scale='Plasma')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            # Difficulty level impact
            if 'difficulty_level' in filtered_df.columns and 'Time_taken (min)' in filtered_df.columns:
                difficulty_impact = filtered_df.groupby('difficulty_level')['Time_taken (min)'].mean()
                fig = px.bar(x=difficulty_impact.index, y=difficulty_impact.values,
                           title='Delivery Time by Difficulty Level',
                           color=difficulty_impact.values,
                           color_continuous_scale='Reds')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Business insights summary
        st.subheader("🎯 Key Business Insights")
        
        insight_col1, insight_col2 = st.columns(2)
        
        with insight_col1:
            st.markdown("""
            **Performance Summary:**
            """)
            if 'delivery_performance' in filtered_df.columns:
                excellent_pct = (filtered_df['delivery_performance'] == 'Excellent').mean() * 100
                st.info(f"🎯 {excellent_pct:.1f}% of deliveries are excellent")
            
            if 'customer_satisfaction' in filtered_df.columns:
                high_sat_pct = (filtered_df['customer_satisfaction'] == 'High').mean() * 100
                st.info(f"😊 {high_sat_pct:.1f}% customers highly satisfied")
            
            if 'is_peak_hour' in filtered_df.columns:
                peak_orders_pct = filtered_df['is_peak_hour'].mean() * 100
                st.info(f"⏰ {peak_orders_pct:.1f}% orders during peak hours")
        
        with insight_col2:
            st.markdown("""
            **Operational Insights:**
            """)
            if 'Time_taken (min)' in filtered_df.columns:
                avg_time = filtered_df['Time_taken (min)'].mean()
                st.warning(f"⏱️ Average delivery time: {avg_time:.1f} minutes")
            
            if 'Delivery_person_Ratings' in filtered_df.columns:
                avg_rating = filtered_df['Delivery_person_Ratings'].mean()
                st.success(f"⭐ Average rating: {avg_rating:.2f}/5")
            
            if 'Festival' in filtered_df.columns:
                festival_pct = (filtered_df['Festival'] == 'Yes').mean() * 100
                st.info(f"🎉 {festival_pct:.1f}% orders during festivals")
    
    # Data table
    st.markdown("---")
    st.header("📋 Raw Data")
    
    # Show data with pagination
    if st.checkbox("Show raw data"):
        st.dataframe(filtered_df.head(1000))
        st.info(f"Showing first 1000 rows of {len(filtered_df)} total filtered records")
    
    # Download filtered data
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download filtered data as CSV",
        data=csv,
        file_name=f'zomato_filtered_data_{selected_city}_{selected_weather}.csv',
        mime='text/csv'
    )

else:
    st.info("Please upload your Zomato delivery dataset to get started!")
    st.markdown("""
    ### Expected CSV Format:
    Your CSV file should contain the following columns:
    - Time_taken (min)
    - Delivery_person_Ratings
    - Delivery_person_Age
    - City
    - Weather_conditions
    - Road_traffic_density
    - Type_of_vehicle
    - Type_of_order
    - Festival
    - delivery_performance
    - customer_satisfaction
    - meal_period
    - efficiency_tier
    - And other features created by the feature engineering process
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
<p> Zomato Delivery Analytics Dashboard | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)