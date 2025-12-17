import random
from functools import partial
from collections import Counter
from data import (NPC_POOL, QUESTS, RANDOM_EVENTS, CHANCE_OF_KIDNAPPING,
                  PRINCE_NAME, PRINCESS_STATUS, STORY_LOG, INVENTORY)
from ui import (init_ui, set_background, set_avatar, show_npc, hide_npc,
                show_scene, add_button, start_mainloop)

# --------------------------------------------------------
# ГЛОБАЛЬНІ ЗМІННІ ЛОГІКИ ГРИ
# --------------------------------------------------------

current_npc = None
previous_scene_func = None
current_character_name = None
inventory = []
story_log = []
PRINCESS_LOCATION = None


# --------------------------------------------------------
# ФУНКЦІЇ NPC ТА ДІАЛОГІВ
# --------------------------------------------------------

def spawn_npc(specific_npc=None):
    global current_npc
    
    if specific_npc:
        current_npc = specific_npc
    else:
        quest_roles = list(QUESTS.keys())
        npc_options = [n for n in NPC_POOL if n['role'] in quest_roles]
        if npc_options:
            current_npc = random.choice(npc_options)
        else:
            current_npc = random.choice(NPC_POOL)
    
    show_npc(current_npc)


def despawn_npc():
    global current_npc
    current_npc = None
    hide_npc()


def talk_to_npc():
    global previous_scene_func
    if not current_npc:
        return

    dialogues = [
        "Я бачив сліди, що вели до північного лісу.",
        "Якщо бажаєш допомоги — знайди рідкісну траву.",
        "У мене є корисні дрібниці — за золото, звісно.",
        "Не заважай мені! Я охороняю цей прохід."
    ]
    
    if current_npc['name'] == PRINCE_NAME:
        line = f"Моя Принцеса має бути зі мною, а не з якимось там... {current_character_name}!"
    elif current_npc['name'] == "Король":
        line = "Я вирішую, хто буде моїм зятем! Не заважай моїм планам."
    elif current_npc['name'] == "Чаклунка":
        line = "Ти ще не готовий протистояти мені!"
    else:
        line = random.choice(dialogues)

    story_log.append(f"{current_npc['name']}: {line}")
    
    if current_npc['name'] in [PRINCE_NAME, "Король", "Чаклунка"]:
        options = [("Закінчити розмову", return_to_previous_scene)]
    else:
        options = [
            ("Спитати про завдання (Квест)", start_quest_with_npc),
            ("Закінчити розмову", return_to_previous_scene)
        ]
    
    show_scene(f"{current_npc['name']} каже:\n\n'{line}'", options)


def start_quest_with_npc():
    global current_npc, previous_scene_func
    role = current_npc["role"]
    
    if role not in QUESTS:
        show_scene("У цього персонажа немає квесту.", [("Назад", return_to_previous_scene)])
        return

    quest = QUESTS[role]
    q_text = quest["question"]

    options = []
    for answer, data in quest["answers"].items():
        if role == "торговець" and answer == "Так, купити" and "срібна монета" not in inventory:
            options.append(
                (f"{answer} (НЕМАЄ СРІБНОЇ МОНЕТИ)", partial(show_scene, "Не вистачає срібної монети!", [("Назад", return_to_previous_scene)]))
            )
        else:
            options.append((answer, partial(finish_quest, role, answer)))

    show_scene(q_text, options)


def finish_quest(role, answer):
    global inventory
    quest = QUESTS[role]
    data = quest["answers"][answer]
    
    result_text = data["result"]
    reward = data["reward"]

    if role == "торговець" and answer == "Так, купити" and "срібна монета" in inventory:
        inventory.remove("срібна монета")
        result_text += "\n(Срібна монета витрачена.)"
    
    if reward:
        inventory.append(reward)
        result_text += f"\n\n✨ Отримана нагорода: {reward}!"

    despawn_npc()
    show_scene(result_text, [("Продовжити пригоду", return_to_previous_scene)])


# --------------------------------------------------------
# УПРАВЛІННЯ СЦЕНАМИ
# --------------------------------------------------------

def set_scene(scene_func, *args, **kwargs):
    global previous_scene_func
    previous_scene_func = partial(scene_func, *args, **kwargs)
    scene_func(*args, **kwargs)


def return_to_previous_scene():
    if previous_scene_func:
        previous_scene_func()
    else:
        start_game()


