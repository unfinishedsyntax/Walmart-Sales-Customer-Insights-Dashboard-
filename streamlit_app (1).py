
import streamlit as st
import pandas as pd
import plotly.express as px
import os

@st.cache_data
def load_data():
    file_path = "src/walmart_clean_data.csv"
    if not os.path.exists(file_path):
        st.error(f"❌ File '{file_path}' not found! Please upload it in your Space.")
        return pd.DataFrame()
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip().str.lower()
    df['date'] = pd.to_datetime(df['date'])
    df['hour'] = pd.to_datetime(df['time']).dt.hour
    df['weekday'] = df['date'].dt.day_name()
    return df

df = load_data()

if df.empty:
    st.stop()

# Sidebar filters
st.sidebar.header("Filter Data")
branch = st.sidebar.multiselect("Select Branch", df['branch'].unique(), default=df['branch'].unique())
category = st.sidebar.multiselect("Select Category", df['category'].unique(), default=df['category'].unique())
date_range = st.sidebar.date_input("Select Date Range", [df['date'].min(), df['date'].max()])

# Filtered data
filtered_df = df[(df['branch'].isin(branch)) &
                 (df['category'].isin(category)) &
                 (df['date'] >= pd.to_datetime(date_range[0])) &
                 (df['date'] <= pd.to_datetime(date_range[1]))]

st.title("🛒 Walmart Sales & Customer Insights Dashboard")

# Calculate total sales manually
# Ensure correct data types before multiplication
filtered_df['unit_price'] = pd.to_numeric(filtered_df['unit_price'], errors='coerce')
filtered_df['quantity'] = pd.to_numeric(filtered_df['quantity'], errors='coerce')
filtered_df.dropna(subset=['unit_price', 'quantity'], inplace=True)
filtered_df['total'] = filtered_df['unit_price'] * filtered_df['quantity']


col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"₹{filtered_df['total'].sum():,.2f}")
col2.metric("Average Rating", f"{filtered_df['rating'].mean():.2f} ⭐")
col3.metric("Total Transactions", f"{filtered_df.shape[0]}")

st.subheader("Revenue by Category")
revenue_by_category = filtered_df.groupby('category')['total'].sum().reset_index()
fig1 = px.bar(revenue_by_category, x='category', y='total', color='category', title="Total Revenue by Category")
st.plotly_chart(fig1)

st.subheader("Daily Sales Trend")
daily_sales = filtered_df.groupby('date')['total'].sum().reset_index()
fig2 = px.line(daily_sales, x='date', y='total', title='Daily Sales Trend')
st.plotly_chart(fig2)

st.subheader("Sales by Hour and Weekday")
heatmap_data = filtered_df.groupby(['weekday', 'hour'])['total'].sum().reset_index()
heatmap_pivot = heatmap_data.pivot(index='weekday', columns='hour', values='total')
heatmap_pivot = heatmap_pivot.reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
st.dataframe(heatmap_pivot.style.background_gradient(cmap='Blues'))

st.subheader("Sales by Payment Method")
payment_sales = filtered_df.groupby('payment_method')['total'].sum().reset_index()
fig3 = px.pie(payment_sales, names='payment_method', values='total', title='Sales by Payment Method')
st.plotly_chart(fig3)

st.subheader("Ratings Distribution by Branch")
fig4 = px.violin(filtered_df, x='branch', y='rating', box=True, points='all', color='branch')
st.plotly_chart(fig4)

st.markdown("---")
st.markdown("Made by Ashutosh Kumar")






