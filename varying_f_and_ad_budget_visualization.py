import streamlit as st
import pandas as pd
import altair as alt

def plot_remaining_production_capacity_vs_f_and_ad_budget():
    results = st.session_state.varying_f_and_ad_budget_results
    f_and_ad_budgets = []
    remaining_capacities = []
    for budget, result in results.items():
        f_and_ad_budgets.append(budget)
        remaining_capacities.append(result["remaining_production_capacity_after_attack"])
    df = pd.DataFrame({
        "Fabrikk- og luftvernbudsjett": f_and_ad_budgets,
        "Produksjonskapasitet": remaining_capacities
    })
    chart = alt.Chart(df).mark_line(
        point=True
    ).encode(
        x=alt.X(
            "Fabrikk- og luftvernbudsjett:O",
            title="Fabrikk- og luftvernbudsjett [MNOK]",
            axis=alt.Axis(labelAngle=0, grid=True)
        ),
        y=alt.Y(
            "Produksjonskapasitet:Q",
            title="Produksjonskapasitet [m³/dag]"
        ),
        tooltip=["Fabrikk- og luftvernbudsjett", "Produksjonskapasitet"],
    )
    st.altair_chart(chart)

def plot_facility_configuration_vs_f_and_ad_budget(type_f):
    results = st.session_state.varying_f_and_ad_budget_results
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
                    "Fabrikk- og luftvernbudsjett": budget,
                    "Fabrikktype": t,
                    "FabrikkID": f"{t} #{type_counters[t]}",
                    "Antall etablert": 1,
                    "Luftvern": ad,
                    "Ødelagt": dest
                })
    df = pd.DataFrame(data)
    bar = alt.Chart(df).mark_bar(
        strokeWidth=2,
        align="center"
    ).encode(
        x=alt.X(
            "Fabrikk- og luftvernbudsjett:O",
            title="Fabrikk- og luftvernbudsjett [MNOK]",
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
        tooltip=["Fabrikk- og luftvernbudsjett", "FabrikkID", "Luftvern", "Ødelagt"],
    )
    text = (
        alt.Chart(df).transform_window(
            stack_index='row_number()',
            groupby=["Fabrikk- og luftvernbudsjett", "Fabrikktype"],
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
            x=alt.X("Fabrikk- og luftvernbudsjett:O"),
            xOffset=alt.XOffset("Fabrikktype:N"),
            y=alt.Y(
                "LabelPos:Q"
            ),
            detail="FabrikkID:N",
            text=alt.Text("Luftvern:N"),
            tooltip=["Fabrikk- og luftvernbudsjett", "FabrikkID", "Luftvern", "Ødelagt"]
        )
    )
    chart = bar + text
    st.altair_chart(chart)

def plot_costs_vs_f_and_ad_budget(C_f, C_A):
    results = st.session_state.varying_f_and_ad_budget_results
    f_and_ad_budgets = []
    facility_costs = []
    air_defense_costs = []
    total_costs = []
    for B_B, result in results.items():
        f_and_ad_budgets.append(B_B)
        facility_cost = sum(C_f[f] for f, est in enumerate(result["established_facilities"]) if est)
        facility_costs.append(facility_cost)
        air_defense_cost = sum(C_A * a_f for f, a_f in enumerate(result["air_defense_assignment"]))
        air_defense_costs.append(air_defense_cost)
        total_costs.append(facility_cost + air_defense_cost)
    df = pd.DataFrame({
        "Fabrikk- og luftvernbudsjett": f_and_ad_budgets,
        "Budsjett": f_and_ad_budgets,
        "Fabrikkostnader": facility_costs,
        "Luftvernkostnader": air_defense_costs,
        "Totale kostnader": total_costs
    })
    df_melted = df.melt(id_vars=["Fabrikk- og luftvernbudsjett"],
                        value_vars=["Budsjett", "Fabrikkostnader", "Luftvernkostnader", "Totale kostnader"],
                        var_name="Kostnadstype",
                        value_name="Kostnad"
    )
    chart = alt.Chart(df_melted).mark_line(
        point=True
    ).encode(
        x=alt.X(
            "Fabrikk- og luftvernbudsjett:O",
            title="Fabrikk- og luftvernbudsjett [MNOK]",
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
        tooltip=["Fabrikk- og luftvernbudsjett", "Kostnadstype", "Kostnad"]
    )
    st.altair_chart(chart)