import streamlit as st
import pandas as pd
from optimizer import solve_interdiction

def combination_results_table():
    df_results = pd.DataFrame(st.session_state.combination_results).T
    st.dataframe(df_results)

def display_combinations(P_A, C_A, A_max, B_R, B_B, F, type_f, K_f, H_f, C_f):
    params = [
        "Kostnad per luftvernmissil",
        "Suksessrate for luftvern",
        "Maks antall luftvernmissiler per fabrikk",
        "Fabrikk- og luftvernbudsjett",
        "Missilbudsjett"
    ]
    facility_types = sorted(set(type_f))
    for param in ["Kapasitet", "Kostnad", "Hardhet"]:
        for facility in facility_types:
            params.append(f"{param} - {facility}")
    default_param_values = {}
    for param in params:
        if " - " in param:
            param_name, facility_name = param.split(" - ", 1)
            if param_name == "Hardhet":
                default_param_values[param] = "3"
            elif param_name == "Kapasitet":
                default_param_values[param] = "50"
            elif param_name == "Kostnad":
                default_param_values[param] = "20"
        else:
            if param == "Kostnad per luftvernmissil":
                default_param_values[param] = "5"
            elif param == "Suksessrate for luftvern":
                default_param_values[param] = "0.5, 0.7, 0.9"
            elif param == "Maks antall luftvernmissiler per fabrikk":
                default_param_values[param] = "100"
            elif param == "Fabrikk- og luftvernbudsjett":
                default_param_values[param] = "0, 50, 100, 150, 200"
            elif param == "Missilbudsjett":
                default_param_values[param] = "0, 4, 8, 12, 16, 20"
    st.caption("Fyll inn ønskede parameterverdier separert med komma.")
    param_values_text = {}
    for param in params:
        param_values_text[param] = st.text_input(
            param,
            value=str(default_param_values[param]),
            key=f"combination_{param}"
        )
    param_values = {}
    for param, values_text in param_values_text.items():
        try:
            values = [float(v.strip()) for v in values_text.split(",")]
            param_values[param] = values
        except ValueError:
            st.error(f"Ugyldig input for {param}. Vennligst fyll inn gyldige tall separert med komma.")
            return
    number_of_combinations = 1
    for values in param_values.values():
        number_of_combinations *= len(values)
    st.write(f"Totalt antall kombinasjoner: :blue-badge[{number_of_combinations:,.0f}]")

    if "combination_results" not in st.session_state:
        st.session_state.combination_results = {}

    run_optimization = st.button("Kjør optimering", type="primary", key="run_combinations")
    results_table_placeholder = st.empty()
    if st.session_state.combination_results:
        with results_table_placeholder.container():
            st.subheader("Resultater")
            combination_results_table()

    if run_optimization:
        st.session_state.combination_results = {}
        combination_count = 0
        for combination in pd.MultiIndex.from_product(param_values.values(), names=param_values.keys()):
            combination_dict = dict(zip(param_values.keys(), combination))
            _P_A, _C_A, _A_max, _B_R, _B_B = P_A, C_A, A_max, B_R, B_B
            _K_f, _H_f, _C_f = K_f.copy(), H_f.copy(), C_f.copy()
            for param, value in combination_dict.items():
                if " - " in param:
                    param_name, facility_name = param.split(" - ", 1)
                    if param_name == "Hardhet":
                        for f in range(F):
                            if type_f[f] == facility_name:
                                _H_f[f] = value
                    elif param_name == "Kapasitet":
                        for f in range(F):
                            if type_f[f] == facility_name:
                                _K_f[f] = round(value)
                    elif param_name == "Kostnad":
                        for f in range(F):
                            if type_f[f] == facility_name:
                                _C_f[f] = value
                else:
                    if param == "Kostnad per luftvernmissil":
                        _C_A = value
                    elif param == "Suksessrate for luftvern":
                        _P_A = value
                    elif param == "Maks antall luftvernmissiler per fabrikk":
                        _A_max = round(value)
                    elif param == "Fabrikk- og luftvernbudsjett":
                        _B_B = value
                    elif param == "Missilbudsjett":
                        _B_R = value
            result = solve_interdiction(_P_A, _C_A, _A_max, _B_R, _B_B, F, type_f, _K_f, _H_f, _C_f)
            if result["status"] != "OPTIMAL":
                st.error(f"Optimeringen feilet for kombinasjon {combination_dict} med status: {result['status']}")
                continue
            facility_type_established_counts = {ftype: 0 for ftype in facility_types}
            facility_type_destroyed_counts = {ftype: 0 for ftype in facility_types}
            facility_type_air_defense_configs = {ftype: [] for ftype in facility_types}
            facility_type_air_defense_counts = {ftype: 0 for ftype in facility_types}
            for f, (is_established, is_destroyed, air_defense) in enumerate(
                zip(
                    result["established_facilities"],
                    result["attack_scenario"],
                    result["air_defense_assignment"]
                    )
                ):
                if is_established:
                    ftype = type_f[f]
                    facility_type_established_counts[ftype] += 1
                    facility_type_air_defense_configs[ftype].append(air_defense)
                    facility_type_air_defense_counts[ftype] += air_defense
                    if is_destroyed:
                        facility_type_destroyed_counts[ftype] += 1
            row = {
                **combination_dict,
                "Gjenværende produksjonskapasitet": result["remaining_production_capacity_after_attack"]
            }
            for ftype in facility_types:
                row[f"Antall etablerte {ftype}"] = facility_type_established_counts[ftype]
            for ftype in facility_types:
                row[f"Luftvernkonfigurasjon {ftype}"] = facility_type_air_defense_configs[ftype]
            for ftype in facility_types:
                row[f"Totalt antall luftvernmissiler {ftype}"] = facility_type_air_defense_counts[ftype]
            for ftype in facility_types:
                row[f"Antall ødelagte {ftype}"] = facility_type_destroyed_counts[ftype]
            combination_count += 1
            st.session_state.combination_results[combination_count] = row
            with results_table_placeholder.container():
                st.progress(
                    combination_count / number_of_combinations,
                    text=f":blue-badge[{(combination_count / number_of_combinations) * 100:.1f} %]"
                )
                st.caption(f"{combination_count} av {number_of_combinations} kombinasjoner evaluert")
        with results_table_placeholder.container():
            st.subheader("Resultater")
            combination_results_table()