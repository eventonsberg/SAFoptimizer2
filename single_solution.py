import streamlit as st
import pandas as pd
from optimizer import solve_interdiction

def single_solution_results():
    type_f, C_f, C_A = st.session_state.single_solution_params
    results = st.session_state.single_solution_results
    results_list = []
    type_counters = {}
    total_f_and_ad_cost = 0
    total_missile_cost = 0
    for f in range(len(results["established_facilities"])):
        if results["established_facilities"][f]:
            if type_f[f] not in type_counters:
                type_counters[type_f[f]] = 0
            type_counters[type_f[f]] += 1
            type_name = f"{type_f[f]} #{type_counters[type_f[f]]}" if type_counters[type_f[f]] > 1 else type_f[f]
            f_and_ad_cost = C_f[f] + C_A * results["air_defense_assignment"][f]
            missile_cost = results["missile_costs"][f]
            results_list.append({
                "Fabrikk": type_name,
                "Antall luftvernmissiler": results["air_defense_assignment"][f],
                "Fabrikk- og luftvernkostnad": f_and_ad_cost,
                "Ødelagt": results["attack_scenario"][f],
                "Missilkostnad": missile_cost,
            })
            total_f_and_ad_cost += f_and_ad_cost
            total_missile_cost += missile_cost
    st.write(f"Gjenværende produksjonskapasitet etter angrep: {results['remaining_production_capacity_after_attack']:,.0f}")
    st.dataframe(
        pd.DataFrame(results_list),
        hide_index=True,
        column_config={
            "Fabrikk- og luftvernkostnad": st.column_config.NumberColumn(format="localized")
        }
    )
    st.write(f"Totale fabrikk- og luftvernkostnader: {total_f_and_ad_cost:,.0f}")
    st.write(f"Totale missilkostnader: {total_missile_cost:,.1f}")

def display_single_solution(P_A, C_A, A_max, B_R, B_B, F, type_f, K_f, H_f, C_f):
    if "single_solution_params" not in st.session_state:
        st.session_state.single_solution_params = []
    if "single_solution_results" not in st.session_state:
        st.session_state.single_solution_results = {}

    run_optimization = st.button("Kjør optimering", type="primary", key="run_single_solution")
    
    iteration_placeholder = st.empty()
    results_placeholder = st.empty()

    if st.session_state.single_solution_results:
        with results_placeholder.container():
            single_solution_results()

    if run_optimization:
        results = solve_interdiction(P_A, C_A, A_max, B_R, B_B, F, type_f, K_f, H_f, C_f,
                                    iteration_placeholder=iteration_placeholder
        )
        if results["status"] != "OPTIMAL":
            st.error(f"Optimeringen feilet med status: {results['status']}")
            with st.expander("Vis iterasjonshistorikk"):
                st.dataframe(results["history"])
            return
        st.session_state.single_solution_params = [type_f, C_f, C_A]
        st.session_state.single_solution_results = results
        with results_placeholder.container():
            single_solution_results()