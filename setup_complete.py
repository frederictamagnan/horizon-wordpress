#!/usr/bin/env python3
"""
Script de configuration complète et automatique de WordPress
Gère tout : pages, menu, contenu, liens, corrections automatiques
"""

import mysql.connector
import re
from datetime import datetime
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'horizon',
    'password': 'horizon_password',
    'database': 'horizon_wordpress'
}

JEKYLL_DIR = Path("/home/ftamagna/codevault/perso/new-website-horizon")
THEME_PAGES_DIR = Path("/home/ftamagna/codevault/perso/horizon-wordpress/wp-content/themes/horizon-belleisle/pages-content")

# Définition complète des pages
PAGES = [
    {
        'title': 'Accueil',
        'slug': 'accueil',
        'source': JEKYLL_DIR / 'index.md',
        'type': 'markdown',
        'in_menu': True,
        'menu_title': 'Home',
        'menu_order': 1
    },
    {
        'title': 'Locations',
        'slug': 'locations',
        'source': THEME_PAGES_DIR / 'locations.html',
        'type': 'html',
        'in_menu': True,
        'menu_title': 'Locations',
        'menu_order': 2
    },
    {
        'title': 'Stages de voile',
        'slug': 'stages',
        'source': THEME_PAGES_DIR / 'stages.html',
        'type': 'html',
        'in_menu': True,
        'menu_title': 'Stages voile',
        'menu_order': 3
    },
    {
        'title': 'Info et contact',
        'slug': 'contact',
        'source': THEME_PAGES_DIR / 'contact.html',
        'type': 'html',
        'in_menu': True,
        'menu_title': 'Info et contact',
        'menu_order': 4
    },
    {
        'title': 'Actualités',
        'slug': 'actualites',
        'source': None,  # Page spéciale qui affichera la liste des posts
        'type': 'special',
        'content': '<!-- Liste des actualités affichée automatiquement -->',
        'in_menu': True,
        'menu_title': 'Actualités',
        'menu_order': 5
    },
    {
        'title': 'Mentions légales',
        'slug': 'mentions-legales',
        'source': THEME_PAGES_DIR / 'mentions-legales.html',
        'type': 'html',
        'in_menu': False,  # Pas dans le menu principal (sera en footer)
        'menu_title': None,
        'menu_order': None
    }
]

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_db_connection():
    """Crée une connexion à la base de données"""
    return mysql.connector.connect(**DB_CONFIG)

def parse_markdown_content(content):
    """Extrait le contenu HTML d'un fichier Markdown Jekyll"""
    match = re.match(r'^---\s*\n.*?\n---\s*\n(.*)$', content, re.DOTALL)
    if match:
        return match.group(1)
    return content

def fix_links(content):
    """Convertit les liens Jekyll en liens WordPress"""
    # Mapping des slugs Jekyll vers WordPress (sans base URL)
    slug_mapping = {
        'info-et-contact': 'contact',
    }

    # Applique les corrections de slugs
    for old_slug, new_slug in slug_mapping.items():
        # Corrige les liens avec /
        content = re.sub(rf'href="/{old_slug}/"', f'href="/{new_slug}/"', content)
        content = re.sub(rf'href="http://localhost:8080/{old_slug}/"', f'href="http://localhost:8080/{new_slug}/"', content)

    return content

# ============================================================================
# GESTION DES PAGES
# ============================================================================

def create_or_update_page(cursor, page_info):
    """Crée ou met à jour une page WordPress avec son contenu"""
    slug = page_info['slug']
    title = page_info['title']

    # Vérifie si la page existe
    cursor.execute(
        "SELECT ID FROM wp_posts WHERE post_name = %s AND post_type = 'page'",
        (slug,)
    )
    existing = cursor.fetchone()

    # Lit et prépare le contenu
    content = ''
    if page_info['type'] == 'special':
        # Page spéciale avec contenu prédéfini
        content = page_info.get('content', f"<!-- Contenu de {title} -->")
    elif page_info['source'] and page_info['source'].exists():
        with open(page_info['source'], 'r', encoding='utf-8') as f:
            raw_content = f.read()

        if page_info['type'] == 'markdown':
            content = parse_markdown_content(raw_content)
        else:
            content = raw_content

        content = fix_links(content)
    else:
        if page_info['source']:
            print(f"   ⚠️  Fichier source introuvable : {page_info['source']}")
        content = f"<!-- Contenu de {title} -->"

    # Crée ou met à jour
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if existing:
        page_id = existing[0]
        cursor.execute(
            "UPDATE wp_posts SET post_content = %s, post_title = %s WHERE ID = %s",
            (content, title, page_id)
        )
        print(f"   ✅ Page '{title}' mise à jour (ID: {page_id})")
    else:
        cursor.execute("""
            INSERT INTO wp_posts (
                post_author, post_date, post_date_gmt, post_content, post_title,
                post_excerpt, post_status, comment_status, ping_status, post_password,
                post_name, to_ping, pinged, post_modified, post_modified_gmt,
                post_content_filtered, post_parent, guid, menu_order, post_type,
                post_mime_type, comment_count
            ) VALUES (
                1, %s, %s, %s, %s, '', 'publish', 'closed', 'closed', '',
                %s, '', '', %s, %s, '', 0, '', 0, 'page', '', 0
            )
        """, (now, now, content, title, slug, now, now))

        page_id = cursor.lastrowid
        cursor.execute(
            "UPDATE wp_posts SET guid = %s WHERE ID = %s",
            (f'http://localhost:8080/?page_id={page_id}', page_id)
        )
        print(f"   ✅ Page '{title}' créée (ID: {page_id})")

    # Assigne le template pour la page Actualités
    if slug == 'actualites':
        # Vérifie si la métadonnée existe
        cursor.execute(
            "SELECT meta_id FROM wp_postmeta WHERE post_id = %s AND meta_key = '_wp_page_template'",
            (page_id,)
        )
        existing_meta = cursor.fetchone()

        if existing_meta:
            cursor.execute(
                "UPDATE wp_postmeta SET meta_value = 'page-actualites.php' WHERE post_id = %s AND meta_key = '_wp_page_template'",
                (page_id,)
            )
        else:
            cursor.execute(
                "INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (%s, '_wp_page_template', 'page-actualites.php')",
                (page_id,)
            )
        print(f"      → Template 'page-actualites.php' assigné")

    return page_id

