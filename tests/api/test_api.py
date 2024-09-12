import unittest
from fastapi.testclient import TestClient
from challenge import app
import numpy as np
from mockito import ANY, when
import time
from unittest.mock import patch
from pathlib import Path
import shutil

class TestBatchPipeline(unittest.TestCase):
    # def setUp(self):
    #     self.client = TestClient(app)

    def setUp(self):
        self.client = TestClient(app)
        # Verificar si el archivo model.pkl ya existe en el directorio raíz, si no, lo copiamos
        model_source_path = Path("F:/Users/Documents/Program Class/latam2/tests/model/model.pkl")
        model_destination_path = Path("model.pkl")

        if not model_destination_path.exists():
            if model_source_path.exists():
                shutil.copy(model_source_path, model_destination_path)
            else:
                raise FileNotFoundError(f"No se encontró el archivo del modelo en {model_source_path}")

    def test_should_get_predict(self):
        data = {
            "flights": [
                {
                    "OPERA": "Aerolineas Argentinas",
                    "TIPOVUELO": "N",
                    "MES": 3
                }
            ]
        }
        #when("xgboost.XGBClassifier").predict(ANY).thenReturn(np.array([0]))
        response = self.client.post("/predict", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"predict": [0]})

    # @patch('challenge.model.DelayModel.predict')
    # def test_should_get_predict(self, mock_predict):
    #     mock_predict.return_value = [0]
    #     data = {
    #         "flights": [
    #             {
    #                 "OPERA": "Aerolineas Argentinas",
    #                 "TIPOVUELO": "N",
    #                 "MES": 3
    #             }
    #         ]
    #     }
    #     response = self.client.post("/predict", json=data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json(), {"predict": [0]})

    def test_should_failed_unkown_column_1(self):
        data = {
            "flights": [
                {
                    "OPERA": "Aerolineas Argentinas",
                    "TIPOVUELO": "N",
                    "MES": 13  # MES fuera del rango permitido
                }
            ]
        }
        response = self.client.post("/predict", json=data)
        self.assertEqual(response.status_code, 400)

    def test_should_failed_unkown_column_2(self):
        data = {
            "flights": [
                {
                    "OPERA": "Aerolineas Argentinas",
                    "TIPOVUELO": "O",  # TIPOVUELO no válido
                    "MES": 13  # MES fuera del rango permitido
                }
            ]
        }
        response = self.client.post("/predict", json=data)
        self.assertEqual(response.status_code, 400)

    def test_should_failed_unkown_column_3(self):
        data = {
            "flights": [
                {
                    "OPERA": "Argentinas",  # OPERA no válido
                    "TIPOVUELO": "O",  # TIPOVUELO no válido
                    "MES": 13  # MES fuera del rango permitido
                }
            ]
        }
        response = self.client.post("/predict", json=data)
        self.assertEqual(response.status_code, 400)
