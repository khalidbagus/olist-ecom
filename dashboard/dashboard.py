import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import folium
import requests
from streamlit_folium import folium_static
import requests
import calendar
import json


sns.set(style='whitegrid')

bStates = pd.read_csv("output/final_dataframe.csv")
bSellers = pd.read_csv("output/product_stats_dataframe.csv")
bTopSellers = pd.read_csv("output/top_sellers.csv")
bProducts = pd.read_csv("output/seller_aggregated_dataframe.csv")
bCities = pd.read_csv("output/cities_by_state.csv")

bTopSeasonalSales = pd.read_csv("output/top_seasonal_sales.csv")
bBottomSeasonalSales = pd.read_csv("output/bottom_seasonal_sales.csv")

brazilian_states = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']


def plot_popular_product_by_state(df):
    fig, ax = plt.subplots(figsize=(14, 8))
    
    sns.barplot(
        data=df.sort_values('Product Sold Count', ascending=False),
        x='State', 
        y='Product Sold Count', 
        hue='Product Category', 
        dodge=False,
        ax=ax
    )
    
    ax.set_title('Most Popular Product Categories by State')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)

    ax.legend(title='Product Category', loc='upper right')
    
    plt.tight_layout()

    st.pyplot(fig)

def plot_customers_and_revenue_by_state(df):
    sorted_final_df = df.sort_values('Total Customer', ascending=False)

    fig, ax1 = plt.subplots(figsize=(14, 8))

    color = 'tab:blue'
    ax1.set_xlabel('State')
    ax1.set_ylabel('Total Customers', color=color)
    sns.barplot(x='State', y='Total Customer', data=sorted_final_df, color=color, alpha=0.6, ax=ax1)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  
    color = 'tab:red'

    ax2.set_ylabel('Total Spent', color=color)
    sns.lineplot(x='State', y='Total Spent', data=sorted_final_df, color=color, marker='o', ax=ax2)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # To ensure the tight layout
    plt.title('Total Customers and Total Revenue by State (Sorted by Total Customers)')

    st.pyplot(fig)

def plot_top_sellers_sales_and_reviews(df):
    fig, ax1 = plt.subplots(figsize=(15, 10))

    sns.barplot(data=df, x='seller_id', y='total_sales', color='lightblue', label='Total Sales', ax=ax1)

    ax2 = ax1.twinx()
    sns.lineplot(data=df, x='seller_id', y='average_review_score', marker='o', color='red', label='Average Review Score', ax=ax2)

    ax1.set_title('Top 20 Sellers: Total Sales and Average Review Score')
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)  # Rotate x-axis labels for better readability
    ax1.set_xlabel('Seller ID')
    ax1.set_ylabel('Total Sales')

    ax2.set_ylabel('Average Review Score')

    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    plt.tight_layout()

    st.pyplot(fig)

def plot_top_seasonal_sales(df):
    season_order = ['Summer', 'Autumn', 'Winter', 'Spring']
    fig, ax = plt.subplots(figsize=(14, 7))
    sns.barplot(data=df, x='product_category_name_english', y='total_sales', hue='season', hue_order=season_order, ax=ax)
    ax.set_title('Seasonal Total Sales for Top Product Categories')
    ax.set_xlabel('Product Category')
    ax.set_ylabel('Total Sales')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    ax.legend(title='Season')
    plt.tight_layout()
    st.pyplot(fig)

def plot_top_seasonal_order_count(df):
    season_order = ['Summer', 'Autumn', 'Winter', 'Spring']
    fig, ax = plt.subplots(figsize=(14, 7))
    sns.barplot(data=df, x='product_category_name_english', y='order_count', hue='season', hue_order=season_order, ax=ax)
    ax.set_title('Seasonal Order Count for Top Product Categories')
    ax.set_xlabel('Product Category')
    ax.set_ylabel('Order Count')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    ax.legend(title='Season')
    plt.tight_layout()
    st.pyplot(fig)

