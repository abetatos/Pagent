"""
Pagent - Sistema Multi-Agente para Escritura de Libros
"""

__version__ = "1.0.0"
__author__ = "Pagent Team"

from .orchestrator import BookOrchestrator
from .agents.base_agent import BaseAgent

__all__ = ['BookOrchestrator', 'BaseAgent']
