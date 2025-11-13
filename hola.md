# Documentación del Proyecto: Oakhill

## 1\. Descripción General

Oakhill es un juego de aventuras y supervivencia en 2D con vista cenital, desarrollado en Python utilizando la biblioteca Pygame. El proyecto presenta una arquitectura robusta que separa la lógica del juego de la creación de niveles.

El sistema está dividido en dos puntos de entrada principales:

  * `main_window.py`: El ejecutable principal del juego.
  * `level_editor.py`: Una herramienta independiente para diseñar visualmente los niveles.

El juego utiliza un motor de escenas basado en JSON (`data/scene_output.json`), una máquina de estados para el jugador y los enemigos, y un sistema de componentes de comportamiento (`Behaviour`) para definir la IA de los enemigos.

## 2\. Requerimientos e Instalación

Para ejecutar este proyecto, necesitas:

  * **Python 3.x**
  * **Pygame:** La única dependencia externa. Se puede instalar con:
    ```bash
    pip install pygame
    ```

Todos los demás módulos (`sys`, `json`, `math`, `random`, `abc`) son bibliotecas estándar de Python.

## 3\. Estructura del Proyecto

```
/Oakhill/
├── data/
│   └── scene_output.json     # Archivo de datos del nivel (salida del editor)
│
├── assets/
│   ├── animations/           # Sprites para animaciones (jugador, enemigos) (estas las dibujamos nosotros :D)
│   ├── fonts/                # Fuentes personalizadas (ej. scary_font.ttf) (la saque de internet jaja)
│   ├── images/               # Sprites estáticos (árboles, rocas, notas, etc.) (estas las dibujamos nosotros :D)
│   └── sounds/               # Archivos de audio (música, SFX) (estos los grabe yo jaja)
│
├── src/
│   ├── Animations.py         # Clase Animation
│   ├── Asset_Config.py       # Configuración central de objetos
│   ├── Behaviour.py          # Clases de IA (Stalker, Sine_Wave) (El de sine-wave no jala tanto, si jala, pero cuando atacamos al enemigo se hace mas grande en lugar de parpadear)
│   ├── Enemies.py            # Clases de Enemigos (_Enemy, Stalker_Ghost)
│   ├── Game_Constants.py     # Constantes globales (SCREEN_WIDTH, FPS, etc.) (si queremos cambiar el mapa lo cambiamos aqui)
│   ├── Interactable.py       # Clases de objetos interactuables (_Interactable, Note)
│   ├── Note_Content.py       # Banco de textos para las notas (nada mas es un dict con listas adentro y ya)
│   ├── Obstacles.py          # Clases de obstáculos (_Obstacle, Tree, Wall)
│   ├── Player.py             # Clase Player
│   ├── Scene.py              # Clase Scene (gestor de sprites)
│   └── Scene_Loader.py       # Clase SceneLoader (lector de JSON)
│
├── main_window.py            # Punto de entrada principal (El Juego)
└── level_editor.py           # Herramienta de creación de niveles
```

## 4\. Módulos Principales (Archivos `.py`)

A continuación se detalla la función de cada archivo y sus componentes clave.

### `main_window.py`

