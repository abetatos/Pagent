"""
Agente Escritor - Escribe el contenido de los capítulos
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class WriterAgent(BaseAgent):
    """Agente especializado en escribir contenido"""

    def __init__(self):
        super().__init__(
            name="Escritor",
            specialization="Escritura de contenido y capítulos"
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Escribe el contenido de un capítulo

        Args:
            input_data: Debe contener 'capitulo_info', 'contexto'

        Returns:
            Diccionario con el contenido generado
        """
        capitulo_info = input_data.get('capitulo_info', {})
        contexto = input_data.get('contexto', '')
        estilo = input_data.get('estilo', 'narrativo')

        numero = capitulo_info.get('numero', 1)
        titulo = capitulo_info.get('titulo', f'Capítulo {numero}')

        # Generar contenido (placeholder - aquí iría la lógica de generación real)
        contenido = self._generar_contenido(titulo, contexto, estilo)

        resultado = {
            'numero_capitulo': numero,
            'titulo': titulo,
            'contenido': contenido,
            'palabras': len(contenido.split())
        }

        self.add_to_memory({
            'action': 'chapter_written',
            'capitulo': numero,
            'palabras': len(contenido.split())
        })

        return {
            'status': 'success',
            'resultado': resultado,
            'mensaje': f'Capítulo {numero} escrito exitosamente'
        }

    def _generar_contenido(self, titulo: str, contexto: str, estilo: str) -> str:
        """
        Genera el contenido del capítulo

        Args:
            titulo: Título del capítulo
            contexto: Contexto del libro
            estilo: Estilo de escritura

        Returns:
            Contenido generado
        """
        # Placeholder - aquí se integraría con un LLM para generar contenido real
        return f"""
# {titulo}

Este es el contenido del capítulo generado en estilo {estilo}.

Contexto: {contexto}

[Aquí iría el contenido completo del capítulo generado por un modelo de lenguaje]

Este es un sistema de ejemplo que demuestra la arquitectura multi-agente.
Para generar contenido real, se debe integrar con APIs de LLMs como:
- OpenAI GPT
- Anthropic Claude
- Google Gemini
- Modelos locales (Llama, Mistral, etc.)
        """.strip()

    def reescribir_seccion(self, contenido: str, instrucciones: str) -> Dict[str, Any]:
        """
        Reescribe una sección específica del contenido

        Args:
            contenido: Contenido original
            instrucciones: Instrucciones para la reescritura

        Returns:
            Contenido reescrito
        """
        # Aquí iría la lógica de reescritura
        contenido_modificado = f"{contenido}\n\n[Modificado según: {instrucciones}]"

        return {
            'status': 'success',
            'contenido': contenido_modificado,
            'mensaje': 'Sección reescrita exitosamente'
        }