def plot_bottom_seasonal_sales(df):
    season_order = ['Summer', 'Autumn', 'Winter', 'Spring']
    fig, ax = plt.subplots(figsize=(14, 7))
    sns.barplot(data=df, x='product_category_name_english', y='total_sales', hue='season', hue_order=season_order, ax=ax)
    ax.set_title('Seasonal Total Sales for Bottom Product Categories')
    ax.set_xlabel('Product Category')
    ax.set_ylabel('Total Sales')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    ax.legend(title='Season')
    plt.tight_layout()
    st.pyplot(fig)

def plot_bottom_seasonal_order_count(df):
    season_order = ['Summer', 'Autumn', 'Winter', 'Spring']
    fig, ax = plt.subplots(figsize=(14, 7))
    sns.barplot(data=df, x='product_category_name_english', y='order_count', hue='season', hue_order=season_order, ax=ax)
    ax.set_title('Seasonal Order Count for Bottom Product Categories')
    ax.set_xlabel('Product Category')
    ax.set_ylabel('Order Count')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    ax.legend(title='Season')
    plt.tight_layout()
    st.pyplot(fig)

def get_state_geojson(state_code):
    geojson_url = f"https://raw.githubusercontent.com/luizpedone/municipal-brazilian-geodata/master/data/{state_code}.json"
    response = requests.get(geojson_url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to load GeoJSON for state {state_code}")
        return None
    
def aggregate_data_by_city(df, state_code):
    """
    Aggregates data by city for a given state.
    
    :param df: The merged dataframe containing all the information.
    :param state_code: The two-letter code for a Brazilian state.
    :return: A dataframe aggregated at the city level.
    """
    state_df = df[df['customer_state'] == state_code]

    city_aggregated = state_df.groupby('customer_city').agg({
        'order_id': 'nunique',
        'payment_value': 'sum',
        'review_score': 'mean',
        'freight_value': 'sum',
        'product_id': 'nunique',
    }).reset_index()

    city_aggregated.rename(columns={
        'order_id': 'total_orders',
        'payment_value': 'total_sales',
        'review_score': 'average_review_score',
        'freight_value': 'total_freight',
        'product_id': 'total_products_sold'
    }, inplace=True)

    return city_aggregated

def create_state_map(state_code, df):
    state_geojson = get_state_geojson(state_code)
    if state_geojson is None:
        return None

    aggregated_data = aggregate_data_by_city(df, state_code)

    city_data_dict = aggregated_data.set_index('customer_city').to_dict(orient='index')
    for feature in state_geojson['features']:
        city_name = feature['properties']['NOME'].lower()
        if city_name in city_data_dict:
            feature['properties'].update(city_data_dict[city_name])
        else:
            feature['properties'].update({
                'total_orders': 0,
                'total_sales': 0.0,
                'average_review_score': None,
                'total_freight': 0.0,
                'total_products_sold': 0
            })

    state_center = [state_geojson['features'][0]['geometry']['coordinates'][0][0][1],  # latitude
                    state_geojson['features'][0]['geometry']['coordinates'][0][0][0]]  # longitude
    state_map = folium.Map(location=state_center, zoom_start=6)

    def style_function(feature):
        return {
            'fillColor': 'green' if feature['properties']['total_orders'] > 0 else 'gray',
            'color': 'black',
            'weight': 0.5,
            'dashArray': '5, 5',
            'fillOpacity': 0.6
        }

    folium.GeoJson(
        data=state_geojson,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=['NOME', 'total_orders', 'total_sales', 'average_review_score', 'total_freight', 'total_products_sold'],
            aliases=['City:', 'Total Orders:', 'Total Sales (BRL):', 'Average Review Score:', 'Total Freight (BRL):', 'Total Products Sold:'],
            localize=True
        )
    ).add_to(state_map)

    return state_map


