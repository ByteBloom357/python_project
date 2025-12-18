import tkinter as tk
from PIL import Image, ImageTk
import os
from data import PATHS

# --------------------------------------------------------
# ГЛОБАЛЬНІ ЗМІННІ ІНТЕРФЕЙСУ
# --------------------------------------------------------

root = None
main_canvas = None
dialog_frame = None
text_label = None
avatar_label = None
npc_frame = None
npc_label = None
npc_name_label = None
buttons_frame = None

current_avatar_photo = None
current_npc_img = None
current_bg_photo = None
current_scene_options = []



def init_ui():
    """Створюємо головне вікно та всі елементи інтерфейсу."""
    global root, main_canvas, dialog_frame, text_label, avatar_label
    global npc_frame, npc_label, npc_name_label, buttons_frame
    
    root = tk.Tk()
    root.title("Пригодницький Квест")
    root.geometry("800x600")
    root.resizable(False, False)
    
    main_canvas = tk.Canvas(root, width=800, height=600)
    main_canvas.pack(fill="both", expand=True)
    
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
    """Встановлює фонове зображення за ключем."""
    global current_bg_photo
    
    filename = PATHS["backgrounds"].get(key)
    
    if not filename or not os.path.exists(filename):
        main_canvas.config(bg="black")
        return
    
    img = Image.open(filename).resize((800, 600))
    current_bg_photo = ImageTk.PhotoImage(img)
    
    if not main_canvas.find_withtag("background_image"):
        main_canvas.create_image(0, 0, image=current_bg_photo, anchor="nw", tags="background_image")
        main_canvas.tag_lower("background_image")
    else:
        main_canvas.itemconfig("background_image", image=current_bg_photo)




def set_avatar(character_name):
    """Встановлює аватар персонажа гравця."""
    global current_avatar_photo
    
    path = PATHS["characters"].get(character_name)
    
    if path and path.endswith(".png") and os.path.exists(path):
        img = Image.open(path).resize((100, 100))
        current_avatar_photo = ImageTk.PhotoImage(img)
        avatar_label.config(image=current_avatar_photo)
    else:
        avatar_label.config(image="")
        print(f"Попередження: файл для {character_name} не знайдено за шляхом {path}")



def show_npc(npc_data):
   
    global current_npc_img
    
    npc_name_label.config(text=f"{npc_data['name']} ({npc_data.get('role', '')})")
    
    img_path = npc_data.get("img", PATHS["characters"].get(npc_data.get("name")))
    
    if npc_data.get("name") in PATHS["characters"]:
        img_path = PATHS["characters"][npc_data["name"]]
    
    if img_path and os.path.exists(img_path):
        img = Image.open(img_path).resize((70, 80))
        current_npc_img = ImageTk.PhotoImage(img)
        npc_label.config(image=current_npc_img, text="")
    else:
        npc_label.config(image="", text="NPC")


def hide_npc():
    """Приховує NPC з екрану."""
    global current_npc_img
    current_npc_img = None
    npc_label.config(image="", text="")
    npc_name_label.config(text="")



def show_scene(text, options):
    """Відображає сцену з текстом та опціями."""
    global current_scene_options
    
    text_label.config(text=text)
    current_scene_options = options
    
    for widget in buttons_frame.winfo_children():
        widget.destroy()
    
    for btn_text, callback in options:
        tk.Button(buttons_frame, text=btn_text, width=40, bg="#4CAF50", fg="white",
                 font=("Arial", 10, "bold"), command=callback).pack(pady=4)


def add_button(text, callback, bg_color="#4CAF50", fg_color="white"):
    """Додає додаткову кнопку до поточної сцени."""
    tk.Button(buttons_frame, text=text, width=40, bg=bg_color, fg=fg_color,
             font=("Arial", 10, "bold"), command=callback).pack(pady=4)


def start_mainloop():
    root.mainloop()