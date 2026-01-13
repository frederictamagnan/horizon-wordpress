# Guide de Migration vers LWS (belleile-voile.com)

## Prérequis
- Accès à l'explorateur de fichiers LWS
- Accès à phpMyAdmin sur LWS
- WordPress déjà installé sur LWS à https://belleile-voile.com/

## Fichiers nécessaires pour la migration
- `wordpress_export_20260113_181847.sql` (655KB) - Base de données
- `wp-content.zip` (15MB) - Tout le contenu (thème + traductions)

## Méthode 1 : Migration complète (RECOMMANDÉE)

### Étape 1 : Export depuis Docker local (DÉJÀ FAIT)
```bash
./export_database.sh  # Génère wordpress_export_YYYYMMDD_HHMMSS.sql
zip -r wp-content.zip wp-content  # Crée wp-content.zip
```

### Étape 2 : Sur LWS via phpMyAdmin
1. Connecte-toi à phpMyAdmin
2. Sélectionne ta base de données
3. Onglet **"Opérations"** > **"Supprimer la base de données"** (ou supprime toutes les tables wp_* manuellement)
4. Recrée la base si nécessaire
5. Onglet **"Importer"** > Choisis `wordpress_export_20260113_181847.sql`
6. Clique sur **"Exécuter"**

### Étape 3 : Upload wp-content.zip sur LWS
1. Via l'explorateur de fichiers LWS, va à la racine de ton WordPress
2. Upload `wp-content.zip`
3. Dézipme-le (remplace le dossier wp-content existant)
4. Supprime le fichier .zip après extraction

### Étape 4 : Mise à jour des URLs
Via phpMyAdmin, exécute ces requêtes SQL :
```sql
UPDATE wp_options SET option_value = 'https://belleile-voile.com' WHERE option_name = 'siteurl';
UPDATE wp_options SET option_value = 'https://belleile-voile.com' WHERE option_name = 'home';
```

### Étape 5 : Vérifications
1. Va sur https://belleile-voile.com
2. Vérifie que le thème Horizon Belle-Isle s'affiche
3. Teste la navigation et les pages
4. Teste wp-admin : https://belleile-voile.com/wp-admin

## Méthode 2 : Migration par parties (si problèmes)

### Étape 1 : Import de la base de données
Même que Méthode 1, Étape 2

### Étape 2 : Upload du thème uniquement
1. Upload le dossier `wp-content/themes/horizon-belleisle/` via FTP/explorateur
2. Vérifie que tous les sous-dossiers sont présents :
   - `css/components/` (11 fichiers CSS)
   - `images/` (logo.png, ffv.jpg)
   - `pages-content/` (4 fichiers HTML)
   - Tous les fichiers PHP à la racine

### Étape 3 : Upload des traductions françaises
Upload le dossier `wp-content/languages/` complet

### Étape 4 : Même que Méthode 1, Étapes 4 et 5

## Configuration wp-config.php

⚠️ **Important :** Le wp-config.php est déjà créé par LWS, ne le modifie PAS sauf si tu as des erreurs de connexion DB.

Si tu as des erreurs, vérifie que wp-config.php contient les bons identifiants fournis par LWS :
```php
define('DB_NAME', 'ton_nom_base_lws');
define('DB_USER', 'ton_user_lws');
define('DB_PASSWORD', 'ton_password_lws');
define('DB_HOST', 'localhost'); // ou autre selon LWS
```

## Problèmes courants

### Le site demande d'installer WordPress
- Les tables de la base de données n'ont pas été importées correctement
- Vérifie que l'import SQL s'est terminé sans erreur
- Réessaye l'import après avoir supprimé toutes les tables

### Les CSS ne se chargent pas
- Vide le cache du navigateur (Ctrl+F5)
- Vérifie que le dossier `wp-content/themes/horizon-belleisle/css/` existe
- Vérifie les permissions : 755 pour les dossiers, 644 pour les fichiers

### Erreur de connexion à la base de données
- Vérifie les informations dans wp-config.php
- Contacte le support LWS pour obtenir les bons identifiants

### Le site affiche le thème Twenty Twenty-Four (thème par défaut)
Active le thème via SQL :
```sql
UPDATE wp_options SET option_value = 'horizon-belleisle' WHERE option_name = 'template';
UPDATE wp_options SET option_value = 'horizon-belleisle' WHERE option_name = 'stylesheet';
```

### Les permalinks ne fonctionnent pas (pages 404)
1. Va dans wp-admin > Réglages > Permalinks
2. Vérifie que c'est bien **"Titre de la publication"** (/%postname%/)
3. Clique sur "Enregistrer" même sans rien changer
4. Vérifie que le fichier `.htaccess` existe et contient les bonnes règles de réécriture

### Le menu n'affiche pas les bons items
Le menu est dans la base de données, il devrait fonctionner après l'import. Si problème :
```sql
SELECT * FROM wp_posts WHERE post_type = 'nav_menu_item';
```

## Checklist de migration

- [ ] Export local fait : `wordpress_export_20260113_181847.sql` + `wp-content.zip`
- [ ] Suppression des tables wp_* sur LWS via phpMyAdmin
- [ ] Import du fichier .sql sur LWS
- [ ] Upload et décompression de wp-content.zip
- [ ] Mise à jour des URLs vers https://belleile-voile.com
- [ ] Site accessible et affiche le bon thème
- [ ] Navigation fonctionne (menu, pages, actualités)
- [ ] Admin accessible avec les credentials locaux
- [ ] CSS et images chargent correctement
- [ ] Page Actualités fonctionne
- [ ] Footer avec lien Instagram présent
- [ ] Permalinks fonctionnent (pas de 404)

## Scripts SQL utiles

### Vérifier les URLs actuelles
```sql
SELECT option_name, option_value FROM wp_options WHERE option_name IN ('siteurl', 'home');
```

### Réinitialiser le mot de passe admin (si nécessaire)
```sql
UPDATE wp_users SET user_pass = MD5('nouveau_mot_de_passe') WHERE user_login = 'admin';
```

### Vérifier le thème actif
```sql
SELECT option_name, option_value FROM wp_options WHERE option_name IN ('template', 'stylesheet');
```

### Lister toutes les pages
```sql
SELECT ID, post_title, post_name, post_status FROM wp_posts WHERE post_type = 'page' ORDER BY post_title;
```

### Vérifier la structure des permalinks
```sql
SELECT option_value FROM wp_options WHERE option_name = 'permalink_structure';
```
-- Devrait retourner: /%postname%/

## Support

Si tu rencontres des problèmes :
1. Vérifie les logs d'erreur PHP sur LWS
2. Active le mode debug WordPress temporairement (dans wp-config.php : `define('WP_DEBUG', true);`)
3. Contacte le support LWS si problème de configuration serveur
