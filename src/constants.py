# Typecodes derived from actual save file analysis
TYPECODE_NAMES = {
    9: "FACTION_RELATIONS",
    21: "RESEARCH_STATE",
    25: "CHARACTER_STATS",
    28: "WORLD_STATE",
    30: "INSTANCE_COLLECTION",
    34: "PLATOON",
    36: "GAMESTATE_CHARACTER",
    37: "GAMESTATE_FACTION",
    38: "GAMESTATE_TOWN",
    41: "CHARACTER_APPEARANCE",
    42: "INVENTORY_ITEM_STATE",
    56: "MAP_FEATURES",
    57: "MEDICAL_STATE",
    66: "APPEARANCE_DETAIL",
    67: "AI_STATE",
    94: "TOWN_STATE",
    108: "GAME_SETTINGS",
}

INVENTORY_SLOTS = [
    "main", "head", "shirt", "armour", "legs", "boots",
    "back", "hip", "belt", "backpack_attach", "backpack_content",
]

# Actual stat names as found in type 25 records (CHARACTER_STATS)
CHARACTER_STATS = [
    "strength", "toughness2", "dexterity", "perception",
    "attack", "defence", "dodge",
    "unarmed", "katana", "sabres", "hackers",
    "heavy weapons", "blunt", "poles",
    "turrets", "bow",
    "medic", "engineer", "robotics", "science",
    "cooking", "farming", "labouring",
    "swimming", "athletics",
    "assassin", "lockpicking", "thievery", "stealth",
    "weapon smith", "armour smith",
]

# Display names for stats
STAT_DISPLAY = {
    "strength": "Strength",
    "toughness2": "Toughness",
    "dexterity": "Dexterity",
    "perception": "Perception",
    "attack": "Melee Attack",
    "defence": "Melee Defence",
    "dodge": "Dodge",
    "unarmed": "Martial Arts",
    "katana": "Katanas",
    "sabres": "Sabres",
    "hackers": "Hackers",
    "heavy weapons": "Heavy Weapons",
    "blunt": "Blunt",
    "poles": "Polearms",
    "turrets": "Turrets",
    "bow": "Crossbows",
    "medic": "Field Medic",
    "engineer": "Engineer",
    "robotics": "Robotics",
    "science": "Science",
    "cooking": "Cooking",
    "farming": "Farming",
    "labouring": "Labouring",
    "swimming": "Swimming",
    "athletics": "Athletics",
    "assassin": "Assassination",
    "lockpicking": "Lockpicking",
    "thievery": "Thievery",
    "stealth": "Stealth",
    "weapon smith": "Weaponsmith",
    "armour smith": "Armoursmith",
}

# Medical state body parts (indexed 0-6)
BODY_PART_NAMES = {
    0: "Head",
    1: "Chest",
    2: "Stomach",
    3: "Right Arm",
    4: "Left Arm",
    5: "Right Leg",
    6: "Left Leg",
}

MEDICAL_FIELD_DISPLAY = {
    "flesh": "Current HP",
    "hit": "Max HP",
    "bandage": "Bandaged",
    "stun": "Stun Damage",
    "rig": "Splint",
    "wear": "Wear (Prosthetic)",
}

MEDICAL_GENERAL_DISPLAY = {
    "blood": "Blood",
    "hung": "Hunger",
    "bleeding": "Bleeding",
    "KO": "Knockout",
    "fed": "Fed",
}

LIMB_NAMES = ["right leg", "left leg", "right arm", "left arm"]
LIMB_STATUS = {0: "Attached", 1: "Severed", 2: "Prosthetic"}

SLOT_DISPLAY = {
    "main": "Backpack / Main",
    "head": "Head",
    "shirt": "Shirt",
    "armour": "Armour",
    "legs": "Legs",
    "boots": "Boots",
    "back": "Back",
    "hip": "Hip",
    "belt": "Belt",
    "backpack_attach": "Backpack",
    "backpack_content": "Backpack Contents",
    "": "Unknown",
}
