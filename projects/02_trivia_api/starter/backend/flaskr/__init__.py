import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/*": {"origins": "*"}}, send_wildcard=True)


  QUESTIONS_PER_PAGE = 10

  def paginate_questions(request, selection):
      page = request.args.get('page', 1, type=int)
      start = (page - 1) * QUESTIONS_PER_PAGE
      end = start + QUESTIONS_PER_PAGE

      questions = [question.format() for question in selection]
      current_questions = questions[start:end]

      return current_questions

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
      response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
      return response

  '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
  @app.route('/categories')
  def get_all_categories():
      categories = Category.query.all()
      formated_categories = {category.id: category.type for category in categories}

      return jsonify({
        'success': True,
        'categories': formated_categories,
        'total_categories': len(formated_categories)
      })

  '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.
  '''
  @app.route('/questions')
  def get_paginated_questions():
      questions_selection = Question.query.order_by(Question.id).all()
      categories_selection = Category.query.order_by(Category.id).all()

      questions = paginate_questions(request, questions_selection)
      categories = {category.id: category.type for category in categories_selection}

      return jsonify({
        'success': True,
        'questions': questions,
        'total_questions': len(questions_selection),
        'current_category': None,
        'categories': categories,
      })

  '''
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''

  '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
      try:
          question = Question.query.filter(Question.id == question_id).one_or_none()
          if question is None:
              abort(404)

          question.delete()

          return jsonify({
            'success': True,
            'deleted': question_id,
          })
      except:
          abort(404)
  '''
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''

  '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
      body = request.get_json()

      new_question = body.get('question', None)
      new_answer = body.get('answer', None)
      new_category = body.get('category', None)
      new_difficulty = body.get('difficulty', None)
      search_term = body.get('searchTerm', None)

      try:
          if search_term is None:
              if new_question is None:
                  abort(422)
              question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
              question.insert()

              selection = Question.query.order_by(Question.id).all()
              current_selection = paginate_questions(request, selection)

              return jsonify({
                'success': True,
                'created': question.id,
              })
          else:
              search_results = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search_term))).all()

              return jsonify({
                'success': True,
                'total_questions': len(search_results),
                'questions': [question.format() for question in search_results]
              })
      except:
          abort(422)
  '''
  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''

  '''
  @TODO:
  Create a GET endpoint to get questions based on category.
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_in_category(category_id):
      current_category = Category.query.filter(Category.id == category_id).one_or_none()

      if current_category is None:
          abort(404)

      questions_selection = Question.query.order_by(Question.id).filter(Question.category == category_id).all()
      questions = paginate_questions(request, questions_selection)

      return jsonify({
        'success': True,
        'questions': questions,
        'total_questions': len(questions_selection),
        'current_category': current_category.type
      })

  '''
  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''


  '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.
  '''

  @app.route('/quizzes', methods=['POST'])
  def show_quiz_question():
    body = request.get_json()
    previous_questions = body.get('previous_questions', None)
    quiz_category = body.get('quiz_category', None)
    try:
        if quiz_category['id'] != 0:
            question = Question.query.filter(Question.category == quiz_category['id']).filter(~Question.id.in_(previous_questions)).order_by(func.random()).first()
        else:
            question = Question.query.filter(~Question.id.in_(previous_questions)).order_by(func.random()).first()
        if question is not None:
            return jsonify({
              'success': True,
              'question': {'question':question.question, 'id':question.id, 'answer': question.answer}
            })
        else:
            return jsonify({
              'success': True,
              'question': False
            })
    except:
        abort(404)

  '''
  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''

  '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
  @app.errorhandler(400)
  def not_found(error):
      return jsonify({
          "success": False,
          "error": 400,
          "message": "Bad Request"
      }), 400


  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": "Not Found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "Unprocessable"
      }), 422

  @app.errorhandler(405)
  def not_allowed(error):
      return jsonify({
          "success": False,
          "error": 405,
          "message": "Method not allowed"
      }), 405

  @app.errorhandler(500)
  def server_error(error):
      return jsonify({
          "success": False,
          "error": 500,
          "message": "Internal Server Error"
      }), 500

  return app
