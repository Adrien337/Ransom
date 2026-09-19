### Libraries
import ctypes
import os
from PIL import Image, ImageTk
import pygame
import random
import tkinter as tk
import time

### For exe file because it wont find the images/audio
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

### Global variables
number_of_stops = 33 # Number of stop signs displayed during the "download" phase.
number_of_gold = 500 # Gold required in order to finish
timer = 78 # Seconds before system shutdown /!\ DO NOT CHANGE THIS !!! IT WILL BREAK THE AUDIO

### Screen size
def get_screen_size():
    user32 = ctypes.windll.user32
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    return width, height

### Pictures loader
def prepare_image(path, transparent=False):
    image = Image.open(resource_path(path)).convert("RGBA")

    if transparent:
        pixels = image.load()
        width, height = image.size
        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                if a < 10:
                    pixels[x, y] = (0, 0, 1, 255)
    return image

def load_all_images():
    images = {
        "attack": prepare_image("images/attack.png"),
        "gold": prepare_image("images/gold.png"),
        "idle": prepare_image("images/idle.png"),
        "ransom": prepare_image("images/ransom.png"),
        "static1": prepare_image("images/static1.png"),
        "static2": prepare_image("images/static2.png"),
        "stop": prepare_image("images/stop.png"),
        "taunt1": prepare_image("images/taunt1.png"),
        "taunt2": prepare_image("images/taunt2.png"),
        "taunt3": prepare_image("images/taunt3.png"),
        "taunt4": prepare_image("images/taunt4.png"),
        "taunt5": prepare_image("images/taunt5.png"),
        "taunt6": prepare_image("images/taunt6.png"),
        "taunt7": prepare_image("images/taunt7.png"),
        "taunt8": prepare_image("images/taunt8.png"),
        "taunt9": prepare_image("images/taunt9.png"),
        "thanks": prepare_image("images/thanks.png")
    }
    return images

### Audio loader
def load_sounds():
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    sounds = {}

    def get_sound(name):
        path = resource_path(os.path.join("audio", name))
        try:
            sound = pygame.mixer.Sound(path)
            print(f"Audio loaded : {path}")
            return sound
        except Exception as e:
            print(f"Error on {name} : {e}")
            return None

    sounds["attack"]  = get_sound("attack.mp3")
    sounds["gold"]  = get_sound("gold.mp3")
    sounds["install"]  = get_sound("install.mp3")
    sounds["ransom"]  = get_sound("ransom.mp3")
    sounds["spawn"]   = get_sound("spawn.mp3")
    sounds["thanks"]  = get_sound("thanks.mp3")

    return sounds

### Functions
def set_idle(root):
    TRANSPARENT_COLOR = "#000001"
    sw, sh = get_screen_size()

    root.config(bg=TRANSPARENT_COLOR)
    root.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)

    idle_for_tk = images["idle"].copy()
    pixels = idle_for_tk.load()
    width, height = idle_for_tk.size
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a < 10:
                pixels[x, y] = (0, 0, 1, 255)

    bg_image = ImageTk.PhotoImage(idle_for_tk)
    img_w, img_h = idle_for_tk.size

    max_x = max(0, sw - img_w)
    max_y = max(0, sh - img_h)
    x = random.randint(0, max_x)
    y = random.randint(0, max_y)

    bg_label = tk.Label(root, image=bg_image, bg=TRANSPARENT_COLOR)
    bg_label.place(x=x, y=y)

    root.bg_image = bg_image
    root.bg_label = bg_label
    root.img_w = img_w
    root.img_h = img_h

def stop(root):
    sw, sh = get_screen_size()

    root.wm_attributes("-transparentcolor", "")
    root.config(bg="black")

    background = images["static1"].resize((sw, sh), Image.LANCZOS).convert("RGBA")

    idle_img = images["idle"].convert("RGBA")
    idle_w, idle_h = idle_img.size
    idle_x = (sw - idle_w) // 2
    idle_y = (sh - idle_h) // 2
    background.paste(idle_img, (idle_x, idle_y), idle_img)

    stop_img = images["stop"].convert("RGBA")
    stop_w, stop_h = stop_img.size
    stop_x = (sw - stop_w) // 2
    stop_y = (sh - stop_h) // 2
    background.paste(stop_img, (stop_x, stop_y), stop_img)

    final_img = ImageTk.PhotoImage(background)

    label = tk.Label(root, image=final_img, bg="black")
    label.place(x=0, y=0, relwidth=1, relheight=1)

    root.final_img = final_img
    root.final_label = label

    # Input detection
    root.user_interacted = False

    def on_input(event=None):
        root.user_interacted = True

    root.bind("<Motion>", on_input)
    root.bind("<Key>", on_input)
    root.bind("<Button>", on_input)

