"""
Ejemplos básicos de uso de Pagent
Sistema Multi-Agente para Escritura de Libros
"""

from pagent import BookOrchestrator


def ejemplo_1_libro_completo():
    """Ejemplo 1: Crear un libro completo con todos los agentes"""
    print("=" * 70)
    print("EJEMPLO 1: Crear un libro completo con todos los agentes")
    print("=" * 70)

    # Inicializar el orquestador
    orquestador = BookOrchestrator()

    # Seleccionar todos los agentes
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
        'tema': 'Inteligencia Artificial y el futuro de la humanidad',
        'genero': 'divulgacion',
        'num_capitulos': 8,
        'estilo': 'academico',
        'profundidad_investigacion': 'alta'
    }

    print(f"\nCreando libro sobre: {config['tema']}")
    print(f"Género: {config['genero']}")
    print(f"Número de capítulos: {config['num_capitulos']}")
    print(f"Estilo: {config['estilo']}\n")

    # Crear el libro
    libro = orquestador.crear_libro(config)

    # Mostrar resultados
    print("\n" + "=" * 70)
    print("RESULTADOS")
    print("=" * 70)
    print(f"Título: {libro['estructura'].get('titulo', 'N/A')}")
    print(f"Total de capítulos: {libro['estadisticas']['total_capitulos']}")
    print(f"Total de palabras: {libro['estadisticas']['total_palabras']}")
    print(f"Promedio palabras/capítulo: {libro['estadisticas']['promedio_palabras_capitulo']}")
    print(f"Coherencia: {'✓ Sí' if libro.get('coherencia', {}).get('coherente', False) else '✗ No'}")
    print(f"\nAgentes utilizados: {', '.join(libro['estadisticas']['agentes_utilizados'])}")


def ejemplo_2_uso_selectivo():
    """Ejemplo 2: Usar solo algunos agentes específicos"""
    print("\n\n" + "=" * 70)
    print("EJEMPLO 2: Uso selectivo de agentes")
    print("=" * 70)

    orquestador = BookOrchestrator()

    # Usar solo planificador y escritor
    orquestador.seleccionar_agentes(['planificador', 'escritor'])

    config = {
        'tema': 'Aventuras en el espacio profundo',
        'genero': 'ciencia ficcion',
        'num_capitulos': 12
    }

    print(f"\nCreando libro de {config['genero']}: {config['tema']}")
    print("Agentes activos: planificador, escritor\n")

    libro = orquestador.crear_libro(config)

    print("\n" + "=" * 70)
    print("RESULTADOS")
    print("=" * 70)
    print(f"Capítulos generados: {len(libro['capitulos'])}")
    print(f"Total palabras: {libro['estadisticas']['total_palabras']}")


def ejemplo_3_agente_individual():
    """Ejemplo 3: Ejecutar agentes individuales"""
    print("\n\n" + "=" * 70)
    print("EJEMPLO 3: Ejecutar agentes individuales")
    print("=" * 70)

    orquestador = BookOrchestrator()

    # Ejemplo 3a: Solo investigación
    print("\n--- 3a. Ejecutar solo el investigador ---")
    resultado = orquestador.ejecutar_agente('investigador', {
        'tema': 'Computación cuántica',
        'profundidad': 'alta',
        'fuentes': ['academico', 'cientifico']
    })

    print(f"Estado: {resultado['status']}")
    print(f"Tema investigado: {resultado['tema']}")
    print(f"Puntos clave encontrados: {len(resultado['informacion']['puntos_clave'])}")
    print(f"Fuentes consultadas: {len(resultado['informacion']['fuentes'])}")

    # Ejemplo 3b: Solo planificación
    print("\n--- 3b. Ejecutar solo el planificador ---")
    plan = orquestador.ejecutar_agente('planificador', {
        'tema': 'Historia del Imperio Romano',
        'genero': 'historico',
        'num_capitulos': 15
    })

    print(f"Estado: {plan['status']}")
    print(f"Título propuesto: {plan['estructura']['titulo']}")
    print(f"Capítulos planeados: {len(plan['estructura']['capitulos'])}")

    # Ejemplo 3c: Solo escritura
    print("\n--- 3c. Ejecutar solo el escritor ---")
    capitulo = orquestador.ejecutar_agente('escritor', {
        'capitulo_info': {
            'numero': 1,
            'titulo': 'Los orígenes de Roma'
        },
        'contexto': 'Un libro histórico sobre el Imperio Romano',
        'estilo': 'narrativo'
    })

    print(f"Estado: {capitulo['status']}")
    print(f"Capítulo: {capitulo['resultado']['titulo']}")
    print(f"Palabras escritas: {capitulo['resultado']['palabras']}")


def ejemplo_4_listar_agentes():
    """Ejemplo 4: Listar agentes disponibles"""
    print("\n\n" + "=" * 70)
    print("EJEMPLO 4: Listar agentes disponibles")
    print("=" * 70)

    orquestador = BookOrchestrator()
    agentes = orquestador.listar_agentes_disponibles()

    print("\nAgentes disponibles en el sistema:\n")
    for agente in agentes:
        estado = "✓ ACTIVO" if agente['activo'] else "○ Inactivo"
        print(f"{estado} - {agente['nombre']}")
        print(f"  └─ {agente['especialization']}\n")


def ejemplo_5_estilos_diferentes():
    """Ejemplo 5: Crear libros con diferentes estilos"""
    print("\n\n" + "=" * 70)
    print("EJEMPLO 5: Libros con diferentes estilos")
    print("=" * 70)

    estilos = ['narrativo', 'academico', 'conversacional']

    for estilo in estilos:
        print(f"\n--- Generando libro en estilo: {estilo} ---")

        orquestador = BookOrchestrator()
        orquestador.seleccionar_agentes(['planificador', 'escritor', 'estilista'])

        config = {
            'tema': 'Python para principiantes',
            'genero': 'tecnico',
            'num_capitulos': 5,
            'estilo': estilo
        }

        libro = orquestador.crear_libro(config)
        print(f"  Capítulos: {libro['estadisticas']['total_capitulos']}")
        print(f"  Palabras: {libro['estadisticas']['total_palabras']}")
        print(f"  Estilo aplicado: {estilo}")


def main():
    """Función principal que ejecuta todos los ejemplos"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "PAGENT - EJEMPLOS BÁSICOS" + " " * 23 + "║")
    print("║" + " " * 15 + "Sistema Multi-Agente para Escritura" + " " * 18 + "║")
    print("╚" + "=" * 68 + "╝")

    try:
        # Ejecutar ejemplos
        ejemplo_1_libro_completo()
        ejemplo_2_uso_selectivo()
        ejemplo_3_agente_individual()
        ejemplo_4_listar_agentes()
        ejemplo_5_estilos_diferentes()

        print("\n\n" + "=" * 70)
        print("TODOS LOS EJEMPLOS COMPLETADOS EXITOSAMENTE")
        print("=" * 70)
        print("\nPara más ejemplos avanzados, consulta: examples/advanced_usage.py")
        print("Para documentación completa, consulta: README.md\n")

    except Exception as e:
        print(f"\n❌ Error al ejecutar ejemplos: {e}")
        print("Asegúrate de que el módulo pagent está instalado correctamente.")


if __name__ == "__main__":
    main()
