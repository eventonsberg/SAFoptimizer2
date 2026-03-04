import streamlit as st
import numpy as np
from optimizer import solve_interdiction
from varying_facility_parameter_visualization import (
    plot_remaining_production_capacity_vs_facility_parameter,
    plot_facility_configuration_vs_facility_parameter,
    plot_costs_vs_facility_parameter
)

def display_varying_facility_parameter(model_inputs):
    F = model_inputs.get("F")
    type_f = model_inputs.get("type_f")
    K_f = model_inputs.get("K_f")
    H_f = model_inputs.get("H_f")
    C_f = model_inputs.get("C_f")
    B = model_inputs.get("B")
    type_b = model_inputs.get("type_b")
    C_b = model_inputs.get("C_b")
    P_b = model_inputs.get("P_b")
    A_b = model_inputs.get("A_b")
    OR = model_inputs.get("OR")
    TE = model_inputs.get("TE")

    facility_name = st.selectbox(
        "Velg fabrikk",
        options=list(set(type_f)),
        key="selected_f_name"
    )
    param_name = st.selectbox(
        "Velg parameter",
        options=["Kapasitet", "Kostnad", "Hardhet"],
        key="selected_p_name"
    )
    col1, col2 = st.columns(2)
    with col1:
        min_param_value = st.number_input(
            "Minimum for valgt parameter",
            value=1.0 if param_name == "Hardhet" else 10,
            step=0.1 if param_name == "Hardhet" else 1,
            min_value=0.0 if param_name == "Hardhet" else 0,
            format="%.1f" if param_name == "Hardhet" else "%d"
        )
    with col2:
        max_param_value = st.number_input(
            "Maksimum for valgt parameter",
            value=5.0 if param_name == "Hardhet" else 100,
            step=0.1 if param_name == "Hardhet" else 1,
            min_value=0.0 if param_name == "Hardhet" else 0,
            format="%.1f" if param_name == "Hardhet" else "%d"
        )
    param_value_step = st.number_input(
        "Steglengde",
        value=0.5 if param_name == "Hardhet" else 10,
        step=0.1 if param_name == "Hardhet" else 1,
        min_value=0.1 if param_name == "Hardhet" else 1,
        format="%.1f" if param_name == "Hardhet" else "%d",
        key="facility_param_step"
    )

    if "varying_facility_parameter_f_name" not in st.session_state:
        st.session_state.varying_facility_parameter_f_name = facility_name
    if "varying_facility_parameter_p_name" not in st.session_state:
        st.session_state.varying_facility_parameter_p_name = param_name
    if "varying_facility_parameter_params" not in st.session_state:
        st.session_state.varying_facility_parameter_params = {}
    if "varying_facility_parameter_results" not in st.session_state:
        st.session_state.varying_facility_parameter_results = {}

    run_optimization = st.button("Kjør optimering", type="primary", key="run_varying_facility_parameter")
    iteration_placeholder = st.empty()
    chart_placeholder = st.empty()
    if st.session_state.varying_facility_parameter_results:
        with chart_placeholder.container():
            st.subheader("Gjenværende produksjonskapasitet etter angrep")
            plot_remaining_production_capacity_vs_facility_parameter()
            st.subheader("Fabrikkonfigurasjon")
            plot_facility_configuration_vs_facility_parameter()
            st.subheader("Kostnader")
            plot_costs_vs_facility_parameter()

    if run_optimization:
        if min_param_value > max_param_value:
            st.error("Minimum verdi for valgt parameter kan ikke være større enn maksimum.")
            return
        if param_name == "Hardhet": # Float value, round to 1 decimal place
            param_values = np.round(np.arange(min_param_value, max_param_value + (param_value_step/2), param_value_step), 1)
        else: # Integer value
            param_values = np.arange(min_param_value, max_param_value + (param_value_step/2), param_value_step)
        st.session_state.varying_facility_parameter_results = {}
        for param_value in param_values:
            K_f_mod = K_f.copy()
            C_f_mod = C_f.copy()
            H_f_mod = H_f.copy()
            facility_indices = [i for i, t in enumerate(type_f) if t == facility_name]
            for idx in facility_indices:
                if param_name == "Kapasitet":
                    K_f_mod[idx] = int(param_value)
                elif param_name == "Kostnad":
                    C_f_mod[idx] = param_value
                elif param_name == "Hardhet":
                    H_f_mod[idx] = param_value
            result = solve_interdiction(F, type_f, K_f_mod, H_f_mod, C_f_mod, B, C_b, P_b, A_b, OR, TE, 
                                        iteration_placeholder=iteration_placeholder,
                                        iteration_detail=f"{param_name}: {param_value}"
            )
            if result["status"] != "OPTIMAL":
                st.error(f"Optimeringen feilet for {param_name} {param_value} med status: {result['status']}")
                continue
            st.session_state.varying_facility_parameter_f_name = facility_name
            st.session_state.varying_facility_parameter_p_name = param_name
            st.session_state.varying_facility_parameter_params = {
                "F": F,
                "type_f": type_f,
                "C_f": C_f_mod,
                "B": B,
                "type_b": type_b,
                "C_b": C_b,
                "OR": OR
            }
            # Store C_f_mod in the result for correct plotting later
            result["C_f"] = C_f_mod.copy()
            st.session_state.varying_facility_parameter_results[param_value] = result
            with chart_placeholder.container():
                st.subheader("Gjenværende produksjonskapasitet etter angrep")
                plot_remaining_production_capacity_vs_facility_parameter()
                st.subheader("Fabrikkonfigurasjon")
                plot_facility_configuration_vs_facility_parameter()
                st.subheader("Kostnader")
                plot_costs_vs_facility_parameter()