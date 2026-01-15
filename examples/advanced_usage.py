"""
Ejemplos avanzados de uso de Pagent
Casos de uso más complejos y personalizaciones
"""

from pagent import BookOrchestrator
from pagent.agents.base_agent import BaseAgent


def ejemplo_avanzado_1_workflow_personalizado():
    """Workflow personalizado con control fino de cada fase"""
    print("=" * 70)
    print("EJEMPLO AVANZADO 1: Workflow personalizado")
    print("=" * 70)

    orquestador = BookOrchestrator()

    # Fase 1: Planificación inicial
    print("\n📋 FASE 1: Planificación inicial")
    plan = orquestador.ejecutar_agente('planificador', {
        'tema': 'Machine Learning en la práctica',
        'genero': 'tecnico',
        'num_capitulos': 12
    })

    estructura = plan['estructura']
    print(f"✓ Plan creado: {len(estructura['capitulos'])} capítulos")

    # Fase 2: Investigación profunda
    print("\n🔍 FASE 2: Investigación profunda")
    investigacion = orquestador.ejecutar_agente('investigador', {
        'tema': 'Machine Learning algoritmos y aplicaciones',
        'profundidad': 'alta'
    })
    print(f"✓ Investigación completada: {len(investigacion['informacion']['puntos_clave'])} puntos clave")

    # Fase 3: Escritura iterativa con feedback
    print("\n✍️  FASE 3: Escritura iterativa")
    capitulos_escritos = []

    for i, cap_info in enumerate(estructura['capitulos'][:3], 1):  # Primeros 3 capítulos
        print(f"  Escribiendo capítulo {i}...")

        # Escribir
        resultado = orquestador.ejecutar_agente('escritor', {
            'capitulo_info': cap_info,
            'contexto': {
                'estructura': estructura,
                'investigacion': investigacion['informacion']
            }
        })

        capitulo = resultado['resultado']

        # Editar
        editado = orquestador.ejecutar_agente('editor', {
            'contenido': capitulo['contenido']
        })

        # Mejorar estilo
        estilizado = orquestador.ejecutar_agente('estilista', {
            'contenido': editado['contenido_editado'],
            'estilo_objetivo': 'tecnico'
        })

        capitulo['contenido'] = estilizado['contenido_mejorado']
        capitulos_escritos.append(capitulo)

        print(f"  ✓ Capítulo {i} completado: {capitulo['palabras']} palabras")

    # Fase 4: Verificación de coherencia
    print("\n🔄 FASE 4: Verificación de coherencia")
    for i, capitulo in enumerate(capitulos_escritos, 1):
        contexto_previo = {
            'capitulos_anteriores': capitulos_escritos[:i-1]
        }

        coherencia = orquestador.ejecutar_agente('coherencia', {
            'contenido': capitulo['contenido'],
            'contexto_previo': contexto_previo
        })

        estado = "✓" if coherencia['coherente'] else "⚠"
        print(f"  {estado} Capítulo {i}: {len(coherencia['problemas'])} problemas encontrados")

    print("\n✅ Workflow personalizado completado")


