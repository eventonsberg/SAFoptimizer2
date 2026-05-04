import streamlit as st
import numpy as np
from optimizer import solve_interdiction
from varying_facility_parameter_visualization import (
    plot_remaining_production_capacity_vs_facility_parameter,
    plot_facility_configuration_vs_facility_parameter,
    plot_costs_vs_facility_parameter,
    plot_bio_production_vs_facility_parameter
)

def display_varying_facility_parameter(model_inputs):
    F = model_inputs.get("F")
    type_f = model_inputs.get("type_f")
    K_f = model_inputs.get("K_f")
    H_f = model_inputs.get("H_f")
    C_f = model_inputs.get("C_f")
    beta_f = model_inputs.get("beta_f")
    B = model_inputs.get("B")
    type_b = model_inputs.get("type_b")
    C_b = model_inputs.get("C_b")
    P_b = model_inputs.get("P_b")
    A_b = model_inputs.get("A_b")
    OE = model_inputs.get("OE")
    T = model_inputs.get("T")
    R = model_inputs.get("R")

    facility_name = st.segmented_control(
        "Velg fabrikk",
        options=list(dict.fromkeys(type_f)),
        default=type_f[0],
        key="facility_name"
    )
    if not facility_name:
        st.warning("Velg fabrikk")
        return
    param_name = st.segmented_control(
        "Velg parameter",
        options=["Kostnad", "Kapasitet", "Hardhet"],
        default="Kostnad",
        key="facility_param_name"
    )
    if not param_name:
        st.warning("Velg parameter")
        return
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
            st.subheader("Biodrivstoff")
            plot_bio_production_vs_facility_parameter()

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
            facility_indices = [f for f, t in enumerate(type_f) if t == facility_name]
            for f in facility_indices:
                if param_name == "Kapasitet":
                    K_f_mod[f] = int(param_value)
                elif param_name == "Kostnad":
                    C_f_mod[f] = param_value
                elif param_name == "Hardhet":
                    H_f_mod[f] = param_value
            result = solve_interdiction(F, type_f, K_f_mod, H_f_mod, C_f_mod, beta_f, B, C_b, P_b, A_b, OE, T, R,
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
                "beta_f": beta_f,
                "B": B,
                "type_b": type_b,
                "C_b": C_b,
                "OE": OE,
                "R": R
            }
            # Store K_f_mod and C_f_mod in the result for correct plotting
            result["K_f"] = K_f_mod.copy()
            result["C_f"] = C_f_mod.copy()
            st.session_state.varying_facility_parameter_results[param_value] = result
            with chart_placeholder.container():
                st.subheader("Gjenværende produksjonskapasitet etter angrep")
                plot_remaining_production_capacity_vs_facility_parameter()
                st.subheader("Fabrikkonfigurasjon")
                plot_facility_configuration_vs_facility_parameter()
                st.subheader("Kostnader")
                plot_costs_vs_facility_parameter()
                st.subheader("Biodrivstoff")
                plot_bio_production_vs_facility_parameter()