# Import python packages
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, when_matched
import requests

# Debug (pour vérifier que c'est la bonne version)
st.write("VERSION FINALE OK")

# Create Snowflake session (via Streamlit secrets)
session = Session.builder.configs(st.secrets["snowflake"]).create()

st.success("Connected to Snowflake!")

# Title
st.title(f"🥤 Smoothie App - Streamlit {st.__version__}")
st.write("Create and manage your smoothie orders!")

# Load fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Convert Snowpark DataFrame → Python list
fruit_rows = my_dataframe.collect()
fruit_list = [row['FRUIT_NAME'] for row in fruit_rows]

# Input: smoothie name
name_on_order = st.text_input('Name of Smoothie')

# Multiselect fruits
#ingredients_list = st.multiselect(
#    "What are your favorite fruits?",
#    fruit_list,
#    max_selections=5
#)

# Build ingredients string
#INGREDIENTS_STRING = ' '.join(ingredients_list)

#
if ingredients_list:
    INGREDIENTS_STRING = ''

    for fruit_chosen in ingredients_list:
        INGREDIENTS_STRING += INGREDIENTS_STRING + ' '
        #request
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
        #st.text(smoothiefroot_response.json())
        sf_sd = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)



    
# Button to insert order
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

# =========================
# UPDATE SECTION (MERGE)
# =========================

st.subheader("Update Orders")

# Load orders into pandas
orders_df = session.table("smoothies.public.orders").to_pandas()

# Editable table
edited_df = st.data_editor(orders_df)

# Update button
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


