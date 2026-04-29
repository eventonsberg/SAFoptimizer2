import streamlit as st
import numpy as np
from optimizer import solve_interdiction
from varying_protection_measure_parameter_visualization import (
    plot_remaining_production_capacity_vs_protection_measure_parameter,
    plot_facility_configuration_vs_protection_measure_parameter,
    plot_costs_vs_protection_measure_parameter
)

def display_varying_protection_measure_parameter(model_inputs):
    F = model_inputs.get("F")
    type_f = model_inputs.get("type_f")
    K_f = model_inputs.get("K_f")
    H_f = model_inputs.get("H_f")
    C_f = model_inputs.get("C_f")
    beta_f = model_inputs.get("beta_f")
    B = model_inputs.get("B")
    type_b = model_inputs.get("type_b")
    C_b = model_inputs.get("C_b")
    effector_b = model_inputs.get("effector_b")
    P_b = model_inputs.get("P_b")
    A_b = model_inputs.get("A_b")
    OE = model_inputs.get("OE")
    T = model_inputs.get("T")
    R = model_inputs.get("R")

    dimension = st.segmented_control(
        "Velg parameterdimensjon",
        options=["Effektor", "Beskyttelsestiltak"],
        default="Beskyttelsestiltak",
        key="protection_measure_dimension"
    )
    if not dimension:
        st.warning("Velg parameterdimensjon")
        return
    type_name = st.segmented_control(
        f"Velg {dimension.casefold()}",
        options=list(dict.fromkeys(effector_b)) if dimension == "Effektor" else list(dict.fromkeys(type_b)),
        default=effector_b[0] if dimension == "Effektor" else type_b[0],
        key="protection_measure_type"
    )
    if not type_name:
        st.warning(f"Velg {dimension.casefold()}")
        return
    param_name = st.segmented_control(
        "Velg parameter",
        options=["Suksessrate"] if dimension == "Effektor" else ["Kostnad", "Antall effektorer"],
        default="Suksessrate" if dimension == "Effektor" else "Kostnad",
        key="protection_measure_param"
    )
    if not param_name:
        st.warning("Velg parameter")
        return
    col1, col2 = st.columns(2)
    with col1:
        min_param_value = st.number_input(
            "Minimum for valgt parameter",
            value=0.5 if param_name == "Suksessrate" else 10,
            step=0.01 if param_name == "Suksessrate" else 1,
            min_value=0.0 if param_name == "Suksessrate" else 0,
            max_value=1.0 if param_name == "Suksessrate" else None,
            format="%.2f" if param_name == "Suksessrate" else "%d",
            key="min_protection_measure_param_value"
        )
    with col2:
        max_param_value = st.number_input(
            "Maksimum for valgt parameter",
            value=1.0 if param_name == "Suksessrate" else 20,
            step=0.01 if param_name == "Suksessrate" else 1,
            min_value=0.0 if param_name == "Suksessrate" else 0,
            max_value=1.0 if param_name == "Suksessrate" else None,
            format="%.2f" if param_name == "Suksessrate" else "%d",
            key="max_protection_measure_param_value"
        )
    param_value_step = st.number_input(
        "Steglengde",
        value=0.05 if param_name == "Suksessrate" else 1,
        step=0.01 if param_name == "Suksessrate" else 1,
        min_value=0.01 if param_name == "Suksessrate" else 1,
        max_value=1.0 if param_name == "Suksessrate" else None,
        format="%.2f" if param_name == "Suksessrate" else "%d",
        key="protection_measure_param_step"
    )

    if "varying_protection_measure_parameter_type_name" not in st.session_state:
        st.session_state.varying_protection_measure_parameter_type_name = type_name
    if "varying_protection_measure_parameter_param_name" not in st.session_state:
        st.session_state.varying_protection_measure_parameter_param_name = param_name
    if "varying_protection_measure_parameter_params" not in st.session_state:
        st.session_state.varying_protection_measure_parameter_params = {}
    if "varying_protection_measure_parameter_results" not in st.session_state:
        st.session_state.varying_protection_measure_parameter_results = {}

    run_optimization = st.button("Kjør optimering", type="primary", key="run_varying_protection_measure_parameter")
    iteration_placeholder = st.empty()
    chart_placeholder = st.empty()
    if st.session_state.varying_protection_measure_parameter_results:
        with chart_placeholder.container():
            st.subheader("Gjenværende produksjonskapasitet etter angrep")
            plot_remaining_production_capacity_vs_protection_measure_parameter()
            st.subheader("Fabrikkonfigurasjon")
            plot_facility_configuration_vs_protection_measure_parameter()
            st.subheader("Kostnader")
            plot_costs_vs_protection_measure_parameter()

    if run_optimization:
        if min_param_value > max_param_value:
            st.error("Minimum verdi for valgt parameter kan ikke være større enn maksimum.")
            return
        if param_name == "Suksessrate": # Float value, round to 2 decimal places
            param_values = np.round(np.arange(min_param_value, max_param_value + (param_value_step/2), param_value_step), 2)
        else: # Integer value
            param_values = np.arange(min_param_value, max_param_value + (param_value_step/2), param_value_step)
        st.session_state.varying_protection_measure_parameter_results = {}
        for param_value in param_values:
            C_b_mod = C_b.copy()
            P_b_mod = P_b.copy()
            A_b_mod = A_b.copy()
            if param_name == "Suksessrate":
                protection_measure_indices = [b for b, t in enumerate(effector_b) if t == type_name]
                for b in protection_measure_indices:
                    P_b_mod[b] = param_value
            else:
                protection_measure_indices = [b for b, t in enumerate(type_b) if t == type_name]
                for b in protection_measure_indices:
                        if param_name == "Kostnad":
                            C_b_mod[b] = param_value
                        elif param_name == "Antall effektorer":
                            A_b_mod[b] = int(param_value)
            result = solve_interdiction(F, type_f, K_f, H_f, C_f, beta_f, B, C_b_mod, P_b_mod, A_b_mod, OE, T, R,
                                        iteration_placeholder=iteration_placeholder,
                                        iteration_detail=f"{param_name}: {param_value}"
            )
            if result["status"] != "OPTIMAL":
                st.error(f"Optimeringen feilet for {param_name} {param_value} med status: {result['status']}")
                continue
            st.session_state.varying_protection_measure_parameter_type_name = type_name
            st.session_state.varying_protection_measure_parameter_param_name = param_name
            st.session_state.varying_protection_measure_parameter_params = {
                "F": F,
                "type_f": type_f,
                "C_f": C_f,
                "B": B,
                "type_b": type_b,
                "OE": OE
            }
            # Store C_b_mod in the result for correct cost plotting
            result["C_b"] = C_b_mod.copy()
            st.session_state.varying_protection_measure_parameter_results[param_value] = result
            with chart_placeholder.container():
                st.subheader("Gjenværende produksjonskapasitet etter angrep")
                plot_remaining_production_capacity_vs_protection_measure_parameter()
                st.subheader("Fabrikkonfigurasjon")
                plot_facility_configuration_vs_protection_measure_parameter()
                st.subheader("Kostnader")
                plot_costs_vs_protection_measure_parameter()