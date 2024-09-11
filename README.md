## MAKE SURE YOU ARE USING PYTHON 3.12.0

This project requires python 3.12.0, please make sure you are running the specified python version in your machine.

## INSTALL POETRY & ACTIVATE VIRTUAL ENVIRONMENT

### INSTALL POETRY

If you don't have poetry package manager install in your system make sure it is installed 

```shell
pip install poetry
```

### CREATE AND ACTIVATE VIRTUAL ENVIRONMENT

- Go to project directory and first make sure you are going to create `.venv` folder in current directory for your virtual environment.

```
export POETRY_VIRTUALENVS_IN_PROJECT=true
```

- Then  create & activate virtual environment with below command

```shell
poetry shell
```

### INSTALL PACKAGES

Add all packages

```
poetry install
```

## RUN PROJECT

For development

```
flask run --reload
```

For production

```
gunicorn -c gunicorn_config.py app:app
```

