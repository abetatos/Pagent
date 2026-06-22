# TODO — book-writer

> Trabajo pendiente que no entra dentro del flujo "escribir el próximo
> capítulo". Cosas estructurales que conviene cerrar antes de empezar
> el Libro II, o que descubrimos como deuda durante el Libro I.

## Alta prioridad

### Gestión de memoria de conversación en las skills

**Problema.** El sistema actual asume que cada `write-chapter` se invoca
en una conversación, y todo lo que se escribe queda en el contexto de
chat. Para una novela larga (25 capítulos × 10 000 palabras de prosa +
todo el razonamiento por capítulo + cada critique + cada revisión), la
conversación se llena rápidamente, aunque el contenido del libro ya
viva en disco (canon, summaries, chapters/).

**Por qué importa.** Claude Code tiene una ventana de contexto finita y
una compactación automática. Si pasamos esa ventana sin disciplina, el
modelo va perdiendo precisión sobre el plan, los personajes y los seeds
— exactamente al revés de lo que pretende este pipeline.

**Diseño deseado (a discutir).** El estado de un libro **debe ser
recuperable desde disco sin necesidad de historial de conversación**.
Cada skill (write-chapter, critique-chapter, update-canon) reconstruye
su contexto leyendo archivos vía `build_context.py` / parseo
determinista. Eso significa que la conversación es **estado efímero**,
no fuente de verdad — y se puede limpiar agresivamente.

**Patrón propuesto (decidir y documentar):**
1. Después de `update-canon <N>` (chapter lock-in), todos los hechos
   relevantes están en `canon/*`, `summaries/ch-NN.md`,
   `summaries/book-summary.md`, `plan/seeds.md` (status), etc.
2. La conversación de la fase ch N ya no aporta nada. La skill
   `update-canon` debe sugerir explícitamente: *"Considera `/clear` la
   conversación antes de escribir el ch N+1; el estado está en disco."*
3. `write-novel` (orquestador) podría usar este principio para correr
   "frío" cada capítulo: cada chapter es una invocación stateless del
   pipeline, no una continuación del razonamiento previo.
4. Documentar en el README una sección "Conversation hygiene" con la
   recomendación de `/clear` cada N capítulos.

**Riesgos.**
- `/clear` pierde la voz que el modelo había calibrado conversando con
  el usuario. ¿Cómo recuperarla? → Quizás un `notes/voice.md` por libro
  donde se anotan los acuerdos de voz/estilo cerrados.
- Algunas decisiones de capítulo emergen de la conversación, no del
  plan. Si limpiamos la conversación, esas decisiones se pierden a
  menos que vayan a `notes/decisions.md`.

**Acciones concretas pendientes.**
- [ ] Decidir la política exacta (clear cada capítulo / cada acto /
      bajo demanda).
- [ ] Implementar mensajes de "considera /clear" en `update-canon` y
      `compress-act` SKILL.md.
- [ ] Crear convención `notes/voice.md` por libro.
- [ ] Documentar en README.

### Biblia como input obligatorio de `book-setup`

**Problema.** Decidido en conversación: queremos que la **biblia de
mundo** sea un paso obligatorio antes de `book-setup`. Sin biblia, no
se puede ni iniciar la estructura. Pero no queremos `ingest-bible` que
parsee la biblia automáticamente — la biblia es para *trabajar el
worldbuilding*, no para auto-derivar setup.md.

**Diseño deseado.**
- `book-setup` SKILL.md exige que `output/<series>/bible.md` exista
  antes de bootstrap. Si no existe, ofrece copiar un template
  (`references/bible-template.md`) y para hasta que el usuario lo
  rellene.
- La biblia es el documento de trabajo: contiene [FIJO] y [PROPUESTA],
  puede tener contradicciones, evoluciona durante el proyecto.
- `book-setup` lee la biblia con el usuario presente y le ayuda a
  *trasladar* lo relevante a `setup.md` interactivamente — la biblia
  permanece como referencia paralela.
- `critique-plan` añade a su flujo: leer la biblia + comparar con
  setup.md por consistencia y completitud.

**Acciones concretas pendientes.**
- [ ] Crear `references/bible-template.md` (estructura de la v4 del
      *Vitral* como ejemplo).
- [ ] Editar `book-setup/SKILL.md` para exigir `bible.md`.
- [ ] Añadir un check al audit: ¿existe bible.md? ¿tiene secciones
      mínimas (premisa, magia, castas, personajes, estructura)?

### Seeds trans-libro

**Problema.** En la trilogía *el Vitral*, varios seeds del Libro I
(Lectura en escena, Blanco Falso, complementario) tienen su payoff real
en Libro III. Mi modelo actual exige `plant_in` y `payoff_in` como
capítulos del **mismo libro**.

**Diseño deseado.** Extender `Seed` con:
```python
trans_book_payoff: list[dict] = []
# cada dict: { book: int, chapter: int, note: str }
```
Y que el `envelope_for_chapter` en cualquier libro consulte también los
seeds de libros anteriores con echo o payoff programado para el libro
actual.

**Acciones concretas pendientes.**
- [ ] Extender `Seed` dataclass + parser.
- [ ] Extender `envelope_for_chapter` para mirar seeds de libros
      previos en la misma serie.
- [ ] Actualizar `update-canon/mark_seed.py` para `--book` opcional.
- [ ] Decidir cómo el writer del Libro III "hereda" el contexto de
      seeds activos del Libro I sin recargar todo el archivo.

## Media prioridad

### Convención de POV en chapter sections

**Problema.** Los slices de shadow.md por capítulo y los seeds asumen
un POV concreto. El audit no comprueba consistencia entre el POV
declarado en `setup.md §POV distribution` y el POV implícito en cada
chapter section.

**Acciones.**
- [ ] Añadir `POV: <name>` como bullet obligatorio en cada `## Chapter N`
      del outline.
- [ ] audit_plan.py comprueba que el POV del chapter section concuerda
      con la distribución global.

### Geografía y nombres como audit dimension

**Problema.** "Las provincias apagadas" y "Aldea natal de Bruno" salen
en el audit como "absent from plan" porque solo aparecen en canon, no
en shadow/seeds/arcs. El check existe pero la convención de qué cuenta
como "mencionado en el plan" puede afinarse.

**Acciones.**
- [ ] Reconciliar con la decisión sobre POV: si un lugar es escenario
      de un capítulo, su nombre debería aparecer en `Where/when`.

### Bugs menores del audit

- [ ] Verificar que el "Magic sections all present" check distingue
      entre placeholder vacío y contenido real (similar al fix de
      source/mechanic).
- [ ] El check de "chapters without any seed activity" tiende a ser
      ruidoso (muchos capítulos sin seed activity es normal). Decidir
      umbral o quitarlo.

## Baja prioridad

### Compile-book skill

Mencionado de pasada en un system reminder: `compile-book` exporta a
EPUB y opcionalmente envía a Kindle. No urgente — se hace tras varios
capítulos escritos.

### Voice drift detection

Algoritmo (probablemente heurístico + revisión manual) para detectar
cuándo la voz de un POV va siendo inconsistente entre capítulos. Útil
sobre todo en la segunda mitad del libro, después de varios `compress-act`.

### Trans-book seed inheritance — UX

Cuando empecemos el Libro II, ¿cómo el writer "siente" qué seeds del
Libro I están todavía vivos? Probablemente: el `build_context.py` para
Libro II lee el `book-summary.md` del Libro I + `plan/seeds.md` del
Libro I, filtra los seeds con status `planted` o `echoed-N` no
`paid_off`, y los incluye como contexto.
