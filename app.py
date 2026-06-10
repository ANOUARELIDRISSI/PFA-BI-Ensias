from __future__ import annotations

import html
import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

from real_estate.services import ListingInput, PropertyInput, RealEstateService
from real_estate.web_search import search_properties


ROOT = Path(__file__).resolve().parent
AGENT_DIR = ROOT / "AI-Agent"
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))


ICONS = {
    "building": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 21V3h11v6h5v12H4Zm3-3h2v-2H7v2Zm0-5h2v-2H7v2Zm0-5h2V6H7v2Zm5 10h2v-2h-2v2Zm0-5h2v-2h-2v2Zm0-5h2V6h-2v2Zm5 10h1v-6h-1v6Z"/></svg>',
    "chart": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19h16v2H2V3h2v16Zm3-2V9h3v8H7Zm5 0V5h3v12h-3Zm5 0v-6h3v6h-3Z"/></svg>',
    "scale": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M11 4H5V2h14v2h-6v3.1l4 2 4-2V9l-3 6h-2l-3-6-1 .5-1-.5-3 6H6L3 9V7.1l4 2 4-2V4Zm-6.4 7L7 13.8 9.4 11H4.6ZM14.6 11l2.4 2.8 2.4-2.8h-4.8ZM11 20v-7h2v7h4v2H7v-2h4Z"/></svg>',
    "search": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m20.7 19.3-4.2-4.2a7 7 0 1 0-1.4 1.4l4.2 4.2 1.4-1.4ZM5 11a6 6 0 1 1 12 0 6 6 0 0 1-12 0Z"/></svg>',
    "chat": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 3h16a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H9l-5 4v-4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Zm2 5v2h12V8H6Zm0 4v2h8v-2H6Z"/></svg>',
}


def icon(name: str) -> str:
    return f'<span class="svg-icon">{ICONS[name]}</span>'


def money(value: float) -> str:
    return f"{value:,.0f} MAD".replace(",", " ")


def compact_money(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.0f}K"
    return f"{value:.0f}"


