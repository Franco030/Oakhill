# Action Manager Documentation

This document describes the scripting language used within the `ActionManager`. These actions can be triggered via `Triggers`, `Interactables`, or event sequences in the JSON level files.

## Global Parameters

The following parameters can be added to **any** action command string. They are processed before the specific action logic.

| Parameter    | Type     | Default | Description                                                                                                                       |
| :---         | :---     | :---    | :---                                                                                                                              |
| `blocking`   | `bool`   | `false` | If `true`, the game pauses player movement and inputs until the action (like a note or animation) is finished.                    |
| `sound`      | `string` | `None`  | Plays a Sound Effect (SFX) from the `assets/sounds/` library when the action triggers.                                            |
| `kill`       | `bool`   | `true`  | *(Triggers Only)* If `true`, the trigger object is permanently removed from the game (registered in `GameState`) after execution. |
| `pause_music`| `bool`   | `false` | *(UI Actions Only)* If `true`, the background music pauses while the UI element (Image, Note, Dialogue) is active.                |

## Action List

### `SET_FLAG`
Sets a value in the global `GameState`. Used to track story progress, puzzle states, or inventory items.
* **`flag`**: (String) The unique identifier for the flag.
* **`value`**: (String/Boolean/Int) The value to store. "true"/"false" are converted to booleans.
* *Example:* `SET_FLAG(flag=has_key; value=true)`

### `INCREMENT_FLAG`
Increments a numeric flag in the `GameState`. Useful for counters (e.g., "candles_lit").
* **`flag`**: (String) The identifier of the flag to increment.
* **`value`**: (Int) The amount to add. Defaults to 1 if omitted.
* *Example:* `INCREMENT_FLAG(flag=coins_collected; value=5)`

### `TELEPORT`
Instantly moves the player to a specific location within the current map or zone.
* **`zone`**: (String) The target zone identifier (e.g., `(0, 1)`).
* **`x`**: (Int) The target X coordinate.
* **`y`**: (Int) The target Y coordinate.
* *Example:* `TELEPORT(zone=(1,0); x=300; y=400)`

### `PLAY_SOUND`
Plays a specific sound effect from the `SoundLibrary` with volume control.
* **`sound`**: (String) The name of the sound file.
* **`volume`**: (Float) The volume level (0.0 to 1.0). Defaults to 1.0.
* *Example:* `PLAY_SOUND(sound=scream; volume=0.8)`

### `UNHIDE_OBJECT`
Reveals an object that was initialized with `is_hidden: true` or previously hidden.
* **`id`**: (String) The unique ID of the object to reveal.
* *Example:* `UNHIDE_OBJECT(id=secret_door)`

### `HIDE_OBJECT`
Removes an object from the scene (stops rendering and collisions).
* **`id`**: (String) The unique ID of the object to hide.
* *Example:* `HIDE_OBJECT(id=breakable_wall)`

### `MODIFY_LIGHT`
Enables or disables the global darkness/flashlight effect in the scene.
* **`enable`**: (Boolean) `true` to enable darkness, `false` to disable it.
* *Example:* `MODIFY_LIGHT(enable=true)`

### `RANDOM_ACTION`
Executes a sub-action based on a probability check.
* **`chance`**: (Int) The percentage chance (0-100) for the action to succeed. Defaults to 50.
* **`action`**: (String) The sub-action string to execute on success.
* *Example:* `RANDOM_ACTION(chance=30; action=PLAY_SOUND(sound=thunder))`

### `CHANGE_LEVEL`
Triggers a transition to a different JSON level file.
* **`level`**: (String) The key name of the map matrix (defined in `Game_Constants.py`).
* **`json`**: (String) Relative path to the JSON level file.
* **`zone`**: (String) The starting zone in the new level.
* **`x`**: (Int) The starting X coordinate for the player.
* **`y`**: (Int) The starting Y coordinate for the player.
* *Example:* `CHANGE_LEVEL(level=forest; json=data/forest.json; zone=(0,0); x=100; y=200)`

### `SHOW_NOTE`
Opens the UI to display a text note.
* **`text`**: (String) The content of the note.
* **`sound`**: (String) Optional sound to play when opening.
* *Example:* `SHOW_NOTE(text=It is locked from the other side.)`

### `SHOW_DIALOGUE`
Displays a dialogue box at the bottom of the screen.
* **`text`**: (String) The dialogue text.
* **`color`**: (String) RGB values separated by commas. Defaults to "255,255,255".
* **`pause_music`**: (Boolean) Whether to pause background music while reading.
* *Example:* `SHOW_DIALOGUE(text=Who is there?; color=255,0,0)`

### `SHOW_IMAGE`
Displays a full-screen or centered static image.
* **`image`** (or `path`): (String) Relative path to the image file.
* **`pause_music`**: (Boolean) Pauses music while image is shown.
* *Example:* `SHOW_IMAGE(image=assets/images/puzzle_clue.png)`

### `CLOSE_IMAGE`
Closes any currently active image or animation overlay.
* *No parameters.*

### `SHOW_ANIMATION`
Plays a frame-by-frame animation on the UI overlay.
* **`path`**: (String) Base path of the animation frame (e.g., `anim_0.png` -> input `anim.png`).
* **`frames`**: (Int) Total number of frames.
* **`speed`**: (Float) Animation speed/delay. Defaults to 0.1.
* **`loop`**: (Boolean) Whether the animation loops. Defaults to `true`.
* *Example:* `SHOW_ANIMATION(path=assets/anim/fire.png; frames=5; speed=0.2)`

### `CHANGE_MUSIC`
Crossfades to a new background music track.
* **`path`** (or `music`): (String) Relative path to the music file.
* **`fade`**: (Int) Fade-out duration in milliseconds. Defaults to 500.
* **`volume`**: (Float) Music volume (0.0 to 1.0).
* **`loop`**: (Int) Number of loops (-1 for infinite).
* *Example:* `CHANGE_MUSIC(path=assets/music/boss_theme.wav; volume=0.8)`

### `MOVE_OBJECT`
Instantly teleports an object to a new position.
* **`id`**: (String) The unique ID of the target object.
* **`x`**: (Int) Target X coordinate.
* **`y`**: (Int) Target Y coordinate.
* **`relative`**: (Boolean) If `true`, adds x/y to current position. Defaults to `false`.
* *Example:* `MOVE_OBJECT(id=box; x=10; y=0; relative=true)`

### `SLIDE_OBJECT`
Smoothly moves an object to a new position over a duration (Tween).
* **`id`**: (String) The unique ID of the target object.
* **`x`**: (Int) Target X coordinate.
* **`y`**: (Int) Target Y coordinate.
* **`duration`**: (Float) Time in seconds for the movement. Defaults to 1.0.
* **`relative`**: (Boolean) If `true`, moves relative to current position.
* **`animate`**: (Boolean) If `true`, triggers the object's internal animation loop during movement.
* *Example:* `SLIDE_OBJECT(id=gate; y=-100; duration=2.5; relative=true; animate=true)`