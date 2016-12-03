#!/bin/bash

# Builds the newest containers and if that succeeds, starts them
docker-compose build  && docker-compose up
