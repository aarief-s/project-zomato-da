import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Zomato Delivery Dashboard",
    page_icon="🍕",
    layout="wide"
)

# Title
st.title("🍕 Zomato Delivery Analytics Dashboard")
st.markdown("---")

# File uploader
uploaded_file = st.file_uploader("📁 Upload your Zomato delivery dataset (CSV)", type=['csv'])

if uploaded_file is not None:
    try:
        # Load data
        df = pd.read_csv(uploaded_file)
        
        st.success(f"✅ Data loaded successfully: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Show basic info
        st.subheader("📊 Dataset Overview")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", f"{len(df):,}")
        with col2:
            st.metric("Total Columns", f"{len(df.columns)}")
        with col3:
            missing_data = df.isnull().sum().sum()
            st.metric("Missing Values", f"{missing_data:,}")
        
        # Display column names
        st.subheader("📋 Available Columns")
        cols_per_row = 4
        for i in range(0, len(df.columns), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col_name in enumerate(df.columns[i:i+cols_per_row]):
                with cols[j]:
                    st.write(f"• {col_name}")
        
        st.markdown("---")
        
        # Filters
        st.sidebar.header("🔍 Filters")
        
        # City filter
        if 'City' in df.columns:
            cities = ['All'] + sorted(df['City'].unique().tolist())
            selected_city = st.sidebar.selectbox("Select City", cities)
            if selected_city != 'All':
                df = df[df['City'] == selected_city]
        
        # Weather filter
        if 'Weather_conditions' in df.columns:
            weather_options = ['All'] + sorted(df['Weather_conditions'].unique().tolist())
            selected_weather = st.sidebar.selectbox("Select Weather", weather_options)
            if selected_weather != 'All':
                df = df[df['Weather_conditions'] == selected_weather]
        
        # Vehicle filter
        if 'Type_of_vehicle' in df.columns:
            vehicle_options = ['All'] + sorted(df['Type_of_vehicle'].unique().tolist())
            selected_vehicle = st.sidebar.selectbox("Select Vehicle Type", vehicle_options)
            if selected_vehicle != 'All':
                df = df[df['Type_of_vehicle'] == selected_vehicle]
        
        st.sidebar.markdown(f"**Filtered Records: {len(df):,}**")
        
        # Main Analysis
        st.header("📈 Key Performance Indicators")
        
        # Calculate metrics
        col1, col2, col3, col4 = st.columns(4)
        
        if 'Time_taken (min)' in df.columns:
            with col1:
                avg_time = df['Time_taken (min)'].mean()
                st.metric("Avg Delivery Time", f"{avg_time:.1f} min")
        
        if 'Delivery_person_Ratings' in df.columns:
            with col2:
                avg_rating = df['Delivery_person_Ratings'].mean()
                st.metric("Avg Rating", f"{avg_rating:.2f}/5")
        
        if 'Delivery_person_Age' in df.columns:
            with col3:
                avg_age = df['Delivery_person_Age'].mean()
                st.metric("Avg Delivery Person Age", f"{avg_age:.1f} years")
        
        with col4:
            if 'Time_taken (min)' in df.columns:
                fast_deliveries = (df['Time_taken (min)'] <= 30).sum()
                fast_pct = (fast_deliveries / len(df) * 100)
                st.metric("Fast Deliveries (≤30min)", f"{fast_pct:.1f}%")
        
        # Analysis tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Basic Stats", "🌍 Categories", "⏰ Time Analysis", "📋 Data Table"])
        
        with tab1:
            st.subheader("📊 Basic Statistics")
            
            # Numeric columns analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                st.write("**Numeric Columns Statistics:**")
                st.dataframe(df[numeric_cols].describe())
            
            # Missing values
            missing_vals = df.isnull().sum()
            if missing_vals.sum() > 0:
                st.write("**Missing Values:**")
                missing_df = missing_vals[missing_vals > 0].reset_index()
                missing_df.columns = ['Column', 'Missing Count']
                missing_df['Missing %'] = (missing_df['Missing Count'] / len(df) * 100).round(2)
                st.dataframe(missing_df)
            else:
                st.success("✅ No missing values found!")
        
        with tab2:
            st.subheader("🌍 Categorical Analysis")
            
            categorical_cols = df.select_dtypes(include=['object']).columns
            
            for col in categorical_cols[:6]:  # Show first 6 categorical columns
                if col in df.columns:
                    st.write(f"**{col} Distribution:**")
                    value_counts = df[col].value_counts().head(10)
                    
                    # Create simple bar chart using st.bar_chart
                    chart_data = pd.DataFrame({
                        'Count': value_counts.values
                    }, index=value_counts.index)
                    
                    st.bar_chart(chart_data)
                    
                    # Show percentages
                    percentages = (value_counts / len(df) * 100).round(2)
                    for idx, (category, count) in enumerate(value_counts.items()):
                        st.write(f"• {category}: {count:,} ({percentages.iloc[idx]}%)")
                    
                    st.markdown("---")
        
        with tab3:
            st.subheader("⏰ Time and Performance Analysis")
            
            # Time taken analysis
            if 'Time_taken (min)' in df.columns:
                st.write("**Delivery Time Analysis:**")
                time_data = df['Time_taken (min)']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Min Time", f"{time_data.min():.0f} min")
                with col2:
                    st.metric("Max Time", f"{time_data.max():.0f} min")
                with col3:
                    st.metric("Median Time", f"{time_data.median():.1f} min")
                
                # Create histogram data
                hist_data = np.histogram(time_data.dropna(), bins=20)
                hist_df = pd.DataFrame({
                    'Frequency': hist_data[0]
                }, index=[f"{hist_data[1][i]:.0f}-{hist_data[1][i+1]:.0f}" for i in range(len(hist_data[0]))])
                
                st.write("**Delivery Time Distribution:**")
                st.bar_chart(hist_df)
            
            # Rating analysis
            if 'Delivery_person_Ratings' in df.columns:
                st.write("**Rating Analysis:**")
                rating_data = df['Delivery_person_Ratings']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Min Rating", f"{rating_data.min():.1f}")
                with col2:
                    st.metric("Max Rating", f"{rating_data.max():.1f}")
                with col3:
                    st.metric("Median Rating", f"{rating_data.median():.2f}")
                
                # Rating distribution
                rating_counts = rating_data.value_counts().sort_index()
                rating_df = pd.DataFrame({
                    'Count': rating_counts.values
                }, index=rating_counts.index)
                
                st.write("**Rating Distribution:**")
                st.bar_chart(rating_df)
            
            # Performance by categories
            if 'Weather_conditions' in df.columns and 'Time_taken (min)' in df.columns:
                st.write("**Average Delivery Time by Weather:**")
                weather_performance = df.groupby('Weather_conditions')['Time_taken (min)'].mean().sort_values(ascending=False)
                weather_df = pd.DataFrame({
                    'Avg Time (min)': weather_performance.values
                }, index=weather_performance.index)
                st.bar_chart(weather_df)
                
                # Show numbers
                for weather, time in weather_performance.items():
                    st.write(f"• {weather}: {time:.1f} minutes")
        
        with tab4:
            st.subheader("📋 Data Table")
            
            # Search functionality
            search_term = st.text_input("🔍 Search in data (case insensitive):")
            
            # Show data
            display_df = df.copy()
            
            if search_term:
                # Search in all string columns
                string_cols = display_df.select_dtypes(include=['object']).columns
                mask = pd.Series([False] * len(display_df))
                
                for col in string_cols:
                    mask |= display_df[col].astype(str).str.contains(search_term, case=False, na=False)
                
                display_df = display_df[mask]
                st.write(f"Found {len(display_df)} records matching '{search_term}'")
            
            # Pagination
            rows_per_page = st.selectbox("Rows per page:", [10, 25, 50, 100], index=1)
            
            total_pages = len(display_df) // rows_per_page + (1 if len(display_df) % rows_per_page > 0 else 0)
            
            if total_pages > 1:
                page = st.number_input("Page:", min_value=1, max_value=total_pages, value=1)
                start_idx = (page - 1) * rows_per_page
                end_idx = start_idx + rows_per_page
                st.write(f"Showing page {page} of {total_pages} (rows {start_idx + 1} to {min(end_idx, len(display_df))} of {len(display_df)})")
                st.dataframe(display_df.iloc[start_idx:end_idx])
            else:
                st.dataframe(display_df.head(rows_per_page))
            
            # Download button
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="📥 Download filtered data as CSV",
                data=csv,
                file_name="zomato_filtered_data.csv",
                mime="text/csv"
            )
        
        # Summary insights
        st.markdown("---")
        st.subheader("🎯 Key Insights")
        
        insights = []
        
        if 'Time_taken (min)' in df.columns:
            avg_time = df['Time_taken (min)'].mean()
            if avg_time <= 25:
                insights.append(f"✅ Excellent average delivery time: {avg_time:.1f} minutes")
            elif avg_time <= 35:
                insights.append(f"⚠️ Moderate average delivery time: {avg_time:.1f} minutes")
            else:
                insights.append(f"❌ High average delivery time: {avg_time:.1f} minutes - needs improvement")
        
        if 'Delivery_person_Ratings' in df.columns:
            avg_rating = df['Delivery_person_Ratings'].mean()
            if avg_rating >= 4.5:
                insights.append(f"⭐ Excellent average rating: {avg_rating:.2f}/5")
            elif avg_rating >= 4.0:
                insights.append(f"👍 Good average rating: {avg_rating:.2f}/5")
            else:
                insights.append(f"👎 Low average rating: {avg_rating:.2f}/5 - needs attention")
        
        if 'City' in df.columns:
            most_active_city = df['City'].mode()[0]
            city_count = (df['City'] == most_active_city).sum()
            insights.append(f"🏙️ Most active city: {most_active_city} ({city_count:,} orders)")
        
        if 'Weather_conditions' in df.columns:
            most_common_weather = df['Weather_conditions'].mode()[0]
            weather_count = (df['Weather_conditions'] == most_common_weather).sum()
            insights.append(f"🌤️ Most common weather: {most_common_weather} ({weather_count:,} orders)")
        
        for insight in insights:
            st.write(insight)
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.write("Please make sure your CSV file is properly formatted.")

else:
    st.info("👆 Please upload your Zomato delivery dataset to start the analysis!")
    
    st.markdown("""
    ### 📋 Instructions:
    
    1. **Download and Upload zomato_delivery_clean_tableau.csv file from github as dataset to uses this app** using the file uploader above
    2. **Github : https://github.com/aarief-s/project-zomato-da**
   
    
    ### 📊 Expected Columns:
    - `Time_taken (min)` - Delivery time
    - `Delivery_person_Ratings` - Ratings (1-5)
    - `City` - Delivery city
    - `Weather_conditions` - Weather conditions
    - `Type_of_vehicle` - Vehicle type
    - And any other columns from your dataset
    """)

# Footer
st.markdown("---")
st.markdown("🍕 **Zomato Delivery Dashboard** | Built with Streamlit")
