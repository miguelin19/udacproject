import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from random import random,choice

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1)* QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  questions = [question.format() for question in selection]
  current_questions = questions[start:end]
  return current_questions

def create_app(test_config=None):
  # create and configure the app
  db = SQLAlchemy()
  app = Flask(__name__)
  setup_db(app)
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources = {r'/*' : {'origins': '*'}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    cat = Category.query.all()
    categories = {}
    for category in cat:
      categories[category.id]=category.type
    return jsonify({
      'success' : True,
      'categories' : categories,
      'total_categories': len(cat)
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    questions = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request,questions)
    if len(current_questions)== 0:
      abort(404)
    
    cat = Category.query.all()
    categories = {}
    for category in cat:
      categories[category.id]=category.type
    return jsonify({
      'success':True, 
      'questions' : current_questions,
      'total_questions' : len(questions),
      'categories':categories,
      'current_category': None
      })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>',methods = ['DELETE'])
  def delete_question(question_id):
      question = Question.query.filter(Question.id==question_id).all()
      if len(question)==0:
        abort(404)
      else:
        try:
          question.delete()
          selection = Question.query.order_by(Question.id).all()
          current_questions = paginate_questions(request,selection)
          return jsonify({
            'success':True,
            'deleted':question_id,
            'questions': current_questions,
            'total_questions': len(selection)
          })
        except:
          abort(422)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.
  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods =['POST'])
  def create_question():
    body = request.get_json()

    n_question = body.get('question',None)
    n_answer = body.get('answer',None)
    n_category = body.get('category',None)
    n_difficulty = body.get('difficulty',None)

    try:
      question = Question(question=n_question, answer=n_answer, category=n_category, difficulty=n_difficulty)
      question.insert()

      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request,selection)
      return jsonify({
        'success':True,
        'created': question.id,
        'questions': current_questions,
        'total_questions' : len(selection)
        })
    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 
  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    search = request.args.get('search',' ', type=str)
    search_term = "%{}%".format(search)
    results = Question.query.filter(Question.question.ilike(search_term)).all()
    current_results = paginate_questions(request,results)
    return jsonify({
      'success':True,
      'total_questions':len(results),
      'questions':current_results,
      'current_category':None
    })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 
  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:cat_id>/questions')
  def questions_in_category(cat_id):
    category_exists = Category.query.filter(Category.id==str(cat_id)).all()
    if len(category_exists)==0:
      abort(404)
    else:
      results = Question.query.filter(Question.category == cat_id).all()
      current_results = paginate_questions(request, results)
      return jsonify({
        'success':True,
        'questions':current_results,
        'total_questions':len(results),
        'current_category': cat_id
      })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 
  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods =['POST'])
  def play_game():
    body = request.get_json()
    previous_questions = body.get('previous_questions',None)
    quiz_category = body.get('quiz_category', None)
    cat_id = quiz_category['id']
    if cat_id == 0:
      questions = Question.query.all()
    else:
      questions = Question.query.filter(Question.category==cat_id)
    possible_questions=[question for question in questions if question.id not in previous_questions]
    if possible_questions == []:
      return jsonify({
      'success':False,
      'question': None
      })
    selec_question = choice(possible_questions).format()
    return jsonify({
      'success':True,
      'question': selec_question
      })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
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

    