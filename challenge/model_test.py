from datetime import datetime
from typing import Tuple, Union, List
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
import yaml
import logging as LOGGER

# Configuración de logging para mostrar mensajes informativos
LOGGER.basicConfig(
    level=LOGGER.INFO,
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%H:%M:%S')

# Cargar el archivo settings.yaml que está en la misma carpeta
with open('F:/Users/Documents/Program Class/latam2/challenge/settings.yaml', 'r') as f:
    SETTINGS = yaml.safe_load(f)


class DelayModel:

    def __init__(self):
        # Inicializamos el modelo XGBoost con un aprendizaje predefinido
        self._model = xgb.XGBClassifier(random_state=1, learning_rate=0.01)

    def preprocess(
            self,
            data: pd.DataFrame,
            target_column: str = None
    ) -> Union[Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame]:
        """
        Preprocesa los datos crudos para entrenamiento o predicción.
        """
        LOGGER.info("Data preprocessing started")
        # Obtener las características
        features = self._features(data)

        # Si estamos en modo de entrenamiento, calcula las columnas adicionales necesarias
        if target_column:
            LOGGER.info("Preprocessing target")
            data['period_day'] = data['Fecha-I'].apply(self._get_period_day)
            data['high_season'] = data['Fecha-I'].apply(self._is_high_season)
            data['min_diff'] = data.apply(self._get_min_diff, axis=1)
            data['delay'] = np.where(data['min_diff'] > SETTINGS['THRESHOLD'], 1, 0)
            return features, data[[target_column]]

        LOGGER.info("Data preprocessing completed successfully")
        return features

    def fit(
            self,
            features: pd.DataFrame,
            target: pd.DataFrame
    ) -> None:
        """
        Ajustar el modelo con los datos preprocesados.

        """
        # Calcular la relación entre clases para equilibrar el modelo
        label_0 = len(target[target["delay"] == 0])
        label_1 = len(target[target["delay"] == 1])
        self._model.set_params(
            scale_pos_weight=label_0 / label_1
        )
        self._model.fit(features, target)

        # Guardar el modelo entrenado
        try:
            joblib.dump(self._model, 'model.pkl')
            LOGGER.info('Model fit and saved successfully')
        except Exception as e:
            LOGGER.error(f'Error saving model: {e}')
        return

    def predict(
            self,
            features: pd.DataFrame
    ) -> List[int]:
        """
        Predecir retrasos en vuelos nuevos.

        """
        # Cargar el modelo entrenado
        model = joblib.load('model.pkl')
        xgboost_y_preds = model.predict(features)
        LOGGER.info('Model prediction completed')
        return [1 if y_pred > 0.5 else 0 for y_pred in xgboost_y_preds]

    @staticmethod
    def _is_high_season(date: str) -> int:
        """
        Determinar si es temporada alta

        """
        fecha_año = int(date.split('-')[0])
        fecha = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        range1_min = datetime.strptime('15-Dec', '%d-%b').replace(year=fecha_año)
        range1_max = datetime.strptime('31-Dec', '%d-%b').replace(year=fecha_año)
        range2_min = datetime.strptime('1-Jan', '%d-%b').replace(year=fecha_año)
        range2_max = datetime.strptime('3-Mar', '%d-%b').replace(year=fecha_año)
        range3_min = datetime.strptime('15-Jul', '%d-%b').replace(year=fecha_año)
        range3_max = datetime.strptime('31-Jul', '%d-%b').replace(year=fecha_año)
        range4_min = datetime.strptime('11-Sep', '%d-%b').replace(year=fecha_año)
        range4_max = datetime.strptime('30-Sep', '%d-%b').replace(year=fecha_año)

        if ((fecha >= range1_min and fecha <= range1_max) or
                (fecha >= range2_min and fecha <= range2_max) or
                (fecha >= range3_min and fecha <= range3_max) or
                (fecha >= range4_min and fecha <= range4_max)):
            return 1
        else:
            return 0

    @staticmethod
    def _get_min_diff(data: str) -> int:
        """
        Obtener la diferencia mínima entre fechas

        """
        fecha_o = datetime.strptime(data['Fecha-O'], '%Y-%m-%d %H:%M:%S')
        fecha_i = datetime.strptime(data['Fecha-I'], '%Y-%m-%d %H:%M:%S')
        min_diff = ((fecha_o - fecha_i).total_seconds()) / 60
        return min_diff

    @staticmethod
    def _get_period_day(date: str) -> str:
        """
        Obtener el periodo del día (mañana, tarde, noche).

        """
        date_time = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').time()
        morning_min = datetime.strptime("05:00", '%H:%M').time()
        morning_max = datetime.strptime("11:59", '%H:%M').time()
        afternoon_min = datetime.strptime("12:00", '%H:%M').time()
        afternoon_max = datetime.strptime("18:59", '%H:%M').time()
        evening_min = datetime.strptime("19:00", '%H:%M').time()
        evening_max = datetime.strptime("23:59", '%H:%M').time()
        night_min = datetime.strptime("00:00", '%H:%M').time()
        night_max = datetime.strptime("04:59", '%H:%M').time()

        if (date_time > morning_min and date_time < morning_max):
            return 'mañana'
        elif (date_time > afternoon_min and date_time < afternoon_max):
            return 'tarde'
        elif (
                (date_time > evening_min and date_time < evening_max) or
                (date_time > night_min and date_time < night_max)
        ):
            return 'noche'

    @staticmethod
    def _features(data: pd.DataFrame) -> pd.DataFrame:
        """
        Obtener las características del DataFrame.

        """
        # Convertir valores a variables categóricas
        data["MES"] = pd.Categorical(data["MES"], categories=[month for month in range(1, 13)])
        data["OPERA"] = pd.Categorical(data["OPERA"], categories=SETTINGS['OPERATORS'])
        data["TIPOVUELO"] = pd.Categorical(data["TIPOVUELO"], categories=SETTINGS['FLIGHT_TYPES'])

        # Obtener variables dummy para las categorías
        features = pd.concat(
            [
                pd.get_dummies(data["OPERA"], prefix="OPERA"),
                pd.get_dummies(data["TIPOVUELO"], prefix="TIPOVUELO"),
                pd.get_dummies(data["MES"], prefix="MES"),
            ],
            axis=1,
        )

        # Seleccionar solo las columnas requeridas
        features = features[SETTINGS['TOP_FEATURES']]
        LOGGER.info("Features completed")
        return features
