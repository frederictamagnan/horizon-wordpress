#!/usr/bin/env python3
"""
Script d'import du contenu HTML dans WordPress
Lit les fichiers Jekyll MD et pages-content HTML et les importe dans les pages WordPress
"""

import mysql.connector
import re
from pathlib import Path

# Configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'horizon',
    'password': 'horizon_password',
    'database': 'horizon_wordpress'
}

JEKYLL_DIR = Path("/home/ftamagna/codevault/perso/new-website-horizon")
THEME_PAGES_DIR = Path("/home/ftamagna/codevault/perso/horizon-wordpress/wp-content/themes/horizon-belleisle/pages-content")

# Mapping des pages
CONTENT_MAPPING = {
    'accueil': {
        'source': JEKYLL_DIR / 'index.md',
        'type': 'markdown'
    },
    'locations': {
        'source': THEME_PAGES_DIR / 'locations.html',
        'type': 'html'
    },
    'stages': {
        'source': THEME_PAGES_DIR / 'stages.html',
        'type': 'html'
    },
    'contact': {
        'source': THEME_PAGES_DIR / 'contact.html',
        'type': 'html'
    }
}

def parse_markdown_content(content):
    """Extrait le contenu HTML d'un fichier Markdown Jekyll"""
    # Enlève le front matter
    match = re.match(r'^---\s*\n.*?\n---\s*\n(.*)$', content, re.DOTALL)
    if match:
        return match.group(1)
    return content

def fix_links(content):
    """Convertit les liens Jekyll en liens WordPress"""
    # /locations/ -> <?php echo home_url('/locations/'); ?>
    # Mais pour le contenu éditable, on garde les liens relatifs simples
    content = re.sub(r'href="/([^"]+)/"', r'href="/\1/"', content)
    content = re.sub(r'href="/info-et-contact/"', r'href="/contact/"', content)
    return content

def get_db_connection():
    """Crée une connexion à la base de données"""
    return mysql.connector.connect(**DB_CONFIG)

def import_content(cursor, slug, content):
    """Importe le contenu dans une page WordPress"""
    # Récupère l'ID de la page
    cursor.execute(
        "SELECT ID FROM wp_posts WHERE post_name = %s AND post_type = 'page'",
        (slug,)
    )
    result = cursor.fetchone()

    if not result:
        print(f"   ❌ Page '{slug}' introuvable")
        return False

    page_id = result[0]

    # Met à jour le contenu
    cursor.execute(
        "UPDATE wp_posts SET post_content = %s WHERE ID = %s",
        (content, page_id)
    )

    print(f"   ✅ Contenu importé pour '{slug}' (ID: {page_id})")
    return True

def main():
    print("📥 Import du contenu HTML dans WordPress")
    print("=" * 60)

    try:
        # Connexion à la base
        print("\n🔌 Connexion à la base de données...")
        conn = get_db_connection()
        cursor = conn.cursor()
        print("✅ Connecté\n")

        imported = 0

        for slug, info in CONTENT_MAPPING.items():
            source_file = info['source']

            if not source_file.exists():
                print(f"⚠️  Fichier source introuvable : {source_file}")
                continue

            print(f"📄 Import du contenu pour '{slug}'...")

            # Lit le contenu
            with open(source_file, 'r', encoding='utf-8') as f:
                raw_content = f.read()

            # Parse selon le type
            if info['type'] == 'markdown':
                content = parse_markdown_content(raw_content)
            else:
                content = raw_content

            # Corrige les liens
            content = fix_links(content)

            # Import dans WordPress
            if import_content(cursor, slug, content):
                imported += 1

        # Commit
        conn.commit()
        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print(f"🎉 Import terminé ! {imported} page(s) mise(s) à jour")
        print("\n🌐 Visitez http://localhost:8080 pour voir le résultat")
        print("✏️  Éditez via http://localhost:8080/wp-admin/edit.php?post_type=page")

    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
