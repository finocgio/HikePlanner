# HikePlanner

inspired by https://blog.mimacom.com/data-collection-scrapy-hiketime-prediction/
similar dataset 

## Data

* https://www.kaggle.com/datasets/roccoli/gpx-hike-tracks

## Azure Blob Storage

* Save model to Azure Blob Storage
* Always save new version of model
* Zugriff: Speicherkonto > Zugriffsschlüssel
    * Als Umgebungsvariable für Docker
    * Als Secret für GitHub

## GitHub Action

* Scrape
* Load data to MongoDB (Azure Cosmos DB)
* Update model and save to Azure Blob Storage

## App
* Backend: Python Flask (backend/app.py)
* Frontend: SvelteKit (build still manually)

## Deployment with Docker

* Dockerfile
* Install dependencies with pip
* Copy Frontend (prebuilt, TODO Build)
* Azure Blob Storage: Zugriffsschlüssel als Umgebungsvariable

## Installation

* pyenv local 3.13.7
* uv venv .venv
* uv sync

## Bonusthema

Im Rahmen des zweiten Bonusthemas wurde die Applikation im Bereich **UI / Backend** erweitert. Neben der reinen Vorhersage der Wanderzeit zeigt die Anwendung nun zusätzlich **ähnliche reale Wanderungen** an.

Dafür wurde das **Backend** so erweitert, dass bei jeder Anfrage an die Vorhersage-API zusätzlich passende Wanderrouten aus der bestehenden **Azure MongoDB** gesucht werden. Die Ähnlichkeit wird über einen einfachen **Similarity Score** berechnet. Dabei werden vor allem die Merkmale **Distanz**, **Aufstieg** und **Abstieg** berücksichtigt. Je kleiner der berechnete Score, desto ähnlicher ist eine gespeicherte Wanderung zur aktuellen Benutzereingabe.

Die gefundenen Resultate werden anschliessend über die API an das **Frontend** übergeben und dort übersichtlich dargestellt. Benutzer erhalten dadurch nicht nur eine geschätzte Dauer, sondern auch konkrete Vergleichswerte aus realen Wanderdaten. Das verbessert die Nachvollziehbarkeit und den praktischen Nutzen der Anwendung.

### Technische Umsetzung

* Erweiterung des Flask-Backends um eine MongoDB-Abfrage auf der bestehenden `tracks`-Collection
* Berechnung eines Similarity Scores auf Basis von:

  * `length_3d`
  * `uphill`
  * `downhill`
* Erweiterung des API-Endpunkts `/api/predict` um das Feld `similar_hikes`
* Anpassung des Svelte-Frontends zur Darstellung der gefundenen ähnlichen Wanderungen in Tabellenform

### Mehrwert

* bessere Benutzerführung
* realitätsnähere Einordnung der Vorhersage
* sichtbare Erweiterung in **Backend und Frontend**
* sinnvoller Einsatz der bereits vorhandenen MongoDB-Datenbasis

