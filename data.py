import random

 
CHANCE_OF_KIDNAPPING = 0.9
PRINCE_NAME = "Артур"
PRINCESS_STATUS = "Викрадена"
STORY_LOG = []
INVENTORY = []



PATHS = {
    "backgrounds": {
        "start": "images/backgrounds/background_start.png",
        "forest": "images/backgrounds/forest.png",
        "castle": "images/backgrounds/castle.png",
        "swamp": "images/backgrounds/swamp.png",
        "magic": "images/backgrounds/magic.png",
        "dungeon": "images/backgrounds/dungeon.png"
    },
    "characters": {
        "Король": "images/characters/king.png",
        "Лицар": "images/characters/knight.png",
        "Принцеса": "images/characters/princess.png",
        "Чаклунка": "images/characters/npc_witch.png",
        "Охоронець": "images/characters/npc_guard.png",
        "Торговець": "images/characters/npc_merchant.png",
        "Принц": "images/characters/npc_prince.png",
        "Тінь": "images/characters/npc_shadow.png",
        "Мандрівник": "images/characters/npc_traveler.png"
    }
}

NPC_POOL = [
    {"name": "Старий Мандрівник", "img": "images/characters/npc_traveler.png", "role": "інформатор"},
    {"name": "Місцевий Торговець", "img": "images/characters/npc_merchant.png", "role": "торговець"},
    {"name": "Загадкова Тінь", "img": "images/characters/npc_shadow.png", "role": "таємничий"},
    {"name": "Воїн-Охоронець", "img": "images/characters/npc_guard.png", "role": "охоронець"}
]
QUESTS = {
    "інформатор": {
        "question": "Куди ведуть сліди, як ти думаєш?",
        "answers": {
            "До лісу": {"result": "Так, саме так! Тримай срібну монету.", "reward": "срібна монета"},
            "До замку": {"result": "Ні, це хибний слід…", "reward": None}
        }
    },
    "торговець": {
        "question": "Ти хочеш купити мапу за 1 срібну монету?",
        "answers": {
            "Так, купити": {"result": "Дякую за покупку!", "reward": "мапа"},
            "Ні, не треба": {"result": "Заходь ще.", "reward": None}
        }
    },
    "таємничий": {
        "question": "Що важливіше: Магія чи Сила?",
        "answers": {
            "Магія": {"result": "Тінь киває: 'Мудро.'", "reward": "магічний талісман"},
            "Сила": {"result": "Тінь зникає: 'Ти ще не готовий.'", "reward": None}
        }
    },
    "охоронець": {
        "question": "Щоб пройти далі, ти повинен знати пароль. Який він?",
        "answers": {
            "Дракон": {"result": "Вірно! Прохід відкрито.", "reward": "ключ від підземелля"},
            "Вовк": {"result": "Неправильно! Спробуй пізніше.", "reward": None}
        }
    }
}

RANDOM_EVENTS = [
    "раптово здійнявся магічний шторм",
    "з'явився дракон",
    "хтось загубив таємний лист",
    "земля загуркотіла під ногами",
    "з-за дерев визирнула дивна тінь",
    "вітер приніс незрозумілий шепіт"
]