def ejemplo_avanzado_2_agente_personalizado():
    """Crear y usar un agente personalizado"""
    print("\n\n" + "=" * 70)
    print("EJEMPLO AVANZADO 2: Agente personalizado")
    print("=" * 70)

    # Definir un agente personalizado
    class SEOAgent(BaseAgent):
        """Agente especializado en optimización SEO de contenido"""

        def __init__(self):
            super().__init__(
                name="SEO Optimizer",
                specialization="Optimización de contenido para motores de búsqueda"
            )

        def process(self, input_data):
            contenido = input_data.get('contenido', '')
            keywords = input_data.get('keywords', [])

            # Análisis SEO básico
            palabras = contenido.lower().split()
            keyword_count = {kw: palabras.count(kw.lower()) for kw in keywords}

            sugerencias = []
            for kw, count in keyword_count.items():
                if count == 0:
                    sugerencias.append(f"Agregar keyword '{kw}' al contenido")
                elif count < 3:
                    sugerencias.append(f"Aumentar frecuencia de '{kw}' (actual: {count})")

            self.add_to_memory({
                'action': 'seo_analysis',
                'keywords_found': sum(1 for c in keyword_count.values() if c > 0)
            })

            return {
                'status': 'success',
                'keyword_density': keyword_count,
                'sugerencias': sugerencias,
                'score': len([c for c in keyword_count.values() if c > 0]) / len(keywords) * 100
            }

    # Usar el agente personalizado
    print("\n--- Creando y usando agente SEO personalizado ---")

    orquestador = BookOrchestrator()

    # Agregar el agente personalizado
    orquestador.agentes_disponibles['seo'] = SEOAgent()

    # Generar contenido
    orquestador.seleccionar_agentes(['escritor'])
    resultado_escritura = orquestador.ejecutar_agente('escritor', {
        'capitulo_info': {
            'numero': 1,
            'titulo': 'Introducción al Marketing Digital'
        },
        'contexto': 'Libro sobre marketing digital para principiantes'
    })

    contenido = resultado_escritura['resultado']['contenido']

    # Analizar con agente SEO
    analisis_seo = orquestador.ejecutar_agente('seo', {
        'contenido': contenido,
        'keywords': ['marketing', 'digital', 'seo', 'contenido', 'web']
    })

    print(f"\nScore SEO: {analisis_seo['score']:.1f}/100")
    print(f"Keywords encontradas: {analisis_seo['keyword_density']}")
    print(f"\nSugerencias SEO:")
    for sugerencia in analisis_seo['sugerencias'][:5]:
        print(f"  • {sugerencia}")


def ejemplo_avanzado_3_multiples_libros():
    """Generar múltiples libros en paralelo (conceptualmente)"""
    print("\n\n" + "=" * 70)
    print("EJEMPLO AVANZADO 3: Generación de múltiples libros")
    print("=" * 70)

    configs = [
        {
            'tema': 'Python Avanzado',
            'genero': 'tecnico',
            'num_capitulos': 8,
            'estilo': 'tecnico'
        },
        {
            'tema': 'Liderazgo en Tiempos de Crisis',
            'genero': 'autoayuda',
            'num_capitulos': 10,
            'estilo': 'conversacional'
        },
        {
            'tema': 'Historia de la Web',
            'genero': 'historico',
            'num_capitulos': 12,
            'estilo': 'narrativo'
        }
    ]

    libros_generados = []

    for i, config in enumerate(configs, 1):
        print(f"\n--- Generando libro {i}/3: {config['tema']} ---")

        orquestador = BookOrchestrator()
        orquestador.seleccionar_agentes(['planificador', 'escritor', 'editor'])

        libro = orquestador.crear_libro(config)
        libros_generados.append(libro)

        print(f"✓ Completado: {libro['estadisticas']['total_capitulos']} capítulos, "
              f"{libro['estadisticas']['total_palabras']} palabras")

    # Resumen
    print("\n" + "=" * 70)
    print("RESUMEN DE LIBROS GENERADOS")
    print("=" * 70)

    total_capitulos = sum(l['estadisticas']['total_capitulos'] for l in libros_generados)
    total_palabras = sum(l['estadisticas']['total_palabras'] for l in libros_generados)

    print(f"\nLibros generados: {len(libros_generados)}")
    print(f"Total capítulos: {total_capitulos}")
    print(f"Total palabras: {total_palabras}")
    print(f"Promedio palabras/libro: {total_palabras // len(libros_generados)}")


