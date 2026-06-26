import pandas as pd
import streamlit as st

potential_facilities = pd.DataFrame([
    {
        "Fabrikk": "Mongstad",
        "Kostnad": 0,
        "Kapasitet": 2100,
        "Hardhet": 3.0,
        "Maks antall": 1,
        "Biodrivstoff": False
    }, 
    {
        "Fabrikk": "Bio-SAF (stor)",
        "Kostnad": 3300,
        "Kapasitet": 170,
        "Hardhet": 3.0,
        "Maks antall": 3,
        "Biodrivstoff": True
    },
    {
        "Fabrikk": "Bio-SAF (mellomstor)",
        "Kostnad": 3400,
        "Kapasitet": 85,
        "Hardhet": 3.0,
        "Maks antall": 6,
        "Biodrivstoff": True
    },
    {
        "Fabrikk": "Bio-SAF (liten)",
        "Kostnad": 2400,
        "Kapasitet": 17,
        "Hardhet": 3.0,
        "Maks antall": 30,
        "Biodrivstoff": True
    },
    {
        "Fabrikk": "e-SAF",
        "Kostnad": 4100,
        "Kapasitet": 29,
        "Hardhet": 3.0,
        "Maks antall": 20,
        "Biodrivstoff": False
    },
])

effectors = pd.DataFrame([
    {
        "Effektor": "Luftvernmissil",
        "Suksessrate": 0.94
    }
])

potential_measures = pd.DataFrame([
    {
        "Beskyttelsestiltak": "Omfattende luftvern",
        "Kostnad": 19000,
        "Effektor": "Luftvernmissil",
        "Antall effektorer": 36
    },
    {
        "Beskyttelsestiltak": "Medium luftvern",
        "Kostnad": 9500,
        "Effektor": "Luftvernmissil",
        "Antall effektorer": 18
    },
    {
        "Beskyttelsestiltak": "Minimalt luftvern",
        "Kostnad": 4800,
        "Effektor": "Luftvernmissil",
        "Antall effektorer": 9
    },
])

restrictions = {
    "Blått budsjett": 30000,
    "Rødt budsjett": 15,
    "Biobudsjett": 500
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
            "Maks antall": st.column_config.NumberColumn(required=True),
            "Biodrivstoff": st.column_config.CheckboxColumn(default=False)
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
        ),
        "bio_budget": st.number_input(
            "Biobudsjett - maksimal totalproduksjon av biodrivstoff",
            value=restrictions["Biobudsjett"],
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
    beta_f = [] # Boolean indicating if facility f is a biofuel production facility
    for f_type in range(len(potential_facilities)):
        max_units = int(potential_facilities.iloc[f_type]["Maks antall"])
        for _ in range(max_units):
            F += 1
            type_f.append(potential_facilities.iloc[f_type]["Fabrikk"])
            C_f.append(float(potential_facilities.iloc[f_type]["Kostnad"]))
            K_f.append(int(potential_facilities.iloc[f_type]["Kapasitet"]))
            H_f.append(float(potential_facilities.iloc[f_type]["Hardhet"]))
            beta_f.append(bool(potential_facilities.iloc[f_type]["Biodrivstoff"]))
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
    OE = float(input_data["restrictions"]["blue_budget"]) # Blue budget - financial constraint
    T = float(input_data["restrictions"]["red_budget"]) # Red budget - number of threat effectors available
    R = int(input_data["restrictions"]["bio_budget"]) # Bio budget - maximum total biofuel production
    return {
        "F": F,
        "type_f": type_f,
        "K_f": K_f,
        "H_f": H_f,
        "C_f": C_f,
        "beta_f": beta_f,
        "B": B,
        "type_b": type_b,
        "C_b": C_b,
        "effector_b": effector_b,
        "P_b": P_b,
        "A_b": A_b,
        "OE": OE,
        "T": T,
        "R": R
    }