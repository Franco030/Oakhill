# Things I have to refactor

## 1. Event Manager "OLD SYSTEM"

Treat carefully, some things like scene methods I can't still make in FER

## 2. Clean Trigger class

Once I delete the old system in event manager I can clean all of the old system in Trigger.
- self.action
- self.params

but NOT self.condition, since that condition is for the collision system

## 3. Clean Game_Enum

I don't need neither IF_FLAG nor AUTO_START.
Some of the actions I don't need them, since the system translates to some actions, in the ACTION MANAGER I can delete anything that I don't make in action manager.

## 4. Clean the JSON files

I need to edit my level_editor so that the old system doesn't get saved in the JSON maps.