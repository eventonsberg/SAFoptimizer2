import streamlit as st

def display_model_description():
    expander = st.expander("Vis modellbeskrivelse")
    expander.markdown(
        """
        Dette er en todelt optimeringsmodell som representerer et samspill mellom en angriper og en forsvarer:  
        - :red[**Angriperen**] forsøker å minimere produksjonskapasiteten ved å ødelegge fabrikker med bruk av trusseleffektorer.  
        - :blue[**Forsvareren**] prøver å maksimere produksjonskapasiteten ved å etablere fabrikker
        og implementere beskyttelsestiltak på en måte som minimerer potensiell skade.  
        
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
        \sum_{f \in F} (H_f + N_f) d_f \leq \text{TE}
        """
    )
    expander.markdown(
        """
        | Parameter | Beskrivelse |
        |-----------|--------------|
        | $H_f$ | Hardheten til fabrikk $f$ -- forventet antall treff som kreves for å ødelegge fabrikken |
        | $N_f$ | Forventet antall trusseleffektorer som vil nøytraliseres av beskyttelsestiltak ved fabrikk $f$ |
        | $\\text{TE}$ | Rødt budsjett -- antall trusseleffektorer til disposisjon |
        """
    )
    expander.latex(
        r"""
        N_f = \sum_{b \in B} P_b A_b i_{bf} \quad \forall f \in F
        """
    )
    expander.markdown(
        """
        | Parameter | Beskrivelse |
        |-----------|--------------|
        | $B$ | Potensielle beskyttelsestiltak |
        | $P_b$ | Sannsynligheten for at en effektor i beskyttelsestiltak $b$ slår ut en innkommende trussel |
        | $A_b$ | Antall effektorer i beskyttelsestiltak $b$ |
        | $i_{bf}$ | Boolsk variabel som indikerer om beskyttelsestiltak $b$ er implementert ved fabrikk $f$ |
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
        \max_{a,\, e} K_{\text{tot}}^*
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
        *Et angrepsscenario $s$ er definert som mulig dersom det tilfredsstiller angriperens trusseleffektorbegrensning.*
        """
    )
    expander.markdown(
        """
        Det gir ikke mening å implementere beskyttelsestiltak ved fabrikker som ikke er etablert,
        og kun ett beskyttelsestiltak kan implementeres ved hver fabrikk.
        """
    )
    expander.latex(
        r"""
        \sum_{b \in B} i_{bf} \leq e_f \quad \forall f \in F
        """
    )
    expander.markdown(
        """
        Etablering av fabrikker og implementering av beskyttelsestiltak må gjøres innenfor et gitt budsjett.
        """
    )
    expander.latex(
        r"""
        \sum_{f \in F} \left(C_f e_f + \sum_{b \in B} C_b i_{bf}\right) \leq \text{ØR}
        """
    )
    expander.markdown(
        """
        | Parameter | Beskrivelse |
        |-----------|--------------|
        | $C_f$ | Kostnad for å etablere fabrikk $f$ |
        | $C_b$ | Kostnad for å implementere beskyttelsestiltak $b$ |
        | $\\text{ØR}$ | Blått budsjett -- økonomisk ramme for fabrikker og beskyttelsestiltak |
        """
    )
    expander.subheader("Samspill")
    expander.markdown(
        """
        Det todelte problemet løses ved å kombinere den indre og ytre optimeringsmodellen.
        Forsvarerens beslutninger om etablering av fabrikker ($e_f$)
        og implementering av beskyttelsestiltak ($i_{bf}$)
        påvirker angriperens muligheter til å ødelegge fabrikker ($d_f$).
        Ved å iterere fram og tilbake mellom den indre og ytre modellen,
        leter man seg fram til en fabrikk- og beskyttelsestiltak-konfigurasjon
        som maksimerer den gjenværende produksjonskapasiteten
        etter at angriperen har utført sitt mest skadelige angrep innenfor sine begrensninger.
        """
    )