with st.sidebar:
    st.image("olist.png")
    mode = st.radio(
        "Choose Dashboard Mode",
        ["Geoanalysis", "All Over Brazil"]
    )


if mode == "Geoanalysis":
    st.title('Geoanalysis Dashboard')
    
    bStates = pd.read_csv('output/final_dataframe.csv')
    bProducts = pd.read_csv('output/seller_aggregated_dataframe.csv')

    seller_state_counts = bProducts['Origin State'].value_counts()

    state_info = bStates.set_index('State').T.to_dict('dict')

    response = requests.get("https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson")
    brazil_geojson = response.json()

    for feature in brazil_geojson["features"]:
        state_code = feature["properties"]["sigla"]
        feature["properties"]["seller_count"] = int(seller_state_counts.get(state_code, 0))
        if state_code in state_info:
            for key, value in state_info[state_code].items():
                feature["properties"][key] = value

    m = folium.Map(location=[-15.78, -47.93], zoom_start=4, tiles="cartodb positron")

    def style_function(feature):
        return {
            'fillOpacity': 0.5,
            'color': 'black',
            'weight': 1
        }

    def highlight_function(feature):
        return {
            'fillColor': '#2aabd2',
            'color': 'green',
            'weight': 3,
            'dashArray': '1',
            'fillOpacity': 0.7
        }

    tooltip = folium.GeoJsonTooltip(
        fields=["sigla", "seller_count", "Popular Product", "Product Category", "Product Sold Count", "Popular Seller", "Total Customer", "Total Spent", "Average review score"],
        aliases=["State:", "Seller Count:", "Popular Product:", "Product Category:", "Product Sold Count:", "Popular Seller:", "Total Customer:", "Total Spent:", "Average Review Score:"],
        localize=True
    )

    folium.Choropleth(
        geo_data=brazil_geojson,
        data=seller_state_counts,
        columns=('Origin State', 'seller_count'),
        key_on='feature.properties.sigla',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        threshold_scale=[1, 50, 200, 400, 675, 950, 1350, 1734],
        nan_fill_color="white",
        legend_name="Number of Sellers by State"
    ).add_to(m)

    geojson_layer = folium.GeoJson(
        data=brazil_geojson,
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=tooltip
    ).add_to(m)

    for feature in brazil_geojson['features']:
        if 'seller_count' in feature['properties']:
            coords = feature['geometry']['coordinates'][0][0]
            x_coords = [coord[0] for coord in coords]
            y_coords = [coord[1] for coord in coords]
            centroid = (sum(y_coords) / len(coords), sum(x_coords) / len(coords))
            label = feature['properties']['sigla']
            folium.Marker(
                location=centroid,
                icon=folium.DivIcon(html=f"<div style='text-align:center;'>{label}</div>"),
                draggable=False,
                keyboard=False,
                disable_3d=True
            ).add_to(m)

    folium_static(m)

    geojson_url_template = "https://raw.githubusercontent.com/luizpedone/municipal-brazilian-geodata/master/data/{state_code}.json"

    option = st.selectbox(
        'Choose State',
        tuple(brazilian_states))
    
    state_map = create_state_map(option, bCities)
    folium_static(state_map)

else:
    st.title('Sales Dashboard')
    
    st.header('Most Popular Product Categories by State')
    plot_popular_product_by_state(bStates)

    st.header('Total Customers and Total Revenue by State')
    plot_customers_and_revenue_by_state(bStates)

    st.header('Seasonal Sales Analysis for Top Product Categories')
    st.subheader('Total Sales')
    plot_top_seasonal_sales(bTopSeasonalSales)

    st.subheader('Order Count')
    plot_top_seasonal_order_count(bTopSeasonalSales)

    st.header('Seasonal Sales Analysis for Bottom Product Categories')
    st.subheader('Total Sales')
    plot_bottom_seasonal_sales(bBottomSeasonalSales)

    st.subheader('Order Count')
    plot_bottom_seasonal_order_count(bBottomSeasonalSales)
