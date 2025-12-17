import tkinter as tk
import random
from PIL import Image, ImageTk
import os
from functools import partial
from collections import Counter
from data import PATHS, NPC_POOL, QUESTS, RANDOM_EVENTS, CHANCE_OF_KIDNAPPING

# --------------------------------------------------------
# 0. НАЛАШТУВАННЯ ТА ІНІЦІАЛІЗАЦІЯ
# --------------------------------------------------------

root = tk.Tk()
root.title("Пригодницький Квест")
root.geometry("800x600") 
root.resizable(False, False) 

main_canvas = tk.Canvas(root, width=800, height=600)
main_canvas.pack(fill="both", expand=True)

# Глобальні змінні 
inventory = []
story_log = []
current_npc = None
current_avatar = None
current_bg_photo = None 
previous_scene_func = None
current_character_name = None

# --------------------------------------------------------
#  ІНТЕРФЕЙС
# --------------------------------------------------------

# Створення елементів інтерфейсу на початку 
dialog_frame = tk.Frame(main_canvas, bg="#36454F", bd=5, relief="raised")
main_canvas.create_window(400, 300, window=dialog_frame, anchor="center")

text_label = tk.Label(dialog_frame, bg="#36454F", fg="white", justify="center", 
                     font=("Arial", 13), wraplength=450, padx=10, pady=10)
text_label.pack(pady=(10, 5), fill="x")

avatar_label = tk.Label(dialog_frame, bg="#36454F")
avatar_label.pack(pady=5)

npc_frame = tk.Frame(dialog_frame, bg="#36454F")
npc_frame.pack(pady=5)
npc_label = tk.Label(npc_frame, bg="#36454F")
npc_label.pack(side="left", padx=5)
npc_name_label = tk.Label(npc_frame, bg="#36454F", fg="yellow", font=("Arial", 11, "bold"))
npc_name_label.pack(side="left", padx=5)

buttons_frame = tk.Frame(dialog_frame, bg="#36454F")
buttons_frame.pack(pady=10, padx=10)


def set_background(key):
    global current_bg_photo
    filename = PATHS["backgrounds"].get(key)
    
    if not os.path.exists(filename):
        main_canvas.config(bg="black") 
        return
    
    img = Image.open(filename).resize((800, 600)) 
    current_bg_photo = ImageTk.PhotoImage(img)
    
    if not main_canvas.find_withtag("background_image"):
        main_canvas.create_image(0, 0, image=current_bg_photo, anchor="nw", tags="background_image")
        main_canvas.tag_lower("background_image")
    else:
        main_canvas.itemconfig("background_image", image=current_bg_photo)


def show_scene(text, options):
    global current_scene_options
    text_label.config(text=text)
    current_scene_options = options

    for w in buttons_frame.winfo_children():
        w.destroy()

    for btn_text, callback in options:
        tk.Button(buttons_frame, text=btn_text,
                  width=40, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                  command=callback).pack(pady=4)

    # Додаємо кнопку "Поговорити" тільки якщо є NPC, і він не Чаклунка зі сюжету
    if current_npc and current_npc.get('role', '') in QUESTS:
        tk.Button(buttons_frame, text=" Поговорити  (КВЕСТ)", width=40, bg="#FFC107", fg="black", 
                  command=talk_to_npc).pack(pady=4)
        
    tk.Button(buttons_frame, text=" Показати Інвентар", width=40, bg="#03A9F4", fg="white", 
              command=show_stats_and_inventory).pack(pady=4)
            

# --------------------------------------------------------
# 3. ФУНКЦІЇ NPC та Діалогів
# --------------------------------------------------------

def set_avatar(key):
    global current_avatar
    img_file = PATHS["characters"].get(key)
    
    if img_file and os.path.exists(img_file):
        img = Image.open(img_file).resize((80, 80)) 
        current_avatar = ImageTk.PhotoImage(img)
        avatar_label.config(image=current_avatar, text="")
    else:
        avatar_label.config(image="", text="Аватар")

