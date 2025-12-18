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
    MOVE_OBJECT = "MoveObject"
    SLIDE_OBJECT = "SlideObject"
    MODIFY_OBJECT = "ModifyObject"
    ASK_CHOICE = "AskChoice"
    JUMP_IF_TRUE = "JumpIfTrue"
    JUMP_IF_FALSE = "JumpIfFalse"
    LABEL = "Label"
    EXIT = "Exit"
    DESTROY_OBJECT = "DestroyObject"

    @classmethod
    def get_actions(cls):
        return [
            cls.WAIT, cls.SET_FLAG, cls.INCREMENT_FLAG, cls.TELEPORT,
            cls.PLAY_SOUND, cls.UNHIDE_OBJECT, cls.HIDE_OBJECT, cls.SHOW_DIALOGUE,
            cls.CHANGE_LEVEL, cls.SHOW_IMAGE, cls.CLOSE_IMAGE, cls.SHOW_NOTE,
            cls.SHOW_ANIMATION, cls.CHANGE_MUSIC, cls.RANDOM_ACTION, cls.MODIFY_LIGHT,
            cls.MOVE_OBJECT, cls.SLIDE_OBJECT, cls.MODIFY_OBJECT, cls.ASK_CHOICE,
            cls.JUMP_IF_TRUE, cls.JUMP_IF_FALSE, cls.LABEL, cls.EXIT, cls.DESTROY_OBJECT
        ]

class Conditions:
    ON_STAY = "OnStay"
    ON_ENTER = "OnEnter"
    ON_INTERACT = "OnInteract"
    AUTO_START = "AutoStart"
    IF_FLAG = "IfFlag"

    @classmethod
    def get_conditions(cls):
        return [
            cls.ON_STAY, cls.ON_ENTER, cls.ON_INTERACT,
            cls.AUTO_START, cls.IF_FLAG
        ]

class ObjectTypes:
    OBSTACLE = "Obstacle"
    MIRROR = "Mirror"
    INTERACTABLE = "Interactable"
    TRIGGER = "Trigger"
    PRIMITIVE = "Primitive"

    @classmethod
    def get_object_types(cls):
        return [
            cls.OBSTACLE, cls.MIRROR, cls.INTERACTABLE,
            cls.TRIGGER, cls.PRIMITIVE
        ]
    

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"

    @classmethod
    def colorize(cls, text, color):
        return f"{color}{text}{cls.RESET}"