Es el punto de entrada principal para jugar.

  * **Propósito:** Inicializa Pygame, gestiona la música, maneja la máquina de estados principal (`game_state`) y contiene el bucle de juego principal.
  * **Funciones Principales:**
      * `draw_note_ui(screen, note_text_lines)`: Dibuja la interfaz de lectura de notas (fondo negro, texto amarillo). Carga una fuente personalizada desde `assets/fonts/scary_font.ttf`.
      * `draw_defeat_text(screen)`: Dibuja el texto "Presiona ESC para reiniciar" sobre un fondo negro semitransparente.
      * `find_safe_spawn(target_pos, player_sprite, obstacles)`: Una función de utilidad crucial. Comprueba si la ubicación de reaparición está bloqueada por un obstáculo. Si lo está, busca en un círculo creciente un lugar seguro para evitar que el jugador se quede atascado.
      * `main()`:
        1.  **Inicialización:** Inicia `pygame`, `pygame.mixer`, y carga todos los efectos de sonido (SFX) y la música de fondo (`pygame.mixer.music`).
        2.  **Configuración:** Crea el `Player` y usa el `SceneLoader` para cargar la escena desde el JSON.
        3.  **Bucle Principal (`while True`)**:
              * **Manejo de Eventos:** Gestiona los eventos de `KEYDOWN` (teclado). Aquí es donde se maneja el `K_SPACE` para atacar (llamando a `player.sprite.attack()`) o cerrar notas, y `K_ESCAPE` para reiniciar desde la muerte (llamando a `player.sprite.reset()`) o cerrar notas.
              * **Máquina de Estados (`game_state`)**: El flujo del juego se divide en tres estados:
                  * `"PLAYING"`: El estado normal. Actualiza al jugador, enemigos e interacciones. Comprueba colisiones de ataque y colisiones de muerte. Dibuja la escena y maneja las transiciones de zona.
                  * `"PLAYER_DEAD"`: Se activa cuando un enemigo golpea al jugador. El jugador es derrotado (`player.sprite.defeat()`). En este estado, el juego sigue actualizando al jugador (para mostrar la animación de derrota) y a los enemigos (para que puedan huir), y dibuja la pantalla de derrota (`draw_defeat_text`).
                  * `"READING_NOTE"`: Congela el juego y solo dibuja la UI de la nota (`draw_note_ui`).

### `level_editor.py`

Una herramienta separada para crear los mapas del juego.

  * **Propósito:** Permite al usuario "pintar" visualmente obstáculos y notas en un sistema de cuadrícula por zonas (`current_zone`).
  * **Lógica Principal:**
      * Importa la configuración de `Asset_Config` y los textos de `Note_Content`.
      * **Bucle de Eventos:**
          * **Teclas 1-8:** Cambia el `current_type` del objeto a colocar (ej. `Tree`, `Note`, `NoteTree`) basándose en `OBSTACLE_CONFIG`.
          * **`[` y `]` (Corchetes):** Cambia el `current_index` del objeto. Tiene lógica especial para `Note` para usar la longitud de `ALL_NOTE_TEXTS` como límite, y lógica para otros obstáculos usando `obstacle['indexes']`.
          * **`S` (Guardar):** Serializa las posiciones de los objetos (`zones_data`) en el archivo `data/scene_output.json`.
          * **`L` (Cargar):** Lee el JSON y recrea los objetos usando `create_obstacle`.
          * **Clic Izquierdo:** Coloca el objeto (`current_type` con el `current_index`) en la cuadrícula. Tiene lógica especial para determinar el `index_to_use` basado en si es una `Note` u otro objeto.
      * **Vista Previa:** Dibuja una versión semitransparente del objeto seleccionado bajo el cursor del ratón.

-----

## 5\. Explicación de Clases

Esta es la arquitectura central del motor de juego.

### `src/Player.py`

#### `class Player(pygame.sprite.Sprite)`

Controla todo lo relacionado con el personaje del jugador.

  * `__init__(self, start_x, start_y, walking_sound=None)`: Configura el `Sprite`. Carga la imagen base, define el `rect` (visual) y el `pos` (lógico). Crea un `_collision_rect` personalizado que es más pequeño, para simular los pies. Inicializa los estados (`is_attacking`, `is_defeated`) y carga todas las animaciones desde `assets/animations/`.
  * `attack(self)`: El método de "un solo pulso" llamado por `main_window.py`. Inicia el estado de ataque (`is_attacking = True`) y resetea el temporizador de ataque.
  * `_player_input(self)`: Una función de estado.
      * Si `self.is_defeated` es `True`, bloquea todos los controles y solo reproduce la animación de derrota.
      * Si `self.is_attacking` es `True`, decrementa `self.attack_timer`, reproduce la animación de ataque, y define el `attack_rect`. Cuando el temporizador llega a cero, resetea el estado.
      * Si no está atacando ni derrotado, lee `pygame.key.get_pressed()` para el movimiento (W, A, S, D) y actualiza `self.direction` y la animación de caminar.
  * `_move_x(self, obstacles)` / `_move_y(self, obstacles)`: Lógica de colisión detallada. Mueve el `_collision_rect` y comprueba si choca con los `collision_rect` de los obstáculos. Si choca, detiene el movimiento.
  * `update(self, obstacles)`: El método principal llamado por `main_window.py` cada frame. Ejecuta la lógica en orden: `_player_input()`, calcula la velocidad, `_handle_walking_sound()`, `_move_x()`, `_move_y()`, y finalmente actualiza el `self.rect` visual a la posición `self.pos`.

