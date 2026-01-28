import streamlit as st
from optimizer import solve_interdiction
from varying_missile_budget_visualization import (
    plot_remaining_production_capacity_vs_missile_budget,
    plot_facility_configuration_vs_missile_budget
)

def display_varying_missile_budget(P_A, C_A, A_max, _, B_B, F, type_f, K_f, H_f, C_f):
    col1, col2 = st.columns(2)
    with col1:
        min_budget = st.number_input(
            "Minimum missilbudsjett",
            value=0,
            step=1,
            min_value=0,
            format="%d"
        )
    with col2:
        max_budget = st.number_input(
            "Maksimum missilbudsjett",
            value=20,
            step=1,
            min_value=0,
            format="%d"
        )

    if "varying_missile_budget_results" not in st.session_state:
        st.session_state.varying_missile_budget_results = {}

    run_optimization = st.button("Kjør optimering", type="primary", key="run_varying_missile_budget")
    iteration_placeholder = st.empty()
    chart1_title_placeholder = st.empty()
    chart1_placeholder = st.empty()
    chart2_title_placeholder = st.empty()
    chart2_placeholder = st.empty()
    if st.session_state.varying_missile_budget_results:
        with chart1_placeholder:
            chart1_title_placeholder.subheader("Gjenværende produksjonskapasitet etter angrep")
            plot_remaining_production_capacity_vs_missile_budget()
        with chart2_placeholder:
            chart2_title_placeholder.subheader("Fabrikkonfigurasjon")
            plot_facility_configuration_vs_missile_budget(type_f)

    if run_optimization:
        if min_budget > max_budget:
            st.error("Minimum missilbudsjett kan ikke være større enn maksimum missilbudsjett.")
            return
        missile_budget_values = list(range(min_budget, max_budget + 1))
        st.session_state.varying_missile_budget_results = {}
        for B_R in missile_budget_values:
            result = solve_interdiction(P_A, C_A, A_max, B_R, B_B, F, type_f, K_f, H_f, C_f,
                                        iteration_placeholder=iteration_placeholder,
                                        iteration_detail=f"Missilbudsjett: {B_R}"
            )
            if result["status"] != "OPTIMAL":
                st.error(f"Optimeringen feilet for missilbudsjett {B_R} med status: {result['status']}")
                continue
            st.session_state.varying_missile_budget_results[B_R] = result
            with chart1_placeholder:
                chart1_title_placeholder.subheader("Gjenværende produksjonskapasitet etter angrep")
                plot_remaining_production_capacity_vs_missile_budget()
            with chart2_placeholder:
                chart2_title_placeholder.subheader("Fabrikkonfigurasjon")
                plot_facility_configuration_vs_missile_budget(type_f)