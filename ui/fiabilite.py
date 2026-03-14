"""
Onglet Fiabilité — Module d'analyse industrielle de la fiabilité des équipements
Calcul MTBF, taux de défaillance, courbes R(t), statistiques descriptives

Structure :
    render()
        └── render_filtres_globaux()      ← filtres uniques en haut (session_state)
        └── st.tabs([ MTBF | Tendances | Statistiques ])
                ├── render_tab_mtbf()
                ├── render_tab_tendances()
                └── render_tab_stats()
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, date
from data.data_manager import charger_equipements, charger_suivi
import io


# =============================================================================
# CONSTANTES
# =============================================================================

VARIABLES_DISPONIBLES = {
    "vitesse_rpm":        "Vitesse (RPM)",
    "twf_rms_g":          "TWF RMS (g)",
    "crest_factor":       "Crest Factor",
    "twf_peak_to_peak_g": "TWF Peak-to-Peak (g)",
}


# =============================================================================
# UTILITAIRES — CALCULS DE FIABILITÉ
# =============================================================================

def calculer_duree_jours(debut: date, fin: date) -> float:
    """Retourne la durée en jours entre deux dates."""
    return max((fin - debut).days, 0)


def calculer_fiabilite(intervalles: list) -> dict:
    """
    Calcule les indicateurs de fiabilité à partir d'une liste d'intervalles.

    Args:
        intervalles: liste de {"debut": date, "fin": date}

    Returns:
        dict avec MTBF, lambda, nombre_pannes, temps_total_h, temps_total_j
    """
    if not intervalles:
        return None

    durees_jours = [calculer_duree_jours(iv["debut"], iv["fin"]) for iv in intervalles]
    temps_total_jours = sum(durees_jours)
    nombre_pannes = max(len(intervalles) - 1, 0)

    if nombre_pannes == 0 or temps_total_jours == 0:
        return {
            "temps_total_jours":  temps_total_jours,
            "temps_total_heures": temps_total_jours * 24,
            "nombre_pannes":      nombre_pannes,
            "mtbf_jours":         None,
            "mtbf_heures":        None,
            "lambda":             None,
            "durees_jours":       durees_jours,
            "erreur": "Pas assez de pannes pour calculer le MTBF (minimum 2 intervalles requis)"
        }

    mtbf_jours  = temps_total_jours / nombre_pannes
    mtbf_heures = mtbf_jours * 24
    lam         = 1.0 / mtbf_heures

    return {
        "temps_total_jours":  temps_total_jours,
        "temps_total_heures": temps_total_jours * 24,
        "nombre_pannes":      nombre_pannes,
        "mtbf_jours":         mtbf_jours,
        "mtbf_heures":        mtbf_heures,
        "lambda":             lam,
        "durees_jours":       durees_jours,
        "erreur":             None
    }


def fiabilite_rt(lam: float, t_heures: float) -> float:
    """R(t) = exp(-λ * t)"""
    return np.exp(-lam * t_heures)


def couleur_fiabilite(r: float) -> str:
    """Indicateur couleur selon le niveau de fiabilité."""
    if r >= 0.80:
        return "🟢"
    elif r >= 0.50:
        return "🟡"
    return "🔴"


# =============================================================================
# FILTRES GLOBAUX
# Affichés une seule fois sous le titre.
# Résultats stockés dans st.session_state pour partage entre les 3 onglets.
# =============================================================================

def render_filtres_globaux(df_equipements: pd.DataFrame, df_suivi: pd.DataFrame):
    """
    Affiche les 4 filtres en cascade et stocke dans session_state :
        fiab_departement, fiab_equipement, fiab_point_mesure,
        fiab_parametre, fiab_df_filtered, fiab_param_label, fiab_selection_ok
    """
    with st.container(border=True):
        st.markdown("#### 🔍 Sélection de l'équipement et du paramètre")
        col1, col2, col3, col4 = st.columns(4)

        # ── 1. Département ────────────────────────────────────────────────────
        with col1:
            departements = sorted(df_equipements["departement"].dropna().unique())
            dept_idx = 0
            if st.session_state.get("fiab_departement") in departements:
                dept_idx = departements.index(st.session_state["fiab_departement"])
            dept = st.selectbox("1️⃣ Département", departements,
                                index=dept_idx, key="fiab_departement")

        # ── 2. ID Équipement ──────────────────────────────────────────────────
        equips_dept   = df_equipements[df_equipements["departement"] == dept]["id_equipement"].tolist()
        equips_valides = sorted([e for e in equips_dept if e in df_suivi["id_equipement"].unique()])

        with col2:
            if not equips_valides:
                st.selectbox("2️⃣ ID Équipement", ["— aucun —"], key="fiab_equipement")
                st.session_state["fiab_selection_ok"] = False
                return
            eq_idx = 0
            if st.session_state.get("fiab_equipement") in equips_valides:
                eq_idx = equips_valides.index(st.session_state["fiab_equipement"])
            id_equip = st.selectbox("2️⃣ ID Équipement", equips_valides,
                                    index=eq_idx, key="fiab_equipement")

        # ── 3. Point de mesure ────────────────────────────────────────────────
        df_equip = df_suivi[df_suivi["id_equipement"] == id_equip]
        points   = sorted(df_equip["point_mesure"].dropna().unique())

        with col3:
            if not points:
                st.selectbox("3️⃣ Point de mesure", ["— aucun —"], key="fiab_point_mesure")
                st.session_state["fiab_selection_ok"] = False
                return
            pm_idx = 0
            if st.session_state.get("fiab_point_mesure") in points:
                pm_idx = points.index(st.session_state["fiab_point_mesure"])
            point_mesure = st.selectbox("3️⃣ Point de mesure", points,
                                        index=pm_idx, key="fiab_point_mesure")

        # ── 4. Paramètre ──────────────────────────────────────────────────────
        with col4:
            param_keys = list(VARIABLES_DISPONIBLES.keys())
            p_idx = 0
            if st.session_state.get("fiab_parametre") in param_keys:
                p_idx = param_keys.index(st.session_state["fiab_parametre"])
            parametre = st.selectbox(
                "4️⃣ Paramètre",
                options=param_keys,
                format_func=lambda k: VARIABLES_DISPONIBLES[k],
                index=p_idx,
                key="fiab_parametre"
            )

    # ── Construction du DataFrame filtré ─────────────────────────────────────
    df_filtered = df_equip[df_equip["point_mesure"] == point_mesure].copy()
    df_filtered["date"] = pd.to_datetime(df_filtered["date"], errors="coerce")
    df_filtered = df_filtered.sort_values("date")

    # Stockage partagé
    st.session_state["fiab_df_filtered"] = df_filtered
    st.session_state["fiab_param_label"] = VARIABLES_DISPONIBLES[parametre]
    st.session_state["fiab_selection_ok"] = not df_filtered.empty

    if df_filtered.empty:
        st.warning("⚠️ Aucune donnée pour cette sélection.")


# =============================================================================
# SECTION — INTERVALLES DE FONCTIONNEMENT
# =============================================================================

def _get_date_min_equipement(df_suivi: pd.DataFrame, id_equip: str) -> date:
    """
    Retourne la date de la première mesure disponible pour l'équipement
    sélectionné dans suivi_equipements.
    Utilisée comme borne minimale pour la saisie des intervalles.

    Args:
        df_suivi  : DataFrame complet de suivi_equipements (déjà chargé)
        id_equip  : ID de l'équipement sélectionné via les filtres globaux

    Returns:
        date minimale trouvée, ou date(2000, 1, 1) par sécurité si aucune donnée
    """
    df_equip = df_suivi[df_suivi["id_equipement"] == id_equip]
    if df_equip.empty:
        return date(2000, 1, 1)
    dates = pd.to_datetime(df_equip["date"], errors="coerce").dropna()
    if dates.empty:
        return date(2000, 1, 1)
    return dates.min().date()


def render_intervalles(date_min: date) -> list:
    """
    Gère l'ajout, l'affichage et la suppression des intervalles.
    Clé session_state unique : 'fiab_intervalles'.

    Args:
        date_min : date minimale autorisée pour les saisies (= première mesure
                   de l'équipement sélectionné, calculée dynamiquement).
    """
    key_list    = "fiab_intervalles"
    key_equip   = "fiab_iv_equip_courant"

    if key_list not in st.session_state:
        st.session_state[key_list] = []

    # ── Réinitialiser les intervalles si l'équipement a changé ───────────────
    equip_courant = st.session_state.get("fiab_equipement", "")
    if st.session_state.get(key_equip) != equip_courant:
        st.session_state[key_list]   = []
        st.session_state[key_equip]  = equip_courant

    intervalles = st.session_state[key_list]

    # ── Affichage de la date minimale pour information ────────────────────────
    st.caption(
        f"📅 Première mesure disponible pour cet équipement : "
        f"**{date_min.strftime('%d/%m/%Y')}** — les dates ne peuvent pas être antérieures."
    )

    st.markdown("#### ➕ Ajouter un intervalle de bon fonctionnement")

    col_d1, col_d2, col_add = st.columns([2, 2, 1])

    # Valeur par défaut intelligente : date_min pour le début, aujourd'hui pour la fin
    default_debut = date_min
    default_fin   = date.today()

    with col_d1:
        debut_new = st.date_input(
            "Date début",
            value=default_debut,
            min_value=date_min,          # ← date min DYNAMIQUE
            max_value=date.today(),
            key="fiab_iv_debut_new"
        )
    with col_d2:
        fin_new = st.date_input(
            "Date fin",
            value=default_fin,
            min_value=date_min,          # ← date min DYNAMIQUE
            max_value=date.today(),
            key="fiab_iv_fin_new"
        )
    with col_add:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Ajouter", key="fiab_iv_btn_add",
                     use_container_width=True, type="primary"):
            # ── Validations ───────────────────────────────────────────────────
            if debut_new < date_min:
                st.error(
                    f"❌ La date de début ({debut_new.strftime('%d/%m/%Y')}) "
                    f"est antérieure à la première mesure de l'équipement "
                    f"({date_min.strftime('%d/%m/%Y')})."
                )
            elif fin_new <= debut_new:
                st.error("❌ La date de fin doit être postérieure à la date de début.")
            elif fin_new < date_min:
                st.error(
                    f"❌ La date de fin ({fin_new.strftime('%d/%m/%Y')}) "
                    f"est antérieure à la première mesure de l'équipement."
                )
            else:
                chevauchement = any(
                    not (fin_new <= iv["debut"] or debut_new >= iv["fin"])
                    for iv in intervalles
                )
                if chevauchement:
                    st.warning("⚠️ Cet intervalle chevauche un intervalle existant.")
                else:
                    intervalles.append({"debut": debut_new, "fin": fin_new})
                    intervalles.sort(key=lambda x: x["debut"])
                    st.session_state[key_list] = intervalles
                    st.rerun()

    # ── Tableau des intervalles ───────────────────────────────────────────────
    if intervalles:
        st.markdown("#### 📋 Liste des intervalles")
        rows = []
        for i, iv in enumerate(intervalles):
            duree = calculer_duree_jours(iv["debut"], iv["fin"])
            rows.append({
                "#":               i + 1,
                "Date début":      iv["debut"].strftime("%d/%m/%Y"),
                "Date fin":        iv["fin"].strftime("%d/%m/%Y"),
                "Durée (jours)":   duree,
                "Durée (mois)":    round(duree / 30.44, 1),
                "Durée (années)":  round(duree / 365.25, 2),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        col_sup, col_clear = st.columns([3, 1])
        with col_sup:
            idx_sup = st.selectbox(
                "Supprimer l'intervalle n°",
                options=list(range(1, len(intervalles) + 1)),
                key="fiab_iv_idx_sup"
            )
            if st.button("🗑️ Supprimer cet intervalle", key="fiab_iv_btn_sup"):
                intervalles.pop(idx_sup - 1)
                st.session_state[key_list] = intervalles
                st.rerun()
        with col_clear:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 Tout effacer", key="fiab_iv_btn_clear",
                         type="secondary", use_container_width=True):
                st.session_state[key_list] = []
                st.rerun()
    else:
        st.info("ℹ️ Aucun intervalle ajouté. Ajoutez au moins 2 intervalles pour calculer le MTBF.")

    return intervalles


# =============================================================================
# SECTION — KPI CARDS
# =============================================================================

def render_kpi_cards(resultats: dict, t_heures: float):
    """Affiche les 6 KPI dans des cartes HTML stylisées."""
    mtbf_h  = resultats.get("mtbf_heures")
    mtbf_j  = resultats.get("mtbf_jours")
    lam     = resultats.get("lambda")
    n_pan   = resultats.get("nombre_pannes", 0)
    t_tot_j = resultats.get("temps_total_jours", 0)
    r_t     = fiabilite_rt(lam, t_heures) if lam else None

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    def card(col, titre, valeur, unite, icone, couleur="#1f77b4"):
        with col:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg,{couleur}15 0%,{couleur}08 100%);
                border: 1.5px solid {couleur}40;
                border-radius: 12px;
                padding: 16px 12px;
                text-align: center;
                min-height: 110px;
            ">
                <div style="font-size:1.6rem;margin-bottom:4px;">{icone}</div>
                <div style="font-size:0.72rem;color:#888;font-weight:600;
                    text-transform:uppercase;letter-spacing:0.05em;">{titre}</div>
                <div style="font-size:1.4rem;font-weight:800;color:{couleur};
                    margin:4px 0;">{valeur}</div>
                <div style="font-size:0.72rem;color:#aaa;">{unite}</div>
            </div>""", unsafe_allow_html=True)

    mc = ("#2ecc71" if mtbf_j and mtbf_j >= 365
          else ("#f39c12" if mtbf_j and mtbf_j >= 90 else "#e74c3c"))
    rc = ("#2ecc71" if r_t and r_t >= 0.80
          else ("#f39c12" if r_t and r_t >= 0.50 else "#e74c3c"))

    card(col1, "MTBF",      f"{mtbf_j:.1f}" if mtbf_j else "—", "jours",          "⚙️", mc)
    card(col2, "MTBF",      f"{mtbf_h:.0f}" if mtbf_h else "—", "heures",          "🕐", mc)
    card(col3, "Taux λ",    f"{lam:.2e}"    if lam    else "—", "pannes/heure",    "📉", "#9b59b6")
    card(col4, f"R({t_heures:.0f}h)",
         f"{r_t*100:.1f}%" if r_t is not None else "—",
         f"t={t_heures:.0f}h", "🎯", rc)
    card(col5, "Pannes",    str(n_pan),                          "défaillances",   "⚠️", "#e74c3c")
    card(col6, "Temps total", f"{t_tot_j:.0f}",                 "jours de fonct.", "📅", "#3498db")