def spawn_npc(specific_npc=None):
    global current_npc, current_npc_img
    
    if specific_npc:
        current_npc = specific_npc
    else:
        quest_roles = list(QUESTS.keys())
        # Шукаємо NPC, які мають квести
        npc_options = [n for n in NPC_POOL if n['role'] in quest_roles]
        if npc_options:
            current_npc = random.choice(npc_options)
        else:
            # Якщо квест-NPC немає, беремо будь-якого
            current_npc = random.choice(NPC_POOL) 

    # Оновлення відображення NPC
    npc_name_label.config(text=f"{current_npc['name']} ({current_npc.get('role', '')})")
    
    img_path = current_npc.get("img", PATHS["characters"].get(current_npc.get("name")))
    
    # Використовуємо PATHS["characters"] для ключових персонажів, якщо немає "img"
    if current_npc.get("name") in PATHS["characters"]:
        img_path = PATHS["characters"][current_npc["name"]]
        
    if img_path and os.path.exists(img_path):
        img = Image.open(img_path).resize((60, 60))
        current_npc_img = ImageTk.PhotoImage(img)
        npc_label.config(image=current_npc_img, text="")
    else:
        npc_label.config(image="", text="NPC")

def despawn_npc():
    global current_npc, current_npc_img
    current_npc = None
    # current_npc_img залишаємо, щоб зображення не зникло, але очищуємо лейбли
    npc_label.config(image="", text="") 
    npc_name_label.config(text="")
    
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
    
    # Спеціальні репліки
    if current_npc['name'] == PRINCE_NAME:
          line = f"Моя Принцеса має бути зі мною, а не з якимось там... {current_character_name}!"
    elif current_npc['name'] == "Король":
          line = "Я вирішую, хто буде моїм зятем! Не заважай моїм планам."
    elif current_npc['name'] == "Чаклунка":
          line = "Ти ще не готовий протистояти мені!"
    else:
        line = random.choice(dialogues) 

    story_log.append(f"{current_npc['name']}: {line}")
    
    # Якщо це Принц, Король, або Чаклунка, немає квесту, лише розмова
    if current_npc['name'] in [PRINCE_NAME, "Король", "Чаклунка"]:
        options = [("Закінчити розмову", return_to_previous_scene)]
    else:
        options = [
            ("Спитати про завдання (Квест)", start_quest_with_npc),
            ("Закінчити розмову", return_to_previous_scene)
        ]
        
    show_scene(
        f"{current_npc['name']} каже:\n\n'{line}'",
        options
    )

def start_quest_with_npc():
    global current_npc, previous_scene_func
    role = current_npc["role"]

    # Зберігаємо функцію сцени, звідки прийшли, щоб повернутися
    # (previous_scene_func вже має бути встановлений функцією set_scene)
    
    if role not in QUESTS:
        show_scene("У цього персонажа немає квесту.", [("Назад", return_to_previous_scene)])
        return

    quest = QUESTS[role]
    q_text = quest["question"]

    options = []
    for answer, data in quest["answers"].items():
        # Перевірка на монету для Торговця
        if role == "торговець" and answer == "Так, купити" and "срібна монета" not in inventory:
            options.append(
                (f"{answer} (НЕМАЄ СРІБНОЇ МОНЕТИ)", partial(show_scene, "Не вистачає срібної монети!", [("Назад", return_to_previous_scene)]))
            )
        else:
            options.append(
                (answer, partial(finish_quest, role, answer))
            )

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
        result_text += f"\n\n Отримана нагорода: {reward}!"

    despawn_npc() 
    
    show_scene(
        result_text,
        [("Продовжити пригоду", return_to_previous_scene)]
    )


# --------------------------------------------------------
# 4. СЦЕНИ ГРИ
# --------------------------------------------------------

def set_scene(scene_func, *args, **kwargs):
    global previous_scene_func
    # Зберігаємо попередню сцену, щоб повернутися після діалогу/інвентарю
    previous_scene_func = partial(scene_func, *args, **kwargs)
    
    # Викликаємо сцену
    scene_func(*args, **kwargs)

