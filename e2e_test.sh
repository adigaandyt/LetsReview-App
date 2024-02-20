#!/bin/bash

# Base URL for your application
BASE_URL="http://nginx:80"

curl -s "${BASE_URL}/health"
curl -s "${BASE_URL}/movies"
curl -X POST ${BASE_URL}/movies -H "Content-Type: application/json" -d '{"title": 123456}'
POST_RESPONSE=$(curl -X POST ${BASE_URL}/movies -H "Content-Type: application/json" -d '{"title": 123456}')
echo $POST_RESPONSE
MOVIE_ID=$(echo "$POST_RESPONSE" | jq -r '.movie_id')
curl -X PUT ${BASE_URL}/movies/${MOVIE_ID} -H "Content-Type: application/json" -d '{"reviews": ["new review"]}'
curl -X DELETE ${BASE_URL}/movies/${MOVIE_ID} 