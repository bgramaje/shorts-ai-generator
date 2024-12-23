from openai import OpenAI
from utils import settings
import json

def chatgpt_video_content(question):
    """Function to ask ChatGPT a question and return the response."""
    
    client = OpenAI(
        api_key=settings.config["settings"]["openai"].get("api_key", None)
    )

    system_message = """
        Genera contenido para videos cortos de YouTube sobre curiosidades de animes. 
        Incluye para empezar el video una pregunta retórica para atraer al espectador. 
        Incluye un texto sin vocabulario complejo que se pueda leer en un minuto como `content`, un título atractivo como `title`, una descripción llamativa como `description`, y tags relevantes separados por comas como `tags`. Devuelve todo el contenido únicamente en formato JSON, utilizando las siguientes claves:
        {
        "title": "Título del video",
        "description": "Descripción del video",
        "content": "Texto para el short que se puede leer en un minuto",
        "tags": "tag1, tag2, tag3"
        }

        El contenido debe ser atractivo, informativo y fácil de entender para el público en general, manteniendo un tono entusiasta y utilizando elementos culturales cuando sea relevante. Además, considera que el texto será utilizado para text-to-speech, por lo que debe ser fácilmente entendible, evitando palabras poco comunes y minimizando el riesgo de errores o palabras malsonantes en el discurso resultante.
        Ten en cuenta  que el texto que vayas a facilitarme, será usado para realizar text-to-speech, por tanto, tiene que ser facilmente interpretable por estos modelos.
        El short debe de tener un contenido de 40-50 segundos
        Devuelve el contenido JSON en una linea.
    """


    response = client.chat.completions.create(
        model="gpt-4o",  # You can also use "gpt-4" if you have access to it
        messages=[
            { "role": "system", "content": system_message },
            {"role": "user", "content": question},
        ],
        max_tokens=400  
    )
    # Extract the response content
    answer = response.choices[0].message.content
    return answer


def load_openai_response(response):
    try:
        data = json.loads(response)
        expected_keys = {"title", "description", "content", "tags"}

        missing_keys = expected_keys - data.keys()

        if missing_keys:
            print("Faltan las siguientes claves:", missing_keys)
        
        return data
    except json.JSONDecodeError as e:
        print("Error al decodificar el JSON:", str(e))
        return None
    except Exception as e:
        print("Se produjo un error inesperado:", str(e))
        return None