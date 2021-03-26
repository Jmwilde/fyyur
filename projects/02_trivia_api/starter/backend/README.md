# Backend - Full Stack Trivia API 

### Installing Dependencies for the Backend

1. **Python 3.7** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)


2. **Virtual Enviornment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)


3. **PIP Dependencies** - Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:
```bash
pip install -r requirements.txt
```
This will install all of the required packages we selected within the `requirements.txt` file.


4. **Key Dependencies**
 - [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

 - [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

 - [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

### Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

### Running the server

From within the `./src` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

## ToDo Tasks
These are the files you'd want to edit in the backend:

1. *./backend/flaskr/`__init__.py`*
2. *./backend/test_flaskr.py*


One note before you delve into your tasks: for each endpoint, you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 


2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 


3. Create an endpoint to handle GET requests for all available categories. 


4. Create an endpoint to DELETE question using a question ID. 


5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 


6. Create a POST endpoint to get questions based on category. 


7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 


8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 


9. Create error handlers for all expected errors including 400, 404, 422 and 500. 


## Endpoints

`BASE URL: http://localhost:5000`

The available resources for the API are questions, categories, and quizzes.  
The following HTTP methods are supported: GET, POST, DELETE.  

- `GET /categories`
- `GET /questions`
- `DELETE /questions/<question_id>`
- `POST /questions`
- `GET /categories/<category_id>/questions`
- `POST /quizzes`


### GET /categories
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Parameters:
    - `None`
- Returns:
    - An object with a single key, categories, that contains a object of id: category_string key:value pairs.

```
curl http://localhost:5000/categories


{
  "categories": {
    "1": "Science", 
    "2": "Art", 
    "3": "Geography", 
    "4": "History", 
    "5": "Entertainment",  
    "6": "Sports"
  }, 
  "success": true
}
```

### GET /questions
- Fetches a dictionary with the key "questions" which contains a paginated list of question objects. Each question object has question, answer, category, difficulty, and id fields. The response dictionary also yields all categories and the total number of question objects in the database.
- Parameters:
    - `None`
- Returns:
    - An object with a single key, categories, that contains a object of id: category_string key:value pairs.

```
curl http://localhost:5000/questions


{
  "categories": {
    "1": "Science", 
    "2": "Art", 
    "3": "Geography", 
    "4": "History", 
    "5": "Entertainment", 
    "6": "Sports"
  }, 
  "current_category": 4, 
  "questions": [
    {
      "answer": "Maya Angelou", 
      "category": 4, 
      "difficulty": 2, 
      "id": 5, 
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
    }, 
    {
      "answer": "Muhammad Ali", 
      "category": 4, 
      "difficulty": 1, 
      "id": 9, 
      "question": "What boxer's original name is Cassius Clay?"
    }, 
    {
      "answer": "Apollo 13", 
      "category": 5, 
      "difficulty": 4, 
      "id": 2, 
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    }
  ], 
  "success": true, 
  "total_questions": 3
}
```

### DELETE /questions/<question_id>
- Deletes the question object with the given id.
- Parameters:
    - `question_id: integer`
- Returns:
    - An object with a single key "success" with a boolean value.

```
curl -X DELETE http://localhost:5000/questions/1

{
  "success": true,
  "message": "Question successfully deleted."
}
```

### POST /questions
- Creates a new question object or performs a case insensitive search for any questions containing a search term.
- Parameters:
    - `question: string`  
    - `answer: string`  
    - `category: integer (optional)`  
    - `difficulty: integer (optional)` 
- Returns:
    - An object with a single key "success" with a boolean value.
    - When the "searchTerm" parameter is specified a list of question objects is returned that contain the term within their respective question fields. 

```
curl -X POST -H "Content-Type: application/json" -d '{"question":"What is the approximate diameter of the Earth?", "answer":"8000 miles", "category":1, "difficulty":2}' http://localhost:5000/questions

{
  "success": true,
  "message": "Question successfully created."
}
```

Search variant
```
curl -X POST -H "Content-Type: application/json" -d '{"searchTerm":"clay"}' http://localhost:5000/questions

{
  "current_category": 4, 
  "questions": [
    {
      "answer": "Muhammad Ali", 
      "category": 4, 
      "difficulty": 1, 
      "id": 9, 
      "question": "What boxer's original name is Cassius Clay?"
    }
  ], 
  "success": true, 
  "total_questions": 1
}
```

### GET /categories/<category_id>/questions
- Fetches a paginated list of question objects that all belong to the specified category.
- Parameters:
    - `category_id: integer`
- Returns:
    - A paginated list of question objects. Also returns the current category and the total number of questions that belong to the specified category.

```
curl http://localhost:5000/categories/1/questions?page=1

{
  "current_category": 1, 
  "questions": [
    {
      "answer": "The Liver", 
      "category": 1, 
      "difficulty": 4, 
      "id": 20, 
      "question": "What is the heaviest organ in the human body?"
    }, 
    {
      "answer": "Alexander Fleming", 
      "category": 1, 
      "difficulty": 3, 
      "id": 21, 
      "question": "Who discovered penicillin?"
    }, 
    {
      "answer": "Blood", 
      "category": 1, 
      "difficulty": 4, 
      "id": 22, 
      "question": "Hematology is a branch of medicine involving the study of what?"
    }, 
    {
      "answer": "8000 miles", 
      "category": 1, 
      "difficulty": 2, 
      "id": 25, 
      "question": "What is the approximate diameter of the Earth?"
    }
  ], 
  "success": true, 
  "total_questions": 4
}

```

### POST /quizzes
- Fetches the next question object for the trivia quiz. This is a randomly selected question that is not found in the specified previous questions list parameter.
- Parameters:
    - `quiz_category: integer (optional)`
    - `previous_questions: list: integer (optional)`
- Returns:
    - A boolean success value and a single question object.

```
curl -X POST -H "Content-Type: application/json" -d '{"previous_questions":[], "quiz_category":{"type":"Science","id":"1"}}' http://localhost:5000/quizzes

{
  "question": {
    "answer": "Blood", 
    "category": 1, 
    "difficulty": 4, 
    "id": 22, 
    "question": "Hematology is a branch of medicine involving the study of what?"
  }, 
  "success": true
}
```
curl http://localhost:5000/categories


{
  "categories": {
    "1": "Science", 
    "2": "Art", 
    "3": "Geography", 
    "4": "History", 
    "5": "Entertainment",  
    "6": "Sports"
  }, 
  "success": true
}
```

### GET /questions
- Fetches a dictionary with the key "questions" which contains a paginated list of question objects. Each question object has question, answer, category, difficulty, and id fields. The response dictionary also yields all categories and the total number of question objects in the database.
- Parameters:
    - `None`
- Returns:
    - An object with a single key, categories, that contains a object of id: category_string key:value pairs.

```
curl http://localhost:5000/questions


{
  "categories": {
    "1": "Science", 
    "2": "Art", 
    "3": "Geography", 
    "4": "History", 
    "5": "Entertainment", 
    "6": "Sports"
  }, 
  "current_category": 4, 
  "questions": [
    {
      "answer": "Maya Angelou", 
      "category": 4, 
      "difficulty": 2, 
      "id": 5, 
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
    }, 
    {
      "answer": "Muhammad Ali", 
      "category": 4, 
      "difficulty": 1, 
      "id": 9, 
      "question": "What boxer's original name is Cassius Clay?"
    }, 
    {
      "answer": "Apollo 13", 
      "category": 5, 
      "difficulty": 4, 
      "id": 2, 
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    }
  ], 
  "success": true, 
  "total_questions": 3
}
```

### DELETE /questions/<question_id>
- Deletes the question object with the given id.
- Parameters:
    - `question_id: integer`
- Returns:
    - An object with a single key "success" with a boolean value.

```
curl -X DELETE http://localhost:5000/questions/1

{
  "success": true,
  "message": "Question successfully deleted."
}
```

### POST /questions
- Creates a new question object or performs a case insensitive search for any questions containing a search term.
- Parameters:
    - `question: string`  
    - `answer: string`  
    - `category: integer (optional)`  
    - `difficulty: integer (optional)` 
- Returns:
    - An object with a single key "success" with a boolean value.
    - When the "searchTerm" parameter is specified a list of question objects is returned that contain the term within their respective question fields. 

```
curl -X POST -H "Content-Type: application/json" -d '{"question":"What is the approximate diameter of the Earth?", "answer":"8000 miles", "category":1, "difficulty":2}' http://localhost:5000/questions

{
  "success": true,
  "message": "Question successfully created."
}
```

Search variant
```
curl -X POST -H "Content-Type: application/json" -d '{"searchTerm":"clay"}' http://localhost:5000/questions

{
  "current_category": 4, 
  "questions": [
    {
      "answer": "Muhammad Ali", 
      "category": 4, 
      "difficulty": 1, 
      "id": 9, 
      "question": "What boxer's original name is Cassius Clay?"
    }
  ], 
  "success": true, 
  "total_questions": 1
}
```

### GET /categories/<category_id>/questions
- Fetches a paginated list of question objects that all belong to the specified category.
- Parameters:
    - `category_id: integer`
- Returns:
    - A paginated list of question objects. Also returns the current category and the total number of questions that belong to the specified category.

```
curl http://localhost:5000/categories/1/questions?page=1

{
  "current_category": 1, 
  "questions": [
    {
      "answer": "The Liver", 
      "category": 1, 
      "difficulty": 4, 
      "id": 20, 
      "question": "What is the heaviest organ in the human body?"
    }, 
    {
      "answer": "Alexander Fleming", 
      "category": 1, 
      "difficulty": 3, 
      "id": 21, 
      "question": "Who discovered penicillin?"
    }, 
    {
      "answer": "Blood", 
      "category": 1, 
      "difficulty": 4, 
      "id": 22, 
      "question": "Hematology is a branch of medicine involving the study of what?"
    }, 
    {
      "answer": "8000 miles", 
      "category": 1, 
      "difficulty": 2, 
      "id": 25, 
      "question": "What is the approximate diameter of the Earth?"
    }
  ], 
  "success": true, 
  "total_questions": 4
}

```

### POST /quizzes
- Fetches the next question object for the trivia quiz. This is a randomly selected question that is not found in the specified previous questions list parameter.
- Parameters:
    - `quiz_category: integer (optional)`
    - `previous_questions: list: integer (optional)`
- Returns:
    - A boolean success value and a single question object.

```
curl -X POST -H "Content-Type: application/json" -d '{"previous_questions":[], "quiz_category":{"type":"Science","id":"1"}}' http://localhost:5000/quizzes

{
  "question": {
    "answer": "Blood", 
    "category": 1, 
    "difficulty": 4, 
    "id": 22, 
    "question": "Hematology is a branch of medicine involving the study of what?"
  }, 
  "success": true
}
```


## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
