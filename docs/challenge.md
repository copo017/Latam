# Desafío LATAM - Solución

## Pasos para resolver el desafío

### 1. Revisar el notebook para seleccionar el modelo
Comenzamos revisando el notebook que contiene varias opciones de modelos para entender cuál sería el más adecuado para predecir retrasos en los vuelos. Después de analizar el rendimiento de diferentes modelos, optamos por utilizar **XGBoost Classifier** debido a su alto rendimiento y capacidad para manejar datos tanto lineales como no lineales.

El modelo XGBoost fue seleccionado porque:
- Tiene un fuerte poder predictivo y es adecuado para tareas de clasificación.
- Puede manejar eficientemente valores faltantes y características categóricas.
- Proporciona mejores resultados en conjuntos de datos desequilibrados, lo cual es importante para predecir retrasos en los vuelos.

### 2. Transcribir el modelo en `model.py`
Una vez seleccionado el modelo **XGBoost**, lo implementamos en el archivo `model.py`.

#### Pasos clave:
- **Cargar y preprocesar** los datos: El preprocesamiento incluyó la transformación de fechas y la creación de características como el mes, operador y tipo de vuelo. Se codificaron variables categóricas y se calculó la diferencia de tiempo (`min_diff`) para determinar si hubo retraso.
- **Ajuste del modelo**: Utilizamos el método `fit` para entrenar el modelo con los datos preprocesados. El modelo fue guardado utilizando `joblib` para facilitar su reutilización.
- **Predicción**: Implementamos el método `predict`, que carga el modelo entrenado y realiza predicciones sobre nuevos datos de vuelo, devolviendo `0` para sin retraso y `1` para con retraso.

### 3. Implementar la lógica del modelo en la API
El siguiente paso fue integrar la lógica del modelo en una API construida con **FastAPI**.

- La API tiene dos rutas principales:
  - **GET /health**: Verifica que la API esté en funcionamiento.
  - **POST /predict**: Acepta datos de vuelos en formato JSON, realiza las predicciones utilizando el modelo XGBoost y devuelve el resultado.

#### Flujo de la API:
1. **Validación de datos**: Usamos **Pydantic** para validar que los datos de entrada cumplan con los requisitos de formato.
2. **Preprocesamiento**: Los datos recibidos son transformados de la misma forma en que fueron tratados en el entrenamiento del modelo, garantizando consistencia en las predicciones.
3. **Predicción**: El modelo preentrenado realiza las predicciones sobre los datos de entrada y la respuesta se devuelve en formato JSON.

### Ejemplo de una solicitud POST en Postman

- **URL**: `https://latam2.onrender.com/predict`
- **Cuerpo de la solicitud**:

```json
{
    "flights": [
        {
            "OPERA": "Aerolineas Argentinas",
            "TIPOVUELO": "N",
            "MES": 3
        }
    ]
}
```
respueta
```json
{
    "predict": [
        0
    ]
}
```
Este ejemplo muestra cómo se puede hacer una solicitud POST para predecir si un vuelo tendrá un retraso. En este caso, la API predice que no habrá retraso.

Cada vez que se hacía una ejecución del método POST /predict y la respuesta era 0 o 1, es porque estábamos utilizando el modelo de clasificación XGBoost Classifier para predecir si un vuelo tendría retraso o no.

El modelo está diseñado para clasificar los vuelos en dos clases:

0: Indica que el vuelo no tendrá un retraso significativo (menor de 15 minutos).
1: Indica que el vuelo tendrá un retraso significativo (mayor de 15 minutos).
Durante el preprocesamiento de los datos, calculamos la diferencia de tiempo entre la hora programada de salida y la hora real de salida. Si esta diferencia (representada por la variable min_diff) era mayor a un umbral (generalmente 15 minutos), el vuelo se etiquetaba como retrasado. Así, cuando el modelo realiza la predicción, devuelve:

0 para "sin retraso".
1 para "con retraso".
Por lo tanto, las respuestas 0 o 1 representan la predicción de si un vuelo estará retrasado o no según el entrenamiento previo del modelo.

### 4. Buenas prácticas de programación
A lo largo del desarrollo, seguimos varias buenas prácticas que garantizaron la calidad y mantenibilidad del código:

- **Modularización**: Mantuvimos la lógica del modelo separada en el archivo `model.py` para facilitar la reutilización y las pruebas.
- **Validación de datos**: Implementamos validaciones utilizando **Pydantic** para asegurar que los datos de entrada tuvieran el formato correcto.
- **Pruebas automatizadas**: Se configuraron pruebas unitarias para garantizar que tanto la lógica del modelo como la API funcionen correctamente. Las pruebas se ejecutan automáticamente en cada cambio mediante **CI/CD**.
- **Control de versiones**: Utilizamos **Git** para controlar los cambios y colaborar eficientemente en el proyecto.
- **Despliegue continuo (CI/CD)**: Implementamos pipelines de CI/CD para ejecutar pruebas automatizadas antes de desplegar la API en producción, asegurando que el código siempre esté en buen estado antes de ser liberado.
- **Utilizamos el archivo settings.yaml** para centralizar la configuración clave de nuestro modelo y la API, y así evitar la repetición de información en múltiples partes del código. El objetivo era hacer que el sistema sea más flexible y fácil de mantener.
    Aquí está el propósito de cada sección dentro del archivo settings.yaml:
    - **TOP_FEATURES:** Especifica las características principales (o variables) que el modelo utilizará para hacer predicciones. Estas son las columnas que demostraron tener más impacto en el rendimiento del modelo durante el entrenamiento. Al definirlas en un archivo separado, podemos modificar las características importantes sin tocar el código del modelo.
    - **THRESHOLD:** Este valor define el umbral en minutos para determinar si un vuelo se considera retrasado. En este caso, cualquier vuelo con una diferencia de más de 15 minutos entre la hora de salida programada y la hora real se clasifica como retrasado.
    - **OPERATORS:** Es una lista de las aerolíneas que el modelo puede manejar. Si en el futuro se agregan nuevas aerolíneas, podemos simplemente actualizar este archivo en lugar de modificar el código base.
    - **FLIGHT_TYPES:** Define los tipos de vuelo que son reconocidos por el sistema, como vuelos internacionales ("I") y nacionales ("N").

### 5. Despliegue en Render
Se opto por desplegar en render por la familiaridad que tengo con este sitio para alojar aplicaciones que no usen tantos recursos.

### Conclusion
El desafío fue resuelto con éxito al seleccionar el modelo XGBoost Classifier, conocido por su capacidad para manejar datos desequilibrados y su alto rendimiento en tareas de clasificación. Se implementó el modelo en el archivo model.py, integrándolo eficientemente con una API construida con FastAPI, que validaba los datos de entrada y realizaba predicciones claras sobre posibles retrasos en vuelos.
Además, se estableció una estrategia de CI/CD que garantizó un flujo de trabajo automatizado y seguro desde la integración hasta el despliegue en Render, asegurando la estabilidad y eficiencia del proyecto. Las pruebas y validaciones continuas fueron clave para mantener la calidad del sistema.
Este enfoque integral, desde la elección del modelo hasta su despliegue, demostró buenas prácticas de programación y una implementación sólida para producción.
