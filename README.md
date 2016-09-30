# Clue-Less the Board Game

This repository is for the Johns Hopkins University course "Foundations of Software Enginerring", 605.401.

## Members
* Jerrold Vincent
* Keith Chason
* Rebecca Friedman
* Greg Hilston

## Project Description

An excerpt from the file "Clue-Less.pdf"

"This game is a simplified version of the popular board game, Clue®. The main simplification is
in the navigation of the game board. In Clue-Less there are the same nine rooms, six weapons,
and six people as in the board game. The rules are pretty much the same except for moving from room to room..."

## Technologies Used

Software Unchained has decided to create a web application using the following technologies

* Django - Web framework
* Postgres - Database
* Javascript - Client side (Framework not yet determined)
* Docker - Simply and maintain a similar work environment amongst the development team

## Installation

*Note I followed the following link's instructions except for the following changes*
* edit Dockerfile
  * from "FROM python:2.7" to "FROM python:3.6"
* Changed creation of Django project
  * from "$ docker-compose run web django-admin.py startproject composeexample ." to "$ docker-compose run web django-admin.py startproject clueless ."

The guide I followed can be found [here](https://docs.docker.com/compose/django/) .
