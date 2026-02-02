import streamlit as st
import pandas as pd
import altair as alt

def plot_remaining_production_capacity_vs_air_defense_cost():
    results = st.session_state.varying_air_defense_cost_results
    air_defense_costs = []
    remaining_capacities = []
    for C_A, result in results.items():
        air_defense_costs.append(C_A)
        remaining_capacities.append(result["remaining_production_capacity_after_attack"])
    df = pd.DataFrame({
        "Kostnad per luftvernmissil": air_defense_costs,
        "Produksjonskapasitet": remaining_capacities
    })
    chart = alt.Chart(df).mark_line(
        point=True
    ).encode(
        x=alt.X(
            "Kostnad per luftvernmissil:O",
            title="Kostnad per luftvernmissil [MNOK]",
            axis=alt.Axis(labelAngle=0, grid=True)
        ),
        y=alt.Y(
            "Produksjonskapasitet:Q",
            title="Produksjonskapasitet [m³/dag]"
        ),
        tooltip=["Kostnad per luftvernmissil", "Produksjonskapasitet"],
    )
    st.altair_chart(chart)

def plot_facility_configuration_vs_air_defense_cost():
    type_f = st.session_state.varying_air_defense_cost_params["type_f"]
    results = st.session_state.varying_air_defense_cost_results
    data = []
    for C_A, result in results.items():
        established = result["established_facilities"]
        air_defense = result["air_defense_assignment"]
        destroyed = result["attack_scenario"]
        type_counters = {}
        for idx, (t, est, ad, dest) in enumerate(zip(type_f, established, air_defense, destroyed)):
            if t not in type_counters:
                type_counters[t] = 0
            type_counters[t] += 1
            if est:
                data.append({
                    "Kostnad per luftvernmissil": C_A,
                    "Fabrikktype": t,
                    "FabrikkID": f"{t} #{type_counters[t]}",
                    "Antall etablert": 1,
                    "Luftvern": ad,
                    "Ødelagt": dest
                })
        if not any(established):
            data.append({
                "Kostnad per luftvernmissil": C_A,
                "Fabrikktype": None,
                "FabrikkID": None,
                "Antall etablert": None,
                "Luftvern": "",
                "Ødelagt": False
            })
    df = pd.DataFrame(data)
    bar = alt.Chart(df).mark_bar(
        strokeWidth=2,
        align="center"
    ).encode(
        x=alt.X(
            "Kostnad per luftvernmissil:O",
            title="Kostnad per luftvernmissil [MNOK]",
            axis=alt.Axis(labelAngle=0)
        ),
        xOffset=alt.XOffset("Fabrikktype:N"),
        y=alt.Y(
            "sum(Antall etablert):Q",
            title="Etablerte fabrikker"
        ),
        color=alt.Color(
            "Fabrikktype:N",
            title="Fabrikktype",
            legend=alt.Legend(orient="bottom")
        ),
        order=alt.Order("Ødelagt:N", sort="ascending"),
        stroke=alt.Stroke(
            "Ødelagt:N",
            scale=alt.Scale(
                domain=[True, False],
                range=["fuchsia", "transparent"]
            ),
            legend=alt.Legend(
                title="Status",
                orient="bottom",
                values=[True],
                labelExpr="'Fabrikk ødelagt'"
            )
        ),
        tooltip=["Kostnad per luftvernmissil", "FabrikkID", "Luftvern", "Ødelagt"],
    )
    text = (
        alt.Chart(df).transform_window(
            stack_index='row_number()',
            groupby=["Kostnad per luftvernmissil", "Fabrikktype"],
            sort=[
                alt.SortField("Ødelagt", order="ascending"),
                alt.SortField("FabrikkID", order="ascending")
            ]
        ).transform_calculate(
            LabelPos="datum.stack_index - 0.5"
        ).mark_text(
            align="center",
            baseline="middle"
        ).encode(
            x=alt.X("Kostnad per luftvernmissil:O"),
            xOffset=alt.XOffset("Fabrikktype:N"),
            y=alt.Y(
                "LabelPos:Q"
            ),
            detail="FabrikkID:N",
            text=alt.Text("Luftvern:N"),
            tooltip=["Kostnad per luftvernmissil", "FabrikkID", "Luftvern", "Ødelagt"]
        )
    )
    chart = bar + text
    st.altair_chart(chart)

def plot_costs_vs_air_defense_cost():
    C_f = st.session_state.varying_air_defense_cost_params["C_f"]
    B_B = st.session_state.varying_air_defense_cost_params["B_B"]
    results = st.session_state.varying_air_defense_cost_results
    air_defense_unit_costs = []
    facility_costs = []
    air_defense_costs = []
    total_costs = []
    for C_A, result in results.items():
        air_defense_unit_costs.append(C_A)
        facility_cost = sum(C_f[f] for f, est in enumerate(result["established_facilities"]) if est)
        facility_costs.append(facility_cost)
        air_defense_cost = sum(C_A * a_f for f, a_f in enumerate(result["air_defense_assignment"]))
        air_defense_costs.append(air_defense_cost)
        total_costs.append(facility_cost + air_defense_cost)
    df = pd.DataFrame({
        "Kostnad per luftvernmissil": air_defense_unit_costs,
        "Budsjett": B_B,
        "Fabrikkostnader": facility_costs,
        "Luftvernkostnader": air_defense_costs,
        "Totale kostnader": total_costs
    })
    df_melted = df.melt(id_vars=["Kostnad per luftvernmissil"],
                        value_vars=["Budsjett", "Fabrikkostnader", "Luftvernkostnader", "Totale kostnader"],
                        var_name="Kostnadstype",
                        value_name="Kostnad"
    )
    chart = alt.Chart(df_melted).mark_line(
        point=True
    ).encode(
        x=alt.X(
            "Kostnad per luftvernmissil:O",
            title="Kostnad per luftvernmissil [MNOK]",
            axis=alt.Axis(labelAngle=0, grid=True)
        ),
        y=alt.Y(
            "Kostnad:Q",
            title="Kostnad [MNOK]"
        ),
        color=alt.Color(
            "Kostnadstype:N",
            title="Kostnadstype",
            legend=alt.Legend(orient="bottom")
        ),
        tooltip=["Kostnad per luftvernmissil", "Kostnadstype", "Kostnad"]
    )
    st.altair_chart(chart)