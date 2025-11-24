from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel,computed_field,Field
from typing import Literal,Annotated,Optional
import json

app = FastAPI()

class patient(BaseModel):

    patient_id: Annotated[str, Field(...,description='enter patient id',examples=['P001'])]
    name: str
    city:str
    age:Annotated[int,Field(...,gt=0)]
    gender: Literal['male','female','others']
    height:Annotated[float,Field(...,gt=0)]
    weight:Annotated[float,Field(...,gt=0)]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:

        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Normal'
        else:
            return 'Obese'


class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]


def load_data():
    with open('patients.json','r') as f:
        data = json.load(f)
        return data

def save_data(data):
    with open('patients.json','w') as f:
        json.dump(data,f)
    
    

@app.get("/")
def hello():
    return "This is dummy api of patient data"

@app.get("/view/{patient_id}")
def view(patient_id):

    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404,detail="id not in data")


@app.post('/create')
def create(patient:patient):

    data = load_data()

    if patient.patient_id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')
    
    data[patient.patient_id] = patient.model_dump(exclude='patient_id')

    save_data(data)

    return JSONResponse(status_code=201, content={'message':'patient created successfully'})


@app.put('/update/{patient_id}')
def update(patient_id: str,PatientUpdate:PatientUpdate):

    data = load_data()
    
    if patient_id not in data:
        raise HTTPException(status_code=404,detail="id not in data")

    existing_info = data[patient_id]

    update_info = PatientUpdate.model_dump(exclude_unset=True)

    for k,v in update_info.items():
        existing_info[k] = v

    existing_info['patient_id'] = patient_id
    pydantic_obj=patient(**existing_info)
    existing_info = pydantic_obj.model_dump(exclude='id')

    data[patient_id] = existing_info

    # save data
    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient updated'})
