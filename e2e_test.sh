#!/bin/bash

# Base URL for your application
BASE_URL="http://nginx:80"

curl -s "${BASE_URL}/health"
curl -s "${BASE_URL}/movies"
curl -X POST ${BASE_URL}/movies -H "Content-Type: application/json" -d '{"title": 123456}'