import streamlit as st
import pandas as pd
import altair as alt
from optimizer import solve_interdiction

def single_solution_results_table():
    F = st.session_state.single_solution_params["F"]
    type_f = st.session_state.single_solution_params["type_f"]
    C_f = st.session_state.single_solution_params["C_f"]
    B = st.session_state.single_solution_params["B"]
    type_b = st.session_state.single_solution_params["type_b"]
    C_b = st.session_state.single_solution_params["C_b"]
    results = st.session_state.single_solution_results
    results_list = []
    type_counters = {}
    total_f_and_b_cost = 0
    total_effector_cost = 0
    for f in range(F):
        if results["established_facilities"][f]:
            if type_f[f] not in type_counters:
                type_counters[type_f[f]] = 0
            type_counters[type_f[f]] += 1
            type_name = f"{type_f[f]} #{type_counters[type_f[f]]}" if type_counters[type_f[f]] > 1 else type_f[f]
            number_of_protection_measures = sum(results["implemented_protection_measures"][b][f] for b in range(B))
            protection_measure = ''
            if number_of_protection_measures > 0:
                protection_measures = [type_b[b] for b in range(B) if results["implemented_protection_measures"][b][f]]
                protection_measure = ', '.join(protection_measures) # Separate with comma if multiple protection measures implemented
            b_cost = sum(C_b[b] * results["implemented_protection_measures"][b][f] for b in range(B))
            f_and_b_cost = C_f[f] + b_cost
            effector_cost = results["effector_costs"][f]
            results_list.append({
                "Fabrikk": type_name,
                "Beskyttelsestiltak": protection_measure,
                "Kostnad": f_and_b_cost,
                "Ødelagt": results["destroyed_facilities"][f],
                "Trusseleffektorer": effector_cost,
            })
            total_f_and_b_cost += f_and_b_cost
            total_effector_cost += effector_cost
    st.write(f"Gjenværende produksjonskapasitet etter angrep: {results['remaining_production_capacity_after_attack']:,.0f} m³/dag")
    st.dataframe(
        pd.DataFrame(results_list),
        hide_index=True,
        column_config={
            "Kostnad": st.column_config.NumberColumn(format="localized")
        }
    )
    st.write(f"Totale fabrikk- og beskyttelseskostnader: {total_f_and_b_cost:,.0f} MNOK")
    st.write(f"Totale trusseleffektorer brukt: {total_effector_cost:,.1f}")
