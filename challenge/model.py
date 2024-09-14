from datetime import datetime
from typing import Tuple, Union, List
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
import yaml
import logging as LOGGER

# Get settings file as SETTINGS
with open('challenge/settings.yaml', 'r') as f:
    SETTINGS = yaml.safe_load(f)

LOGGER.basicConfig(
    level=LOGGER.INFO,
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%H:%M:%S')


class DelayModel:

    def __init__(self):
        self._model = xgb.XGBClassifier(random_state=1, learning_rate=0.01)

    def preprocess(
            self,
            data: pd.DataFrame,
            target_column: str = None
    ) -> Union[Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame]:
        """
        Prepare raw data for training or predict.

        Args:
            data (pd.DataFrame): raw data.
            target_column (str, optional): if set, the target is returned.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: features and target.
            or
            pd.DataFrame: features.
        """
        LOGGER.info("Data preprocessing started")
        # Get features
        features = self._features(data)

        if target_column:
            LOGGER.info("preprocessing target")
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
        Fit model with preprocessed data.

        Args:
            features (pd.DataFrame): preprocessed data.
            target (pd.DataFrame): target.
        """
        label_0 = len(target[target["delay"] == 0])
        label_1 = len(target[target["delay"] == 1])
        self._model.set_params(
            scale_pos_weight=label_0 / label_1
        )
        self._model.fit(features, target)
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
        Predict delays for new flights.

        Args:
            features (pd.DataFrame): preprocessed data.

        Returns:
            (List[int]): predicted targets.
        """
        model = joblib.load('model.pkl')
        xgboost_y_preds = model.predict(features)
        LOGGER.info('Model prediction completed')
        return [1 if y_pred > 0.5 else 0 for y_pred in xgboost_y_preds]

    @staticmethod
    def _is_high_season(date: str) -> int:
        """
        Get if is high season

        Args:
            date: str

        Returns:
            int: 1 True, 0 False
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
        Get difference

        Args:
            date: str

        Returns:
            int: Minimal differene in seconds
        """
        fecha_o = datetime.strptime(data['Fecha-O'], '%Y-%m-%d %H:%M:%S')
        fecha_i = datetime.strptime(data['Fecha-I'], '%Y-%m-%d %H:%M:%S')
        min_diff = ((fecha_o - fecha_i).total_seconds()) / 60
        return min_diff

    @staticmethod
    def _get_period_day(date: str) -> str:
        """
        Get the period of the day.

        Args:
            date: str

        Returns:
            str: mañana, tarde o noche
        """
        date_time = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').time()
        morning_min = datetime.strptime("05:00", '%H:%M').time()
        morning_max = datetime.strptime("11:59", '%H:%M').time()
        afternoon_min = datetime.strptime("12:00", '%H:%M').time()
        afternoon_max = datetime.strptime("18:59", '%H:%M').time()
        evening_min = datetime.strptime("19:00", '%H:%M').time()
        evening_max = datetime.strptime("23:59", '%H:%M').time()
        night_min = datetime.strptime("00:00", '%H:%M').time()
        night_max = datetime.strptime("4:59", '%H:%M').time()

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
        Get the features from data.

        Args:
            data (pd.DataFrame): raw data.

        Returns:
            pd.DataFrame: features.
        """

        # Convert values into categorical values
        data["MES"] = pd.Categorical(data["MES"], categories=[month for month in range(1, 13)])
        data["OPERA"] = pd.Categorical(data["OPERA"], categories=SETTINGS['OPERATORS'])
        data["TIPOVUELO"] = pd.Categorical(data["TIPOVUELO"], categories=SETTINGS['FLIGHT_TYPES'])

        # Get the dummy variables for categories
        features = pd.concat(
            [
                pd.get_dummies(data["OPERA"], prefix="OPERA"),
                pd.get_dummies(data["TIPOVUELO"], prefix="TIPOVUELO"),
                pd.get_dummies(data["MES"], prefix="MES"),
            ],
            axis=1,
        )

        features = features[SETTINGS['TOP_FEATURES']]
        LOGGER.info("Features completed")
        return features

