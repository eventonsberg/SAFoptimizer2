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
            title="Produksjonskapasitet [m³/dag]"
        ),
        tooltip=[param_name, "Produksjonskapasitet"],
    )
    st.altair_chart(chart)

def plot_facility_configuration_vs_facility_parameter():
    facility_name = st.session_state.varying_facility_parameter_f_name
    param_name = st.session_state.varying_facility_parameter_p_name
    param_unit = " [m³/dag]" if param_name == "Kapasitet" else " [MNOK]" if param_name == "Kostnad" else ""
    type_f = st.session_state.varying_facility_parameter_params["type_f"]
    results = st.session_state.varying_facility_parameter_results
    data = []
    for param_value, result in results.items():
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
                    f"{param_name}": param_value,
                    "Fabrikktype": t,
                    "FabrikkID": f"{t} #{type_counters[t]}",
                    "Antall etablert": 1,
                    "Luftvern": ad,
                    "Ødelagt": dest
                })
        if not any(established):
            data.append({
                f"{param_name}": param_value,
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
            f"{param_name}:O",
            title=f"{param_name} til {facility_name}{param_unit}",
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
        tooltip=[param_name, "FabrikkID", "Luftvern", "Ødelagt"],
    )
    text = (
        alt.Chart(df).transform_window(
            stack_index='row_number()',
            groupby=[param_name, "Fabrikktype"],
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
            x=alt.X(f"{param_name}:O"),
            xOffset=alt.XOffset("Fabrikktype:N"),
            y=alt.Y(
                "LabelPos:Q"
            ),
            detail="FabrikkID:N",
            text=alt.Text("Luftvern:N"),
            tooltip=[param_name, "FabrikkID", "Luftvern", "Ødelagt"]
        )
    )
    chart = bar + text
    st.altair_chart(chart)

def plot_costs_vs_facility_parameter():
    facility_name = st.session_state.varying_facility_parameter_f_name
    param_name = st.session_state.varying_facility_parameter_p_name
    param_unit = " [m³/dag]" if param_name == "Kapasitet" else " [MNOK]" if param_name == "Kostnad" else ""
    C_A = st.session_state.varying_facility_parameter_params["C_A"]
    B_B = st.session_state.varying_facility_parameter_params["B_B"]
    results = st.session_state.varying_facility_parameter_results
    param_values = []
    facility_costs = []
    air_defense_costs = []
    total_costs = []
    for param_value, result in results.items():
        param_values.append(param_value)
        C_f_this = result.get("C_f")
        facility_cost = sum(C_f_this[f] for f, est in enumerate(result["established_facilities"]) if est) if C_f_this is not None else 0
        facility_costs.append(facility_cost)
        air_defense_cost = sum(C_A * a_f for f, a_f in enumerate(result["air_defense_assignment"]))
        air_defense_costs.append(air_defense_cost)
        total_costs.append(facility_cost + air_defense_cost)
    df = pd.DataFrame({
        f"{param_name} - {facility_name}": param_values,
        "Budsjett": B_B,
        "Fabrikkostnader": facility_costs,
        "Luftvernkostnader": air_defense_costs,
        "Totale kostnader": total_costs
    })
    df_melted = df.melt(id_vars=[f"{param_name} - {facility_name}"],
                        value_vars=["Budsjett", "Fabrikkostnader", "Luftvernkostnader", "Totale kostnader"],
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
            title="Kostnad [MNOK]"
        ),
        color=alt.Color(
            "Kostnadstype:N",
            title="Kostnadstype",
            legend=alt.Legend(orient="bottom")
        ),
        tooltip=[f"{param_name} - {facility_name}", "Kostnadstype", "Kostnad"]
    )
    st.altair_chart(chart)