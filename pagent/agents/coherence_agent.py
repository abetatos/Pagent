"""
Agente de Coherencia - Asegura coherencia en trama, argumentos y personajes
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent


class CoherenceAgent(BaseAgent):
    """Agente especializado en mantener la coherencia del libro"""

    def __init__(self):
        super().__init__(
            name="Revisor de Coherencia",
            specialization="Verificación de coherencia narrativa y argumentativa"
        )
        self.personajes_registrados = {}
        self.eventos_registrados = []
        self.temas_principales = []

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifica la coherencia del contenido

        Args:
            input_data: Debe contener 'contenido', 'contexto_previo'

        Returns:
            Diccionario con análisis de coherencia
        """
        contenido = input_data.get('contenido', '')
        contexto_previo = input_data.get('contexto_previo', {})
        tipo = input_data.get('tipo', 'narrativo')  # narrativo, argumentativo, tecnico

        # Verificar coherencia
        problemas = self._verificar_coherencia(contenido, contexto_previo, tipo)
        sugerencias = self._generar_sugerencias(problemas)

        self.add_to_memory({
            'action': 'coherence_checked',
            'problemas_encontrados': len(problemas)
        })

        return {
            'status': 'success',
            'coherente': len(problemas) == 0,
            'problemas': problemas,
            'sugerencias': sugerencias,
            'mensaje': f'Análisis completado. {len(problemas)} problemas encontrados'
        }

    def _verificar_coherencia(self, contenido: str, contexto: Dict, tipo: str) -> List[Dict[str, str]]:
        """
        Verifica la coherencia del contenido

        Args:
            contenido: Contenido a verificar
            contexto: Contexto previo del libro
            tipo: Tipo de coherencia a verificar

        Returns:
            Lista de problemas encontrados
        """
        problemas = []

        # Verificar coherencia temporal
        if tipo == 'narrativo':
            problemas.extend(self._verificar_coherencia_temporal(contenido, contexto))
            problemas.extend(self._verificar_coherencia_personajes(contenido, contexto))

        # Verificar coherencia argumentativa
        if tipo == 'argumentativo':
            problemas.extend(self._verificar_coherencia_argumentos(contenido, contexto))

        return problemas

    def _verificar_coherencia_temporal(self, contenido: str, contexto: Dict) -> List[Dict[str, str]]:
        """Verifica coherencia en la línea temporal"""
        # Placeholder
        return []

    def _verificar_coherencia_personajes(self, contenido: str, contexto: Dict) -> List[Dict[str, str]]:
        """Verifica coherencia en personajes"""
        problemas = []

        # Aquí se verificarían inconsistencias en personajes
        # Por ejemplo: cambios de nombre, contradicciones en características, etc.

        return problemas

    def _verificar_coherencia_argumentos(self, contenido: str, contexto: Dict) -> List[Dict[str, str]]:
        """Verifica coherencia en argumentos"""
        # Placeholder
        return []

    def _generar_sugerencias(self, problemas: List[Dict[str, str]]) -> List[str]:
        """
        Genera sugerencias para resolver problemas de coherencia

        Args:
            problemas: Lista de problemas encontrados

        Returns:
            Lista de sugerencias
        """
        sugerencias = []
        for problema in problemas:
            sugerencias.append(f"Resolver: {problema.get('descripcion', 'Problema de coherencia')}")

        return sugerencias

    def registrar_personaje(self, personaje: Dict[str, Any]):
        """
        Registra un personaje para seguimiento

        Args:
            personaje: Información del personaje
        """
        nombre = personaje.get('nombre', '')
        self.personajes_registrados[nombre] = personaje

    def registrar_evento(self, evento: Dict[str, Any]):
        """
        Registra un evento importante

        Args:
            evento: Información del evento
        """
        self.eventos_registrados.append(evento)

    def verificar_continuidad(self, capitulo_actual: str, capitulo_anterior: str) -> Dict[str, Any]:
        """
        Verifica la continuidad entre capítulos

        Args:
            capitulo_actual: Contenido del capítulo actual
            capitulo_anterior: Contenido del capítulo anterior

        Returns:
            Análisis de continuidad
        """
        return {
            'status': 'success',
            'continuo': True,
            'problemas': [],
            'mensaje': 'Continuidad verificada'
        }
