import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry

countries = {}

for country in pycountry.countries:
    countries[country.name] = country.alpha_3

def get_iso_code(country):
    iso_code = countries.get(country, 'Unknown code')
    if iso_code == 'Unknown code':
        return country
    return iso_code

st.title('Sales Trend Analysis')

DATA_URL = './data/online_retail.csv'

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
    description['items'] = description['StockCode'] + ' - ' + description['Description']
    products = [i for i in description['items'].unique()]

    prod = ''
    for i in products:
        prod = prod + i + '\n'

    # Sales per day analysis
    selecte_item_data = data[data['StockCode'].isin(selected_item)]

    sales_per_day = selecte_item_data[['StockCode', 'Date']]
    grouped_df = sales_per_day.groupby(['StockCode', 'Date'])
    count_per_group = grouped_df.size()
    count_per_group = count_per_group.reset_index(name='Sales per Day')
    
    selecte_item_data['CountryCode'] = selecte_item_data['Country'].apply(get_iso_code)
    map_data = selecte_item_data[['Quantity', 'TotalPrice', 'CountryCode', 'Country']]
    # total sales for a country
    grouped_df = map_data.groupby('CountryCode')[['Quantity', 'TotalPrice']].sum()
    sales_per_group = grouped_df.reset_index()

    country_sales = [i for i in map_data['Country'].unique()]
    count = ''
    for i in country_sales:
        count = count + i + '\n'

    row1 = st.columns(2)
    row2 = st.columns(2)

    with row1[0]:
        st.metric("Unique Customers", selecte_item_data['CustomerID'].nunique())
    
    with row1[1]:
        items_sold = selecte_item_data['Quantity'].sum()
        st.metric("Total Quantity", items_sold)
    
    with row2[0]:
        sales = "$ " + str(round(selecte_item_data['TotalPrice'].sum(), 2))
        st.metric("Total Sales", sales)

    st.subheader(f'Selected products: \n ')
    st.text(prod)

    st.subheader('Countries:')
    st.text(count)


tab1, tab2, tab3, tab4 = st.tabs(["Sales Trends", "Distribution (World)", "Tabular", "Stats"])

with tab1:
    st.area_chart(
        count_per_group,
        x='Date',
        y='Sales per Day',
        color='StockCode',
        use_container_width=True
    )

with tab2:
    fig = px.choropleth(sales_per_group, 
                        locations="CountryCode",
                        color="TotalPrice", # lifeExp is a column of gapminder
                        hover_name="Quantity", # column to add to hover information
                        color_continuous_scale=px.colors.sequential.Rainbow
                    )
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with tab3:
    st.dataframe(
        selecte_item_data[['InvoiceNo', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'UnitPrice', 'Country', 'TotalPrice']], 
        hide_index=True,
        use_container_width=True
    )

with tab4:

    r1 = st.columns(2)

    with r1[0]:
        fig_2 = px.pie(
            map_data, 
            values='Quantity', 
            names='Country', 
            title='Quantity per Country'
        )
        st.plotly_chart(fig_2, theme="streamlit", use_container_width=True)
    
    with r1[1]:
        group_per_country = selecte_item_data.groupby('Country')['CustomerID'].nunique()
        customer_per_country = group_per_country.reset_index()
        fig_3 = px.pie(
            customer_per_country, 
            values='CustomerID', 
            names='Country', 
            title='Customers Distribution'
        )
        st.plotly_chart(fig_3, theme="streamlit", use_container_width=True)

    fig_3 = px.pie(
        map_data, 
        values='TotalPrice', 
        names='Country', 
        title='Sales(Revenue) per Country'
    )
    st.plotly_chart(fig_3, theme="streamlit", use_container_width=True)
    