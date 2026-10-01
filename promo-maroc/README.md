# Promo Maroc — application mobile de promotions

Application mobile (PWA, installable sur Android et iPhone, fonctionne hors ligne) pour suivre les
promotions commerciales au Maroc, tous types de produits.

## Fonctionnalités

- Pour chaque promotion : **produit, marque, enseigne, ville, catégorie, prix original, prix promo,
  pourcentage de remise, date de début, date de fin**, conditions et lien vers la source.
- Calcul automatique : saisissez deux valeurs parmi prix original / prix promo / pourcentage, la troisième est calculée.
- Statut automatique selon la date du jour : **En cours**, **À venir**, **Expirée**, avec le nombre de jours restants
  et une barre d'avancement.
- Recherche, filtres (ville, statut, remise minimum, 17 catégories), tri (% de remise, fin proche,
  économie, prix, récentes).
- Favoris, ajout / modification / suppression de promotions, partage (WhatsApp ou partage natif).
- Import / export JSON, thème clair / sombre, prix en dirhams (DH).

## Lancer l'application

```bash
cd promo-maroc
python3 -m http.server 8080
# puis ouvrir http://localhost:8080 (ou http://<ip-du-pc>:8080 depuis le téléphone)
```

Pour l'installer sur un téléphone, hébergez le dossier en HTTPS (GitHub Pages, Netlify…), ouvrez-le dans
Chrome / Safari puis « Ajouter à l'écran d'accueil ».

## Données

Les promotions marquées **Exemple** sont des données de démonstration (prix plausibles, **non vérifiés**) ;
elles peuvent être masquées dans le menu **Plus**. Les vraies promotions s'ajoutent via le bouton **＋**
ou par import JSON :

```json
[
  {
    "product": "Huile de table 5 L",
    "brand": "Lesieur",
    "store": "Marjane",
    "city": "Casablanca",
    "category": "alimentation",
    "originalPrice": 99.9,
    "promoPrice": 84.9,
    "startDate": "2026-10-01",
    "endDate": "2026-10-15",
    "source": "https://lien-du-catalogue",
    "conditions": "Dans la limite des stocks"
  }
]
```

Le pourcentage est recalculé à partir des prix. `category` prend l'un des identifiants de `data.js`
(`alimentation`, `boissons`, `hygiene`, `entretien`, `electromenager`, `high-tech`, `informatique`, `mode`,
`maison`, `bricolage`, `bebe`, `sport`, `auto`, `sante`, `telecom`, `voyage`, `autre`).

## Fichiers

| Fichier | Rôle |
|---|---|
| `index.html` | Structure de l'interface |
| `styles.css` | Styles mobiles (clair / sombre) |
| `app.js` | Logique : filtres, statuts, calculs, formulaire, stockage local |
| `data.js` | Catégories, villes, enseignes et exemples |
| `manifest.webmanifest`, `sw.js`, `icon.svg` | Installation PWA et mode hors ligne |
