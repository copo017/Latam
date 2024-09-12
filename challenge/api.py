import fastapi
from pydantic import BaseModel, validator
import pandas as pd
import yaml
from typing import List
from challenge import model

with open('F:/Users/Documents/Program Class/latam-challenge-main/challenge/settings.yaml', 'r') as f:
    SETTINGS = yaml.safe_load(f)

app = fastapi.FastAPI()
model = model.DelayModel()


class FlightValidation(BaseModel):
    TIPOVUELO: str
    MES: int
    OPERA: str

    @validator("TIPOVUELO")
    def validate_TIPOVUELO(cls, value):
        if value not in SETTINGS['FLIGHT_TYPES']:
            raise fastapi.HTTPException(status_code=400, detail=str(ValueError))
        return value

    @validator("MES")
    def validate_MES(cls, value):
        if value not in range(1, 13):
            raise fastapi.HTTPException(status_code=400, detail=str(ValueError))
        return value


class FlightRequest(BaseModel):
    flights: List[FlightValidation]


class FlightPrediction(BaseModel):
    predict: List[int]


@app.get("/health", status_code=200)
async def get_health() -> dict:
    return {
        "status": "OK"
    }


@app.post("/predict", status_code=200)
async def post_predict(data: FlightRequest) -> FlightPrediction:
    # Get Request
    f_type = [flight.TIPOVUELO for flight in data.flights]
    f_month = [flight.MES for flight in data.flights]
    f_operator = [flight.OPERA for flight in data.flights]
    # Create DataFrame
    request = {"MES": f_month, "OPERA": f_operator, "TIPOVUELO": f_type}
    features = pd.DataFrame(request)
    try:
        features = model.preprocess(features)
    except ValueError as e:
        raise fastapi.HTTPException(status_code=400, detail=str(e))
    # Get Prediction
    predictions = model.predict(features)
    return FlightPrediction(predict=predictions)