### `src/Scene.py`

#### `class Scene`

El gestor de nivel. Mantiene todos los sprites que están actualmente "activos" en el mundo.

  * `__init__(self, initial_location, obstacles, interactables, enemies, map_level)`: Toma los diccionarios de objetos cargados por `SceneLoader`. Crea los `pygame.sprite.Group` para `_enemies`, `_obstacles`, y `_interactables` y los llena con los objetos de la zona inicial.
  * `_load_obstacles_for_current_location(self)`: Esta es la función clave de transición. Vacía los grupos `_obstacles` e `_interactables`. Luego, los rellena desde los diccionarios (`obstacles_dict`, `_interactables_dict`), **pero** ignora inteligentemente cualquier interactuable que ya tenga `interacted_once == True`. **Notablemente, no vacía `_enemies`**, permitiendo que los enemigos (como el Stalker) persistan entre zonas.
  * `set_location(self, new_location)`: Llama a `_load_obstacles_for_current_location` cuando el jugador cambia de zona.
  * `draw(self, screen, player)`: Implementa un sistema de dibujado por capas para la profundidad:
    1.  Separa todos los sprites en `background_sprites` (objetos con `collision_rect.width == 0`) y `main_sprites` (jugador, obstáculos con colisión, interactuables).
    2.  Ordena la capa principal por `sprite.collision_rect.bottom` para un correcto "Y-sorting" (orden de profundidad).
    3.  Dibuja el fondo, luego la capa principal, y finalmente los enemigos (que siempre están encima).

### `src/Scene_Loader.py`

#### `class SceneLoader`

Actúa como el puente entre los datos del nivel y el motor del juego.

  * `load_from_json(path, map_level, initial_zone, player, ...)`:
    1.  Abre y parsea el archivo JSON (ej. `data/scene_output.json`).
    2.  Itera sobre cada objeto en cada zona.
    3.  Usa `Asset_Config.OBSTACLE_CONFIG` para encontrar la clase correcta (ej. `'Tree'` -\> `Tree` class).
    4.  Crea una instancia del objeto (`cls(x, y, index)`).
    5.  Clasifica el objeto: si es una instancia de `_Interactable`, lo añade a `interactable_list`; si no, a `obstacle_list`.
    6.  **Hardcodea** la creación del `Stalker_Ghost` y su `StalkerBehaviour`, pasándole la referencia del `player` y los sonidos (por la naturaleza del juego no tiene sentido que podamos agregar los enemigos y el comportamiento desde el editor, por que querriamos 2 stalkers?).
    7.  Devuelve un objeto `Scene` nuevo y poblado.

### `src/Obstacles.py`

#### `class _Obstacle(pygame.sprite.Sprite)`

Clase base para todos los objetos estáticos del mundo.

  * `__init__(self, start_x, start_y, image, resize_factor)`: Carga, escala y crea el `self.image` y `self.rect`. Crucialmente, crea `self._collision_rect` como una copia del `rect`, que las clases hijas pueden modificar.
  * `Tree`, `Rock`, `Wall`: Clases hijas que simplemente definen sus listas `images` y personalizan sus `_collision_rect` para que la colisión sea más precisa (ej. solo en el tronco del árbol).
  * `Deco_Wall`: Una subclase especial que establece su `_collision_rect` con un ancho y alto de `0`. El método `Scene.draw` usa esto para identificarlo como un objeto de fondo.