def finish_stop(root):
    sw, sh = get_screen_size()

    root.wm_attributes("-transparentcolor", "")
    root.config(bg="black")

    background = images["static1"].resize((sw, sh), Image.LANCZOS).convert("RGBA")
    alpha = background.split()[3]
    alpha = alpha.point(lambda p: int(p * 0.5))
    background.putalpha(alpha)

    idle_img = images["idle"].convert("RGBA")
    idle_w, idle_h = idle_img.size
    idle_x = (sw - idle_w) // 2
    idle_y = (sh - idle_h) // 2
    background.paste(idle_img, (idle_x, idle_y), idle_img)

    final_img = ImageTk.PhotoImage(background)

    label = tk.Label(root, image=final_img, bg="black")
    label.place(x=0, y=0, relwidth=1, relheight=1)

    root.final_img = final_img
    root.final_label = label

def attack(root, scale=1.0):

    sw, sh = get_screen_size()
    root.wm_attributes("-transparentcolor", "")
    root.config(bg="black")

    # Stop previous animation
    if hasattr(root, "attack_after_id"):
        root.after_cancel(root.attack_after_id)

    def create_attack_frame(static_img, scale=1.0):
        background = static_img.resize((sw, sh), Image.LANCZOS).convert("RGBA")

        attack_img = images["attack"].convert("RGBA")

        if scale != 1.0:
            new_size = (int(attack_img.width * scale), int(attack_img.height * scale))
            attack_img = attack_img.resize(new_size, Image.LANCZOS)

        attack_w, attack_h = attack_img.size
        attack_x = (sw - attack_w) // 2
        attack_y = (sh - attack_h) // 2
        background.paste(attack_img, (attack_x, attack_y), attack_img)

        return ImageTk.PhotoImage(background)

    frame1 = create_attack_frame(images["static1"], scale)
    frame2 = create_attack_frame(images["static2"], scale)

    if not hasattr(root, "attack_label"):
        label = tk.Label(root, bg="black")
        label.place(x=0, y=0, relwidth=1, relheight=1)
        root.attack_label = label
    else:
        label = root.attack_label

    root.attack_frames = [frame1, frame2]
    root.attack_index = 0

    def switch():
        root.attack_index = 1 - root.attack_index
        root.attack_label.config(image=root.attack_frames[root.attack_index])
        root.attack_after_id = root.after(50, switch)

    label.config(image=frame1)
    root.attack_after_id = root.after(50, switch)

def download_ransom(root, i, stops=None):
    if i <= 0:
        return

    sw, sh = get_screen_size()

    # Stop previous animation
    if hasattr(root, "attack_after_id"):
        try:
            root.after_cancel(root.attack_after_id)
        except:
            pass

    if stops is None:
        stops = []

    static = images["static1"] if i % 2 == 0 else images["static2"]
    background = static.resize((sw, sh), Image.LANCZOS).convert("RGBA")

    stop_img = images["stop"].convert("RGBA")
    stop_w, stop_h = stop_img.size

    max_x = max(0, sw - stop_w)
    max_y = max(0, sh - stop_h)
    new_x = random.randint(0, max_x)
    new_y = random.randint(0, max_y)
    stops.append((new_x, new_y))

    for x, y in stops:
        background.paste(stop_img, (x, y), stop_img)

    final_img = ImageTk.PhotoImage(background)

    if not hasattr(root, "attack_label"):
        label = tk.Label(root, bg="black")
        label.place(x=0, y=0, relwidth=1, relheight=1)
        root.attack_label = label
    else:
        label = root.attack_label

    label.config(image=final_img)
    root.stop_img = final_img
    root.stops_list = stops

    root.after(25, lambda: download_ransom(root, i - 1, stops))

