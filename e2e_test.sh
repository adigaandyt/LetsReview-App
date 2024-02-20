#!/bin/bash

# Base URL for your application
BASE_URL="http://localhost:80"

curl -X POST ${BASE_URL}/health

curl -X POST ${BASE_URL}/movies
   -H "Content-Type: application/json"
   -d '{"title": 123456}'  