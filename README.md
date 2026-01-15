# 📚 Pagent - Sistema Multi-Agente para Escritura de Libros

**Pagent** es un sistema avanzado de inteligencia artificial que utiliza múltiples agentes especializados para crear libros de manera colaborativa y automatizada. Cada agente se especializa en una tarea específica del proceso de escritura, permitiendo generar contenido de alta calidad de forma estructurada y coherente.

## 🎯 Características Principales

- **Sistema Multi-Agente**: 6 agentes especializados trabajando en conjunto
- **Arquitectura Modular**: Fácil de extender y personalizar
- **Selección Flexible**: Elige qué agentes utilizar según tus necesidades
- **Proceso Automatizado**: Desde la planificación hasta la edición final
- **Coherencia Garantizada**: Verificación automática de consistencia narrativa
- **Múltiples Estilos**: Soporte para diferentes géneros y estilos de escritura

## 🤖 Agentes Especializados

### 1. **Planificador** 📋
- Crea la estructura y outline del libro
- Define capítulos y temas principales
- Organiza el flujo narrativo

### 2. **Investigador** 🔍
- Busca y recopila información relevante
- Verifica datos y hechos
- Proporciona referencias bibliográficas

### 3. **Escritor** ✍️
- Genera el contenido de los capítulos
- Desarrolla narrativas y argumentos
- Adapta el contenido al género específico

### 4. **Editor** 📝
- Revisa y mejora el contenido
- Corrige errores gramaticales
- Optimiza la estructura del texto

### 5. **Estilista** 🎨
- Mejora el estilo de escritura
- Ajusta el tono y vocabulario
- Aplica estilos específicos (narrativo, académico, conversacional, etc.)

### 6. **Revisor de Coherencia** 🔄
- Verifica la coherencia narrativa
- Mantiene consistencia de personajes y eventos
- Asegura continuidad entre capítulos

## 🚀 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tuusuario/Pagent.git
cd Pagent

# Instalar dependencias
pip install -r requirements.txt
```

## 💡 Uso Básico

### Ejemplo 1: Crear un libro completo con todos los agentes

```python
from pagent import BookOrchestrator

# Inicializar el orquestador
orquestador = BookOrchestrator()

# Seleccionar agentes a utilizar
orquestador.seleccionar_agentes([
    'planificador',
    'investigador',
    'escritor',
    'editor',
    'estilista',
    'coherencia'
])

# Configurar el libro
config = {
    'tema': 'Inteligencia Artificial y el futuro',
    'genero': 'divulgacion',
    'num_capitulos': 10,
    'estilo': 'academico',
    'profundidad_investigacion': 'alta'
}

# Crear el libro
libro = orquestador.crear_libro(config)

# El libro contiene:
# - libro['metadata']: Información del libro
# - libro['estructura']: Outline y estructura
# - libro['capitulos']: Lista de capítulos generados
# - libro['estadisticas']: Estadísticas del libro
```

### Ejemplo 2: Uso selectivo de agentes

```python
from pagent import BookOrchestrator

# Usar solo planificador y escritor
orquestador = BookOrchestrator()
orquestador.seleccionar_agentes(['planificador', 'escritor'])

config = {
    'tema': 'Aventuras en el espacio',
    'genero': 'ciencia ficcion',
    'num_capitulos': 15
}

libro = orquestador.crear_libro(config)
```

### Ejemplo 3: Ejecutar agentes individuales

```python
from pagent import BookOrchestrator

orquestador = BookOrchestrador()

# Ejecutar solo el investigador
resultado = orquestador.ejecutar_agente('investigador', {
    'tema': 'Cambio climático',
    'profundidad': 'alta',
    'fuentes': ['academico', 'cientifico']
})

print(resultado['informacion'])

# Ejecutar solo el planificador
plan = orquestador.ejecutar_agente('planificador', {
    'tema': 'Historia de Roma',
    'genero': 'historico',
    'num_capitulos': 20
})

