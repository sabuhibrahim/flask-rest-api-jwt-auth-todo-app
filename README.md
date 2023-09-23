# Flask Todo App with JWT Authentication example

This project includes authentication APIs (login, register), tasklist APIs (list, create, order update, delete), task APIs (list, create, update order, task detail, task update, task delete), also steps APIs (add step, update step and delete step). It uses a PostgreSQL connection with SqlAlchemy ORM. There is an alembic config also.

## Installation
- If you want to run docker you need to [install docker](https://docs.docker.com/engine/install/)
- Configure your postgresql
- Create .env from .env.example
```bash
cp .env.example .env
```
- Add Postgresql config to .env
- Run docker
```bash
docker-compose up -d --build
```
or
```bash
docker compose up -d --build
```
### if you want to run this app without docker
- Add Postgresql config to alembic/env.py
- Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements.txt.
```bash
pip install -r requirements.txt
```
- Run app with start.sh. It will do migrate migrations then run app 
```bash
chmod 755 start.sh
sh start.sh
```
- Or you can run manual on development mode
```bash
python -m flask --app todo_app run 
```