# =============================================================================
# SECTION — COURBE R(t)
# =============================================================================

def render_courbe_fiabilite(lam: float, mtbf_h: float):
    """Courbe R(t) = exp(-λt). Key unique : fiab_fig_rt"""
    t_max  = mtbf_h * 3
    t_vals = np.linspace(0, t_max, 500)
    r_vals = np.exp(-lam * t_vals)

    fig = go.Figure()
    fig.add_hrect(y0=0.80, y1=1.0,  fillcolor="rgba(46,204,113,0.1)",  line_width=0,
                  annotation_text="Bon (>80%)",     annotation_position="right")
    fig.add_hrect(y0=0.50, y1=0.80, fillcolor="rgba(243,156,18,0.1)",  line_width=0,
                  annotation_text="Attention",      annotation_position="right")
    fig.add_hrect(y0=0,    y1=0.50, fillcolor="rgba(231,76,60,0.1)",   line_width=0,
                  annotation_text="Critique (<50%)", annotation_position="right")
    fig.add_trace(go.Scatter(
        x=t_vals, y=r_vals, mode="lines", name="R(t) = e^(−λt)",
        line=dict(color="#2980b9", width=3),
        fill="tozeroy", fillcolor="rgba(41,128,185,0.1)"
    ))
    fig.add_vline(x=mtbf_h, line_dash="dash", line_color="#e74c3c",
                  annotation_text=f"MTBF = {mtbf_h:.0f}h (R≈36.8%)",
                  annotation_position="top right")
    fig.add_hline(y=np.exp(-1), line_dash="dot", line_color="#e74c3c", line_width=1)
    fig.update_layout(
        title="📈 Courbe de fiabilité R(t) — Loi exponentielle",
        xaxis_title="Temps t (heures)",
        yaxis_title="Fiabilité R(t)",
        yaxis=dict(range=[0, 1.05], tickformat=".0%"),
        hovermode="x unified", height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True, key="fiab_fig_rt")