print(plan['estructura'])
```

## 🔧 Configuración Avanzada

### Estilos de Escritura Disponibles

- `narrativo`: Para novelas y relatos
- `descriptivo`: Para descripciones detalladas
- `academico`: Para textos científicos y técnicos
- `conversacional`: Para blogs y contenido informal
- `poetico`: Para contenido literario y artístico
- `tecnico`: Para documentación y manuales

### Géneros Soportados

- Ficción: ciencia ficción, fantasía, thriller, romance, terror
- No ficción: biografía, historia, divulgación, ensayo, autoayuda
- Académico: investigación, tesis, paper científico
- Técnico: manuales, tutoriales, documentación

## 📊 Ejemplo de Salida

```python
{
    'metadata': {
        'tema': 'Inteligencia Artificial',
        'genero': 'divulgacion',
        'estilo': 'academico'
    },
    'estructura': {
        'titulo': 'Libro sobre Inteligencia Artificial',
        'sinopsis': '...',
        'capitulos': [...]
    },
    'capitulos': [
        {
            'numero_capitulo': 1,
            'titulo': 'Introducción a la IA',
            'contenido': '...',
            'palabras': 2500,
            'sugerencias_editor': [...],
            'analisis_estilo': {...}
        },
        ...
    ],
    'estadisticas': {
        'total_capitulos': 10,
        'total_palabras': 25000,
        'promedio_palabras_capitulo': 2500,
        'agentes_utilizados': ['planificador', 'escritor', 'editor', ...]
    },
    'coherencia': {
        'coherente': True,
        'problemas': [],
        'num_problemas': 0
    }
}
```

## 🏗️ Arquitectura del Sistema

```
Pagent/
├── pagent/
│   ├── __init__.py
│   ├── orchestrator.py          # Orquestador principal
│   └── agents/
│       ├── __init__.py
│       ├── base_agent.py        # Clase base para agentes
│       ├── planner_agent.py     # Agente planificador
│       ├── writer_agent.py      # Agente escritor
│       ├── editor_agent.py      # Agente editor
│       ├── researcher_agent.py  # Agente investigador
│       ├── style_agent.py       # Agente de estilo
│       └── coherence_agent.py   # Agente de coherencia
├── examples/
│   ├── basic_usage.py           # Ejemplos básicos
│   └── advanced_usage.py        # Ejemplos avanzados
├── requirements.txt
├── LICENSE
└── README.md
```

## 🔌 Integración con LLMs

Pagent está diseñado para integrarse con modelos de lenguaje grandes (LLMs). Para generar contenido real, puedes integrar:

- **OpenAI GPT-4/GPT-3.5**
- **Anthropic Claude**
- **Google Gemini**
- **Modelos locales**: Llama, Mistral, etc. vía Ollama o LM Studio

Ejemplo de integración:

```python
# En writer_agent.py o cualquier agente que genere contenido
import openai

def _generar_contenido(self, titulo, contexto, estilo):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Eres un escritor experto en estilo {estilo}"},
            {"role": "user", "content": f"Escribe un capítulo titulado '{titulo}'. Contexto: {contexto}"}
        ]
    )
    return response.choices[0].message.content
```

## 🛠️ Personalización

### Crear un Agente Personalizado

```python
from pagent.agents.base_agent import BaseAgent

class MiAgentePersonalizado(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Mi Agente",
            specialization="Especialización específica"
        )

    def process(self, input_data):
        # Tu lógica personalizada aquí
        return {
            'status': 'success',
            'resultado': 'Mi resultado'
        }
```

### Agregar el Agente al Orquestador

```python
# En orchestrator.py
self.agentes_disponibles['mi_agente'] = MiAgentePersonalizado()
```

## 📈 Roadmap

- [ ] Integración nativa con APIs de LLMs populares
- [ ] Interfaz gráfica de usuario (GUI)
- [ ] Exportación a múltiples formatos (PDF, EPUB, DOCX)
- [ ] Soporte multiidioma
- [ ] Plantillas predefinidas por género
- [ ] Sistema de plugins para agentes personalizados
- [ ] Colaboración en tiempo real
- [ ] Análisis de sentimiento y emociones
- [ ] Generación de imágenes para ilustraciones

## 🤝 Contribuciones

Este proyecto tiene una licencia restrictiva que **NO permite contribuciones** ni distribución del código. El código es visible únicamente con fines educativos e instructivos.

## 📄 Licencia

Este software está protegido bajo una licencia restrictiva. Ver [LICENSE](LICENSE) para más detalles.

**Resumen de la licencia:**
- ❌ NO se permite uso comercial
- ❌ NO se permite distribución
- ❌ NO se permite modificación para redistribución
- ✅ SÍ se permite visualizar el código fuente
- ✅ SÍ se permite usar para aprendizaje personal
- ✅ SÍ se permite uso no comercial con fines instructivos

## 👨‍💻 Autor

Desarrollado por el equipo de Pagent

## 📧 Contacto

Para consultas sobre licencias comerciales o uso empresarial, contactar a: [tu-email@ejemplo.com]

## ⚠️ Disclaimer

Este es un sistema de demostración que muestra la arquitectura de un sistema multi-agente. Para generar contenido real de calidad, es necesario integrar modelos de lenguaje apropiados (GPT-4, Claude, etc.) y ajustar los prompts según las necesidades específicas.

## 🌟 Casos de Uso

- **Escritores**: Acelera tu proceso de escritura
- **Educadores**: Genera material educativo estructurado
- **Empresas**: Crea documentación técnica automáticamente
- **Investigadores**: Genera drafts de papers y artículos
- **Creadores de contenido**: Produce libros electrónicos y guías

---

**Nota**: Este software está en desarrollo activo. Las características y API pueden cambiar sin previo aviso.