def return_to_previous_scene():
    if previous_scene_func:
        # Викликаємо збережений partial
        previous_scene_func() 
    else:
        start_game() 

def show_stats_and_inventory():
    """Відображає вміст інвентаря (тепер у діалоговому вікні)."""
    
    item_counts = Counter(inventory)
    
    if not item_counts:
        inv_text = "(порожньо)"
    else:
        inv_list = [f"{count} x {item}" for item, count in item_counts.items()]
        inv_text = "\n".join(inv_list)
    
    text = (
        f" ВМІСТ ТВОГО ІНВЕНТАРЯ:\n\n"
        f"{inv_text}"
    )
    
    options = [("Назад до Пригоди", return_to_previous_scene)]
    show_scene(text, options)
    
def start_game():
    global PRINCESS_STATUS, PRINCE_NAME, PRINCESS_LOCATION, inventory, story_log
    
    # Скидання даних при новій грі
    inventory = ["срібна монета"] # Даємо стартову монету для тестування квесту
    story_log = []
    
    despawn_npc()
    set_background("start")
    
    # Рандомний вибір статусу Принцеси та її місця
    if random.random() < CHANCE_OF_KIDNAPPING:
        PRINCESS_STATUS = "Викрадена"
        PRINCESS_LOCATION = random.choice(["Ліс", "Болото", "Магічні руїни"])
        PRINCE_NAME = random.choice(["Едвін", "Леон", "Валентин"])
    else:
        PRINCESS_STATUS = "У замку"
        
    options = [
        ("Вибрати Короля ", partial(set_scene, choose_character, "Король")),
        ("Вибрати Принцесу ", partial(set_scene, choose_character, "Принцеса")),
        ("Вибрати Лицаря ", partial(set_scene, choose_character, "Лицар"))
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
            ("Іти до лісу 🌳", partial(set_scene, scene_forest)),
            ("Іти до замку 🏰", partial(set_scene, scene_castle))
        ]
        show_scene("З чого почнеш пригоду?", options)
        
def kidnapped_princess_start():
    set_background("magic")
    story_log.append("Принцеса починає гру в полоні!")
    
    # Не спаунимо Чаклунку як NPC з квестом, лише як ключового персонажа
    spawn_npc({"name": "Чаклунка", "img": PATHS["characters"]["Чаклунка"], "role": "ворог"}) 
    
    text = "Ти прокидаєшся у дивному місці. Ти викрадена! Чаклунка, яка тебе охороняє, каже, що захищає тебе від небажаного шлюбу з Принцем."
    
    options = [
        ("Спробувати втекти ", partial(set_scene, scene_magic_escape)),
        ("Поговорити з Чаклункою ", partial(set_scene, talk_to_witch_princess))
    ]
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
        ("Продовжити лісом (До Болота) ", partial(set_scene, scene_swamp)), 
        ("Іти до замку ", partial(set_scene, scene_castle)),
        ("Повернутися на старт", partial(set_scene, start_game))
    ]
    
    if PRINCESS_STATUS == "Викрадена" and PRINCESS_LOCATION == "Ліс":
          options.insert(0, ("Шукати схованку Принцеси", partial(set_scene, scene_rescue_attempt)))

    show_scene(" ".join(text_parts), options)

