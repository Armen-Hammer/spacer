from discord import SlashCommandGroup, SlashCommand
from typing import Union

client = None

class Layer:
    @classmethod
    def create(cls, slashItem: Union[SlashCommandGroup,SlashCommand]): #TODO: find a way to just overload __init__
        return Layer(slashItem.name, slashItem, None)

    def __init__(self, name, value, nextLayer):
        self.refDict = {}
        self.name: str = name
        self.value: Union[SlashCommandGroup,SlashCommand] = value

        if nextLayer:
            self.refDict[nextLayer.name] = nextLayer

    def contains(self, layerName): #sees if this layer contains a reference to a specific name, returns None if there is no reference to it or returns the object
        return self.refDict.get(layerName)

    def add(self, layerToAdd):
        self.refDict[layerToAdd.name] = layerToAdd

    def get(self, layerName):
        return self.refDict.get(layerName)

    def __repr__(self):
        return f'{self.name}: {list(self.refDict.keys())}'

_outerLayer = Layer("_outerLayer",None,None)

def commandWithSpaces(**kwargs):

    def wrapper(func):
        if not client:
            raise TypeError("The client variable was not set") #make sure the client was set

        nameArr = func.__name__.split('_') #split function name by underscore
        if len(nameArr) > 3:  # only 3 words can be used as per the discord API
            raise ValueError("Discord supports nesting one level deep within a group, meaning your top level command can contain subcommand groups, and those groups can contain subcommands. That is the only kind of nesting supported. Here are some visual examples: https://discord.com/developers/docs/interactions/application-commands#subcommands-and-subcommand-groups")

        elif len(nameArr) == 1: #if there is no need to space, add the command and break out of this function
            if _outerLayer.contains(func.__name__):
                raise ValueError(f'You can only have one outer slash command/slash command group with the name "{func.__name__}"')

            layer = Layer.create(client.slash_command(**kwargs)(func))
            _outerLayer.add(layer)
            return

        reference = _outerLayer
        finalLayerVal = None
        for index,word in enumerate(nameArr[:-1]): #this is only to create or instantiate the final layer and update the command group structure
            if temp := reference.contains(word):
                if isinstance(temp.value, SlashCommandGroup):  # if the reference layer has a slash command group with the name already
                    finalLayerVal = temp.value
                else:
                    raise ValueError(f'Error with slash command group {func.__name__}. You can not have both a slash command and slash command group named "{word}".')

            else:
                if finalLayerVal:
                    layer = Layer.create( finalLayerVal.create_subgroup(word, "No description provided"))
                else:
                    layer = Layer.create( SlashCommandGroup(word, "No description provided", parent=finalLayerVal))

                reference.add(layer)
                finalLayerVal = layer.value


            reference = reference.refDict.get(word)

        layer = Layer.create(finalLayerVal.command(name=nameArr[-1], **kwargs)(func))
        reference.add(layer)


    return wrapper


def finish():
    for value in _outerLayer.refDict.values():
        client.add_application_command(value.value) #add the command group to the client

