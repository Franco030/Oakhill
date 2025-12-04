# Oakhill Action System Documentation

This document serves as a comprehensive reference for the Action System used in the Oakhill engine. Actions are defined in the `ActionManager` and executed via Triggers, Interactables, or Scripted Events.

## Syntax Overview

Parameters for actions are defined as a single string in the editor, using the following format:
`key=value;key2=value`

* **Separators:** Use semicolons (`;`) or newlines (Enter in the editor) to separate multiple parameters.
* **Values:** The engine automatically parses values into Booleans (`true`/`false`), Integers, Floats, or Strings.
* **Text Content:** For actions involving text, use `\n` to insert a line break within the text itself.

---

## Global Parameters

These parameters can be added to most actions to modify their general behavior.

| Parameter    | Type     | Default | Description                                                                                                                       |
| :---         | :---     | :---    | :---                                                                                                                              |
| `blocking`   | `bool`   | `false` | If `true`, the game pauses player movement and inputs until the action (like a note or animation) is finished.                    |
| `sound`      | `string` | `None`  | Plays a Sound Effect (SFX) from the `assets/sounds/` library when the action triggers.                                            |
| `kill`       | `bool`   | `true`  | *(Triggers Only)* If `true`, the trigger object is permanently removed from the game (registered in `GameState`) after execution. |
| `pause_music`| `bool`   | `false` | *(UI Actions Only)* If `true`, the background music pauses while the UI element (Image, Note, Dialogue) is active.                |

---

## Action Reference

### 1. User Interface (UI)

#### `ShowNote`
Displays a text document on a dark background. Supports multi-page content.
* `text`: The content of the note. Use `[P]` to separate pages.
* **Example:** `text=Entry 1: Safe.\nNothing here.[P]Entry 2: Run.;blocking=true`

#### `ShowDialogue`
Displays a text box at the bottom of the screen with a transparent background (RPG style).
* `text`: The dialogue lines.
* `color`: RGB tuple string defining text color. Default is white.
* **Example:** `text=I see you...;color=255,0,0;blocking=true`

#### `ShowImage`
Displays a static image centered on the screen.
* `path` (or `image`): Relative path to the image file.
* **Example:** `path=assets/images/map.png;blocking=true`

#### `ShowAnimation`
Plays a sequence of images as an animation loop.
* `path`: Base path of the image sequence **without** the number suffix or extension (e.g., `assets/anim/fire` loads `fire_0.png`, `fire_1.png`...).
* `frames`: Total number of frames to load.
* `speed`: Time in seconds between frames.
* `loop`: If `true` (default), loops infinitely. If `false`, stops at the last frame.
* **Example:** `path=assets/anim/cinematic;frames=6;speed=0.2;loop=false;blocking=true`

### 2. Level & Movement

#### `Teleport`
Moves the player to a new position within the **same** map/scene. Triggers a glitch transition effect.
* `zone`: The target zone coordinates in format `(y, x)`.
* `x`: Target pixel X position.
* `y`: Target pixel Y position.
* **Example:** `zone=(1, 2);x=500;y=400`

#### `ChangeLevel`
Unloads the current scene and loads a completely new JSON map file.
* `level`: The map key identifier (e.g., `forest`, `school`) -> this is made in `Game_Constants.py`. 
* `json`: Path to the new scene JSON file.
* `zone`: Initial zone coordinates in the new map.
* `x`, `y`: Player spawn position.
* **Example:** `level=school;json=data/school_interior.json;zone=(0,0);x=100;y=500`

#### `UnhideObject`
Reveals an object that was initialized with `starts_hidden=true`.
* `id`: The unique `id` of the object to reveal.
* **Example:** `id=hidden_door_1;sound=secret_found`

### 3. State Management

#### `SetFlag`
Sets a global variable in the `GameState`.
* `flag`: The unique key name for the flag.
* `value`: The value to store.
* **Example:** `flag=has_key;value=true`

#### `IncrementFlag`
Adds a value to a numeric flag. Useful for counting events.
* `flag`: The key name.
* `value`: Amount to add (default is 1).
* **Example:** `flag=notes_read;value=1`

### 4. Audio

#### `PlaySound`
Plays a Sound Effect (SFX) once.
* `sound`: The filename key from `assets/sounds/` (without extension).
* **Example:** `sound=scream_short`

#### `ChangeMusic`
Switches the background music track with a crossfade.
* `path`: Relative path to the new music file.
* `fade`: Fade-out time in milliseconds (default 500).
* `volume`: Volume level from 0.0 to 1.0.
* `loop`: Number of loops (-1 for infinite).
* **Example:** `path=assets/music/boss_theme.wav;fade=2000;volume=0.8`

### 5. Sequencing

#### `Wait`
*Note: This action is primarily used inside `scripted_events` lists.*
Pauses the execution of the event sequence for a set duration.
* `time`: Duration in seconds.
* **Example:** `action=Wait;params=time=3.0`