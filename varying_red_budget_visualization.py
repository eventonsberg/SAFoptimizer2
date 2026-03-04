import streamlit as st
import pandas as pd
import altair as alt

def plot_remaining_production_capacity_vs_red_budget():
    results = st.session_state.varying_red_budget_results
    red_budgets = []
    remaining_capacities = []
    for budget, result in results.items():
        red_budgets.append(budget)
        remaining_capacities.append(result["remaining_production_capacity_after_attack"])
    df = pd.DataFrame({
        "Rødt budsjett": red_budgets,
        "Produksjonskapasitet": remaining_capacities
    })
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
        tooltip=["Rødt budsjett", "Produksjonskapasitet"],
    )
    st.altair_chart(chart)

def plot_facility_configuration_vs_red_budget():
    F = st.session_state.varying_red_budget_params["F"]
    type_f = st.session_state.varying_red_budget_params["type_f"]
    B = st.session_state.varying_red_budget_params["B"]
    type_b = st.session_state.varying_red_budget_params["type_b"]
    results = st.session_state.varying_red_budget_results
    data = []
    for budget, result in results.items():
        established_f = result["established_facilities"]
        implemented_bf = result["implemented_protection_measures"]
        destroyed_f = result["destroyed_facilities"]
        facility_counters = {}
        for f in range(F):
            if established_f[f]:
                facility = type_f[f]
                if facility not in facility_counters:
                    facility_counters[facility] = 0
                facility_counters[facility] += 1
                protection_measure_string = ""
                protection_measure_types = [type_b[b] for b in range(B) if implemented_bf[b][f]]
                if protection_measure_types:
                    protection_measure_string = ", ".join(protection_measure_types)
                data.append({
                    "Rødt budsjett": budget,
                    "Fabrikktype": facility,
                    "FabrikkID": f"{facility} #{facility_counters[facility]}",
                    "Antall etablert": 1,
                    "Beskyttelsestiltak": protection_measure_string,
                    "Ødelagt": destroyed_f[f]
                })
        if not any(established_f):
            data.append({ # Avoid empty dataframe if no facilities are established
                "Rødt budsjett": budget,
                "Fabrikktype": None,
                "FabrikkID": None,
                "Antall etablert": None,
                "Beskyttelsestiltak": "",
                "Ødelagt": False
            })
    df = pd.DataFrame(data)
    bar = alt.Chart(df).mark_bar(
        strokeWidth=3,
        align="center"
    ).encode(
        x=alt.X(
            "Rødt budsjett:O",
            title="Rødt budsjett [# trusseleffektorer]",
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
            legend=alt.Legend(
                orient="bottom",
                direction="vertical"
            ),
            scale=alt.Scale(
                scheme="set2"
            )
        ),
        order=alt.Order("Ødelagt:N", sort="ascending"),
        stroke=alt.Stroke(
            "Ødelagt:N",
            scale=alt.Scale(
                domain=[True, False],
                range=["#c30101", "transparent"]
            ),
            legend=alt.Legend(
                title="Status",
                orient="bottom",
                values=[True],
                labelExpr="'Fabrikk ødelagt'",
                symbolStrokeWidth=3,
                symbolFillColor="transparent"
            )
        ),
        tooltip=["Rødt budsjett", "FabrikkID", "Beskyttelsestiltak", "Ødelagt"],
    )
    protection_measures_df = df[df["Beskyttelsestiltak"] != ""]
    if protection_measures_df.empty:
        chart = bar # If no protection measures, just show the bar chart
    else:
        point = ( # Overlay symbols for protection measures on top of the bar chart
            alt.Chart(protection_measures_df).transform_window(
                stack_index='row_number()',
                groupby=["Rødt budsjett", "Fabrikktype"],
                sort=[
                    alt.SortField("Ødelagt", order="ascending"),
                    alt.SortField("FabrikkID", order="ascending")
                ]
            ).transform_calculate(
                LabelPos="datum.stack_index - 0.5"
            ).mark_point(
                color="blue",
                opacity=1,
                size=80,
                strokeWidth=2
            ).encode(
                x=alt.X("Rødt budsjett:O"),
                xOffset=alt.XOffset("Fabrikktype:N"),
                y=alt.Y(
                    "LabelPos:Q"
                ),
                detail="FabrikkID:N",
                shape=alt.Shape(
                    "Beskyttelsestiltak:N",
                    scale=alt.Scale(
                        range=["circle", "triangle-up", "diamond", "cross", "triangle-down"]
                    ),
                    title="Beskyttelsestiltak",
                    legend=alt.Legend(
                        orient="bottom",
                        direction="vertical",
                        symbolStrokeWidth=3
                    )
                ),
                tooltip=["Rødt budsjett", "FabrikkID", "Beskyttelsestiltak", "Ødelagt"]
            )
        )
        chart = bar + point
    st.altair_chart(chart)

def plot_costs_vs_red_budget():
    F = st.session_state.varying_red_budget_params["F"]
    C_f = st.session_state.varying_red_budget_params["C_f"]
    B = st.session_state.varying_red_budget_params["B"]
    C_b = st.session_state.varying_red_budget_params["C_b"]
    OR = st.session_state.varying_red_budget_params["OR"]
    results = st.session_state.varying_red_budget_results
    red_budgets = []
    facility_costs = []
    protection_measure_costs = []
    total_costs = []
    for TE, result in results.items():
        red_budgets.append(TE)
        established_f = result["established_facilities"]
        facility_cost = sum(C_f[f] for f in range(F) if established_f[f])
        facility_costs.append(facility_cost)
        implemented_bf = result["implemented_protection_measures"]
        protection_measure_cost = sum(C_b[b] * implemented_bf[b][f] for f in range(F) for b in range(B))
        protection_measure_costs.append(protection_measure_cost)
        total_costs.append(facility_cost + protection_measure_cost)
    df = pd.DataFrame({
        "Rødt budsjett": red_budgets,
        "Totalbudsjett": OR,
        "Kostnad fabrikker": facility_costs,
        "Kostnad beskyttelsestiltak": protection_measure_costs,
        "Totalkostnad": total_costs
    })
    df_melted = df.melt(id_vars=["Rødt budsjett"],
                        value_vars=["Totalbudsjett", "Kostnad fabrikker", "Kostnad beskyttelsestiltak", "Totalkostnad"],
                        var_name="Kostnadstype",
                        value_name="Kostnad"
    )
    chart = alt.Chart(df_melted).mark_line(
        point=True
    ).encode(
        x=alt.X(
            "Rødt budsjett:O",
            title="Rødt budsjett [MNOK]",
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
        tooltip=["Rødt budsjett", "Kostnadstype", "Kostnad"]
    )
    st.altair_chart(chart)