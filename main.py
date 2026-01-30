import streamlit as st
from model_description import display_model_description
from input_data import display_input_fields, format_model_inputs
from single_solution import display_single_solution
from varying_missile_budget import display_varying_missile_budget
from varying_f_and_ad_budget import display_varying_f_and_ad_budget
from missile_budget_vs_f_and_ad_budget import display_varying_missile_budget_vs_f_and_ad_budget

st.set_page_config(
    page_title="SAF optimizer",
    page_icon=":material/travel:"
)

display_model_description()

input_data = display_input_fields()
model_inputs = format_model_inputs(input_data)

st.subheader("Optimal løsning")
tab1, tab2, tab3, tab4 = st.tabs([
    "Enkeltløsning",
    "Varierende missilbudsjett",
    "Varierende fabrikk- og luftvernbudsjett",
    "Missilbudsjett vs. fabrikk- og luftvernbudsjett"
])

with tab1:
    display_single_solution(*model_inputs)

with tab2:
    display_varying_missile_budget(*model_inputs)

with tab3:
    display_varying_f_and_ad_budget(*model_inputs)

with tab4:
    display_varying_missile_budget_vs_f_and_ad_budget(*model_inputs)