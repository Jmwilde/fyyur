import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after each test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_categories_404_response(self):
        res = self.client().get('/categorie')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 10)
    
    def test_get_questions_404_response(self):
        res = self.client().get('/question')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
    
    def test_delete_question(self):
        # Create a new question to use for deletion
        question = Question(question='What is the approximate diameter of the Earth?', answer='8000 miles', category=1, difficulty=2)
        question.insert()
        q_id = question.id

        res = self.client().delete('/questions/{}'.format(q_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    
    def test_delete_question_422_response(self):
        q_id = 1
        res = self.client().delete('/questions/{}'.format(q_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
    
    def test_create_question(self):
        req_body = {
            'question':'What is the tallest type of grass?',
            'answer':'Bamboo',
            'category':1,
            'difficulty':4
        }
        res = self.client().post('/questions', json=req_body)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_create_question_422_response(self):
        req_body = {
            'question':'What is the tallest type of grass?',
            'answer':None,
            'category':1,
            'difficulty':4
        }
        res = self.client().post('/questions', json=req_body)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
    
    def test_search_question(self):
        req_body = {
            'searchTerm':'clay'
        }
        res = self.client().post('/questions', json=req_body)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
    
    def test_create_question_search_returns_422_response(self):
        # req_body = {
        #     'searchTerm':'test'
        # }
        req_body = "test"
        res = self.client().post('/questions', json=req_body)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
    
    def test_get_questions_for_category(self):
        category_id = 1
        res = self.client().get('/categories/{}/questions'.format(category_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
    
    def test_get_questions_for_category_404_response(self):
        category_id = 1
        res = self.client().get('/categories/foo/questions?page=1000'.format(category_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
    
    def test_get_quiz_question(self):
        req_body = {
            'previous_questions':[],
            'quiz_category':{'type':'Science','id':1}
        }
        res = self.client().post('/quizzes', json=req_body)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
    
    def test_get_quiz_question_422_response(self):
        req_body = {
            'previous_questions':['foo'],
            'quiz_category':{'type':'Science','id':1}
        }
        res = self.client().post('/quizzes', json=req_body)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    


    


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()