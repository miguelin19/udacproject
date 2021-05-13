import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from models import Actor, Movie, Casting
from auth import AuthError, requires_auth

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  CORS(app)

  # 'GET' endpoints
  @app.route('/movies')
  def get_movies():
    movies = Movie.query.all()
    return jsonify({
      'success' : True,
      'movies' : [movie.info() for movie in movies],
      'total_movies' : len(movies)
    }), 200

  @app.route('/actors')
  def get_actors():
    actors = Actor.query.all()
    return jsonify({
      'success' : True,
      'actors' : [actor.info() for actor in actors],
      'total_actors' : len(actors)
    }), 200

  # 'POST' endpoints
  @app.route('/movies', methods = ['POST'])
  @requires_auth('post:movies')
  def post_movie(payload):
    data = request.get_json()
    movie_title = data['title']
    movie_release_date = data['release_date']

    try:
      new_movie = Movie(title=movie_title, release_date=movie_release_date)
      new_movie.insert()
      movies = Movie.query.all()
      return jsonify({
        'success' : True,
        'movies' : [movie.info() for movie in movies],
        'total_movies' : len(movies)
      }), 200

    except:
      abort(422)
  
  @app.route('/actors', methods = ['POST'])
  @requires_auth('post:actors')
  def post_movie(payload):
    data = request.get_json()
    actor_name = data['name']
    actor_age = data['age']
    actor_gender = data['gender']

    try:
      new_actor = Actor(name=actor_name, age=actor_age, gender=actor_gender)
      new_actor.insert()
      actors = Actor.query.all()
      return jsonify({
        'success' : True,
        'movies' : [actor.info() for actor in actors],
        'total_movies' : len(actors)
      }), 200

    except:
      abort(422)
  
  # 'PATCH' endpoints
  @app.route('/movies/<int:id>', methods=['PATCH'])
  @requires_auth('patch:movies')
  def patch_movie(payload,id):
    data = request.json()
    movie = Movie.query.get(id)
    if movie == None:
      abort(404)
    else:
      try:
        if data['title']:
          movie.title = data['title']
        if data['release_date']:
          movie.release_date = data['release_date']
        movie.update()
      except:
        abort(422)
      return jsonify({
        'success' : True,
        'movie' : movie.info()
      }), 200
  
  @app.route('/actors/<int:id>',methods=['PATCH'])
  @requires_auth('patch:actors')
  def patch_actor(payload,id):
    data = request.get_json()
    actor = Actor.query.get(id)
    if actor == None:
      abort(404)
    else:
      try:
        if data['name']:
          actor.name = data['name']
        if data['age']:
          actor.age = data['age']
        if data['gender']:
          actor.gender = data['gender']
        actor.update()
      except:
        abort(422)
      return jsonify({
        'success': True,
        'actor' : actor.info()
      }), 200

  # 'DELETE' endpoints
  @app.route('/movies/<int:id>', methods=['DELETE'])
  @requires_auth('delete:movies')
  def delete_movie(payload,id):
    movie = Movie.query.get(id)
    if movie == None:
      abort(404)
    else:
      try:
        movie.delete()
      except:
        abort(422)
      return jsonify({
        'success' : True,
        'deleted_movie_id' : id
      }), 200
  
  @app.route('/actors/<int:id>', methods=['DELETE'])
  @requires_auth('delete:actors')
  def delete_actor(payload,id):
    actor = Actor.query.get(id)
    if actor == None:
      abort(404)
    else:
      try:
        actor.delete()
      except:
        abort(422)
      return jsonify({
        'success' : True,
        'deleted_actor_id' : id
      }), 200

  # Error handlers
  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False, 
          "error": 400,
          "message": "Bad request"
          }), 400
          
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False, 
          "error": 404,
          "message": "Not found"
          }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
        }), 422

  @app.errorhandler(405)
  def method_not_allowed(error):
      return jsonify({
        "success": False, 
        "error": 405,
        "message": "method not allowed"
        }), 405

  @app.errorhandler(500)
  def internal_server_error(error):
      return jsonify({
        "success": False, 
        "error": 500,
        "message": "internal server error"
        }), 500

  return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)