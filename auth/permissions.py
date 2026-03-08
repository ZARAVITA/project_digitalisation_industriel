"""
Système de gestion des rôles et permissions
Définit les permissions pour chaque rôle
"""

from enum import Enum
from typing import List, Dict


class Role(Enum):
    """Énumération des rôles disponibles"""
    ADMIN = "admin"
    ANALYSTE = "analyste"
    TECHNICIEN = "technicien"
    AUTRE = "autre"


class Permission(Enum):
    """Énumération des permissions disponibles"""
    # Gestion utilisateurs
    GERER_UTILISATEURS = "gerer_utilisateurs"
    
    # Équipements
    VOIR_EQUIPEMENTS = "voir_equipements"
    AJOUTER_EQUIPEMENTS = "ajouter_equipements"
    MODIFIER_EQUIPEMENTS = "modifier_equipements"
    SUPPRIMER_EQUIPEMENTS = "supprimer_equipements"
    
    # Observations
    VOIR_OBSERVATIONS = "voir_observations"
    AJOUTER_OBSERVATIONS = "ajouter_observations"
    MODIFIER_OBSERVATIONS = "modifier_observations"
    SUPPRIMER_OBSERVATIONS = "supprimer_observations"
    
    # Suivis
    VOIR_SUIVIS = "voir_suivis"
    AJOUTER_SUIVIS = "ajouter_suivis"
    MODIFIER_SUIVIS = "modifier_suivis"
    SUPPRIMER_SUIVIS = "supprimer_suivis"
    
    # Exports
    EXPORTER_DONNEES = "exporter_donnees"
    
    # Administration
    VOIR_STATISTIQUES = "voir_statistiques"
    VOIR_AUDIT = "voir_audit"


# Matrice de permissions par rôle
ROLE_PERMISSIONS: Dict[Role, List[Permission]] = {
    # ADMIN : Accès total
    Role.ADMIN: [
        # Utilisateurs
        Permission.GERER_UTILISATEURS,
        
        # Équipements
        Permission.VOIR_EQUIPEMENTS,
        Permission.AJOUTER_EQUIPEMENTS,
        Permission.MODIFIER_EQUIPEMENTS,
        Permission.SUPPRIMER_EQUIPEMENTS,
        
        # Observations
        Permission.VOIR_OBSERVATIONS,
        Permission.AJOUTER_OBSERVATIONS,
        Permission.MODIFIER_OBSERVATIONS,
        Permission.SUPPRIMER_OBSERVATIONS,
        
        # Suivis
        Permission.VOIR_SUIVIS,
        Permission.AJOUTER_SUIVIS,
        Permission.MODIFIER_SUIVIS,
        Permission.SUPPRIMER_SUIVIS,
        
        # Exports et stats
        Permission.EXPORTER_DONNEES,
        Permission.VOIR_STATISTIQUES,
        Permission.VOIR_AUDIT,
    ],
    
    # ANALYSTE : Accès complet sauf gestion utilisateurs
    Role.ANALYSTE: [
        # Équipements
        Permission.VOIR_EQUIPEMENTS,
        Permission.AJOUTER_EQUIPEMENTS,
        Permission.MODIFIER_EQUIPEMENTS,
        Permission.SUPPRIMER_EQUIPEMENTS,
        
        # Observations
        Permission.VOIR_OBSERVATIONS,
        Permission.AJOUTER_OBSERVATIONS,
        Permission.MODIFIER_OBSERVATIONS,
        Permission.SUPPRIMER_OBSERVATIONS,
        
        # Suivis
        Permission.VOIR_SUIVIS,
        Permission.AJOUTER_SUIVIS,
        Permission.MODIFIER_SUIVIS,
        Permission.SUPPRIMER_SUIVIS,
        
        # Exports et stats
        Permission.EXPORTER_DONNEES,
        Permission.VOIR_STATISTIQUES,
    ],
    
    # TECHNICIEN : Peut ajouter/modifier, pas supprimer
    Role.TECHNICIEN: [
        # Équipements
        Permission.VOIR_EQUIPEMENTS,
        Permission.AJOUTER_EQUIPEMENTS,
        
        # Observations
        Permission.VOIR_OBSERVATIONS,
        Permission.AJOUTER_OBSERVATIONS,
        Permission.MODIFIER_OBSERVATIONS,  # Ses propres observations uniquement
        
        # Suivis
        Permission.VOIR_SUIVIS,
        Permission.AJOUTER_SUIVIS,
        Permission.MODIFIER_SUIVIS,
        
        # Exports
        Permission.EXPORTER_DONNEES,
    ],
    
    # AUTRE : Lecture seule
    Role.AUTRE: [
        # Lecture seule
        Permission.VOIR_EQUIPEMENTS,
        Permission.VOIR_OBSERVATIONS,
        Permission.VOIR_SUIVIS,
        
        # Export seulement
        Permission.EXPORTER_DONNEES,
    ],
}