def scene_castle():
    set_background("castle")
    event = random.choice(RANDOM_EVENTS)
    despawn_npc()
    
    text_parts = [f"Ти у замку, і {event}."]
    
    if PRINCESS_STATUS == "У замку":
        text_parts.append(f"Король свариться з Принцем {PRINCE_NAME} через весілля.")
        
        # Спаунимо Короля для розмови, якщо він не є персонажем гравця
        if current_character_name != "Король":
            spawn_npc({"name": "Король", "img": PATHS["characters"]["Король"], "role": "Король"})
            
        # Принц з'являється рандомно
        if random.random() < 0.5 and current_character_name != "Принц":
            spawn_npc({"name": PRINCE_NAME, "img": PATHS["characters"]["Принц"], "role": "Принц"})
            
    elif PRINCESS_STATUS == "Викрадена":
          text_parts.append(f"У замку паніка. Принцеса зникла!")
    
    story_log.append(f"У замку: {event}")

    options = [
        ("Спуститися у підземелля ", partial(set_scene, scene_dungeon)), 
        ("Вийти до лісу ", partial(set_scene, scene_forest)),
        ("Повернутися на старт", partial(set_scene, start_game))
    ]
    
    show_scene(" ".join(text_parts), options)

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
        ("Заглибитись у магічні руїни ", partial(set_scene, scene_magic)), 
        ("Повернутися до лісу ", partial(set_scene, scene_forest)),
        ("Повернутися на старт", partial(set_scene, start_game))
    ]
    
    if PRINCESS_STATUS == "Викрадена" and PRINCESS_LOCATION == "Болото":
          options.insert(0, ("Шукати схованку Принцеси", partial(set_scene, scene_rescue_attempt)))
    
    show_scene(" ".join(text_parts), options)

def scene_dungeon():
    set_background("dungeon")
    despawn_npc()
    
    if "ключ від підземелля" in inventory:
        text = "Ти використовуєш ключ і відчиняєш стародавні двері. Вони ведуть до магічних руїн."
        options = [
            ("Прямо до магії ", partial(set_scene, scene_magic)), 
            ("Назад до замку ", partial(set_scene, scene_castle))
        ]
    else:
        # Примусово з'являється охоронець для квесту на ключ
        npc_guard = next((n for n in NPC_POOL if n['role'] == "охоронець"), None)
        if npc_guard:
             spawn_npc(npc_guard) # Використовуємо spawn_npc для коректного відображення
        
        text = "Прохід заблоковано! Перед тобою стоїть Воїн-Охоронець. Щоб пройти, потрібен ключ."
        options = [
            ("Поговорити з охоронцем", talk_to_npc),
            ("Назад до замку ", partial(set_scene, scene_castle))
        ]
        
    story_log.append(f"У підземеллі (Ключ: {'Є' if 'ключ від підземелля' in inventory else 'Немає'})")
    show_scene(text, options)

def scene_magic():
    set_background("magic")
    despawn_npc()
    
    text_parts = ["Ти потрапив у магічне місце. Попереду щось магічне. Це кінець шляху..."]
    
    if PRINCESS_STATUS == "Викрадена" and PRINCESS_LOCATION == "Магічні руїни":
          text_parts.append("Чаклунка охороняє Принцесу в центрі руїн!")
    
    options = [
        ("Фіналізувати пригоду! ", final_scene),
        ("Повернутися на старт", partial(set_scene, start_game))
    ]
    
    if PRINCESS_STATUS == "Викрадена" and PRINCESS_LOCATION == "Магічні руїни":
          options.insert(0, ("Шукати схованку Принцеси", partial(set_scene, scene_rescue_attempt)))

    story_log.append("Ти потрапив у магічне місце")
    show_scene(" ".join(text_parts), options)

def scene_rescue_attempt():
    """Сцена спроби порятунку Принцеси."""
    global PRINCESS_STATUS, current_character_name
    despawn_npc()
    
    if current_character_name == "Принцеса":
          # Принцеса сама намагається себе врятувати
          return set_scene(kidnapped_princess_start) 
          
    # З'являється Чаклунка
    spawn_npc({"name": "Чаклунка", "img": PATHS["characters"]["Чаклунка"], "role": "ворог"})
    
    text = "Чаклунка стоїть перед Принцесою. Вона каже: 'Я не дозволю Королю насильно видати її за Принца!'"
    
    # Рандомізація вибору
    magic_power = random.randint(1, 10)
    
    options = [
        ("Спробувати домовитися", partial(set_scene, scene_rescue_talk, magic_power)),
        ("Спробувати силою відібрати Принцесу", partial(set_scene, scene_rescue_fight, magic_power))
    ]
    
    show_scene(text, options)
    