# ============================================================================
# GESTION DU MENU
# ============================================================================

def clean_existing_menu(cursor):
    """Supprime le menu existant pour repartir de zéro"""
    print("   🧹 Nettoyage de l'ancien menu...")

    # Récupère l'ID du menu
    cursor.execute(
        "SELECT term_id FROM wp_terms WHERE name = 'Menu Principal'"
    )
    result = cursor.fetchone()

    if result:
        menu_term_id = result[0]

        # Récupère le term_taxonomy_id
        cursor.execute(
            "SELECT term_taxonomy_id FROM wp_term_taxonomy WHERE term_id = %s AND taxonomy = 'nav_menu'",
            (menu_term_id,)
        )
        tax_result = cursor.fetchone()

        if tax_result:
            menu_taxonomy_id = tax_result[0]

            # Récupère tous les items du menu
            cursor.execute(
                "SELECT object_id FROM wp_term_relationships WHERE term_taxonomy_id = %s",
                (menu_taxonomy_id,)
            )
            menu_items = cursor.fetchall()

            # Supprime les items
            for (item_id,) in menu_items:
                # Supprime les métadonnées
                cursor.execute("DELETE FROM wp_postmeta WHERE post_id = %s", (item_id,))
                # Supprime le post
                cursor.execute("DELETE FROM wp_posts WHERE ID = %s", (item_id,))

            # Supprime les relations
            cursor.execute(
                "DELETE FROM wp_term_relationships WHERE term_taxonomy_id = %s",
                (menu_taxonomy_id,)
            )

            # Supprime la taxonomy
            cursor.execute("DELETE FROM wp_term_taxonomy WHERE term_taxonomy_id = %s", (menu_taxonomy_id,))

            # Supprime le terme
            cursor.execute("DELETE FROM wp_terms WHERE term_id = %s", (menu_term_id,))

            print(f"   ✅ Ancien menu supprimé ({len(menu_items)} items)")

