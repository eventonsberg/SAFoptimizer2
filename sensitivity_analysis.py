import streamlit as st
from optimizer import solve_interdiction
from sensitivity_analysis_visualization import plot_sensitivity_analysis

def display_sensitivity_analysis(model_inputs):
    F = model_inputs.get("F")
    type_f = model_inputs.get("type_f")
    K_f = model_inputs.get("K_f")
    H_f = model_inputs.get("H_f")
    C_f = model_inputs.get("C_f")
    beta_f = model_inputs.get("beta_f")
    B = model_inputs.get("B")
    type_b = model_inputs.get("type_b")
    C_b = model_inputs.get("C_b")
    effector_b = model_inputs.get("effector_b")
    P_b = model_inputs.get("P_b")
    A_b = model_inputs.get("A_b")
    OE = model_inputs.get("OE")
    T = model_inputs.get("T")
    R = model_inputs.get("R")

    facility_options = []
    for param in ["Kostnad", "Kapasitet", "Hardhet"]:
        for facility in dict.fromkeys(type_f):
            facility_options.append(f"{param} - {facility}")
    selected_facility_params = st.pills(
        "Velg fabrikkparametere",
        options=facility_options,
        default=facility_options,
        selection_mode="multi",
        key="sensitivity_analysis_facility_params"
    )
    effector_b = model_inputs.get("effector_b")
    type_b = model_inputs.get("type_b")
    protection_measure_options = []
    for effector in dict.fromkeys(effector_b):
        protection_measure_options.append(f"Suksessrate - {effector}")
    for param in ["Kostnad", "Antall effektorer"]:
        for protection_measure in dict.fromkeys(type_b):
            protection_measure_options.append(f"{param} - {protection_measure}")
    selected_protection_measure_params = st.pills(
        "Velg beskyttelsestiltak-parametere",
        options=protection_measure_options,
        default=protection_measure_options,
        selection_mode="multi",
        key="sensitivity_analysis_protection_measure_params"
    )
    selected_budget_params = st.pills(
        "Velg budsjettparametere",
        options=["Blått budsjett", "Rødt budsjett", "Biobudsjett"],
        default=["Blått budsjett", "Rødt budsjett", "Biobudsjett"],
        selection_mode="multi",
        key="sensitivity_analysis_budget_params"
    )
    selected_params = selected_facility_params + selected_protection_measure_params + selected_budget_params
    if not selected_params:
        st.warning("Velg minst én parameter for sensitivitetsanalysen")
        return
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
        st.session_state.sensitivity_analysis_results = {}
        base_result = solve_interdiction(F, type_f, K_f, H_f, C_f, beta_f, B, C_b, P_b, A_b, OE, T, R,
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
                _K_f, _H_f, _C_f = K_f.copy(), H_f.copy(), C_f.copy()
                _C_b, _P_b, _A_b = C_b.copy(), P_b.copy(), A_b.copy()
                _OE, _T, _R = OE, T, R
                factor = 1 + (variation / 100)
                param_value = None
                if param in selected_facility_params:
                    param_name, facility_name = param.split(" - ", 1)
                    if param_name == "Kostnad":
                        for f in range(F):
                            if type_f[f] == facility_name:
                                _C_f[f] = C_f[f] * factor
                                param_value = _C_f[f]
                    elif param_name == "Kapasitet":
                        for f in range(F):
                            if type_f[f] == facility_name:
                                _K_f[f] = round(K_f[f] * factor) # Integer
                                param_value = _K_f[f]
                    else: # param_name == "Hardhet"
                        for f in range(F):
                            if type_f[f] == facility_name:
                                _H_f[f] = H_f[f] * factor
                                param_value = _H_f[f]
                elif param in selected_protection_measure_params:
                    param_name, type_name = param.split(" - ", 1)
                    if param_name == "Suksessrate":
                        for b in range(B):
                            if effector_b[b] == type_name:
                                if P_b[b] * factor > 1.0:
                                    _P_b[b] = 1.0  # Probability cannot exceed 100%
                                else:
                                    _P_b[b] = P_b[b] * factor
                                param_value = _P_b[b]
                    elif param_name == "Kostnad":
                        for b in range(B):
                            if type_b[b] == type_name:
                                _C_b[b] = C_b[b] * factor
                                param_value = _C_b[b]
                    else: # param_name == "Antall effektorer"
                        for b in range(B):
                            if type_b[b] == type_name:
                                _A_b[b] = round(A_b[b] * factor) # Integer
                                param_value = _A_b[b]
                else: # Budget parameters
                    if param == "Blått budsjett":
                        _OE = OE * factor
                        param_value = _OE
                    elif param == "Rødt budsjett":
                        _T = T * factor
                        param_value = _T
                    elif param == "Biobudsjett":
                        _R = round(R * factor) # Integer
                        param_value = _R
                result = solve_interdiction(F, type_f, _K_f, _H_f, _C_f, beta_f, B, _C_b, _P_b, _A_b, _OE, _T, _R,
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
