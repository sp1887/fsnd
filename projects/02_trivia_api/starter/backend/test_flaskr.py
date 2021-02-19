import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'admin', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question':'Which country won the soccer World cup in 2018',
            'answer': 'France',
            'difficulty': 1,
            'category': 6
        }

        self.new_question_422 = {
            'question':'Which country won the soccer World cup in 2018',
            'answer': 'France',
            'difficulty': 1,
            'category': 'Sports'
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['categories'])

    def test_get_paginated_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])

    def test_get_paginated_questions_in_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        category = Category.query.filter(Category.id == 1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(category.format()['id'], 1)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_search_for_question_with_results(self):
        res = self.client().post('/questions', json={'searchTerm': 'soccer'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_search_questions_without_results(self):
        res = self.client().post('/questions', json={'searchTerm': 'basketball'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 0)

    def test_delete_question(self):
        new_question = Question(question="test", category=1, answer="test", difficulty=1)
        new_question.insert()
        res = self.client().delete('/questions/'+str(new_question.id))
        data = json.loads(res.data)

        deleted_question = Question.query.filter(Question.id == new_question.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], new_question.id)

    def test_get_quiz_question_without_category(self):
        res = self.client().post('/quizzes', json={'previous_questions': [1,2,3], 'quiz_category': {"id":0}})
        data = json.loads(res.data)
        question = Question.query.filter(~Question.id.in_([1,2,3])).order_by(func.random()).first()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotIn(question.id, [1,2,3])

    def test_get_quiz_question_with_category(self):
        res = self.client().post('/quizzes', json={'previous_questions': [1,2,3], 'quiz_category': {"id":1}})
        data = json.loads(res.data)
        question = Question.query.filter(~Question.id.in_([1,2,3])).filter(Question.category == 1).order_by(func.random()).first()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotIn(question.id, [1,2,3])
        self.assertEqual(question.category, 1)

    def test_405_question_creation_not_allowed(self):
        res = self.client().post('/questions/45', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method not allowed')

    def test_422_search_question(self):
        res = self.client().post('/questions', json={"search": "WorldCup"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    def test_404_search_questions_in_inexisting_category(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
