import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

from settings import DB_NAME, DB_USER, DB_PASSWORD

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = DB_NAME
        self.database_path = "postgresql://{}:{}@{}/{}".format(DB_USER,DB_PASSWORD, 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    
    """Test GET /categories endpoint"""
    def test_get_categories_success(self):
        categories_count = len(Category.query.all())

        res = self.client().get("/categories")
        data = res.get_json()

        # Assert the response status code is 200
        self.assertEqual(res.status_code, 200)

        # Assert the response data matches the expected format
        self.assertEqual(data['success'], True)
        self.assertTrue("categories" in data)
        self.assertEqual(len(data["categories"]), categories_count)
        
    """Test GET /questions endpoint"""
    def test_get_questions_success(self):
        res = self.client().get('/questions')
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 10 if data['total_questions'] - 10 > 0 else abs(data['total_questions'] - 10))
        self.assertTrue(len(data['categories']))
        
    """Test GET /questions endpoint with an expected error"""
    def test_get_questions_error(self):

        res = self.client().get("/questions?page=-1")
        data = res.get_json()

        # Assert the response status code is the expected error code
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Invalid page number. Page number must be a positive integer.')
        self.assertEqual(res.status_code, 422)
        
    """Test GET categories/:id/questions/ endpoint"""
    def test_get_questions_per_category_success(self):
        
        res = self.client().get('/categories/1/questions')
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])
        
    """Test GET categories/:id/questions/ endpoint with an expected error"""
    def test_get_questions_per_category_error(self):

        res = self.client().get("/categories/noexist/questions")
        data = res.get_json()
          
        # Assert the response status code is the expected error code
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Invalid category ID. Category ID must be an integer.')
        self.assertEqual(res.status_code, 422)
        
    """Test POST /questions endpoint: create new question"""
    def test_create_question_success(self):
        payload = {
            'question': 'What is the capital of VN?',
            'answer': 'Hanoi',
            'category': 3,
            'difficulty': 1
        }
        res = self.client().post('/questions', json=payload)
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question created')
        
    """Test POST /questions endpoint: create new question with an expected error"""
    def test_create_question_error(self):
        payload = {
            'question': 'What is the capital of VN?',
            'answer': 'Hanoi',
            'category': 3,
        }
        res = self.client().post('/questions', json=payload)
        data = res.get_json()

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Missing required fields')
        
    """Test POST /questions endpoint: delete question"""
    def test_delete_question_success(self):
        question = Question(question='It me', answer='Mario',
                            difficulty=1, category=1)
        question.insert()
        question_id = question.id

        res = self.client().delete(f'/questions/{question_id}')
        data = res.get_json()

        question = Question.query.filter(
            Question.id == question.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question deleted')
        
    """Test POST /questions endpoint: delete question with an expected error"""
    def test_delete_question_error(self):
        res = self.client().delete('/questions/99999')
        data = res.get_json()

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Question not found')
        
    """Test GET /questions/search endpoint"""
    def test_search_questions_success(self):
        search = {'searchTerm': 'a'}
        res = self.client().post('/questions/search', json=search)
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])
        
    """Test GET /questions/search endpoint with an expected error"""
    def test_search_questions_error(self):
        search = {'searchTerm': ''}

        res = self.client().post('/questions/search', json=search)
        data = res.get_json()

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], 'Missing search term')
        
    """Test POST /quizzes endpoint"""
    def test_play_quiz_success(self):
        quiz = {
                 'previous_questions': [],
                   'quiz_category': {
                       'type': 'Entertainment', 
                       'id'  : 1
                   }
               }

        res = self.client().post('/quizzes', json=quiz)
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        
    """Test POST /quizzes endpoint with an expected error"""
    def test_play_quiz_error(self):
        
        quiz = {'previous_questions': []}
        
        res = self.client().post('/quizzes', json=quiz)
        data = res.get_json()

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Missing required fields")
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()