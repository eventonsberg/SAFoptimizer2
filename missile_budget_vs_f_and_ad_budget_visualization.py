import streamlit as st
import pandas as pd
import altair as alt

def plot_missile_budget_vs_f_and_ad_budget_heatmap():
    results = st.session_state.varying_missile_budget_vs_f_and_ad_budget_results
    missile_budgets = []
    f_and_ad_budgets = []
    production_capacities = []
    for (missile_budget, f_and_ad_budget), result in results.items():
        missile_budgets.append(missile_budget)
        f_and_ad_budgets.append(f_and_ad_budget)
        production_capacities.append(result["remaining_production_capacity_after_attack"])
    df = pd.DataFrame({
        "Missilbudsjett": missile_budgets,
        "Fabrikk- og luftvernbudsjett": f_and_ad_budgets,
        "Produksjonskapasitet": production_capacities
    })
    chart = alt.Chart(df).mark_rect().encode(
        x=alt.X(
            "Fabrikk- og luftvernbudsjett:O",
            title="Fabrikk- og luftvernbudsjett [MNOK]",
            axis=alt.Axis(labelAngle=0)
        ),
        y=alt.Y(
            "Missilbudsjett:O",
            title="Missilbudsjett",
            sort="descending"
        ),
        color=alt.Color(
            "Produksjonskapasitet:Q",
            title="Produksjonskapasitet [m³/dag]",
            scale=alt.Scale(scheme="redblue"),
            legend=alt.Legend(
                orient="bottom",
                gradientLength=300,
                titleLimit=300
            )
        ),
        tooltip=["Missilbudsjett", "Fabrikk- og luftvernbudsjett", "Produksjonskapasitet"],
    )
    st.altair_chart(chart, height=400)

def plot_production_capacity_vs_f_and_ad_budget_for_different_missile_budgets():
    results = st.session_state.varying_missile_budget_vs_f_and_ad_budget_results
    missile_budgets = sorted(set([key[0] for key in results.keys()]))
    f_and_ad_budgets = sorted(set([key[1] for key in results.keys()]))
    data = []
    for missile_budget in missile_budgets:
        for f_and_ad_budget in f_and_ad_budgets:
            result = results.get((missile_budget, f_and_ad_budget))
            if result:
                data.append({
                    "Missilbudsjett": missile_budget,
                    "Fabrikk- og luftvernbudsjett": f_and_ad_budget,
                    "Produksjonskapasitet": result["remaining_production_capacity_after_attack"]
                })
    df = pd.DataFrame(data)
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
        color=alt.Color(
            "Missilbudsjett:N",
            title="Missilbudsjett",
            legend=alt.Legend(orient="bottom")
        ),
        tooltip=["Missilbudsjett", "Fabrikk- og luftvernbudsjett", "Produksjonskapasitet"],
    )
    st.altair_chart(chart)

def plot_production_capacity_vs_missile_budget_for_different_f_and_ad_budgets():
    results = st.session_state.varying_missile_budget_vs_f_and_ad_budget_results
    missile_budgets = sorted(set([key[0] for key in results.keys()]))
    f_and_ad_budgets = sorted(set([key[1] for key in results.keys()]))
    data = []
    for f_and_ad_budget in f_and_ad_budgets:
        for missile_budget in missile_budgets:
            result = results.get((missile_budget, f_and_ad_budget))
            if result:
                data.append({
                    "Fabrikk- og luftvernbudsjett": f_and_ad_budget,
                    "Missilbudsjett": missile_budget,
                    "Produksjonskapasitet": result["remaining_production_capacity_after_attack"]
                })
    df = pd.DataFrame(data)
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
        color=alt.Color(
            "Fabrikk- og luftvernbudsjett:N",
            title="Fabrikk- og luftvernbudsjett [MNOK]",
            legend=alt.Legend(
                orient="bottom",
                titleLimit=300
            )
        ),
        tooltip=["Fabrikk- og luftvernbudsjett", "Missilbudsjett", "Produksjonskapasitet"],
    )
    st.altair_chart(chart)