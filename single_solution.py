import streamlit as st
import pandas as pd
from optimizer import solve_interdiction
from single_solution_visualization import single_solution_results_table

def display_single_solution(P_A, C_A, A_max, B_R, B_B, F, type_f, K_f, H_f, C_f):
    if "single_solution_params" not in st.session_state:
        st.session_state.single_solution_params = {}
    if "single_solution_results" not in st.session_state:
        st.session_state.single_solution_results = {}

    run_optimization = st.button("Kjør optimering", type="primary", key="run_single_solution")
    
    iteration_placeholder = st.empty()
    results_placeholder = st.empty()

    if st.session_state.single_solution_results:
        with results_placeholder.container():
            single_solution_results_table()

    if run_optimization:
        results = solve_interdiction(P_A, C_A, A_max, B_R, B_B, F, type_f, K_f, H_f, C_f,
                                    iteration_placeholder=iteration_placeholder
        )
        if results["status"] != "OPTIMAL":
            st.error(f"Optimeringen feilet med status: {results['status']}")
            with st.expander("Vis iterasjonshistorikk"):
                st.dataframe(results["history"])
            return
        st.session_state.single_solution_params = {
            "type_f": type_f,
            "C_f": C_f,
            "C_A": C_A
        }
        st.session_state.single_solution_results = results
        with results_placeholder.container():
            single_solution_results_table()