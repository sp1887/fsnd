# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server.

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application.

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior.

1. Use Flask-CORS to enable cross-domain requests and set response headers.
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories.
3. Create an endpoint to handle GET requests for all available categories.
4. Create an endpoint to DELETE question using a question ID.
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score.
6. Create a POST endpoint to get questions based on category.
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question.
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions.
9. Create error handlers for all expected errors including 400, 404, 422 and 500.

REVIEW_COMMENT

```
This README is missing documentation of your endpoints. Below is an example for your endpoint to get all categories. Please use it as a reference for creating your documentation and resubmit your code.
```

Endpoints

GET '/categories'

- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a keys:
   - categories, that contains a object of id: category_string key:value pairs.
   - success, that contains a boolean which represents successfully processed request
   - total_categories, that contains number of total categories fetched

  {
    "categories": {
      "1": "Science",
      "2": "Art",
      "3": "Geography",
      "4": "History",
      "5": "Entertainment",
      "6": "Sports"
    },
    "success": true,
    "total_categories": 6
  }


GET '/questions'

- Fetches a dictionary of questions in which the keys are the categories, current category, questions, total_questions and the value is the corresponding dictionary of categories, integer of the current category, list of questions, and total number of questions

- Request Arguments: None

- Returns: An object with multiple keys:
   - categories that contains object of id: category_string key:value pairs  
   - current_category that contains integer of category
   - questions that contain list of objects that contain key:value pairs:
      - answer:answer_string,
      - category:category_integer,
      - difficulty:difficulty_integer,
      - id:question_id_integer and
      - question:question_string
   - total_questions that contains number of all questions
   - success that contains boolean which represents successfully processed request

  {
    "categories": {
      "1": "Science",
      "2": "Art",
      "3": "Geography",
      "4": "History",
      "5": "Entertainment",
      "6": "Sports"
    },
    "current_category": null,
    "questions": [
      {
        "answer": "Apollo 13",
        "category": 5,
        "difficulty": 4,
        "id": 2,
        "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
      },
      {
        "answer": "Tom Cruise",
        "category": 5,
        "difficulty": 4,
        "id": 4,
        "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
      },
      .
      .
      .
      {
        "answer": "The Palace of Versailles",
        "category": 3,
        "difficulty": 3,
        "id": 14,
        "question": "In which royal palace would you find the Hall of Mirrors?"
      }
    ],
    "success": true,
    "total_questions": 20
  }


POST /questions

- Fetch questions related to search term or insert new questions in database.  

- Request Arguments:

a) to insert question to database: dictionary with key:value pairs:
    - question: question_string
    - answer: answer_string
    - category: category_integer
    - difficulty: difficulty_integer

  {
    answer: "France"
    category: "6"
    difficulty: 1
    question: "Which country won the soccer World cup in 2018?"
  }

b) to perform search query: dictionary with searchTerm key and corresponding value search_term_string.

  {
    searchTerm: "World cup"
  }

- Returns an object depends on which request argument was provided:

a) an object with keys: 'created' that contains id_integer of created question and 'success' that contains boolean which represents successfully processed request

  {
    "created": 30,
    "success": true
  }

b) an object with keys:
  - questions that contains list of objects with key:value pairs:
    - answer:answer_string,
    - category:category_integer,
    - difficulty:difficulty_integer,
    - id:id_integer,
    - question:question_string
  - success that contains boolean which represents successfully processed request
  - total_questions that contains number of all questions

  {
    "questions": [
      {
        "answer": "Brazil",
        "category": 6,
        "difficulty": 3,
        "id": 10,
        "question": "Which is the only team to play in every soccer World Cup tournament?"
      },
      {
        "answer": "Uruguay",
        "category": 6,
        "difficulty": 4,
        "id": 11,
        "question": "Which country won the first ever soccer World Cup in 1930?"
      },
    ],
    "success": true,
    "total_questions": 2
  }

GET '/categories/<int:category_id>/questions'

- Fetch questions related to category.

- Request Arguments: None

- Returns: An object with multiple keys:
   - current_category that contains category string
   - questions that contain list of objects that contain key:value pairs:
      - answer:answer_string,
      - category:category_integer,
      - difficulty:difficulty_integer,
      - id:question_id_integer,
      - question:question_string
   - total_questions that contains number of all questions in category
   - success that contains boolean that represents successfully processed request

   {
     "current_category": "Art",
     "questions": [
       {
         "answer": "Escher",
         "category": 2,
         "difficulty": 1,
         "id": 16,
         "question": "Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
       },
       .
       .
       .
       {
         "answer": "Jackson Pollock",
         "category": 2,
         "difficulty": 2,
         "id": 19,
         "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
       }
     ],
     "success": true,
     "total_questions": 4
   }


POST '/quizzes'

- Fetch question which wasn't displayed yet in current trivia game.

- Request Arguments:
An object with keys: previous_questions which contains a list of ids of previous displayed questions and quiz_category which contains a dictionary with type:type_string and id:category_id_string key:values pairs.

  {
    previous_questions: [22]
    quiz_category: {type: "Science", id: "1"}
  }

- Returns: An object with keys:
     - question that contains object with keys
        - answer:answer_string
        - id: question_id_integer
        - question: question_string  
     - success that contains boolean which represents successfully processed request

   {
     "question": {
       "answer": "The Liver",
       "id": 20,
       "question": "What is the heaviest organ in the human body?"
     },
     "success": true
   }


## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
