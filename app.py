import streamlit as st
import pandas as pd
import numpy as np

st.title('Sales Trend Analysis')

DATA_URL = './data/online_retail.csv'
MAPPING = {"United Kingdom": (54.7023545, -3.2765753), "France": (46.603354, 1.8883335), "Australia": (-24.7761086, 134.755), "Netherlands": (52.2434979, 5.6343227), "Germany": (51.1638175, 10.4478313), "Norway": (64.5731537, 11.52803643954819), "EIRE": (52.865196, -7.9794599), "Switzerland": (46.7985624, 8.2319736), "Spain": (39.3260685, -4.8379791), "Poland": (52.215933, 19.134422), "Portugal": (39.6621648, -8.1353519), "Italy": (42.6384261, 12.674297), "Belgium": (50.6402809, 4.6667145), "Lithuania": (55.3500003, 23.7499997), "Japan": (36.5748441, 139.2394179), "Iceland": (64.9841821, -18.1059013), "Channel Islands": (49.21230655, -2.1255999596428845), "Denmark": (55.670249, 10.3333283), "Cyprus": (34.9174159, 32.889902651331866), "Sweden": (59.6749712, 14.5208584), "Austria": (47.59397, 14.12456), "Israel": (30.8124247, 34.8594762), "Finland": (63.2467777, 25.9209164), "Bahrain": (26.1551249, 50.5344606), "Greece": (43.2097838, -77.6930602), "Hong Kong": (22.2793278, 114.1628131), "Singapore": (1.357107, 103.8194992), "Lebanon": (40.375713, -76.4626118), "United Arab Emirates": (24.0002488, 53.9994829), "Saudi Arabia": (25.6242618, 42.3528328), "Czech Republic": (49.7439047, 15.3381061), "Canada": (61.0666922, -107.991707), "Unspecified": (27.1556836, 65.6101216), "Brazil": (-10.3333333, -53.2), "USA": (39.7837304, -100.445882), "European Community": (24.2222445, 120.6898197), "Malta": (35.8885993, 14.4476911), "RSA": (-28.8166236, 24.991639)}

def create_lat(x):
    lat = MAPPING[x][0]
    return lat

def create_lon(x):
    lon = MAPPING[x][1]
    return lon

@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    # data.rename(lowercase, axis='columns', inplace=True)
    data = data.drop('index', axis=1)
    data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'])
    data['Date'] = data['InvoiceDate'].dt.date
    data['TotalPrice'] = data['Quantity'] * data['UnitPrice']
    return data
 
data_load_state = st.text('Loading data...')
data = load_data(20000)
data_load_state.text("")


with st.sidebar:
    selected_item = st.multiselect(
                        'Stock Code', 
                        data['StockCode'],
                        default=None
                    )

    # Selected products
    description = data[data['StockCode'].isin(selected_item)]
    products = [i for i in description['Description'].unique()]

    prod = ''
    for i in products:
        prod = prod + i + '\n'

    # Sales per day analysis
    selecte_item_data = data[data['StockCode'].isin(selected_item)]

    sales_per_day = selecte_item_data[['StockCode', 'Date']]
    grouped_df = sales_per_day.groupby(['StockCode', 'Date'])
    count_per_group = grouped_df.size()
    count_per_group = count_per_group.reset_index(name='Sales per Day')

    st.metric("Unique Customers By Selected Items", selecte_item_data['CustomerID'].nunique())
    revenue = "$ " + str(selecte_item_data['TotalPrice'].count().sum())
    st.metric("Total Revenue By Selected Items", revenue)
    
    st.subheader(f'Selected products: \n ')
    st.text(prod)


tab1, tab2, tab3 = st.tabs(["Sales Trends", "Distribution (World)", "Tabular"])

with tab1:
    st.line_chart(
        count_per_group,
        x='Date',
        y='Sales per Day',
        color='StockCode',
        use_container_width=True
    )

with tab2:
    data['lat'] = data['Country'].apply(create_lat)
    data['lon'] = data['Country'].apply(create_lon)
    st.map(
        data,
        latitude='lat',
        longitude='lon',
        size='TotalPrice',
        use_container_width=True,
        zoom=3
    )

with tab3:
    st.dataframe(
        selecte_item_data[['InvoiceNo', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'UnitPrice', 'Country', 'TotalPrice']], 
        hide_index=True,
        use_container_width=True
    )