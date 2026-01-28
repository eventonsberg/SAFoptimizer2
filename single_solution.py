import streamlit as st
import pandas as pd
from optimizer import solve_interdiction

def display_single_solution(P_A, C_A, A_max, B_R, B_B, F, type_f, K_f, H_f, C_f):
    if st.button("Kjør optimering", type="primary", key="run_single_solution"):
        iteration_placeholder = st.empty()
        result = solve_interdiction(P_A, C_A, A_max, B_R, B_B, F, type_f, K_f, H_f, C_f,
                                    iteration_placeholder=iteration_placeholder
        )
        if result["status"] != "OPTIMAL":
            st.error(f"Optimeringen feilet med status: {result['status']}")
            with st.expander("Vis iterasjonshistorikk"):
                st.dataframe(result["history"])
            return
        results = []
        type_counters = {}
        total_f_and_ad_cost = 0
        total_missile_cost = 0
        for f in range(len(result["established_facilities"])):
            if result["established_facilities"][f]:
                if type_f[f] not in type_counters:
                    type_counters[type_f[f]] = 0
                type_counters[type_f[f]] += 1
                type_name = f"{type_f[f]} #{type_counters[type_f[f]]}" if type_counters[type_f[f]] > 1 else type_f[f]
                f_and_ad_cost = C_f[f] + C_A * result["air_defense_assignment"][f]
                missile_cost = result["missile_costs"][f]
                results.append({
                    "Fabrikk": type_name,
                    "Antall luftvernmissiler": result["air_defense_assignment"][f],
                    "Fabrikk- og luftvernkostnad": f_and_ad_cost,
                    "Ødelagt": result["attack_scenario"][f],
                    "Missilkostnad": missile_cost,
                })
                total_f_and_ad_cost += f_and_ad_cost
                total_missile_cost += missile_cost
        st.write(f"Gjenværende produksjonskapasitet etter angrep: {result['remaining_production_capacity_after_attack']:,.0f}")
        st.dataframe(
            pd.DataFrame(results),
            hide_index=True,
            column_config={
                "Fabrikk- og luftvernkostnad": st.column_config.NumberColumn(format="localized")
            }
        )
        st.write(f"Totale fabrikk- og luftvernkostnader: {total_f_and_ad_cost:,.0f}")
        st.write(f"Totale missilkostnader: {total_missile_cost:,.1f}")