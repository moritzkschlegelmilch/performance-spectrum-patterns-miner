# SPP Performance Spectrum Patterns Miner



## Getting started

### General

There is a backend and a frontend folder each containing the structure for the frontend or the api.
- The backend is written in [FastAPI](https://fastapi.tiangolo.com/), using [SQLAlchemy](https://www.sqlalchemy.org/) ORM with SQLite. We use [alembic](https://alembic.sqlalchemy.org/en/latest/) for migrating the database.
- The frontend is written in [Vue.js](https://vuejs.org/) and uses the [shadcdn](https://www.shadcn-vue.com/) component library with [tailwindcss](https://tailwindcss.com/).

After initializing the project, you must create two files `backend/app/env.py` and `frontend/.env` based on the example files provided in the respective folder. 
These are configuration files that are not tracked by git in case the project is going to be deployed towards the end of the SPP.

### Running the backend

To have the backend running, first install the dependencies in the backend folder:
```
cd backend
pip install -r requirements.txt
```

After that you need to migrate your database (which we use for simple tasks such as storing event log metadata or perhaps user management later on).
Perhaps you need to restart your terminal for that. To learn more about database migrations, visit https://alembic.sqlalchemy.org/en/latest/tutorial.html.

```
cd app
alembic upgrade head
```

Now you are ready to start the backend server, which is done by running the following command:
```
uvicorn main:app --reload
```
Now your dev server should be running at localhost:8000 and automatically track changes.

### Running the frontend

To have the frontend running, first install the dependencies from npm. But make sure you have [node.js](https://nodejs.org/en) installed.
```
cd frontend
npm install
```
After that you can start the frontend dev server by running:
```
npm run dev
```

Now you should be able to access the application at `http://localhost:5173/`.