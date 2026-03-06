import streamlit as st
import pandas as pd
import altair as alt

def plot_remaining_production_capacity_vs_facility_parameter():
    facility_name = st.session_state.varying_facility_parameter_f_name
    param_name = st.session_state.varying_facility_parameter_p_name
    param_unit = " [m³/dag]" if param_name == "Kapasitet" else " [MNOK]" if param_name == "Kostnad" else ""
    results = st.session_state.varying_facility_parameter_results
    param_values = []
    remaining_capacities = []
    for param_value, result in results.items():
        param_values.append(param_value)
        remaining_capacities.append(result["remaining_production_capacity_after_attack"])
    df = pd.DataFrame({
        param_name: param_values,
        "Produksjonskapasitet": remaining_capacities
    })
    chart = alt.Chart(df).mark_line(
        point=True
    ).encode(
        x=alt.X(
            f"{param_name}:O",
            title=f"{param_name} til {facility_name}{param_unit}",
            axis=alt.Axis(labelAngle=0, grid=True)
        ),
        y=alt.Y(
            "Produksjonskapasitet:Q",
            title="Produksjonskapasitet [m³/dag]",
            axis=alt.Axis(labelBaseline="middle")
        ),
        tooltip=[param_name, "Produksjonskapasitet"],
    )
    st.altair_chart(chart)

def plot_facility_configuration_vs_facility_parameter():
    facility_name = st.session_state.varying_facility_parameter_f_name
    param_name = st.session_state.varying_facility_parameter_p_name
    param_unit = " [m³/dag]" if param_name == "Kapasitet" else " [MNOK]" if param_name == "Kostnad" else ""
    F = st.session_state.varying_facility_parameter_params["F"]
    type_f = st.session_state.varying_facility_parameter_params["type_f"]
    B = st.session_state.varying_facility_parameter_params["B"]
    type_b = st.session_state.varying_facility_parameter_params["type_b"]
    results = st.session_state.varying_facility_parameter_results
    data = []
    for param_value, result in results.items(): 
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
                    f"{param_name}": param_value,
                    "Fabrikktype": facility,
                    "FabrikkID": f"{facility} #{facility_counters[facility]}",
                    "Antall etablert": 1,
                    "Beskyttelsestiltak": protection_measure_string,
                    "Ødelagt": destroyed_f[f]
                })
        if not any(established_f):
            data.append({ # Avoid empty dataframe if no facilities are established
                f"{param_name}": param_value,
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
            f"{param_name}:O",
            title=f"{param_name} til {facility_name}{param_unit}",
            axis=alt.Axis(labelAngle=0)
        ),
        xOffset=alt.XOffset("Fabrikktype:N"),
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
        tooltip=[param_name, "FabrikkID", "Beskyttelsestiltak", "Ødelagt"],
    )
    protection_measures_df = df[df["Beskyttelsestiltak"] != ""]
    if protection_measures_df.empty:
        chart = bar # If no protection measures, just show the bar chart
    else:
        point = ( # Overlay symbols for protection measures on top of the bar chart
            alt.Chart(protection_measures_df).transform_window(
                stack_index='row_number()',
                groupby=[param_name, "Fabrikktype"],
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
                x=alt.X(f"{param_name}:O"),
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
                tooltip=[param_name, "FabrikkID", "Beskyttelsestiltak", "Ødelagt"]
            )
        )
        chart = bar + point
    st.altair_chart(chart)

def plot_costs_vs_facility_parameter():
    facility_name = st.session_state.varying_facility_parameter_f_name
    param_name = st.session_state.varying_facility_parameter_p_name
    param_unit = " [m³/dag]" if param_name == "Kapasitet" else " [MNOK]" if param_name == "Kostnad" else ""
    F = st.session_state.varying_facility_parameter_params["F"]
    B = st.session_state.varying_facility_parameter_params["B"]
    C_b = st.session_state.varying_facility_parameter_params["C_b"]
    OR = st.session_state.varying_facility_parameter_params["OR"]
    results = st.session_state.varying_facility_parameter_results
    param_values = []
    facility_costs = []
    protection_measure_costs = []
    total_costs = []
    for param_value, result in results.items():
        param_values.append(param_value)
        C_f_this = result.get("C_f")
        established_f = result["established_facilities"]
        facility_cost = sum(C_f_this[f] for f in range(F) if established_f[f])
        facility_costs.append(facility_cost)
        implemented_bf = result["implemented_protection_measures"]
        protection_measure_cost = sum(C_b[b] * implemented_bf[b][f] for f in range(F) for b in range(B))
        protection_measure_costs.append(protection_measure_cost)
        total_costs.append(facility_cost + protection_measure_cost)
    df = pd.DataFrame({
        f"{param_name} - {facility_name}": param_values,
        "Totalbudsjett": OR,
        "Kostnad fabrikker": facility_costs,
        "Kostnad beskyttelsestiltak": protection_measure_costs,
        "Totalkostnad": total_costs
    })
    df_melted = df.melt(id_vars=[f"{param_name} - {facility_name}"],
                        value_vars=["Totalbudsjett", "Kostnad fabrikker", "Kostnad beskyttelsestiltak", "Totalkostnad"],
                        var_name="Kostnadstype",
                        value_name="Kostnad"
    )
    chart = alt.Chart(df_melted).mark_line(
        point=True
    ).encode(
        x=alt.X(
            f"{param_name} - {facility_name}:O",
            title=f"{param_name} til {facility_name}{param_unit}",
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
        tooltip=[f"{param_name} - {facility_name}", "Kostnadstype", "Kostnad"]
    )
    st.altair_chart(chart)