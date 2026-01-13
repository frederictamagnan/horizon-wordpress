# Security Cleanup Required

## Situation
Les commits précédents contenaient des mots de passe en dur dans `docker-compose.yml` et `export_database.sh`.

Ces mots de passe étaient uniquement pour l'environnement Docker local et ne concernent pas de vrais systèmes de production.

## Nettoyage de l'historique Git

Pour supprimer complètement ces passwords de l'historique Git, il faut réécrire l'historique.

### Option 1 : Force push (Simple mais destructif)

⚠️ **ATTENTION** : Ceci va réécrire l'historique et nécessite un force push

```bash
# 1. Sauvegarder la branche actuelle
git branch backup-main

# 2. Créer un commit squash de tout
git reset --soft $(git rev-list --max-parents=0 HEAD)
git commit -m "Initial commit with clean configuration"

# 3. Force push
git push --force origin main
```

### Option 2 : Utiliser git-filter-repo (Recommandé)

```bash
# Installer git-filter-repo
pip install git-filter-repo

# Créer un fichier de remplacement
cat > replacements.txt <<EOF
horizon_password==>YOUR_PASSWORD_HERE
root_password==>YOUR_ROOT_PASSWORD_HERE
EOF

# Exécuter le nettoyage
git filter-repo --replace-text replacements.txt

# Force push
git push --force origin main
```

### Option 3 : Nouveau repo (Plus simple)

Si personne d'autre n'a cloné le repo :

```bash
# 1. Supprimer le repo GitHub
# Aller sur https://github.com/frederictamagnan/horizon-wordpress/settings
# Scroll down > Delete this repository

# 2. Supprimer l'historique local
rm -rf .git

# 3. Réinitialiser
git init
git add .
git commit -m "Initial commit: WordPress theme with secure configuration"
git remote add origin git@github.com:frederictamagnan/horizon-wordpress.git
git push -u origin main
```

## État actuel

✅ Les nouveaux commits n'exposent plus de passwords
✅ Le fichier .env est ignoré par git
✅ .env.example contient des placeholders

⚠️ Les anciens commits (5568920 et 611508f) contiennent encore :
- `horizon_password`
- `root_password`

Ces passwords étaient uniquement pour Docker local et n'ont jamais été utilisés en production.

## Recommandation

Comme c'est un repo récent et que les passwords concernent uniquement l'environnement local Docker, **Option 3** (nouveau repo) est la plus simple.
