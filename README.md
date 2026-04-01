# CV-LLM - Analizador de Currículum con IA

Aplicación web para analizar CVs utilizando inteligencia artificial. Sube un currículum en PDF y chatea con él para extraer información, o compara el perfil con palabras clave de una vacante.

## Características

- 📄 **Subir CV** - Arrastra y suelta un archivo PDF
- 💬 **Chat con IA** - Haz preguntas sobre el CV cargado
- 🔍 **Match de Vacantes** - Compara el perfil con palabras clave
- 🎨 **Interfaz Moderna** - Diseño oscuro y responsivo

## Requisitos

- Python 3.10+
- API Key de Groq (gratis)

## Instalación Local

### 1. Clonar el repositorio

```bash
git clone https://github.com/MorenDevEng/CV-LLM.git
cd CV-LLM
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv env
env\Scripts\activate

# Linux/Mac
python -m venv env
source env/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
GROQ_API_KEY=tu_api_key_aqui
```

Para obtener tu API Key:
1. Ve a [groq.com](https://groq.com)
2. Regístrate gratis
3. Copia tu API Key

### 5. Ejecutar la aplicación

```bash
python src/app.py
```

Abre tu navegador en: **http://127.0.0.1:5000**

## Docker

### Construir imagen

```bash
docker build -t cv-llm .
```

### Ejecutar contenedor

```bash
docker run -p 5000:5000 --env-file .env cv-llm
```

## Uso

1. **Sube un CV** - Arrastra un archivo PDF al área designada
2. **Espera el procesamiento** - El sistema generará los embeddings
3. **Chatea** - Haz preguntas como "¿Cuál es la experiencia profesional?"
4. **Compara con vacantes** - Ingresa palabras clave separadas por coma

## Tecnologías

- **Backend**: Flask
- **IA**: LangChain + Groq (Llama 3.3)
- **Base de datos**: ChromaDB
- **Frontend**: HTML/CSS/JS

## Licencia

MIT
