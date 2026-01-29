import streamlit as st
from optimizer import solve_interdiction
from missile_budget_vs_f_and_ad_budget_visualization import (
    plot_missile_budget_vs_f_and_ad_budget_heatmap,
    plot_production_capacity_vs_f_and_ad_budget_for_different_missile_budgets,
    plot_production_capacity_vs_missile_budget_for_different_f_and_ad_budgets
)

def display_varying_missile_budget_vs_f_and_ad_budget(P_A, C_A, A_max, _B_R, _B_B, F, type_f, K_f, H_f, C_f):
    col1, col2 = st.columns(2)
    with col1:
        min_budget_R = st.number_input(
            "Minimum missilbudsjett",
            value=0,
            step=1,
            min_value=0,
            format="%d",
            key="min_budget_R"
        )
    with col2:
        max_budget_R = st.number_input(
            "Maksimum missilbudsjett",
            value=20,
            step=1,
            min_value=0,
            format="%d",
            key="max_budget_R"
        )
    budget_R_step = st.number_input(
        "Steglengde missilbudsjett",
        value=5,
        step=1,
        min_value=1,
        format="%d",
        key="budget_R_step"
    )
    col1_1, col2_1 = st.columns(2)
    with col1_1:
        min_budget_B = st.number_input(
            "Minimum fabrikk- og luftvernbudsjett",
            value=0,
            step=1,
            min_value=0,
            format="%d",
            key="min_budget_B"
        )
    with col2_1:
        max_budget_B = st.number_input(
            "Maksimum fabrikk- og luftvernbudsjett",
            value=500,
            step=1,
            min_value=0,
            format="%d",
            key="max_budget_B"
        )
    budget_B_step = st.number_input(
        "Steglengde fabrikk- og luftvernbudsjett",
        value=50,
        step=1,
        min_value=1,
        format="%d",
        key="budget_B_step"
    )

    if "varying_missile_budget_vs_f_and_ad_budget_results" not in st.session_state:
        st.session_state.varying_missile_budget_vs_f_and_ad_budget_results = {}
    
    run_optimization = st.button("Kjør optimering", type="primary", key="run_varying_missile_budget_vs_f_and_ad_budget")
    iteration_placeholder = st.empty()
    chart_placeholder = st.empty()
    if st.session_state.varying_missile_budget_vs_f_and_ad_budget_results:
        with chart_placeholder.container():
            st.subheader("Gjenværende produksjonskapasitet etter angrep")
            plot_missile_budget_vs_f_and_ad_budget_heatmap()
            plot_production_capacity_vs_f_and_ad_budget_for_different_missile_budgets()
            plot_production_capacity_vs_missile_budget_for_different_f_and_ad_budgets()

    if run_optimization:
        if min_budget_R > max_budget_R:
            st.error("Minimum missilbudsjett kan ikke være større enn maksimum.")
            return
        if min_budget_B > max_budget_B:
            st.error("Minimum fabrikk- og luftvernbudsjett kan ikke være større enn maksimum.")
            return
        f_and_ad_budget_values = list(range(min_budget_B, max_budget_B + 1, budget_B_step))
        missile_budget_values = list(range(min_budget_R, max_budget_R + 1, budget_R_step))
        st.session_state.varying_missile_budget_vs_f_and_ad_budget_results = {}
        for B_R in missile_budget_values:
            for B_B in f_and_ad_budget_values:
                result = solve_interdiction(P_A, C_A, A_max, B_R, B_B, F, type_f, K_f, H_f, C_f,
                                            iteration_placeholder=iteration_placeholder,
                                            iteration_detail=f"Missilbudsjett: {B_R}, Fabrikk- og luftvernbudsjett: {B_B}"
                )
                if result["status"] != "OPTIMAL":
                    st.error(f"Optimeringen feilet for missilbudsjett {B_R} og fabrikk- og luftvernbudsjett {B_B} med status: {result['status']}")
                    continue
                st.session_state.varying_missile_budget_vs_f_and_ad_budget_results[(B_R, B_B)] = result
                with chart_placeholder.container():
                    st.subheader("Gjenværende produksjonskapasitet etter angrep")
                    plot_missile_budget_vs_f_and_ad_budget_heatmap()
                    plot_production_capacity_vs_f_and_ad_budget_for_different_missile_budgets()
                    plot_production_capacity_vs_missile_budget_for_different_f_and_ad_budgets()