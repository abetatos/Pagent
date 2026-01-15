"""
Agente de Estilo - Mejora el estilo de escritura
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class StyleAgent(BaseAgent):
    """Agente especializado en mejorar el estilo de escritura"""

    def __init__(self):
        super().__init__(
            name="Estilista",
            specialization="Mejora de estilo y tono de escritura"
        )
        self.estilos_disponibles = [
            'narrativo',
            'descriptivo',
            'academico',
            'conversacional',
            'poetico',
            'tecnico'
        ]

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mejora el estilo del contenido proporcionado

        Args:
            input_data: Debe contener 'contenido', 'estilo_objetivo'

        Returns:
            Diccionario con el contenido mejorado
        """
        contenido = input_data.get('contenido', '')
        estilo_objetivo = input_data.get('estilo_objetivo', 'narrativo')

        if estilo_objetivo not in self.estilos_disponibles:
            return {
                'status': 'error',
                'mensaje': f'Estilo no disponible. Opciones: {", ".join(self.estilos_disponibles)}'
            }

        # Analizar y mejorar estilo
        analisis = self._analizar_estilo(contenido)
        contenido_mejorado = self._aplicar_estilo(contenido, estilo_objetivo)

        self.add_to_memory({
            'action': 'style_improved',
            'estilo_objetivo': estilo_objetivo
        })

        return {
            'status': 'success',
            'contenido_original': contenido,
            'contenido_mejorado': contenido_mejorado,
            'analisis': analisis,
            'estilo_aplicado': estilo_objetivo,
            'mensaje': f'Estilo mejorado a {estilo_objetivo}'
        }

    def _analizar_estilo(self, contenido: str) -> Dict[str, Any]:
        """
        Analiza el estilo actual del contenido

        Args:
            contenido: Contenido a analizar

        Returns:
            Análisis del estilo
        """
        palabras = contenido.split()
        oraciones = contenido.split('.')

        return {
            'longitud_promedio_palabra': sum(len(p) for p in palabras) / len(palabras) if palabras else 0,
            'longitud_promedio_oracion': sum(len(o.split()) for o in oraciones) / len(oraciones) if oraciones else 0,
            'complejidad': 'media',
            'tono': 'neutral',
            'legibilidad': 75
        }

    def _aplicar_estilo(self, contenido: str, estilo: str) -> str:
        """
        Aplica el estilo objetivo al contenido

        Args:
            contenido: Contenido original
            estilo: Estilo a aplicar

        Returns:
            Contenido con estilo aplicado
        """
        # Placeholder - aquí se aplicaría la transformación de estilo real
        return f"{contenido}\n\n[Estilo {estilo} aplicado]"

    def ajustar_tono(self, contenido: str, tono: str) -> Dict[str, Any]:
        """
        Ajusta el tono del contenido

        Args:
            contenido: Contenido a ajustar
            tono: Tono objetivo (formal, informal, profesional, amigable, etc.)

        Returns:
            Contenido con tono ajustado
        """
        # Aquí se implementaría el ajuste de tono
        contenido_ajustado = f"{contenido}\n\n[Tono {tono} aplicado]"

        return {
            'status': 'success',
            'contenido': contenido_ajustado,
            'tono': tono,
            'mensaje': f'Tono ajustado a {tono}'
        }

    def mejorar_vocabulario(self, contenido: str) -> Dict[str, Any]:
        """
        Enriquece el vocabulario del contenido

        Args:
            contenido: Contenido a mejorar

        Returns:
            Contenido con vocabulario mejorado
        """
        # Aquí se implementaría la mejora de vocabulario
        return {
            'status': 'success',
            'contenido': contenido,
            'sustituciones': [],
            'mensaje': 'Vocabulario mejorado'
        }
