"""
Onglet Gestion des Utilisateurs - Accessible uniquement par l'administrateur
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from auth.auth import (
    get_supabase_client,
    get_user_email,
    get_user_name,
    check_permission,
    create_user,
    get_all_users,
    update_user_role,
    deactivate_user,
    reactivate_user,
    delete_user,
    log_action,
    get_audit_logs,
)
from auth.permissions import (
    Permission,
    get_role_label,
    get_role_icon,
    get_all_roles,
    ROLE_METADATA,
    Role,
)


# =============================================================================
# HELPERS
# =============================================================================

def _badge(label: str, color: str) -> str:
    """Retourne un badge HTML coloré."""
    return (
        f"<span style='background:{color}22; color:{color}; border:1px solid {color}55;"
        f"border-radius:12px; padding:2px 10px; font-size:0.8rem; font-weight:600;'>"
        f"{label}</span>"
    )


def _role_badge(role: str) -> str:
    meta = ROLE_METADATA.get(Role(role) if role in [r.value for r in Role] else Role.AUTRE, {})
    color = meta.get("color", "#888")
    icon  = meta.get("icon", "👤")
    label = meta.get("label", role)
    return _badge(f"{icon} {label}", color)


def _statut_badge(actif: bool) -> str:
    if actif:
        return _badge("✅ Actif", "#2ca02c")
    return _badge("🔴 Désactivé", "#d62728")


def _compter_observations(email: str, df_obs: pd.DataFrame) -> int:
    """Compte les observations enregistrées par un utilisateur (via colonne analyste)."""
    if df_obs.empty or 'analyste' not in df_obs.columns:
        return 0
    # On fait une correspondance souple : email ou nom complet dans la colonne analyste
    return int((df_obs['analyste'].astype(str).str.lower() == email.lower()).sum())


def _charger_stats_observations() -> pd.DataFrame:
    """Charge toutes les observations pour les statistiques par analyste."""
    try:
        client = get_supabase_client()
        resp = client.table("observations").select("analyste, date").execute()
        if resp.data:
            return pd.DataFrame(resp.data)
    except Exception:
        pass
    return pd.DataFrame(columns=["analyste", "date"])


def _reset_password_admin(email: str, nouveau_mdp: str) -> tuple:
    """Réinitialise le mot de passe d'un utilisateur via l'API admin Supabase."""
    if not check_permission(Permission.GERER_UTILISATEURS):
        return False, "🔒 Permission refusée"
    try:
        client = get_supabase_client()
        # Récupérer le user_id Supabase Auth via la table users
        res = client.table("users").select("user_id").eq("email", email).single().execute()
        if not res.data:
            return False, "⚠️ Utilisateur introuvable"
        uid = res.data["user_id"]
        client.auth.admin.update_user_by_id(uid, {"password": nouveau_mdp})
        log_action("reset_password_admin", "users", uid, {
            "email": email,
            "reset_by": get_user_email()
        })
        return True, f"✅ Mot de passe réinitialisé pour {email}"
    except Exception as e:
        return False, f"❌ Erreur : {e}"


# =============================================================================
# SECTIONS DE L'INTERFACE
# =============================================================================

def _section_kpis(users: list, df_obs: pd.DataFrame):
    """Affiche les KPIs globaux en haut de page."""
    total       = len(users)
    actifs      = sum(1 for u in users if u.get("actif", True))
    desactives  = total - actifs
    admins      = sum(1 for u in users if u.get("role") == "admin")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Total utilisateurs", total)
    c2.metric("✅ Actifs",             actifs)
    c3.metric("🔴 Désactivés",         desactives)
    c4.metric("🔑 Administrateurs",    admins)


def _section_liste(users: list, df_obs: pd.DataFrame):
    """Tableau principal des utilisateurs avec recherche et filtres."""
    st.subheader("📋 Liste des utilisateurs")

    # ── Filtres ──────────────────────────────────────────────────────────────
    col_search, col_role, col_statut = st.columns([3, 2, 2])

    with col_search:
        recherche = st.text_input(
            "🔍 Rechercher par nom ou email",
            placeholder="Tapez un nom ou email...",
            key="gu_search"
        )

    with col_role:
        roles_dispo = ["Tous"] + get_all_roles()
        filtre_role = st.selectbox("Filtrer par rôle", options=roles_dispo, key="gu_role_filter")

    with col_statut:
        filtre_statut = st.selectbox(
            "Filtrer par statut",
            options=["Tous", "Actifs", "Désactivés"],
            key="gu_statut_filter"
        )

    # ── Application des filtres ───────────────────────────────────────────────
    users_filtres = users[:]

    if recherche:
        q = recherche.lower()
        users_filtres = [
            u for u in users_filtres
            if q in u.get("email", "").lower() or q in u.get("nom_complet", "").lower()
        ]

    if filtre_role != "Tous":
        users_filtres = [u for u in users_filtres if u.get("role") == filtre_role]

    if filtre_statut == "Actifs":
        users_filtres = [u for u in users_filtres if u.get("actif", True)]
    elif filtre_statut == "Désactivés":
        users_filtres = [u for u in users_filtres if not u.get("actif", True)]

    st.caption(f"**{len(users_filtres)}** utilisateur(s) affiché(s) sur {len(users)}")

    if not users_filtres:
        st.info("ℹ️ Aucun utilisateur ne correspond aux critères.")
        return

    # ── Construction du DataFrame d'affichage ────────────────────────────────
    rows = []
    for u in users_filtres:
        email       = u.get("email", "")
        nom         = u.get("nom_complet", "—")
        role        = u.get("role", "autre")
        actif       = u.get("actif", True)
        dept        = u.get("departement", "—") or "—"
        date_crea   = u.get("date_creation", "")
        last_co     = u.get("derniere_connexion", "")
        nb_obs      = _compter_observations(nom, df_obs)

        # Formatage des dates
        try:
            date_crea_fmt = datetime.fromisoformat(date_crea[:19]).strftime("%d/%m/%Y") if date_crea else "—"
        except Exception:
            date_crea_fmt = "—"

        try:
            last_co_fmt = datetime.fromisoformat(last_co[:19]).strftime("%d/%m/%Y %H:%M") if last_co else "Jamais"
        except Exception:
            last_co_fmt = "Jamais"

        rows.append({
            "Nom":               nom,
            "Email":             email,
            "Rôle":              f"{get_role_icon(role)} {get_role_label(role)}",
            "Département":       dept,
            "Statut":            "✅ Actif" if actif else "🔴 Désactivé",
            "Observations":      nb_obs,
            "Dernière connexion": last_co_fmt,
            "Créé le":           date_crea_fmt,
        })

    df_display = pd.DataFrame(rows)

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Nom":               st.column_config.TextColumn("Nom", width="medium"),
            "Email":             st.column_config.TextColumn("Email", width="large"),
            "Rôle":              st.column_config.TextColumn("Rôle", width="medium"),
            "Département":       st.column_config.TextColumn("Département", width="medium"),
            "Statut":            st.column_config.TextColumn("Statut", width="small"),
            "Observations":      st.column_config.NumberColumn("Obs.", width="small"),
            "Dernière connexion": st.column_config.TextColumn("Dernière connexion", width="medium"),
            "Créé le":           st.column_config.TextColumn("Créé le", width="small"),
        }
    )


def _section_ajouter():
    """Formulaire d'ajout d'un nouvel utilisateur."""
    with st.container(border=True):
        st.subheader("➕ Ajouter un utilisateur")
        st.caption("Crée le compte dans Supabase Auth et dans la table users")

        with st.form("form_ajouter_user", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                nom_complet = st.text_input(
                    "Nom complet *",
                    placeholder="Ex: Ahmed Benali",
                    key="gu_add_nom"
                )
                email_new = st.text_input(
                    "Email *",
                    placeholder="Ex: ahmed.benali@entreprise.ma",
                    key="gu_add_email"
                )
                password_new = st.text_input(
                    "Mot de passe *",
                    type="password",
                    placeholder="Minimum 8 caractères",
                    key="gu_add_pwd"
                )

            with col2:
                roles_list = get_all_roles()
                role_labels = [f"{get_role_icon(r)} {get_role_label(r)}" for r in roles_list]
                role_index = st.selectbox(
                    "Rôle *",
                    options=role_labels,
                    index=roles_list.index("technicien") if "technicien" in roles_list else 0,
                    key="gu_add_role"
                )
                role_new = roles_list[role_labels.index(role_index)]

                departement_new = st.text_input(
                    "Département",
                    placeholder="Ex: Maintenance (optionnel)",
                    key="gu_add_dept"
                )

            st.markdown("##")
            col_info, col_btn = st.columns([3, 1])
            with col_info:
                st.caption("📌 Les champs marqués * sont obligatoires")
            with col_btn:
                submitted = st.form_submit_button(
                    "✅ Créer l'utilisateur",
                    type="primary",
                    use_container_width=True
                )

            if submitted:
                if not nom_complet.strip():
                    st.error("⚠️ Le nom complet est requis")
                elif not email_new.strip():
                    st.error("⚠️ L'email est requis")
                elif "@" not in email_new:
                    st.error("⚠️ L'email n'est pas valide")
                elif len(password_new) < 8:
                    st.error("⚠️ Le mot de passe doit contenir au moins 8 caractères")
                else:
                    success, message = create_user(
                        email=email_new.strip(),
                        password=password_new,
                        nom_complet=nom_complet.strip(),
                        departement=departement_new.strip(),
                        role=role_new
                    )
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)


def _section_actions(users: list):
    """Actions sur un utilisateur sélectionné : rôle, désactiver, réactiver, reset mdp, supprimer."""
    with st.container(border=True):
        st.subheader("⚙️ Actions sur un utilisateur")

        current_email = get_user_email()

        # Liste des emails disponibles (on exclut soi-même pour les actions sensibles)
        emails_tous  = [u.get("email", "") for u in users]
        emails_autres = [e for e in emails_tous if e != current_email]

        if not emails_autres:
            st.info("ℹ️ Aucun autre utilisateur dans le système.")
            return

        # Sélection de l'utilisateur cible
        email_cible = st.selectbox(
            "Sélectionner un utilisateur",
            options=emails_autres,
            key="gu_action_email"
        )

        user_cible = next((u for u in users if u.get("email") == email_cible), None)
        if not user_cible:
            return

        actif_cible = user_cible.get("actif", True)
        role_cible  = user_cible.get("role", "autre")
        nom_cible   = user_cible.get("nom_complet", email_cible)

        # Infos rapides sur la cible
        st.markdown(
            f"**{nom_cible}** &nbsp;|&nbsp; "
            f"{get_role_icon(role_cible)} {get_role_label(role_cible)} &nbsp;|&nbsp; "
            f"{'✅ Actif' if actif_cible else '🔴 Désactivé'}",
            unsafe_allow_html=False
        )

        st.markdown("---")

        tab_role, tab_statut, tab_pwd, tab_suppr = st.tabs([
            "🎭 Modifier le rôle",
            "🔛 Activer / Désactiver",
            "🔑 Réinitialiser mot de passe",
            "🗑️ Supprimer"
        ])

        # ── Modifier le rôle ──────────────────────────────────────────────────
        with tab_role:
            roles_list = get_all_roles()
            role_labels = [f"{get_role_icon(r)} {get_role_label(r)}" for r in roles_list]
            role_actuel_label = f"{get_role_icon(role_cible)} {get_role_label(role_cible)}"
            idx_actuel = role_labels.index(role_actuel_label) if role_actuel_label in role_labels else 0

            nouveau_role_label = st.selectbox(
                "Nouveau rôle",
                options=role_labels,
                index=idx_actuel,
                key="gu_new_role"
            )
            nouveau_role = roles_list[role_labels.index(nouveau_role_label)]

            if st.button("✅ Appliquer le nouveau rôle", key="btn_update_role", type="primary"):
                if nouveau_role == role_cible:
                    st.warning("⚠️ Le rôle sélectionné est déjà celui de l'utilisateur.")
                else:
                    success, message = update_user_role(email_cible, nouveau_role)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

        # ── Activer / Désactiver ─────────────────────────────────────────────
        with tab_statut:
            if actif_cible:
                st.warning(f"⚠️ Vous allez **désactiver** le compte de **{nom_cible}**. L'utilisateur ne pourra plus se connecter.")
                if st.button("🔴 Désactiver ce compte", key="btn_desactiver", type="secondary"):
                    success, message = deactivate_user(email_cible)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.info(f"ℹ️ Le compte de **{nom_cible}** est actuellement désactivé.")
                if st.button("✅ Réactiver ce compte", key="btn_reactiver", type="primary"):
                    success, message = reactivate_user(email_cible)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

        # ── Réinitialiser mot de passe ────────────────────────────────────────
        with tab_pwd:
            st.caption(f"Définir un nouveau mot de passe pour **{nom_cible}** ({email_cible})")
            nouveau_mdp = st.text_input(
                "Nouveau mot de passe *",
                type="password",
                placeholder="Minimum 8 caractères",
                key="gu_reset_pwd"
            )
            confirm_mdp = st.text_input(
                "Confirmer le mot de passe *",
                type="password",
                placeholder="Répétez le mot de passe",
                key="gu_reset_pwd_confirm"
            )
            if st.button("🔑 Réinitialiser le mot de passe", key="btn_reset_pwd", type="primary"):
                if len(nouveau_mdp) < 8:
                    st.error("⚠️ Le mot de passe doit contenir au moins 8 caractères")
                elif nouveau_mdp != confirm_mdp:
                    st.error("⚠️ Les mots de passe ne correspondent pas")
                else:
                    success, message = _reset_password_admin(email_cible, nouveau_mdp)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

        # ── Supprimer ────────────────────────────────────────────────────────
        with tab_suppr:
            st.error(
                f"⚠️ **Action irréversible** — Vous allez supprimer définitivement le compte de "
                f"**{nom_cible}** ({email_cible})."
            )
            confirmation = st.text_input(
                f"Tapez exactement **{email_cible}** pour confirmer",
                placeholder=email_cible,
                key="gu_suppr_confirm"
            )
            if st.button("🗑️ Supprimer définitivement", key="btn_suppr_user", type="secondary"):
                if confirmation.strip() != email_cible:
                    st.error("⚠️ La confirmation ne correspond pas à l'email.")
                else:
                    success, message = delete_user(email_cible)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)


def _section_statistiques(users: list, df_obs: pd.DataFrame):
    """Statistiques détaillées par utilisateur."""
    with st.container(border=True):
        st.subheader("📊 Statistiques par utilisateur")

        if not users:
            st.info("ℹ️ Aucun utilisateur.")
            return

        rows = []
        for u in users:
            email     = u.get("email", "")
            nom       = u.get("nom_complet", "—")
            role      = u.get("role", "autre")
            dept      = u.get("departement", "—") or "—"
            date_crea = u.get("date_creation", "")
            last_co   = u.get("derniere_connexion", "")
            actif     = u.get("actif", True)
            nb_obs    = _compter_observations(nom, df_obs)

            # Dernière observation
            if not df_obs.empty and 'analyste' in df_obs.columns and 'date' in df_obs.columns:
                obs_user = df_obs[df_obs['analyste'].astype(str).str.lower() == nom.lower()]
                if not obs_user.empty:
                    derniere_obs = pd.to_datetime(obs_user['date'], errors='coerce').max()
                    derniere_obs_fmt = derniere_obs.strftime("%d/%m/%Y") if pd.notna(derniere_obs) else "—"
                else:
                    derniere_obs_fmt = "—"
            else:
                derniere_obs_fmt = "—"

            try:
                date_crea_fmt = datetime.fromisoformat(date_crea[:19]).strftime("%d/%m/%Y") if date_crea else "—"
            except Exception:
                date_crea_fmt = "—"

            try:
                last_co_fmt = datetime.fromisoformat(last_co[:19]).strftime("%d/%m/%Y %H:%M") if last_co else "Jamais"
            except Exception:
                last_co_fmt = "Jamais"

            rows.append({
                "Nom":                nom,
                "Email":              email,
                "Rôle":               f"{get_role_icon(role)} {get_role_label(role)}",
                "Département":        dept,
                "Statut":             "✅ Actif" if actif else "🔴 Désactivé",
                "Total obs.":         nb_obs,
                "Dernière obs.":      derniere_obs_fmt,
                "Dernière connexion": last_co_fmt,
                "Compte créé le":     date_crea_fmt,
            })

        df_stats = pd.DataFrame(rows).sort_values("Total obs.", ascending=False)

        st.dataframe(
            df_stats,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Total obs.": st.column_config.ProgressColumn(
                    "Observations",
                    min_value=0,
                    max_value=max(df_stats["Total obs."].max(), 1),
                    format="%d",
                    width="medium"
                ),
            }
        )


def _section_audit():
    """Journal d'audit des 100 dernières actions."""
    with st.container(border=True):
        st.subheader("🕵️ Journal d'audit")
        st.caption("100 dernières actions enregistrées dans le système")

        logs = get_audit_logs(limit=100)

        if not logs:
            st.info("ℹ️ Aucune action enregistrée.")
            return

        rows = []
        for log in logs:
            ts = log.get("timestamp", "")
            try:
                ts_fmt = datetime.fromisoformat(ts[:19]).strftime("%d/%m/%Y %H:%M:%S")
            except Exception:
                ts_fmt = ts

            details = log.get("details", {})
            detail_str = ", ".join(f"{k}: {v}" for k, v in details.items()) if isinstance(details, dict) else str(details)

            rows.append({
                "Date / Heure":   ts_fmt,
                "Utilisateur":    log.get("email", "—"),
                "Action":         log.get("action", "—"),
                "Table":          log.get("table_name", "—"),
                "Détails":        detail_str,
            })

        df_audit = pd.DataFrame(rows)
        st.dataframe(df_audit, use_container_width=True, hide_index=True)


