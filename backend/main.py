from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.165.10:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Task(BaseModel):
    title: str


@app.get("/")
def home():
    return {"message": "Personal Task Tracker API is running"}


@app.get("/db-test")
def db_test():
    conn = psycopg.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

    conn.close()

    return {"message": "Database connection successful"}

@app.get("/tasks")
def get_tasks(status: str = None):
    conn = psycopg.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

    cursor = conn.cursor()

    if status:
        cursor.execute("""
        SELECT id, title, status, created_at
        FROM tasks
        WHERE status = %s
        ORDER BY id;
    """, (status,))
    else:
        cursor.execute("""
        SELECT id, title, status, created_at
        FROM tasks
        ORDER BY id;
    """)

    tasks = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {
            "id": task[0],
            "title": task[1],
            "status": task[2],
            "created_at": task[3]
        }
        for task in tasks
    ]

@app.post("/tasks")
def create_task(task: Task):
    conn = psycopg.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO tasks (title)
        VALUES (%s)
        RETURNING id, title, status, created_at;
        """,
        (task.title,)
    )

    new_task = cursor.fetchone()

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "id": new_task[0],
        "title": new_task[1],
        "status": new_task[2],
        "created_at": new_task[3]
    }

@app.patch("/tasks/{task_id}")
def update_task_status(task_id: int, status: str):
    if status not in ["pending", "completed"]:
        raise HTTPException(
            status_code=400,
            detail="Status must be 'pending' or 'completed'"
        )
    
    conn = psycopg.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET status = %s
        WHERE id = %s
        RETURNING id, title, status, created_at;
        """,
        (status, task_id)
    )

    updated_task = cursor.fetchone()

    if updated_task is None:
        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    
    conn.commit()

    cursor.close()
    conn.close()

    return {
        "id": updated_task[0],
        "title": updated_task[1],
        "status": updated_task[2],
        "created_at": updated_task[3]
    }

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = psycopg.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM tasks
        WHERE id = %s
        RETURNING id;
        """,
        (task_id,)
    )

    deleted_task = cursor.fetchone()

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "message": "Task deleted successfully",
        "id": deleted_task[0]
    }