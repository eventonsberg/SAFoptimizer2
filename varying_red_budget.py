import streamlit as st
from optimizer import solve_interdiction
from varying_red_budget_visualization import (
    plot_remaining_production_capacity_vs_red_budget,
    plot_facility_configuration_vs_red_budget,
    plot_costs_vs_red_budget
)

def display_varying_red_budget(model_inputs):
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

    col1, col2 = st.columns(2)
    with col1:
        min_budget = st.number_input(
            "Minimum rødt budsjett",
            value=0,
            step=1,
            min_value=0,
            format="%d"
        )
    with col2:
        max_budget = st.number_input(
            "Maksimum rødt budsjett",
            value=20,
            step=1,
            min_value=0,
            format="%d"
        )
    budget_step = st.number_input(
        "Steglengde",
        value=1,
        step=1,
        min_value=1,
        format="%d",
        key="red_budget_step"
    )

    if "varying_red_budget_params" not in st.session_state:
        st.session_state.varying_red_budget_params = {}
    if "varying_red_budget_results" not in st.session_state:
        st.session_state.varying_red_budget_results = {}

    run_optimization = st.button("Kjør optimering", type="primary", key="run_varying_red_budget")
    iteration_placeholder = st.empty()
    chart_placeholder = st.empty()
    if st.session_state.varying_red_budget_results:
        with chart_placeholder.container():
            st.subheader("Gjenværende produksjonskapasitet etter angrep")
            plot_remaining_production_capacity_vs_red_budget()
            st.subheader("Fabrikkonfigurasjon")
            plot_facility_configuration_vs_red_budget()
            st.subheader("Kostnader")
            plot_costs_vs_red_budget()

    if run_optimization:
        if min_budget > max_budget:
            st.error("Minimum rødt budsjett kan ikke være større enn maksimum.")
            return
        red_budget_values = list(range(min_budget, max_budget + 1, budget_step))
        st.session_state.varying_red_budget_results = {}
        for TE in red_budget_values:
            result = solve_interdiction(
                F, type_f, K_f, H_f, C_f, B, C_b, P_b, A_b, OR, TE,
                iteration_placeholder=iteration_placeholder,
                iteration_detail=f"Rødt budsjett: {TE}"
            )
            if result["status"] != "OPTIMAL":
                st.error(f"Optimeringen feilet for rødt budsjett {TE} med status: {result['status']}")
                continue
            st.session_state.varying_red_budget_params = {
                "F": F,
                "type_f": type_f,
                "C_f": C_f,
                "B": B,
                "type_b": type_b,
                "C_b": C_b,
                "OR": OR
            }
            st.session_state.varying_red_budget_results[TE] = result
            with chart_placeholder.container():
                st.subheader("Gjenværende produksjonskapasitet etter angrep")
                plot_remaining_production_capacity_vs_red_budget()
                st.subheader("Fabrikkonfigurasjon")
                plot_facility_configuration_vs_red_budget()
                st.subheader("Kostnader")
                plot_costs_vs_red_budget()