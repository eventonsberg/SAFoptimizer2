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

analysis = st.sidebar.radio(
    "**Velg ønsket analyse:**",
    [
        "Enkeltløsning",
        "Sensitivitetsanalyse",
        "Varierende fabrikkparameter",
        "Varierende kostnad per luftvernmissil",
        "Varierende suksessrate for luftvern",
        "Varierende fabrikk- og luftvernbudsjett",
        "Varierende missilbudsjett",
        "Missilbudsjett vs. fabrikk- og luftvernbudsjett",
    ]
)

st.divider()
st.subheader(analysis)

if analysis == "Enkeltløsning":
    display_single_solution(*model_inputs)
elif analysis == "Sensitivitetsanalyse":
    display_sensitivity_analysis(*model_inputs)
elif analysis == "Varierende missilbudsjett":
    display_varying_missile_budget(*model_inputs)
elif analysis == "Varierende fabrikk- og luftvernbudsjett":
    display_varying_f_and_ad_budget(*model_inputs)
elif analysis == "Missilbudsjett vs. fabrikk- og luftvernbudsjett":
    display_varying_missile_budget_vs_f_and_ad_budget(*model_inputs)
elif analysis == "Varierende kostnad per luftvernmissil":
    display_varying_air_defense_cost(*model_inputs)
elif analysis == "Varierende suksessrate for luftvern":
    display_varying_ad_success_rate(*model_inputs)
elif analysis == "Varierende fabrikkparameter":
    display_varying_facility_parameter(*model_inputs)