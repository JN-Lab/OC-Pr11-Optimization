# OC-Pr11-OpenFoodFacts-App
Repository for Project 11 from Openclassrooms cursus in Software Development

## Project Description

This is a web application built with **Django** to help user to find healthier products of their favorites food.
The objective of this project is to improve the project 8 by:
* Reinforcing the Search algorithm
* Reinforcing the Registration process with email validation

Before testing, do not forget to set-up your SMTP server in **settings.py** !

### Simplified App Structure

```
|-- .gitignore
|-- README.md
|-- requirements.txt
|-- manage.py
|-- Procfile
|-- geckodriver.log
|-- purbeurre_platform/
    |-- __init__.py
    |-- settings.py
    |-- urls.py
    |-- wsgi.py
    |-- static/s
|-- search/
    |-- __init__.py
    |-- dumps/
    |-- management/
    |-- migrations/
    |-- static/
    |-- templates/
    |-- utils/
    |-- tests/
    |-- admin.py
    |-- apps.py
    |-- forms.py
    |-- models.py
    |-- urls.py
    |-- views.py
|-- static/
    |-- boostrap/
    |-- css/
    |-- scss/
    |-- jquery/
    |-- js/
    |-- magnific-popup/
|-- templates/
    |-- 404.html
    |-- 500.html
    |-- base.html
    |-- legal.html
```

## Getting Started

1. Clone the repository:
```
git clone https://github.com/JN-Lab/OC-Pr8-OpenFoodFacts-App.git
```

When you are in your directory (root):

2. Set-up your virtual environment
```
python3 -m venv env
```

3. Activate your virtual environment:
```
source env/bin/activate
```

5. Install all necessary frameworks and libraries
```
pip install -r requirements.txt
```

6. Set-up your database in **settings.py** file 

7. Set-up yout SMTP server in **settings.py** file

8. Go in purbeurre platform directory to have access to manage.py file to launch the initialisation of the database with the basic datas:
```
./manage.py dbinit
```

9. Run the django local server:
```
./manage.py runserver
```

10. You go on your favorite browser and copy paste this url:
```
http://127.0.0.1:8000/
```

## Running the tests
To run the unit tests (in the directory containing manage.py file):
```
./manage.py test -v 3
```

## Built With
* Django
* psycopg2
* requests
