import streamlit as st
import pandas as pd
import altair as alt

def plot_blue_vs_red_budget_heatmap():
    results = st.session_state.varying_blue_vs_red_budget_results
    blue_budgets = []
    red_budgets = []
    production_capacities = []
    for (blue_budget, red_budget), result in results.items():
        blue_budgets.append(blue_budget)
        red_budgets.append(red_budget)
        production_capacities.append(result["remaining_production_capacity_after_attack"])
    df = pd.DataFrame({
        "Blått budsjett": blue_budgets,
        "Rødt budsjett": red_budgets,
        "Produksjonskapasitet": production_capacities
    })
    chart = alt.Chart(df).mark_rect().encode(
        x=alt.X(
            "Blått budsjett:O",
            title="Blått budsjett [MNOK]",
            axis=alt.Axis(labelAngle=0)
        ),
        y=alt.Y(
            "Rødt budsjett:O",
            title="Rødt budsjett [# trusseleffektorer]",
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
        tooltip=["Blått budsjett", "Rødt budsjett", "Produksjonskapasitet"],
    )
    st.altair_chart(chart, height=400)

def plot_production_capacity_vs_blue_budget_for_different_red_budgets():
    results = st.session_state.varying_blue_vs_red_budget_results
    data = []
    for (blue_budget, red_budget), result in results.items():
        data.append({
            "Blått budsjett": blue_budget,
            "Rødt budsjett": red_budget,
            "Produksjonskapasitet": result["remaining_production_capacity_after_attack"]
        })
    df = pd.DataFrame(data)
    chart = alt.Chart(df).mark_line(
        point=True
    ).encode(
        x=alt.X(
            "Blått budsjett:O",
            title="Blått budsjett [MNOK]",
            axis=alt.Axis(labelAngle=0, grid=True)
        ),
        y=alt.Y(
            "Produksjonskapasitet:Q",
            title="Produksjonskapasitet [m³/dag]"
        ),
        color=alt.Color(
            "Rødt budsjett:N",
            title="Rødt budsjett [# trusseleffektorer]",
            legend=alt.Legend(
                orient="bottom",
                titleLimit=300
            )
        ),
        tooltip=["Blått budsjett", "Rødt budsjett", "Produksjonskapasitet"],
    )
    st.altair_chart(chart)

def plot_production_capacity_vs_red_budget_for_different_blue_budgets():
    results = st.session_state.varying_blue_vs_red_budget_results
    data = []
    for (blue_budget, red_budget), result in results.items():
        data.append({
            "Blått budsjett": blue_budget,
            "Rødt budsjett": red_budget,
            "Produksjonskapasitet": result["remaining_production_capacity_after_attack"]
        })
    df = pd.DataFrame(data)
    chart = alt.Chart(df).mark_line(
        point=True
    ).encode(
        x=alt.X(
            "Rødt budsjett:O",
            title="Rødt budsjett [# trusseleffektorer]",
            axis=alt.Axis(labelAngle=0, grid=True)
        ),
        y=alt.Y(
            "Produksjonskapasitet:Q",
            title="Produksjonskapasitet [m³/dag]"
        ),
        color=alt.Color(
            "Blått budsjett:N",
            title="Blått budsjett [MNOK]",
            legend=alt.Legend(
                orient="bottom",
                titleLimit=300
            )
        ),
        tooltip=["Blått budsjett", "Rødt budsjett", "Produksjonskapasitet"],
    )
    st.altair_chart(chart)