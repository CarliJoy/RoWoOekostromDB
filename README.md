<p align="center">
<a href="https://github.com/CarliJoy/RoWoOekostromDB/blob/master/README.md"><img alt="License: MIT" src="https://black.readthedocs.io/en/stable/_static/license.svg"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

# Status
This software is currently **Alpha** and actively developed.

#  Abstract
This is the repository for the 
[Robin Wood Renewable Electric Energy Provider Report](https://www.robinwood.de/oekostromreport/).
It contains a Django application that is responsible for handling the information 
needed to create this report and keep the information up to date.
As this Report and the containing information are relevant mostly Germany 
the following documentation is in German
only.

# Development

- Ensure `docker`, `docker-compose`, `docker buildx` and `pre-commit` are installed.
  - Under ubuntu `sudo apt-get install docker-buildx docker-compose pre-commit` 
- clone and cd to the project root 
- Create a `.env` file running `python oekostrom_db/generate_env.py`
- Create the docker containers running `COMPOSE_DOCKER_CLI_BUILD=1 docker-compose build`
- Simply run `docker-compose up dev` to get a working development installation running under `http://127.0.0.1:8001`
  

# Einführung
Dieses git repro beinhaltet die Datenbank zur Verwaltung der Daten aus dem 
[Robin Wood Ökostrom Report](https://www.robinwood.de/oekostromreport/).
Es handelt sich um eine Django Application.

Ziel ist künftige Anbieterrecherchen zu erleichtern und die aktuelle
Recherche besser zu dokumentieren, in dem z.B. PDF der Stromkennzeichnung
automatisiert gespeichert wird und automatisiert ermittelt ob die Seiten 
mit Stromkennzeichnungen noch erreichbar sind.

Dieses Tool soll später die Daten für die 
[Anbietersuche](https://github.com/Datenschule/oekostromreport-data/)
bereitstellen.
Dies Tool bearbeitet die Daten, so dass es am Ende für das 
[Drupal Modul](https://github.com/Robin-Wood/rowo-drupal-module) der Robin Wood
Homepage zum Ökostromreport bereitsteht.
