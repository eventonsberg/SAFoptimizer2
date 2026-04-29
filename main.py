import streamlit as st
from model_description import display_model_description
from input_data import display_input_fields, format_model_inputs
from single_solution import display_single_solution
from varying_facility_parameter import display_varying_facility_parameter
from varying_protection_measure_parameter import display_varying_protection_measure_parameter
from varying_blue_budget import display_varying_blue_budget
from varying_red_budget import display_varying_red_budget
from blue_vs_red_budget import display_blue_vs_red_budget
from varying_bio_budget import display_varying_bio_budget
from sensitivity_analysis import display_sensitivity_analysis

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
        "Varierende fabrikkparameter",
        "Varierende beskyttelsestiltak-parameter",
        "Varierende blått budsjett",
        "Varierende rødt budsjett",
        "Blått vs. rødt budsjett",
        "Varierende biobudsjett",
        "Sensitivitetsanalyse"
    ]
)

st.divider()
st.subheader(analysis)

if analysis == "Enkeltløsning":
    display_single_solution(model_inputs)
elif analysis == "Varierende fabrikkparameter":
    display_varying_facility_parameter(model_inputs)
elif analysis == "Varierende beskyttelsestiltak-parameter":
    display_varying_protection_measure_parameter(model_inputs)
elif analysis == "Varierende blått budsjett":
    display_varying_blue_budget(model_inputs)
elif analysis == "Varierende rødt budsjett":
    display_varying_red_budget(model_inputs)
elif analysis == "Blått vs. rødt budsjett":
    display_blue_vs_red_budget(model_inputs)
elif analysis == "Varierende biobudsjett":
    display_varying_bio_budget(model_inputs)
elif analysis == "Sensitivitetsanalyse":
    display_sensitivity_analysis(model_inputs)