def show_stats_and_inventory():
    """Відображає вміст інвентаря."""
    item_counts = Counter(inventory)
    
    if not item_counts:
        inv_text = "(порожньо)"
    else:
        inv_list = [f"{count} x {item}" for item, count in item_counts.items()]
        inv_text = "\n".join(inv_list)
    
    text = f"🎒 ВМІСТ ТВОГО ІНВЕНТАРЯ:\n\n{inv_text}"
    show_scene(text, [("Назад до Пригоди", return_to_previous_scene)])


# --------------------------------------------------------
# СЦЕНИ ГРИ
# --------------------------------------------------------

def start_game():
    global PRINCESS_STATUS, PRINCE_NAME, PRINCESS_LOCATION, inventory, story_log
    
    inventory = ["срібна монета"]
    story_log = []
    
    despawn_npc()
    set_background("start")
    
    if random.random() < CHANCE_OF_KIDNAPPING:
        PRINCESS_STATUS = "Викрадена"
        PRINCESS_LOCATION = random.choice(["Ліс", "Болото", "Магічні руїни"])
        PRINCE_NAME = random.choice(["Едвін", "Леон", "Валентин"])
    else:
        PRINCESS_STATUS = "У замку"
    
    options = [
        ("Вибрати Короля 👑", partial(set_scene, choose_character, "Король")),
        ("Вибрати Принцесу 👸", partial(set_scene, choose_character, "Принцеса")),
        ("Вибрати Лицаря ⚔️", partial(set_scene, choose_character, "Лицар"))
    ]
    show_scene(f"Вітаю! Принц {PRINCE_NAME} чекає на весілля. Принцеса: {PRINCESS_STATUS}. Вибери свого персонажа:", options)


def choose_character(name):
    global current_character_name
    current_character_name = name
    set_avatar(name)
    story_log.append(f"Ти граєш як {name}")

    if name == "Принцеса" and PRINCESS_STATUS == "Викрадена":
        set_scene(kidnapped_princess_start)
    else:
        options = [
            ("Іти до лісу 🌲", partial(set_scene, scene_forest)),
            ("Іти до замку 🏰", partial(set_scene, scene_castle))
        ]
        show_scene("З чого почнеш пригоду?", options)


def kidnapped_princess_start():
    set_background("magic")
    spawn_npc({"name": "Чаклунка", "img": None, "role": "ворог"})
    
    text = "Ти у полоні. Чаклунка каже, що захищає тебе, але за дверима чути кроки..."
    
    options = [
        ("Шукати таємний вихід у кімнаті", partial(set_scene, scene_secret_passage)),
        ("Вкрасти магічний амулет", scene_steal_amulet)
    ]
    show_scene(text, options)
    add_button("🗣️ Поговорити з Чаклункою", talk_to_npc, "#FFC107", "black")
    add_button("🎒 Показати Інвентар", show_stats_and_inventory, "#03A9F4", "white")


def scene_secret_passage():
    set_background("dungeon")
    despawn_npc()
    
    text = "Ти знайшла замаскований люк під старим килимом! Він веде в темний тунель. Куди він виведе?"
    
    options = [
        ("Йти на світло (до Замку)", partial(set_scene, scene_castle)),
        ("Йти в глибину (до Болота)", partial(set_scene, scene_swamp)),
        ("Повернутися в кімнату", partial(set_scene, kidnapped_princess_start))
    ]
    show_scene(text, options)


def scene_steal_amulet():
    global inventory
    if random.random() > 0.5:
        inventory.append("магічний талісман")
        text = "Тобі вдалося непомітно витягнути талісман з кишені Чаклунки! Тепер ти маєш силу."
    else:
        text = "Чаклунка помітила твій рух! 'Не варто було цього робити, люба'. Вона замикає тебе на ключ."
    
    options = [("Продовжити", partial(set_scene, kidnapped_princess_start))]
    show_scene(text, options)


def scene_forest():
    set_background("forest")
    event = random.choice(RANDOM_EVENTS)
    despawn_npc()

    text_parts = [f"Ти в лісі, і {event}."]
    
    if PRINCESS_STATUS == "Викрадена" and PRINCESS_LOCATION == "Ліс":
        text_parts.append("Кажуть, десь тут Чаклунка ховає Принцесу!")
    
    if random.random() < 0.7:
        spawn_npc()

    story_log.append(f"У лісі: {event}")

    options = [
        ("Продовжити лісом (До Болота) 🌿", partial(set_scene, scene_swamp)),
        ("Іти до замку 🏰", partial(set_scene, scene_castle)),
        ("Повернутися на старт", partial(set_scene, start_game))
    ]
    
    if PRINCESS_STATUS == "Викрадена" and PRINCESS_LOCATION == "Ліс":
        options.insert(0, ("🔍 Шукати схованку Принцеси", partial(set_scene, scene_rescue_attempt)))

    show_scene(" ".join(text_parts), options)
    
    if current_npc and current_npc.get('role', '') in QUESTS:
        add_button("🗣️ Поговорити (КВЕСТ)", talk_to_npc, "#FFC107", "black")
    
    add_button("🎒 Показати Інвентар", show_stats_and_inventory, "#03A9F4", "white")


