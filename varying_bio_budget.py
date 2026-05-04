import streamlit as st
from optimizer import solve_interdiction
from varying_bio_budget_visualization import (
    plot_remaining_production_capacity_vs_bio_budget,
    plot_facility_configuration_vs_bio_budget,
    plot_costs_vs_bio_budget,
    plot_bio_production_vs_bio_budget
)

def display_varying_bio_budget(model_inputs):
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

    col1, col2 = st.columns(2)
    with col1:
        min_budget = st.number_input(
            "Minimum biobudsjett",
            value=0,
            step=1,
            min_value=0,
            format="%d"
        )
    with col2:
        max_budget = st.number_input(
            "Maksimum biobudsjett",
            value=500,
            step=1,
            min_value=0,
            format="%d"
        )
    budget_step = st.number_input(
        "Steglengde",
        value=50,
        step=1,
        min_value=1,
        format="%d",
        key="bio_budget_step"
    )

    if "varying_bio_budget_params" not in st.session_state:
        st.session_state.varying_bio_budget_params = {}
    if "varying_bio_budget_results" not in st.session_state:
        st.session_state.varying_bio_budget_results = {}

    run_optimization = st.button("Kjør optimering", type="primary", key="run_varying_bio_budget")
    iteration_placeholder = st.empty()
    chart_placeholder = st.empty()
    if st.session_state.varying_bio_budget_results:
        with chart_placeholder.container():
            st.subheader("Gjenværende produksjonskapasitet etter angrep")
            plot_remaining_production_capacity_vs_bio_budget()
            st.subheader("Fabrikkonfigurasjon")
            plot_facility_configuration_vs_bio_budget()
            st.subheader("Kostnader")
            plot_costs_vs_bio_budget()
            st.subheader("Biodrivstoff")
            plot_bio_production_vs_bio_budget()

    if run_optimization:
        if min_budget > max_budget:
            st.error("Minimum biobudsjett kan ikke være større enn maksimum.")
            return
        bio_budget_values = list(range(min_budget, max_budget + 1, budget_step))
        st.session_state.varying_bio_budget_results = {}
        for R in bio_budget_values:
            result = solve_interdiction(
                F, type_f, K_f, H_f, C_f, beta_f, B, C_b, P_b, A_b, OE, T, R,
                iteration_placeholder=iteration_placeholder,
                iteration_detail=f"Biobudsjett: {R}"
            )
            if result["status"] != "OPTIMAL":
                st.error(f"Optimeringen feilet for biobudsjett {R} med status: {result['status']}")
                continue
            st.session_state.varying_bio_budget_params = {
                "F": F,
                "type_f": type_f,
                "K_f": K_f,
                "C_f": C_f,
                "beta_f": beta_f,
                "B": B,
                "type_b": type_b,
                "C_b": C_b,
                "OE": OE
            }
            st.session_state.varying_bio_budget_results[R] = result
            with chart_placeholder.container():
                st.subheader("Gjenværende produksjonskapasitet etter angrep")
                plot_remaining_production_capacity_vs_bio_budget()
                st.subheader("Fabrikkonfigurasjon")
                plot_facility_configuration_vs_bio_budget()
                st.subheader("Kostnader")
                plot_costs_vs_bio_budget()
                st.subheader("Biodrivstoff")
                plot_bio_production_vs_bio_budget()