# =============================================================================
# POINT D'ENTRÉE PRINCIPAL
# =============================================================================

def render():
    """Affiche l'onglet Gestion des Utilisateurs (admin uniquement)."""

    # ── Vérification de permission ────────────────────────────────────────────
    if not check_permission(Permission.GERER_UTILISATEURS):
        st.error("🔒 Accès refusé — Cette section est réservée aux administrateurs.")
        st.info("💡 Connectez-vous avec un compte administrateur pour accéder à cette page.")
        st.stop()

    st.header("👥 Gestion des Utilisateurs")
    st.caption(f"Administration des comptes — connecté en tant que **{get_user_name()}**")
    st.markdown("---")

    # ── Chargement des données ────────────────────────────────────────────────
    users = get_all_users()
    df_obs = _charger_stats_observations()

    if not users:
        st.warning("⚠️ Impossible de charger les utilisateurs. Vérifiez la connexion Supabase.")
        users = []

    # ── KPIs globaux ─────────────────────────────────────────────────────────
    _section_kpis(users, df_obs)

    st.markdown("##")

    # ── Onglets principaux ───────────────────────────────────────────────────
    tab_liste, tab_ajouter, tab_actions, tab_stats, tab_audit = st.tabs([
        "📋 Liste",
        "➕ Ajouter",
        "⚙️ Actions",
        "📊 Statistiques",
        "🕵️ Audit",
    ])

    with tab_liste:
        st.markdown("##")
        _section_liste(users, df_obs)

    with tab_ajouter:
        st.markdown("##")
        _section_ajouter()

    with tab_actions:
        st.markdown("##")
        _section_actions(users)

    with tab_stats:
        st.markdown("##")
        _section_statistiques(users, df_obs)

    with tab_audit:
        st.markdown("##")
        _section_audit()
