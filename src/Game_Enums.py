class Actions:
    WAIT = "Wait"
    SET_FLAG = "SetFlag"
    INCREMENT_FLAG = "IncrementFlag"
    TELEPORT = "Teleport"
    PLAY_SOUND = "PlaySound"
    UNHIDE_OBJECT = "UnhideObject"
    SHOW_DIALOGUE = "ShowDialogue"
    CHANGE_LEVEL = "ChangeLevel"
    SHOW_IMAGE = "ShowImage"
    CLOSE_IMAGE = "CloseImage"
    SHOW_NOTE = "ShowNote"
    SHOW_ANIMATION = "ShowAnimation"
    CHANGE_MUSIC = "ChangeMusic"

class Conditions:
    ON_ENTER = "OnEnter"
    ON_INTERACT = "OnInteract"
    AUTO_START = "AutoStart"
    IF_FLAG = "IfFlag"

class ObjectTypes:
    OBSTACLE = "Obstacle"
    MIRROR = "Mirror"
    INTERACTABLE = "Interactable"
    TRIGGER = "Trigger"
    PRIMITIVE = "Primitive"