def pop_up(root):
    root.destroy()

    master = tk.Tk()
    master.withdraw()

    if sounds.get("ransom"):
        sounds["ransom"].play()

    sw, sh = get_screen_size()

    remaining_gold = number_of_gold
    remaining_time = timer

    titles = [
        "Untitled", "Untitled (2)", "Untitled (3)", "RANSOM.exe", "RANASOM",
        "MOSNAR", "I FOUND YOU", "", "RANSOMRANSOM", "RRAANNSSOOMM",
        "LACKLUSTER", "INCOMPETENT", "YOU ARE AN IDIOT", "NONIMPRESSIVE",
        "ENCRYPTED", "AdWBXV Rk1PRVJNR09PUlRJVEVFU04=", "times up", "_____",
        "YOUR GOLD IS VERY YUMMY!", "YOURGOLDAREBELONGTOUS", "ERROR", "Error. Not found."
    ]

    variable_images = [
        images["taunt1"], images["taunt2"], images["taunt3"], images["taunt4"],
        images["taunt5"], images["taunt6"], images["taunt7"], images["taunt8"],
        images["taunt9"],
    ]

    def create_popup(is_ransom=False):
        win = tk.Toplevel(master)
        win.overrideredirect(True)
        win.attributes("-topmost", True)

        if is_ransom:
            win.attributes("-alpha", 1.0)
        else:
            win.attributes("-alpha", 0.88)

        border_color = "#1a1a1a"
        outer = tk.Frame(win, bg=border_color, bd=0)
        outer.pack(fill="both", expand=True)

        title_text = random.choice(titles)
        title_bar = tk.Frame(outer, bg="#0d0d0d", height=28)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)

        title_label = tk.Label(
            title_bar, text=title_text, bg="#0d0d0d", fg="#ff3333",
            font=("Consolas", 10, "bold"), anchor="w", padx=8
        )
        title_label.pack(side="left", fill="y")

        content = tk.Frame(outer, bg=border_color, padx=4, pady=4)
        content.pack(fill="both", expand=True)

        if is_ransom:
            pil_img = images["ransom"]
        else:
            pil_img = random.choice(variable_images)

        tk_img = ImageTk.PhotoImage(pil_img)
        img_label = tk.Label(content, image=tk_img, bg=border_color, bd=0)
        img_label.image = tk_img
        img_label.pack()

        ## UI + gold timer
        gold_label = None
        time_label = None
        if is_ransom:
            ui_frame = tk.Frame(content, bg="#000000")
            ui_frame.pack(fill="x", pady=(8, 4))

            # Gold
            gold_frame = tk.Frame(ui_frame, bg="#000000")
            gold_frame.pack(side="left", padx=10)

            gold_icon = ImageTk.PhotoImage(images["gold"].resize((28, 28), Image.LANCZOS))
            gold_icon_label = tk.Label(gold_frame, image=gold_icon, bg="#000000")
            gold_icon_label.image = gold_icon
            gold_icon_label.pack(side="left")

            gold_label = tk.Label(
                gold_frame,
                text=f"{remaining_gold}",
                bg="#000000",
                fg="#ffd700",
                font=("Consolas", 16, "bold")
            )
            gold_label.pack(side="left", padx=(6, 0))

            # Timer
            time_label = tk.Label(
                ui_frame,
                text="TIME: 01:30",
                bg="#000000",
                fg="#ff2222",
                font=("Consolas", 14, "bold")
            )
            time_label.pack(side="right", padx=10)

        return {
            "win": win,
            "pil": pil_img,
            "img_label": img_label,
            "title_label": title_label,
            "gold_label": gold_label,
            "time_label": time_label,
            "is_ransom": is_ransom
        }

    ransom_popup = create_popup(is_ransom=True)
    var1 = create_popup(is_ransom=False)
    var2 = create_popup(is_ransom=False)
    popups = [ransom_popup, var1, var2]

    def place_random(popup):
        try:
            if not popup["win"].winfo_exists():
                return
        except:
            return

        w = popup["pil"].width + 8
        h = popup["pil"].height + 28 + 8 + (50 if popup["is_ransom"] else 0)
        max_x = max(0, sw - w)
        max_y = max(0, sh - h)
        x = random.randint(0, max_x)
        y = random.randint(0, max_y)

        try:
            popup["win"].geometry(f"+{x}+{y}")
            if popup["is_ransom"]:
                popup["win"].attributes("-topmost", True)
                popup["win"].lift()
                popup["win"].focus_force()
        except:
            pass

    def teleport_ransom():
        try:
            if not popups[0]["win"].winfo_exists():
                return
        except:
            return
        place_random(popups[0])
        master.after(5000, teleport_ransom)

    def teleport_variable(popup):
        try:
            if not popup["win"].winfo_exists():
                return
        except:
            return
        place_random(popup)
        delay = random.randint(500, 2000)
        master.after(delay, lambda: teleport_variable(popup))

    def maybe_change_image_and_title(popup):
        try:
            if not popup["win"].winfo_exists():
                return
        except:
            return

        if random.random() < 0.5:
            new_pil = random.choice(variable_images)
            new_tk = ImageTk.PhotoImage(new_pil)
            popup["img_label"].config(image=new_tk)
            popup["img_label"].image = new_tk
            popup["pil"] = new_pil

            new_title = random.choice(titles)
            popup["title_label"].config(text=new_title)
            place_random(popup)

        master.after(4000, lambda: maybe_change_image_and_title(popup))

    ## Gold system
    gold_icons = []
    gold_layer = tk.Toplevel(master)
    gold_layer.overrideredirect(True)
    gold_layer.attributes("-topmost", True)
    gold_layer.geometry(f"{sw}x{sh}+0+0")
    gold_layer.config(bg="black")
    gold_layer.attributes("-transparentcolor", "black")
    gold_layer.attributes("-alpha", 1.0)

    def update_ui():
        try:
            if ransom_popup["gold_label"] and ransom_popup["gold_label"].winfo_exists():
                ransom_popup["gold_label"].config(text=f"{remaining_gold}")
            if ransom_popup["time_label"] and ransom_popup["time_label"].winfo_exists():
                mins = remaining_time // 60
                secs = remaining_time % 60
                ransom_popup["time_label"].config(text=f"TIME: {mins:02d}:{secs:02d}")
        except:
            pass

    def collect_gold(event, icon_data):
        if sounds.get("gold"):
            sounds["gold"].play()
    
        nonlocal remaining_gold
        remaining_gold = max(0, remaining_gold - 100)
        update_ui()

        try:
            icon_data["label"].destroy()
        except:
            pass
        if icon_data in gold_icons:
            gold_icons.remove(icon_data)

        if remaining_gold <= 0:
            win_screen()

    def spawn_gold():
        if remaining_gold <= 0 or remaining_time <= 0:
            return

        try:
            if not gold_layer.winfo_exists():
                return
        except:
            return

        pil = images["gold"].resize((64, 64), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(pil)

        label = tk.Label(gold_layer, image=tk_img, bg="black", bd=0, cursor="hand2")
        label.image = tk_img

        w, h = pil.size
        x = random.randint(0, max(0, sw - w))
        y = random.randint(0, max(0, sh - h))
        label.place(x=x, y=y)

        icon_data = {"label": label, "pil": pil}
        gold_icons.append(icon_data)

        label.bind("<Button-1>", lambda e, d=icon_data: collect_gold(e, d))

        master.after(random.randint(500, 1500), lambda: remove_gold_if_exists(icon_data))
        master.after(random.randint(600, 1600), spawn_gold)

    def remove_gold_if_exists(icon_data):
        if icon_data in gold_icons:
            try:
                icon_data["label"].destroy()
                gold_icons.remove(icon_data)
            except:
                pass

    def tick_timer():
        nonlocal remaining_time
        try:
            if remaining_time <= 0:
                lose_screen()
                return
            remaining_time -= 1
            update_ui()
            master.after(1000, tick_timer)
        except:
            pass

    def win_screen():
        cleanup()

        if sounds.get("ransom"):
            sounds["ransom"].stop()
        if sounds.get("thanks"):
            sounds["thanks"].play()

        thanks_win = tk.Toplevel(master)
        thanks_win.overrideredirect(True)
        thanks_win.attributes("-topmost", True)

        pil = images["thanks"]
        tk_img = ImageTk.PhotoImage(pil)

        label = tk.Label(thanks_win, image=tk_img, bg="black", bd=0)
        label.image = tk_img
        label.pack()

        w, h = pil.size
        x = (sw - w) // 2
        y = (sh - h) // 2
        thanks_win.geometry(f"+{x}+{y}")

        master.after(4500, lambda: close_everything(thanks_win))

    def lose_screen():
        cleanup()

        if sounds.get("attack"):
            sounds["attack"].play()

        os.system("shutdown /s /t 2")

    def cleanup():
        for p in popups:
            try:
                p["win"].destroy()
            except:
                pass
        try:
            gold_layer.destroy()
        except:
            pass
        for g in gold_icons[:]:
            try:
                g["label"].destroy()
            except:
                pass

    def close_everything(thanks_win):
        try:
            thanks_win.destroy()
        except:
            pass
        try:
            master.destroy()
        except:
            pass

    ## Start
    for p in popups:
        place_random(p)

    teleport_ransom()
    teleport_variable(popups[1])
    teleport_variable(popups[2])
    maybe_change_image_and_title(popups[1])
    maybe_change_image_and_title(popups[2])

    spawn_gold()
    tick_timer()

    master.mainloop()

### Spawn Ransom
def spawn():
    if sounds.get("spawn"):
        sounds["spawn"].play()

    sw, sh = get_screen_size()

    root = tk.Tk()
    root.overrideredirect(True)
    root.wm_attributes("-topmost", True)
    root.geometry(f"{sw}x{sh}")

    set_idle(root)
    root.after(333, lambda: stop(root))
    root.after(750, lambda: finish_stop(root))
    root.after(850, lambda: check_if_attack(root))

    def check_if_attack(root):
        if root.user_interacted:
            if sounds.get("install"):
                sounds["install"].play()
            attack(root)
            root.after(250, lambda : attack(root, scale=4))
            root.after(500, lambda : download_ransom(root, number_of_stops))
            root.after(1250+(25*number_of_stops), lambda : pop_up(root))
        else:
            root.destroy()

    root.mainloop()

### Launcher
if __name__ == "__main__":
    images = load_all_images()
    sounds = load_sounds()
    time.sleep(random.randint(1, 3))
    spawn()