# =============================================================================
# SECTION — GRAPHIQUES ANALYSE
# tab_prefix garantit des keys uniques par onglet : "tend" ou "stat"
# =============================================================================

def render_graphiques_analyse(df: pd.DataFrame, parametre: str, param_label: str,
                               id_equip: str, point_mesure: str,
                               val_min: float = None, val_max: float = None,
                               tab_prefix: str = "tab"):
    """
    Graphiques Plotly : évolution temporelle, histogramme, boxplot, KDE.
    tab_prefix garantit que chaque st.plotly_chart a un key unique dans la page.
    """
    serie_raw = df[parametre].dropna()
    df_plot   = df[["date", parametre]].dropna().sort_values("date")

    if val_min is not None and val_max is not None:
        df_plot = df_plot[(df_plot[parametre] >= val_min) & (df_plot[parametre] <= val_max)]
        serie   = df_plot[parametre]
    else:
        serie = serie_raw

    if df_plot.empty or serie.empty:
        st.warning("⚠️ Aucune donnée après application du filtre.")
        return

    # ── Fig 1 : Évolution temporelle + tendance + moyenne mobile ─────────────
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df_plot["date"], y=df_plot[parametre],
        mode="lines+markers", name=param_label,
        line=dict(color="#2980b9", width=2), marker=dict(size=5)
    ))
    if len(df_plot) >= 3:
        x_num  = (df_plot["date"] - df_plot["date"].min()).dt.days.values
        coeffs = np.polyfit(x_num, df_plot[parametre].values, 1)
        fig1.add_trace(go.Scatter(
            x=df_plot["date"], y=np.polyval(coeffs, x_num),
            mode="lines", name="Tendance linéaire",
            line=dict(color="#e74c3c", width=2, dash="dash")
        ))
    if len(df_plot) >= 5:
        fig1.add_trace(go.Scatter(
            x=df_plot["date"],
            y=df_plot[parametre].rolling(5, center=True).mean(),
            mode="lines", name="Moyenne mobile (5 pts)",
            line=dict(color="#2ecc71", width=2, dash="dot")
        ))
    fig1.update_layout(
        title=f"📊 Évolution temporelle — {id_equip} | {point_mesure} | {param_label}",
        xaxis_title="Date", yaxis_title=param_label,
        hovermode="x unified", height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig1, use_container_width=True,
                    key=f"fiab_{tab_prefix}_fig_evolution")

    # ── Fig 2 + Fig 3 : Histogramme & Boxplot ────────────────────────────────
    col_g2, col_g3 = st.columns(2)

    with col_g2:
        fig2 = go.Figure()
        fig2.add_trace(go.Histogram(
            x=serie, nbinsx=30,
            marker_color="#3498db",
            marker_line=dict(color="#2980b9", width=1),
            opacity=0.85, name=param_label
        ))
        fig2.add_vline(x=serie.mean(), line_dash="dash", line_color="#e74c3c",
                       annotation_text=f"Moy = {serie.mean():.3f}",
                       annotation_position="top right")
        fig2.add_vline(x=serie.median(), line_dash="dot", line_color="#f39c12",
                       annotation_text=f"Méd = {serie.median():.3f}",
                       annotation_position="top left")
        fig2.update_layout(
            title="📊 Distribution des valeurs",
            xaxis_title=param_label, yaxis_title="Fréquence",
            height=380, showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True,
                        key=f"fiab_{tab_prefix}_fig_histo")

    with col_g3:
        fig3 = go.Figure()
        fig3.add_trace(go.Box(
            y=serie, boxpoints="outliers",
            marker_color="#9b59b6", line_color="#8e44ad",
            name=param_label, fillcolor="rgba(155,89,182,0.2)"
        ))
        fig3.update_layout(
            title="📦 Boîte à moustaches",
            yaxis_title=param_label, height=380, showlegend=False
        )
        st.plotly_chart(fig3, use_container_width=True,
                        key=f"fiab_{tab_prefix}_fig_box")

    # ── Fig 4 : Densité KDE (optionnel — scipy requis) ────────────────────────
    try:
        from scipy.stats import gaussian_kde  # type: ignore
        kde   = gaussian_kde(serie)
        x_kde = np.linspace(serie.min(), serie.max(), 300)
        fig4  = go.Figure()
        fig4.add_trace(go.Scatter(
            x=x_kde, y=kde(x_kde),
            fill="tozeroy", fillcolor="rgba(46,204,113,0.2)",
            line=dict(color="#2ecc71", width=2.5), name="Densité KDE"
        ))
        fig4.add_vline(x=serie.mean(), line_dash="dash", line_color="#e74c3c",
                       annotation_text="Moyenne", annotation_position="top right")
        fig4.update_layout(
            title="📈 Densité de probabilité (KDE)",
            xaxis_title=param_label, yaxis_title="Densité", height=360
        )
        st.plotly_chart(fig4, use_container_width=True,
                        key=f"fiab_{tab_prefix}_fig_kde")
    except Exception:
        pass  # scipy absent ou données insuffisantes → graphique ignoré silencieusement


