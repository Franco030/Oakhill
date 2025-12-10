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


# Scripting System and Action Reference

This document serves as the technical reference for the scripting system used in the Level Editor. It details all available Actions that can be assigned to Triggers, Interactables, or Scripted Sequences.

## Parameter Syntax
Parameters are passed as a single string string, separated by semicolons (`;`). Key-value pairs are separated by an equals sign (`=`).

**Format:**
`key=value;key2=value2;key3=value3`

**Example:**
`text=Hello World;speed=0.5;blocking=true`

---

## 1. Flow Control
These actions control the execution order of the script sequence, allowing for branching paths, loops, and decision-making.

### `Label`
Defines a destination point for Jump actions. It performs no logic on its own.
* **name**: The unique identifier for this label within the sequence.
* **Example**: `name=START_PUZZLE`

### `AskChoice`
Opens a UI prompt asking the player to choose between "YES" and "NO". The result is stored in a boolean Global Flag. This action should be blocking.
* **text**: The question to display to the player.
* **flag**: The name of the flag where the result (True/False) will be saved.
* **Example**: `text=Do you want to use the key?;flag=decision_use_key`

### `JumpIfTrue`
Jumps to a specific Label if a Global Flag is set to True.
* **flag**: The name of the flag to check.
* **target**: The name of the `Label` to jump to.
* **Example**: `flag=decision_use_key;target=OPEN_DOOR_SEQ`

### `JumpIfFalse`
Jumps to a specific Label if a Global Flag is set to False (or does not exist).
* **flag**: The name of the flag to check.
* **target**: The name of the `Label` to jump to.
* **Example**: `flag=has_master_key;target=LOCKED_MESSAGE`

### `Exit`
Immediately terminates the current sequence. Useful for stopping execution after a successful branch to prevent fall-through.
* **No parameters required.**

### `Wait`
Pauses the execution of the sequence for a specific amount of time.
* **time**: Duration in seconds.
* **Example**: `time=1.5`

### `RandomAction`
(Implementation specific) Executes one random action from a predefined set or logic.
* **params**: Context-dependent.

---

## 2. State Management
Actions used to manipulate the persistent state of the game session.

### `SetFlag`
Sets a Global Flag to a specific value.
* **flag**: The name of the flag.
* **value**: The value to set (true, false, or an integer/string).
* **Example**: `flag=boss_defeated;value=true`

### `IncrementFlag`
Increments an integer flag by a specific amount. Useful for counters.
* **flag**: The name of the flag.
* **value**: The amount to add (can be negative).
* **Example**: `flag=coins_collected;value=1`

---

## 3. UI and Dialogues
Actions that display visual elements on the screen.

### `ShowDialogue`
Displays the standard text box at the bottom of the screen.
* **text**: The content string. Use `\n` for line breaks.
* **name**: (Optional) Name of the speaker.
* **speed**: (Optional) Text scrolling speed.
* **Example**: `text=It is locked from the other side.;speed=0.05`

### `ShowNote`
Displays a full-screen note or document overlay.
* **text**: The content of the note.
* **image**: (Optional) Background image ID for the note.
* **Example**: `text=Day 4: They are coming...`

### `ShowImage`
Displays a standalone image overlay on the screen (e.g., jumpscares, item pickups).
* **image**: The Asset ID of the image to display.
* **duration**: (Optional) How long to show it. If omitted, requires `CloseImage`.
* **Example**: `image=spr_item_key_big`

### `CloseImage`
Manually closes any currently active overlay image.
* **No parameters required.**

### `ShowAnimation`
Plays a specific animation sequence on the UI layer.
* **animation**: The Asset ID of the animation.
* **loop**: (Optional) true/false.
* **Example**: `animation=anim_static_noise;loop=true`

---

## 4. Object Control
Actions to manipulate objects within the current scene.

### `ModifyObject`
Changes properties of a specific object.
* **id**: The ID of the target object.
* **...**: Any property key to update (e.g., `image_id`, `x`, `y`, `color`).
* **Example**: `id=obj_door_01;image_id=spr_door_open;is_passable=true`

### `MoveObject`
Instantly moves an object to a new position.
* **id**: The ID of the target object.
* **x**: New X coordinate.
* **y**: New Y coordinate.
* **Example**: `id=player;x=500;y=300`

### `SlideObject`
Smoothly interpolates an object to a new position over time.
* **id**: The ID of the target object.
* **x**: Target X coordinate.
* **y**: Target Y coordinate.
* **speed**: (or `duration`) Speed of movement.
* **Example**: `id=obj_moving_platform;x=600;y=600;speed=2.0`

### `HideObject`
Makes an object invisible and non-interactable.
* **id**: The ID of the target object.
* **Example**: `id=obj_secret_wall`

### `UnhideObject`
Makes a hidden object visible and interactable.
* **id**: The ID of the target object.
* **Example**: `id=obj_monster_ambush`

### `ModifyLight`
(If lighting system is active) Changes the properties of a light source.
* **id**: Light ID.
* **radius**: New radius.
* **color**: New RGB color.
* **Example**: `id=light_01;radius=200;color=(255,0,0)`

---

## 5. Audio
Actions to control the sound engine.

### `PlaySound`
Plays a one-shot sound effect.
* **sound**: The Asset ID of the SFX.
* **volume**: (Optional) 0.0 to 1.0.
* **Example**: `sound=sfx_explosion;volume=0.8`

### `ChangeMusic`
Crossfades to a new background music track.
* **music**: The Asset ID of the BGM.
* **fade**: (Optional) Fade duration in seconds.
* **Example**: `music=bgm_boss_fight;fade=2.0`

---

## 6. Level Navigation
Actions related to map traversal.

### `Teleport`
Moves the player to a different location within the *current* map.
* **zone**: The target zone key (e.g., `(0, 0)`).
* **x**: Target X coordinate.
* **y**: Target Y coordinate.
* **Example**: `zone=(1, 0);x=50;y=300`

### `ChangeLevel`
Unloads the current map and loads a new JSON map file.
* **map**: The filename of the new map (without extension, or relative path).
* **entry_zone**: The starting zone in the new map.
* **entry_x**: Starting X.
* **entry_y**: Starting Y.
* **Example**: `map=hospital_f2;entry_zone=(0, 0);entry_x=100;entry_y=100`