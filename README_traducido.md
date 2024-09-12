# Desafío para Ingeniero de Software (ML & LLMs)

## Descripción general

Bienvenido al **Desafío de Ingeniero de Software (ML & LLMs).** En este reto, tendrás la oportunidad de acercarte a una parte de la realidad del rol y demostrar tus habilidades y conocimientos en machine learning y la nube.
## Problema

Se te ha proporcionado un notebook de Jupyter `(exploration.ipynb)` con el trabajo de un Científico de Datos (a partir de ahora, el CD). El CD entrenó un modelo para predecir la probabilidad de retraso de un vuelo que despegue o aterrice en el aeropuerto SCL. El modelo fue entrenado con datos públicos y reales. A continuación, te proporcionamos la descripción del conjunto de datos:

|Columna|Descripción|
|-----|-----------|
|`Fecha-I`|Fecha y hora programada del vuelo.|
|`Vlo-I`|Número de vuelo programado.|
|`Ori-I`|Código de la ciudad de origen programada.|
|`Des-I`|Código de la ciudad de destino programada.|
|`Emp-I`|Código de la aerolínea del vuelo programado.|
|`Fecha-O`|Fecha y hora de la operación del vuelo.|
|`Vlo-O`|Número de vuelo de la operación.|
|`Ori-O`|Código de la ciudad de origen de la operación.|
|`Des-O`|Código de la ciudad de destino de la operación.|
|`Emp-O`|Código de la aerolínea de la operación.|
|`DIA`|	Día del mes de la operación del vuelo.|
|`MES`|Número del mes de la operación del vuelo.|
|`AÑO`|Año de la operación del vuelo.|
|`DIANOM`|Día de la semana de la operación del vuelo.|
|`TIPOVUELO`|Tipo de vuelo, I = Internacional, N = Nacional.|
|`OPERA`|Nombre de la aerolínea que opera.|
|`SIGLAORI`|Nombre de la ciudad de origen.|
|`SIGLADES`|Nombre de la ciudad de destino.|

Además, el CD consideró relevante crear las siguientes columnas:

|Column| Description                                                                                                        |
|-----|--------------------------------------------------------------------------------------------------------------------|
|`high_season`| 1 si `Date-I` está entre el 15-Dic y el 3-Mar, o el 15-Jul y el 31-Jul, o el 11-Sep y el 30-Sep; 0 de lo contrario. |
|`min_diff`| 	Diferencia en minutos entre `Date-O` y `Date-I`                                                                   |
|`period_day`| Mañana (entre 5:00 y 11:59), tarde (entre 12:00 y 18:59) y noche (entre 19:00 y 4:59), basado en  `Date-I`.        |
|`delay`| 1 si `min_diff` > 15, 0 si no.                                                                                     |

## Desafío

### Instrucciones:

1. Crea un repositorio en **github** y copia todo el contenido del desafío en él. Recuerda que el repositorio debe ser **público**.

2. Utilice la rama **principal** para cualquier versión oficial que debamos revisar. Se recomienda encarecidamente utilizar las prácticas de desarrollo de [GitFlow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow). **NOTA: no elimine sus ramas de desarrollo.**

3. Por favor, no cambie la estructura del desafío (nombres de carpetas y archivos).

4. Toda la documentación y explicaciones que tengas que darnos deben ir en el archivo `challenge.md` dentro de la carpeta `docs`.

5. Para enviar tu desafío, debes realizar una solicitud `POST` a:
    `https://advana-challenge-check-api-cr-k4hdbggvoq-uc.a.run.app/software-engineer`
    Este es un ejemplo del `cuerpo` que debes enviar:
    ```json
    {
      "name": "Juan Perez",
      "mail": "juan.perez@example.com",
      "github_url": "https://github.com/juanperez/latam-challenge.git",
      "api_url": "https://juan-perez.api"
    }
    ```
    ##### ***POR FAVOR, ENVÍE LA SOLICITUD UNA VEZ***

    Si su solicitud fue exitosa, recibirá este mensaje:
    ```json
    {
      "status": "OK",
      "detail": "your request was received"
    }
    ```


***NOTA: Te recomendamos enviar el desafío incluso si no lograste completar todas las partes.***

### Context:

Necesitamos operacionalizar el trabajo de ciencia de datos para el equipo del aeropuerto. Para ello, hemos decidido habilitar una `API` en la que puedan consultar la predicción de retraso de un vuelo.

*Recomendamos leer todo el desafío (todas sus partes) antes de comenzar a desarrollar.*

### Part I

Para operacionalizar el modelo, transcribe el archivo `.ipynb` en el archivo `model.py`:

- Si encuentras algún error, corrígelo.
- El CD propuso algunos modelos al final. Elige el mejor modelo a tu discreción y argumenta por qué. No es necesario mejorar el modelo.
- Aplica todas las buenas prácticas de programación que consideres necesarias en este ítem.
- El modelo debe pasar las pruebas ejecutando `make model-test`.

>**Nota:**

>**No puedes** eliminar o cambiar el nombre o los argumentos de los métodos proporcionados.
>**Puedes** cambiar/completar la implementación de los métodos proporcionados.
>**Puedes** crear las clases y métodos adicionales que consideres necesarios.

### Part II

Despliega el modelo en una `API` con `FastAPI` utilizando el archivo `api.py`.

- La `API` debe pasar las pruebas ejecutando `make api-test`.
> **Nota:**
> - **No puedes** usar otro framework.

### Part III

Despliega la `API` en tu proveedor de nube favorito (recomendamos usar GCP).

- Coloca la URL de la `API` en el `Makefile` (`line 26`).
- La `API` debe pasar las pruebas ejecutando `make stress-test`.

> **Nota:**

> - **Es importante que la API esté desplegada hasta que revisemos las pruebas.**

### Part IV

Estamos buscando una implementación adecuada de `CI/CD` para este desarrollo.

- Crea una nueva carpeta llamada `.github` y copia la carpeta `workflows` que te proporcionamos dentro de ella.
- Completa tanto `ci.yml` como `cd.yml` (considera lo que hiciste en las partes anteriores).