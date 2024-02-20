#!/bin/bash

# Base URL for your application
BASE_URL="http://localhost:80"

echo "Running Health Check..."
curl -s "${BASE_URL}/health" | jq .

echo -e "\nFetching movies..."
curl -s "${BASE_URL}/movies" | jq .

echo -e "\nAdding a new movie..."
ADD_RESPONSE=$(curl -s -X POST "${BASE_URL}/movies" \
               -H "Content-Type: application/json" \
               -d '{"title": "Inception", "director": "Christopher Nolan", "year": "2010"}')
echo "Add response: $ADD_RESPONSE"
MOVIE_ID=$(echo $ADD_RESPONSE | jq -r '.movie_id')
echo "Movie added with ID: $MOVIE_ID"

if [ "$MOVIE_ID" == "null" ] || [ -z "$MOVIE_ID" ]; then
  echo "Failed to add movie. Exiting..."
  exit 1
fi

echo -e "\nUpdating movie with ID: $MOVIE_ID..."
UPDATE_RESPONSE=$(curl -s -X PUT "${BASE_URL}/movies/$MOVIE_ID" \
     -H "Content-Type: application/json" \
     -d '{"review": "Outstanding movie!"}')
echo "Update response: $UPDATE_RESPONSE"

echo -e "\nFetching movie by ID: $MOVIE_ID..."
curl -s "${BASE_URL}/movies/$MOVIE_ID" | jq .

echo -e "\nDeleting movie with ID: $MOVIE_ID..."
DELETE_RESPONSE=$(curl -s -X DELETE "${BASE_URL}/movies/$MOVIE_ID")
echo "Delete response: $DELETE_RESPONSE"

echo -e "\nEnd-to-End testing completed."
