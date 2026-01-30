import pandas as pd
import streamlit as st

potential_facilities = pd.DataFrame([
    {
        "Type": "Mongstad",
        "Kapasitet": 500,
        "Kostnad": 0,
        "Hardhet": 3.0,
        "Maks antall": 1
    },
    
    {
        "Type": "SAF-anlegg (liten)",
        "Kapasitet": 20,
        "Kostnad": 20,
        "Hardhet": 3.0,
        "Maks antall": 12
    },
    {
        "Type": "SAF-anlegg (stor)",
        "Kapasitet": 200,
        "Kostnad": 100,
        "Hardhet": 3.0,
        "Maks antall": 2
    }
])

air_defense = {
    "Kostnad": 5,
    "Suksessrate": 0.7,
    "Maks antall": 20
}

restrictions = {
        "Missilbudsjett": 5,
        "Fabrikk- og luftvernbudsjett": 250
    }

def display_input_fields():
    st.subheader("Potensielle fabrikker")
    potential_facilities_edited = st.data_editor(
        potential_facilities,
        num_rows="dynamic",
        column_config={
            "Kostnad": st.column_config.NumberColumn(format="localized")
        },
        key="prod_facilities"
    )
    st.subheader("Luftvern")
    air_defense_edited = {
        "cost": st.number_input(
            "Kostnad per luftvernmissil",
            value=air_defense["Kostnad"],
            step=1,
            min_value=0,
            format="%d"
        ),
        "success_rate": st.number_input(
            "Suksessrate",
            value=air_defense["Suksessrate"],
            step=0.01,
            min_value=0.0,
            max_value=1.0,
            format="%.2f"
        ),
        "max_count": st.number_input(
            "Maks antall luftvernmissiler per fabrikk",
            value=air_defense["Maks antall"],
            step=1,
            min_value=0,
            format="%d"
        )
    }
    st.subheader("Begrensninger")
    restrictions_edited = {
        "factory_and_air_defense_budget": st.number_input(
            "Fabrikk- og luftvernbudsjett",
            value=restrictions["Fabrikk- og luftvernbudsjett"],
            step=1,
            min_value=0,
            format="%d"
        ),
        "missile_budget": st.number_input(
            "Missilbudsjett",
            value=restrictions["Missilbudsjett"],
            step=1,
            min_value=0,
            format="%d"
        )
    }
    return {
        "potential_facilities": potential_facilities_edited,
        "air_defense": air_defense_edited,
        "restrictions": restrictions_edited
    }

def format_model_inputs(input_data):
    P_A = float(input_data["air_defense"]["success_rate"]) # Probability of successful interception by an air defense missile
    C_A = int(input_data["air_defense"]["cost"]) # Cost of an air defense missile
    A_max = int(input_data["air_defense"]["max_count"]) # Maximum number of air defense missiles protecting a facility
    B_R = int(input_data["restrictions"]["missile_budget"]) # Missile budget
    B_B = int(input_data["restrictions"]["factory_and_air_defense_budget"]) # Facility and air defense budget
    potential_facilities = input_data["potential_facilities"]
    F = 0 # Number of potential facilities
    type_f = [] # Type of facility f
    K_f = [] # Production capacity of facility f
    H_f = [] # Number of hits required to destroy facility f
    C_f = [] # Cost of facility f
    for f_type in range(len(potential_facilities)):
        max_units = int(potential_facilities.iloc[f_type]["Maks antall"])
        for _ in range(max_units):
            F += 1
            type_f.append(potential_facilities.iloc[f_type]["Type"])
            K_f.append(int(potential_facilities.iloc[f_type]["Kapasitet"]))
            H_f.append(float(potential_facilities.iloc[f_type]["Hardhet"]))
            C_f.append(int(potential_facilities.iloc[f_type]["Kostnad"]))
    return P_A, C_A, A_max, B_R, B_B, F, type_f, K_f, H_f, C_f