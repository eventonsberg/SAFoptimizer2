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
        "Gjenværende produksjonskapasitet": remaining_capacities
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
            "Gjenværende produksjonskapasitet:Q",
            title="Produksjonskapasitet [m³/dag]"
        ),
        tooltip=["Missilbudsjett", "Gjenværende produksjonskapasitet"],
    )
    st.altair_chart(chart)

def plot_facility_configuration_vs_missile_budget(type_f):
    results = st.session_state.varying_missile_budget_results
    data = []
    for budget, result in results.items():
        established = result["established_facilities"]
        air_defense = result["air_defense_assignment"]
        destroyed = result["attack_scenario"]
        for idx, (t, est, ad, dest) in enumerate(zip(type_f, established, air_defense, destroyed)):
            if est:
                data.append({
                    "Missilbudsjett": budget,
                    "Fabrikktype": t,
                    "FabrikkID": f"{t} #{idx+1}",
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
            title="",
            legend=alt.Legend(orient="bottom")
        ),
        order=alt.Order("Ødelagt:O", sort="ascending"),
        stroke=alt.Stroke(
            "Ødelagt:N",
            scale=alt.Scale(domain=[True, False],
                            range=["fuchsia", "transparent"]
            ),
            legend=alt.Legend(title="",
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
            text=alt.Text("Luftvern:N")
        )
    )
    chart = bar + text
    st.altair_chart(chart, width="stretch")