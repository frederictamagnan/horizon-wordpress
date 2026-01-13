# Guide d'administration WordPress - Horizon Belle-Isle

Ce guide explique comment administrer votre site via l'interface WordPress.

## Accès à l'administration

**URL** : http://localhost:8080/wp-admin (local) ou https://votresite.fr/wp-admin (production)

Connectez-vous avec les identifiants créés lors de l'installation.

## 1. Activer le thème

1. Allez dans **Apparence > Thèmes**
2. Cliquez sur **Activer** sous "Horizon Belle-Isle"

## 2. Créer les pages

### Page d'accueil

1. Allez dans **Pages > Ajouter**
2. Titre : `Accueil`
3. Contenu : Laissez vide (géré automatiquement par le thème)
4. Cliquez sur **Publier**

### Page Locations

1. **Pages > Ajouter**
2. Titre : `Locations`
3. Slug : `locations` (dans le panneau latéral, sous "Permalien")
4. Basculez en mode **Éditeur de code** (⋮ en haut à droite > Éditeur de code)
5. Copiez-collez le contenu du fichier `wp-content/themes/horizon-belleisle/pages-content/locations.html`
6. **Publier**

### Page Stages voile

1. **Pages > Ajouter**
2. Titre : `Stages voile`
3. Slug : `stages`
4. Mode **Éditeur de code**
5. Copiez le contenu de `pages-content/stages.html`
6. **Publier**

### Page Info et contact

1. **Pages > Ajouter**
2. Titre : `Info et contact`
3. Slug : `info-et-contact`
4. Mode **Éditeur de code**
5. Copiez le contenu de `pages-content/contact.html`
6. **Publier**

### Page Mentions légales

1. **Pages > Ajouter**
2. Titre : `Mentions légales`
3. Slug : `mentions-legales`
4. Mode **Éditeur de code**
5. Copiez le contenu de `pages-content/mentions-legales.html`
6. **Publier**

## 3. Configurer le menu

1. Allez dans **Apparence > Menus**
2. Cliquez sur **Créer un nouveau menu**
3. Nom du menu : `Menu Principal`
4. Cochez **Menu Principal** dans "Emplacement du thème"
5. Cliquez sur **Créer le menu**

### Ajouter les pages au menu

Dans la colonne de gauche, sous "Pages" :

1. **Accueil** - Ajoutez-la
2. **Locations** - Ajoutez-la
3. **Stages voile** - Ajoutez-la
4. **Info et contact** - Ajoutez-la

### Créer les sous-menus pour Locations

1. Dans la colonne de gauche, cliquez sur **Liens personnalisés**
2. Ajoutez ces liens un par un :
   - URL : `/locations/#hobbie-cat` | Texte : `Hobbie Cat`
   - URL : `/locations/#planche-voile` | Texte : `Planche à voile`
   - URL : `/locations/#paddle` | Texte : `Paddle`
   - URL : `/locations/#moteur` | Texte : `Moteur`
   - URL : `/locations/#kayak` | Texte : `Kayak`

3. **Glissez-déposez** ces liens sous "Locations" en les décalant vers la droite pour en faire des sous-éléments

4. Cliquez sur **Enregistrer le menu**

## 4. Configurer la page d'accueil

1. Allez dans **Réglages > Lecture**
2. Sélectionnez **Une page statique**
3. Page d'accueil : sélectionnez **Accueil**
4. **Enregistrer**

## 5. Configurer les permaliens

1. Allez dans **Réglages > Permaliens**
2. Sélectionnez **Titre de la publication**
3. **Enregistrer**

## 6. Ajouter le logo

1. Allez dans **Apparence > Personnaliser**
2. Cliquez sur **Identité du site**
3. Dans "Logo", cliquez sur **Sélectionner un logo**
4. Uploadez `wp-content/themes/horizon-belleisle/images/logo.png`
5. **Publier**

## 7. Modifier le contenu des pages

### Via l'éditeur WordPress (recommandé)

1. Allez dans **Pages > Toutes les pages**
2. Cliquez sur le titre de la page à modifier
3. Modifiez le contenu directement dans l'éditeur
4. Cliquez sur **Mettre à jour**

### Éléments modifiables facilement :

- **Textes** : Cliquez et modifiez directement
- **Prix** : Modifiez les montants dans les sections `.price`
- **Horaires** : Changez les heures d'ouverture
- **Coordonnées** : Téléphone, email, adresse
- **Réseaux sociaux** : Facebook, Instagram

### Pour les modifications avancées :

Passez en mode **Éditeur de code** (⋮ en haut à droite) pour modifier le HTML directement.

## 8. Ajouter des images

1. Dans l'éditeur de page, cliquez sur **+** pour ajouter un bloc
2. Recherchez "Image"
3. Uploadez votre image ou sélectionnez-en une de la médiathèque
4. **Mettre à jour** la page

## 9. Gérer les commentaires

Par défaut, les commentaires sont désactivés sur les pages. Si besoin :

1. **Réglages > Discussion**
2. Décochez "Autoriser les visiteurs à publier des commentaires"

## 10. Sauvegardes

### En local (Docker)

Les données sont dans des volumes Docker :
```bash
# Exporter la base de données
docker compose exec db mysqldump -u horizon -phorizon_password horizon_wordpress > backup.sql

# Sauvegarder les fichiers
cp -r wp-content/ backup-wp-content/
```

### Sur LWS

Utilisez les outils de sauvegarde LWS ou installez une extension comme **UpdraftPlus**.

## Extensions recommandées (optionnelles)

1. **Contact Form 7** - Pour ajouter un formulaire de contact
2. **Google Analytics for WordPress** - Pour les statistiques
3. **WP Super Cache** - Pour améliorer les performances
4. **UpdraftPlus** - Pour les sauvegardes automatiques

Pour installer une extension :
1. **Extensions > Ajouter**
2. Recherchez l'extension
3. Cliquez sur **Installer** puis **Activer**

## Problèmes courants

### Le thème n'apparaît pas
- Vérifiez que le dossier `wp-content/themes/horizon-belleisle/` existe
- Vérifiez les permissions (755 pour les dossiers, 644 pour les fichiers)

### Les styles ne s'appliquent pas
- Videz le cache : **Apparence > Personnaliser** puis rechargez
- Vérifiez que `style.css` est bien présent dans le dossier du thème

### Le menu ne s'affiche pas
- Vérifiez que vous avez bien assigné le menu à l'emplacement "Menu Principal"
- Allez dans **Apparence > Menus** pour vérifier

## Support

- Documentation WordPress FR : https://fr.wordpress.org/support/
- Forum WordPress FR : https://wpfr.net/