def scene_castle():
    set_background("castle")
    event = random.choice(RANDOM_EVENTS)
    despawn_npc()
    
    text_parts = [f"Ти у замку, і {event}."]
    
    if PRINCESS_STATUS == "У замку":
        text_parts.append(f"Король свариться з Принцем {PRINCE_NAME} через весілля.")
        
        if current_character_name != "Король":
            spawn_npc({"name": "Король", "img": None, "role": "Король"})
        
        if random.random() < 0.5 and current_character_name != "Принц":
            spawn_npc({"name": PRINCE_NAME, "img": None, "role": "Принц"})
    elif PRINCESS_STATUS == "Викрадена":
        text_parts.append(f"У замку паніка. Принцеса зникла!")
    
    story_log.append(f"У замку: {event}")

    options = [
        ("Спуститися у підземелля 🕳️", partial(set_scene, scene_dungeon)),
        ("Вийти до лісу 🌲", partial(set_scene, scene_forest)),
        ("Повернутися на старт", partial(set_scene, start_game))
    ]
    
    show_scene(" ".join(text_parts), options)
    
    if current_npc and current_npc.get('role', '') in QUESTS:
        add_button("🗣️ Поговорити (КВЕСТ)", talk_to_npc, "#FFC107", "black")
    
    add_button("🎒 Показати Інвентар", show_stats_and_inventory, "#03A9F4", "white")


def scene_swamp():
    set_background("swamp")
    despawn_npc()

    event = random.choice(RANDOM_EVENTS)
    text_parts = [f"Ти на болоті. Воно гниле та мокре, і {event}."]
    
    if PRINCESS_STATUS == "Викрадена" and PRINCESS_LOCATION == "Болото":
        text_parts.append("Ти відчуваєш дивну магію – близько схованка Принцеси!")
    
    if random.random() < 0.8:
        spawn_npc()
    
    story_log.append(f"На болоті: {event}")

    options = [
        ("Заглибитись у магічні руїни ✨", partial(set_scene, scene_magic)),
        ("Повернутися до лісу 🌲", partial(set_scene, scene_forest)),
        ("Повернутися на старт", partial(set_scene, start_game))
    ]
    
    if PRINCESS_STATUS == "Викрадена" and PRINCESS_LOCATION == "Болото":
        options.insert(0, ("🔍 Шукати схованку Принцеси", partial(set_scene, scene_rescue_attempt)))
    
    show_scene(" ".join(text_parts), options)
    
    if current_npc and current_npc.get('role', '') in QUESTS:
        add_button("🗣️ Поговорити (КВЕСТ)", talk_to_npc, "#FFC107", "black")
    
    add_button("🎒 Показати Інвентар", show_stats_and_inventory, "#03A9F4", "white")


def scene_dungeon():
    set_background("dungeon")
    despawn_npc()
    
    if "ключ від підземелля" in inventory:
        text = "Ти використовуєш ключ і відчиняєш стародавні двері. Вони ведуть до магічних руїн."
        options = [
            ("Прямо до магії ✨", partial(set_scene, scene_magic)),
            ("Назад до замку 🏰", partial(set_scene, scene_castle))
        ]
    else:
        npc_guard = next((n for n in NPC_POOL if n['role'] == "охоронець"), None)
        if npc_guard:
            spawn_npc(npc_guard)
        
        text = "Прохід заблоковано! Перед тобою стоїть Воїн-Охоронець. Щоб пройти, потрібен ключ."
        options = [
            ("Назад до замку 🏰", partial(set_scene, scene_castle))
        ]
    
    story_log.append(f"У підземеллі (Ключ: {'Є' if 'ключ від підземелля' in inventory else 'Немає'})")
    show_scene(text, options)
    
    if current_npc and current_npc.get('role', '') in QUESTS:
        add_button("🗣️ Поговорити з охоронцем", talk_to_npc, "#FFC107", "black")
    
    add_button("🎒 Показати Інвентар", show_stats_and_inventory, "#03A9F4", "white")


