import streamlit as st
import pandas as pd
import altair as alt

def plot_remaining_production_capacity_vs_missile_budget():
    results = st.session_state.varying_missile_budget_results
    missile_budgets = []
    remaining_capacities = []
    for budget, result in results.items():
        missile_budgets.append(budget)
        remaining_capacities.append(result["remaining_production_capacity_after_attack"])
    df = pd.DataFrame({
        "Missilbudsjett": missile_budgets,
        "Produksjonskapasitet": remaining_capacities
    })
    chart = alt.Chart(df).mark_line(
        point=True
    ).encode(
        x=alt.X(
            "Missilbudsjett:O",
            title="Missilbudsjett",
            axis=alt.Axis(labelAngle=0, grid=True)
        ),
        y=alt.Y(
            "Produksjonskapasitet:Q",
            title="Produksjonskapasitet [m³/dag]"
        ),
        tooltip=["Missilbudsjett", "Produksjonskapasitet"],
    )
    st.altair_chart(chart)

def plot_facility_configuration_vs_missile_budget():
    type_f = st.session_state.varying_missile_budget_params["type_f"]
    results = st.session_state.varying_missile_budget_results
    data = []
    for budget, result in results.items():
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
                    "Missilbudsjett": budget,
                    "Fabrikktype": t,
                    "FabrikkID": f"{t} #{type_counters[t]}",
                    "Antall etablert": 1,
                    "Luftvern": ad,
                    "Ødelagt": dest
                })
        if not any(established):
            data.append({
                "Missilbudsjett": budget,
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
            "Missilbudsjett:O",
            title="Missilbudsjett",
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
        order=alt.Order("Ødelagt:O", sort="ascending"),
        stroke=alt.Stroke(
            "Ødelagt:N",
            scale=alt.Scale(domain=[True, False],
                            range=["fuchsia", "transparent"]
            ),
            legend=alt.Legend(title="Status",
                              orient="bottom",
                              values=[True],
                              labelExpr="'Fabrikk ødelagt'"
            )
        ),
        tooltip=["Missilbudsjett", "FabrikkID", "Luftvern", "Ødelagt"]
    )
    text = (
        alt.Chart(df).transform_window(
            stack_index='row_number()',
            groupby=["Missilbudsjett", "Fabrikktype"],
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
            x=alt.X("Missilbudsjett:O"),
            xOffset=alt.XOffset("Fabrikktype:N"),
            y=alt.Y(
                "LabelPos:Q"
            ),
            detail="FabrikkID:N",
            text=alt.Text("Luftvern:N"),
            tooltip=["Missilbudsjett", "FabrikkID", "Luftvern", "Ødelagt"]
        )
    )
    chart = bar + text
    st.altair_chart(chart, width="stretch")

def plot_costs_vs_missile_budget():
    B_B = st.session_state.varying_missile_budget_params["B_B"]
    C_f = st.session_state.varying_missile_budget_params["C_f"]
    C_A = st.session_state.varying_missile_budget_params["C_A"]
    results = st.session_state.varying_missile_budget_results
    missile_budget = []
    facility_and_air_defence_budget = []
    facility_costs = []
    air_defense_costs = []
    total_costs = []
    for B_R, result in results.items():
        missile_budget.append(B_R)
        facility_and_air_defence_budget.append(B_B)
        facility_cost = sum(C_f[f] for f, est in enumerate(result["established_facilities"]) if est)
        facility_costs.append(facility_cost)
        air_defense_cost = sum(C_A * a_f for f, a_f in enumerate(result["air_defense_assignment"]))
        air_defense_costs.append(air_defense_cost)
        total_costs.append(facility_cost + air_defense_cost)
    df = pd.DataFrame({
        "Missilbudsjett": missile_budget,
        "Budsjett": facility_and_air_defence_budget,
        "Fabrikkostnader": facility_costs,
        "Luftvernkostnader": air_defense_costs,
        "Totale kostnader": total_costs
    })
    df_melted = df.melt(id_vars=["Missilbudsjett"], 
                        value_vars=["Budsjett", "Fabrikkostnader", "Luftvernkostnader", "Totale kostnader"],
                        var_name="Kostnadstype",
                        value_name="Kostnad"
    )
    chart = alt.Chart(df_melted).mark_line(
        point=True
    ).encode(
        x=alt.X(
            "Missilbudsjett:O",
            title="Missilbudsjett",
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
        tooltip=["Missilbudsjett", "Kostnadstype", "Kostnad"],
    )
    st.altair_chart(chart)