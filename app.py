from fastapi import FastAPI
import joblib
import pandas as pd
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI()
model = joblib.load('model.pkl') #Load the trained data


#pydantic model for input validation (frontend ke data ka structure )

class Job(BaseModel):
    title : str
    company_profile : str = ""
    description : str = "" 
    requirements : str = ""


    employment_type : str = 'Unknown'
    required_experience : str = 'Unknown'
    required_education : str = 'Unknown'

    telecommuting : int
    has_company_logo : int
    has_questions : int



#Creating the fastapi
@app.get("/")
def home():
    return FileResponse("index.html") 


# ---- Added: prediction endpoint used by the frontend ----
@app.post("/predict")
def predict(job: Job):
    # Same feature layout the pipeline was trained on (see notebook):
    # one combined 'text' column + 3 numeric flags + 3 categorical columns.
    row = pd.DataFrame([{
        "text": f"{job.title} {job.company_profile} {job.description} {job.requirements}",
        "telecommuting": job.telecommuting,
        "has_company_logo": job.has_company_logo,
        "has_questions": job.has_questions,
        "employment_type": job.employment_type,
        "required_experience": job.required_experience,
        "required_education": job.required_education,
    }])

    prediction = int(model.predict(row)[0])
    fraud_probability = float(model.predict_proba(row)[0][1])

    return {
        "prediction": prediction,                       # 1 = fake, 0 = genuine
        "label": "Fake Job" if prediction == 1 else "Genuine Job",
        "fraud_probability": round(fraud_probability, 4),
    }
