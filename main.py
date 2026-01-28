import streamlit as st
from input_data import display_input_fields, format_model_inputs
from single_solution import display_single_solution
from varying_missile_budget import display_varying_missile_budget

st.set_page_config(
    page_title="SAF optimizer",
    page_icon=":material/travel:"
)

input_data = display_input_fields()
model_inputs = format_model_inputs(input_data)

st.subheader("Optimal løsning")
tab1, tab2 = st.tabs(["Enkeltløsning", "Varierende missilbudsjett"])

with tab1:
    display_single_solution(*model_inputs)

with tab2:
    display_varying_missile_budget(*model_inputs)