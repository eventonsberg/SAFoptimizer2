import pandas as pd
import streamlit as st

potential_facilities = pd.DataFrame([
    {
        "Fabrikk": "Mongstad",
        "Kostnad": 0,
        "Kapasitet": 500,
        "Hardhet": 3.0,
        "Maks antall": 1
    }, 
    {
        "Fabrikk": "SAF-anlegg (liten)",
        "Kostnad": 20,
        "Kapasitet": 20,
        "Hardhet": 3.0,
        "Maks antall": 20
    },
    {
        "Fabrikk": "SAF-anlegg (stor)",
        "Kostnad": 100,
        "Kapasitet": 200,
        "Hardhet": 3.0,
        "Maks antall": 10
    }
])

effectors = pd.DataFrame([
    {
        "Effektor": "Luftvernmissil",
        "Suksessrate": 0.7
    }
])

potential_measures = pd.DataFrame([
    {
        "Beskyttelsestiltak": "Minimalt luftvern",
        "Kostnad": 30,
        "Effektor": "Luftvernmissil",
        "Antall effektorer": 6
    },
    {
        "Beskyttelsestiltak": "Omfattende luftvern",
        "Kostnad": 60,
        "Effektor": "Luftvernmissil",
        "Antall effektorer": 18
    }
])

restrictions = {
    "Blått budsjett": 250,
    "Rødt budsjett": 5
}

def display_input_fields():
    st.subheader("Potensielle fabrikker")
    potential_facilities_edited = st.data_editor(
        potential_facilities,
        num_rows="dynamic",
        column_config={
            "Fabrikk": st.column_config.TextColumn(required=True),
            "Kostnad": st.column_config.NumberColumn(format="localized", required=True),
            "Kapasitet": st.column_config.NumberColumn(format="localized", required=True),
            "Hardhet": st.column_config.NumberColumn(required=True),
            "Maks antall": st.column_config.NumberColumn(required=True)
        },
        key="potential_facilities"
    )

    st.subheader("Potensielle beskyttelsestiltak")
    effectors_edited = st.data_editor(
        effectors,
        num_rows="dynamic",
        column_config={
            "Effektor": st.column_config.TextColumn(required=True),
            "Suksessrate": st.column_config.NumberColumn(required=True)
        },
        key="effectors"
    )
    potential_measures_edited = st.data_editor(
        potential_measures,
        num_rows="dynamic",
        column_config={
            "Beskyttelsestiltak": st.column_config.TextColumn(required=True),
            "Kostnad": st.column_config.NumberColumn(format="localized", required=True),
            "Effektor": st.column_config.SelectboxColumn(options=effectors_edited["Effektor"].tolist(), required=True),
            "Antall effektorer": st.column_config.NumberColumn(format="localized", required=True)
        },
        key="potential_measures"
    )

    st.subheader("Begrensninger")
    restrictions_edited = {
        "blue_budget": st.number_input(
            "Blått budsjett - økonomisk ramme for fabrikker og beskyttelsestiltak",
            value=restrictions["Blått budsjett"],
            step=1,
            min_value=0,
            format="%d"
        ),
        "red_budget": st.number_input(
            "Rødt budsjett - antall trusseleffektorer til disposisjon",
            value=restrictions["Rødt budsjett"],
            step=1,
            min_value=0,
            format="%d"
        )
    }
    return {
        "potential_facilities": potential_facilities_edited,
        "effectors": effectors_edited,
        "potential_measures": potential_measures_edited,
        "restrictions": restrictions_edited
    }

def format_model_inputs(input_data):
    potential_facilities = input_data["potential_facilities"]
    F = 0 # Number of potential facilities
    type_f = [] # Type of facility f
    C_f = [] # Cost of facility f
    K_f = [] # Production capacity of facility f
    H_f = [] # Number of hits required to destroy facility f
    for f_type in range(len(potential_facilities)):
        max_units = int(potential_facilities.iloc[f_type]["Maks antall"])
        for _ in range(max_units):
            F += 1
            type_f.append(potential_facilities.iloc[f_type]["Fabrikk"])
            C_f.append(float(potential_facilities.iloc[f_type]["Kostnad"]))
            K_f.append(int(potential_facilities.iloc[f_type]["Kapasitet"]))
            H_f.append(float(potential_facilities.iloc[f_type]["Hardhet"]))
    effectors = input_data["effectors"]
    potential_measures = input_data["potential_measures"]
    B = len(potential_measures) # Number of potential protective measures
    type_b = [] # Type of protective measure b
    C_b = [] # Cost of protective measure b
    effector_b = [] # Effector used in protective measure b
    P_b = [] # Success rate of effectors in protective measure b
    A_b = [] # Number of effectors in protective measure b
    for b in range(B):
        type_b.append(potential_measures.iloc[b]["Beskyttelsestiltak"])
        C_b.append(float(potential_measures.iloc[b]["Kostnad"]))
        effector = potential_measures.iloc[b]["Effektor"]
        effector_b.append(effector)
        success_rate = effectors.loc[effectors["Effektor"] == effector, "Suksessrate"].values[0]
        P_b.append(float(success_rate))
        A_b.append(int(potential_measures.iloc[b]["Antall effektorer"]))
    OR = float(input_data["restrictions"]["blue_budget"]) # Blue budget - financial constraint
    TE = float(input_data["restrictions"]["red_budget"]) # Red budget - number of threat effectors available
    return F, type_f, K_f, H_f, C_f, B, type_b, C_b, effector_b, P_b, A_b, OR, TE