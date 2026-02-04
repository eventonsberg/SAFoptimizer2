import streamlit as st
from optimizer import solve_interdiction
from sensitivity_analysis_visualization import plot_sensitivity_analysis

def display_sensitivity_analysis(P_A, C_A, A_max, B_R, B_B, F, type_f, K_f, H_f, C_f):
    options = [
        "Kostnad per luftvernmissil",
        "Suksessrate for luftvern",
        "Maks antall luftvernmissiler per fabrikk",
        "Fabrikk- og luftvernbudsjett",
        "Missilbudsjett"
    ]
    for param in ["Kapasitet", "Kostnad", "Hardhet"]:
        for facility in set(type_f):
            options.append(f"{param} - {facility}")
    selected_params = st.multiselect(
        "Parametere",
        options=options,
        default=options,
        key="sensitivity_analysis_params"
    )
    variation = st.number_input(
        "Prosentvis parametervariasjon",
        value=20,
        step=1,
        min_value=1,
        max_value=100,
        format="%d",
        key="sensitivity_analysis_variation"
    )
    
    if "sensitivity_analysis_base_production" not in st.session_state:
        st.session_state.sensitivity_analysis_base_production = None
    if "sensitivity_analysis_results" not in st.session_state:
        st.session_state.sensitivity_analysis_results = {}
    
    run_optimization = st.button("Kjør optimering", type="primary", key="run_sensitivity_analysis")
    iteration_placeholder = st.empty()
    chart_placeholder = st.empty()
    if st.session_state.sensitivity_analysis_results:
        with chart_placeholder.container():
            st.subheader("Gjenværende produksjonskapasitet etter angrep")
            plot_sensitivity_analysis()
    
    if run_optimization:
        if selected_params == []:
            st.error("Velg minst én parameter for sensitivitetsanalysen.")
            return
        st.session_state.sensitivity_analysis_results = {}
        base_result = solve_interdiction(P_A, C_A, A_max, B_R, B_B, F, type_f, K_f, H_f, C_f,
                                        iteration_placeholder=iteration_placeholder,
                                        iteration_detail="Basislinje"
        )
        if base_result["status"] != "OPTIMAL":
            st.error(f"Optimeringen feilet for basislinje med status: {base_result['status']}")
            return
        st.session_state.sensitivity_analysis_base_production = base_result["remaining_production_capacity_after_attack"]
        variation_values = [-variation, variation]
        for param in selected_params:
            for variation in variation_values:
                _P_A, _C_A, _A_max, _B_R, _B_B = P_A, C_A, A_max, B_R, B_B
                _K_f, _H_f, _C_f = K_f.copy(), H_f.copy(), C_f.copy()
                factor = 1 + (variation / 100)
                param_value = None
                if " - " in param:
                    param_name, facility_name = param.split(" - ", 1)
                    if param_name == "Hardhet":
                        for f in range(F):
                            if type_f[f] == facility_name:
                                _H_f[f] = H_f[f] * factor
                                param_value = _H_f[f]
                    elif param_name == "Kapasitet":
                        for f in range(F):
                            if type_f[f] == facility_name:
                                _K_f[f] = round(K_f[f] * factor)
                                param_value = _K_f[f]
                    elif param_name == "Kostnad":
                        for f in range(F):
                            if type_f[f] == facility_name:
                                _C_f[f] = C_f[f] * factor
                                param_value = _C_f[f]
                else:
                    if param == "Kostnad per luftvernmissil":
                        _C_A = C_A * factor
                        param_value = _C_A
                    elif param == "Suksessrate for luftvern":
                        if P_A * factor > 1.0:
                            _P_A = 1.0  # Probability cannot exceed 100%
                        else:
                            _P_A = P_A * factor
                        param_value = _P_A
                    elif param == "Maks antall luftvernmissiler per fabrikk":
                        _A_max = round(A_max * factor)
                        param_value = _A_max
                    elif param == "Fabrikk- og luftvernbudsjett":
                        _B_B = B_B * factor
                        param_value = _B_B
                    elif param == "Missilbudsjett":
                        _B_R = B_R * factor
                        param_value = _B_R
                result = solve_interdiction(_P_A, _C_A, _A_max, _B_R, _B_B, F, type_f, _K_f, _H_f, _C_f,
                                            iteration_placeholder=iteration_placeholder,
                                            iteration_detail=f"{param}: {variation}%"
                )
                if result["status"] != "OPTIMAL":
                    st.error(f"Optimeringen feilet for {param} med {variation}% variasjon, status: {result['status']}")
                    continue
                st.session_state.sensitivity_analysis_results[(param, variation, param_value)] = result["remaining_production_capacity_after_attack"]
                with chart_placeholder.container():
                    st.subheader("Gjenværende produksjonskapasitet etter angrep")
                    plot_sensitivity_analysis()
