# enums.py
from enum import Enum

class DaltonismTypeEnum(Enum):
    ACROMATOPSIA = 'acromatopsia'
    DICROMATOPSIA = 'dicromatopsia'
    TRICROMATOPSIA_ANOMALA = 'tricromatopsia_anomala'

class DicromatopsiaSubtypeEnum(Enum):
    PROTANOPIA = 'protanopia'
    DEUTERANOPIA = 'deuteranopia'
    TRITANOPIA = 'tritanopia'

class TricromatopsiaAnomalaSubtypeEnum(Enum):
    PROTANOMALIA = 'protanomalia'
    DEUTERANOMALIA = 'deuteranomalia'
    TRITANOMALIA = 'tritanomalia'