### `src/Interactable.py`

Define objetos con los que el jugador puede interactuar.

  * **`class _Interactable(_Obstacle)`:**
      * Hereda de `_Obstacle` para ser un objeto visible.
  * **`class Note(_Interactable)`:**
      * `__init__(self, start_x, start_y, index_image)`: Define el `note_text_content` (hardcodeado en esta versión del archivo). Configura las variables para la lógica de parpadeo (`is_interacting`, `interaction_timer`).
      * `interact(self)`: Inicia el parpadeo. Es llamado por `main_window.py`.
      * `read(self)`: Establece `self.interacted_once = True` y llama a `self.kill()` para que la nota desaparezca de los grupos de sprites.
      * `update(self)`: El motor del parpadeo. Decrementa el temporizador. Si el temporizador está activo, alterna `self.image` entre la imagen original y una superficie blanca usando `BLEND_RGBA_MULT`. Devuelve `"interaction_finished"` cuando el temporizador llega a cero.

### `src/Behaviour.py`

Define los "cerebros" modulares para la IA de los enemigos.

  * `_Behaviour` (ABC): Una clase abstracta que define la interfaz. Requiere un método `apply(self, enemy, delta_time)`.
  * `Sine_Wave_Movement`: Una IA simple que mueve al enemigo en una onda senoidal.
  * `StalkerBehaviour`: La IA principal del `Stalker_Ghost`. Es una máquina de estados compleja:
      * `__init__`: Recibe el `target` (jugador) y los sonidos (`chase_sound`, `flee_sound`) y se inicializa en estado `"WAITING"`.
      * `_start_waiting_offscreen(self, enemy)`: Teletransporta al enemigo a un borde aleatorio de la pantalla y resetea su temporizador de espera.
      * `apply(self, enemy, delta_time)`: El bucle de "pensamiento".
        1.  Primero comprueba si el jugador está derrotado (`self.target.is_defeated`). Si es así, detiene la música de persecución y se detiene.
        2.  `"WAITING"`: No hace nada y espera a que `self.timer` llegue a `self.current_wait_time`.
        3.  `"PURSUING"`: Reproduce el `chase_sound` en bucle. Calcula el vector hacia el jugador y mueve `enemy.x` y `enemy.y`.
        4.  `"ARRIVED"`: Detiene el `chase_sound`.
        5.  `"FLEEING"`: Detiene el `chase_sound` y se mueve hacia el `flee_target`.
      * `shoo(self, enemy)`: Llamado por `Stalker_Ghost.while_attacked`. Inicia el estado `"FLEEING"`, reproduce el `flee_sound` (si se proporcionó) y calcula la ruta de escape más cercana.

### `src/Enemies.py`

Define a los enemigos.

  * `_Enemy` (Base): Clase base para todos los enemigos.
      * `__init__`: Configura `self.x`, `self.y` (posiciones lógicas), `health`, `behaviours`, y el sistema de `flash` (que se usa como "cooldown" de invencibilidad).
      * `update(self, delta_time)`: Aplica el comportamiento (`self.behaviours.apply`), actualiza las posiciones `rect` a las posiciones lógicas (`self.x`, `self.y`), y maneja la lógica del temporizador de `flash`.
  * `Stalker_Ghost`: Subclase de `_Enemy`.
      * `while_attacked(self)`: Lógica de golpe. Comprueba si el fantasma ya está en cooldown (`is_flashing`). Si no lo está, inicia un `start_flash()` (el cooldown) y llama a `self.behaviours.shoo(self)`.
      * `update(self, delta_time)`: Sobrescribe el `update` base. Llama primero a `super().update()` (para manejar el `flash`) y *luego* llama a `self.animation.animate()`. Este orden asegura que el cooldown de `flash` no congele la animación de huida.