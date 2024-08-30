import streamlit as st
import pandas as pd
import sqlite3

#from IPython.display import display, HTML

st.set_page_config(layout='wide', page_title='Rental Analysis')
cnn = sqlite3.connect('sqlite-sakila.db')

def top_5_cities(data):

    query_1 = """SELECT city, COUNT(c.customer_id) AS "Customer Count" 
    FROM customer c 
    JOIN address a 
    ON c.address_id = a.address_id
    JOIN city ct 
    ON a.city_id=ct.city_id 
    GROUP BY city 
    ORDER BY "Customer Count" DESC 
    LIMIT 5"""

    top_cities = pd.read_sql_query(query_1, data)

    st.dataframe(top_cities)
    st.write("### SQL Query")
    st.code(query_1, language = 'sql')

def revenue_per_customer(data):

    query_2 = """SELECT c.customer_id AS ID, first_name || ' ' || last_name AS Name, payment_date, 
    SUM(amount) OVER 
    (PARTITION BY c.customer_id 
    ORDER BY payment_date 
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
    AS "Amount" 
    FROM customer c JOIN payment p 
    ON c.customer_id=p.customer_id 
    ORDER BY c.customer_id"""

    cust_rev = pd.read_sql_query(query_2, cnn)

    customer_dict = cust_rev.set_index('ID')['Name'].to_dict()
    options = [f"{key}: {value}" for key, value in customer_dict.items()]

    selected = st.sidebar.selectbox("Select 'customer key : name' pair", options)

    id = int(str(selected).split(':')[0])
    desired = cust_rev.loc[cust_rev['ID']==id]
    total = cust_rev.loc[cust_rev['ID']==id]['Amount'].sum()

    cl1, cl2 = st.columns(2)

    with cl1:
        st.dataframe(desired)

    with cl2:
        st.write("### Total Revenue")
        st.text(total)

    st.write("### SQL Query")
    st.code(query_2, language='sql')

def top_movies(data):
    query_3 = """SELECT f.film_id, title AS Title, name AS Category, COUNT(f.film_id) AS "Rental Count",
    RANK() OVER (ORDER BY COUNT(f.film_id) DESC) AS "Rental Rank"
    FROM film f 
    JOIN film_category fc
    ON f.film_id = fc.film_id 
    JOIN category ct
    ON fc.category_id = ct.category_id
    JOIN inventory i 
    ON f.film_id = i.film_id 
    JOIN rental r 
    ON i.inventory_id = r.inventory_id
    GROUP BY f.film_id, title, name
    ORDER BY "Rental Count" 
    DESC"""

    l = list(range(1,101))
    selected = st.sidebar.selectbox('Select a number to view top n movies', l)
    n = selected-1
    t_m = pd.read_sql_query(query_3, data).loc[:n]

    st.dataframe(t_m)
    st.write('### SQL Query')
    st.code(query_3, language='sql')


st.sidebar.title('Rental Analysis')
st.sidebar.write('### To view complete code of deployment, visit the github repo: https://github.com/Ankit27596/Rental_analysis_SQL_Python')
selected = st.sidebar.selectbox('Select one', ['Database structure', 'Customer revenue', 'Top 5 cities with most customers',
                                               'Top rented movies'])

if selected == 'Database structure':
    st.image('SQLite3 Sakila Sample Database ERD.png')
elif selected == 'Top 5 cities with most customers':
    st.title('Top 5 cities with most customers')
    top_5_cities(cnn)
elif selected == 'Customer revenue':
    st.title('Customer report')
    revenue_per_customer(cnn)
elif selected == 'Top rented movies':
    st.title('Top movies')
    top_movies(cnn)
