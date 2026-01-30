import streamlit as st

def display_model_description():
    expander = st.expander("Vis modellbeskrivelse")
    expander.markdown(
        """
        Dette er en *bilevel* optimeringsmodell som løser et interdiksjonsproblem hvor:  
        - En angriper forsøker å minimere produksjonskapasiteten ved å ødelegge fabrikker med bruk av missiler.  
        - En forsvarer prøver å maksimere produksjonskapasiteten ved å sette opp en fabrikkonfigurasjon
        og fordele luftvernmissiler på en måte som minimerer potensiell skade.  
        
        Følgende indre- og ytre optimeringsmodell løses,
        hvor den indre modellen representerer angriperens problem og den ytre modellen representerer forsvarerens problem.
        """
    )
    expander.subheader("Indre optimeringsmodell")
    expander.markdown(
        """
        :red-badge[**Angriperens objektiv:**]  
        Minimer total produksjonskapasitet ved å ødelegge etablerte fabrikker.
        """
    )
    expander.latex(
        r"""
        \min_{d} \sum_{f \in F} K_f e_f (1 - d_f)
        """
    )
    expander.markdown(
        """
        | Parameter | Beskrivelse |
        |-----------|--------------|
        | $F$ | Potensielle fabrikker |
        | $K_f$ | Produksjonskapasiteten til fabrikk $f$ |
        | $e_f$ | Boolsk variabel som indikerer om fabrikk $f$ er etablert |
        | $d_f$ | Boolsk variabel som indikerer om fabrikk $f$ er ødelagt |
        """
    )
    expander.markdown(
        """
        :red-badge[**Angriperens begrensninger:**]  
        Det gir ikke mening å ødelegge fabrikker som ikke er etablert.
    """
    )
    expander.latex(
        r"""
        d_f \leq e_f \quad \forall f \in F
        """
    )
    expander.markdown(
        """ 
        Et begrenset antall missiler kan brukes til å ødelegge fabrikker.
        """
    )
    expander.latex(
        r"""
        \sum_{f \in F} (H_f + P_A a_f) d_f \leq B_R
        """
    )
    expander.markdown(
        """
        | Parameter | Beskrivelse |
        |-----------|--------------|
        | $H_f$ | Antall treff som kreves for å ødelegge fabrikk $f$ |
        | $P_A$ | Sannsynlighet for at et luftvernmissil slår ut et innkommende missil |
        | $a_f$ | Antall luftvernmissiler som beskytter fabrikk $f$ |
        | $B_R$ | Rødt budsjett -- antall missiler angriperen har til disposisjon |
        """
    )
    expander.subheader("Ytre optimeringsmodell")
    expander.markdown(
        """
        :blue-badge[**Forsvarerens objektiv:**]  
        Maksimer total gjenværende produksjonskapasitet etter verste mulige angrep.
        """
    )
    expander.latex(
        r"""
        \max_{e, a} K_{\text{tot}}^*
        """
    )
    expander.markdown(
        """
        | Parameter | Beskrivelse |
        |-----------|--------------|
        | $K_{\\text{tot}}^*$ | Total gjenværende produksjonskapasitet etter verste mulige angrep |
        """
    )
    expander.markdown(
        """
        :blue-badge[**Forsvarerens begrensninger:**]  
        Total gjenværende produksjonskapasitet etter verste mulige angrep er mindre enn eller lik total gjenværende produksjonskapasitet
        i alle mulige angrepsscenarier.
        """
    )
    expander.latex(
        r"""
        K_{\text{tot}}^* \leq \sum_{f \in F} K_f e_f (1 - d_f^s) \quad \forall s \in S
        """
    )
    expander.markdown(
        """
        | Parameter | Beskrivelse |
        |-----------|--------------|
        | $d_f^s$ | Boolsk variabel som indikerer om fabrikk $f$ er ødelagt i angrepsscenario $s$ |
        | $S$ | Potensielle angrepsscenarier |
        """
    )
    expander.caption(
        """
        *Et angrepsscenario $s$ er definert som mulig dersom det tilfredsstiller angriperens missilbudsjettbegrensning.*
        """
    )
    expander.markdown(
        """
        Det gir ikke mening å allokere luftvernmissiler til fabrikker som ikke er etablert.
        """
    )
    expander.latex(
        r"""
        a_f \leq A^{\max} e_f \quad \forall f \in F
        """
    )
    expander.markdown(
        """ 
        | Parameter | Beskrivelse |
        |-----------|--------------|
        | $A^{\\max}$ | Maksimalt antall luftvernmissiler som kan beskytte en fabrikk |
        """
    )
    expander.markdown(
        """
        Etablering av fabrikker og luftvern må gjøres innenfor et gitt budsjett.
        """
    )
    expander.latex(
        r"""
        \sum_{f \in F} (C_f e_f + C_A a_f) \leq B_B
        """
    )
    expander.markdown(
        """
        | Parameter | Beskrivelse |
        |-----------|--------------|
        | $C_f$ | Kostnad for å etablere fabrikk $f$ |
        | $C_A$ | Kostnad per luftvernmissil |
        | $B_B$ | Blått budsjett -- ramme for etablering av fabrikker og luftvern |
        """
    )
    expander.subheader("Interdiksjon")
    expander.markdown(
        """
        Interdiksjonsproblemet løses ved å kombinere den indre og ytre optimeringsmodellen.
        Forsvarerens beslutninger om etablering av fabrikker ($e_f$) og allokering av luftvernmissiler ($a_f$)
        påvirker angriperens muligheter til å ødelegge fabrikker ($d_f$).
        Ved å iterere fram og tilbake mellom den indre og ytre modellen,
        leter man seg fram til en fabrikk- og luftvernkonfigurasjon
        som maksimerer den gjenværende produksjonskapasiteten
        etter at angriperen har utført sitt mest skadelige angrep innenfor sine begrensninger.
        """
    )