# Métadonnées des rôles (pour l'affichage)
ROLE_METADATA = {
    Role.ADMIN: {
        "icon": "🔑",
        "label": "Administrateur",
        "color": "#FF4B4B",
        "description": "Accès total au système, gestion des utilisateurs"
    },
    Role.ANALYSTE: {
        "icon": "📊",
        "label": "Analyste",
        "color": "#0068C9",
        "description": "Accès complet aux données, peut tout modifier et supprimer"
    },
    Role.TECHNICIEN: {
        "icon": "🔧",
        "label": "Technicien",
        "color": "#29B09D",
        "description": "Peut ajouter et modifier, lecture complète"
    },
    Role.AUTRE: {
        "icon": "👁️",
        "label": "Consultation",
        "color": "#7D7D7D",
        "description": "Lecture seule et export des données"
    }
}


def has_permission(role: str, permission: Permission) -> bool:
    """
    Vérifie si un rôle a une permission spécifique
    
    Args:
        role (str): Nom du rôle (admin, analyste, technicien, autre)
        permission (Permission): Permission à vérifier
    
    Returns:
        bool: True si le rôle a la permission
    """
    try:
        role_enum = Role(role)
        return permission in ROLE_PERMISSIONS.get(role_enum, [])
    except ValueError:
        return False


def get_role_permissions(role: str) -> List[Permission]:
    """
    Retourne toutes les permissions d'un rôle
    
    Args:
        role (str): Nom du rôle
    
    Returns:
        List[Permission]: Liste des permissions
    """
    try:
        role_enum = Role(role)
        return ROLE_PERMISSIONS.get(role_enum, [])
    except ValueError:
        return []


def get_role_label(role: str) -> str:
    """Retourne le label d'affichage d'un rôle"""
    try:
        role_enum = Role(role)
        return ROLE_METADATA[role_enum]["label"]
    except (ValueError, KeyError):
        return role


def get_role_icon(role: str) -> str:
    """Retourne l'icône d'un rôle"""
    try:
        role_enum = Role(role)
        return ROLE_METADATA[role_enum]["icon"]
    except (ValueError, KeyError):
        return "👤"


def get_role_color(role: str) -> str:
    """Retourne la couleur associée à un rôle"""
    try:
        role_enum = Role(role)
        return ROLE_METADATA[role_enum]["color"]
    except (ValueError, KeyError):
        return "#7D7D7D"


def get_role_description(role: str) -> str:
    """Retourne la description d'un rôle"""
    try:
        role_enum = Role(role)
        return ROLE_METADATA[role_enum]["description"]
    except (ValueError, KeyError):
        return ""


def get_all_roles() -> List[str]:
    """Retourne la liste de tous les rôles disponibles"""
    return [role.value for role in Role]


def format_role_for_display(role: str) -> str:
    """
    Formate un rôle pour l'affichage avec icône
    
    Args:
        role (str): Nom du rôle
    
    Returns:
        str: Rôle formaté avec icône (ex: "🔑 Administrateur")
    """
    icon = get_role_icon(role)
    label = get_role_label(role)
    return f"{icon} {label}"


# =============================================================================
# MESSAGES D'ERREUR PERSONNALISÉS PAR PERMISSION
# =============================================================================

PERMISSION_ERROR_MESSAGES = {
    Permission.GERER_UTILISATEURS: "🔒 Seuls les administrateurs peuvent gérer les utilisateurs",
    Permission.SUPPRIMER_EQUIPEMENTS: "🔒 Vous n'avez pas la permission de supprimer des équipements",
    Permission.SUPPRIMER_OBSERVATIONS: "🔒 Vous n'avez pas la permission de supprimer des observations",
    Permission.SUPPRIMER_SUIVIS: "🔒 Vous n'avez pas la permission de supprimer des suivis",
    Permission.MODIFIER_EQUIPEMENTS: "🔒 Vous n'avez pas la permission de modifier des équipements",
    Permission.MODIFIER_OBSERVATIONS: "🔒 Vous n'avez pas la permission de modifier des observations",
    Permission.AJOUTER_EQUIPEMENTS: "🔒 Vous n'avez pas la permission d'ajouter des équipements",
    Permission.VOIR_AUDIT: "🔒 Seuls les administrateurs peuvent voir les logs d'audit",
}


def get_permission_error_message(permission: Permission) -> str:
    """Retourne un message d'erreur personnalisé pour une permission"""
    return PERMISSION_ERROR_MESSAGES.get(
        permission,
        "🔒 Vous n'avez pas la permission d'effectuer cette action"
    )
