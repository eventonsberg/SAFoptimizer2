import streamlit as st
from optimizer import solve_interdiction
from varying_protection_cost_visualization import (
    plot_remaining_production_capacity_vs_cost_variation,
    plot_facility_configuration_vs_cost_variation
)

def display_varying_protection_cost(model_inputs):
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

    min_cost_variation = st.number_input(
        "Prosentvis kostnad - Nedre grense",
        value=25,
        step=1,
        min_value=1
    )
    max_cost_variation = st.number_input(
        "Prosentvis kostnad - Øvre grense",
        value=400,
        step=1,
        min_value=1
    )

    if "varying_protection_cost_params" not in st.session_state:
        st.session_state.varying_protection_cost_params = {}
    if "varying_protection_cost_results" not in st.session_state:
        st.session_state.varying_protection_cost_results = {}

    run_optimization = st.button("Kjør optimering", type="primary", key="run_varying_protection_cost")
    iteration_placeholder = st.empty()
    chart_placeholder = st.empty()
    if st.session_state.varying_protection_cost_results:
        with chart_placeholder.container():
            st.subheader("Gjenværende produksjonskapasitet etter angrep")
            plot_remaining_production_capacity_vs_cost_variation()
            st.subheader("Fabrikkonfigurasjon")
            plot_facility_configuration_vs_cost_variation()

    if run_optimization:
        if min_cost_variation >= max_cost_variation:
            st.warning("Nedre grense må være mindre enn øvre grense.")
            return
        cost_variations = []
        cost_variation = min_cost_variation
        while cost_variation <= max_cost_variation:
            cost_variations.append(cost_variation)
            cost_variation *= 2
        st.session_state.varying_protection_cost_results = {}
        for cost_variation in cost_variations:
            scaled_C_b = [cost * cost_variation / 100 for cost in C_b]
            result = solve_interdiction(
                F, type_f, K_f, H_f, C_f, beta_f, B, scaled_C_b, P_b, A_b, OE, T, R,
                iteration_placeholder=iteration_placeholder,
                iteration_detail=f"Kostnad: {cost_variation} %"
            )
            if result["status"] != "OPTIMAL":
                st.error(f"Optimering feilet for kostnad {cost_variation} % med status: {result['status']}")
                continue
            st.session_state.varying_protection_cost_params = {
                "F": F,
                "type_f": type_f,
                "K_f": K_f,
                "C_f": C_f,
                "beta_f": beta_f,
                "B": B,
                "type_b": type_b,
                "C_b": C_b,
                "R": R
            }
            st.session_state.varying_protection_cost_results[cost_variation] = result
            with chart_placeholder.container():
                st.subheader("Gjenværende produksjonskapasitet etter angrep")
                plot_remaining_production_capacity_vs_cost_variation()
                st.subheader("Fabrikkonfigurasjon")
                plot_facility_configuration_vs_cost_variation()