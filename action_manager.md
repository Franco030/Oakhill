# Action Reference Documentation

This document describes the Global Parameters available for all actions and the specific parameters for each Action Type registered in the `ActionManager`.

## Global Parameters

These parameters can be added to **any** action string. They are handled by the main execution logic before or after the specific action handler.

| Parameter  | Type    | Default | Description                                                                                                                                   |
| :---       | :---    | :---    | :---                                                                                                                                          |
| `sound`    | String  | None    | The ID of a sound asset to play immediately when the action starts.                                                                           |
| `volume`   | Float   | 1.0     | The volume level for the sound specified in the `sound` parameter (0.0 to 1.0).                                                               |
| `blocking` | Boolean | Varies  | Overrides the default blocking behavior of the action. If `true`, the `EventManager` will wait for this action to complete before proceeding. |

---

## Action Types

### SET_FLAG
Sets a global game flag to a specific value.
* **flag** (String): The name of the flag to set.
* **value** (Any): The value to assign to the flag (can be string, number, or boolean).

### INCREMENT_FLAG
Increments the numeric value of a global game flag.
* **flag** (String): The name of the flag to modify.
* **value** (Int): The amount to add to the current flag value. Default: `1`.

### TELEPORT
Instantly moves the player to a specific coordinate within the current map.
* **zone** (String): The zone identifier (e.g., "(0,0)").
* **x** (Int): The target X coordinate in pixels.
* **y** (Int): The target Y coordinate in pixels.

### PLAY_SOUND
Plays a sound effect. (Mostly used with the global `sound` parameter, but registered as a standalone action).
* *Accepts Global Parameters only.*

### UNHIDE_OBJECT
Reveals a hidden object in the current scene.
* **id** (String): The unique identifier of the object to unhide.

### HIDE_OBJECT
Hides a visible object in the current scene.
* **id** (String): The unique identifier of the object to hide.

### MODIFY_LIGHT
Enables or disables the global darkness/lighting overlay for the scene.
* **enable** (Boolean): `true` to enable darkness, `false` to disable it. Default: `false`.

### RANDOM_ACTION
Executes another action based on a probability chance.
* **chance** (Int): The percentage probability (0-100) of success. Default: `50`.
* **action** (String): The action string to execute if the roll succeeds.

### CHANGE_LEVEL
Transfers the player to a different map/level.
* **level** (String): The key name of the level in the `MAPS` constant.
* **json** (String): The relative path to the JSON file for the map collision data.
* **zone** (String): The entry zone identifier (e.g., "(0,0)").
* **x** (Int): The initial X coordinate for the player in the new level.
* **y** (Int): The initial Y coordinate for the player in the new level.

### SHOW_NOTE
Displays a full-screen note or document UI.
* **id** (String): The unique ID of the note content (from `NoteManager`).
* **save** (Boolean): If `true`, marks the note as "collected" in the persistent game state. Default: `false`.
* **blocking** (Boolean): Default is `true`.

### SHOW_DIALOGUE
Displays a text box with dialogue at the bottom of the screen.
* **text** (String): The text content to display.
* **color** (String): RGB color code for the text (e.g., "255,0,0"). Default: "255,255,255".
* **pause_music** (Boolean): If `true`, pauses the background music while the dialogue is open. Default: `false`.
* **blocking** (Boolean): Default is `true`.

### SHOW_IMAGE
Displays a static image overlay on the screen.
* **image** / **path** (String): The resource ID or path of the image to display.
* **pause_music** (Boolean): If `true`, pauses music while the image is shown. Default: `false`.
* **blocking** (Boolean): Default is `false` (unless overridden globally).

### CLOSE_IMAGE
Closes any currently displayed image overlay.
* *No specific parameters.*

### SHOW_ANIMATION
Plays a frame-by-frame animation overlay.
* **path** (String): The base name of the animation frames (e.g., "anim_fire" looks for "anim_fire_0", "anim_fire_1"...).
* **frames** (Int): The total number of frames in the sequence. Default: `1`.
* **speed** (Float): The duration of each frame in seconds. Default: `0.1`.
* **loop** (Boolean): If `true`, the animation repeats indefinitely. Default: `true`.
* **pause_music** (Boolean): If `true`, pauses music during the animation. Default: `false`.
* **blocking** (Boolean): Default is `true`.

### CHANGE_MUSIC
Changes the currently playing background music.
* **path** / **music** (String): The resource ID of the music track.
* **fade** (Int): Time in milliseconds to fade into the new track. Default: `500`.
* **volume** (Float): The playback volume (0.0 to 1.0). Default: `0.6`.
* **loop** (Int): Number of times to loop (-1 for infinite). Default: `-1`.

### MOVE_OBJECT
Instantly teleports an object within the scene to a new position.
* **id** (String): The unique ID of the target object.
* **x** (Int): Target X coordinate.
* **y** (Int): Target Y coordinate.
* **relative** (Boolean): If `true`, adds x/y to current position instead of setting absolute position. Default: `false`.

### SLIDE_OBJECT
Smoothly moves an object to a new position over time (Tween).
* **id** (String): The unique ID of the target object.
* **x** (Int): Target X coordinate.
* **y** (Int): Target Y coordinate.
* **duration** (Float): Time in seconds for the movement to complete. Default: `1.0`.
* **relative** (Boolean): If `true`, moves relative to current position. Default: `false`.
* **animate** (Boolean): If `true`, triggers the object's walking animation during the move. Default: `false`.

### MODIFY_OBJECT
Updates arbitrary attributes of a scene object.
* **id** (String): The unique ID of the target object.
* **[Any Key]**: Any other parameter provided will be set as an attribute on the object instance.

### ASK_CHOICE
Displays a choice selection UI to the player.
* **text** (String): The prompt text (though often the choice text comes from the UI setup). Default: "Choose".
* **flag** (String): The name of the flag where the result (index of chosen option) will be stored. Default: "temp_decision".

### JUMP_IF_TRUE
Jumps to a specific LABEL in the event sequence if a flag is TRUE.
* **flag** (String): The name of the flag to check.
* **label** / **target** (String): The name of the label to jump to.

### JUMP_IF_FALSE
Jumps to a specific LABEL in the event sequence if a flag is FALSE.
* **flag** (String): The name of the flag to check.
* **label** / **target** (String): The name of the label to jump to.

### EXIT
Immediately terminates the current event sequence processing.
* *No specific parameters.*

### LABEL
Marks a point in the event sequence for JUMP actions.
* **name** / **id** (String): The name of this label.

### WAIT
Pauses the event execution for a set time.
* **time** (Float): Duration to wait in seconds. Default: `1.0`.

### DESTROY_OBJECT
Permanently removes an object from the current scene.
* **id** (String): The unique ID of the object to remove. Use "SELF" to refer to the object triggering the event.