def scene_rescue_talk(power):
    global PRINCESS_STATUS
    despawn_npc()
    
    # Використовуємо наявні предмети як умову
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
    
    # Використовуємо наявні предмети як умову
    if "еліксир" in inventory or power > 8: 
        PRINCESS_STATUS = "Звільнена"
        text = "Твоя сила чи кмітливість допомагає тобі здолати чари. Принцеса вільна!"
        options = [("Взяти Принцесу і йти до замку", final_scene_after_rescue)]
    else:
        text = "Чаклунка занадто сильна. Її магія кидає тебе на землю. Тобі доведеться знайти інший шлях."
        options = [("Відступити", return_to_previous_scene)]

    show_scene(text, options)

def talk_to_witch_princess():
    """Спеціальна розмова для Принцеси з Чаклункою."""
    set_background("magic")
    spawn_npc({"name": "Чаклунка", "img": PATHS["characters"]["Чаклунка"], "role": "ворог"})
    
    dialogues = [
        "Не бійся, Принцесо. Я не ворог, а захисниця від Принца, якого нав'язує тобі батько.",
        "Король думає лише про владу, а не про твоє щастя. Я просто приховую тебе.",
        "Ти маєш вирішити, що важливіше: обов'язок чи кохання."
    ]
    line = random.choice(dialogues)
    
    options = [
        ("Спробувати втекти 🏃", partial(set_scene, scene_magic_escape)),
        ("Подумати про почуте", return_to_previous_scene)
    ]
    show_scene(f"Чаклунка каже:\n\n'{line}'", options)
    
def scene_magic_escape():
    """Спроба втечі для Принцеси."""
    global PRINCESS_STATUS
    despawn_npc()
    
    text = "Ти намагаєшся втекти... але магічний бар'єр занадто міцний."
    
    if "ключ від підземелля" in inventory: # Використовуємо існуючий предмет як умову
          text = "Ти використовуєш залізний ключ, щоб відволікти Чаклунку, і втікаєш!"
          PRINCESS_STATUS = "Звільнена"
          options = [("Втеча вдалася. Йти до замку", final_scene_after_rescue)]
    else:
          options = [("Не вдалося. Повернутися до Чаклунки", partial(set_scene, kidnapped_princess_start))]
          
    show_scene(text, options)

def final_scene_after_rescue():
    """Фінальна сцена після успішного порятунку/втечі Принцеси."""
    despawn_npc()
    
    # ВИПРАВЛЕННЯ: оголошуємо global на початку
    global story_log, inventory 
    
    if current_character_name == "Лицар":
        result = "Ти, Лицар, привів Принцесу до замку, і Король не зміг заперечити твоїй доблесті. Принц залишився ні з чим!"
    elif current_character_name == "Принцеса":
        result = "Ти, Принцеса, повернулася на власних умовах, оголосивши батькові, що сама обереш свою долю."
    elif current_character_name == "Король":
          result = "Ти, Король, мудро (чи ні) вирішив, що шлюб по любові краще, ніж викрадення та скандал. Але Принца доведеться втішати."
    else:
        result = "Принцеса звільнена, і історія набула щасливого кінця!"
        
    final_text = (
        f" ФІНАЛ ПРИГОДИ! \n\n"
        f"{result}\n"
        f"Ти зібрав {len(inventory)} цінних предметів!"
    )
    
    # Скидаємо глобальні змінні для нової гри
    story_log = []
    inventory = []
    
    show_scene(final_text, [("Грати знову", start_game)])


def final_scene():
    """Початкова фінальна сцена, якщо гра не стосувалася порятунку."""
    despawn_npc()
    
    #  оголошуємо global на початку
    global story_log, inventory 
    
    final_text = (
        f" ФІНАЛ ПРИГОДИ! \n\n"
        f"Твоя пригода завершена.\n"
        f"Ти зібрав {len(inventory)} цінних предметів!"
    )
    
    # Скидаємо глобальні змінні для нової гри
    story_log = []
    inventory = []
    
    show_scene(final_text, [("Грати знову", start_game)])


# --------------------------------------------------------
# 5. ЗАПУСК
# --------------------------------------------------------

start_game()
root.mainloop()