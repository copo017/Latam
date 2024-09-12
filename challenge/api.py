import fastapi
from pydantic import BaseModel, validator
import pandas as pd
import yaml
from typing import List
from challenge import model

# Cargar archivo settings.yaml
with open('F:/Users/Documents/Program Class/latam-challenge-main/challenge/settings.yaml', 'r') as f:
    SETTINGS = yaml.safe_load(f)

app = fastapi.FastAPI()

# Instanciar el modelo
model = model.DelayModel()

# Definir el esquema de validación para los datos de vuelo
class FlightValidation(BaseModel):
    TIPOVUELO: str
    MES: int
    OPERA: str

    # Validar el campo TIPOVUELO
    @validator("TIPOVUELO")
    def validate_TIPOVUELO(cls, value):
        if value not in SETTINGS['FLIGHT_TYPES']:
            raise fastapi.HTTPException(status_code=400, detail=f"Invalid TIPOVUELO value: {value}")
        return value

    # Validar el campo MES (debe estar entre 1 y 12)
    @validator("MES")
    def validate_MES(cls, value):
        if value not in range(1, 13):
            raise fastapi.HTTPException(status_code=400, detail=f"Invalid MES value: {value}")
        return value

    # Validar el campo OPERA
    @validator("OPERA")
    def validate_OPERA(cls, value):
        if value not in SETTINGS['OPERATORS']:
            raise fastapi.HTTPException(status_code=400, detail=f"Invalid OPERA value: {value}")
        return value


# Definir el esquema para la solicitud de predicción
class FlightRequest(BaseModel):
    flights: List[FlightValidation]


# Definir el esquema para la respuesta de predicción
class FlightPrediction(BaseModel):
    predict: List[int]


@app.get("/health", status_code=200)
async def get_health() -> dict:
    return {
        "status": "OK"
    }


@app.post("/predict", status_code=200)
async def post_predict(data: FlightRequest) -> FlightPrediction:
    try:
        # Extraer los datos de la solicitud
        f_type = [flight.TIPOVUELO for flight in data.flights]
        f_month = [flight.MES for flight in data.flights]
        f_operator = [flight.OPERA for flight in data.flights]

        # Crear un DataFrame con los datos de entrada
        request = {"MES": f_month, "OPERA": f_operator, "TIPOVUELO": f_type}
        features = pd.DataFrame(request)

        # Preprocesar los datos
        features = model.preprocess(features)

        # Obtener las predicciones
        predictions = model.predict(features)
        return FlightPrediction(predict=predictions)

    except ValueError as e:
        raise fastapi.HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail=f"Internal server error: {e}")