def create_menu(cursor, conn, page_ids):
    """Crée le menu WordPress avec tous les items"""

    # Nettoie l'ancien menu
    clean_existing_menu(cursor)
    conn.commit()

    print("   📋 Création du nouveau menu...")

    # Crée le terme pour le menu
    cursor.execute(
        "INSERT INTO wp_terms (name, slug) VALUES ('Menu Principal', 'menu-principal')"
    )
    menu_term_id = cursor.lastrowid

    # Associe le terme à la taxonomie nav_menu
    cursor.execute(
        "INSERT INTO wp_term_taxonomy (term_id, taxonomy, description, parent, count) VALUES (%s, 'nav_menu', '', 0, 0)",
        (menu_term_id,)
    )
    menu_taxonomy_id = cursor.lastrowid

    print(f"   ✅ Menu 'Menu Principal' créé (ID: {menu_term_id})")

    # Configure l'emplacement du menu dans le thème
    cursor.execute(
        "UPDATE wp_options SET option_value = %s WHERE option_name = 'theme_mods_horizon-belleisle'",
        (f'a:1:{{s:18:"nav_menu_locations";a:1:{{s:7:"primary";i:{menu_term_id};}}}}',)
    )

    # Crée les items du menu
    print("   📝 Ajout des items au menu...")

    for page_info in PAGES:
        if not page_info['in_menu']:
            continue

        slug = page_info['slug']
        menu_title = page_info['menu_title']
        order = page_info['menu_order']

        page_id = page_ids.get(slug)
        if not page_id:
            print(f"      ⚠️  Page '{slug}' introuvable")
            continue

        # Crée le post pour l'item de menu
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            INSERT INTO wp_posts (
                post_author, post_date, post_date_gmt, post_content, post_title,
                post_excerpt, post_status, comment_status, ping_status, post_password,
                post_name, to_ping, pinged, post_modified, post_modified_gmt,
                post_content_filtered, post_parent, guid, menu_order, post_type,
                post_mime_type, comment_count
            ) VALUES (
                1, %s, %s, '', %s, '', 'publish', 'closed', 'closed', '',
                %s, '', '', %s, %s, '', 0, '', %s, 'nav_menu_item', '', 0
            )
        """, (now, now, menu_title, f'menu-item-{page_id}', now, now, order))

        menu_item_id = cursor.lastrowid

        # Associe l'item au menu
        cursor.execute(
            "INSERT INTO wp_term_relationships (object_id, term_taxonomy_id, term_order) VALUES (%s, %s, %s)",
            (menu_item_id, menu_taxonomy_id, order)
        )

        # Ajoute les métadonnées
        meta_data = [
            ('_menu_item_type', 'post_type'),
            ('_menu_item_menu_item_parent', '0'),
            ('_menu_item_object_id', str(page_id)),
            ('_menu_item_object', 'page'),
            ('_menu_item_target', ''),
            ('_menu_item_classes', 'a:1:{i:0;s:0:"";}'),
            ('_menu_item_xfn', ''),
            ('_menu_item_url', ''),
        ]

        for meta_key, meta_value in meta_data:
            cursor.execute(
                "INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (%s, %s, %s)",
                (menu_item_id, meta_key, meta_value)
            )

        print(f"      ✅ Item '{menu_title}' ajouté")

    # Met à jour le compteur d'items
    cursor.execute(
        "UPDATE wp_term_taxonomy SET count = (SELECT COUNT(*) FROM wp_term_relationships WHERE term_taxonomy_id = %s) WHERE term_taxonomy_id = %s",
        (menu_taxonomy_id, menu_taxonomy_id)
    )

# ============================================================================
# CONFIGURATION WORDPRESS
# ============================================================================

def configure_wordpress(cursor, page_ids):
    """Configure les options WordPress (page d'accueil, etc.)"""
    print("   ⚙️  Configuration de WordPress...")

    # Page d'accueil statique
    cursor.execute(
        "UPDATE wp_options SET option_value = 'page' WHERE option_name = 'show_on_front'"
    )
    cursor.execute(
        "UPDATE wp_options SET option_value = %s WHERE option_name = 'page_on_front'",
        (page_ids['accueil'],)
    )

    # Structure des permaliens (URLs propres)
    cursor.execute(
        "UPDATE wp_options SET option_value = '/%postname%/' WHERE option_name = 'permalink_structure'"
    )

    print("   ✅ Page d'accueil configurée")
    print("   ✅ Permaliens configurés (/%postname%/)")

# ============================================================================
# SCRIPT PRINCIPAL
# ============================================================================

def main():
    print("=" * 70)
    print("🚀 CONFIGURATION COMPLÈTE DE WORDPRESS HORIZON BELLE-ISLE")
    print("=" * 70)

    try:
        # Connexion
        print("\n🔌 Connexion à la base de données...")
        conn = get_db_connection()
        cursor = conn.cursor()
        print("✅ Connecté")

        # Création/mise à jour des pages
        print("\n📄 Gestion des pages...")
        page_ids = {}
        for page_info in PAGES:
            page_id = create_or_update_page(cursor, page_info)
            page_ids[page_info['slug']] = page_id

        conn.commit()
        print(f"✅ {len(PAGES)} pages traitées")

        # Configuration WordPress
        print("\n⚙️  Configuration WordPress...")
        configure_wordpress(cursor, page_ids)
        conn.commit()

        # Création du menu
        print("\n📋 Gestion du menu...")
        create_menu(cursor, conn, page_ids)
        conn.commit()
        print("✅ Menu créé et configuré")

        # Fermeture
        cursor.close()
        conn.close()

        # Résumé
        print("\n" + "=" * 70)
        print("🎉 CONFIGURATION TERMINÉE AVEC SUCCÈS !")
        print("=" * 70)
        print(f"\n📊 Résumé :")
        print(f"   • {len(PAGES)} pages créées/mises à jour")
        print(f"   • {sum(1 for p in PAGES if p['in_menu'])} items de menu")
        print(f"   • Page d'accueil : {page_ids['accueil']}")

        print(f"\n🌐 Votre site est prêt :")
        print(f"   • Site public : http://localhost:8080")
        print(f"   • Administration : http://localhost:8080/wp-admin")
        print(f"   • Éditer les pages : http://localhost:8080/wp-admin/edit.php?post_type=page")
        print(f"   • Gérer le menu : http://localhost:8080/wp-admin/nav-menus.php")

        print("\n💡 Ce script peut être relancé à tout moment pour :")
        print("   • Réimporter le contenu depuis les fichiers sources")
        print("   • Corriger des problèmes de menu")
        print("   • Ajouter de nouvelles pages")
        print("\n")

    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
