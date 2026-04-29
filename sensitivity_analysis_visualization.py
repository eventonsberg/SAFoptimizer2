import streamlit as st
import pandas as pd
import altair as alt

def plot_sensitivity_analysis():
    base_production = st.session_state.sensitivity_analysis_base_production
    results = st.session_state.sensitivity_analysis_results
    results_list = []
    for (param, variation, param_value), production in results.items():
        results_list.append({
            "Parameter": param,
            "Parametervariasjon": f"{variation}% økning" if variation > 0 else f"{-variation}% reduksjon",
            "Parameterverdi": param_value,
            "Produksjonskapasitet": production,
            "Endring i produksjonskapasitet": production - base_production
        })
    df = pd.DataFrame(results_list)
    max_variation = df["Endring i produksjonskapasitet"].abs().max()
    bar = alt.Chart(df).mark_bar(opacity=0.7).encode(
        x=alt.X("Endring i produksjonskapasitet:Q",
                title="Endring i produksjonskapasitet [m³/dag]",
                scale=alt.Scale(domain=[-max_variation, max_variation]),
                axis=alt.Axis(labelAlign="center"),
                stack=None
        ),
        y=alt.Y("Parameter:N",
                title="Parameter",
                axis=alt.Axis(labelLimit=300, labelBaseline="middle")
        ),
        color=alt.Color("Parametervariasjon:O",
                        title="Parametervariasjon",
                        scale=alt.Scale(scheme="category10"),
                        legend=alt.Legend(orient="bottom")
        ),
        tooltip=["Parameter", "Parametervariasjon", "Parameterverdi", "Produksjonskapasitet", "Endring i produksjonskapasitet"]
    ).properties(
        title=f"Utgangspunkt for produksjonskapasitet: {base_production} m³/dag"
    )
    line = alt.Chart(pd.DataFrame({'x': [0]})).mark_rule(
        color='grey',
        strokeWidth=3
    ).encode(
        x=alt.X(
            'x:Q',
            scale=alt.Scale(domain=[-max_variation, max_variation])
        ),
        tooltip=alt.TooltipValue(f"Utgangspunkt: {base_production} m³/dag")
    )
    chart = (bar + line)
    st.altair_chart(chart)
    st.dataframe(df, hide_index=True)