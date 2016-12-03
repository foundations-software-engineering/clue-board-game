# Clue-Less the Board Game

This repository is for the Johns Hopkins University course "Foundations of Software Engineering", 605.401.

## Members
* Jerrold Vincent
* Keith Chason
* Rebecca Friedman
* Greg Hilston

## Project Description

An excerpt from the file "doc/Clue-Less.pdf"

"This game is a simplified version of the popular board game, Clue®. The main simplification is in the navigation of the game board. In Clue-Less there are the same nine rooms, six weapons, and six people as in the board game. The rules are pretty much the same except for moving from room to room..."

## Technologies Used

Software Unchained has decided to create a web application using the following technologies

* Django - Web framework
* Postgres - Database
* Javascript - Client side
* Docker - Simplifies and maintains a similar work environment amongst the development team

## Installation
**Ensure settings_secret.py is in the "clueless" directory**

*For Linux/Windows installation*
*Note I followed the following link's instructions except for the following changes*
* edit Dockerfile
  * from "FROM python:2.7" to "FROM python:3.6"
* Changed creation of Django project
  * from "$ docker-compose run web django-admin.py startproject composeexample ." to "$ docker-compose run web django-admin.py startproject clueless ."
  * for windows, run the following command instead (add -d flag): "$ docker-compose run -d web django-admin.py startproject clueless"
* Visited http://localhost:8000/ to see if everything was successful

The guide I followed can be found [here](https://docs.docker.com/compose/django/) .

*For Mac OSX installation*
Mac needs to be installed using docker machine, and can be installed using the following guide.
* If installing a local instance follow steps 1-9
* If installing  using this repository: follow steps 1-3,  and then step 9 when in the repo project directory
Mac OSX guide is [here](https://howchoo.com/g/y2y1mtkznda/getting-started-with-docker-compose-and-django) .

## First Time Setup
Build script to migrate to database and migrate.

**Run these two whenever models.py is updated**

`$ docker-compose run web python manage.py makemigrations clueless`

`$ docker-compose run web python manage.py migrate`

Setup default objects

`$ docker-compose run web python manage.py create_default_objects`

Create a super user

`$ docker-compose run web python manage.py createsuperuser`

## Running
Simply execute `$ ./run.sh`

## Stopping
To gracefully stop, a single `CTRL + C` command should be executed  

## Basic Docker Commands

See `$ docker --help`

### Start up a container and connect to it
`# docker run -it <containerIdOrName> bash`

### Connect to a running container
`# docker exec -it <containerIdOrName> bash`

## Setting up Project for the first time....
Build script to migrate to database and migrate.  Run these two whenever models.py is updated

`docker-compose run web python manage.py makemigrations clueless`

`docker-compose run web python manage.py migrate`

Setup default objects

`docker-compose run web python manage.py create_default_objects`

Create a super user

`docker-compose run web python manage.py createsuperuser`
