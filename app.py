from __future__ import annotations

import html
import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

from real_estate.services import ListingInput, PropertyInput, RealEstateService
from real_estate.web_search import search_properties
from scraping.runner import run_scraper


ROOT = Path(__file__).resolve().parent
AGENT_DIR = ROOT / "AI-Agent"
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))


ICONS = {
    "logo": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 21V8l9-6 9 6v13h-7v-7h-4v7H3Zm3-3h1v-6h10v6h1V9.7l-6-4-6 4V18Z"/></svg>',
    "building": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 21V3h11v6h5v12H4Zm3-3h2v-2H7v2Zm0-5h2v-2H7v2Zm0-5h2V6H7v2Zm5 10h2v-2h-2v2Zm0-5h2v-2h-2v2Zm0-5h2V6h-2v2Zm5 10h1v-6h-1v6Z"/></svg>',
    "chart": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19h16v2H2V3h2v16Zm3-2V9h3v8H7Zm5 0V5h3v12h-3Zm5 0v-6h3v6h-3Z"/></svg>',
    "scale": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M11 4H5V2h14v2h-6v3.1l4 2 4-2V9l-3 6h-2l-3-6-1 .5-1-.5-3 6H6L3 9V7.1l4 2 4-2V4Zm-6.4 7L7 13.8 9.4 11H4.6ZM14.6 11l2.4 2.8 2.4-2.8h-4.8ZM11 20v-7h2v7h4v2H7v-2h4Z"/></svg>',
    "search": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m20.7 19.3-4.2-4.2a7 7 0 1 0-1.4 1.4l4.2 4.2 1.4-1.4ZM5 11a6 6 0 1 1 12 0 6 6 0 0 1-12 0Z"/></svg>',
    "chat": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 3h16a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H9l-5 4v-4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Zm2 5v2h12V8H6Zm0 4v2h8v-2H6Z"/></svg>',
    "database": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2C6.5 2 3 3.8 3 6v12c0 2.2 3.5 4 9 4s9-1.8 9-4V6c0-2.2-3.5-4-9-4Zm0 3c3.7 0 5.7.8 6 1-.3.2-2.3 1-6 1s-5.7-.8-6-1c.3-.2 2.3-1 6-1Zm0 14c-3.9 0-6-1-6-1v-2.7c1.5.7 3.5 1.1 6 1.1s4.5-.4 6-1.1V18s-2.1 1-6 1Zm0-5.6c-3.9 0-6-1-6-1V9.7c1.5.7 3.5 1.1 6 1.1s4.5-.4 6-1.1v2.7s-2.1 1-6 1Z"/></svg>',
    "pulse": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 13h4l2-7 4 13 2-6h6v-2h-4.5L13 2 9 15 7.5 11H3v2Z"/></svg>',
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
        :root {
          --navy:#101b2d; --navy-soft:#18263d; --accent:#0f8a72;
          --accent-dark:#0b6b59; --accent-soft:#e8f5f1; --canvas:#f4f7f9;
          --surface:#ffffff; --ink:#172033; --muted:#667085; --line:#e3e8ef;
          --shadow:0 12px 35px rgba(16,27,45,.08);
        }
        html, body, [class*="css"] { font-family:Inter,ui-sans-serif,system-ui,-apple-system,sans-serif; }
        .stApp { background:var(--canvas); color:var(--ink); }
        [data-testid="stHeader"] { background:transparent; }
        [data-testid="stToolbar"] { right:1.25rem; }
        .block-container { max-width:1380px; padding:1.2rem 2rem 4rem; }
        .app-bar { display:flex; align-items:center; justify-content:space-between;
                   padding:10px 4px 24px; }
        .brand { display:flex; align-items:center; gap:12px; }
        .brand-mark { display:grid; place-items:center; width:42px; height:42px;
                      border-radius:12px; color:white; background:var(--navy); }
        .brand-mark .svg-icon { color:white; width:22px; height:22px; }
        .brand-name { font-weight:750; letter-spacing:-.02em; color:var(--navy); }
        .brand-subtitle { color:var(--muted); font-size:.78rem; margin-top:1px; }
        .status-pill { display:flex; align-items:center; gap:8px; padding:8px 12px;
                       border:1px solid #cce8df; border-radius:999px;
                       background:#f3fbf8; color:#166b59; font-size:.8rem; font-weight:650; }
        .status-dot { width:7px; height:7px; border-radius:50%; background:#18a77f;
                      box-shadow:0 0 0 4px rgba(24,167,127,.12); }
        .hero { position:relative; overflow:hidden; display:grid;
                grid-template-columns:minmax(0,1.5fr) minmax(280px,.7fr); gap:28px;
                background:linear-gradient(130deg,#101b2d 0%,#172b42 58%,#0f6c61 130%);
                color:white; padding:38px 40px; border-radius:24px; margin-bottom:22px;
                box-shadow:0 24px 50px rgba(16,27,45,.18); }
        .hero:after { content:""; position:absolute; width:360px; height:360px;
                      right:-150px; top:-210px; border:1px solid rgba(255,255,255,.12);
                      border-radius:50%; box-shadow:0 0 0 55px rgba(255,255,255,.025),
                      0 0 0 110px rgba(255,255,255,.02); }
        .hero-copy, .hero-panel { position:relative; z-index:1; }
        .eyebrow { color:#8de1cc; font-size:.75rem; font-weight:750;
                   text-transform:uppercase; letter-spacing:.13em; }
        .hero h1 { margin:10px 0 12px; font-size:clamp(2rem,4vw,3.25rem);
                   letter-spacing:-.045em; line-height:1.05; max-width:760px; }
        .hero p { margin:0; color:#ced8e5; max-width:700px; line-height:1.65; }
        .hero-panel { align-self:center; display:grid; grid-template-columns:1fr 1fr;
                      gap:10px; }
        .hero-stat { padding:15px; border:1px solid rgba(255,255,255,.13);
                     border-radius:14px; background:rgba(255,255,255,.07);
                     backdrop-filter:blur(12px); }
        .hero-stat strong { display:block; font-size:1.15rem; }
        .hero-stat span { display:block; color:#b8c6d6; font-size:.72rem; margin-top:4px; }
        .page-intro { display:flex; align-items:flex-start; justify-content:space-between;
                      gap:20px; margin:8px 0 20px; }
        .section-title { display:flex; align-items:center; gap:12px; margin:0; }
        .section-title h2 { margin:0; font-size:1.42rem; letter-spacing:-.025em; color:var(--navy); }
        .section-description { color:var(--muted); margin:6px 0 0 38px; font-size:.9rem; }
        .svg-icon { display:inline-flex; width:24px; height:24px; color:var(--accent); }
        .svg-icon svg { width:100%; height:100%; fill:currentColor; }
        .result-card { background:var(--surface); border:1px solid var(--line);
                       border-radius:16px; padding:20px 22px; margin:12px 0;
                       box-shadow:0 5px 18px rgba(16,27,45,.04);
                       transition:transform .18s ease,box-shadow .18s ease; }
        .result-card:hover { transform:translateY(-2px); box-shadow:var(--shadow); }
        .result-card h3 { color:var(--navy); margin:9px 0; letter-spacing:-.015em; }
        .result-card a { color:var(--accent-dark); font-weight:700; text-decoration:none; }
        .rank { color:var(--accent-dark); font-size:.77rem; font-weight:750;
                letter-spacing:.04em; text-transform:uppercase; }
        .small { color:var(--muted); font-size:.85rem; line-height:1.55; }
        div[data-testid="stMetric"] { background:var(--surface); border:1px solid var(--line);
                                     border-radius:16px; padding:17px 18px;
                                     box-shadow:0 5px 18px rgba(16,27,45,.04); }
        div[data-testid="stMetricLabel"] { color:var(--muted); }
        div[data-testid="stMetricValue"] { color:var(--navy); letter-spacing:-.035em; }
        div[data-testid="stForm"], div[data-testid="stExpander"] {
          background:var(--surface); border:1px solid var(--line); border-radius:18px;
          padding:8px 12px; box-shadow:0 5px 18px rgba(16,27,45,.035);
        }
        div[data-baseweb="input"] > div, div[data-baseweb="select"] > div,
        div[data-testid="stNumberInputContainer"] {
          border-color:#d7dee7 !important; border-radius:10px !important;
          background:#fbfcfd !important;
        }
        .stButton > button, .stFormSubmitButton > button {
          min-height:42px; border-radius:10px; border:0; padding:0 18px;
          background:var(--accent); color:white; font-weight:700;
          box-shadow:0 6px 16px rgba(15,138,114,.2);
        }
        .stButton > button:hover, .stFormSubmitButton > button:hover {
          background:var(--accent-dark); color:white; border:0;
        }
        .stTabs [data-baseweb="tab-list"] { gap:5px; padding:6px; border:1px solid var(--line);
                                           background:white; border-radius:14px;
                                           box-shadow:0 5px 18px rgba(16,27,45,.035); }
        .stTabs [data-baseweb="tab"] { height:42px; border-radius:9px; padding:0 16px;
                                      color:var(--muted); font-weight:650; }
        .stTabs [aria-selected="true"] { color:var(--navy) !important;
                                         background:var(--accent-soft) !important; }
        .stTabs [data-baseweb="tab-highlight"] { display:none; }
        [data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:14px;
                                     overflow:hidden; background:white; }
        [data-testid="stAlert"] { border-radius:12px; }
        [data-testid="stChatMessage"] { background:white; border:1px solid var(--line);
                                       border-radius:14px; padding:8px 14px; margin:10px 0; }
        [data-testid="stChatInput"] { border-color:var(--line); }
        hr { border-color:var(--line); }
        @media (max-width:850px) {
          .block-container { padding:1rem 1rem 3rem; }
          .hero { grid-template-columns:1fr; padding:28px 24px; border-radius:18px; }
          .hero-panel { grid-template-columns:repeat(4,1fr); }
          .app-bar { align-items:flex-start; }
          .status-pill { display:none; }
          .stTabs [data-baseweb="tab-list"] { overflow-x:auto; }
        }
        @media (max-width:560px) {
          .hero-panel { grid-template-columns:1fr 1fr; }
          .hero h1 { font-size:2rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_heading(icon_name: str, title: str, description: str) -> None:
    st.markdown(
        f"""
        <div class="page-intro">
          <div>
            <div class="section-title">{icon(icon_name)}<h2>{html.escape(title)}</h2></div>
            <p class="section-description">{html.escape(description)}</p>
          </div>
        </div>
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
    page_heading("building", "Estimation de prix", "Estimez un bien avec le modele et les annonces comparables.")
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
    page_heading("search", "Recommandations", "Trouvez les annonces les plus adaptees a vos criteres.")
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
                  <div class="rank">Rang {item['rank']} &middot; Score {item['recommendation_score']}/100</div>
                  <h3>{title}</h3>
                  <p>{money(item['price_mad'])} &middot; {item['surface_m2']:.0f} m2 &middot;
                     {item['bedrooms']:.0f} chambres &middot; {money(item['price_per_m2'])}/m2</p>
                  <p class="small">{html.escape(item['neighborhood'])}, {html.escape(item['city'])}
                     &middot; Source {html.escape(item['source'])}</p>
                  <a href="{link}" target="_blank">Consulter l'annonce</a>
                </div>
                """,
                unsafe_allow_html=True,
            )


def comparison_page(service: RealEstateService, cities: list[str]) -> None:
    page_heading("scale", "Comparateur de biens", "Comparez valeur, budget, completude et localisation.")
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
            width="stretch",
            hide_index=True,
        )
        for item in ranked:
            st.markdown(
                f"""
                <div class="result-card">
                  <div class="rank">Rang {item['rank']} &middot; Score {item['score']}/100</div>
                  <h3>{html.escape(item['name'])}</h3>
                  <p>{html.escape(item['explanation'])}</p>
                  <p class="small">Prix annonce {money(item['advertised_price_mad'])} &middot;
                     Estimation {money(item['estimated_price_mad'])} &middot;
                     Ecart {item['difference_percent']}%</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def market_page(service: RealEstateService, cities: list[str]) -> None:
    page_heading("chart", "Marche observe", "Explorez les prix et surfaces presents dans les donnees.")
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
    page_heading("pulse", "Performance du modele", "Consultez les metriques mesurees et les limites actuelles.")
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
            st.dataframe(frame, hide_index=True, width="stretch")
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
        st.dataframe(comparison, hide_index=True, width="stretch")

    st.subheader("Erreurs par tranche de prix")
    bands = report.get("error_by_price_band", [])
    if bands:
        st.dataframe(pd.DataFrame(bands), hide_index=True, width="stretch")
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
    page_heading("search", "Recherche en ligne", "Recherchez des annonces recentes et verifiez leurs sources.")
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
                  <div class="rank">{html.escape(item['source'])} &middot; {verification}</div>
                  <h3>{html.escape(item['title'])}</h3>
                  <p>{price} &middot; {html.escape(item['location'] or city)}</p>
                  <p class="small">{html.escape(item['snippet'][:280])}</p>
                  <a href="{html.escape(item['url'])}" target="_blank">Ouvrir la source</a>
                  <p class="small">Consulte le {html.escape(item['checked_at'])}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def collection_page() -> None:
    page_heading(
        "database",
        "Collecte des donnees",
        "Lancez les collecteurs approuves et suivez leur execution depuis l'interface.",
    )
    st.info(
        "La collecte remplace les fichiers stables de la source choisie. "
        "Les exports restent locaux et ignores par Git."
    )
    with st.form("scraper_form"):
        c1, c2 = st.columns(2)
        source_label = c1.selectbox("Source", ["Mubawab", "Sarouty"])
        transaction_label = c2.selectbox("Transaction", ["Vente", "Location"])
        c3, c4 = st.columns(2)
        min_listings = c3.number_input(
            "Nombre minimum d'annonces", min_value=1, max_value=1_000, value=150
        )
        max_pages = c4.number_input(
            "Nombre maximal de pages Mubawab", min_value=1, max_value=100, value=20
        )
        submitted = st.form_submit_button("Lancer la collecte")

    if submitted:
        source = source_label.lower()
        transaction = "rent" if transaction_label == "Location" else "sale"
        with st.spinner(
            f"Collecte {source_label} en cours. Cette operation peut durer plusieurs minutes."
        ):
            try:
                result = run_scraper(
                    source=source,
                    transaction=transaction,
                    min_listings=int(min_listings),
                    max_pages=int(max_pages),
                )
            except Exception as error:
                st.error(f"Execution impossible : {error}")
                return

        if result["success"]:
            st.success(f"Collecte {source_label} terminee avec succes.")
            c1, c2, c3 = st.columns(3)
            c1.metric("Source", source_label)
            c2.metric("Transaction", transaction_label)
            c3.metric("Code de sortie", result["return_code"])
            st.code(result["csv_path"], language=None)
        else:
            st.error(
                f"La collecte a echoue avec le code {result['return_code']}."
            )
        with st.expander("Journal d'execution", expanded=not result["success"]):
            st.code(result["stdout"] or "Aucune sortie standard.", language=None)
            if result["stderr"]:
                st.code(result["stderr"], language=None)


def chat_page() -> None:
    page_heading("chat", "Assistant Mistral", "Interrogez les donnees avec les outils immobiliers de l'agent.")
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
    st.set_page_config(
        page_title="Immo Maroc Intelligence",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_css()
    service = get_service()
    cities = sorted(service.data["city"].dropna().unique().tolist())
    report_path = ROOT / "reports" / "model_metrics.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
    best_model = str(report.get("best_model", "Non entraine")).replace("_", " ").title()
    dataset_rows = int(report.get("dataset_rows", len(service.data)))
    source_count = int(service.data["source"].nunique())
    st.markdown(
        f"""
        <div class="app-bar">
          <div class="brand">
            <div class="brand-mark">{icon("logo")}</div>
            <div>
              <div class="brand-name">Immo Maroc Intelligence</div>
              <div class="brand-subtitle">Decision immobiliere assistee par les donnees</div>
            </div>
          </div>
          <div class="status-pill"><span class="status-dot"></span>Services operationnels</div>
        </div>
        <div class="hero">
          <div class="hero-copy">
            <div class="eyebrow">Plateforme immobiliere intelligente</div>
            <h1>Comprendre le marche. Evaluer avec methode.</h1>
            <p>Estimation, comparaison, recherche et analyse du marche marocain,
               reunies dans une experience claire, fiable et professionnelle.</p>
          </div>
          <div class="hero-panel">
            <div class="hero-stat"><strong>{dataset_rows}</strong><span>Annonces ML</span></div>
            <div class="hero-stat"><strong>{len(cities)}</strong><span>Villes observees</span></div>
            <div class="hero-stat"><strong>{source_count}</strong><span>Sources locales</span></div>
            <div class="hero-stat"><strong>{html.escape(best_model)}</strong><span>Meilleur modele</span></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    tabs = st.tabs(
        [
            "Estimation",
            "Recommandations",
            "Comparateur",
            "Marche",
            "Modele ML",
            "Collecte",
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
        collection_page()
    with tabs[6]:
        live_search_page(cities)
    with tabs[7]:
        chat_page()


if __name__ == "__main__":
    main()
