import streamlit as st
from optimizer import solve_interdiction
from blue_vs_red_budget_visualization import (
    plot_blue_vs_red_budget_heatmap,
    plot_production_capacity_vs_blue_budget_for_different_red_budgets,
    plot_production_capacity_vs_red_budget_for_different_blue_budgets
)

def display_blue_vs_red_budget(model_inputs):
    F = model_inputs.get("F")
    type_f = model_inputs.get("type_f")
    K_f = model_inputs.get("K_f")
    H_f = model_inputs.get("H_f")
    C_f = model_inputs.get("C_f")
    beta_f = model_inputs.get("beta_f")
    B = model_inputs.get("B")
    C_b = model_inputs.get("C_b")
    P_b = model_inputs.get("P_b")
    A_b = model_inputs.get("A_b")
    R = model_inputs.get("R")

    col1_1, col2_1 = st.columns(2)
    with col1_1:
        min_blue_budget = st.number_input(
            "Minimum :blue-badge[blått budsjett]",
            value=0,
            step=1,
            min_value=0,
            format="%d",
            key="min_blue_budget"
        )
    with col2_1:
        max_blue_budget = st.number_input(
            "Maksimum :blue-badge[blått budsjett]",
            value=500,
            step=1,
            min_value=0,
            format="%d",
            key="max_blue_budget"
        )
    blue_budget_step = st.number_input(
        "Steglengde :blue-badge[blått budsjett]",
        value=50,
        step=1,
        min_value=1,
        format="%d",
        key="blue_budget_step"
    )
    col1, col2 = st.columns(2)
    with col1:
        min_red_budget = st.number_input(
            "Minimum :red-badge[rødt budsjett]",
            value=0,
            step=1,
            min_value=0,
            format="%d",
            key="min_red_budget"
        )
    with col2:
        max_red_budget = st.number_input(
            "Maksimum :red-badge[rødt budsjett]",
            value=20,
            step=1,
            min_value=0,
            format="%d",
            key="max_red_budget"
        )
    red_budget_step = st.number_input(
        "Steglengde :red-badge[rødt budsjett]",
        value=5,
        step=1,
        min_value=1,
        format="%d",
        key="red_budget_step"
    )
    

    if "varying_blue_vs_red_budget_results" not in st.session_state:
        st.session_state.varying_blue_vs_red_budget_results = {}
    
    run_optimization = st.button("Kjør optimering", type="primary", key="run_varying_blue_vs_red_budget")
    iteration_placeholder = st.empty()
    chart_placeholder = st.empty()
    if st.session_state.varying_blue_vs_red_budget_results:
        with chart_placeholder.container():
            st.subheader("Gjenværende produksjonskapasitet etter angrep")
            plot_blue_vs_red_budget_heatmap()
            plot_production_capacity_vs_blue_budget_for_different_red_budgets()
            plot_production_capacity_vs_red_budget_for_different_blue_budgets()

    if run_optimization:
        if min_blue_budget > max_blue_budget:
            st.error("Minimum blått budsjett kan ikke være større enn maksimum.")
            return
        if min_red_budget > max_red_budget:
            st.error("Minimum rødt budsjett kan ikke være større enn maksimum.")
            return
        blue_budget_values = list(range(min_blue_budget, max_blue_budget + 1, blue_budget_step))
        red_budget_values = list(range(min_red_budget, max_red_budget + 1, red_budget_step))
        st.session_state.varying_blue_vs_red_budget_results = {}
        for T in red_budget_values:
            for OE in blue_budget_values:
                result = solve_interdiction(F, type_f, K_f, H_f, C_f, beta_f, B, C_b, P_b, A_b, OE, T, R,
                                            iteration_placeholder=iteration_placeholder,
                                            iteration_detail=f"Blått budsjett: {OE}, Rødt budsjett: {T}",
                                            with_tie_breakers=False
                )
                if result["status"] != "OPTIMAL":
                    st.error(f"Optimeringen feilet for  blått budsjett {OE} og rødt budsjett {T} med status: {result['status']}")
                    continue
                st.session_state.varying_blue_vs_red_budget_results[(OE, T)] = result
                with chart_placeholder.container():
                    st.subheader("Gjenværende produksjonskapasitet etter angrep")
                    plot_blue_vs_red_budget_heatmap()
                    plot_production_capacity_vs_blue_budget_for_different_red_budgets()
                    plot_production_capacity_vs_red_budget_for_different_blue_budgets()