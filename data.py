import random

# --- ГЛОБАЛЬНІ НАЛАШТУВАННЯ ТА СЮЖЕТ ---
CHANCE_OF_KIDNAPPING = 0.9

PATHS = {
    "characters": {
        "Король": "king.png",
        "Принцеса": "princess.png",
        "Лицар": "knight.png",
        "Принц": "npc_prince.png", 
        "Чаклунка": "npc_witch.png", 
        "npc_traveler": "npc_traveler.png", 
        "npc_merchant": "npc_merchant.png",
        "npc_shadow": "npc_shadow.png",
        "npc_guard": "npc_guard.png"
    },
    "backgrounds": {
        "start": "background_start.png",
        "forest": "forest.png",
        "castle": "castle.png",
        "magic": "magic.png",
        "swamp": "swamp.png", 
        "dungeon": "dungeon.png"
    }
}

NPC_POOL = [
    {"name": "Старий Мандрівник", "img": "npc_traveler.png", "role": "інформатор"},
    {"name": "Місцевий Торговець", "img": "npc_merchant.png", "role": "торговець"},
    {"name": "Загадкова Тінь", "img": "npc_shadow.png", "role": "таємничий"},
    {"name": "Воїн-Охоронець", "img": "npc_guard.png", "role": "охоронець"}
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