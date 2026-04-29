import streamlit as st
import pandas as pd
from optimizer import solve_interdiction
from single_solution_visualization import single_solution_results_table

def display_single_solution(model_inputs):
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
    R = model_inputs.get("R")

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
        results = solve_interdiction(
            F, type_f, K_f, H_f, C_f, beta_f, B, C_b, P_b, A_b, OE, T, R,
            iteration_placeholder=iteration_placeholder
        )
        if results["status"] != "OPTIMAL":
            st.error(f"Optimeringen feilet med status: {results['status']}")
            with st.expander("Vis iterasjonshistorikk"):
                st.dataframe(results["history"])
            return
        st.session_state.single_solution_params = {
            "F": F,
            "type_f": type_f,
            "C_f": C_f,
            "B": B,
            "type_b": type_b,
            "C_b": C_b
        }
        st.session_state.single_solution_results = results
        with results_placeholder.container():
            single_solution_results_table()