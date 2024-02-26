from flask import Flask, request,jsonify, render_template, Response
import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
import psutil
#TST


# Create the app
app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()
MONGO_URL = os.getenv('MONGO_URL')
DATABASE_NAME = os.getenv('DATABASE_NAME')
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
DNS_ADDRESS = os.getenv('DNS_ADDRESS')  # Get DNS address from .env
VERSION = os.getenv('VERSION')

#######################################
############### LOGGING ###############

# Setup logging
log_level = getattr(logging, log_level)
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)
# logger.error("This is an error message")
# logger.critical("This is a critical message")

############### LOGGING ###############
#######################################
######## BEFORE/AFTER REQUESTS ########
# Middleware to log every request
@app.before_request
def log_request_info():
    logger.info('Request: %s %s', request.method, request.path)

@app.before_request
def connect_to_db():
    global client
    global db
    try:
        client = MongoClient(MONGO_URL)
        db = client.get_database(DATABASE_NAME)  # Specify your database name here
        logger.info(f"Database name: {MONGO_URL}")
        logger.info(f"Connected to MongoDB" )
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")

# Close the database connection after each request
@app.teardown_request
def teardown_request(exception):
    try:
        if client:
            client.close()
            logger.info("Disconnected from MongoDB")
    except Exception as e:
        logger.error(f"Error while disconnecting from MongoDB: {e}")

######## BEFORE/AFTER REQUESTS ########
#######################################
############### API CALLS #############

@app.route('/')
def index():
    return render_template('index.html', DNS_ADDRESS=DNS_ADDRESS,VERSION=VERSION)

@app.route('/movies', methods=['GET', 'POST'])
def get_movies():
    try:

        if request.method == 'POST':
            movie_data = request.json
            result = db.movies.insert_one(movie_data)
            return jsonify({"message": "Movie added successfully", "movie_id": str(result.inserted_id)}), 201
        elif request.method == 'GET':
            movies_collection = db.movies
            movies = list(movies_collection.find({}))
            for movie in movies:
                movie['_id'] = str(movie['_id'])
            return jsonify(movies)
        else:
            return jsonify({"error": "Unsupported HTTP method"}), 405

    except Exception as e:
        logger.error(f"Failed to retrieve movies from the database: {e}")
        return jsonify({"error": "Failed to retrieve movies from the database"}), 500

@app.route('/movies/<string:movie_id>', methods=['PUT'])
def add_review_to_movie(movie_id):
    try:
        movie_id = ObjectId(movie_id)
        # Retrieve the movie document by ID
        movies_collection = db.movies
        movie = movies_collection.find_one({"_id": ObjectId(movie_id)})
        if not movie:
            return jsonify({"error": "Movie not found"}), 404
        new_review = request.json.get('review')
        movie['reviews'].append(new_review)

        # Update the movie document in the database
        result = movies_collection.replace_one({"_id": ObjectId(movie_id)}, movie)
        if result.modified_count == 1:
            movie['_id'] = str(movie['_id'])
            return jsonify({"message": "Review added successfully", "movie": movie}), 200
        else:
            return jsonify({"error": "Failed to update movie"}), 500

    except Exception as e:
        logger.error(f"Failed to add review to movie: {e}")
        return jsonify({"error": "Failed to add review to movie"}), 500

@app.route('/movies/<string:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    try:
        movie_id = ObjectId(movie_id)
        # Retrieve the movie document by ID
        movies_collection = db.movies
        movie = movies_collection.find_one({"_id": movie_id})
        if not movie:
            return jsonify({"error": "Movie not found"}), 404

        # Delete the movie document from the database
        result = movies_collection.delete_one({"_id": movie_id})
        if result.deleted_count == 1:
            # Convert ObjectId to string for JSON serialization
            movie['_id'] = str(movie['_id'])
            return jsonify({"message": "Movie deleted successfully", "movie": movie}), 200
        else:
            return jsonify({"error": "Failed to delete movie"}), 500

    except Exception as e:
        logger.error(f"Failed to delete movie: {e}")
        return jsonify({"error": "Failed to delete movie"}), 500

@app.route('/movies/<string:movie_id>', methods=['GET'])
def get_movie(movie_id):
    try:
        movie_id = ObjectId(movie_id)
        # Retrieve the movie document by ID
        movies_collection = db.movies
        movie = movies_collection.find_one({"_id": movie_id})
        if not movie:
            return jsonify({"error": "Movie not found"}), 404

        # Convert ObjectId to string for JSON serialization
        movie['_id'] = str(movie['_id'])
        return jsonify(movie), 200

    except Exception as e:
        logger.error(f"Failed to retrieve movie: {e}")
        return jsonify({"error": "Failed to retrieve movie"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Check if the database is reachable
        db.command('ping')

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "error"}), 500

@app.route('/metrics')
def get_metrics():
    try:
        # Gather some metrics
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent

        # Construct a string with the metrics in Prometheus exposition format
        prometheus_metrics = f"# HELP cpu_usage Percentage of CPU usage\n# TYPE cpu_usage gauge\ncpu_usage {cpu_usage}\n\n# HELP memory_usage Percentage of memory usage\n# TYPE memory_usage gauge\nmemory_usage {memory_usage}\n"

        # Return the metrics as a response with content type text/plain
        return Response(prometheus_metrics, mimetype='text/plain')

    except Exception as e:
        return jsonify({"error": str(e)}), 500


############### API CALLS ##############
########################################

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7070, debug=True)

