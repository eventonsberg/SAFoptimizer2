import streamlit as st
import numpy as np
from optimizer import solve_interdiction
from varying_ad_success_rate_visualization import (
    plot_remaining_production_capacity_vs_ad_success_rate,
    plot_facility_configuration_vs_ad_success_rate,
    plot_costs_vs_ad_success_rate
)

def display_varying_ad_success_rate(_, C_A, A_max, B_R, B_B, F, type_f, K_f, H_f, C_f):
    col1, col2 = st.columns(2)
    with col1:
        min_ad_success_rate = st.number_input(
            "Minimum suksessrate for luftvern",
            value=0.5,
            step=0.01,
            min_value=0.0,
            max_value=1.0,
            format="%f"
        )
    with col2:
        max_ad_success_rate = st.number_input(
            "Maksimum suksessrate for luftvern",
            value=1.0,
            step=0.01,
            min_value=0.0,
            max_value=1.0,
            format="%f"
        )
    ad_success_rate_step = st.number_input(
        "Steglengde",
        value=0.05,
        step=0.01,
        min_value=0.01,
        max_value=1.0,
        format="%f",
        key="ad_success_rate_step"
    )

    if "varying_ad_success_rate_params" not in st.session_state:
        st.session_state.varying_ad_success_rate_params = {}
    if "varying_ad_success_rate_results" not in st.session_state:
        st.session_state.varying_ad_success_rate_results = {}

    run_optimization = st.button("Kjør optimering", type="primary", key="run_varying_ad_success_rate")
    iteration_placeholder = st.empty()
    chart_placeholder = st.empty()
    if st.session_state.varying_ad_success_rate_results:
        with chart_placeholder.container():
            st.subheader("Gjenværende produksjonskapasitet etter angrep")
            plot_remaining_production_capacity_vs_ad_success_rate()
            st.subheader("Fabrikkonfigurasjon")
            plot_facility_configuration_vs_ad_success_rate()
            st.subheader("Kostnader")
            plot_costs_vs_ad_success_rate()

    if run_optimization:
        if min_ad_success_rate > max_ad_success_rate:
            st.error("Minimum suksessrate kan ikke være større enn maksimum.")
            return
        ad_success_rate_values = [round(p, 2) for p in np.arange(min_ad_success_rate, max_ad_success_rate + 0.01, ad_success_rate_step)]
        st.session_state.varying_ad_success_rate_results = {}
        for P_A in ad_success_rate_values:
            result = solve_interdiction(P_A, C_A, A_max, B_R, B_B, F, type_f, K_f, H_f, C_f,
                                        iteration_placeholder=iteration_placeholder,
                                        iteration_detail=f"Suksessrate: {P_A}"
            )
            if result["status"] != "OPTIMAL":
                st.error(f"Optimeringen feilet for suksessrate {P_A} med status: {result['status']}")
                continue
            st.session_state.varying_ad_success_rate_params = {
                "type_f": type_f,
                "C_f": C_f,
                "C_A": C_A,
                "B_B": B_B
            }
            st.session_state.varying_ad_success_rate_results[P_A] = result
            with chart_placeholder.container():
                st.subheader("Gjenværende produksjonskapasitet etter angrep")
                plot_remaining_production_capacity_vs_ad_success_rate()
                st.subheader("Fabrikkonfigurasjon")
                plot_facility_configuration_vs_ad_success_rate()
                st.subheader("Kostnader")
                plot_costs_vs_ad_success_rate()