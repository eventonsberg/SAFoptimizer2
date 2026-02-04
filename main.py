import streamlit as st
from model_description import display_model_description
from input_data import display_input_fields, format_model_inputs
from single_solution import display_single_solution
from sensitivity_analysis import display_sensitivity_analysis
from varying_missile_budget import display_varying_missile_budget
from varying_f_and_ad_budget import display_varying_f_and_ad_budget
from missile_budget_vs_f_and_ad_budget import display_varying_missile_budget_vs_f_and_ad_budget
from varying_air_defense_cost import display_varying_air_defense_cost
from varying_ad_success_rate import display_varying_ad_success_rate
from varying_facility_parameter import display_varying_facility_parameter

st.set_page_config(
    page_title="SAF optimizer",
    page_icon=":material/travel:"
)

display_model_description()

input_data = display_input_fields()
model_inputs = format_model_inputs(input_data)

st.subheader("Optimal løsning")
tabs = st.tabs([
    "Enkeltløsning",
    "Sensitivitetsanalyse",
    "Varierende missilbudsjett",
    "Varierende fabrikk- og luftvernbudsjett",
    "Missilbudsjett vs. fabrikk- og luftvernbudsjett",
    "Varierende luftvernkostnad",
    "Varierende suksessrate",
    "Varierende fabrikkparameter"
])

with tabs[0]:
    display_single_solution(*model_inputs)

with tabs[1]:
    display_sensitivity_analysis(*model_inputs)

with tabs[2]:
    display_varying_missile_budget(*model_inputs)

with tabs[3]:
    display_varying_f_and_ad_budget(*model_inputs)

with tabs[4]:
    display_varying_missile_budget_vs_f_and_ad_budget(*model_inputs)

with tabs[5]:
    display_varying_air_defense_cost(*model_inputs)

with tabs[6]:
    display_varying_ad_success_rate(*model_inputs)

with tabs[7]:
    display_varying_facility_parameter(*model_inputs)