# =============================================================================
# SECTION — STATISTIQUES DESCRIPTIVES
# =============================================================================

def render_statistiques(df: pd.DataFrame, parametre: str, param_label: str):
    """Tableau de statistiques descriptives du paramètre."""
    serie = df[parametre].dropna()
    if serie.empty:
        st.warning("⚠️ Aucune donnée disponible pour ce paramètre.")
        return

    rms_val = np.sqrt(np.mean(serie ** 2))
    stats   = {
        "Moyenne":           serie.mean(),
        "Médiane":           serie.median(),
        "Min":               serie.min(),
        "Max":               serie.max(),
        "Écart-type (σ)":    serie.std(),
        "Variance (σ²)":     serie.var(),
        "RMS":               rms_val,
        "P10":               serie.quantile(0.10),
        "P25 (Q1)":          serie.quantile(0.25),
        "P75 (Q3)":          serie.quantile(0.75),
        "P90":               serie.quantile(0.90),
        "Plage (max−min)":   serie.max() - serie.min(),
        "Nombre de mesures": len(serie),
    }
    df_stats = pd.DataFrame([
        {"Indicateur": k,
         "Valeur": f"{v:.4f}" if isinstance(v, float) else str(v)}
        for k, v in stats.items()
    ])
    st.dataframe(df_stats, use_container_width=True, hide_index=True)


