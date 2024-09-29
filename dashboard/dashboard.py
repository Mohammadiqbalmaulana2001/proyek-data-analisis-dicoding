import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
import urllib
from fungsi import DataAnalyzer,BrazilMapPlotter
from babel.numbers import format_currency

# All Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df = pd.read_csv("../Dataset/all_data.csv")
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

# geolocation dataset
geolocation_df = pd.read_csv("../Dataset/geolocation_silver.csv")
data = geolocation_df.drop_duplicates(subset='customer_unique_id')

for col in datetime_cols:
  all_df[col] = pd.to_datetime(all_df[col])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

with st.sidebar:
    # Menampilkan teks di tengah
    st.markdown("<h1 style='text-align: center;'>Mohammad Iqbal Maulana</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>S1 Teknik Informatika</p>", unsafe_allow_html=True)
    
    # Logo Image
    st.image("./logo-im.png")

    # Date Range
    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Main
main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                  (all_df["order_approved_at"] <= str(end_date))]

fungsi = DataAnalyzer(main_df)
map_plotter = BrazilMapPlotter(data=geolocation_df, plt=plt, mpimg=mpimg, urllib=urllib, st=st)


daily_orders_df = fungsi.create_daily_orders_df()
sum_spend_df = fungsi.create_sum_spend_df()
sum_order_items_df = fungsi.create_sum_order_items_df()
review_score, common_score = fungsi.review_score_df()
state, most_common_state = fungsi.create_bystate_df()
order_status, common_status = fungsi.create_order_status()

st.markdown("<h2 style='text-align: center;'>E-Commerce Dashboard 📦</h2>", unsafe_allow_html=True)

# Daily Orders
st.subheader("Daily Orders")
col1, col2 = st.columns(2)

with col1:
    total_order = daily_orders_df["order_count"].sum()
    st.markdown(f"Total Order: **{total_order}**")
with col2:
    total_revenue = format_currency(daily_orders_df["revenue"].sum(), "IDR", locale="id_ID")
    st.markdown(f"Total Revenue: **{total_revenue}**")

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#ff0000",
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

# Customer Spend Money
st.subheader("Customer Spend Money")
col1, col2 = st.columns(2)

with col1:
    total_spend = format_currency(sum_spend_df["total_spend"].sum(), "IDR", locale="id_ID")
    st.markdown(f"Total Spend: **{total_spend}**")
with col2:
    avg_spend = format_currency(sum_spend_df["total_spend"].mean(), "IDR", locale="id_ID")
    st.markdown(f"Average Spend: **{avg_spend}**")

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    sum_spend_df["order_approved_at"],
    sum_spend_df["total_spend"],
    marker='o', 
    linewidth=2,
    color="#ff0000",
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

# Customer Order Items
st.subheader("Customer Order Items")
col1, col2 = st.columns(2)

with col1:
    total_items = sum_order_items_df["product_count"].sum()
    st.markdown(f"Total Items: **{total_items}**")
with col2:
    avg_items = sum_order_items_df["product_count"].mean()
    st.markdown(f"Average Items: **{avg_items}**")

# Membuat subplots
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 10))  # Ukuran lebih kecil untuk ditampilkan di Streamlit

colors = ["#ff0000", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

# Pastikan y adalah kolom yang berisi nilai numerik
sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel("Product Category")
ax[0].set_xlabel("Total Items Sold")  
ax[0].set_title("Produk Terlaris", loc="center", fontsize=20) 
ax[0].tick_params(axis='y', labelsize=12)

# Untuk produk terendah, ambil 5 produk terendah
sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel("Product Category")  
ax[1].set_xlabel("Total Items Sold")  
ax[1].invert_xaxis() 
ax[1].yaxis.set_label_position("right") 
ax[1].yaxis.tick_right()
ax[1].set_title("Produk Terendah", loc="center", fontsize=20)
ax[1].tick_params(axis='y', labelsize=12)

plt.suptitle("Produk Terlaris dan Terendah", fontsize=24) 
plt.subplots_adjust(top=0.85, wspace=0.3)  
st.pyplot(fig)

# Review Score
st.subheader("Review Score")
col1, col2 = st.columns(2)

with col1:
    review_score_count = review_score.mean()
    st.markdown(f"Average Review Score: **{review_score_count}**")
with col2:
    most_common_score = review_score.value_counts().idxmax()
    st.markdown(f"Most Common Review Score: **{most_common_score}**")

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x=review_score.index, 
            y=review_score.values, 
            order=review_score.index,
            palette=["#ff0000" if score == common_score else "#D3D3D3" for score in review_score.index]
            )

plt.title("Rating by customers for service", fontsize=15)
plt.xlabel("Rating")
plt.ylabel("Count")
plt.xticks(fontsize=12)
st.pyplot(fig)

# geolocation 
st.subheader("Geolocation")
tab1,tab2,tab3 = st.tabs(["State","Order Status","Geolocation"])

with tab1:
    most_common_state = state.customer_state.value_counts().index[0]
    st.markdown(f"Most Common State: **{most_common_state}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=state.customer_state.value_counts().index,
                y=state.customer_count.values, 
                data=state,
                palette=["#ff0000" if score == most_common_state else "#D3D3D3" for score in state.customer_state.value_counts().index]
                    )

    plt.title("Number customers from State", fontsize=15)
    plt.xlabel("State")
    plt.ylabel("Number of Customers")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

with tab2:
    common_status_ = order_status.value_counts().index[0]
    st.markdown(f"Most Common Order Status: **{common_status_}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=order_status.index,
                y=order_status.values,
                order=order_status.index,
                palette=["#ff0000" if score == common_status else "#D3D3D3" for score in order_status.index]
                )
    
    plt.title("Order Status", fontsize=15)
    plt.xlabel("Status")
    plt.ylabel("Count")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

with tab3:
    map_plotter.plot()