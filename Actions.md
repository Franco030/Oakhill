# Documentación de Acciones

Este documento detalla todas las acciones que se pueden utilizar en `trigger_action` (para objetos individuales) o dentro de la lista `scripted_events` (para secuencias).

## Parámetros Globales

Estos parámetros pueden añadirse a casi cualquier acción para modificar su comportamiento general.

| Flag | Tipo | Descripción |
| :--- | :--- | :--- |
| `blocking` | `bool` | Si es `true`, detiene el movimiento del jugador y el ataque mientras dura la acción (ej. leer nota, ver imagen). |
| `kill` | `bool` | *(Solo en Triggers)* Si es `true`, el objeto trigger se elimina tras ejecutarse. Por defecto es `true` para `OnEnter` y `IfFlag`. |
| `sound` | `str` | Nombre del sonido a reproducir junto con la acción (debe existir en `assets/sounds`). |

-----

## 1\. Control de Flujo (EventManager)

Estas acciones son gestionadas directamente por el `EventManager` para controlar el tiempo de las secuencias.

### `Wait`

Detiene la ejecución de la secuencia durante un tiempo determinado.

  * **Uso:** Pausas dramáticas en cinemáticas.
  * **Parámetros:**
      * `time`: (float) Tiempo en segundos a esperar.
  * **Ejemplo:** `action="Wait", params="time=2.0"`

-----

## 2\. Acciones de Interfaz (Visuales)

Acciones que muestran elementos en pantalla. Gestionadas por `ActionManager` -\> `UIManager`.

### `ShowNote`

Muestra una nota de texto en pantalla sobre un fondo.

  * **Parámetros:**
      * `text`: (str) El contenido del texto. Usa `\n` para saltos de línea (si lo escribes en código) o escríbelo en el editor.
      * `sound`: (str) Sonido al abrir la nota (ej. `note_reading`).
      * `blocking`: (bool) Recomendado `true`.
  * **Ejemplo:** `text=Esto es una pista...;blocking=true`

### `ShowImage`

Muestra una imagen estática centrada en la pantalla.

  * **Parámetros:**
      * `image` o `path`: (str) Ruta relativa de la imagen (ej. `assets/images/map.png`).
      * `sound`: (str) Sonido opcional.
      * `blocking`: (bool) Recomendado `true`.
  * **Ejemplo:** `path=assets/images/clue.png;blocking=true`

### `ShowAnimation`

Muestra una secuencia de imágenes como una animación en bucle.

  * **Parámetros:**
      * `path`: (str) Ruta base de las imágenes **sin** número ni extensión (ej. `assets/anim/fire` leerá `fire_0.png`, `fire_1.png`...).
      * `frames`: (int) Cantidad total de imágenes en la secuencia.
      * `speed`: (float) Tiempo en segundos entre cada frame (menor es más rápido).
      * `blocking`: (bool) Recomendado `true`.
  * **Ejemplo:** `path=assets/images/cinematic;frames=4;speed=0.5;blocking=true`

### `CloseImage` (Implícito)

*Nota: Actualmente el cierre se gestiona con la tecla ESPACIO en el UIManager*

-----

## 3\. Acciones de Estado del Juego

Modifican las variables globales (`game_state`) para recordar eventos.

### `SetFlag`

Establece una variable global a un valor específico.

  * **Parámetros:**
      * `flag`: (str) Nombre único de la variable (ID).
      * `value`: (bool/str/int) Valor a asignar.
  * **Ejemplo:** `flag=has_key;value=true`

### `IncrementFlag`

Suma un valor a una variable numérica existente (o la crea si no existe).

  * **Parámetros:**
      * `flag`: (str) Nombre de la variable.
      * `value`: (int) Cantidad a sumar (por defecto 1).
  * **Ejemplo:** `flag=notes_read;value=1`

-----

## 4\. Acciones de Entorno y Objetos

Interactúan con el nivel actual o los objetos en él.

### `UnhideObject`

Hace visible un objeto que estaba oculto (`starts_hidden=true`).

  * **Parámetros:**
      * `id`: (str) El `id` del objeto que quieres revelar.
      * `sound`: (str) Sonido opcional (ej. `secret` o `item_discovered`).
  * **Ejemplo:** `id=hidden_door_1;sound=secret`

### `PlaySound`

Reproduce un efecto de sonido sin acción visual asociada.

  * **Parámetros:**
      * `sound`: (str) Nombre del archivo de sonido (sin extensión, clave del diccionario de recursos).
  * **Ejemplo:** `sound=scream`

-----

## 5\. Acciones de Movimiento y Nivel

Cambian la posición del jugador o el escenario completo.

### `Teleport`

Mueve al jugador instantáneamente a otra posición dentro del **mismo** mapa.

  * **Parámetros:**
      * `zone`: (str) Coordenadas de la zona destino en formato `(y, x)` (ej. `(0, 1)`).
      * `x`: (int) Nueva posición X en píxeles.
      * `y`: (int) Nueva posición Y en píxeles.
  * **Ejemplo:** `zone=(1, 2);x=400;y=300`

### `ChangeLevel`

Carga un archivo JSON diferente (otro mapa/nivel).

  * **Parámetros:**
      * `level`: (str) Clave del nivel en `MAPS` (ej. `school`, `forest`).
      * `json`: (str) Ruta al archivo JSON del nuevo nivel (ej. `data/school_interior.json`).
      * `zone`: (str) Zona inicial en el nuevo mapa `(y, x)`.
      * `x`: (int) Posición X inicial del jugador.
      * `y`: (int) Posición Y inicial del jugador.
  * **Ejemplo:** `level=school;json=data/school.json;zone=(0,0);x=100;y=500`

-----

## Referencia Rápida de Sintaxis (Editor)

Recuerda que en el campo `trigger_params` o `params` del editor, los pares clave-valor se separan por punto y coma (`;`) o saltos de línea (gracias a tu última corrección).

**Formato recomendado:**

```text
text=Hola mundo
sound=note_reading
blocking=true

text=Hola mundo; sound=note_reading; blocking=true
```