@st.cache_resource
def get_service() -> RealEstateService:
    return RealEstateService()


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root { --ink:#14213d; --accent:#1f6f5f; --soft:#eef5f2; --line:#d8e2df; }
        .stApp { background:#f7f9f8; color:var(--ink); }
        .block-container { max-width:1200px; padding-top:2rem; }
        .hero { background:linear-gradient(135deg,#14213d,#1f6f5f); color:white;
                padding:28px 30px; border-radius:18px; margin-bottom:22px; }
        .hero h1 { margin:0 0 8px; font-size:2rem; }
        .hero p { margin:0; opacity:.88; }
        .section-title { display:flex; align-items:center; gap:10px; margin:10px 0 16px; }
        .section-title h2 { margin:0; font-size:1.25rem; }
        .svg-icon { display:inline-flex; width:24px; height:24px; color:#1f6f5f; }
        .svg-icon svg { width:100%; height:100%; fill:currentColor; }
        .metric-card { background:white; border:1px solid var(--line); border-radius:14px;
                       padding:17px; min-height:112px; }
        .metric-label { color:#5c6b66; font-size:.85rem; }
        .metric-value { color:var(--ink); font-size:1.35rem; font-weight:700; margin-top:7px; }
        .result-card { background:white; border:1px solid var(--line); border-radius:14px;
                       padding:18px; margin:10px 0; }
        .rank { color:#1f6f5f; font-weight:700; }
        .small { color:#62716c; font-size:.88rem; }
        div[data-testid="stMetric"] { background:white; border:1px solid var(--line);
                                     border-radius:14px; padding:12px; }
        .stButton > button { border-radius:10px; border:0; background:#1f6f5f; color:white; }
        .stButton > button:hover { background:#18594d; color:white; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def property_fields(prefix: str, cities: list[str]) -> PropertyInput:
    city = st.selectbox("Ville", cities, key=f"{prefix}_city")
    neighborhood = st.text_input("Quartier", "Unknown", key=f"{prefix}_neighborhood")
    c1, c2 = st.columns(2)
    surface = c1.number_input("Surface m2", 20.0, 500.0, 100.0, key=f"{prefix}_surface")
    rooms = c2.number_input("Pieces", 1.0, 15.0, 3.0, key=f"{prefix}_rooms")
    c3, c4 = st.columns(2)
    bedrooms = c3.number_input("Chambres", 0.0, 10.0, 2.0, key=f"{prefix}_bedrooms")
    bathrooms = c4.number_input("Salles de bain", 0.0, 10.0, 2.0, key=f"{prefix}_bathrooms")
    furnished = st.selectbox("Meuble", ["NO", "YES", "UNKNOWN"], key=f"{prefix}_furnished")
    return PropertyInput(surface, rooms, bedrooms, bathrooms, city, neighborhood, furnished)


def estimator_page(service: RealEstateService, cities: list[str]) -> None:
    st.markdown(
        f'<div class="section-title">{icon("building")}<h2>Estimation de prix</h2></div>',
        unsafe_allow_html=True,
    )
    with st.form("estimate_form"):
        item = property_fields("estimate", cities)
        submitted = st.form_submit_button("Calculer l'estimation")
    if submitted:
        result = service.predict_price(item)
        c1, c2, c3 = st.columns(3)
        c1.metric("Prix estime", money(result["estimated_price_mad"]))
        c2.metric("Prix estime au m2", money(result["estimated_price_per_m2"]))
        c3.metric("Biens comparables", result["comparable_count"])
        low, high = result["indicative_range_mad"]
        st.info(f"Fourchette indicative : {money(low)} a {money(high)}")
        st.caption(result["warning"])


def recommendations_page(service: RealEstateService, cities: list[str]) -> None:
    st.markdown(
        f'<div class="section-title">{icon("search")}<h2>Recommandations</h2></div>',
        unsafe_allow_html=True,
    )
    with st.form("recommend_form"):
        c1, c2 = st.columns(2)
        budget = c1.number_input("Budget maximal MAD", 100_000, 20_000_000, 2_000_000, 50_000)
        city = c2.selectbox("Ville", cities, key="recommend_city")
        neighborhood = st.text_input("Quartier prefere, facultatif")
        c3, c4, c5 = st.columns(3)
        surface = c3.number_input("Surface minimale", 0, 500, 70)
        bedrooms = c4.number_input("Chambres minimales", 0, 10, 2)
        limit = c5.number_input("Nombre de resultats", 1, 10, 5)
        submitted = st.form_submit_button("Rechercher dans les donnees")
    if submitted:
        results = service.recommend_properties(
            budget, city, neighborhood or None, surface, bedrooms, limit
        )
        if not results:
            st.warning("Aucune annonce locale ne correspond a ces criteres.")
        for item in results:
            title = html.escape(str(item.get("title") or "Annonce immobiliere"))
            link = html.escape(str(item.get("url") or "#"))
            st.markdown(
                f"""
                <div class="result-card">
                  <div class="rank">Rang {item['rank']} · Score {item['recommendation_score']}/100</div>
                  <h3>{title}</h3>
                  <p>{money(item['price_mad'])} · {item['surface_m2']:.0f} m2 ·
                     {item['bedrooms']:.0f} chambres · {money(item['price_per_m2'])}/m2</p>
                  <p class="small">{html.escape(item['neighborhood'])}, {html.escape(item['city'])}
                     · Source {html.escape(item['source'])}</p>
                  <a href="{link}" target="_blank">Consulter l'annonce</a>
                </div>
                """,
                unsafe_allow_html=True,
            )


def comparison_page(service: RealEstateService, cities: list[str]) -> None:
    st.markdown(
        f'<div class="section-title">{icon("scale")}<h2>Comparateur de biens</h2></div>',
        unsafe_allow_html=True,
    )
    count = st.number_input("Nombre de biens", 2, 5, 2)
    listings = []
    for index in range(int(count)):
        with st.expander(f"Bien {index + 1}", expanded=index < 2):
            name = st.text_input("Nom", f"Bien {index + 1}", key=f"cmp_name_{index}")
            price = st.number_input(
                "Prix annonce MAD", 100_000, 20_000_000, 1_500_000, 50_000,
                key=f"cmp_price_{index}",
            )
            item = property_fields(f"cmp_{index}", cities)
            url = st.text_input("URL facultative", key=f"cmp_url_{index}")
            listings.append(ListingInput(name, price, item, url))
    c1, c2 = st.columns(2)
    budget = c1.number_input("Budget de reference MAD", 0, 20_000_000, 2_000_000, 50_000)
    preferred_city = c2.selectbox("Ville preferee", [""] + cities)
    if st.button("Comparer et classer"):
        ranked = service.compare_properties(
            listings,
            budget_mad=budget or None,
            preferred_city=preferred_city or None,
        )
        frame = pd.DataFrame(ranked)
        st.dataframe(
            frame[
                [
                    "rank", "name", "score", "advertised_price_mad",
                    "estimated_price_mad", "difference_percent", "price_per_m2",
                    "completeness_percent",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )
        for item in ranked:
            st.markdown(
                f"""
                <div class="result-card">
                  <div class="rank">Rang {item['rank']} · Score {item['score']}/100</div>
                  <h3>{html.escape(item['name'])}</h3>
                  <p>{html.escape(item['explanation'])}</p>
                  <p class="small">Prix annonce {money(item['advertised_price_mad'])} ·
                     Estimation {money(item['estimated_price_mad'])} ·
                     Ecart {item['difference_percent']}%</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def market_page(service: RealEstateService, cities: list[str]) -> None:
    st.markdown(
        f'<div class="section-title">{icon("chart")}<h2>Marche observe</h2></div>',
        unsafe_allow_html=True,
    )
    city = st.selectbox("Ville", cities, key="market_city")
    neighborhood = st.text_input("Quartier facultatif", key="market_neighborhood")
    try:
        result = service.market_summary(city, neighborhood or None)
    except ValueError as error:
        st.warning(str(error))
        return
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Annonces", result["listing_count"])
    c2.metric("Prix median", money(result["median_price_mad"]))
    c3.metric("Prix median au m2", money(result["median_price_per_m2"]))
    c4.metric("Surface moyenne", f"{result['mean_surface_m2']} m2")
    local = service.data[service.data["city"].str.casefold() == city.casefold()].copy()
    if neighborhood:
        local = local[
            local["neighborhood"].fillna("").str.casefold() == neighborhood.casefold()
        ]
    st.bar_chart(local.groupby("neighborhood")["price_mad"].median().nlargest(12))


def model_performance_page() -> None:
    st.markdown(
        f'<div class="section-title">{icon("chart")}<h2>Performance du modele</h2></div>',
        unsafe_allow_html=True,
    )
    report_path = ROOT / "reports" / "model_metrics.json"
    if not report_path.exists():
        st.warning("Rapport absent. Lancez `uv run python -m ml.train`.")
        return

    report = json.loads(report_path.read_text(encoding="utf-8"))
    best_name = report["best_model"]
    metrics = report["models"][best_name]
    mape = metrics.get("test_mape")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("R2", f"{metrics['test_r2']:.3f}")
    c2.metric("MAE", f"{compact_money(metrics['test_mae'])} MAD")
    c3.metric("RMSE", f"{compact_money(metrics['test_rmse'])} MAD")
    c4.metric("MAPE", f"{mape:.1f}%" if mape is not None else "A recalculer")
    st.caption(
        f"Modele selectionne : {best_name} | "
        f"{report['dataset_rows']} annonces | jeu de test separe."
    )

    left, right = st.columns(2)
    with left:
        st.subheader("Interpretation de la MAPE")
        if mape is None:
            st.info("Reentrainez le modele pour calculer cette metrique.")
        else:
            examples = [300_000, 800_000, 1_500_000, 5_000_000, 8_000_000]
            frame = pd.DataFrame(
                {
                    "Prix du bien": [money(value) for value in examples],
                    "Erreur moyenne indicative": [
                        f"+/- {money(value * mape / 100)}" for value in examples
                    ],
                }
            )
            st.dataframe(frame, hide_index=True, use_container_width=True)
            st.caption(
                "Cette conversion illustre la MAPE globale; elle ne constitue pas "
                "un intervalle de confiance individuel."
            )
    with right:
        st.subheader("Comparaison des modeles")
        comparison = pd.DataFrame(
            [
                {
                    "Modele": name,
                    "R2": values["test_r2"],
                    "MAE MAD": values["test_mae"],
                    "MAPE %": values.get("test_mape"),
                }
                for name, values in report["models"].items()
            ]
        ).sort_values("MAE MAD")
        st.dataframe(comparison, hide_index=True, use_container_width=True)

    st.subheader("Erreurs par tranche de prix")
    bands = report.get("error_by_price_band", [])
    if bands:
        st.dataframe(pd.DataFrame(bands), hide_index=True, use_container_width=True)
    else:
        st.info("Reentrainez le modele pour produire cette analyse.")

    st.subheader("Donnees a collecter pour progresser")
    st.markdown(
        """
        - Quartier normalise et coordonnees geographiques
        - Etat du bien, etage, ascenseur et parking
        - Annee de construction et qualite des finitions
        - Date de publication et historique des changements de prix

        Les gains de performance doivent etre mesures par validation croisee.
        Ils ne sont pas affiches comme acquis avant une nouvelle evaluation.
        """
    )


def live_search_page(cities: list[str]) -> None:
    st.markdown(
        f'<div class="section-title">{icon("search")}<h2>Recherche en ligne</h2></div>',
        unsafe_allow_html=True,
    )
    with st.form("live_search_form"):
        c1, c2 = st.columns(2)
        city = c1.selectbox("Ville", cities, key="live_city")
        transaction_label = c2.selectbox("Transaction", ["Vente", "Location"])
        c3, c4 = st.columns(2)
        property_type = c3.selectbox(
            "Type de bien", ["appartement", "villa", "maison", "terrain"]
        )
        neighborhood = c4.text_input("Quartier facultatif", key="live_neighborhood")
        max_results = st.slider("Nombre maximal de resultats", 4, 20, 8)
        submitted = st.form_submit_button("Lancer la recherche")
    if submitted:
        with st.spinner("Recherche et verification des annonces en cours"):
            try:
                results = search_properties(
                    city=city,
                    transaction="rent" if transaction_label == "Location" else "sale",
                    property_type=property_type,
                    neighborhood=neighborhood or None,
                    max_results=max_results,
                    verify=True,
                )
            except Exception as error:
                st.error(f"Recherche indisponible : {error}")
                return
        if not results:
            st.warning("Aucun resultat trouve sur les domaines autorises.")
        for item in results:
            verification = "Verifie" if item["verified"] else "Non verifie"
            price = money(item["price_mad"]) if item["price_mad"] else "Prix non detecte"
            st.markdown(
                f"""
                <div class="result-card">
                  <div class="rank">{html.escape(item['source'])} · {verification}</div>
                  <h3>{html.escape(item['title'])}</h3>
                  <p>{price} · {html.escape(item['location'] or city)}</p>
                  <p class="small">{html.escape(item['snippet'][:280])}</p>
                  <a href="{html.escape(item['url'])}" target="_blank">Ouvrir la source</a>
                  <p class="small">Consulte le {html.escape(item['checked_at'])}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def chat_page() -> None:
    st.markdown(
        f'<div class="section-title">{icon("chat")}<h2>Assistant Mistral</h2></div>',
        unsafe_allow_html=True,
    )
    try:
        from agent import RealEstateAgent
        if "agent" not in st.session_state:
            st.session_state.agent = RealEstateAgent()
    except Exception as error:
        st.warning(f"Agent indisponible : {error}")
        return
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    prompt = st.chat_input("Posez une question immobiliere")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            response = st.session_state.agent.chat(prompt)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})


def main() -> None:
    st.set_page_config(page_title="Immo Maroc Intelligence", layout="wide")
    inject_css()
    st.markdown(
        """
        <div class="hero">
          <h1>Immo Maroc Intelligence</h1>
          <p>Estimation, comparaison, recommandations et analyse du marche immobilier marocain.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    service = get_service()
    cities = sorted(service.data["city"].dropna().unique().tolist())
    tabs = st.tabs(
        [
            "Estimation",
            "Recommandations",
            "Comparateur",
            "Marche",
            "Modele ML",
            "Recherche en ligne",
            "Agent IA",
        ]
    )
    with tabs[0]:
        estimator_page(service, cities)
    with tabs[1]:
        recommendations_page(service, cities)
    with tabs[2]:
        comparison_page(service, cities)
    with tabs[3]:
        market_page(service, cities)
    with tabs[4]:
        model_performance_page()
    with tabs[5]:
        live_search_page(cities)
    with tabs[6]:
        chat_page()


if __name__ == "__main__":
    main()
