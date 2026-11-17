#!/usr/bin/env python3
"""Assemble les pages du site : en-tête et pied communs autour de chaque contenu.

Usage : python3 _build/gabarit.py   (depuis la racine du dépôt)
Les contenus sont dans _build/pages/<nom>.html ; la première ligne est un bloc de réglages :
<!-- titre: ... | description: ... | menu: accueil|support|legal | robots: index -->
"""
import pathlib
import re

RACINE = pathlib.Path(__file__).resolve().parent.parent
PAGES = RACINE / "_build" / "pages"

CSP = ("default-src 'none'; img-src 'self'; style-src 'self'; "
       "base-uri 'none'; form-action 'none'")

ENTETE = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="referrer" content="no-referrer">
  <meta http-equiv="Content-Security-Policy" content="{csp}">
  <meta name="color-scheme" content="light">
  <meta name="theme-color" content="#F7EEE4">
  <meta name="robots" content="{robots}">
  <title>{titre}</title>
  <meta name="description" content="{description}">
  <meta property="og:title" content="{titre}">
  <meta property="og:description" content="{description}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://getkokon.app/{chemin}">
  <meta property="og:image" content="https://getkokon.app/assets/img/table.jpg">
  <link rel="canonical" href="https://getkokon.app/{chemin}">
  <link rel="icon" href="assets/favicon.png" type="image/png">
  <link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
  <link rel="stylesheet" href="assets/site.css">
</head>
<body>
  <a class="sr" href="#principal">Aller au contenu</a>
  <header class="entete">
    <div class="contenu">
      <a class="logo" href="./" aria-label="KOKON, accueil">
        <img src="assets/logo.png" alt="" width="34" height="34">
        <span>KOKON</span>
      </a>
      <nav class="menu" aria-label="Navigation principale">
        <a class="optionnel" href="./#fonctions">Fonctions</a>
        <a href="./#tarifs">Tarifs</a>
        <a href="support.html"{support_actif}>Aide</a>
      </nav>
    </div>
  </header>
  <main id="principal">
"""

PIED = """  </main>
  <footer class="pied">
    <div class="contenu">
      <div>
        <a class="logo" href="./" aria-label="KOKON, accueil">
          <img src="assets/logo.png" alt="" width="34" height="34">
          <span>KOKON</span>
        </a>
        <p class="accroche">L’app du foyer : planning, repas, courses et discussion de la famille, au même endroit.</p>
        <p class="accroche"><a href="mailto:contact@getkokon.app">contact@getkokon.app</a></p>
      </div>
      <div>
        <h2>KOKON</h2>
        <ul>
          <li><a href="./#fonctions">Fonctions</a></li>
          <li><a href="./#tarifs">Tarifs</a></li>
          <li><a href="support.html">Aide et contact</a></li>
          <li><a href="support.html#suppression">Supprimer son compte</a></li>
        </ul>
      </div>
      <div>
        <h2>Informations légales</h2>
        <ul>
          <li><a href="mentions-legales.html">Mentions légales</a></li>
          <li><a href="privacy.html">Confidentialité</a></li>
          <li><a href="cgu.html">Conditions d’utilisation</a></li>
          <li><a href="cgv.html">Conditions de vente</a></li>
        </ul>
      </div>
      <p class="bas">© 2026 KOKON. Sans publicité, sans traceur. Données hébergées dans l’Union européenne.</p>
    </div>
  </footer>
</body>
</html>
"""


def construire():
    for source in sorted(PAGES.glob("*.html")):
        texte = source.read_text(encoding="utf-8")
        premiere, _, corps = texte.partition("\n")
        m = re.match(r"<!--(.*)-->", premiere.strip())
        if not m:
            raise SystemExit(f"{source.name} : réglages manquants")
        reglages = dict(
            (cle.strip(), val.strip())
            for cle, val in (p.split(":", 1) for p in m.group(1).split("|"))
        )
        nom = source.name
        chemin = "" if nom == "index.html" else nom
        html = ENTETE.format(
            csp=CSP,
            robots=reglages.get("robots", "index, follow"),
            titre=reglages["titre"],
            description=reglages["description"],
            chemin=chemin,
            support_actif=' aria-current="page"' if reglages.get("menu") == "support" else "",
        ) + corps.rstrip() + "\n" + PIED
        if nom == "404.html":
            # Servie à n'importe quelle profondeur : liens absolus.
            html = re.sub(r'(href|src)="(?!https?:|mailto:|#|/)(\./)?', r'\1="/', html)
        (RACINE / nom).write_text(html, encoding="utf-8")
        print("écrit", nom)


if __name__ == "__main__":
    construire()
