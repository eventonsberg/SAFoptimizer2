import streamlit as st
import pandas as pd
import altair as alt

def plot_remaining_production_capacity_vs_bio_budget():
    results = st.session_state.varying_bio_budget_results
    bio_budgets = []
    remaining_capacities = []
    for budget, result in results.items():
        bio_budgets.append(budget)
        remaining_capacities.append(result["remaining_production_capacity_after_attack"])
    df = pd.DataFrame({
        "Biobudsjett": bio_budgets,
        "Produksjonskapasitet": remaining_capacities
    })
    chart = alt.Chart(df).mark_line(
        point=True
    ).encode(
        x=alt.X(
            "Biobudsjett:O",
            title="Biobudsjett [m³/dag]",
            axis=alt.Axis(labelAngle=0, grid=True)
        ),
        y=alt.Y(
            "Produksjonskapasitet:Q",
            title="Produksjonskapasitet [m³/dag]",
            axis=alt.Axis(labelBaseline="middle")
        ),
        tooltip=["Biobudsjett", "Produksjonskapasitet"],
    )
    st.altair_chart(chart)

def plot_facility_configuration_vs_bio_budget():
    F = st.session_state.varying_bio_budget_params["F"]
    type_f = st.session_state.varying_bio_budget_params["type_f"]
    B = st.session_state.varying_bio_budget_params["B"]
    type_b = st.session_state.varying_bio_budget_params["type_b"]
    results = st.session_state.varying_bio_budget_results
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
                    "Biobudsjett": budget,
                    "Fabrikktype": facility,
                    "FabrikkID": f"{facility} #{facility_counters[facility]}",
                    "Antall etablert": 1,
                    "Beskyttelsestiltak": protection_measure_string,
                    "Ødelagt": destroyed_f[f]
                })
        if not any(established_f):
            data.append({ # Avoid empty dataframe if no facilities are established
                "Biobudsjett": budget,
                "Fabrikktype": None,
                "FabrikkID": None,
                "Antall etablert": None,
                "Beskyttelsestiltak": "",
                "Ødelagt": False
            })
    df = pd.DataFrame(data)
    all_facility_types = list(dict.fromkeys(type_f))
    present_facility_types_in_df = set(df["Fabrikktype"].dropna())
    present_facility_types = [
        facility_type for facility_type in all_facility_types
        if facility_type in present_facility_types_in_df
    ]
    bar = alt.Chart(df).mark_bar(
        strokeWidth=3,
        align="center"
    ).encode(
        x=alt.X(
            "Biobudsjett:O",
            title="Biobudsjett [m³/dag]",
            axis=alt.Axis(labelAngle=0, grid=True, bandPosition=1.125)
        ),
        xOffset=alt.XOffset(
            "Fabrikktype:N",
            scale=alt.Scale(domain=present_facility_types)
        ),
        y=alt.Y(
            "sum(Antall etablert):Q",
            title="Etablerte fabrikker",
            axis=alt.Axis(format="d", labelBaseline="middle")
        ),
        color=alt.Color(
            "Fabrikktype:N",
            title="Fabrikktype",
            legend=alt.Legend(
                orient="bottom",
                direction="vertical",
                values=present_facility_types
            ),
            scale=alt.Scale(
                domain=all_facility_types,
                scheme="set2"
            ),
            sort=all_facility_types
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
        tooltip=["Biobudsjett", "FabrikkID", "Beskyttelsestiltak", "Ødelagt"],
    )
    protection_measures_df = df[df["Beskyttelsestiltak"] != ""]
    present_protection_measures_in_df = set(protection_measures_df["Beskyttelsestiltak"])
    all_protection_measures = list(dict.fromkeys(type_b))
    present_protection_measures = [
        protection_measure for protection_measure in all_protection_measures
        if protection_measure in present_protection_measures_in_df
    ]
    if protection_measures_df.empty:
        chart = bar # If no protection measures, just show the bar chart
    else:
        shape_palette = [
            "circle",
            "triangle-up",
            "diamond",
            "cross",
            "triangle-down",
            "square",
            "triangle-right",
            "triangle-left"
        ]
        fixed_shape_range = [
            shape_palette[i % len(shape_palette)] for i in range(len(all_protection_measures))
        ]
        point = ( # Overlay symbols for protection measures on top of the bar chart
            alt.Chart(protection_measures_df).transform_window(
                stack_index='row_number()',
                groupby=["Biobudsjett", "Fabrikktype"],
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
                x=alt.X("Biobudsjett:O"),
                xOffset=alt.XOffset(
                    "Fabrikktype:N",
                    scale=alt.Scale(domain=present_facility_types)
                ),
                y=alt.Y(
                    "LabelPos:Q"
                ),
                detail="FabrikkID:N",
                shape=alt.Shape(
                    "Beskyttelsestiltak:N",
                    scale=alt.Scale(
                        domain=all_protection_measures,
                        range=fixed_shape_range
                    ),
                    title="Beskyttelsestiltak",
                    legend=alt.Legend(
                        orient="bottom",
                        direction="vertical",
                        values=present_protection_measures,
                        symbolStrokeWidth=3
                    )
                ),
                tooltip=["Biobudsjett", "FabrikkID", "Beskyttelsestiltak", "Ødelagt"]
            )
        )
        chart = bar + point
    st.altair_chart(chart)

def plot_costs_vs_bio_budget():
    F = st.session_state.varying_bio_budget_params["F"]
    C_f = st.session_state.varying_bio_budget_params["C_f"]
    B = st.session_state.varying_bio_budget_params["B"]
    C_b = st.session_state.varying_bio_budget_params["C_b"]
    OE = st.session_state.varying_bio_budget_params["OE"]
    results = st.session_state.varying_bio_budget_results
    bio_budgets = []
    facility_costs = []
    protection_measure_costs = []
    total_costs = []
    for R, result in results.items():
        bio_budgets.append(R)
        established_f = result["established_facilities"]
        facility_cost = sum(C_f[f] for f in range(F) if established_f[f])
        facility_costs.append(facility_cost)
        implemented_bf = result["implemented_protection_measures"]
        protection_measure_cost = sum(C_b[b] * implemented_bf[b][f] for f in range(F) for b in range(B))
        protection_measure_costs.append(protection_measure_cost)
        total_costs.append(facility_cost + protection_measure_cost)
    df = pd.DataFrame({
        "Biobudsjett": bio_budgets,
        "Totalbudsjett": OE,
        "Kostnad fabrikker": facility_costs,
        "Kostnad beskyttelsestiltak": protection_measure_costs,
        "Totalkostnad": total_costs
    })
    df_melted = df.melt(id_vars=["Biobudsjett"],
                        value_vars=["Totalbudsjett", "Kostnad fabrikker", "Kostnad beskyttelsestiltak", "Totalkostnad"],
                        var_name="Kostnadstype",
                        value_name="Kostnad"
    )
    chart = alt.Chart(df_melted).mark_line(
        point=True
    ).encode(
        x=alt.X(
            "Biobudsjett:O",
            title="Biobudsjett [m³/dag]",
            axis=alt.Axis(labelAngle=0, grid=True)
        ),
        y=alt.Y(
            "Kostnad:Q",
            title="Kostnad [MNOK]",
            axis=alt.Axis(labelBaseline="middle")
        ),
        color=alt.Color(
            "Kostnadstype:N",
            title="Kostnadstype",
            legend=alt.Legend(orient="bottom")
        ),
        tooltip=["Biobudsjett", "Kostnadstype", "Kostnad"]
    )
    st.altair_chart(chart)

def plot_bio_production_vs_bio_budget():
    F = st.session_state.varying_bio_budget_params["F"]
    K_f = st.session_state.varying_bio_budget_params["K_f"]
    beta_f = st.session_state.varying_bio_budget_params["beta_f"]
    results = st.session_state.varying_bio_budget_results
    bio_budgets = []
    bio_productions = []
    for bio_budget, result in results.items():
        bio_budgets.append(bio_budget)
        established_f = result["established_facilities"]
        bio_production = sum(K_f[f] * beta_f[f] for f in range(F) if established_f[f])
        bio_productions.append(bio_production)
    df = pd.DataFrame({
        "Budsjett": bio_budgets,
        "Biobudsjett": bio_budgets,
        "Etablert bioproduksjon": bio_productions,
    })
    df_melted = df.melt(id_vars=["Biobudsjett"],
                        value_vars=["Budsjett", "Etablert bioproduksjon"],
                        var_name="Parameter",
                        value_name="Produksjonskapasitet"
    )
    chart = alt.Chart(df_melted).mark_line(
        point=True
    ).encode(
        x=alt.X(
            "Biobudsjett:O",
            title="Biobudsjett [m³/dag]",
            axis=alt.Axis(labelAngle=0, grid=True)
        ),
        y=alt.Y(
            "Produksjonskapasitet:Q",
            title="Produksjonskapasitet [m³/dag]",
            axis=alt.Axis(labelBaseline="middle")
        ),
        color=alt.Color(
            "Parameter:N",
            title="Parameter",
            legend=alt.Legend(orient="bottom")
        ),
        tooltip=["Biobudsjett", "Parameter", "Produksjonskapasitet"]
    )
    st.altair_chart(chart)