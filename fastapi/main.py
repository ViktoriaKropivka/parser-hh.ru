import mysql
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import pars_vacancies, connect_to_db

app = FastAPI()

class CriteriaModel(BaseModel):
    criteria: str

@app.post("/pars/vacancies")
async def post_vacancies(data: CriteriaModel):
    criteria = data.criteria
    table_name = criteria.replace(" ", "_")
    try:
        pars_vacancies(criteria, table_name)
        return {"status": "completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during parsing: {e}")

@app.get("/get_vacancy")
async def get_vacancy_from_database(id: int, table_name: str):
    table_name = table_name.replace(' ', '_')
    conn = connect_to_db()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM `{table_name}`На WHERE id = %s", (id,))
        vacancy = cursor.fetchone()
        if not vacancy:
            raise HTTPException(status_code=404, detail="Vacancy not found")
        return {"vacancy": vacancy}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
    finally:
        conn.close()

@app.get("/get_count")
async def get_row_count(table_name: str):
    table_name = table_name.replace(' ', '_')
    conn = connect_to_db()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) AS count FROM `{table_name}`")
        result = cursor.fetchone()
        return {"count": result[0]}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)