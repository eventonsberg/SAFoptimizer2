import streamlit as st
import pandas as pd
import altair as alt

def plot_remaining_production_capacity_vs_cost_variation():
    results = st.session_state.varying_protection_cost_results
    cost_variations = []
    remaining_capacities = []
    for cost_variation, result in results.items():
        cost_variations.append(cost_variation)
        remaining_capacities.append(result['remaining_production_capacity_after_attack'])
    df = pd.DataFrame({
        "Kostnad": cost_variations,
        "Produksjonskapasitet": remaining_capacities
    })
    chart = alt.Chart(df).mark_line(
        point=True
    ).encode(
        x=alt.X(
            "Kostnad:O",
            title="Kostnad beskyttelsestiltak [andel av opprinnelig kostnad]",
            axis=alt.Axis(labelAngle=0, grid=True, labelExpr="datum.label + ' %'")
        ),
        y=alt.Y(
            "Produksjonskapasitet:Q",
            title="Produksjonskapasitet [m³/dag]",
            axis=alt.Axis(labelBaseline="middle")
        ),
        tooltip=["Kostnad", "Produksjonskapasitet"],
    )
    st.altair_chart(chart)

def plot_facility_configuration_vs_cost_variation():
    F = st.session_state.varying_protection_cost_params["F"]
    type_f = st.session_state.varying_protection_cost_params["type_f"]
    B = st.session_state.varying_protection_cost_params["B"]
    type_b = st.session_state.varying_protection_cost_params["type_b"]
    results = st.session_state.varying_protection_cost_results
    data = []
    for cost_variation, result in results.items():
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
                    "Kostnad": cost_variation,
                    "Fabrikktype": facility,
                    "FabrikkID": f"{facility} #{facility_counters[facility]}",
                    "Antall etablert": 1,
                    "Beskyttelsestiltak": protection_measure_string,
                    "Ødelagt": destroyed_f[f]
                })
        if not any(established_f):
            data.append({ # Avoid empty dataframe if no facilities are established
                "Kostnad": cost_variation,
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
            "Kostnad:O",
            title="Kostnad beskyttelsestiltak [andel av opprinnelig kostnad]",
            axis=alt.Axis(labelAngle=0, grid=True, bandPosition=1.125, labelExpr="datum.label + ' %'")
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
        tooltip=["Kostnad", "FabrikkID", "Beskyttelsestiltak", "Ødelagt"],
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
                groupby=["Kostnad", "Fabrikktype"],
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
                x=alt.X("Kostnad:O"),
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
                tooltip=["Kostnad", "FabrikkID", "Beskyttelsestiltak", "Ødelagt"]
            )
        )
        chart = bar + point
    st.altair_chart(chart)