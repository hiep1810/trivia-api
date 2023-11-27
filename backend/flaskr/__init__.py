import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/*": {"origins": "*"}})
    
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    # Set Access-Control-Allow-Origin header for all responses
    @app.after_request
    def set_access_control(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            categories = Category.query.all()

            return jsonify({
                'success': True,
                'categories': {category.id: category.type for category in categories}
            })
        
        except Exception as e:
            abort(500, 'Failed to get categories')
            
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():
        
        page = request.args.get('page',1,type=int)
        
        if page < 1:
            abort(422, 'Invalid page number. Page number must be a positive integer.')
            
        try:
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE

            questions = Question.query.all()
            categories = Category.query.all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions][start:end],
                'total_questions': len(questions),
                'categories': {category.id: category.type for category in categories},
                'current_category': None  
            })

        except Exception as e:
            abort(500, 'Failed to get questions.')
            
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        
        if question is None:
            abort(404, 'Question not found')
        try:
            question.delete()
            
            return jsonify({
                'success': True, 
                'message': 'Question deleted',
                'question_id': question_id

            })

        except Exception as e:
            abort(500, 'Failed to delete question')

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        data = request.get_json()

        question = data.get('question')
        answer = data.get('answer')
        category = data.get('category')
        difficulty = data.get('difficulty')

        if not question \
        or not answer \
        or not category \
        or not difficulty:
            abort(422, 'Missing required fields')
        try:
            question = Question(question, answer, category, difficulty)
            question.insert()
            
            return jsonify({
                'success': True, 
                'message': 'Question created'
            })

        except Exception as e:
            abort(500, 'Failed to create question')

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():

        data = request.get_json()
        search_term = data.get('searchTerm')

        if not search_term:
              abort(422, 'Missing search term')
                
        try:    
            matching_questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
                            
            return jsonify({
                'success': True, 
                'questions': [question.format() for question in matching_questions],
                'total_questions': len(matching_questions),
                'current_category': None
            })
        except Exception as e:
            print(e)
            abort(500, 'Failed to search for questions')
            
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        if not category_id.isdigit():
            abort(422, 'Invalid category ID. Category ID must be an integer.')
        try:
            matching_questions = Question.query.filter(
                Question.category == str(category_id)).all()
                    
            return jsonify({
                'success': True, 
                'questions': [question.format() for question in matching_questions],
                'total_questions': len(matching_questions),
                'current_category': category_id
            })

        except Exception as e:
            print(e)
            abort(500, 'Failed to get questions.')
            
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()


        if not ('quiz_category' in body and 'previous_questions' in body):
            abort(422, 'Missing required fields')
            
        try:       
            category = body.get('quiz_category')

            previous_questions = body.get('previous_questions')

            query = Question.query \
                    if   category["type"] == "click" \
                    else Question.query.filter \
                         (Question.category == category['id'])

            
            if previous_questions:
                query = query.filter(Question.id.notin_(previous_questions))
            
            matching_questions = query.all()
 
            random_question = random.choice(matching_questions).format() if matching_questions else None
    
    
            return jsonify({
                'success': True,
                'question': random_question
            })
        except Exception as e:
            print(e)
            abort(500, 'Failed to get questions.')

   
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": error.description
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": error.description
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": error.description
        }), 500

    return app