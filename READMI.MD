docker:
docker-compose up --build

alembic:
alembic revision --autogenerate -m "init migration"
alembic update head  

test+coverage:
python -m unittest discover -s tests
coverage report 

pytest:
pytest .\tests\test_dashboard.py