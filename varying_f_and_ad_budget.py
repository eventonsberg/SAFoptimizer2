import streamlit as st
from optimizer import solve_interdiction
from varying_f_and_ad_budget_visualization import (
    plot_remaining_production_capacity_vs_f_and_ad_budget,
    plot_facility_configuration_vs_f_and_ad_budget,
    plot_costs_vs_f_and_ad_budget
)

def display_varying_f_and_ad_budget(P_A, C_A, A_max, B_R, _, F, type_f, K_f, H_f, C_f):
    col1, col2 = st.columns(2)
    with col1:
        min_budget = st.number_input(
            "Minimum fabrikk- og luftvernbudsjett",
            value=0,
            step=1,
            min_value=0,
            format="%d"
        )
    with col2:
        max_budget = st.number_input(
            "Maksimum fabrikk- og luftvernbudsjett",
            value=500,
            step=1,
            min_value=0,
            format="%d"
        )
    budget_step = st.number_input(
        "Budsjettsteg",
        value=50,
        step=1,
        min_value=1,
        format="%d"
    )

    if "varying_f_and_ad_budget_results" not in st.session_state:
        st.session_state.varying_f_and_ad_budget_results = {}

    run_optimization = st.button("Kjør optimering", type="primary", key="run_varying_f_and_ad_budget")
    iteration_placeholder = st.empty()
    chart_placeholder = st.empty()
    if st.session_state.varying_f_and_ad_budget_results:
        with chart_placeholder.container():
            st.subheader("Gjenværende produksjonskapasitet etter angrep")
            plot_remaining_production_capacity_vs_f_and_ad_budget()
            st.subheader("Fabrikkonfigurasjon")
            plot_facility_configuration_vs_f_and_ad_budget(type_f)
            st.subheader("Kostnader")
            plot_costs_vs_f_and_ad_budget(C_f, C_A)

    if run_optimization:
        if min_budget > max_budget:
            st.error("Minimum fabrikk- og luftvernbudsjett kan ikke være større enn maksimum.")
            return
        f_and_ad_budget_values = list(range(min_budget, max_budget + 1, budget_step))
        st.session_state.varying_f_and_ad_budget_results = {}
        for B_B in f_and_ad_budget_values:
            result = solve_interdiction(P_A, C_A, A_max, B_R, B_B, F, type_f, K_f, H_f, C_f,
                                        iteration_placeholder=iteration_placeholder,
                                        iteration_detail=f"Fabrikk- og luftvernbudsjett: {B_B}"
            )
            if result["status"] != "OPTIMAL":
                st.error(f"Optimeringen feilet for fabrikk- og luftvernbudsjett {B_B} med status: {result['status']}")
                continue
            st.session_state.varying_f_and_ad_budget_results[B_B] = result
            with chart_placeholder.container():
                st.subheader("Gjenværende produksjonskapasitet etter angrep")
                plot_remaining_production_capacity_vs_f_and_ad_budget()
                st.subheader("Fabrikkonfigurasjon")
                plot_facility_configuration_vs_f_and_ad_budget(type_f)
                st.subheader("Kostnader")
                plot_costs_vs_f_and_ad_budget(C_f, C_A)