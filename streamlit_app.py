# Import python packages
import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col
import requests


# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

name_on_order = st.text_input("Name on Smoothie: ")
st.write("Name on Smoothie will be: "+name_on_order)


cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options")
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()

pd_df = my_dataframe.to_pandas()
# st.dataframe(pd_df)
# st.stop()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients!",
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ""
    for ingredient in ingredients_list:
        ingredients_string += ingredient + " "

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == ingredient, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', ingredient,' is ', search_on, '.')
        
        st.subheader(ingredient + ' Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + ingredient)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

    st.write(ingredients_string)
    
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order) values ('""" + ingredients_string + """','"""+name_on_order+"""')"""
    submit = st.button("Submit Order")

    if submit:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")