# =============================================================================
# SECTION — EXPORTS CSV / EXCEL
# =============================================================================

def render_exports(df: pd.DataFrame, parametre: str, param_label: str,
                   resultats: dict, intervalles: list,
                   id_equip: str, point_mesure: str):
    """Boutons d'export CSV et Excel."""
    st.markdown("#### 📤 Exports")
    col_csv, col_xlsx = st.columns(2)

    # ── CSV ───────────────────────────────────────────────────────────────────
    with col_csv:
        df_exp = df[["date", "id_equipement", "point_mesure", parametre]].copy()
        df_exp["date"] = pd.to_datetime(df_exp["date"]).dt.strftime("%d/%m/%Y")
        st.download_button(
            label="📥 Export CSV (données)",
            data=df_exp.to_csv(index=False, sep=";").encode("utf-8-sig"),
            file_name=f"fiabilite_{id_equip}_{parametre}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # ── Excel ─────────────────────────────────────────────────────────────────
    with col_xlsx:
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            from openpyxl.utils import get_column_letter

            buf    = io.BytesIO()
            wb     = openpyxl.Workbook()
            hfill  = PatternFill("solid", fgColor="1A5276")
            hfont  = Font(bold=True, color="FFFFFF", size=11)
            bfont  = Font(bold=True, size=11)
            border = Border(
                left=Side(style="thin"),  right=Side(style="thin"),
                top=Side(style="thin"),   bottom=Side(style="thin")
            )

            # Feuille 1 : Résumé
            ws = wb.active
            ws.title = "Résumé Fiabilité"
            ws.cell(row=1, column=1,
                    value=f"Rapport de Fiabilité — {id_equip} | {point_mesure} | {param_label}"
                    ).font = Font(bold=True, size=14, color="1A5276")
            ws.cell(row=2, column=1,
                    value=f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            ws.merge_cells("A1:D1")
            for i, (lbl, val) in enumerate([
                ("Équipement",   id_equip),
                ("Point de mesure", point_mesure),
                ("Paramètre",    param_label),
                ("Temps total fonctionnement (jours)",
                 round(resultats.get("temps_total_jours", 0), 1)),
                ("Temps total fonctionnement (heures)",
                 round(resultats.get("temps_total_heures", 0), 0)),
                ("Nombre de défaillances",
                 resultats.get("nombre_pannes", "—")),
                ("MTBF (jours)",
                 round(resultats["mtbf_jours"], 2) if resultats.get("mtbf_jours") else "—"),
                ("MTBF (heures)",
                 round(resultats["mtbf_heures"], 1) if resultats.get("mtbf_heures") else "—"),
                ("Taux λ (pannes/h)",
                 f"{resultats['lambda']:.4e}" if resultats.get("lambda") else "—"),
            ], start=4):
                c1 = ws.cell(row=i, column=1, value=lbl)
                c2 = ws.cell(row=i, column=2, value=val)
                c1.font = bfont;  c1.border = border
                c2.border = border
            ws.column_dimensions["A"].width = 38
            ws.column_dimensions["B"].width = 22

            # Feuille 2 : Intervalles
            ws2 = wb.create_sheet("Intervalles")
            for j, h in enumerate(["N°", "Date début", "Date fin",
                                    "Durée (jours)", "Durée (mois)", "Durée (années)"], 1):
                c = ws2.cell(row=1, column=j, value=h)
                c.fill = hfill; c.font = hfont
                c.alignment = Alignment(horizontal="center"); c.border = border
            for i, iv in enumerate(intervalles, 2):
                d = calculer_duree_jours(iv["debut"], iv["fin"])
                for j, val in enumerate(
                    [i-1, iv["debut"].strftime("%d/%m/%Y"), iv["fin"].strftime("%d/%m/%Y"),
                     d, round(d/30.44, 1), round(d/365.25, 2)], 1
                ):
                    c = ws2.cell(row=i, column=j, value=val)
                    c.border = border; c.alignment = Alignment(horizontal="center")
            for j in range(1, 7):
                ws2.column_dimensions[get_column_letter(j)].width = 16

            # Feuille 3 : Données brutes
            ws3   = wb.create_sheet("Données")
            cols3 = ["date", "id_equipement", "point_mesure", parametre]
            for j, h in enumerate(cols3, 1):
                c = ws3.cell(row=1, column=j, value=h)
                c.fill = hfill; c.font = hfont; c.border = border
            for i, (_, row) in enumerate(df[cols3].iterrows(), 2):
                ws3.cell(row=i, column=1,
                         value=pd.to_datetime(row["date"]).strftime("%d/%m/%Y")).border = border
                ws3.cell(row=i, column=2, value=row["id_equipement"]).border = border
                ws3.cell(row=i, column=3, value=row["point_mesure"]).border = border
                ws3.cell(row=i, column=4,
                         value=float(row[parametre]) if pd.notna(row[parametre]) else None
                         ).border = border
            for j in range(1, 5):
                ws3.column_dimensions[get_column_letter(j)].width = 20

            wb.save(buf); buf.seek(0)
            st.download_button(
                label="📥 Export Excel (rapport)",
                data=buf,
                file_name=f"rapport_fiabilite_{id_equip}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except ImportError:
            st.warning("⚠️ openpyxl non disponible — export Excel désactivé.")


# =============================================================================
# ONGLET 1 — CALCUL MTBF & FIABILITÉ
# =============================================================================

def render_tab_mtbf():
    """
    Onglet MTBF & Fiabilité.
    Lit les données depuis session_state (filtres globaux).

    Nouveautés :
      - date_min dynamique : calculée à partir de MIN(date) dans suivi_equipements
        pour l'équipement sélectionné → passée à render_intervalles()
      - choix d'unité pour R(t) : heures ou jours (1 jour = 24 heures)
    """
    if not st.session_state.get("fiab_selection_ok", False):
        st.info("ℹ️ Sélectionnez un équipement et un paramètre dans les filtres ci-dessus.")
        return

    df_filtered  = st.session_state["fiab_df_filtered"]
    id_equip     = st.session_state["fiab_equipement"]
    point_mesure = st.session_state["fiab_point_mesure"]
    parametre    = st.session_state["fiab_parametre"]
    param_label  = st.session_state["fiab_param_label"]

    # ── Date min dynamique : première mesure de l'équipement ─────────────────
    # On récupère le df_suivi complet depuis session_state (déjà chargé dans render())
    df_suivi_global = st.session_state.get("fiab_df_suivi_global", pd.DataFrame())
    date_min = _get_date_min_equipement(df_suivi_global, id_equip)

    # ── Intervalles ───────────────────────────────────────────────────────────
    with st.container(border=True):
        st.subheader("📅 Intervalles de bon fonctionnement")
        st.caption(
            "Ajoutez chaque période pendant laquelle l'équipement a fonctionné "
            "correctement. Nombre de pannes = nombre d'intervalles − 1."
        )
        intervalles = render_intervalles(date_min=date_min)

    # ── Calcul MTBF ───────────────────────────────────────────────────────────
    resultats = calculer_fiabilite(intervalles) if intervalles else None

    if resultats and resultats.get("erreur"):
        st.warning(f"⚠️ {resultats['erreur']}")

    # ── Saisie t pour R(t) + choix d'unité ───────────────────────────────────
    with st.container(border=True):
        st.subheader("🎯 Calcul de la fiabilité R(t)")

        col_t, col_unite, col_info = st.columns([1, 1, 2])

        with col_unite:
            unite_t = st.selectbox(
                "Unité du temps",
                options=["heures", "jours"],
                index=0,
                key="fiab_rt_unite",
                help="Choisissez l'unité dans laquelle vous saisissez t. "
                     "Si « jours » est sélectionné, la conversion t × 24 est "
                     "appliquée automatiquement avant le calcul."
            )

        # Paramètres d'affichage selon l'unité choisie
        if unite_t == "heures":
            label_t    = "Temps t (heures)"
            val_defaut = 720.0      # 30 jours en heures
            step_t     = 24.0
            max_t      = 100_000.0
        else:
            label_t    = "Temps t (jours)"
            val_defaut = 30.0
            step_t     = 1.0
            max_t      = 4_000.0   # ≈ 11 ans en jours

        with col_t:
            t_saisi = st.number_input(
                label_t,
                min_value=1.0,
                max_value=max_t,
                value=val_defaut,
                step=step_t,
                key="fiab_t_saisi",
                help=(
                    "Durée pour laquelle on calcule R(t). "
                    "Les calculs internes sont toujours en heures "
                    "(λ en pannes/heure)."
                )
            )

        # Conversion en heures pour tous les calculs (λ est en pannes/heure)
        if unite_t == "jours":
            t_heures = t_saisi * 24.0
            label_t_display = f"{t_saisi:.0f} jours ({t_heures:.0f}h)"
        else:
            t_heures        = t_saisi
            label_t_display = f"{t_heures:.0f}h"

        if resultats and not resultats.get("erreur") and resultats.get("lambda"):
            r_t       = fiabilite_rt(resultats["lambda"], t_heures)
            indicateur = couleur_fiabilite(r_t)
            with col_info:
                st.markdown(f"""
                <div style="background:#f8f9fa;border-radius:10px;
                            padding:16px;margin-top:8px;">
                    <span style="font-size:1.05rem;">
                        {indicateur}&nbsp;
                        Pour <b>t = {label_t_display}</b>, la probabilité que
                        l'équipement fonctionne sans défaillance est :
                    </span><br>
                    <span style="font-size:2rem;font-weight:800;color:#2980b9;">
                        R(t) = {r_t * 100:.2f}%
                    </span><br>
                    <span style="font-size:0.8rem;color:#888;">
                        λ = {resultats['lambda']:.4e} pannes/h —
                        calcul : exp(−{resultats['lambda']:.4e} × {t_heures:.1f})
                    </span>
                </div>
                """, unsafe_allow_html=True)

    # ── Dashboard KPI + récapitulatif + courbe R(t) ───────────────────────────
    if resultats and not resultats.get("erreur"):
        with st.container(border=True):
            st.subheader("📊 Tableau de bord — Indicateurs de fiabilité")
            render_kpi_cards(resultats, t_heures)
            st.markdown("---")

            col_tab, col_courbe = st.columns([1, 2])
            with col_tab:
                st.markdown("##### 📋 Récapitulatif")
                lam = resultats["lambda"]
                recap = {
                    "Indicateur": [
                        "Temps total de fonctionnement",
                        "Temps total (heures)",
                        "Nombre de défaillances",
                        "MTBF",
                        "MTBF (heures)",
                        "Taux de défaillance λ",
                        f"t saisi",
                        f"t converti (heures)",
                        f"Fiabilité R(t)",
                    ],
                    "Valeur": [
                        f"{resultats['temps_total_jours']:.1f} jours",
                        f"{resultats['temps_total_heures']:.0f} h",
                        f"{resultats['nombre_pannes']} panne(s)",
                        f"{resultats['mtbf_jours']:.1f} jours" if resultats.get("mtbf_jours") else "—",
                        f"{resultats['mtbf_heures']:.1f} h"    if resultats.get("mtbf_heures") else "—",
                        f"{lam:.4e} pannes/h"                  if lam else "—",
                        f"{t_saisi:.1f} {unite_t}",
                        f"{t_heures:.1f} h",
                        f"{fiabilite_rt(lam, t_heures)*100:.2f}%" if lam else "—",
                    ]
                }
                st.dataframe(pd.DataFrame(recap), use_container_width=True, hide_index=True)

            with col_courbe:
                if resultats.get("lambda") and resultats.get("mtbf_heures"):
                    render_courbe_fiabilite(resultats["lambda"], resultats["mtbf_heures"])

        # ── Exports ───────────────────────────────────────────────────────────
        with st.container(border=True):
            render_exports(df_filtered, parametre, param_label,
                           resultats, intervalles, id_equip, point_mesure)


# =============================================================================
# ONGLET 2 — VISUALISATION DES TENDANCES
# =============================================================================

def render_tab_tendances():
    """Lit session_state (filtres globaux) — aucun filtre dupliqué."""
    if not st.session_state.get("fiab_selection_ok", False):
        st.info("ℹ️ Sélectionnez un équipement et un paramètre dans les filtres ci-dessus.")
        return

    df_base      = st.session_state["fiab_df_filtered"].copy()
    id_equip     = st.session_state["fiab_equipement"]
    point_mesure = st.session_state["fiab_point_mesure"]
    parametre    = st.session_state["fiab_parametre"]
    param_label  = st.session_state["fiab_param_label"]

    # Options d'affichage
    with st.container(border=True):
        st.subheader("⚙️ Options d'affichage")
        col_o1, col_o2, col_o3 = st.columns(3)

        with col_o1:
            mode = st.radio(
                "Mode de filtrage",
                ["Période personnalisée", "N dernières observations"],
                horizontal=True, key="fiab_tend_mode"
            )

        df_plot = df_base.copy()

        if mode == "Période personnalisée":
            with col_o2:
                d1 = st.date_input(
                    "Date début",
                    value=df_base["date"].min().date(),
                    min_value=df_base["date"].min().date(),
                    max_value=df_base["date"].max().date(),
                    key="fiab_tend_d1"
                )
            with col_o3:
                d2 = st.date_input(
                    "Date fin",
                    value=df_base["date"].max().date(),
                    min_value=df_base["date"].min().date(),
                    max_value=df_base["date"].max().date(),
                    key="fiab_tend_d2"
                )
            df_plot = df_plot[
                (df_plot["date"].dt.date >= d1) &
                (df_plot["date"].dt.date <= d2)
            ]
        else:
            with col_o2:
                n_obs = st.number_input(
                    "N dernières observations",
                    min_value=5, max_value=500, value=22, step=1,
                    key="fiab_tend_n"
                )
            df_plot = df_plot.tail(int(n_obs))

        st.markdown("---")
        activer_filtre = st.toggle(
            "🔎 Filtrer les valeurs (plage personnalisée)",
            value=False, key="fiab_tend_filtre_val"
        )
        val_min = val_max = None
        if activer_filtre and not df_plot.empty:
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                val_min = st.number_input(
                    "Valeur minimum",
                    value=float(df_plot[parametre].min()),
                    key="fiab_tend_vmin"
                )
            with col_v2:
                val_max = st.number_input(
                    "Valeur maximum",
                    value=float(df_plot[parametre].max()),
                    key="fiab_tend_vmax"
                )

    if df_plot.empty:
        st.warning("⚠️ Aucune donnée pour cette période.")
        return

    with st.container(border=True):
        st.subheader(f"📈 Tendances — {id_equip} | {point_mesure} | {param_label}")
        render_graphiques_analyse(
            df_plot, parametre, param_label, id_equip, point_mesure,
            val_min=val_min, val_max=val_max,
            tab_prefix="tend"   # keys uniques : fiab_tend_fig_*
        )


# =============================================================================
# ONGLET 3 — STATISTIQUES DESCRIPTIVES
# =============================================================================

def render_tab_stats():
    """Lit session_state (filtres globaux) — aucun filtre dupliqué."""
    if not st.session_state.get("fiab_selection_ok", False):
        st.info("ℹ️ Sélectionnez un équipement et un paramètre dans les filtres ci-dessus.")
        return

    df_base      = st.session_state["fiab_df_filtered"].copy()
    id_equip     = st.session_state["fiab_equipement"]
    point_mesure = st.session_state["fiab_point_mesure"]
    parametre    = st.session_state["fiab_parametre"]
    param_label  = st.session_state["fiab_param_label"]

    # Filtre temporel
    with st.container(border=True):
        st.subheader("⚙️ Filtre temporel")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            ds1 = st.date_input(
                "Date début",
                value=df_base["date"].min().date(),
                key="fiab_stat_d1"
            )
        with col_s2:
            ds2 = st.date_input(
                "Date fin",
                value=df_base["date"].max().date(),
                key="fiab_stat_d2"
            )

    df_stat = df_base[
        (df_base["date"].dt.date >= ds1) &
        (df_base["date"].dt.date <= ds2)
    ]

    if df_stat.empty:
        st.warning("⚠️ Aucune donnée pour cette période.")
        return

    with st.container(border=True):
        st.subheader(f"📋 Statistiques descriptives — {param_label}")
        render_statistiques(df_stat, parametre, param_label)

    with st.container(border=True):
        st.subheader("📊 Visualisations statistiques")
        activer_filtre = st.toggle(
            "🔎 Filtrer les valeurs",
            value=False, key="fiab_stat_filtre"
        )
        val_min_s = val_max_s = None
        if activer_filtre:
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                val_min_s = st.number_input(
                    "Valeur min",
                    value=float(df_stat[parametre].min()),
                    key="fiab_stat_vmin"
                )
            with col_v2:
                val_max_s = st.number_input(
                    "Valeur max",
                    value=float(df_stat[parametre].max()),
                    key="fiab_stat_vmax"
                )
        render_graphiques_analyse(
            df_stat, parametre, param_label, id_equip, point_mesure,
            val_min=val_min_s, val_max=val_max_s,
            tab_prefix="stat"   # keys uniques : fiab_stat_fig_*
        )


# =============================================================================
# POINT D'ENTRÉE PRINCIPAL
# =============================================================================

def render():
    """
    Structure finale :

        Titre  : 🔧 Analyse de Fiabilité
        ┌──────────────────────────────────┐
        │  Filtres globaux (session_state) │
        │  Dept | Équip | Point | Param    │
        └──────────────────────────────────┘
        ┌──────────────────────────────────────────────────────┐
        │  [ ⚙️ Calcul MTBF | 📈 Tendances | 📊 Statistiques ] │
        └──────────────────────────────────────────────────────┘
    """
    st.header("🔧 Analyse de Fiabilité")
    st.caption("Calcul du MTBF, taux de défaillance, courbes R(t) et statistiques industrielles")

    df_equipements = charger_equipements()
    df_suivi       = charger_suivi()

    if df_equipements.empty or df_suivi.empty:
        st.error("⚠️ Données insuffisantes. Vérifiez la connexion à la base de données.")
        return

    # Stocker df_suivi complet en session_state pour que render_tab_mtbf()
    # puisse calculer la date min dynamique sans re-charger depuis Supabase.
    st.session_state["fiab_df_suivi_global"] = df_suivi

    # Filtres globaux — une seule fois — résultats dans session_state
    render_filtres_globaux(df_equipements, df_suivi)

    st.markdown("---")

    # Onglets — lisent session_state, ne répètent pas les filtres
    tab_mtbf, tab_tend, tab_stats = st.tabs([
        "⚙️ Calcul MTBF & Fiabilité",
        "📈 Visualisation des tendances",
        "📊 Statistiques descriptives",
    ])

    with tab_mtbf:
        render_tab_mtbf()

    with tab_tend:
        render_tab_tendances()

    with tab_stats:
        render_tab_stats()