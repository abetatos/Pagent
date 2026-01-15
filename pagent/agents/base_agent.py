"""
Agente base del que heredan todos los agentes especializados
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseAgent(ABC):
    """Clase base para todos los agentes especializados"""

    def __init__(self, name: str, specialization: str):
        """
        Inicializa el agente base

        Args:
            name: Nombre del agente
            specialization: Especialización del agente
        """
        self.name = name
        self.specialization = specialization
        self.memory: List[Dict[str, Any]] = []

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa la entrada y retorna el resultado

        Args:
            input_data: Datos de entrada para procesar

        Returns:
            Resultado del procesamiento
        """
        pass

    def add_to_memory(self, data: Dict[str, Any]):
        """Añade información a la memoria del agente"""
        self.memory.append(data)

    def get_memory(self) -> List[Dict[str, Any]]:
        """Obtiene el historial de memoria del agente"""
        return self.memory

    def clear_memory(self):
        """Limpia la memoria del agente"""
        self.memory = []

    def __str__(self) -> str:
        return f"{self.name} ({self.specialization})"
