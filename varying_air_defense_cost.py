import streamlit as st
from optimizer import solve_interdiction
from varying_air_defense_cost_visualization import (
    plot_remaining_production_capacity_vs_air_defense_cost,
    plot_facility_configuration_vs_air_defense_cost,
    plot_costs_vs_air_defense_cost
)

def display_varying_air_defense_cost(P_A, _, A_max, B_R, B_B, F, type_f, K_f, H_f, C_f):
    col1, col2 = st.columns(2)
    with col1:
        min_ad_cost = st.number_input(
            "Minimum kostnad per luftvernmissil",
            value=0,
            step=1,
            min_value=0,
            format="%d"
        )
    with col2:
        max_ad_cost = st.number_input(
            "Maksimum kostnad per luftvernmissil",
            value=20,
            step=1,
            min_value=0,
            format="%d"
        )
    ad_cost_step = st.number_input(
        "Steglengde",
        value=1,
        step=1,
        min_value=1,
        format="%d",
        key="ad_cost_step"
    )

    if "varying_air_defense_cost_params" not in st.session_state:
        st.session_state.varying_air_defense_cost_params = {}
    if "varying_air_defense_cost_results" not in st.session_state:
        st.session_state.varying_air_defense_cost_results = {}

    run_optimization = st.button("Kjør optimering", type="primary", key="run_varying_air_defense_cost")
    iteration_placeholder = st.empty()
    chart_placeholder = st.empty()
    if st.session_state.varying_air_defense_cost_results:
        with chart_placeholder.container():
            st.subheader("Gjenværende produksjonskapasitet etter angrep")
            plot_remaining_production_capacity_vs_air_defense_cost()
            st.subheader("Fabrikkonfigurasjon")
            plot_facility_configuration_vs_air_defense_cost()
            st.subheader("Kostnader")
            plot_costs_vs_air_defense_cost()

    if run_optimization:
        if min_ad_cost > max_ad_cost:
            st.error("Minimum kostnad per luftvernmissil kan ikke være større enn maksimum.")
            return
        air_defense_cost_values = list(range(min_ad_cost, max_ad_cost + 1, ad_cost_step))
        st.session_state.varying_air_defense_cost_results = {}
        for C_A in air_defense_cost_values:
            result = solve_interdiction(P_A, C_A, A_max, B_R, B_B, F, type_f, K_f, H_f, C_f,
                                        iteration_placeholder=iteration_placeholder,
                                        iteration_detail=f"Kostnad per luftvernmissil: {C_A}"
            )
            if result["status"] != "OPTIMAL":
                st.error(f"Optimeringen feilet for kostnad per luftvernmissil {C_A} med status: {result['status']}")
                continue
            st.session_state.varying_air_defense_cost_params = {
                "type_f": type_f,
                "C_f": C_f,
                "C_A": C_A,
                "B_B": B_B
            }
            st.session_state.varying_air_defense_cost_results[C_A] = result
            with chart_placeholder.container():
                st.subheader("Gjenværende produksjonskapasitet etter angrep")
                plot_remaining_production_capacity_vs_air_defense_cost()
                st.subheader("Fabrikkonfigurasjon")
                plot_facility_configuration_vs_air_defense_cost()
                st.subheader("Kostnader")
                plot_costs_vs_air_defense_cost()