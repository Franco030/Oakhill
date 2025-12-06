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
    HIDE_OBJECT = "HideObject"
    RANDOM_ACTION = "RandomAction"
    MODIFY_LIGHT = "ModifyLight"

    @staticmethod
    def get_actions():
        return [
            Actions.WAIT, Actions.SET_FLAG, Actions.INCREMENT_FLAG, Actions.TELEPORT,
            Actions.PLAY_SOUND, Actions.UNHIDE_OBJECT, Actions.HIDE_OBJECT, Actions.SHOW_DIALOGUE,
            Actions.CHANGE_LEVEL, Actions.SHOW_IMAGE, Actions.CLOSE_IMAGE, Actions.SHOW_NOTE,
            Actions.SHOW_ANIMATION, Actions.CHANGE_MUSIC, Actions.RANDOM_ACTION, Actions.MODIFY_LIGHT
        ]

class Conditions:
    ON_STAY = "OnStay"
    ON_ENTER = "OnEnter"
    ON_INTERACT = "OnInteract"
    AUTO_START = "AutoStart"
    IF_FLAG = "IfFlag"

    @staticmethod
    def get_conditions():
        return [
            Conditions.ON_STAY, Conditions.ON_ENTER, Conditions.ON_INTERACT,
            Conditions.AUTO_START, Conditions.IF_FLAG
        ]

class ObjectTypes:
    OBSTACLE = "Obstacle"
    MIRROR = "Mirror"
    INTERACTABLE = "Interactable"
    TRIGGER = "Trigger"
    PRIMITIVE = "Primitive"

    @staticmethod
    def get_object_types():
        return [
            ObjectTypes.OBSTACLE, ObjectTypes.MIRROR, ObjectTypes.INTERACTABLE,
            ObjectTypes.TRIGGER, ObjectTypes.PRIMITIVE
        ]