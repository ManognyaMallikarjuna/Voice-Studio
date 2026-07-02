import tkinter as tk
from tkinter import ttk, filedialog
from gtts import gTTS
import pygame
from deep_translator import GoogleTranslator
import pytesseract
from PIL import Image
import os
import threading
import time

# Initialize Mixer
pygame.mixer.init()

# -------- TESSERACT PATH --------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# -------- EXTENDED LANGUAGES (Now Alphabetized) --------
unsorted_languages = {
    "Hindi": "hi", "English": "en", "Spanish": "es", "French": "fr", 
    "German": "de", "Telugu": "te", "Tamil": "ta", "Bengali": "bn",
    "Japanese": "ja", "Korean": "ko", "Chinese": "zh-CN", "Italian": "it",
    "Russian": "ru", "Arabic": "ar", "Portuguese": "pt"
}

# Sort the dictionary by keys (Language Names)
languages = dict(sorted(unsorted_languages.items()))

# -------- GLOBAL STATES --------
is_looping = False
is_playing = False

def set_status(msg):
    status_label.config(text=msg)
    root.update()

def set_volume(val):
    pygame.mixer.music.set_volume(float(val) / 100)

# -------- CORE FUNCTIONS --------
def play_audio():
    global is_playing
    text = text_area.get("1.0", tk.END).strip()
    if not text: return

    if pygame.mixer.music.get_busy():
        stop_audio()
        time.sleep(0.2)

    lang = languages[lang_var.get()]
    set_status("Processing... 🎧")
    filename = f"temp_{int(time.time())}.mp3"

    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(filename)
    except:
        set_status("Error: Check Internet")
        return

    is_playing = True

    def run():
        global is_playing
        set_status("Playing...")
        while is_playing:
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                if not is_playing:
                    pygame.mixer.music.stop()
                    break
                time.sleep(0.1)
            if not is_looping or not is_playing: break

        is_playing = False
        set_status("")
        pygame.mixer.music.unload()
        if os.path.exists(filename):
            try: os.remove(filename)
            except: pass

    threading.Thread(target=run, daemon=True).start()

def stop_audio():
    global is_playing, is_looping
    is_playing = False
    is_looping = False
    pygame.mixer.music.stop()
    set_status("Stopped")

def rewind_audio():
    stop_audio()
    root.after(200, play_audio)

def toggle_loop():
    global is_looping
    is_looping = not is_looping
    set_status("Loop ON 🔁" if is_looping else "Loop OFF")

# -------- UI DESIGN --------
root = tk.Tk()
root.title("Voice Studio Pro")
root.geometry("850x900")
root.configure(bg="#1E1E1E") 

# Center Container
main = tk.Frame(root, bg="#1E1E1E")
main.place(relx=0.5, rely=0.5, anchor="center")

# TITLE
tk.Label(main, text="Voice Studio", font=("Segoe UI", 30, "bold"), 
         bg="#1E1E1E", fg="#D8B4FE").pack(pady=20)

# TEXT AREA
text_area = tk.Text(main, height=11, width=65, font=("Segoe UI", 12), 
                    bg="#2D2D2D", fg="#F0F0F0", relief="flat", padx=15, pady=15)
text_area.pack(pady=10)

# SETTINGS (Centered)
settings = tk.Frame(main, bg="#1E1E1E")
settings.pack(pady=10)

lang_var = tk.StringVar(value="English") # Set default to English
lang_drop = ttk.Combobox(settings, textvariable=lang_var, values=list(languages.keys()), 
                         state="readonly", width=25)
lang_drop.pack(pady=5)

vol_slider = tk.Scale(settings, from_=0, to=100, orient="horizontal", label="Volume",
                      command=set_volume, bg="#1E1E1E", fg="#D8B4FE", 
                      highlightthickness=0, troughcolor="#2D2D2D", length=200)
vol_slider.set(70)
vol_slider.pack(pady=5)

# MEDIA CONTROLS
media = tk.Frame(main, bg="#1E1E1E")
media.pack(pady=20)

media_btn_style = {"font": ("Segoe UI", 16), "width": 5, "bg": "#D8B4FE", 
                   "fg": "#1E1E1E", "relief": "flat", "cursor": "hand2", "activebackground": "#C499F3"}

tk.Button(media, text="⏪", command=rewind_audio, **media_btn_style).grid(row=0, column=0, padx=10)
tk.Button(media, text="⏸", command=stop_audio, **media_btn_style).grid(row=0, column=1, padx=10)
tk.Button(media, text="▶", command=play_audio, **media_btn_style).grid(row=0, column=2, padx=10)
tk.Button(media, text="🔁", command=toggle_loop, **media_btn_style).grid(row=0, column=3, padx=10)

# FEATURES (Action Row)
btn_frame = tk.Frame(main, bg="#1E1E1E")
btn_frame.pack(pady=10)

feat_style = {"font": ("Segoe UI", 10, "bold"), "bg": "#A78BFA", "fg": "#FFFFFF", 
              "relief": "flat", "padx": 15, "pady": 8, "cursor": "hand2"}

# Feature Logic
def run_translation():
    set_status("Translating...")
    text = text_area.get("1.0", tk.END).strip()
    translated = GoogleTranslator(source='auto', target=languages[lang_var.get()]).translate(text)
    text_area.delete("1.0", tk.END)
    text_area.insert(tk.END, translated)
    set_status("")

def run_ocr():
    file_path = filedialog.askopenfilename()
    if file_path:
        set_status("Reading image...")
        text = pytesseract.image_to_string(Image.open(file_path))
        text_area.insert(tk.END, text)
        set_status("")

tk.Button(btn_frame, text="Translate", command=lambda: threading.Thread(target=run_translation).start(), **feat_style).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Upload Image", command=lambda: threading.Thread(target=run_ocr).start(), **feat_style).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Save MP3", command=lambda: gTTS(text_area.get("1.0", tk.END), lang=languages[lang_var.get()]).save("output.mp3"), **feat_style).grid(row=0, column=2, padx=5)
tk.Button(btn_frame, text="Clear", command=lambda: text_area.delete("1.0", tk.END), **feat_style).grid(row=0, column=3, padx=5)

# STATUS
status_label = tk.Label(main, text="", bg="#1E1E1E", fg="#9CA3AF", font=("Segoe UI", 10))
status_label.pack(pady=20)

root.mainloop()