def scene_magic():
    set_background("magic")
    despawn_npc()
    
    text_parts = ["Ти потрапив у магічне місце. Попереду щось магічне. Це кінець шляху..."]
    
    if PRINCESS_STATUS == "Викрадена" and PRINCESS_LOCATION == "Магічні руїни":
        text_parts.append("Чаклунка охороняє Принцесу в центрі руїн!")
    
    options = [
        ("⭐ Фіналізувати пригоду!", final_scene),
        ("Повернутися на старт", partial(set_scene, start_game))
    ]
    
    if PRINCESS_STATUS == "Викрадена" and PRINCESS_LOCATION == "Магічні руїни":
        options.insert(0, ("🔍 Шукати схованку Принцеси", partial(set_scene, scene_rescue_attempt)))

    story_log.append("Ти потрапив у магічне місце")
    show_scene(" ".join(text_parts), options)


def scene_rescue_attempt():
    """Сцена спроби порятунку Принцеси."""
    global PRINCESS_STATUS, current_character_name
    despawn_npc()
    
    if current_character_name == "Принцеса":
        return set_scene(kidnapped_princess_start)
    
    spawn_npc({"name": "Чаклунка", "img": None, "role": "ворог"})
    
    text = "Чаклунка стоїть перед Принцесою. Вона каже: 'Я не дозволю Королю насильно видати її за Принца!'"
    
    magic_power = random.randint(1, 10)
    
    options = [
        ("💬 Спробувати домовитися", partial(set_scene, scene_rescue_talk, magic_power)),
        ("⚔️ Спробувати силою відібрати Принцесу", partial(set_scene, scene_rescue_fight, magic_power))
    ]
    
    show_scene(text, options)


def scene_rescue_talk(power):
    global PRINCESS_STATUS
    despawn_npc()
    
    if "магічний талісман" in inventory or power < 5:
        PRINCESS_STATUS = "Звільнена"
        text = "Чаклунка бачить у тобі чесну людину (або талісман) і погоджується відпустити Принцесу. 'Вона заслуговує на любов, а не на політику!'"
        options = [("Взяти Принцесу і йти до замку", final_scene_after_rescue)]
    else:
        text = "Чаклунка не вірить тобі. 'Йди, поки ціла!' Вона змушує тебе відступити."
        options = [("Відступити", return_to_previous_scene)]

    show_scene(text, options)


def scene_rescue_fight(power):
    global PRINCESS_STATUS
    despawn_npc()
    
    if "еліксир" in inventory or power > 8:
        PRINCESS_STATUS = "Звільнена"
        text = "Твоя сила чи кмітливість допомагає тобі здолати чари. Принцеса вільна!"
        options = [("Взяти Принцесу і йти до замку", final_scene_after_rescue)]
    else:
        text = "Чаклунка занадто сильна. Її магія кидає тебе на землю. Тобі доведеться знайти інший шлях."
        options = [("Відступити", return_to_previous_scene)]

    show_scene(text, options)


def final_scene_after_rescue():
    """Фінальна сцена після успішного порятунку/втечі Принцеси."""
    global story_log, inventory
    despawn_npc()
    
    if current_character_name == "Лицар":
        result = "Ти, Лицар, привів Принцесу до замку, і Король не зміг заперечити твоїй доблесті. Принц залишився ні з чим!"
    elif current_character_name == "Принцеса":
        result = "Ти, Принцеса, повернулася на власних умовах, оголосивши батькові, що сама обереш свою долю."
    elif current_character_name == "Король":
        result = "Ти, Король, мудро (чи ні) вирішив, що шлюб по любові краще, ніж викрадення та скандал. Але Принца доведеться втішати."
    else:
        result = "Принцеса звільнена, і історія набула щасливого кінця!"
    
    final_text = (
        f"🎉 ФІНАЛ ПРИГОДИ! 🎉\n\n"
        f"{result}\n"
        f"Ти зібрав {len(inventory)} цінних предметів!"
    )
    
    story_log = []
    inventory = []
    
    show_scene(final_text, [("🔄 Грати знову", start_game)])


def final_scene():
    """Початкова фінальна сцена, якщо гра не стосувалася порятунку."""
    global story_log, inventory
    despawn_npc()
    
    final_text = (
        f"🎉 ФІНАЛ ПРИГОДИ! 🎉\n\n"
        f"Твоя пригода завершена.\n"
        f"Ти зібрав {len(inventory)} цінних предметів!"
    )
    
    story_log = []
    inventory = []
    
    show_scene(final_text, [("🔄 Грати знову", start_game)])


# --------------------------------------------------------
# ЗАПУСК ГРИ
# --------------------------------------------------------

if __name__ == "__main__":
    init_ui()
    start_game()
    start_mainloop()