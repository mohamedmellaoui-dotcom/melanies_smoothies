# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
from snowflake.snowpark.context import get_active_session
import streamlit as st
from snowflake.snowpark.functions import col, when_matched

# Write directly to the app
st.title(f"cup_with_straw: {st.__version__}")
st.write(
  """Replace this example with your own code!
  **And if you're new to Streamlit,** check
  out our easy-to-follow guides at
  [docs.streamlit.io](https://docs.streamlit.io).
  """
)

#option = st.selectbox(
#    "What is your favorite fruit",
#    ("Email", "Home phone", "Mobile phone"),
#)

#st.write("You selected:", option)



session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'));
#st.dataframe(data=my_dataframe, use_container_width=True)

name_on_order = st.text_input('Name of Smoothie')
st.write('The name of your Smoothie will be:', name_on_order)

ingredients_list = st.multiselect(
    "What are your favorite colors?",
    my_dataframe,
    max_selections = 5
)
#if ingredients_list:
#    st.write(ingredients_list)
#    st.text(ingredients_list)
INGREDIENTS_STRING = ''

for fruit_chosen in ingredients_list:
        INGREDIENTS_STRING +=fruit_chosen + ' '
        #st.write(INGREDIENTS_STRING)

my_insert_stmt = """ insert into smoothies.public.orders(ingredients,NAME_ON_ORDER)
                    values ('""" + INGREDIENTS_STRING + """', '""" + name_on_order + """')"""



tim_to_insert = st.button('Submit Order')

st.write(my_insert_stmt)
#st.stop()
if tim_to_insert:
       session.sql(my_insert_stmt).collect()
       st.success('Your Smoothie is ordered!', icon="✅")

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