def ejemplo_avanzado_4_refinamiento_iterativo():
    """Refinamiento iterativo de contenido"""
    print("\n\n" + "=" * 70)
    print("EJEMPLO AVANZADO 4: Refinamiento iterativo")
    print("=" * 70)

    orquestador = BookOrchestrator()

    # Generar contenido inicial
    print("\n📝 Iteración 1: Generación inicial")
    resultado = orquestador.ejecutar_agente('escritor', {
        'capitulo_info': {
            'numero': 1,
            'titulo': 'Fundamentos de Blockchain'
        },
        'contexto': 'Libro técnico sobre blockchain'
    })

    contenido = resultado['resultado']['contenido']
    print(f"✓ Contenido inicial: {len(contenido.split())} palabras")

    # Iteración 2: Edición
    print("\n✏️  Iteración 2: Edición")
    editado = orquestador.ejecutar_agente('editor', {
        'contenido': contenido
    })
    contenido = editado['contenido_editado']
    print(f"✓ Sugerencias aplicadas: {len(editado['sugerencias'])}")

    # Iteración 3: Mejora de estilo
    print("\n🎨 Iteración 3: Mejora de estilo")
    estilizado = orquestador.ejecutar_agente('estilista', {
        'contenido': contenido,
        'estilo_objetivo': 'tecnico'
    })
    contenido = estilizado['contenido_mejorado']
    legibilidad = estilizado['analisis']['legibilidad']
    print(f"✓ Legibilidad mejorada: {legibilidad}%")

    # Iteración 4: Re-edición final
    print("\n📋 Iteración 4: Edición final")
    final = orquestador.ejecutar_agente('editor', {
        'contenido': contenido
    })
    print(f"✓ Refinamiento completado: {len(final['sugerencias'])} ajustes finales")

    print("\n✅ Proceso de refinamiento completado")


def ejemplo_avanzado_5_analisis_profundo():
    """Análisis profundo de un libro completo"""
    print("\n\n" + "=" * 70)
    print("EJEMPLO AVANZADO 5: Análisis profundo de libro")
    print("=" * 70)

    orquestador = BookOrchestrator()

    # Generar libro
    print("\n📚 Generando libro para análisis...")
    orquestador.seleccionar_agentes(['planificador', 'escritor'])

    config = {
        'tema': 'Criptografía moderna',
        'genero': 'tecnico',
        'num_capitulos': 6,
        'estilo': 'tecnico'
    }

    libro = orquestador.crear_libro(config)
    print(f"✓ Libro generado: {len(libro['capitulos'])} capítulos")

    # Análisis detallado
    print("\n🔍 Realizando análisis profundo...")

    # Estadísticas por capítulo
    print("\n--- Estadísticas por capítulo ---")
    for cap in libro['capitulos']:
        print(f"Capítulo {cap['numero_capitulo']}: {cap['titulo']}")
        print(f"  • Palabras: {cap['palabras']}")
        print(f"  • Longitud promedio palabra: {sum(len(p) for p in cap['contenido'].split()) / cap['palabras']:.1f}")

    # Análisis de coherencia global
    print("\n--- Análisis de coherencia global ---")
    problemas_totales = []

    for i, cap in enumerate(libro['capitulos']):
        coherencia = orquestador.ejecutar_agente('coherencia', {
            'contenido': cap['contenido'],
            'contexto_previo': {
                'capitulos_anteriores': libro['capitulos'][:i]
            }
        })
        problemas_totales.extend(coherencia['problemas'])

    print(f"Coherencia global: {'✓ Excelente' if len(problemas_totales) == 0 else f'⚠ {len(problemas_totales)} problemas'}")

    # Resumen final
    print("\n--- Resumen del análisis ---")
    print(f"Total palabras: {libro['estadisticas']['total_palabras']}")
    print(f"Promedio por capítulo: {libro['estadisticas']['promedio_palabras_capitulo']}")
    print(f"Coherencia: {len(problemas_totales)} problemas detectados")

    print("\n✅ Análisis completado")


def main():
    """Función principal que ejecuta ejemplos avanzados"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 19 + "PAGENT - EJEMPLOS AVANZADOS" + " " * 22 + "║")
    print("║" + " " * 12 + "Casos de uso complejos y personalizaciones" + " " * 15 + "║")
    print("╚" + "=" * 68 + "╝")

    try:
        ejemplo_avanzado_1_workflow_personalizado()
        ejemplo_avanzado_2_agente_personalizado()
        ejemplo_avanzado_3_multiples_libros()
        ejemplo_avanzado_4_refinamiento_iterativo()
        ejemplo_avanzado_5_analisis_profundo()

        print("\n\n" + "=" * 70)
        print("TODOS LOS EJEMPLOS AVANZADOS COMPLETADOS")
        print("=" * 70)
        print("\nEstos ejemplos demuestran las capacidades avanzadas de Pagent.")
        print("Puedes combinar y adaptar estos patrones para tus necesidades.\n")

    except Exception as e:
        print(f"\n❌ Error al ejecutar ejemplos: {e}")


if __name__ == "__main__":
    main()
