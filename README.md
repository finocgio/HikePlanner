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

## Bonusthema ähnliche Wanderrouten UI/Backend

Im Rahmen des ersten Bonusthemas wurde die Applikation im Bereich **UI / Backend** erweitert. Neben der reinen Vorhersage der Wanderzeit zeigt die Anwendung nun zusätzlich **ähnliche reale Wanderungen** an.

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

## Bonusthema Random Forest Training und Modell

Im Rahmen des zweiten Bonusthemas wurde die Applikation im Bereich **Training / Modell** erweitert. Neben den bestehenden Modellen wurde zusätzlich ein **Random-Forest-Modell** integriert, um die Vorhersage der Wanderzeit weiter zu verbessern.

Dafür wurde das bestehende **Modelltraining** erweitert, sodass ein weiteres Machine-Learning-Modell auf Basis der vorhandenen Trainingsdaten berechnet wird. Das Random-Forest-Modell kombiniert mehrere Entscheidungsbäume und ermöglicht dadurch robustere und genauere Vorhersagen im Vergleich zu einfacheren Modellen.

Die verschiedenen Modelle werden anhand von Kennzahlen wie dem **Bestimmtheitsmass R²** und dem **Mean Squared Error (MSE)** bewertet. Dadurch kann die Qualität der Modelle nachvollzogen und miteinander verglichen werden. Die Auswertung zeigt, dass das Random-Forest-Modell eine höhere Genauigkeit erreicht und somit eine sinnvolle Erweiterung darstellt.

Die berechneten Resultate werden anschliessend über die API an das **Frontend** übergeben und dort gemeinsam mit den anderen Modellen dargestellt. Benutzer erhalten dadurch mehrere Vorhersagen und können diese direkt vergleichen.

### Technische Umsetzung

* Erweiterung des Trainingsscripts um ein zusätzliches Modell (`RandomForestRegressor`)
* Training des Modells auf den bestehenden Features:

  * `downhill`
  * `uphill`
  * `length_3d`
  * `max_elevation`
* Evaluation des Modells anhand von:

  * R² (Bestimmtheitsmass)
  * MSE (Mean Squared Error)
* Speicherung des Modells als `RandomForestRegressor.pkl`
* Erweiterung des API-Endpunkts `/api/predict` um das Feld `random_forest`
* Anpassung des Svelte-Frontends zur Darstellung der zusätzlichen Modellvorhersage

### Mehrwert

* verbesserte Modellgenauigkeit durch zusätzliches Machine-Learning-Modell
* Vergleichbarkeit verschiedener Modellansätze
* bessere Nachvollziehbarkeit der Vorhersagen
* sinnvolle Erweiterung des bestehenden Trainingsprozesses
