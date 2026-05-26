# Import python packages
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, when_matched
import requests
import pandas as pd

# Snowflake session
session = Session.builder.configs(st.secrets["snowflake"]).create()
st.success("Connected to Snowflake!")

st.title(f"🥤 Smoothie App - Streamlit {st.__version__}")
st.write("Create and manage your smoothie orders!")

# Load fruits
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col('FRUIT_NAME'), col('SEARCH_ON'))

st.dataframe(data=my_dataframe, use_container_width=True)

# Convert to pandas
pd_pf = my_dataframe.to_pandas()

# Create fruit list
fruit_list = pd_pf['FRUIT_NAME'].tolist()

# Name input
name_on_order = st.text_input('Name of Smoothie')

# Multiselect
ingredients_list = st.multiselect(
    "What are your favorite fruits?",
    fruit_list,
    max_selections=5
)

# Process selection
INGREDIENTS_STRING = ''

if ingredients_list:
    for fruit_chosen in ingredients_list:
        INGREDIENTS_STRING += fruit_chosen + ' '

        # ✅ FIX variable name + indentation
        search_on = pd_pf.loc[
            pd_pf['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'
        ].iloc[0]

        st.write(f"The search value for {fruit_chosen} is {search_on}")

        st.subheader(f"{fruit_chosen} Nutrition Informations")

        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

# INSERT
tim_to_insert = st.button('Submit Order')

if tim_to_insert:
    if name_on_order and INGREDIENTS_STRING:
        session.sql(
            "INSERT INTO smoothies.public.orders(ingredients, NAME_ON_ORDER) VALUES (?, ?)",
            params=[INGREDIENTS_STRING, name_on_order]
        ).collect()

        st.success('Your Smoothie is ordered!', icon="✅")
    else:
        st.warning("Please enter a name and select at least one fruit.")

# UPDATE
st.subheader("Update Orders")

orders_df = session.table("smoothies.public.orders").to_pandas()
edited_df = st.data_editor(orders_df)

update_button = st.button("Update Orders")

if update_button:
    og_dataset = session.table("smoothies.public.orders")
    edited_dataset = session.create_dataframe(edited_df)

    og_dataset.merge(
        edited_dataset,
        og_dataset["ORDER_UID"] == edited_dataset["ORDER_UID"],
        [
            when_matched().update({
                "ORDER_FILLED": edited_dataset["ORDER_FILLED"]
            })
        ]
    )

    st.success("Orders updated!", icon="✅")
