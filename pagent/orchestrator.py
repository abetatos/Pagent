"""
Orquestador de Agentes - Coordina y gestiona todos los agentes especializados
"""

from typing import Dict, Any, List, Optional
from .agents import (
    PlannerAgent,
    WriterAgent,
    EditorAgent,
    ResearcherAgent,
    StyleAgent,
    CoherenceAgent
)


class BookOrchestrator:
    """Orquestador principal que coordina todos los agentes para crear un libro"""

    def __init__(self):
        """Inicializa el orquestador y todos los agentes"""
        self.agentes_disponibles = {
            'planificador': PlannerAgent(),
            'escritor': WriterAgent(),
            'editor': EditorAgent(),
            'investigador': ResearcherAgent(),
            'estilista': StyleAgent(),
            'coherencia': CoherenceAgent()
        }
        self.agentes_activos = []
        self.contexto_libro = {}
        self.historial = []

    def seleccionar_agentes(self, nombres_agentes: List[str]) -> Dict[str, Any]:
        """
        Selecciona los agentes que participarán en la creación del libro

        Args:
            nombres_agentes: Lista de nombres de agentes a activar

        Returns:
            Resultado de la selección
        """
        agentes_seleccionados = []
        agentes_no_encontrados = []

        for nombre in nombres_agentes:
            if nombre in self.agentes_disponibles:
                agentes_seleccionados.append(nombre)
            else:
                agentes_no_encontrados.append(nombre)

        self.agentes_activos = agentes_seleccionados

        return {
            'status': 'success',
            'agentes_activos': agentes_seleccionados,
            'agentes_no_encontrados': agentes_no_encontrados,
            'mensaje': f'{len(agentes_seleccionados)} agentes activados'
        }

    def listar_agentes_disponibles(self) -> List[Dict[str, str]]:
        """
        Lista todos los agentes disponibles con sus especializaciones

        Returns:
            Lista de agentes con información
        """
        return [
            {
                'nombre': nombre,
                'especialization': agente.specialization,
                'activo': nombre in self.agentes_activos
            }
            for nombre, agente in self.agentes_disponibles.items()
        ]

    def crear_libro(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Proceso completo de creación de un libro

        Args:
            config: Configuración del libro (tema, género, estilo, etc.)

        Returns:
            Libro completo generado
        """
        if not self.agentes_activos:
            # Activar agentes por defecto
            self.seleccionar_agentes(['planificador', 'escritor', 'editor'])

        resultado = {
            'metadata': config,
            'estructura': {},
            'capitulos': [],
            'estadisticas': {}
        }

        # Fase 1: Planificación
        if 'planificador' in self.agentes_activos:
            print("📋 Fase 1: Planificando estructura del libro...")
            plan = self._ejecutar_planificacion(config)
            resultado['estructura'] = plan
            self.contexto_libro['estructura'] = plan

        # Fase 2: Investigación (si está activo)
        if 'investigador' in self.agentes_activos:
            print("🔍 Fase 2: Investigando temas relevantes...")
            investigacion = self._ejecutar_investigacion(config)
            self.contexto_libro['investigacion'] = investigacion

        # Fase 3: Escritura
        if 'escritor' in self.agentes_activos:
            print("✍️  Fase 3: Escribiendo capítulos...")
            capitulos = self._ejecutar_escritura(resultado['estructura'])
            resultado['capitulos'] = capitulos

        # Fase 4: Edición (si está activo)
        if 'editor' in self.agentes_activos:
            print("📝 Fase 4: Editando contenido...")
            resultado['capitulos'] = self._ejecutar_edicion(resultado['capitulos'])

        # Fase 5: Mejora de estilo (si está activo)
        if 'estilista' in self.agentes_activos:
            print("🎨 Fase 5: Mejorando estilo...")
            resultado['capitulos'] = self._ejecutar_mejora_estilo(
                resultado['capitulos'],
                config.get('estilo', 'narrativo')
            )

        # Fase 6: Verificación de coherencia (si está activo)
        if 'coherencia' in self.agentes_activos:
            print("🔄 Fase 6: Verificando coherencia...")
            verificacion = self._ejecutar_verificacion_coherencia(resultado['capitulos'])
            resultado['coherencia'] = verificacion

        # Estadísticas finales
        resultado['estadisticas'] = self._calcular_estadisticas(resultado)

        self._registrar_en_historial('libro_creado', resultado)

        return resultado

    def _ejecutar_planificacion(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta la fase de planificación"""
        agente = self.agentes_disponibles['planificador']
        resultado = agente.process(config)
        return resultado.get('estructura', {})

    def _ejecutar_investigacion(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta la fase de investigación"""
        agente = self.agentes_disponibles['investigador']
        resultado = agente.process({
            'tema': config.get('tema', ''),
            'profundidad': config.get('profundidad_investigacion', 'media')
        })
        return resultado.get('informacion', {})

    def _ejecutar_escritura(self, estructura: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ejecuta la fase de escritura"""
        agente = self.agentes_disponibles['escritor']
        capitulos = []

        for cap_info in estructura.get('capitulos', []):
            resultado = agente.process({
                'capitulo_info': cap_info,
                'contexto': self.contexto_libro
            })
            capitulos.append(resultado.get('resultado', {}))

        return capitulos

    def _ejecutar_edicion(self, capitulos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ejecuta la fase de edición"""
        agente = self.agentes_disponibles['editor']
        capitulos_editados = []

        for capitulo in capitulos:
            resultado = agente.process({
                'contenido': capitulo.get('contenido', '')
            })
            capitulo['contenido'] = resultado.get('contenido_editado', capitulo.get('contenido', ''))
            capitulo['sugerencias_editor'] = resultado.get('sugerencias', [])
            capitulos_editados.append(capitulo)

        return capitulos_editados

    def _ejecutar_mejora_estilo(self, capitulos: List[Dict[str, Any]], estilo: str) -> List[Dict[str, Any]]:
        """Ejecuta la fase de mejora de estilo"""
        agente = self.agentes_disponibles['estilista']
        capitulos_mejorados = []

        for capitulo in capitulos:
            resultado = agente.process({
                'contenido': capitulo.get('contenido', ''),
                'estilo_objetivo': estilo
            })
            capitulo['contenido'] = resultado.get('contenido_mejorado', capitulo.get('contenido', ''))
            capitulo['analisis_estilo'] = resultado.get('analisis', {})
            capitulos_mejorados.append(capitulo)

        return capitulos_mejorados

    def _ejecutar_verificacion_coherencia(self, capitulos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Ejecuta la verificación de coherencia"""
        agente = self.agentes_disponibles['coherencia']
        problemas_totales = []

        for i, capitulo in enumerate(capitulos):
            contexto_previo = {
                'capitulos_anteriores': capitulos[:i] if i > 0 else []
            }

            resultado = agente.process({
                'contenido': capitulo.get('contenido', ''),
                'contexto_previo': contexto_previo
            })

            if not resultado.get('coherente', True):
                problemas_totales.extend(resultado.get('problemas', []))

        return {
            'coherente': len(problemas_totales) == 0,
            'problemas': problemas_totales,
            'num_problemas': len(problemas_totales)
        }

    def _calcular_estadisticas(self, resultado: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula estadísticas del libro generado"""
        capitulos = resultado.get('capitulos', [])

        total_palabras = sum(cap.get('palabras', 0) for cap in capitulos)
        total_capitulos = len(capitulos)

        return {
            'total_capitulos': total_capitulos,
            'total_palabras': total_palabras,
            'promedio_palabras_capitulo': total_palabras // total_capitulos if total_capitulos > 0 else 0,
            'agentes_utilizados': self.agentes_activos
        }

    def _registrar_en_historial(self, accion: str, datos: Any):
        """Registra una acción en el historial"""
        self.historial.append({
            'accion': accion,
            'datos': datos
        })

    def ejecutar_agente(self, nombre_agente: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta un agente específico manualmente

        Args:
            nombre_agente: Nombre del agente a ejecutar
            input_data: Datos de entrada para el agente

        Returns:
            Resultado de la ejecución del agente
        """
        if nombre_agente not in self.agentes_disponibles:
            return {
                'status': 'error',
                'mensaje': f'Agente "{nombre_agente}" no encontrado'
            }

        agente = self.agentes_disponibles[nombre_agente]
        resultado = agente.process(input_data)

        self._registrar_en_historial(f'agente_{nombre_agente}', resultado)

        return resultado

    def obtener_historial(self) -> List[Dict[str, Any]]:
        """Obtiene el historial de acciones"""
        return self.historial

    def limpiar_contexto(self):
        """Limpia el contexto y reinicia el orquestador"""
        self.contexto_libro = {}
        self.historial = []
        for agente in self.agentes_disponibles.values():
            agente.clear_memory()
