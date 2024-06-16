
import numpy as np
import skforecast
import lightgbm as lgb
from skforecast.ForecasterAutoreg import ForecasterAutoreg
from sklearn.metrics import mean_squared_error

class LightGBM :

    def __init__(self):

        "Forecaster Information"
        self.steps = None
        self.lags =  None
        self.datos_train = None
        self.datos_test = None
        

        """LightGBM ML model"""
        self.light = lgb.LGBMRegressor(objective='regression', random_state=123)
        
        """Forecaster AutoReg"""
        self.forecaster = ForecasterAutoreg(
                regressor = self.light,
                lags      = self.lags
        )

    def datatest(self):
        if self.datos_test :
            return self.datos_test
        return None

    """
        Predice en el futuro para dentro de "minutes" minutos
    """
    def predictions(self):
        return self.forecast()
    
    """
        Entrenamos el modelo con los datos de entrenamiento y variables exogenenas
    """
    def fitLight(self, datos_train, datos_test,steps):
        
        self.steps = steps
        self.lags = steps * 5

        self.datos_train = datos_train
        self.datos_test = datos_test

        self.forecaster.fit(y=self.datos_train['HeartRate'], exog=self.datos_train[['Calories','Steps','Distance']])
       
    """
        Para predecir a x minutos en el futuro
    """
    def forecast(self):
        
        self.predicciones = self.forecaster.predict(steps=self.steps,  exog=self.datos_test[['Calories', 'Steps', 'Distance']])

        error_mse = mean_squared_error(
            y_true = self.datos_test['HeartRate'],
            y_pred = self.predicciones
        )

        print(f"Error de test (mse): {error_mse}")


        return self.predicciones
