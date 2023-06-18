FROM python:3.8-slim-buster
WORKDIR /.
COPY Pipfile Pipfile
RUN pip install pipenv
RUN pipenv install
COPY . .
CMD ["python3","-m","docker_test.py"]