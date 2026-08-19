from flask import jsonify
from flask.views import MethodView

from .database import get_all_movies, get_movie


class Movies(MethodView):
    def get(self, movie_id):
        if movie_id is None:
            # Return a list of all movies
            return jsonify({"movies": get_all_movies()})
        else:
            # Return the details of a specific movie
            movie = get_movie(movie_id)
            if movie is None:
                return jsonify({"error": "Movie not found"}), 404
            return jsonify({"movie": movie})
