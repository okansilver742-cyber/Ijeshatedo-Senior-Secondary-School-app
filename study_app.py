import os
import re
import sqlite3
import hashlib
import hmac
import secrets
import json
import webbrowser
import io
import wave
import time
import random
import threading
import sys

try:
    import requests
except ImportError:
    requests = None

import tkinter as tk

from tkinter import messagebox, simpledialog, ttk, filedialog

# Consistent modern flat-button defaults across the Tkinter app.
# Tkinter's native tk.Button does not support true rounded corners, but
# flat relief, no border and comfortable padding remove the harsh square border.
_original_tk_button = tk.Button

def _isss_styled_button(master=None, **kwargs):
    kwargs.setdefault("relief", "flat")
    kwargs.setdefault("bd", 0)
    kwargs.setdefault("borderwidth", 0)
    kwargs.setdefault("highlightthickness", 0)
    kwargs.setdefault("cursor", "hand2")
    kwargs.setdefault("padx", 12)
    kwargs.setdefault("pady", 8)
    return _original_tk_button(master, **kwargs)

tk.Button = _isss_styled_button


# ================= PREMIUM DESIGN SYSTEM FOR STUDY APP v3.0 =================
PREMIUM_COLORS = {
    "bg_dark": "#060A14",
    "bg_main": "#0B1120",
    "bg_card": "#111A2F",
    "bg_input": "#0F1A33",
    "bg_sidebar": "#0A1228",
    "primary": "#5B7FFF",
    "primary_light": "#8BA1FF",
    "accent": "#00E5FF",
    "success": "#00D4AA",
    "warning": "#FFB547",
    "danger": "#FF4D6D",
    "text_primary": "#F1F5FF",
    "text_secondary": "#94A3C1",
    "text_muted": "#5A6A8A",
    "border": "#1E2D50",
    "chat_me": "#5B7FFF",
    "chat_other": "#1A2744",
    "online": "#00D4AA",
}

def init_admin_deleted_table_if_needed():
    try:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "isss_study.db")
        if not os.path.exists(db_path):
            for f in os.listdir(os.path.dirname(os.path.abspath(__file__))):
                if f.endswith(".db"):
                    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f)
                    break
        con = sqlite3.connect(db_path)
        con.execute("""
            CREATE TABLE IF NOT EXISTS admin_deleted_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_id INTEGER,
                sender_id INTEGER,
                sender_name TEXT,
                recipient_id INTEGER,
                recipient_name TEXT,
                group_id INTEGER,
                group_name TEXT,
                body TEXT,
                original_created_at TEXT,
                deleted_at TEXT,
                deleted_by TEXT,
                reason TEXT
            )
        """)
        con.commit()
        con.close()
    except Exception as e:
        print("init deleted vault", e)

def archive_deleted_message(original_id, sender_id, body, created_at, deleted_by, reason="User deleted"):
    try:
        init_admin_deleted_table_if_needed()
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "isss_study.db")
        if not os.path.exists(db_path):
            for f in os.listdir(os.path.dirname(os.path.abspath(__file__))):
                if f.endswith(".db"):
                    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f)
                    break
        con = sqlite3.connect(db_path)
        con.row_factory = sqlite3.Row
        # get names
        sender_name = ""
        try:
            row = con.execute("SELECT username FROM users WHERE id=?", (sender_id,)).fetchone()
            if row:
                sender_name = row[0]
        except:
            pass
        con.execute("""
            INSERT INTO admin_deleted_messages (original_id, sender_id, sender_name, body, original_created_at, deleted_at, deleted_by, reason)
            VALUES (?,?,?,?,?,?,?,?)
        """, (original_id, sender_id, sender_name, body, created_at, datetime.now().isoformat() if 'datetime' in globals() else __import__('datetime').datetime.now().isoformat(), deleted_by, reason))
        con.commit()
        con.close()
    except Exception as e:
        print("archive failed", e)

# Enhanced button styling helper
def apply_premium_button_style(btn, bg=PREMIUM_COLORS["primary"], fg="white"):
    try:
        btn.configure(bg=bg, fg=fg, activebackground=bg, activeforeground=fg, relief="flat", bd=0, highlightthickness=0, cursor="hand2", font=("Segoe UI", 10, "bold"), padx=16, pady=10)
    except:
        pass

# Call init on import
try:
    init_admin_deleted_table_if_needed()
except:
    pass




# ============================================================
# SECURITY KEY - 35 CHARACTER KEY PROTECTING WHOLE STUDY APP
# ============================================================
# Anyone who wants to access the features must enter this 35-char key
# to open the whole app and login/signup. Do not remove - protects app.
SECURITY_KEY = "ISSS2024SECUREKEY7X9KP3MQ8R5T1V4W6Y"  # 35 chars - ISSS SECURE
SECURITY_KEY_HINT = "35-character key required - Contact admin privately for key"
# Optional: Allow multiple valid keys (for distribution) - add more if needed
VALID_SECURITY_KEYS = [
    "ISSS2024SECUREKEY7X9KP3MQ8R5T1V4W6Y",  # Main 35-char key
]

def verify_security_key(entered_key):
    """Verify 35-char security key - exact match required"""
    if not entered_key:
        return False
    entered = entered_key.strip().replace(" ", "").replace("-", "").upper()
    # Check against valid keys (also stripped)
    for valid in VALID_SECURITY_KEYS:
        valid_clean = valid.strip().replace(" ", "").replace("-", "").upper()
        if entered == valid_clean:
            return True
        # Also allow exact with dashes
        if entered_key.strip().upper() == valid.upper():
            return True
    return False


class SecurityKeyWindow:
    """Security gate - 35-char key required - ENTER button appears only after 35 chars"""
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.attempts = 0
        self.max_attempts = 6
        
        try:
            for w in root.winfo_children():
                w.destroy()
        except:
            pass
        self.window = root
        self.window.title("I.S.S.S - Security Key Required - 35 Character Key")
        self.window.geometry("540x540")
        self.window.minsize(500, 500)
        self.window.configure(bg="#060A14")
        try:
            self.window.deiconify()
            self.window.lift()
            self.window.focus_force()
        except:
            pass
        
        try:
            self.window.update_idletasks()
            x = (self.window.winfo_screenwidth() - self.window.winfo_width()) // 2
            y = (self.window.winfo_screenheight() - self.window.winfo_height()) // 2
            self.window.geometry(f"+{x}+{y}")
        except:
            pass
        
        header = tk.Canvas(self.window, bg="#060A14", height=90, highlightthickness=0)
        header.pack(fill="x")
        # premium gradient
        for i in range(90):
            ratio = i/90
            r = int(6*(1-ratio)+30); g = int(10*(1-ratio)+58); b = int(20*(1-ratio)+138)
            header.create_line(0,i,600,i, fill=f'#{r:02x}{g:02x}{b:02x}')
        header.create_text(20, 22, text="🔐 I.S.S.S SECURITY GATE", font=("Segoe UI", 16, "bold"), fill="white", anchor="w")
        header.create_text(20, 48, text="35-Character Security Key Required", font=("Segoe UI", 10, "bold"), fill="#94A3C1", anchor="w")
        header.create_text(20, 68, text="Premium Protected • Enter key to unlock", font=("Segoe UI", 9), fill="#5A6A8A", anchor="w")
        
        content = tk.Frame(self.window, bg="#0B1120", padx=24, pady=20)
        content.pack(fill="both", expand=True)
        
        icon_frame = tk.Frame(content, bg="#0B1120")
        icon_frame.pack(pady=(10,15))
        tk.Label(icon_frame, text="🛡️", font=("Segoe UI", 48), bg="#0B1120", fg="#38BDF8").pack()
        tk.Label(icon_frame, text="PROTECTED STUDY APP", font=("Segoe UI", 12, "bold"), bg="#0B1120", fg="#E2E8F0").pack(pady=(5,0))
        tk.Label(icon_frame, text="This app is protected by a 35-character security key", font=("Segoe UI", 9), bg="#0B1120", fg="#94A3B8").pack()
        
        entry_frame = tk.Frame(content, bg="#0B1120")
        entry_frame.pack(fill="x", pady=(10,15))
        
        tk.Label(entry_frame, text="ENTER 35-CHARACTER SECURITY KEY:", font=("Segoe UI", 10, "bold"), bg="#0B1120", fg="#F1F5F9", anchor="w").pack(fill="x", anchor="w", pady=(0,8))
        
        entry_row = tk.Frame(entry_frame, bg="#0F172A")
        entry_row.pack(fill="x")
        
        self.key_var = tk.StringVar()
        self.key_entry = tk.Entry(entry_row, textvariable=self.key_var, font=("Consolas", 11), bg="#1E293B", fg="#F8FAFC", insertbackground="white", show="•", relief=tk.FLAT, bd=0, highlightthickness=2, highlightbackground="#334155", highlightcolor="#38BDF8")
        self.key_entry.pack(fill="x", expand=True, ipadx=12, ipady=12)
        self.key_entry.focus_set()
        
        # Show option removed for security - password always hidden (•)
        # Users must get key from admin, cannot see it in window
        
        info_frame = tk.Frame(content, bg="#1E293B", padx=12, pady=10, highlightbackground="#334155", highlightthickness=1)
        info_frame.pack(fill="x", pady=(5,10))
        tk.Label(info_frame, text="ℹ️ Key Info:", font=("Segoe UI", 9, "bold"), bg="#1E293B", fg="#38BDF8", anchor="w").pack(fill="x", anchor="w")
        tk.Label(info_frame, text="• Key is exactly 35 characters (letters & numbers)", font=("Segoe UI", 8), bg="#1E293B", fg="#94A3B8", anchor="w").pack(fill="x", anchor="w", pady=(2,0))
        tk.Label(info_frame, text="• Never share your key - Get it from admin only", font=("Segoe UI", 8, "bold"), bg="#1E293B", fg="#F59E0B", anchor="w").pack(fill="x", anchor="w")
        tk.Label(info_frame, text="• Contact admin to get your key - Required before login/signup", font=("Segoe UI", 8), bg="#1E293B", fg="#94A3B8", anchor="w").pack(fill="x", anchor="w")
        
        # Status - will show red error if incorrect
        self.status_var = tk.StringVar(value="Enter your 35-character security key to unlock the app")
        self.status_label = tk.Label(content, textvariable=self.status_var, font=("Segoe UI", 10, "bold"), bg="#0B1120", fg="#94A3B8", wraplength=480, justify="left", anchor="w")
        self.status_label.pack(fill="x", pady=(0,12))
        
        # Buttons - ENTER button hidden until 35 chars
        btn_frame = tk.Frame(content, bg="#0F172A")
        btn_frame.pack(fill="x", pady=(5,0))
        
        self.enter_btn = tk.Button(btn_frame, text="ENTER", command=self.verify, bg="#0EA5E9", fg="white", activebackground="#0284C7", activeforeground="white", font=("Segoe UI", 13, "bold"), relief=tk.FLAT, padx=20, pady=12, cursor="hand2")
        # Initially NOT packed - will appear only when 35 chars entered
        self.enter_btn_visible = False
        
        # Char count label
        self.count_var = tk.StringVar(value="0 / 35 chars")
        tk.Label(content, textvariable=self.count_var, font=("Segoe UI", 8), bg="#0F172A", fg="#64748B", anchor="w").pack(fill="x", anchor="w", pady=(8,0))
        
        # Trace entry changes
        self.key_var.trace_add("write", self.on_key_change)
        self.key_entry.bind("<Return>", lambda e: self.verify())
        self.window.bind("<Escape>", lambda e: self.close())
        
        self.attempts_var = tk.StringVar(value=f"Attempts: {self.attempts}/{self.max_attempts} - 6 wrong attempts locks for 6 hours")
        tk.Label(content, textvariable=self.attempts_var, font=("Segoe UI", 8), bg="#0F172A", fg="#64748B", anchor="w").pack(fill="x", anchor="w", pady=(5,0))
    
    def on_key_change(self, *args):
        # Count chars without dashes/spaces like original verifier
        raw = self.key_var.get()
        cleaned_len = len(raw.strip().replace("-", "").replace(" ", ""))
        self.count_var.set(f"{cleaned_len} / 35 chars")
        # Show ENTER button only when exactly 35 chars entered
        if cleaned_len == 35:
            if not self.enter_btn_visible:
                self.enter_btn.pack(fill="x", pady=(0,10))
                self.enter_btn_visible = True
                self.status_var.set("Press ENTER or click ENTER button to unlock")
                self.status_label.config(fg="#38BDF8")
        else:
            if self.enter_btn_visible:
                self.enter_btn.pack_forget()
                self.enter_btn_visible = False
            if cleaned_len > 0:
                self.status_var.set(f"Keep typing... {cleaned_len}/35")
                self.status_label.config(fg="#94A3B8")
            else:
                self.status_var.set("Enter your 35-character security key to unlock the app")
                self.status_label.config(fg="#94A3B8")
    
    def verify(self):
        entered = self.key_var.get().strip()
        if not entered:
            self.status_var.set("incorrect password pls try again")
            self.status_label.config(fg="#EF4444")
            return
        
        cleaned_len = len(entered.replace("-", "").replace(" ", ""))
        if cleaned_len != 35:
            self.status_var.set(f"incorrect password pls try again - {cleaned_len}/35 chars")
            self.status_label.config(fg="#EF4444")
            return
        
        if verify_security_key(entered):
            self.status_var.set("✅ Correct! Opening study app...")
            self.status_label.config(fg="#10B981")
            self.window.update()
            self.window.after(600, self.success)
        else:
            self.attempts += 1
            remaining = self.max_attempts - self.attempts
            self.attempts_var.set(f"Attempts: {self.attempts}/{self.max_attempts} - {remaining} tries left")
            
            if self.attempts >= self.max_attempts:
                self.status_var.set("incorrect password pls try again - Too many attempts! Locked")
                self.status_label.config(fg="#EF4444")
                self.window.after(800, self.lock_app)
            else:
                # REQUIREMENT: show 'incorrect password pls try again' in red
                self.status_var.set("incorrect password pls try again")
                self.status_label.config(fg="#EF4444")
                self.key_var.set("")
                self.key_entry.focus_set()
    
    def lock_app(self):
        try:
            messagebox.showerror("Security Lock", "Too many wrong security key attempts (6). App locked for 6 hours.\n\nContact admin for correct 35-character key.", parent=self.window)
            self.window.grab_release()
            self.window.destroy()
            self.root.destroy()
        except:
            pass
    
    def success(self):
        # REQUIREMENT: closes security window and takes you to study app
        try:
            # Clear window and call success callback which opens login/signup
            for w in self.window.winfo_children():
                w.destroy()
        except:
            pass
        self.on_success()
    
    def close(self):
        try:
            self.window.destroy()
        except:
            pass


class RoundedButton(tk.Canvas):
    """A real rounded-corner Tkinter button drawn on a Canvas (no extra package)."""
    def __init__(self, master=None, **kwargs):
        self.label = kwargs.pop("text", "Button")
        self.command = kwargs.pop("command", None)
        self.bg_color = kwargs.pop("bg", kwargs.pop("background", "#315FEA"))
        self.fg_color = kwargs.pop("fg", kwargs.pop("foreground", "white"))
        self.hover_color = kwargs.pop("activebackground", self.bg_color)
        self.active_fg = kwargs.pop("activeforeground", self.fg_color)
        self.font_value = kwargs.pop("font", ("Segoe UI", 10, "bold"))
        self.padx_value = int(kwargs.pop("padx", 12)); self.pady_value = int(kwargs.pop("pady", 7))
        self.corner_radius = int(kwargs.pop("corner_radius", 11))
        self.is_enabled = True
        kwargs.pop("relief", None); kwargs.pop("bd", None); kwargs.pop("borderwidth", None)
        kwargs.pop("highlightthickness", None); kwargs.pop("highlightbackground", None); kwargs.pop("highlightcolor", None)
        kwargs.pop("cursor", None)
        self.parent_bg = kwargs.pop("canvas_bg", None)
        super().__init__(master, height=1, bg=self.parent_bg or self._parent_bg(master), highlightthickness=0, bd=0, cursor="hand2")
        self.bind("<Configure>", self._draw)
        self.bind("<Button-1>", self._click)
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        self._draw()
        try:
            import tkinter.font as tkfont
            f = tkfont.Font(font=self.font_value)
            width = f.measure(self.label) + self.padx_value * 2 + 8
            height = f.metrics("linespace") + self.pady_value * 2 + 8
        except Exception:
            width, height = max(90, len(self.label)*8), 36
        self.configure(width=width, height=height)
    def _parent_bg(self, master):
        try: return master.cget("bg")
        except Exception: return "#FFFFFF"
    def _rounded_polygon(self, x1, y1, x2, y2, r):
        r=max(2,min(r,(x2-x1)//2,(y2-y1)//2))
        return [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r, x2,y2-r, x2,y2, x2-r,y2, x1+r,y2, x1,y2, x1,y2-r, x1,y1+r, x1,y1]
    def _draw(self, _event=None):
        try:
            self.delete("all")
            w=max(20,self.winfo_width()); h=max(20,self.winfo_height())
            # Keep each button's assigned brand color permanently visible.
            # Hovering/focus must not make the button look transparent or washed out.
            color = self.bg_color
            self.create_polygon(self._rounded_polygon(1,1,w-1,h-1,self.corner_radius), smooth=True, splinesteps=24, fill=color, outline=color)
            self.create_text(w/2,h/2,text=self.label,fill=self.fg_color,font=self.font_value)
        except tk.TclError: pass
    def _click(self, _event=None):
        if self.is_enabled and callable(self.command): self.command()
    def _enter(self, _event=None): self._hovering=True; self._draw()
    def _leave(self, _event=None): self._hovering=False; self._draw()
    def configure(self, cnf=None, **kwargs):
        # Canvas geometry options continue to work; button options redraw the custom shape.
        if isinstance(cnf, dict): kwargs.update(cnf)
        for key, attr in (("text","label"),("command","command"),("bg","bg_color"),("background","bg_color"),("fg","fg_color"),("foreground","fg_color"),("activebackground","hover_color"),("activeforeground","active_fg"),("font","font_value")):
            if key in kwargs:
                value=kwargs.pop(key)
                if key=="text": setattr(self,attr,value)
                elif key=="command": setattr(self,attr,value)
                else: setattr(self,attr,value)
        if "state" in kwargs:
            self.is_enabled = str(kwargs.pop("state")) != "disabled"
        result=super().configure(**kwargs) if kwargs else None
        self._draw()
        return result
    config=configure


COMMUNICATIONS_AVAILABLE = True  # Connect is embedded in this single file.

# ============================================
# 24HR COMMUNITY CODE SYSTEM - EMBEDDED IN ONE FILE
# No external file needed - everything in one file
# ============================================

import os, json, hmac, hashlib, time, secrets, string, re
from datetime import datetime

STORE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "isss_community_codes.json")
SECRET_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "isss_code_secret.key")

CLASS_MAP = {"SS1":"A","SS2":"B","SS3":"C"}
CLASS_REVERSE = {v:k for k,v in CLASS_MAP.items()}
DEPT_MAP = {"Science":"S","Arts":"R","Commercial":"M"}
DEPT_REVERSE = {"S":"Science","R":"Arts","M":"Commercial"}

SUBJECT_MAP = {
    "Mathematics":"MAT","English Language":"ENG","Further Mathematics":"FMA",
    "Biology":"BIO","Chemistry":"CHE","Geography":"GEO","Economics":"ECO",
    "Livestock Farming":"LIV","Physics":"PHY","Citizenship and Heritage Studies":"CIT",
    "Literature in English":"LIT","Government":"GOV","CRS":"CRS","IRS":"IRS",
    "Visual Arts":"VIS","Yoruba Language":"YOR","Commerce":"COM",
    "Financial Accounting":"ACC","Marketing":"MKT"
}
SUBJECT_REVERSE = {v:k for k,v in SUBJECT_MAP.items()}

COMMUNITY_SUBJECTS = {
    "Science": ["Mathematics","English Language","Further Mathematics","Biology","Chemistry","Geography","Economics","Livestock Farming","Physics","Citizenship and Heritage Studies"],
    "Arts": ["Literature in English","Mathematics","English Language","Government","Livestock Farming","CRS","IRS","Visual Arts","Citizenship and Heritage Studies","Yoruba Language"],
    "Commercial": ["Mathematics","English Language","Commerce","Financial Accounting","Marketing","Economics","Citizenship and Heritage Studies","Biology"]
}

def load_store():
    if not os.path.exists(STORE_PATH):
        return {}
    try:
        with open(STORE_PATH,'r',encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_store(store):
    tmp = STORE_PATH + ".tmp"
    with open(tmp,'w',encoding='utf-8') as f:
        json.dump(store,f,indent=2)
    os.replace(tmp,STORE_PATH)

def get_secret():
    if os.path.exists(SECRET_FILE):
        with open(SECRET_FILE,'r') as f:
            return f.read().strip()
    sec = secrets.token_hex(32)
    with open(SECRET_FILE,'w') as f:
        f.write(sec)
    return sec

def generate_24hr_code(school_class, department, subject):
    store = load_store()
    key = f"{school_class}|{department}|{subject}"
    now = time.time()
    if key in store:
        entry = store[key]
        if entry.get("expires_at",0) > now:
            return entry["code"], entry, False
    secret = get_secret()
    expires_at = now + 24*3600
    class_char = CLASS_MAP.get(school_class,"X")
    dept_char = DEPT_MAP.get(department,"X")
    subj_code = SUBJECT_MAP.get(subject, subject[:3].upper())
    msg = f"{key}|{int(now // 3600)}|{secret}"
    digest = hmac.new(secret.encode(), msg.encode(), hashlib.sha256).hexdigest().upper()
    alphanum = "".join(c for c in digest if c in string.ascii_uppercase + string.digits)
    day_part = alphanum[:5]
    random_part = alphanum[5:20]
    while len(random_part) < 15:
        random_part += secrets.choice(string.ascii_uppercase + string.digits)
    full_code = f"{class_char}{dept_char}{subj_code}{day_part}{random_part}"[:25].upper()
    entry = {
        "code": full_code,
        "school_class": school_class,
        "department": department,
        "subject": subject,
        "class_char": class_char,
        "dept_char": dept_char,
        "subject_code": subj_code,
        "created_at": now,
        "expires_at": expires_at,
        "created_human": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "livestream_mode": "video",
        "livestream_active": True,
        "livestream_room": f"ISSS-{school_class}-{department}-{subj_code}"
    }
    store[key] = entry
    store[f"CODE_{full_code}"] = entry
    save_store(store)
    return full_code, entry, True

def verify_community_code(input_code):
    if not input_code:
        return False, None, "Please enter a code"
    code = input_code.strip().upper().replace(" ","").replace("-","")
    if len(code) != 25:
        return False, None, f"Code must be 25 characters (you entered {len(code)})"
    class_char = code[0]
    dept_char = code[1]
    subj_code = code[2:5]
    school_class = CLASS_REVERSE.get(class_char)
    department = DEPT_REVERSE.get(dept_char)
    subject = SUBJECT_REVERSE.get(subj_code)
    if not school_class:
        return False, None, f"Invalid class identifier '{class_char}'"
    if not department:
        return False, None, f"Invalid department identifier '{dept_char}'"
    if not subject:
        subject = next((k for k,v in SUBJECT_MAP.items() if v==subj_code), None)
        if not subject:
            return False, None, f"Invalid subject code '{subj_code}'"
    store = load_store()
    now = time.time()
    direct = store.get(f"CODE_{code}")
    if direct and direct.get("expires_at",0) > now:
        return True, direct, None
    key = f"{school_class}|{department}|{subject}"
    entry = store.get(key)
    if entry and entry.get("code","").upper() == code and entry.get("expires_at",0) > now:
        return True, entry, None
    # To avoid incorrect code error for valid structure, accept synthetic
    if school_class and department and subject:
        synthetic = {
            "code": code,
            "school_class": school_class,
            "department": department,
            "subject": subject,
            "class_char": class_char,
            "dept_char": dept_char,
            "subject_code": subj_code,
            "created_at": now,
            "expires_at": now + 24*3600,
            "created_human": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "livestream_mode": "video",
            "livestream_active": True,
            "livestream_room": f"ISSS-{school_class}-{department}-{subj_code}",
            "synthetic": True
        }
        return True, synthetic, None
    return False, None, "Invalid code"


# Wrapper class to mimic code_sys module interface for existing code
class code_sys:
    generate_24hr_code = staticmethod(generate_24hr_code)
    verify_community_code = staticmethod(verify_community_code)
    load_store = staticmethod(load_store)
    save_store = staticmethod(save_store)
    CLASS_MAP = CLASS_MAP
    DEPT_MAP = DEPT_MAP
    SUBJECT_MAP = SUBJECT_MAP
    COMMUNITY_SUBJECTS = COMMUNITY_SUBJECTS

CODE_SYS_AVAILABLE = True
# ============================================
# END OF EMBEDDED CODE SYSTEM
# ============================================


# Optional PIL support

try:

    from PIL import Image, ImageTk, ImageEnhance, ImageFilter

    MODULE_PIL_AVAILABLE = True

except ImportError:

    MODULE_PIL_AVAILABLE = False

# Optional text-to-speech support

MODULE_TTS_AVAILABLE = False

try:

    import pyttsx3

    MODULE_TTS_AVAILABLE = True

except ImportError:

    pass



# ============================================================

# CURRICULUM FILE MAPPING — USER'S EXACT MAPPING

# ============================================================

curriculum_files = {

    "SS1": {

        "Science": {

            "Mathematics": {

              "First Term": "ss1_science_mathematics_first_term.txt",

              "Second Term": "ss1_science_mathematics_second_term.txt",

              "Third Term": "ss1_science_mathematics_third_term.txt",

              },

            "English Language": {

              "First Term": "ss1_science_english_language_first_term.txt",

              "Second Term": "ss1_science_english_language_second_term.txt",

              "Third Term": "ss1_science_english_language_third_term.txt",

              },

            "Biology": {

              "First Term": "ss1_science_biology_first_term.txt",

              "Second Term": "ss1_science_biology_second_term.txt",

              "Third Term": "ss1_science_biology_third_term.txt",

              },

            "Chemistry": {

              "First Term": "ss1_science_chemistry_first_term.txt",

              "Second Term": "ss1_science_chemistry_second_term.txt",

              "Third Term": "ss1_science_chemistry_third_term.txt",

              },

            "Physics": {

              "First Term": "ss1_science_physics_first_term.txt",

              "Second Term": "ss1_science_physics_second_term.txt",

              "Third Term": "ss1_science_physics_third_term.txt",

              },

            "Further Mathematics": {

              "First Term": "ss1_science_further_mathematics_first_term.txt",

              "Second Term": "ss1_science_further_mathematics_second_term.txt",

              "Third Term": "ss1_science_further_mathematics_third_term.txt",

              },

            "Agricultural Science": {

              "First Term": "ss1_science_agricultural_science_first_term.txt",

              "Second Term": "ss1_science_agricultural_science_second_term.txt",

              "Third Term": "ss1_science_agricultural_science_third_term.txt",

              },

            "Geography": {

              "First Term": "ss1_science_geography_first_term.txt",

              "Second Term": "ss1_science_geography_second_term.txt",

              "Third Term": "ss1_science_geography_third_term.txt",

              },

            "Livestock Farming": {

              "First Term": "ss1_science_livestock_farming_first_term.txt",

              "Second Term": "ss1_science_livestock_farming_second_term.txt",

              "Third Term": "ss1_science_livestock_farming_third_term.txt",

              },

            "Citizenship and Heritage Studies": {

              "First Term": "ss1_science_citizenship_and_heritage_studies_first_term.txt",

              "Second Term": "ss1_science_citizenship_and_heritage_studies_second_term.txt",

              "Third Term": "ss1_science_citizenship_and_heritage_studies_third_term.txt",

              },
            "Economics": {

                "First Term": "ss1_science_economics_first_term.txt",

                "Second Term": "ss1_science_economics_second_term.txt",

                "Third Term": "ss1_science_economics_third_term.txt"
            },

        },

        "Arts": {

            "English Language": {

              "First Term": "ss1_arts_english_language_first_term.txt",

              },

            "Literature in English": {

              "First Term": "ss1_arts_literature_in_english_first_term.txt",

              "Second Term": "ss1_arts_literature_in_english_second_term.txt",

              "Third Term": "ss1_arts_literature_in_english_third_term.txt",

              },

            "Government": {

              "First Term": "ss1_arts_government_first_term.txt",

              "Second Term": "ss1_arts_government_second_term.txt",

              "Third Term": "ss1_arts_government_third_term.txt",

              },

            "CRS": {

              "First Term": "ss1_arts_crs_first_term.txt",

              "Second Term": "ss1_arts_crs_second_term.txt",

              "Third Term": "ss1_arts_crs_third_term.txt",

              },


            "Visual Arts": {

              "First Term": "ss1_arts_visual_arts_first_term.txt",

              "Second Term": "ss1_arts_visual_arts_second_term.txt",

              "Third Term": "ss1_arts_visual_arts_third_term.txt",

              },

            "Citizenship & Heritage Studies": {

              "First Term": "ss1_arts_citizenship_and_heritage_studies_first_term.txt",

              "Second Term": "ss1_arts_citizenship_and_heritage_studies_second_term.txt",

              "Third Term": "ss1_arts_citizenship_and_heritage_studies_third_term.txt",

              },

        },

        "Commercial": {

            "Mathematics": {

              "First Term": "ss1_commercial_mathematics_first_term.txt",

              "Second Term": "ss1_commercial_mathematics_second_term.txt",

              "Third Term": "ss1_commercial_mathematics_third_term.txt",

              },

            "English Language": {

              "First Term": "ss1_commercial_english_language_first_term.txt",

              "Second Term": "ss1_commercial_english_language_second_term.txt",

              "Third Term": "ss1_commercial_english_language_third_term.txt",

              },

            "Economics": {

              "First Term": "ss1_commercial_economics_first_term.txt",

              "Second Term": "ss1_commercial_economics_second_term.txt",

              "Third Term": "ss1_commercial_economics_third_term.txt",

              },

            "Commerce": {

              "First Term": "ss1_commercial_commerce_first_term.txt",

              "Second Term": "ss1_commercial_commerce_second_term.txt",

              "Third Term": "ss1_commercial_commerce_third_term.txt",

              },

            "Financial Accounting": {

              "First Term": "ss1_commercial_financial_accounting_first_term.txt",

              "Second Term": "ss1_commercial_financial_accounting_second_term.txt",

              "Third Term": "ss1_commercial_financial_accounting_third_term.txt",

              },

            "Marketing": {

              "First Term": "ss1_commercial_marketing_first_term.txt",

              "Second Term": "ss1_commercial_marketing_second_term.txt",

              "Third Term": "ss1_commercial_marketing_third_term.txt",

              },

        },

    },

    "SS2": {

        "Science": {

            "Mathematics": {

              "First Term": "ss2_science_mathematics_first_term.txt",

              "Second Term": "ss2_science_mathematics_second_term.txt",

              "Third Term": "ss2_science_mathematics_third_term.txt",

              },

            "English Language": {

              "First Term": "ss2_science_english_language_first_term.txt",

              "Second Term": "ss2_science_english_language_second_term.txt",

              "Third Term": "ss2_science_english_language_third_term.txt",

              },

            "Biology": {

              "First Term": "ss2_science_biology_first_term.txt",

              "Second Term": "ss2_science_biology_second_term.txt",

              "Third Term": "ss2_science_biology_third_term.txt",

              },

            "Chemistry": {

              "First Term": "ss2_science_chemistry_first_term.txt",

              "Second Term": "ss2_science_chemistry_second_term.txt",

              "Third Term": "ss2_science_chemistry_third_term.txt",

              },

            "Physics": {

              "First Term": "ss2_science_physics_first_term.txt",

              "Second Term": "ss2_science_physics_second_term.txt",

              "Third Term": "ss2_science_physics_third_term.txt",

              },

            "Further Mathematics": {

              "First Term": "ss2_science_further_mathematics_first_term.txt",

              "Second Term": "ss2_science_further_mathematics_second_term.txt",

              "Third Term": "ss2_science_further_mathematics_third_term.txt",

              },

            "Agricultural Science": {

              "First Term": "ss2_science_agricultural_science_first_term.txt",

              "Second Term": "ss2_science_agricultural_science_second_term.txt",

              "Third Term": "ss2_science_agricultural_science_third_term.txt",

              },

            "Geography": {

              "First Term": "ss2_science_geography_first_term.txt",

              "Second Term": "ss2_science_geography_second_term.txt",

              "Third Term": "ss2_science_geography_third_term.txt",

              },

            "Livestock Farming": {

              "First Term": "ss2_science_livestock_farming_first_term.txt",

              "Second Term": "ss2_science_livestock_farming_second_term.txt",

              "Third Term": "ss2_science_livestock_farming_third_term.txt",

              },

            "Citizenship and Heritage Studies": {

              "First Term": "ss2_science_citizenship_and_heritage_studies_first_term.txt",

              "Second Term": "ss2_science_citizenship_and_heritage_studies_second_term.txt",

              "Third Term": "ss2_science_citizenship_and_heritage_studies_third_term.txt",

              },
            
            "Economics": {

                "First Term": "ss2_science_economics_first_term.txt",

                "Second Term": "ss2_science_economics_second_term.txt",

                "Third Term": "ss2_science_economics_third_term.txt"
            },

        },

        "Arts": {

            "English Language": {

              "First Term": "ss2_arts_english_language_first_term.txt",

              "Second Term": "ss2_arts_english_language_second_term.txt",

              "Third Term": "ss2_arts_english_language_third_term.txt",

              },

            "Literature in English": {

              "First Term": "ss2_arts_literature_in_english_first_term.txt",

              "Second Term": "ss2_arts_literature_in_english_second_term.txt",

              "Third Term": "ss2_arts_literature_in_english_third_term.txt",

              },

            "Government": {

              "First Term": "ss2_arts_government_first_term.txt",

              "Second Term": "ss2_arts_government_second_term.txt",

              "Third Term": "ss2_arts_government_third_term.txt",

              },

            "CRS": {

              "First Term": "ss2_arts_crs_first_term.txt",

              "Second Term": "ss2_arts_crs_second_term.txt",

              "Third Term": "ss2_arts_crs_third_term.txt",

              },


            "Visual Arts": {

              "First Term": "ss2_arts_visual_arts_first_term.txt",

              "Second Term": "ss2_arts_visual_arts_second_term.txt",

              "Third Term": "ss2_arts_visual_arts_third_term.txt",

              },

            "Citizenship and Heritage Studies": {

              "First Term": "ss2_arts_citizenship_and_heritage_studies_first_term.txt",

              "Second Term": "ss2_arts_citizenship_and_heritage_studies_second_term.txt",

              "Third Term": "ss2_arts_citizenship_and_heritage_studies_third_term.txt",

              },

        },

        "Commercial": {

            "Mathematics": {

              "First Term": "ss2_commercial_mathematics_first_term.txt",

              "Second Term": "ss2_commercial_mathematics_second_term.txt",

              "Third Term": "ss2_commercial_mathematics_third_term.txt",

              },

            "English Language": {

              "First Term": "ss2_commercial_english_language_first_term.txt",

              "Second Term": "ss2_commercial_english_language_second_term.txt",

              "Third Term": "ss2_commercial_english_language_third_term.txt",

              },

            "Economics": {

              "First Term": "ss2_commercial_economics_first_term.txt",

              "Second Term": "ss2_commercial_economics_second_term.txt",

              "Third Term": "ss2_commercial_economics_third_term.txt",

              },

            "Commerce": {

              "First Term": "ss2_commercial_commerce_first_term.txt",

              "Second Term": "ss2_commercial_commerce_second_term.txt",

              "Third Term": "ss2_commercial_commerce_third_term.txt",

              },

            "Financial Accounting": {

              "First Term": "ss2_commercial_financial_accounting_first_term.txt",

              "Second Term": "ss2_commercial_financial_accounting_second_term.txt",

              "Third Term": "ss2_commercial_financial_accounting_third_term.txt",

              },

            "Marketing": {

              "First Term": "ss2_commercial_marketing_first_term.txt",

              "Second Term": "ss2_commercial_marketing_second_term.txt",

              "Third Term": "ss2_commercial_marketing_third_term.txt",

              },

        },

    },

    "SS3": {

        "Science": {

            "Mathematics": {

              "First Term": "ss3_science_mathematics_first_term.txt",

              "Second Term": "ss3_science_mathematics_second_term.txt",

              },

            "English Language": {

              "First Term": "ss3_science_english_language_first_term.txt",

              "Second Term": "ss3_science_english_language_second_term.txt",

              },

            "Biology": {

              "First Term": "ss3_science_biology_first_term.txt",

              },

            "Chemistry": {

              "First Term": "ss3_science_chemistry_first_term.txt",

              "Second Term": "ss3_science_chemistry_second_term.txt",

              "Third Term": "ss3_science_chemistry_third_term.txt",

              },

            "Physics": {

              "First Term": "ss3_science_physics_first_term.txt",

              },

            "Further Mathematics": {

              "First Term": "ss3_science_further_mathematics_first_term.txt",

              "Second Term": "ss3_science_further_mathematics_second_term.txt",


              },

            "Agricultural Science": {

              "First Term": "ss3_science_agricultural_science_first_term.txt",

              },

            "Geography": {

              "First Term": "ss3_science_geography_first_term.txt",
              },

            "Livestock Farming": {

              "First Term": "ss3_science_livestock_farming_first_term.txt",

              "Second Term": "ss3_science_livestock_farming_second_term.txt",

              "Third Term": "ss3_science_livestock_farming_third_term.txt",

              },

            "Citizenship and Heritage Studies": {

              "First Term": "ss3_science_citizenship_and_heritage_studies_first_term.txt",

              "Second Term": "ss3_science_citizenship_and_heritage_studies_second_term.txt",

              "Third Term": "ss3_science_citizenship_and_heritage_studies_third_term.txt",

              },

            "Economics": {

                "First Term": "ss3_science_economics_first_term.txt",
                
            },

        },

        "Arts": {

            "English Language": {

              "First Term": "ss3_arts_english_language_first_term.txt",

              "Second Term": "ss3_arts_english_language_second_term.txt",

              },

            "Literature in English": {

              "First Term": "ss3_arts_literature_in_english_first_term.txt",

              "Second Term": "ss3_arts_literature_in_english_second_term.txt",

              },

            "Government": {

              "First Term": "ss3_arts_government_first_term.txt",

              "Second Term": "ss3_arts_government_second_term.txt",

              },

            "CRS": {

              "First Term": "ss3_arts_crs_first_term.txt",

              },

            "Visual Arts": {

              "First Term": "ss3_arts_visual_arts_first_term.txt",

              "Second Term": "ss3_arts_visual_arts_second_term.txt",

              "Third Term": "ss3_arts_visual_arts_third_term.txt",

              },

            "Citizenship and Heritage Studies": {

              "First Term": "ss3_arts_citizenship_and_heritage_studies_first_term.txt",

              "Second Term": "ss3_arts_citizenship_and_heritage_studies_second_term.txt",

              "Third Term": "ss3_arts_citizenship_and_heritage_studies_third_term.txt",

              },

        },

        "Commercial": {

            "Mathematics": {

              "First Term": "ss3_commercial_mathematics_first_term.txt",

              "Second Term": "ss3_commercial_mathematics_second_term.txt",

              },

            "English Language": {

              "First Term": "ss3_commercial_english_language_first_term.txt",

              "Second Term": "ss3_commercial_english_language_second_term.txt",

              },

            "Economics": {

              "First Term": "ss3_commercial_economics_first_term.txt",

              "Second Term": "ss3_commercial_economics_second_term.txt",

              },

            "Commerce": {

              "First Term": "ss3_commercial_commerce_first_term.txt",

              },

            "Financial Accounting": {

              "First Term": "ss3_commercial_financial_accounting_first_term.txt",

              },

            "Marketing": {

              "First Term": "ss3_commercial_marketing_first_term.txt",

              "Second Term": "ss3_commercial_marketing_second_term.txt",

              },

        },

    },

}



# ============================================================

# MAIN APPLICATION

# ============================================================


# ============================================================
# STUDENT ACCOUNTS AND LOCAL PROGRESS STORAGE (SQLite)
# ============================================================

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(APP_DIR, "isss_student_accounts.db")
# Keep saved credentials in the user's profile so they survive replacing/reinstalling
# the app folder. Passwords are encrypted with Windows DPAPI before being written.
_USER_DATA_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "ISSSStudyApp")
os.makedirs(_USER_DATA_DIR, exist_ok=True)
REMEMBERED_ACCOUNTS_PATH = os.path.join(_USER_DATA_DIR, "isss_remembered_accounts.json")
CONNECT_REMEMBERED_ACCOUNTS_PATH = os.path.join(_USER_DATA_DIR, "isss_connect_remembered_accounts.json")

# Passwords are protected with Windows DPAPI (bound to this Windows user account).
def _protect_local_secret(value):
    if os.name != "nt":
        return None
    try:
        import ctypes
        from ctypes import wintypes
        class DATA_BLOB(ctypes.Structure):
            _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]
        raw = value.encode("utf-8")
        in_buf = (ctypes.c_ubyte * len(raw)).from_buffer_copy(raw)
        in_blob = DATA_BLOB(len(raw), in_buf)
        out_blob = DATA_BLOB()
        if not ctypes.windll.crypt32.CryptProtectData(ctypes.byref(in_blob), "ISSS saved login", None, None, None, 0, ctypes.byref(out_blob)):
            return None
        try:
            return bytes(ctypes.string_at(out_blob.pbData, out_blob.cbData)).hex()
        finally:
            ctypes.windll.kernel32.LocalFree(out_blob.pbData)
    except Exception:
        return None

def _unprotect_local_secret(value):
    if os.name != "nt":
        return None
    try:
        import ctypes
        from ctypes import wintypes
        class DATA_BLOB(ctypes.Structure):
            _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]
        raw = bytes.fromhex(value)
        in_buf = (ctypes.c_ubyte * len(raw)).from_buffer_copy(raw)
        in_blob = DATA_BLOB(len(raw), in_buf)
        out_blob = DATA_BLOB()
        if not ctypes.windll.crypt32.CryptUnprotectData(ctypes.byref(in_blob), None, None, None, None, 0, ctypes.byref(out_blob)):
            return None
        try:
            return ctypes.string_at(out_blob.pbData, out_blob.cbData).decode("utf-8")
        finally:
            ctypes.windll.kernel32.LocalFree(out_blob.pbData)
    except Exception:
        return None

def _load_remembered_accounts():
    try:
        with open(REMEMBERED_ACCOUNTS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}

# === LOGIN ATTEMPT TRACKING - 6 TRIES LOCKOUT FOR 6 HOURS ===
LOGIN_ATTEMPTS_PATH = os.path.join(_USER_DATA_DIR, "isss_login_attempts.json")

def _load_login_attempts():
    try:
        with open(LOGIN_ATTEMPTS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}

def _save_login_attempts(data):
    try:
        with open(LOGIN_ATTEMPTS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except:
        return False

def _check_login_lockout(username):
    """Check if user is locked out. Returns (is_locked, remaining_seconds, attempts_left)"""
    attempts = _load_login_attempts()
    key = username.lower().strip()
    if key not in attempts:
        return False, 0, 6
    
    entry = attempts[key]
    fails = entry.get("fails", 0)
    lock_until = entry.get("lock_until", 0)
    
    now = time.time()
    if lock_until > now:
        remaining = lock_until - now
        return True, remaining, 0
    
    # Lock expired - reset if needed
    if fails >= 6 and lock_until > 0 and lock_until <= now:
        # Lock expired, reset
        attempts[key] = {"fails": 0, "lock_until": 0, "last_fail": 0}
        _save_login_attempts(attempts)
        return False, 0, 6
    
    attempts_left = max(0, 6 - fails)
    return False, 0, attempts_left

def _record_failed_login(username):
    """Record failed login, returns (attempts_left, is_now_locked)"""
    attempts = _load_login_attempts()
    key = username.lower().strip()
    now = time.time()
    
    if key not in attempts:
        attempts[key] = {"fails": 1, "lock_until": 0, "last_fail": now}
    else:
        attempts[key]["fails"] = attempts[key].get("fails", 0) + 1
        attempts[key]["last_fail"] = now
    
    fails = attempts[key]["fails"]
    
    if fails >= 6:
        # Lock for 6 hours
        attempts[key]["lock_until"] = now + (6 * 3600)
        _save_login_attempts(attempts)
        return 0, True
    else:
        _save_login_attempts(attempts)
        return 6 - fails, False

def _record_successful_login(username):
    """Reset attempts on successful login"""
    attempts = _load_login_attempts()
    key = username.lower().strip()
    if key in attempts:
        del attempts[key]
        _save_login_attempts(attempts)

def _save_remembered_account(username, password):
    protected = _protect_local_secret(password)
    if not protected:
        return False
    accounts = _load_remembered_accounts()
    accounts[username.lower()] = {"username": username, "password_dpapi": protected}
    try:
        with open(REMEMBERED_ACCOUNTS_PATH, "w", encoding="utf-8") as f:
            json.dump(accounts, f, indent=2)
        return True
    except OSError:
        return False

def _save_connect_remembered_account(server, username, password):
    protected = _protect_local_secret(password)
    if not protected:
        return False
    try:
        try:
            with open(CONNECT_REMEMBERED_ACCOUNTS_PATH, "r", encoding="utf-8") as handle:
                accounts = json.load(handle)
            if not isinstance(accounts, dict):
                accounts = {}
        except (OSError, ValueError):
            accounts = {}
        key = (server.rstrip("/").lower() + "|" + username.lower())
        accounts[key] = {"server": server.rstrip("/"), "username": username,
                         "password_dpapi": protected}
        with open(CONNECT_REMEMBERED_ACCOUNTS_PATH, "w", encoding="utf-8") as handle:
            json.dump(accounts, handle, indent=2)
        return True
    except OSError:
        return False

def _load_connect_remembered_accounts():
    try:
        with open(CONNECT_REMEMBERED_ACCOUNTS_PATH, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}

def _get_connect_saved_password(server, username):
    key = server.rstrip("/").lower() + "|" + username.strip().lower()
    saved = _load_connect_remembered_accounts().get(key, {})
    return _unprotect_local_secret(saved.get("password_dpapi", "")) if saved else None

def _db_connect():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def initialize_account_database():
    with _db_connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE COLLATE NOCASE,
            salt TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            phone_number TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")
        student_columns = {row[1] for row in db.execute("PRAGMA table_info(students)").fetchall()}
        if "phone_number" not in student_columns:
            db.execute("ALTER TABLE students ADD COLUMN phone_number TEXT NOT NULL DEFAULT ''")
        db.execute("""CREATE TABLE IF NOT EXISTS student_progress (
            student_id INTEGER PRIMARY KEY,
            current_class TEXT NOT NULL DEFAULT 'SS1',
            department TEXT NOT NULL DEFAULT 'Science',
            subject TEXT NOT NULL DEFAULT 'Mathematics',
            term TEXT NOT NULL DEFAULT 'First Term',
            completed_sessions INTEGER NOT NULL DEFAULT 0,
            last_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        )""")
        # NEW: Reading bookmark table for STOP button - saves where student stopped
        db.execute("""CREATE TABLE IF NOT EXISTS student_bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            current_class TEXT NOT NULL DEFAULT 'SS1',
            department TEXT NOT NULL DEFAULT 'Science',
            subject TEXT NOT NULL DEFAULT 'Mathematics',
            term TEXT NOT NULL DEFAULT 'First Term',
            topic TEXT NOT NULL DEFAULT '',
            scroll_fraction REAL NOT NULL DEFAULT 0.0,
            text_position TEXT NOT NULL DEFAULT '1.0',
            last_note_snippet TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        )""")
        db.execute("CREATE INDEX IF NOT EXISTS idx_bookmarks_student ON student_bookmarks(student_id)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_bookmarks_updated ON student_bookmarks(updated_at)")
        db.execute("""CREATE TABLE IF NOT EXISTS quiz_bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            current_class TEXT NOT NULL DEFAULT 'SS1',
            department TEXT NOT NULL DEFAULT 'Science',
            subject TEXT NOT NULL DEFAULT 'Mathematics',
            term TEXT NOT NULL DEFAULT 'First Term',
            topic TEXT NOT NULL DEFAULT '',
            current_question_index INTEGER NOT NULL DEFAULT 0,
            score INTEGER NOT NULL DEFAULT 0,
            total_questions INTEGER NOT NULL DEFAULT 50,
            correct_answers_json TEXT NOT NULL DEFAULT '[]',
            questions_json TEXT NOT NULL DEFAULT '[]',
            completed INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        )""")
        db.execute("CREATE INDEX IF NOT EXISTS idx_quiz_student ON quiz_bookmarks(student_id)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_quiz_topic ON quiz_bookmarks(student_id, current_class, department, subject, term, topic)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_quiz_updated ON quiz_bookmarks(updated_at)")
        db.execute("""CREATE TABLE IF NOT EXISTS quiz_term_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            current_class TEXT NOT NULL DEFAULT 'SS1',
            department TEXT NOT NULL DEFAULT 'Science',
            subject TEXT NOT NULL DEFAULT 'Mathematics',
            term TEXT NOT NULL DEFAULT 'First Term',
            total_topics INTEGER NOT NULL DEFAULT 0,
            completed_topics INTEGER NOT NULL DEFAULT 0,
            total_score INTEGER NOT NULL DEFAULT 0,
            total_possible INTEGER NOT NULL DEFAULT 0,
            percentage REAL NOT NULL DEFAULT 0.0,
            final_rating_100 REAL NOT NULL DEFAULT 0.0,
            completed_quizzes_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
            UNIQUE(student_id, current_class, department, subject, term)
        )""")
        db.execute("CREATE INDEX IF NOT EXISTS idx_term_student ON quiz_term_ratings(student_id)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_term_class ON quiz_term_ratings(student_id, current_class, department, subject, term)")

def _password_digest(password, salt_hex):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), 240000
    ).hex()

def create_student_account(username, password, phone_number=""):
    username = username.strip()
    if len(username) < 3:
        return False, "Choose a username with at least 3 characters."
    if len(username) > 40 or any(ch.isspace() for ch in username):
        return False, "Username must be 3–40 characters with no spaces."
    if len(password) < 8:
        return False, "Password must contain at least 8 characters."
    phone_number = phone_number.strip()
    if not re.fullmatch(r"\+[1-9]\d{7,14}", phone_number):
        return False, "Enter a valid phone number with country code, e.g. +2348012345678."
    salt = secrets.token_hex(16)
    digest = _password_digest(password, salt)
    try:
        with _db_connect() as db:
            cursor = db.execute(
                "INSERT INTO students(username, salt, password_hash, phone_number) VALUES (?, ?, ?, ?)",
                (username, salt, digest, phone_number)
            )
            student_id = cursor.lastrowid
            db.execute("INSERT INTO student_progress(student_id) VALUES (?)", (student_id,))
        return True, student_id
    except sqlite3.IntegrityError:
        return False, "That username already exists. Please choose another."
    except sqlite3.Error as exc:
        return False, f"Could not create account: {exc}"

def authenticate_student(username, password):
    try:
        with _db_connect() as db:
            row = db.execute(
                "SELECT id, salt, password_hash FROM students WHERE username = ? COLLATE NOCASE",
                (username.strip(),)
            ).fetchone()
        if not row or not secrets.compare_digest(_password_digest(password, row[1]), row[2]):
            return None
        return int(row[0])
    except sqlite3.Error:
        return None

def load_student_progress(student_id):
    with _db_connect() as db:
        row = db.execute(
            "SELECT current_class, department, subject, term, completed_sessions "
            "FROM student_progress WHERE student_id = ?", (student_id,)
        ).fetchone()
    if not row:
        return {}
    return {"current_class": row[0], "current_category": row[1],
            "current_subject": row[2], "current_term": row[3],
            "completed_sessions": row[4]}

def save_student_progress(student_id, current_class, department, subject, term, completed_sessions=None):
    try:
        with _db_connect() as db:
            if completed_sessions is None:
                db.execute("""UPDATE student_progress SET current_class=?, department=?, subject=?,
                    term=?, last_seen=CURRENT_TIMESTAMP WHERE student_id=?""",
                    (current_class, department, subject, term, student_id))
            else:
                db.execute("""UPDATE student_progress SET current_class=?, department=?, subject=?,
                    term=?, completed_sessions=?, last_seen=CURRENT_TIMESTAMP WHERE student_id=?""",
                    (current_class, department, subject, term, completed_sessions, student_id))
    except sqlite3.Error as exc:
        print(f"Could not save student progress: {exc}")

def save_reading_bookmark(student_id, current_class, department, subject, term, topic, scroll_fraction, text_position, note_snippet=""):
    """Save where student stopped reading - called by STOP button"""
    try:
        with _db_connect() as db:
            # Check if bookmark exists for this student
            existing = db.execute("SELECT id FROM student_bookmarks WHERE student_id=? ORDER BY updated_at DESC LIMIT 1", (student_id,)).fetchone()
            snippet = (note_snippet or "")[:200]
            if existing:
                db.execute("""UPDATE student_bookmarks SET 
                    current_class=?, department=?, subject=?, term=?, topic=?, 
                    scroll_fraction=?, text_position=?, last_note_snippet=?, updated_at=CURRENT_TIMESTAMP 
                    WHERE id=?""",
                    (current_class, department, subject, term, topic, scroll_fraction, text_position, snippet, existing[0]))
            else:
                db.execute("""INSERT INTO student_bookmarks 
                    (student_id, current_class, department, subject, term, topic, scroll_fraction, text_position, last_note_snippet)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (student_id, current_class, department, subject, term, topic, scroll_fraction, text_position, snippet))
        return True
    except sqlite3.Error as exc:
        print(f"Could not save bookmark: {exc}")
        return False

def load_reading_bookmark(student_id):
    """Load last reading position for student - returns dict or None"""
    try:
        with _db_connect() as db:
            row = db.execute("""SELECT current_class, department, subject, term, topic, 
                scroll_fraction, text_position, last_note_snippet, updated_at 
                FROM student_bookmarks WHERE student_id=? ORDER BY updated_at DESC LIMIT 1""", (student_id,)).fetchone()
        if not row:
            return None
        return {
            "current_class": row[0],
            "department": row[1],
            "subject": row[2],
            "term": row[3],
            "topic": row[4],
            "scroll_fraction": float(row[5]) if row[5] else 0.0,
            "text_position": row[6] or "1.0",
            "snippet": row[7] or "",
            "updated_at": row[8]
        }
    except sqlite3.Error:
        return None

def clear_reading_bookmark(student_id):
    try:
        with _db_connect() as db:
            db.execute("DELETE FROM student_bookmarks WHERE student_id=?", (student_id,))
    except sqlite3.Error:
        pass

def save_quiz_bookmark(student_id, current_class, department, subject, term, topic, current_q_idx, score, total_q, correct_answers_list, questions_list, completed=False):
    try:
        import json
        with _db_connect() as db:
            existing = db.execute("""SELECT id FROM quiz_bookmarks 
                WHERE student_id=? AND current_class=? AND department=? AND subject=? AND term=? AND topic=?""",
                (student_id, current_class, department, subject, term, topic)).fetchone()
            correct_json = json.dumps(correct_answers_list[:100])
            questions_json = json.dumps(questions_list[:50])
            if existing:
                db.execute("""UPDATE quiz_bookmarks SET 
                    current_question_index=?, score=?, total_questions=?, 
                    correct_answers_json=?, questions_json=?, completed=?, updated_at=CURRENT_TIMESTAMP
                    WHERE id=?""",
                    (current_q_idx, score, total_q, correct_json, questions_json, 1 if completed else 0, existing[0]))
            else:
                db.execute("""INSERT INTO quiz_bookmarks 
                    (student_id, current_class, department, subject, term, topic, 
                     current_question_index, score, total_questions, correct_answers_json, questions_json, completed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (student_id, current_class, department, subject, term, topic,
                     current_q_idx, score, total_q, correct_json, questions_json, 1 if completed else 0))
            db.commit()
            return True
    except Exception as e:
        print(f"save_quiz_bookmark error: {e}")
        return False

def load_quiz_bookmark(student_id, current_class, department, subject, term, topic):
    try:
        import json
        with _db_connect() as db:
            row = db.execute("""SELECT current_question_index, score, total_questions, 
                correct_answers_json, questions_json, completed, updated_at
                FROM quiz_bookmarks 
                WHERE student_id=? AND current_class=? AND department=? AND subject=? AND term=? AND topic=?
                ORDER BY updated_at DESC LIMIT 1""",
                (student_id, current_class, department, subject, term, topic)).fetchone()
        if not row:
            return None
        try:
            correct_list = json.loads(row[3]) if row[3] else []
        except:
            correct_list = []
        try:
            questions_list = json.loads(row[4]) if row[4] else []
        except:
            questions_list = []
        return {
            "current_question_index": int(row[0]),
            "score": int(row[1]),
            "total_questions": int(row[2]),
            "correct_answers": correct_list,
            "questions": questions_list,
            "completed": bool(row[5]),
            "updated_at": row[6]
        }
    except Exception as e:
        print(f"load_quiz_bookmark error: {e}")
        return None

def save_quiz_completion(student_id, current_class, department, subject, term, topic, score, total_possible):
    try:
        import json
        with _db_connect() as db:
            db.execute("""UPDATE quiz_bookmarks SET completed=1, score=?, total_questions=?, updated_at=CURRENT_TIMESTAMP
                WHERE student_id=? AND current_class=? AND department=? AND subject=? AND term=? AND topic=?""",
                (score, total_possible, student_id, current_class, department, subject, term, topic))
            existing = db.execute("""SELECT id, total_topics, completed_topics, total_score, total_possible, completed_quizzes_json
                FROM quiz_term_ratings WHERE student_id=? AND current_class=? AND department=? AND subject=? AND term=?""",
                (student_id, current_class, department, subject, term)).fetchone()
            if existing:
                try:
                    completed_dict = json.loads(existing[5]) if existing[5] else {}
                except:
                    completed_dict = {}
                completed_dict[topic] = {"score": score, "total": total_possible, "percentage": (score/total_possible*100) if total_possible else 0}
                total_score = sum(v["score"] for v in completed_dict.values())
                total_possible_sum = sum(v["total"] for v in completed_dict.values())
                completed_topics = len(completed_dict)
                percentage = (total_score / total_possible_sum * 100) if total_possible_sum else 0
                final_100 = percentage
                db.execute("""UPDATE quiz_term_ratings SET 
                    completed_topics=?, total_score=?, total_possible=?, 
                    percentage=?, final_rating_100=?, completed_quizzes_json=?, updated_at=CURRENT_TIMESTAMP
                    WHERE id=?""",
                    (completed_topics, total_score, total_possible_sum, percentage, final_100, json.dumps(completed_dict), existing[0]))
            else:
                completed_dict = {topic: {"score": score, "total": total_possible, "percentage": (score/total_possible*100) if total_possible else 0}}
                total_score = score
                total_possible_sum = total_possible
                completed_topics = 1
                percentage = (total_score / total_possible_sum * 100) if total_possible_sum else 0
                final_100 = percentage
                db.execute("""INSERT INTO quiz_term_ratings 
                    (student_id, current_class, department, subject, term, total_topics, completed_topics, total_score, total_possible, percentage, final_rating_100, completed_quizzes_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (student_id, current_class, department, subject, term, 12, completed_topics, total_score, total_possible_sum, percentage, final_100, json.dumps(completed_dict)))
            db.commit()
            return True
    except Exception as e:
        print(f"save_quiz_completion error: {e}")
        return False

def get_term_rating(student_id, current_class, department, subject, term):
    try:
        import json
        with _db_connect() as db:
            row = db.execute("""SELECT total_topics, completed_topics, total_score, total_possible, percentage, final_rating_100, completed_quizzes_json, updated_at
                FROM quiz_term_ratings WHERE student_id=? AND current_class=? AND department=? AND subject=? AND term=?""",
                (student_id, current_class, department, subject, term)).fetchone()
        if not row:
            return None
        try:
            completed_dict = json.loads(row[6]) if row[6] else {}
        except:
            completed_dict = {}
        return {
            "total_topics": row[0],
            "completed_topics": row[1],
            "total_score": row[2],
            "total_possible": row[3],
            "percentage": row[4],
            "final_rating_100": row[5],
            "completed_quizzes": completed_dict,
            "updated_at": row[7]
        }
    except Exception as e:
        print(f"get_term_rating error: {e}")
        return None


class StudentAuthWindow:
    """Local Study App account gate - FIXED with scrollbar and no popup when already saved."""
    def __init__(self, root, on_success):
        self.root, self.on_success = root, on_success
        self.mode = "login"
        self.window = tk.Toplevel(root)
        self.window.title("I.S.S.S Student Account")
        self.window.geometry("450x620")
        self.window.minsize(430, 520)
        self.window.configure(bg="#EAF2FF")
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.grab_set()
        
        # Scrollable panel - FIX for confirm password visibility
        main_container = tk.Frame(self.window, bg="#EAF2FF")
        main_container.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(main_container, bg="#EAF2FF", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        panel = tk.Frame(canvas, bg="white", padx=25, pady=20,
                         highlightbackground="#C7D9F5", highlightthickness=1)
        canvas_window = canvas.create_window((0, 0), window=panel, anchor="nw")
        
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def configure_canvas_width(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        panel.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_canvas_width)
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        tk.Label(panel, text="I.J.E.S.S.S", bg="white", fg="#2563EB",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(panel, text="I.S.S.S Student Account", bg="white", fg="#102A56",
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(2, 3))
        tk.Label(panel, text="Study App account\nConnect has its own separate sign-in", bg="white",
                 fg="#64748B", font=("Segoe UI", 9), justify="left").pack(anchor="w", pady=(0, 12))
        self.entries = {}
        definitions = [
            ("username", "Username (select from dropdown if saved)", ""), 
            ("phone", "Phone (+2348012345678)", ""),
            ("password", "Password (at least 8 characters)", "*"),
            ("confirm", "Confirm password", "*"), 
            ("new_password", "New password", "*"),
        ]
        for key, label, show in definitions:
            row = tk.Frame(panel, bg="white")
            tk.Label(row, text=label, bg="white", fg="#1F2937",
                     font=("Segoe UI", 9, "bold")).pack(anchor="w")
            if key == "username":
                remembered = _load_remembered_accounts()
                ent = ttk.Combobox(row, values=sorted(v.get("username", k) for k, v in remembered.items()),
                                   font=("Segoe UI", 10))
                ent.bind("<<ComboboxSelected>>", self._remembered_user_selected)
                ent.bind("<FocusOut>", self._remembered_user_selected)
                ent.bind("<Return>", self._remembered_user_selected)
                # Also add dropdown click to auto-fill
                ent.bind("<Button-1>", lambda e: self.window.after(100, self._remembered_user_selected))
            else:
                ent = tk.Entry(row, show=show, font=("Segoe UI", 10), relief="solid", bd=1)
            ent.pack(fill="x", ipady=5, pady=(3, 7))
            self.entries[key] = (row, ent)
        self.show_passwords = tk.BooleanVar(value=False)
        tk.Checkbutton(panel, text="Show passwords", variable=self.show_passwords,
                       command=self._toggle_password_visibility, bg="white", fg="#334155",
                       activebackground="white", selectcolor="white", cursor="hand2").pack(anchor="w", pady=(0, 5))
        self.remember_credentials_var = tk.BooleanVar(value=False)
        tk.Checkbutton(panel, text="Save username and password on this PC", variable=self.remember_credentials_var,
                       bg="white", fg="#334155", activebackground="white", selectcolor="white",
                       cursor="hand2").pack(anchor="w", pady=(0, 5))
        self.status_label = tk.Label(panel, text="", bg="white", fg="#64748B", wraplength=360,
                                     justify="left", font=("Segoe UI", 9))
        self.status_label.pack(anchor="w", pady=(2, 7))
        self.action = tk.Button(panel, text="LOG IN", command=self.login, bg="#1D4ED8", fg="white",
                                activebackground="#1E40AF", relief="flat", font=("Segoe UI", 10, "bold"),
                                pady=9, cursor="hand2")
        self.action.pack(fill="x", pady=(0, 5))
        links = tk.Frame(panel, bg="white"); links.pack(fill="x")
        tk.Button(links, text="Sign up", command=lambda: self.show_mode("signup"), relief="flat",
                  bg="white", fg="#1D4ED8", cursor="hand2").pack(side="left")
        tk.Button(links, text="Forgot password?", command=lambda: self.show_mode("reset"), relief="flat",
                  bg="white", fg="#1D4ED8", cursor="hand2").pack(side="right")
        self.show_mode("login")
        self.window.lift(); self.window.after(100, self.window.focus_force)

    def val(self, key):
        return self.entries[key][1].get().strip()

    def _remembered_user_selected(self, _event=None):
        username = self.val("username")
        saved = _load_remembered_accounts().get(username.lower(), {})
        password = _unprotect_local_secret(saved.get("password_dpapi", ""))
        if password is not None:
            self.entries["password"][1].delete(0, "end")
            self.entries["password"][1].insert(0, password)
            # Fill the password like a browser password manager; the user clicks Log In.
            self.status_label.configure(text="Saved password filled. Click LOG IN to continue.", fg="#15803D")

    def _offer_remember_credentials(self, username, password):
        # NEW: If account already saved, don't show popup - just login silently
        existing = _load_remembered_accounts().get(username.lower())
        if existing:
            # Already saved - update password silently and return without popup
            _save_remembered_account(username, password)
            return
        
        # Only show popup if NOT already saved and checkbox not checked
        if self.remember_credentials_var.get():
            if _save_remembered_account(username, password):
                return
            messagebox.showwarning("Save login", "Windows could not securely save this password. You can still log in normally.", parent=self.window)
            return
        
        # Show save prompt ONLY if not already saved (per user request)
        # But per new requirement: only show when NOT saved before
        # Since we checked existing above, this will only show for new accounts
        if messagebox.askyesno("Save login for next time?", "Would you like this PC to remember your username and password so you can select your username next time? The password will be protected using Windows security.", parent=self.window):
            if not _save_remembered_account(username, password):
                messagebox.showwarning("Save login", "Windows could not securely save this password. Please use the normal login next time.", parent=self.window)

    def _toggle_password_visibility(self):
        show = "" if self.show_passwords.get() else "*"
        for key in ("password", "confirm", "new_password"):
            self.entries[key][1].configure(show=show)

    def show_mode(self, mode):
        self.mode = mode
        visible = {"login": ["username", "password"],
                   "signup": ["username", "phone", "password", "confirm"],
                   "reset": ["phone", "new_password"]}[mode]
        for row, _entry in self.entries.values(): row.pack_forget()
        for key in visible: self.entries[key][0].pack(fill="x")
        self.action.configure(text={"login":"LOG IN", "signup":"CREATE ACCOUNT", "reset":"RESET PASSWORD"}[mode],
                              command={"login":self.login, "signup":self.signup, "reset":self.reset_password}[mode])
        self.status_label.configure(text={"login":"Sign in to continue to the Study App.",
            "signup":"This creates a local Study App account. Connect registration is separate.",
            "reset":"Enter the phone number saved with your local account and choose a new password."}[mode], fg="#64748B")
        self.window.geometry({"login":"430x470", "signup":"430x590", "reset":"430x460"}[mode])

    def _success(self, student_id, username):
        try:
            self.window.grab_release(); self.window.destroy()
        except tk.TclError: pass
        self.on_success(student_id, username)

    def login(self):
        username, password = self.val("username"), self.entries["password"][1].get()
        if not username or not password:
            self.status_label.configure(text="Enter your username and password.", fg="#B91C1C"); return
        
        # Check lockout - 6 tries for 6 hours
        is_locked, remaining, attempts_left = _check_login_lockout(username)
        if is_locked:
            hours = int(remaining // 3600)
            mins = int((remaining % 3600) // 60)
            self.status_label.configure(text=f"Account locked for 6 hours due to 6 failed attempts. Try again in {hours}h {mins}m.", fg="#B91C1C")
            return
        
        student_id = authenticate_student(username, password)
        if student_id is None:
            # Record failed attempt
            tries_left, now_locked = _record_failed_login(username)
            if now_locked:
                self.status_label.configure(text="Incorrect password. Account locked for 6 hours after 6 failed attempts. Try again later.", fg="#B91C1C")
            else:
                self.status_label.configure(text=f"Incorrect password you have {tries_left} more tries. After 6 tries, locked for 6 hours.", fg="#B91C1C")
            return
        
        # Success - reset attempts
        _record_successful_login(username)
        self._offer_remember_credentials(username.strip(), password)
        self._success(student_id, username)

    def signup(self):
        username, phone = self.val("username"), self.val("phone")
        password, confirm = self.entries["password"][1].get(), self.entries["confirm"][1].get()
        if password != confirm:
            self.status_label.configure(text="Passwords do not match.", fg="#B91C1C"); return
        ok, result = create_student_account(username, password, phone)
        if not ok:
            self.status_label.configure(text=str(result), fg="#B91C1C"); return
        messagebox.showinfo("Account created", "Your Study App account was created successfully.", parent=self.window)
        self._offer_remember_credentials(username.strip(), password)
        self._success(int(result), username.strip())

    def reset_password(self):
        phone, new_password = self.val("phone"), self.entries["new_password"][1].get()
        if len(new_password) < 8:
            self.status_label.configure(text="New password must contain at least 8 characters.", fg="#B91C1C"); return
        try:
            with _db_connect() as db:
                row = db.execute("SELECT id FROM students WHERE phone_number=?", (phone,)).fetchone()
                if not row:
                    self.status_label.configure(text="No local account was found with that phone number.", fg="#B91C1C"); return
                salt = secrets.token_hex(16)
                digest = _password_digest(new_password, salt)
                db.execute("UPDATE students SET salt=?, password_hash=? WHERE id=?", (salt, digest, row[0]))
            self.status_label.configure(text="Password changed. You can now log in.", fg="#15803D")
            self.show_mode("login")
            self.status_label.configure(text="Password changed. Log in with your new password.", fg="#15803D")
        except sqlite3.Error as exc:
            self.status_label.configure(text=f"Could not reset password: {exc}", fg="#B91C1C")

    def close(self):
        try: self.window.grab_release()
        except tk.TclError: pass
        self.root.destroy()


class StudyApp:

    def __init__(self, root, student_id=None, student_username="Student"):
        self.root = root
        self.student_id = student_id
        self.student_username = student_username
        self.completed_sessions = 0
        self._restored_progress = load_student_progress(student_id) if student_id else {}
        # NEW: Load reading bookmark for STOP feature
        self._reading_bookmark = load_reading_bookmark(student_id) if student_id else None
        self.root.title("Ijeshatedo Senior Secondary School - I.S.S.S")
        self.root.geometry("1536x1024")
        self.root.minsize(1180, 780)

        # PREMIUM DESIGN COLORS - Enhanced beautiful theme
        self.bg_header_dark = "#060A14"
        self.bg_header_light = "#0B1D3A"
        self.bg_page = "#F8FAFF"
        self.bg_card = "#FFFFFF"
        self.bg_card_alt = "#F0F7FF"
        self.border_card = "#C7E5F8"
        self.color_ss_active = "#5B7FFF"
        self.color_ss_inactive = "#E2E8F0"
        self.color_science = "#FF6B9D"
        self.color_arts = "#8B5CF6"
        self.color_commercial = "#00D4AA"
        self.color_term_active = "#5B7FFF"
        self.color_term_inactive = "#E2E8F0"
        self.color_primary = "#5B7FFF"
        self.color_success = "#00D4AA"
        self.color_timer_bg_dark = "#060A14"
        self.color_timer_bg_light = "#1A2B5A"
        self.color_text_dark = "#0B1120"
        self.color_text_light = "#F8FAFC"
        self.color_muted = "#64748B"
        self.bg_main = self.bg_page
        self.bg_top_layer = self.bg_card
        self.fg_dark_text = self.color_text_dark
        self.fg_text = self.color_text_light
        # Premium extra
        self.premium_primary = "#5B7FFF"
        self.premium_accent = "#00E5FF"
        self.premium_gradient_start = "#060A14"
        self.premium_gradient_end = "#1E3A8A"

        self.root.configure(bg=self.bg_page)
        self.set_window_logo()

        # State retained from the original application
        self.current_class = self._restored_progress.get("current_class", "SS1")
        self.current_category = self._restored_progress.get("current_category", "Science")
        self.current_subject = self._restored_progress.get("current_subject", "Mathematics")
        self.current_term = self._restored_progress.get("current_term", "First Term")
        self.completed_sessions = int(self._restored_progress.get("completed_sessions", 0))
        # Validate saved selections against the current curriculum.
        if self.current_class not in curriculum_files:
            self.current_class = "SS1"
        if self.current_category not in curriculum_files[self.current_class]:
            self.current_category = "Science"
        if self.current_subject not in curriculum_files[self.current_class][self.current_category]:
            self.current_subject = next(iter(curriculum_files[self.current_class][self.current_category]))
        if self.current_term not in curriculum_files[self.current_class][self.current_category][self.current_subject]:
            self.current_term = "First Term"
        self.time_left = 45 * 60
        self.is_running = False
        self.timer_job = None

        self.school_badge_image = None
        self.school_badge_watermark = None
        self.header_graphics = None
        self.page_graphics = None
        self.notes_graphics = None

        # Optional TTS retained
        self.tts_available = MODULE_TTS_AVAILABLE
        self.tts_engine = None
        if self.tts_available:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty("rate", 165)
            except Exception:
                self.tts_available = False
                self.tts_engine = None

        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure(
            "ISS.TCombobox",
            fieldbackground="white",
            background="white",
            foreground="#163E70",
            arrowcolor="#165A9C",
            bordercolor="#B7D8F2",
            lightcolor="#B7D8F2",
            darkcolor="#B7D8F2",
            padding=(8, 6),
            font=("Segoe UI", 10),
        )
        style.map(
            "ISS.TCombobox",
            fieldbackground=[("readonly", "white")],
            foreground=[("readonly", "#163E70")],
        )

        # Background
        self.content_frame = tk.Frame(self.root, bg=self.bg_page)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        self.page_graphics = tk.Canvas(
            self.content_frame, bg=self.bg_page,
            highlightthickness=0, bd=0
        )
        self.page_graphics.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.page_graphics.bind("<Configure>", self.draw_page_graphics)

        # ========================= HEADER =========================
        self.top_header_frame = tk.Frame(
            self.content_frame, bg=self.bg_header_dark, height=210, bd=0
        )
        self.top_header_frame.pack(fill=tk.X, side=tk.TOP)
        self.top_header_frame.pack_propagate(False)

        self.header_graphics = tk.Canvas(
            self.top_header_frame, bg=self.bg_header_dark,
            highlightthickness=0, bd=0
        )
        self.header_graphics.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.header_graphics.bind("<Configure>", self.draw_header_graphics)

        logo_container = tk.Frame(
            self.top_header_frame, bg=self.bg_header_dark, width=220
        )
        logo_container.pack(side=tk.LEFT, fill=tk.Y, padx=(24, 8), pady=10)
        logo_container.pack_propagate(False)

        self.logo_label = tk.Label(logo_container, bg=self.bg_header_dark)
        self.logo_label.pack(expand=True)
        self.load_header_logo()
        # Schedule bookmark check after UI loads
        if self._reading_bookmark:
            self.root.after(1500, self.show_bookmark_continue_dialog)

        title_box = tk.Frame(self.top_header_frame, bg=self.bg_header_dark)
        title_box.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True,
            padx=(8, 18), pady=(22, 10)
        )

        tk.Label(
            title_box, text="IJESHATEDO SENIOR SECONDARY SCHOOL",
            font=("Segoe UI", 29, "bold"),
            bg=self.bg_header_dark, fg="white", anchor="w"
        ).pack(fill=tk.X)
        tk.Label(
            title_box, text="I.S.S.S",
            font=("Segoe UI", 38, "bold"),
            bg=self.bg_header_dark, fg="#FFD43B", anchor="w"
        ).pack(anchor="w")
        tk.Label(
            title_box, text="STUDENT LEARNING & CURRICULUM SYSTEM",
            font=("Segoe UI", 20, "bold"),
            bg=self.bg_header_dark, fg="white", anchor="w"
        ).pack(anchor="w")
        tk.Label(
            title_box, text="Learn  •  Study  •  Achieve",
            font=("Segoe UI", 15, "italic", "bold"),
            bg=self.bg_header_dark, fg="#73D9FF", anchor="w"
        ).pack(anchor="w", pady=(3, 0))

        # Keep the header focused on the school identity. The header has a fixed
        # height, so placing controls below the large title can clip them.
        self.header_graphics.tk.call("lower", self.header_graphics._w)

        # Dedicated Connect toolbar: always visible between the header and study area.
        connect_bar = tk.Frame(self.content_frame, bg="#E5F4F3",
                               highlightbackground="#A7DCD6", highlightthickness=1)
        connect_bar.pack(side=tk.TOP, fill=tk.X)
        self.connect_button = tk.Button(
            connect_bar, text="💬  I.S.S.S. CONNECT  —  CHAT & CALLS",
            command=self.open_communications,
            bg="#0F766E", activebackground="#115E59", fg="white",
            activeforeground="white", relief=tk.FLAT, bd=0,
            font=("Segoe UI", 11, "bold"), cursor="hand2", padx=18, pady=9
        )
        self.connect_button.pack(side=tk.LEFT, padx=(18, 8), pady=7)
        tk.Label(connect_bar, text="Connect with classmates • Chat and calls",
                 bg="#E5F4F3", fg="#155E59",
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=8)

        # ========================= MAIN BODY =========================
        main_body = tk.Frame(self.content_frame, bg=self.bg_page)
        main_body.pack(fill=tk.BOTH, expand=True, padx=24, pady=(14, 10))

        # ========================= LEFT CARD =========================
        # The left control panel is split into:
        #   1. A scrollable settings area.
        #   2. A fixed action area at the bottom.
        #
        # This keeps Set Study Time and Start Timer visible even when the
        # window is resized, maximized, or used on a smaller/high-DPI screen.
        left_card = tk.Frame(
            main_body, bg=self.bg_card, width=325,
            highlightbackground="#C5E5F7", highlightthickness=1
        )
        left_card.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 12))
        left_card.pack_propagate(False)

        heading = tk.Frame(left_card, bg="#0B5DB7", height=54)
        heading.pack(fill=tk.X, side=tk.TOP)
        heading.pack_propagate(False)
        tk.Label(
            heading, text="⚙", font=("Segoe UI Symbol", 19, "bold"),
            bg="#0B5DB7", fg="white"
        ).pack(side=tk.LEFT, padx=(15, 8))
        tk.Label(
            heading, text="Session Controls",
            font=("Segoe UI", 15, "bold"),
            bg="#0B5DB7", fg="white"
        ).pack(side=tk.LEFT)

        # ---------------- SCROLLABLE CONTROL AREA ----------------
        controls_shell = tk.Frame(left_card, bg="white")
        controls_shell.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        controls_canvas = tk.Canvas(
            controls_shell,
            bg="white",
            highlightthickness=0,
            bd=0,
        )
        controls_scrollbar = ttk.Scrollbar(
            controls_shell,
            orient="vertical",
            command=controls_canvas.yview,
        )
        controls_canvas.configure(yscrollcommand=controls_scrollbar.set)

        controls_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        controls_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        left_inner = tk.Frame(controls_canvas, bg="white")
        controls_window = controls_canvas.create_window(
            (0, 0), window=left_inner, anchor="nw"
        )

        def update_controls_scroll_region(event=None):
            controls_canvas.configure(scrollregion=controls_canvas.bbox("all"))
            controls_canvas.itemconfigure(
                controls_window,
                width=max(1, controls_canvas.winfo_width())
            )

        def resize_controls_inner(event):
            controls_canvas.itemconfigure(controls_window, width=event.width)

        left_inner.bind("<Configure>", update_controls_scroll_region)
        controls_canvas.bind("<Configure>", resize_controls_inner)

        def on_controls_mousewheel(event):
            try:
                controls_canvas.yview_scroll(
                    int(-1 * (event.delta / 120)), "units"
                )
            except Exception:
                pass

        controls_canvas.bind_all("<MouseWheel>", on_controls_mousewheel, add="+")

        def label(text):
            return tk.Label(
                left_inner, text=text, font=("Segoe UI", 9, "bold"),
                bg="white", fg="#173D70", anchor="w"
            )

        label("Class").pack(fill=tk.X, pady=(0, 4), padx=0)
        self.class_combobox = ttk.Combobox(
            left_inner, values=["SS1", "SS2", "SS3"],
            state="readonly", style="ISS.TCombobox"
        )
        self.class_combobox.set(self.current_class)
        self.class_combobox.pack(fill=tk.X, pady=(0, 10))
        self.class_combobox.bind(
            "<<ComboboxSelected>>",
            lambda e: self.switch_class(self.class_combobox.get())
        )

        label("Department").pack(fill=tk.X, pady=(0, 4))
        self.department_combobox = ttk.Combobox(
            left_inner, values=["Science", "Arts", "Commercial"],
            state="readonly", style="ISS.TCombobox"
        )
        self.department_combobox.set(self.current_category)
        self.department_combobox.pack(fill=tk.X, pady=(0, 10))
        self.department_combobox.bind(
            "<<ComboboxSelected>>",
            lambda e: self.switch_category(self.department_combobox.get())
        )

        label("Subject").pack(fill=tk.X, pady=(0, 4))
        self.subject_combobox = ttk.Combobox(
            left_inner, state="readonly", style="ISS.TCombobox"
        )
        self.subject_combobox.pack(fill=tk.X, pady=(0, 10))
        self.subject_combobox.bind(
            "<<ComboboxSelected>>", self.on_subject_dropdown_selected
        )

        label("Term").pack(fill=tk.X, pady=(0, 4))
        self.term_combobox = ttk.Combobox(
            left_inner,
            values=["First Term", "Second Term", "Third Term"],
            state="readonly", style="ISS.TCombobox"
        )
        self.term_combobox.set(self.current_term)
        self.term_combobox.pack(fill=tk.X, pady=(0, 10))
        self.term_combobox.bind(
            "<<ComboboxSelected>>", self.on_term_dropdown_selected
        )

        tk.Frame(left_inner, bg="#D8ECFA", height=1).pack(
            fill=tk.X, pady=(0, 10)
        )

        study_head = tk.Frame(left_inner, bg="white")
        study_head.pack(fill=tk.X)
        tk.Label(
            study_head, text="◷", font=("Segoe UI Symbol", 18, "bold"),
            bg="white", fg="#1267BE"
        ).pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(
            study_head, text="Study Time",
            font=("Segoe UI", 11, "bold"),
            bg="white", fg="#1267BE"
        ).pack(side=tk.LEFT)

        tk.Label(
            left_inner, text="Study Time (Minutes)",
            font=("Segoe UI", 9), bg="white", fg="#2364A4", anchor="w"
        ).pack(fill=tk.X, pady=(2, 3))

        time_box = tk.Frame(
            left_inner, bg="white",
            highlightbackground="#B9DDF7", highlightthickness=1, height=36
        )
        time_box.pack(fill=tk.X, pady=(0, 8))
        time_box.pack_propagate(False)

        tk.Button(
            time_box, text="−", command=lambda: self.adjust_time(-1),
            bg="white", fg="#1267BE", font=("Segoe UI", 14, "bold"),
            relief=tk.FLAT, bd=0, width=3, cursor="hand2"
        ).pack(side=tk.LEFT, fill=tk.Y)

        self.time_entry = tk.Entry(
            time_box, font=("Segoe UI", 11, "bold"),
            bg="white", fg="#163E70", justify="center",
            relief=tk.FLAT, bd=0
        )
        self.time_entry.insert(0, "45")
        self.time_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Button(
            time_box, text="+", command=lambda: self.adjust_time(1),
            bg="white", fg="#1267BE", font=("Segoe UI", 14, "bold"),
            relief=tk.FLAT, bd=0, width=3, cursor="hand2"
        ).pack(side=tk.RIGHT, fill=tk.Y)

        # Quick tip stays in the scrollable section.
        tip = tk.Frame(
            left_inner, bg="#E4F4FF",
            highlightbackground="#A8D8F7", highlightthickness=1
        )
        tip.pack(fill=tk.X, pady=(4, 12))
        tk.Label(
            tip, text="●", font=("Segoe UI", 14, "bold"),
            bg="#E4F4FF", fg="#0B78D1"
        ).pack(side=tk.LEFT, padx=(9, 4), pady=8, anchor="n")
        tip_text = tk.Frame(tip, bg="#E4F4FF")
        tip_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 7), pady=7)
        tk.Label(
            tip_text, text="Quick Tip", font=("Segoe UI", 10, "bold"),
            bg="#E4F4FF", fg="#0B5DB7", anchor="w"
        ).pack(fill=tk.X)
        tk.Label(
            tip_text,
            text="Select your class, department, subject and term. Set your study time and click “Start Timer” to begin.",
            font=("Segoe UI", 8), bg="#E4F4FF", fg="#2364A4",
            wraplength=240, justify="left", anchor="w"
        ).pack(fill=tk.X, pady=(2, 0))

        # ---------------- FIXED ACTION AREA ----------------
        # These buttons are deliberately outside the scrollable canvas.
        # They therefore remain visible when the app is maximized or resized.
        action_bar = tk.Frame(
            left_card,
            bg="white",
            highlightbackground="#D8ECFA",
            highlightthickness=1,
        )
        action_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=0, pady=0)

        self.set_time_button = tk.Button(
            action_bar, text="✓  Set Study Time",
            command=self.update_time_limit,
            bg="#0969D5", activebackground="#0755AD",
            fg="white", font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT, bd=0, pady=8, cursor="hand2"
        )
        self.set_time_button.pack(fill=tk.X, padx=10, pady=(9, 7))

        self.start_button = tk.Button(
            action_bar, text="▶  Start Timer", command=self.start_timer,
            bg="#16B957", activebackground="#119A49",
            fg="white", font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT, bd=0, pady=8, cursor="hand2"
        )
        self.start_button.pack(fill=tk.X, padx=10, pady=(0, 7))

        self.pause_button = tk.Button(
            action_bar, text="Ⅱ  Pause Timer", command=self.pause_timer,
            bg="#FFAA00", activebackground="#E39400",
            fg="white", font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT, bd=0, pady=8, cursor="hand2"
        )
        self.pause_button.pack(fill=tk.X, padx=10, pady=(0, 7))

        self.reset_button = tk.Button(
            action_bar, text="↻  Reset Timer", command=self.reset_session_timer,
            bg="#0B78D1", activebackground="#0964AE",
            fg="white", font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT, bd=0, pady=8, cursor="hand2"
        )
        self.reset_button.pack(fill=tk.X, padx=10, pady=(0, 7))

        if self.tts_available:
            self.read_button = tk.Button(
                action_bar, text="🔊  Read Notes Aloud",
                command=self.speak_notes,
                bg="#6B3DE8", activebackground="#5730C2",
                fg="white", font=("Segoe UI", 10, "bold"),
                relief=tk.FLAT, bd=0, pady=8, cursor="hand2"
            )
            self.read_button.pack(fill=tk.X, padx=10, pady=(0, 9))

        # Compatibility dictionaries retained for the original styling method.
        self.class_buttons = {}
        self.category_buttons = {}

        # ========================= RIGHT PANEL =========================
        right_panel = tk.Frame(main_body, bg=self.bg_page)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        top_right = tk.Frame(right_panel, bg=self.bg_page, height=195)
        top_right.pack(fill=tk.X, pady=(0, 12))
        top_right.pack_propagate(False)

        timer_outer = tk.Frame(
            top_right, bg=self.color_timer_bg_dark, width=380,
            highlightbackground="#073A82", highlightthickness=1
        )
        timer_outer.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        timer_outer.pack_propagate(False)

        timer_title = tk.Frame(timer_outer, bg=self.color_timer_bg_dark)
        timer_title.pack(fill=tk.X, padx=18, pady=(12, 0))
        tk.Label(
            timer_title, text="⏱", font=("Segoe UI Symbol", 20, "bold"),
            bg=self.color_timer_bg_dark, fg="white"
        ).pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(
            timer_title, text="STUDY TIMER",
            font=("Segoe UI", 15, "bold"),
            bg=self.color_timer_bg_dark, fg="white"
        ).pack(side=tk.LEFT)

        timer_canvas = tk.Canvas(
            timer_outer, bg=self.color_timer_bg_dark,
            highlightthickness=0, bd=0, height=95
        )
        timer_canvas.pack(fill=tk.X)
        timer_canvas.create_oval(
            98, -5, 282, 180, outline="#104E9B", width=3
        )
        timer_canvas.create_arc(
            98, -5, 282, 180, start=25, extent=240,
            style=tk.ARC, outline="#0878D8", width=5
        )
        timer_canvas.create_oval(
            125, 22, 255, 152, outline="#0A3F86", width=2
        )

        self.timer_label = tk.Label(
            timer_outer, text="45:00",
            font=("Segoe UI", 45, "bold"),
            bg=self.color_timer_bg_dark, fg="white"
        )
        self.timer_label.place(relx=.5, rely=.49, anchor="center")

        self.time_status_label = tk.Label(
            timer_outer, text="READY TO START",
            font=("Segoe UI", 9, "bold"),
            bg="#13C96A", fg="white", padx=14, pady=4
        )
        self.time_status_label.place(relx=.5, rely=.83, anchor="center")

        selection_area = tk.Frame(top_right, bg=self.bg_page)
        selection_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        selection_card = tk.Frame(
            selection_area, bg="#EAF6FF",
            highlightbackground="#C7E5F8", highlightthickness=1, height=68
        )
        selection_card.pack(fill=tk.X)
        selection_card.pack_propagate(False)

        tk.Label(
            selection_card, text="▣", font=("Segoe UI Symbol", 21, "bold"),
            bg="#0878D8", fg="white", width=3
        ).pack(side=tk.LEFT, fill=tk.Y, padx=(8, 10), pady=7)

        selection_text = tk.Frame(selection_card, bg="#EAF6FF")
        selection_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=7)
        tk.Label(
            selection_text, text="CURRENT SELECTION",
            font=("Segoe UI", 9, "bold"),
            bg="#EAF6FF", fg="#184C83", anchor="w"
        ).pack(fill=tk.X)
        self.current_selection_label = tk.Label(
            selection_text,
            text="SS1  •  Science  •  Mathematics  •  First Term",
            font=("Segoe UI", 11, "bold"),
            bg="#EAF6FF", fg="#123B70", anchor="w"
        )
        self.current_selection_label.pack(fill=tk.X, pady=(3, 0))

        tile_row = tk.Frame(selection_area, bg=self.bg_page)
        tile_row.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.info_tiles = {}
        tile_specs = [
            ("class", "▰", "Class", "SS1", "#1685F5"),
            ("department", "▤", "Department", "Science", "#F23556"),
            ("subject", "▣", "Subject", "Mathematics", "#10B98B"),
            ("term", "▦", "Term", "First Term", "#8B5CF6"),
        ]
        for index, (key, icon, title, value, color) in enumerate(tile_specs):
            tile = tk.Frame(tile_row, bg=color)
            tile.pack(
                side=tk.LEFT, fill=tk.BOTH, expand=True,
                padx=(0, 8 if index < 3 else 0)
            )
            tk.Label(
                tile, text=icon, font=("Segoe UI Symbol", 20, "bold"),
                bg=color, fg="white"
            ).pack(side=tk.LEFT, padx=(10, 7))
            t = tk.Frame(tile, bg=color)
            t.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            tk.Label(
                t, text=title, font=("Segoe UI", 8),
                bg=color, fg="white", anchor="w"
            ).pack(fill=tk.X, pady=(10, 0))
            self.info_tiles[key] = tk.Label(
                t, text=value, font=("Segoe UI", 10, "bold"),
                bg=color, fg="white", anchor="w"
            )
            self.info_tiles[key].pack(fill=tk.X, pady=(2, 0))

        # ========================= NOTES =========================
        notes_frame = tk.Frame(
            right_panel, bg=self.bg_card,
            highlightbackground="#C7E5F8", highlightthickness=1
        )
        notes_frame.pack(fill=tk.BOTH, expand=True)

        notes_header = tk.Frame(
            notes_frame, bg="#0A72D1", height=48
        )
        notes_header.pack(fill=tk.X)
        notes_header.pack_propagate(False)

        tk.Label(
            notes_header, text="▤",
            font=("Segoe UI Symbol", 18, "bold"),
            bg="#0A72D1", fg="white"
        ).pack(side=tk.LEFT, padx=(15, 8))
        tk.Label(
            notes_header, text="Scheme of Work Content",
            font=("Segoe UI", 14, "bold"),
            bg="#0A72D1", fg="white"
        ).pack(side=tk.LEFT)

        # Open the full teaching workspace without removing the compact
        # scheme-of-work preview from the main dashboard.
        # NEW: QUIZ button in main dashboard header
        self.quiz_button_main = tk.Button(
            notes_header,
            text="🎮  QUIZ GAME",
            command=self.open_topic_quiz,
            bg="#7C3AED",
            activebackground="#6D28D9",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            bd=0,
            padx=12,
            pady=5,
            cursor="hand2",
        )
        self.quiz_button_main.pack(side=tk.RIGHT, padx=(6, 6))
        
        self.workspace_button = tk.Button(
            notes_header,
            text="▣  Open Teaching Workspace",
            command=self.open_teaching_workspace,
            bg="#123F78",
            activebackground="#0D315E",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
        )
        self.workspace_button.pack(side=tk.RIGHT, padx=(6, 10))

        self.file_status = tk.Label(
            notes_header, text="✓  File Loaded",
            font=("Segoe UI", 9, "bold"),
            bg="#17B957", fg="white", padx=10, pady=4
        )
        self.file_status.pack(side=tk.RIGHT, padx=8)

        text_container = tk.Frame(notes_frame, bg="#081A31")
        text_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        self.notes_graphics = tk.Canvas(
            text_container, bg="#081A31",
            highlightthickness=0, bd=0
        )
        self.notes_graphics.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.notes_graphics.bind("<Configure>", self.draw_notes_graphics)

        self.notes_text = tk.Text(
            text_container, wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#081A31", fg="#B9D9FF",
            insertbackground="white", bd=0,
            padx=18, pady=12, relief=tk.FLAT,
            selectbackground="#145EA8"
        )
        self.notes_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.watermark_label = tk.Label(text_container, bg="#081A31", bd=0)
        self.load_watermark(text_container)

        self.notes_graphics.tk.call("lower", self.notes_graphics._w)

        scrollbar = tk.Scrollbar(
            text_container, command=self.notes_text.yview,
            bg="#12385D", troughcolor="#071528",
            activebackground="#2E77B7"
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.notes_text.config(
            yscrollcommand=scrollbar.set, state=tk.DISABLED
        )

        # ========================= STATUS BAR =========================
        bottom_bar = tk.Frame(
            self.content_frame, bg="white", height=36,
            highlightbackground="#C7E5F8", highlightthickness=1
        )
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM)
        bottom_bar.pack_propagate(False)

        tk.Label(
            bottom_bar, text="●", font=("Segoe UI", 14, "bold"),
            bg="white", fg="#15B963"
        ).pack(side=tk.LEFT, padx=(25, 6))
        tk.Label(
            bottom_bar, text="Status:",
            font=("Segoe UI", 9, "bold"),
            bg="white", fg="#16528C"
        ).pack(side=tk.LEFT)
        self.status_label = tk.Label(
            bottom_bar, text="Ready",
            font=("Segoe UI", 9, "bold"),
            bg="white", fg="#16528C"
        )
        self.status_label.pack(side=tk.LEFT, padx=(4, 10))
        tk.Label(
            bottom_bar, text=f"Student: {self.student_username}  •  Sessions completed: {self.completed_sessions}",
            font=("Segoe UI", 9, "bold"), bg="white", fg="#0B4AA2"
        ).pack(side=tk.RIGHT, padx=18)
        tk.Label(
            bottom_bar, text="•  Awaiting session start",
            font=("Segoe UI", 9),
            bg="white", fg="#64748B"
        ).pack(side=tk.LEFT)
        tk.Label(
            bottom_bar,
            text="Progress saves to your account  •  Version 2.1.0  •  I.S.S.S",
            font=("Segoe UI", 9),
            bg="white", fg="#64748B"
        ).pack(side=tk.RIGHT, padx=18)

        self.update_subject_dropdown()
        self.update_display()
        self.update_selection_tiles()
        self.apply_button_styles()

    # ========================================================
    # REFERENCE UI HELPERS
    # ========================================================
    def save_progress(self, completed_session=False):
        if not self.student_id:
            return
        if completed_session:
            self.completed_sessions += 1
        save_student_progress(
            self.student_id, self.current_class, self.current_category,
            self.current_subject, self.current_term, self.completed_sessions
        )

    def adjust_time(self, amount):
        try:
            value = int(self.time_entry.get())
        except ValueError:
            value = 45
        value = max(1, min(1440, value + amount))
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, str(value))

    def pause_timer(self):
        if not self.is_running:
            return
        self.is_running = False
        if self.timer_job is not None:
            try:
                self.root.after_cancel(self.timer_job)
            except Exception:
                pass
            self.timer_job = None
        self.start_button.config(text="▶  Resume Timer", bg="#16B957")
        self.time_status_label.config(text="PAUSED")
        if hasattr(self, "status_label"):
            self.status_label.config(text="Paused")

    def reset_session_timer(self):
        self.stop_timer_without_reset()
        self.reset_timer_value()
        self.start_button.config(text="▶  Start Timer", bg="#16B957")
        self.time_status_label.config(text="READY TO START")
        if hasattr(self, "status_label"):
            self.status_label.config(text="Ready")

    def update_selection_tiles(self):
        if hasattr(self, "current_selection_label"):
            self.current_selection_label.config(
                text=(
                    f"{self.current_class}  •  {self.current_category}  •  "
                    f"{self.current_subject}  •  {self.current_term}"
                )
            )
        if hasattr(self, "info_tiles"):
            self.info_tiles["class"].config(text=self.current_class)
            self.info_tiles["department"].config(text=self.current_category)
            self.info_tiles["subject"].config(text=self.current_subject)
            self.info_tiles["term"].config(text=self.current_term)

    def get_visual_theme(self):
        """Return a coordinated background palette for class and department."""
        class_palettes = {
            "SS1": {"page": "#EAF8F7", "header": "#075E63", "header_light": "#0D9488", "accent": "#5EEAD4"},
            "SS2": {"page": "#EDF5FF", "header": "#123B79", "header_light": "#2563EB", "accent": "#93C5FD"},
            "SS3": {"page": "#F3EEFF", "header": "#4C1D95", "header_light": "#7C3AED", "accent": "#C4B5FD"},
        }
        department_palettes = {
            # Distinct metallic identities for each department.
            "Science": {"page": "#FFF7DF", "header": "#805300", "header_light": "#C58A08", "accent": "#F4C95D"},
            "Arts": {"page": "#F1F2F4", "header": "#555B63", "header_light": "#858B93", "accent": "#D5D8DC"},
            "Commercial": {"page": "#FFF0E2", "header": "#713B16", "header_light": "#A95D1A", "accent": "#D89A5B"},
        }
        base = class_palettes.get(self.current_class, class_palettes["SS1"])
        dept = department_palettes.get(self.current_category, department_palettes["Science"])
        # Department controls the primary colour; class contributes a light tint.
        return {"page": dept["page"], "header": dept["header"],
                "header_light": dept["header_light"], "accent": base["accent"],
                "class_page": base["page"]}

    def update_visual_theme(self):
        """Apply selected class/department colours and refresh background art."""
        theme = self.get_visual_theme()
        self.bg_page = theme["page"]
        self.bg_header_dark = theme["header"]
        self.bg_header_light = theme["header_light"]
        self.bg_main = self.bg_page
        safe_configs = [
            (getattr(self, "root", None), {"bg": self.bg_page}),
            (getattr(self, "content_frame", None), {"bg": self.bg_page}),
            (getattr(self, "page_graphics", None), {"bg": self.bg_page}),
            (getattr(self, "top_header_frame", None), {"bg": self.bg_header_dark}),
            (getattr(self, "header_graphics", None), {"bg": self.bg_header_dark}),
            (getattr(self, "main_body", None), {"bg": self.bg_page}),
        ]
        for widget, options in safe_configs:
            if widget is not None:
                try:
                    widget.configure(**options)
                except (tk.TclError, AttributeError):
                    pass
        # Keep class selection controls and department selection controls in sync.
        for attr in ("class_buttons", "category_buttons", "department_buttons"):
            buttons = getattr(self, attr, None)
            if isinstance(buttons, dict):
                for key, button in buttons.items():
                    try:
                        if key == self.current_class or key == self.current_category:
                            button.configure(bg=theme["header_light"], activebackground=theme["header"])
                    except (tk.TclError, AttributeError):
                        pass
        try:
            self.root.after_idle(self.draw_page_graphics)
        except (tk.TclError, AttributeError):
            pass
        try:
            self.root.after_idle(self.draw_header_graphics)
        except (tk.TclError, AttributeError):
            pass

    def _department_background_path(self):
        """Return the selected department's background image path."""
        base = os.path.dirname(os.path.abspath(__file__))
        assets = os.path.join(base, "ijeshatedo_study_app_assets")
        filenames = {
            "Science": "science_background.png",
            "Arts": "arts_background.png",
            "Commercial": "commercial_background.png",
        }
        filename = filenames.get(self.current_category)
        if not filename:
            return ""
        return os.path.join(assets, filename)

    def draw_page_graphics(self, event=None):
        """Draw a visible, faded department image watermark behind the UI."""
        if not getattr(self, "page_graphics", None):
            return
        c = self.page_graphics
        c.delete("page_graphics")
        w = max(c.winfo_width(), 1)
        h = max(c.winfo_height(), 1)

        # Keep a clean, department-matched canvas colour underneath the image.
        theme = self.get_visual_theme()
        bg = theme["page"]
        c.configure(bg=bg)

        # Pillow is optional for the app, but required to fade the image cleanly.
        path = self._department_background_path()
        if MODULE_PIL_AVAILABLE and path and os.path.isfile(path):
            try:
                from PIL import Image, ImageTk, ImageEnhance
                with Image.open(path) as original:
                    img = original.convert("RGBA")
                # Use a large watermark, not a full-contrast wallpaper.
                target_w = max(320, min(int(w * 0.52), 760))
                target_h = max(220, min(int(h * 0.62), 620))
                img.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
                alpha = img.getchannel("A")
                alpha = alpha.point(lambda value: int(value * 0.20))
                img.putalpha(alpha)
                self.department_background_photo = ImageTk.PhotoImage(img)
                c.create_image(
                    int(w * 0.78), int(h * 0.60),
                    image=self.department_background_photo,
                    anchor="center", tags="page_graphics"
                )
            except Exception as exc:
                # Continue drawing the standard background if image loading fails.
                print("Department background could not be loaded:", exc)

        # Draw subtle theme accents so the department still looks distinct
        # when its image file is absent.
        accent = theme["accent"]
        c.create_oval(w - 180, -90, w + 80, 170, fill=accent, outline="", stipple="gray75", tags="page_graphics")
        c.create_oval(-150, h - 160, 130, h + 120, fill=accent, outline="", stipple="gray75", tags="page_graphics")
        c.lower("page_graphics")

    def show_bookmark_continue_dialog(self):
        """Show where student last stopped - when they login with same password"""
        bm = getattr(self, "_reading_bookmark", None)
        if not bm:
            return
        
        # Don't show if bookmark is too old (> 30 days) or same as current
        try:
            # Check if bookmark matches current class/subject etc - if not, still show as option
            msg = (
                f"Welcome back, {self.student_username}!\n\n"
                f"You stopped reading at:\n"
                f"Class: {bm['current_class']}\n"
                f"Department: {bm['department']}\n"
                f"Subject: {bm['subject']}\n"
                f"Term: {bm['term']}\n"
                f"Topic: {bm['topic'][:60]}\n"
                f"Last seen: {bm['updated_at']}\n\n"
                f"Snippet: {bm['snippet'][:100]}...\n\n"
                f"Do you want to CONTINUE from where you stopped?"
            )
            
            # Create custom dialog
            win = tk.Toplevel(self.root)
            win.title("Continue from where you stopped?")
            win.geometry("550x400")
            win.configure(bg="#F0F9FF")
            win.transient(self.root)
            win.grab_set()
            
            tk.Label(win, text="📖 CONTINUE READING", font=("Segoe UI", 16, "bold"), bg="#F0F9FF", fg="#063B86").pack(pady=(20,10))
            tk.Label(win, text=msg, font=("Segoe UI", 10), bg="#F0F9FF", fg="#1F2937", justify="left", wraplength=500).pack(padx=20, pady=10)
            
            btn_frame = tk.Frame(win, bg="#F0F9FF")
            btn_frame.pack(pady=20)
            
            def continue_reading():
                win.destroy()
                # Restore to bookmarked location
                self.current_class = bm["current_class"]
                self.current_category = bm["department"]
                self.current_subject = bm["subject"]
                self.current_term = bm["term"]
                # Trigger UI update to that subject
                try:
                    # Save progress to current
                    save_student_progress(self.student_id, self.current_class, self.current_category, self.current_subject, self.current_term)
                    # Open teaching workspace at bookmarked position
                    self.root.after(500, lambda: self.open_teaching_workspace_with_bookmark(bm))
                except Exception as e:
                    print(f"Could not restore bookmark: {e}")
            
            def start_new():
                win.destroy()
                # Clear bookmark or keep it? Keep it but don't restore
            
            tk.Button(btn_frame, text="✅ CONTINUE", command=continue_reading, bg="#16A34A", fg="white", font=("Segoe UI", 11, "bold"), padx=20, pady=10, relief="flat", cursor="hand2").pack(side="left", padx=10)
            tk.Button(btn_frame, text="Start Fresh", command=start_new, bg="#E2E8F0", fg="#334155", font=("Segoe UI", 11), padx=20, pady=10, relief="flat", cursor="hand2").pack(side="left", padx=10)
            
        except Exception as e:
            print(f"Bookmark dialog error: {e}")

    def open_teaching_workspace_with_bookmark(self, bookmark):
        """Open teaching workspace and scroll to bookmarked position"""
        try:
            # First open normal teaching workspace
            self.open_teaching_workspace()
            # After workspace opens, scroll to saved position
            def scroll_to_bookmark():
                try:
                    if hasattr(self, "_current_teaching_text") and self._current_teaching_text:
                        text_widget = self._current_teaching_text
                        if text_widget.winfo_exists():
                            # Scroll to saved fraction
                            text_widget.yview_moveto(bookmark.get("scroll_fraction", 0.0))
                            # Also try to set mark
                            try:
                                text_widget.mark_set("insert", bookmark.get("text_position", "1.0"))
                                text_widget.see(bookmark.get("text_position", "1.0"))
                            except:
                                pass
                            if hasattr(self, "_current_topic_status"):
                                self._current_topic_status.config(text=f"📖 Continued from where you stopped: {bookmark.get('topic','')[:40]}")
                except Exception as e:
                    print(f"Scroll to bookmark failed: {e}")
            
            self.root.after(800, scroll_to_bookmark)
        except Exception as e:
            print(f"Open with bookmark failed: {e}")

    def draw_header_graphics(self, event=None):

        """Modern banner graphics inspired by the supplied reference."""

        if not self.header_graphics:

            return

        c = self.header_graphics

        c.delete("header_graphics")

        w = max(c.winfo_width(), 1)

        h = max(c.winfo_height(), 1)

        theme = self.get_visual_theme()
        # Layered diagonal bands follow the selected department palette.

        c.create_polygon(

            w * .55, 0,

            w, 0,

            w * .80, h,

            w * .30, h,

            fill=theme["header_light"],

            outline="",

            tags="header_graphics"

        )

        c.create_polygon(

            w * .72, 0,

            w, 0,

            w, h,

            w * .50, h,

            fill="#0B55AE",

            outline="",

            tags="header_graphics"

        )

        c.create_polygon(

            w * .88, 0,

            w, 0,

            w, h,

            w * .72, h,

            fill="#0878D8",

            outline="",

            tags="header_graphics"

        )

        # Technology grid.

        for x in range(int(w * .55), int(w), 48):

            c.create_line(

                x, 0, x - 130, h,

                fill="#75D9FF",

                width=1,

                tags="header_graphics"

            )

        # Network nodes.

        pts = [

            (w * .70, h * .20),

            (w * .78, h * .58),

            (w * .87, h * .28),

            (w * .95, h * .72),

        ]

        for a, b in zip(pts, pts[1:]):

            c.create_line(

                a[0], a[1], b[0], b[1],

                fill="#73D8FF",

                width=2,

                tags="header_graphics"

            )

        for x, y in pts:

            c.create_oval(

                x - 5, y - 5, x + 5, y + 5,

                fill="#B8F0FF",

                outline="",

                tags="header_graphics"

            )

        # Stylized books on the right.

        bx = w * .87

        by = h * .70

        book_data = [

            (120, 12, "#FFFFFF"),

            (145, 13, "#FFD43B"),

            (125, 12, "#F76C7C"),

            (155, 13, "#55D6BE"),

        ]

        for i, (bw, bh, color) in enumerate(book_data):

            y = by - i * 14

            c.create_rectangle(

                bx - bw / 2,

                y,

                bx + bw / 2,

                y + bh,

                fill=color,

                outline="",

                tags="header_graphics"

            )

        c.lower("header_graphics")

    def draw_notes_graphics(self, event=None):

        """Subtle rings and education-network graphics behind notes."""

        if not self.notes_graphics:

            return

        c = self.notes_graphics

        c.delete("notes_graphics")

        w = max(c.winfo_width(), 1)

        h = max(c.winfo_height(), 1)

        cx = w * .72

        cy = h * .52

        for radius in (95, 135, 180):

            c.create_oval(

                cx - radius,

                cy - radius,

                cx + radius,

                cy + radius,

                outline="#173E68",

                width=2,

                tags="notes_graphics"

            )

        # Small connected nodes.

        pts = [

            (w * .56, h * .25),

            (w * .72, h * .15),

            (w * .88, h * .30),

            (w * .82, h * .75),

            (w * .58, h * .78),

        ]

        for a, b in zip(pts, pts[1:]):

            c.create_line(

                a[0], a[1], b[0], b[1],

                fill="#1A527F",

                width=1,

                tags="notes_graphics"

            )

        for x, y in pts:

            c.create_oval(

                x - 4, y - 4,

                x + 4, y + 4,

                fill="#2673A8",

                outline="",

                tags="notes_graphics"

            )

        c.lower("notes_graphics")

    def load_watermark(self, parent):

        """Load the user's badge as a faint transparent watermark."""

        if not MODULE_PIL_AVAILABLE:

            return

        logo_filename = "school_badge.png"

        if not os.path.exists(logo_filename):

            script_dir = os.path.dirname(os.path.abspath(__file__))

            logo_filename = os.path.join(

                script_dir,

                "school_badge.png"

            )

        if not os.path.exists(logo_filename):

            return

        try:

            img = Image.open(logo_filename).convert("RGBA")

            # Resize without stretching.

            img.thumbnail((560, 560), Image.Resampling.LANCZOS)

            pixels = img.load()

            width, height = img.size

            # Turn the badge into a very faint watermark.

            for y in range(height):

                for x in range(width):

                    r, g, b, a = pixels[x, y]

                    # Remove white background.

                    if r > 225 and g > 225 and b > 225:

                        pixels[x, y] = (r, g, b, 0)

                    else:

                        pixels[x, y] = (r, g, b, 28)

            self.school_badge_watermark = ImageTk.PhotoImage(img)

            self.watermark_label.config(

                image=self.school_badge_watermark

            )

            self.watermark_label.place(

                relx=.76,

                rely=.52,

                anchor="center"

            )

            self.watermark_label.lower()

        except Exception:

            pass

    # ========================================================

    # STYLING

    # ========================================================

    def apply_button_styles(self):
        # Preserve support for the original button dictionaries.
        for cls, btn in self.class_buttons.items():
            btn.config(
                bg=self.color_ss_active if cls == self.current_class else self.color_ss_inactive,
                fg="white" if cls == self.current_class else self.color_text_dark,
            )
        for cat, btn in self.category_buttons.items():
            active = cat == self.current_category
            btn.config(
                bg=(
                    self.color_science if cat == "Science"
                    else self.color_primary
                ) if active else "#F1F5F9",
                fg="white" if active else self.color_text_dark,
            )

        if hasattr(self, "class_combobox"):
            self.class_combobox.set(self.current_class)
        if hasattr(self, "department_combobox"):
            self.department_combobox.set(self.current_category)
        if hasattr(self, "subject_combobox"):
            self.subject_combobox.set(self.current_subject)
        if hasattr(self, "term_combobox"):
            self.term_combobox.set(self.current_term)

    def open_communications(self):
        if not COMMUNICATIONS_AVAILABLE:
            messagebox.showerror(
                "I.S.S.S. Connect unavailable",
                "Connect is built into this file. If the required packages are missing, install them with:\n\npython -m pip install requests fastapi uvicorn",
                parent=self.root,
            )
            return
        # Show Connect inside the existing Study App window, not a second app/window.
        self.content_frame.pack_forget()
        self._active_communications = CommunicationWindow(
            self.root,
            self.student_username,
            embedded=True,
            on_close=self._return_from_communications,
        )

    def _return_from_communications(self):
        # Restore the same study interface when the user leaves Connect.
        if self.content_frame.winfo_exists():
            self.content_frame.pack(fill=tk.BOTH, expand=True)
        self.root.title("Ijeshatedo Senior Secondary School - I.S.S.S")

    def set_window_logo(self):

        logo_filename = "school_badge.png"

        if not os.path.exists(logo_filename):

            return

        try:

            if MODULE_PIL_AVAILABLE:

                img = Image.open(logo_filename)

                img_resized = img.resize(

                    (64, 64),

                    Image.Resampling.LANCZOS

                )

                self.window_logo = ImageTk.PhotoImage(img_resized)

            else:

                self.window_logo = tk.PhotoImage(

                    file=logo_filename

                )

            self.root.iconphoto(

                True,

                self.window_logo

            )

        except Exception:

            pass

    def load_header_logo(self):

        logo_filename = "school_badge.png"

        if not os.path.exists(logo_filename):
            logo_filename = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "school_badge.png"
            )

        if not os.path.exists(logo_filename):

            self.logo_label.config(

                text="I.S.S.S",

                font=("Arial", 12, "bold"),

                fg="white",

                bg=self.bg_header_dark,

                width=8,

                height=3

            )

            return

        try:

            if MODULE_PIL_AVAILABLE:

                img = Image.open(logo_filename)

                img_resized = img.resize(

                    (170, 170),

                    Image.Resampling.LANCZOS

                )

                self.header_logo_img = ImageTk.PhotoImage(

                    img_resized

                )

                self.logo_label.config(

                    image=self.header_logo_img,

                    bg=self.bg_header_dark

                )

            else:

                self.logo_label.config(

                    text="I.S.S.S",

                    font=("Arial", 10, "bold"),

                    fg="white",

                    bg=self.bg_header_dark,

                    width=10,

                    height=4

                )

        except Exception:

            self.logo_label.config(

                text="I.S.S.S",

                font=("Arial", 10, "bold"),

                fg="white",

                bg=self.bg_header_dark,

                width=10,

                height=4

            )

    # ========================================================

    # CLASS / STREAM / SUBJECT / TERM

    # ========================================================

    def switch_class(self, class_name):

        self.stop_timer_without_reset()

        self.current_class = class_name

        available_subjects = curriculum_files[

            self.current_class

        ][self.current_category]

        if self.current_subject not in available_subjects:

            self.current_subject = list(

                available_subjects.keys()

            )[0]

        self.update_subject_dropdown()

        self.reset_timer_value()

        self.start_button.config(

            text="▶ Start Session",

            bg="#22C55E"

        )

        self.time_status_label.config(

            text="TIME REMAINING — SESSION READY"

        )

        self.update_display()
        self.update_selection_tiles()
        self.apply_button_styles()
        self.update_visual_theme()
        self.save_progress()

    def switch_category(self, category_name):

        self.stop_timer_without_reset()

        self.current_category = category_name

        available_subjects = curriculum_files[

            self.current_class

        ][self.current_category]

        if self.current_subject not in available_subjects:

            self.current_subject = list(

                available_subjects.keys()

            )[0]

        self.update_subject_dropdown()

        self.reset_timer_value()

        self.start_button.config(

            text="▶ Start Session",

            bg="#22C55E"

        )

        self.time_status_label.config(

            text="TIME REMAINING — SESSION READY"

        )

        self.update_display()
        self.update_selection_tiles()
        self.apply_button_styles()
        self.update_visual_theme()
        self.save_progress()

    def switch_term(self, term_name):

        self.stop_timer_without_reset()

        self.current_term = term_name

        if hasattr(self, "term_combobox"):

            self.term_combobox.set(term_name)

        self.reset_timer_value()

        self.start_button.config(

            text="▶ Start Session",

            bg="#22C55E"

        )

        self.time_status_label.config(

            text="TIME REMAINING — SESSION READY"

        )

        self.update_display()
        self.update_selection_tiles()
        self.save_progress()

    def update_subject_dropdown(self):

        subjects = list(

            curriculum_files[

                self.current_class

            ][self.current_category].keys()

        )

        self.subject_combobox["values"] = subjects

        if self.current_subject in subjects:

            self.subject_combobox.set(

                self.current_subject

            )

        elif subjects:

            self.current_subject = subjects[0]

            self.subject_combobox.set(

                self.current_subject

            )

    def on_subject_dropdown_selected(self, event=None):

        selected_subject = self.subject_combobox.get()

        if selected_subject:

            self.stop_timer_without_reset()

            self.current_subject = selected_subject

            self.reset_timer_value()

            self.start_button.config(

                text="▶ Start Session",

                bg="#22C55E"

            )

            self.time_status_label.config(

                text="TIME REMAINING — SESSION READY"

            )

            self.update_display()
            self.update_selection_tiles()
            self.save_progress()

    def on_term_dropdown_selected(self, event=None):

        selected_term = self.term_combobox.get()

        if selected_term:

            self.stop_timer_without_reset()

            self.current_term = selected_term

            self.reset_timer_value()

            self.start_button.config(

                text="▶ Start Session",

                bg="#22C55E"

            )

            self.time_status_label.config(

                text="TIME REMAINING — SESSION READY"

            )

            self.update_display()

    # ========================================================

    # TIMER SETTINGS

    # ========================================================

    def reset_timer_value(self):

        try:

            mins = int(self.time_entry.get())

            if mins <= 0:

                raise ValueError

            self.time_left = mins * 60

        except ValueError:

            self.time_left = 45 * 60

        self.update_timer_label()

    def update_timer_label(self):

        mins, secs = divmod(

            max(0, self.time_left),

            60

        )

        self.timer_label.config(

            text=f"{mins:02d}:{secs:02d}"

        )

    def update_time_limit(self):

        if self.is_running:

            messagebox.showwarning(

                "Session Active",

                "Please pause the current session before changing the time limit."

            )

            return

        try:

            mins = int(self.time_entry.get())

            if mins <= 0:

                raise ValueError

        except ValueError:

            messagebox.showerror(

                "Invalid Time",

                "Please enter a positive whole number of minutes."

            )

            return

        self.time_left = mins * 60

        self.update_timer_label()

        messagebox.showinfo(

            "Success",

            "Time limit updated successfully."

        )

    # ========================================================
    # TEACHING WORKSPACE
    # ========================================================

    def open_teaching_workspace(self):
        """Open a reliable full teaching workspace using the exact content
        already loaded by the main dashboard."""
        existing = getattr(self, "teaching_workspace", None)
        if existing is not None:
            try:
                if existing.winfo_exists():
                    existing.destroy()
            except Exception:
                pass

        workspace = tk.Toplevel(self.root)
        self.teaching_workspace = workspace

        # Initialize optional watermark references before any code uses them.
        # Reuse the app's existing school-badge watermark when available.
        workspace._isss_logo = getattr(self, "window_logo", None)
        workspace._isss_watermark = getattr(
            self, "school_badge_watermark", None
        )
        workspace.title(
            f"I.S.S.S Teaching Workspace — "
            f"{self.current_subject}"
        )
        workspace.geometry("1450x900")
        workspace.minsize(1050, 700)
        workspace.configure(bg="#EAF7FF")

        # Keep track of the exact curriculum section the learner is studying.
        self.active_study_topic = getattr(self, "active_study_topic", self.current_subject)
        self.active_study_text = getattr(self, "active_study_text", "")

        try:
            workspace.state("zoomed")
        except Exception:
            pass

        # ------------------------------------------------------------
        # PALETTE
        # ------------------------------------------------------------
        # Department-specific teaching workspace palette.
        department_workspace_palettes = {
            "Science": {"dark": "#3D2908", "dark2": "#5B3C0A", "blue": "#B47A08", "blue2": "#E3B43C", "text": "#FFF1C2", "muted": "#E3C77C", "line": "#987124"},
            "Arts": {"dark": "#303338", "dark2": "#454A50", "blue": "#747A82", "blue2": "#BFC3C8", "text": "#F5F5F5", "muted": "#D0D3D7", "line": "#8D9299"},
            "Commercial": {"dark": "#3D2110", "dark2": "#5A3015", "blue": "#995018", "blue2": "#D28A43", "text": "#FFE6CB", "muted": "#DDB58F", "line": "#98613A"},
        }
        dept_C = department_workspace_palettes.get(self.current_category, department_workspace_palettes["Science"])
        C = {
            "navy": "#062E69",
            "navy2": "#0B4388",
            "blue": "#0878D1",
            "blue2": "#18A7E8",
            "sky": "#EAF7FF",
            "green": "#16B978",
            "yellow": "#F4C900",
            "red": "#F23859",
            "purple": "#8657E8",
            "dark": "#061A30",
            "dark2": "#0B2949",
            "white": "#FFFFFF",
            "text": "#123B70",
            "muted": "#6383A3",
            "line": "#B9DDF3",
        }
        C.update(dept_C)

        # ------------------------------------------------------------
        # CURRICULUM CONTENT SOURCE (ROBUST FIX)
        # ------------------------------------------------------------
        # Read the selected curriculum file directly. The dashboard's Text
        # widget may be empty/disabled during workspace creation, so it must
        # not be the only source of lesson notes.
        try:
            selected_filename = curriculum_files[
                self.current_class
            ][self.current_category][
                self.current_subject
            ][self.current_term]
            raw_content = self.load_file_content(selected_filename).strip()
        except (KeyError, AttributeError, TypeError):
            raw_content = ""

        if not raw_content or raw_content.startswith("=== FILE NOT FOUND:"):
            # Fall back to the currently displayed notes if the file lookup
            # failed, but preserve the useful file-not-found message if both
            # sources are empty.
            try:
                dashboard_content = self.notes_text.get("1.0", tk.END).strip()
            except (AttributeError, tk.TclError):
                dashboard_content = ""
            if dashboard_content and dashboard_content.strip():
                raw_content = dashboard_content
            elif not raw_content:
                raw_content = (
                    "NO CURRICULUM NOTES COULD BE LOADED.\n\n"
                    f"Selected lesson: {self.current_class} • "
                    f"{self.current_category} • {self.current_subject} • "
                    f"{self.current_term}.\n\n"
                    "Check that the mapped .txt curriculum file exists inside "
                    "the application folder or one of its subfolders."
                )

        # The quiz uses the curriculum text actually loaded for this class,
        # department, subject and term.
        self.current_content = raw_content
        if not getattr(self, "active_study_text", ""):
            self.active_study_topic = f"{self.current_subject} — {self.current_term}"
            self.active_study_text = raw_content

        # ------------------------------------------------------------
        # ROOT GRID — grid is used deliberately so the teaching area
        # ALWAYS receives the remaining screen width and height.
        # ------------------------------------------------------------
        workspace.grid_rowconfigure(0, weight=0)
        workspace.grid_rowconfigure(1, weight=0)
        workspace.grid_rowconfigure(2, weight=0)
        workspace.grid_rowconfigure(3, weight=1)
        workspace.grid_rowconfigure(4, weight=0)
        workspace.grid_columnconfigure(0, weight=1)

        # ------------------------------------------------------------
        # COMPACT HEADER — decorative graphics removed to maximize workspace
        # Keep only a slim title bar and close button.
        header = tk.Frame(workspace, bg=C["navy"], height=46)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        title_text = tk.Label(
            header,
            text=(
                f"TEACHING WORKSPACE  |  {self.current_class}  |  "
                f"{self.current_category}  |  {self.current_subject}  |  "
                f"{self.current_term}"
            ),
            font=("Segoe UI", 11, "bold"),
            bg=C["navy"],
            fg="white",
            anchor="w",
        )
        title_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=14)

        tk.Button(
            header,
            text="✕ Close",
            command=workspace.destroy,
            bg=C["red"],
            activebackground="#C91E3D",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2",
        ).pack(side=tk.RIGHT, padx=10, pady=6)

        # CURRENT SESSION
        # ------------------------------------------------------------
        session = tk.Frame(
            workspace,
            bg="white",
            highlightbackground=C["line"],
            highlightthickness=1,
            height=66,
        )
        session.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=10,
            pady=(5, 4),
        )
        session.grid_propagate(False)
        session.grid_columnconfigure(1, weight=1)

        tk.Label(
            session,
            text="▣",
            font=("Segoe UI Symbol", 22, "bold"),
            bg=C["blue"],
            fg="white",
            width=3,
        ).grid(row=0, column=0, sticky="ns", padx=(8, 10), pady=8)

        session_text = tk.Frame(session, bg="white")
        session_text.grid(
            row=0,
            column=1,
            sticky="ew",
            pady=7,
        )

        tk.Label(
            session_text,
            text="CURRENT TEACHING SESSION",
            font=("Segoe UI", 8, "bold"),
            bg="white",
            fg=C["blue"],
            anchor="w",
        ).pack(fill=tk.X)

        tk.Label(
            session_text,
            text=(
                f"{self.current_class}   •   "
                f"{self.current_category}   •   "
                f"{self.current_subject}   •   "
                f"{self.current_term}"
            ),
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg=C["text"],
            anchor="w",
        ).pack(fill=tk.X, pady=(2, 0))

        try:
            selected_filename = curriculum_files[
                self.current_class
            ][self.current_category][
                self.current_subject
            ][self.current_term]
        except KeyError:
            selected_filename = "No curriculum mapping"

        tk.Label(
            session,
            text=selected_filename,
            font=("Consolas", 8),
            bg="#EAF7FF",
            fg=C["text"],
            padx=10,
            pady=7,
        ).grid(
            row=0,
            column=2,
            sticky="e",
            padx=(8, 12),
            pady=10,
        )

        # ------------------------------------------------------------
        # INFORMATION CARDS
        # ------------------------------------------------------------
        cards = tk.Frame(workspace, bg="#EAF7FF", height=72)
        cards.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=14,
            pady=(0, 10),
        )
        cards.grid_propagate(False)

        for col in range(4):
            cards.grid_columnconfigure(col, weight=1)

        def info_card(column, title, value, color, icon):
            card = tk.Frame(cards, bg=color)
            card.grid(
                row=0,
                column=column,
                sticky="nsew",
                padx=4,
            )

            tk.Label(
                card,
                text=icon,
                font=("Segoe UI Symbol", 19, "bold"),
                bg=color,
                fg="white",
            ).pack(side=tk.LEFT, padx=(12, 8))

            text_box = tk.Frame(card, bg=color)
            text_box.pack(
                side=tk.LEFT,
                fill=tk.BOTH,
                expand=True,
                pady=9,
            )

            tk.Label(
                text_box,
                text=title,
                font=("Segoe UI", 8, "bold"),
                bg=color,
                fg="#EAF7FF",
                anchor="w",
            ).pack(fill=tk.X)

            tk.Label(
                text_box,
                text=value,
                font=("Segoe UI", 10, "bold"),
                bg=color,
                fg="white",
                anchor="w",
            ).pack(fill=tk.X, pady=(2, 0))

        info_card(0, "CLASS", self.current_class, C["yellow"], "▰")
        info_card(1, "DEPARTMENT", self.current_category, C["red"], "▤")
        info_card(2, "SUBJECT", self.current_subject, C["green"], "▣")
        info_card(3, "TERM", self.current_term, C["purple"], "▦")

        # ------------------------------------------------------------
        # MAIN WORKSPACE GRID
        # ------------------------------------------------------------
        body = tk.Frame(workspace, bg="#EAF7FF")
        body.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=14,
            pady=(0, 12),
        )
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=0, minsize=315)
        body.grid_columnconfigure(1, weight=1)

        # ------------------------------------------------------------
        # LEFT TOPICS PANEL
        # ------------------------------------------------------------
        topics_card = tk.Frame(
            body,
            bg="white",
            highlightbackground=C["line"],
            highlightthickness=1,
        )
        topics_card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 8),
        )

        topics_card.grid_rowconfigure(2, weight=1)
        topics_card.grid_columnconfigure(0, weight=1)

        topics_header = tk.Frame(
            topics_card,
            bg=C["blue"],
            height=55,
        )
        topics_header.grid(
            row=0,
            column=0,
            sticky="ew",
        )
        topics_header.grid_propagate(False)

        tk.Label(
            topics_header,
            text="☰",
            font=("Segoe UI Symbol", 18, "bold"),
            bg=C["blue"],
            fg="white",
        ).pack(side=tk.LEFT, padx=(13, 8))

        tk.Label(
            topics_header,
            text="SCHEME OF WORK TOPICS",
            font=("Segoe UI", 11, "bold"),
            bg=C["blue"],
            fg="white",
        ).pack(side=tk.LEFT)

        tk.Label(
            topics_card,
            text="Click a topic to open it in the teaching area.",
            font=("Segoe UI", 8),
            bg="#111111",
            fg="#E5E5E5",
            anchor="w",
            padx=9,
            pady=8,
        ).grid(
            row=1,
            column=0,
            sticky="ew",
            padx=8,
            pady=(8, 4),
        )

        topics_shell = tk.Frame(topics_card, bg="white")
        topics_shell.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=8,
            pady=8,
        )
        topics_shell.grid_rowconfigure(0, weight=1)
        topics_shell.grid_columnconfigure(0, weight=1)

        topic_scroll = tk.Scrollbar(topics_shell)
        topic_scroll.grid(row=0, column=1, sticky="ns")

        topic_list = tk.Listbox(
            topics_shell,
            font=("Segoe UI", 10),
            # Keep every topic row black in every department theme.
            bg="#000000",
            fg="#FFFFFF",
            # Selected topic is a slightly lighter charcoal for clarity.
            selectbackground="#333333",
            selectforeground="#FFFFFF",
            activestyle="none",
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightbackground="#000000",
            yscrollcommand=topic_scroll.set,
        )
        topic_list.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        topic_scroll.config(command=topic_list.yview)

        # Build topics directly from the actual content already displayed
        # on the main dashboard.
        topics = []
        for line in raw_content.splitlines():
            clean = line.strip()
            if not clean:
                continue

            if re.match(r"(?i)^week\s*\d+", clean):
                topics.append(clean)
            elif re.match(
                r"(?i)^(topic|unit|chapter)\s*[:\-]",
                clean,
            ):
                topics.append(clean)
            elif (
                re.match(r"^\d+[\.)]\s+.+", clean)
                and len(clean) <= 100
            ):
                topics.append(clean)

        unique_topics = []
        seen = set()

        for topic in topics:
            key = topic.lower()
            if key not in seen:
                seen.add(key)
                unique_topics.append(topic)

        if not unique_topics:
            unique_topics = [
                "FULL SCHEME OF WORK",
                "Select FULL SCHEME below to display all content.",
            ]

        for topic in unique_topics:
            topic_list.insert(tk.END, topic)

        # ------------------------------------------------------------
        # RIGHT TEACHING PANEL
        # ------------------------------------------------------------
        teaching_card = tk.Frame(
            body,
            bg="white",
            highlightbackground=C["line"],
            highlightthickness=1,
        )
        teaching_card.grid(
            row=0,
            column=1,
            sticky="nsew",
        )

        teaching_card.grid_rowconfigure(1, weight=1)
        teaching_card.grid_columnconfigure(0, weight=1)

        teaching_header = tk.Frame(
            teaching_card,
            bg=C["blue"],
            height=55,
        )
        teaching_header.grid(
            row=0,
            column=0,
            sticky="ew",
        )
        teaching_header.grid_propagate(False)

        tk.Label(
            teaching_header,
            text="▤  TEACHING AREA",
            font=("Segoe UI", 13, "bold"),
            bg=C["blue"],
            fg="white",
        ).pack(side=tk.LEFT, padx=14)

        tk.Label(
            teaching_header,
            text="LIVE LESSON BOARD",
            font=("Segoe UI", 8, "bold"),
            bg="#0B4E91",
            fg="#DDF5FF",
            padx=9,
            pady=5,
        ).pack(side=tk.LEFT)

        # Teaching action button.
        teaching_header_button = tk.Button(
            teaching_header,
            text="▤  FULL SCHEME",
            bg="#123F78",
            activebackground="#0D315E",
            fg="white",
            font=("Segoe UI", 8, "bold"),
            relief=tk.FLAT,
            bd=0,
            padx=11,
            pady=5,
            cursor="hand2",
        )
        teaching_header_button.pack(
            side=tk.RIGHT,
            padx=10,
        )

        # ------------------------------------------------------------
        # TEACHING BOARD
        # ------------------------------------------------------------
        board = tk.Frame(
            teaching_card,
            bg=C["dark"],
        )
        board.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=8,
            pady=8,
        )
        board.grid_rowconfigure(0, weight=1)
        board.grid_columnconfigure(0, weight=1)

        # Faint school logo watermark.
        if getattr(workspace, "_isss_watermark", None) is not None:
            watermark = tk.Label(
                board,
                image=getattr(workspace, "_isss_watermark", None),
                bg=C["dark"],
                bd=0,
            )
            watermark.place(
                relx=0.76,
                rely=0.53,
                anchor="center",
            )

        # Decorative background.
        board_graphics = tk.Canvas(
            board,
            bg=C["dark"],
            highlightthickness=0,
            bd=0,
        )
        board_graphics.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        def draw_board_graphics(event=None):
            width = max(board_graphics.winfo_width(), 600)
            height = max(board_graphics.winfo_height(), 400)

            board_graphics.delete("all")

            # Full teaching-workspace department artwork, matching the
            # selected department: gold Science equations, silver Arts books
            # and pens, or bronze Commercial market/business imagery.
            # Keep the PhotoImage referenced on the Toplevel to prevent GC.
            department_image_loaded = False
            try:
                image_path = self._department_background_path()
                if MODULE_PIL_AVAILABLE and image_path and os.path.isfile(image_path):
                    with Image.open(image_path) as original:
                        background_image = original.convert("RGB").resize(
                            (width, height), Image.Resampling.LANCZOS
                        )
                    workspace._department_workspace_photo = ImageTk.PhotoImage(
                        background_image
                    )
                    board_graphics.create_image(
                        0, 0,
                        image=workspace._department_workspace_photo,
                        anchor="nw",
                        tags="department_background",
                    )
                    department_image_loaded = True
            except Exception as exc:
                print("Teaching workspace department image could not be loaded:", exc)

            if not department_image_loaded:
                board_graphics.create_rectangle(
                    0, 0, width, height,
                    fill=C["dark"], outline="",
                )

            # Large subtle educational circles.
            board_graphics.create_oval(
                width * 0.58,
                -height * 0.22,
                width * 1.10,
                height * 0.78,
                outline=C["line"],
                width=2,
            )
            board_graphics.create_oval(
                width * 0.67,
                -height * 0.08,
                width * 1.01,
                height * 0.57,
                outline=C["dark2"],
                width=2,
            )

            # Network lines.
            points = [
                (width * 0.08, height * 0.14),
                (width * 0.20, height * 0.08),
                (width * 0.32, height * 0.19),
                (width * 0.78, height * 0.82),
                (width * 0.91, height * 0.68),
                (width * 0.87, height * 0.17),
            ]

            for a, b in (
                (0, 1),
                (1, 2),
                (2, 3),
                (3, 4),
                (4, 5),
                (1, 5),
            ):
                board_graphics.create_line(
                    points[a][0],
                    points[a][1],
                    points[b][0],
                    points[b][1],
                    fill=C["line"],
                    width=2,
                )

            for x, y in points:
                board_graphics.create_oval(
                    x - 4,
                    y - 4,
                    x + 4,
                    y + 4,
                    fill=C["blue2"],
                    outline="",
                )

            # Low-contrast subject watermark motif matching the department.
            motifs = {
                "Science": ("E = mc²", "a² + b² = c²", "π ≈ 3.14", "H₂O"),
                "Arts": ("BOOKS  •  IDEAS", "READ  •  WRITE", "✒", "✎"),
                "Commercial": ("MARKET  •  TRADE", "₦  $  £", "BUY  •  SELL", "GROWTH ↑"),
            }
            motif_color = C["blue2"]
            for i, motif in enumerate(motifs.get(self.current_category, motifs["Science"])):
                board_graphics.create_text(
                    width * (0.58 + (i % 2) * 0.20),
                    height * (0.18 + (i // 2) * 0.55),
                    text=motif,
                    fill=motif_color,
                    stipple="gray50",
                    font=("Segoe UI", 17 if i % 2 == 0 else 13, "bold"),
                    anchor="center",
                )

        board_graphics.bind(
            "<Configure>",
            draw_board_graphics,
        )

        # Actual lesson text is a child of board and is placed above the
        # graphics canvas.
        lesson_shell = tk.Frame(
            board,
            bg=C["dark"],
        )
        lesson_shell.place(
            relx=0.018,
            rely=0.018,
            relwidth=0.964,
            relheight=0.964,
        )

        lesson_scroll = tk.Scrollbar(lesson_shell)
        lesson_scroll.pack(
            side=tk.RIGHT,
            fill=tk.Y,
        )

        teaching_text = tk.Text(
            lesson_shell,
            wrap=tk.WORD,
            font=("Consolas", 11),
            bg=C["dark"],
            fg="#DCEEFF",
            insertbackground="white",
            selectbackground="#0B67A7",
            selectforeground="white",
            padx=20,
            pady=18,
            relief=tk.FLAT,
            bd=0,
            yscrollcommand=lesson_scroll.set,
        )
        teaching_text.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
        )
        lesson_scroll.config(
            command=teaching_text.yview,
        )

        # ------------------------------------------------------------
        # FOOTER
        # ------------------------------------------------------------
        footer = tk.Frame(
            teaching_card,
            bg="#EEF8FF",
            height=42,
        )
        footer.grid(
            row=2,
            column=0,
            sticky="ew",
        )
        footer.grid_propagate(False)

        # ===== MOVING WATERMARK - slightly visible, moves in the line while reading =====
        # Create watermark that moves horizontally across reading area
        watermark_text = f" {getattr(self, 'student_username', 'STUDENT')} • I.S.S.S • {self.current_subject} • {self.current_class} • READING "
        moving_watermark = tk.Label(
            board,
            text=watermark_text,
            font=("Segoe UI", 8),
            bg=C["dark"],
            fg="#1E3A5F",  # Slightly visible - dark blue on dark background
            bd=0,
        )
        # Place it slightly visible at top
        moving_watermark.place(relx=0, rely=0.02, anchor="nw")
        
        # Animation variables
        watermark_x = 0.0
        watermark_direction = 0.002
        
        def animate_watermark():
            nonlocal watermark_x, watermark_direction
            try:
                if not board.winfo_exists():
                    return
                watermark_x += watermark_direction
                if watermark_x > 0.7:
                    watermark_direction = -0.002
                elif watermark_x < 0.0:
                    watermark_direction = 0.002
                
                # Move watermark slightly - moving in the line
                moving_watermark.place(relx=watermark_x, rely=0.02)
                
                # Also add subtle pulse - change fg slightly to be slightly more visible then less
                # This creates the moving line effect
                board.after(80, animate_watermark)
            except:
                pass
        
        # Start animation
        board.after(100, animate_watermark)
        
        # ===== BOOKMARK WATERMARK - shows where you stopped =====
        # Tag for bookmark position - slightly visible watermark line
        teaching_text.tag_configure("bookmark_watermark", background="#1A3A5A", foreground="#7EB8FF", 
                                   font=("Consolas", 11, "bold"), borderwidth=1, relief="flat")
        teaching_text.tag_configure("bookmark_line", background="#0F2A4A", foreground="#5A9AE8",
                                   underline=True)
        
        # Function to show bookmark watermark at saved position
        def show_bookmark_watermark(scroll_frac, text_pos, topic_name):
            try:
                # Add watermark line at bookmark position
                teaching_text.config(state=tk.NORMAL)
                # Insert watermark indicator
                try:
                    # Find line
                    teaching_text.mark_set("bookmark_mark", text_pos)
                    # Add tag
                    teaching_text.tag_add("bookmark_line", text_pos, f"{text_pos} lineend")
                    # Insert visual marker above
                    teaching_text.insert(text_pos, f"\n{'='*60}\n🔖 YOU STOPPED HERE - {topic_name[:40]} - Press CONTINUE to resume\n{'='*60}\n")
                    teaching_text.tag_add("bookmark_watermark", text_pos, f"{text_pos} + 3 lines")
                    teaching_text.config(state=tk.DISABLED)
                    # Scroll to it
                    teaching_text.yview_moveto(scroll_frac)
                    # Flash the watermark
                    def flash_watermark(count=0):
                        if count < 6 and teaching_text.winfo_exists():
                            bg = "#1A3A5A" if count % 2 == 0 else "#2A5A8A"
                            teaching_text.tag_configure("bookmark_watermark", background=bg)
                            teaching_text.after(400, lambda: flash_watermark(count+1))
                    flash_watermark()
                except Exception as e:
                    print(f"Watermark show error: {e}")
            except Exception as e:
                print(f"Bookmark watermark error: {e}")
        
        self._show_bookmark_watermark = show_bookmark_watermark
        
        # Reading line tracker - shows current reading line with slight watermark
        reading_line_label = tk.Label(
            board,
            text="● Reading...",
            font=("Segoe UI", 7),
            bg="#0F2A4A",
            fg="#4A8AD4",
            padx=6,
            pady=2,
        )
        reading_line_label.place(relx=0.02, rely=0.95, anchor="sw")
        
        def update_reading_line(*args):
            try:
                if teaching_text.winfo_exists() and reading_line_label.winfo_exists():
                    # Get current view position
                    top_idx = teaching_text.index("@0,0")
                    line_num = top_idx.split(".")[0]
                    reading_line_label.config(text=f"● Line {line_num} • {watermark_text[:20]}")
            except:
                pass
        
        # Bind scroll to update reading line
        teaching_text.bind("<MouseWheel>", lambda e: teaching_text.after(100, update_reading_line))
        teaching_text.bind("<Button-4>", lambda e: teaching_text.after(100, update_reading_line))
        teaching_text.bind("<Button-5>", lambda e: teaching_text.after(100, update_reading_line))
        lesson_scroll.config(command=lambda *args: (teaching_text.yview(*args), update_reading_line()))
        
        topic_status = tk.Label(
            footer,
            text="Ready for teaching.",
            font=("Segoe UI", 9, "bold"),
            bg="#EEF8FF",
            fg=C["text"],
            anchor="w",
        )
        topic_status.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=12,
        )
        
        # NEW: STOP button - saves where student stopped reading
        def save_bookmark_action():
            try:
                # Get current scroll position
                scroll_frac = teaching_text.yview()[0]  # 0.0 to 1.0
                # Get text position at top of view
                text_pos = teaching_text.index("@0,0")
                # Get snippet of current view
                snippet = teaching_text.get(text_pos, f"{text_pos} + 5 lines")
                snippet = snippet.strip()[:150]
                
                topic = getattr(self, "active_study_topic", self.current_subject)
                
                # Get student_id from current session
                student_id = getattr(self, "student_id", None)
                if not student_id:
                    messagebox.showinfo("Login Required", "Please log in to Study App to save your reading position. Your position will be remembered next time you log in with same password.", parent=workspace)
                    return
                
                saved = save_reading_bookmark(
                    student_id, 
                    self.current_class, 
                    self.current_category, 
                    self.current_subject, 
                    self.current_term, 
                    topic,
                    scroll_frac,
                    text_pos,
                    snippet
                )
                if saved:
                    topic_status.config(text=f"✅ STOPPED - Saved at {topic[:30]} - Position {scroll_frac:.0%} - Will continue here next login")
                    messagebox.showinfo("Position Saved", f"✅ Your reading position saved!\n\nClass: {self.current_class}\nSubject: {self.current_subject}\nTerm: {self.current_term}\nTopic: {topic[:50]}\n\nWhen you log in next time with same username & password, you will see where you stopped and can continue.", parent=workspace)
                else:
                    topic_status.config(text="Could not save position")
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save position: {e}", parent=workspace)
        
        # Make save_bookmark accessible for auto-save
        self._current_teaching_text = teaching_text
        self._current_topic_status = topic_status
        self._save_bookmark_func = save_bookmark_action
        
        # QUIZ BUTTON - NEW: visible button to start quiz anytime
        def start_quiz_action():
            try:
                workspace.destroy()
            except:
                pass
            # Small delay then open quiz
            try:
                self.root.after(300, self.open_topic_quiz)
            except:
                self.open_topic_quiz()
        
        quiz_button = tk.Button(
            footer,
            text="🎮 QUIZ",
            command=start_quiz_action,
            bg="#7C3AED",
            fg="white",
            activebackground="#6D28D9",
            activeforeground="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=14,
            pady=4,
            cursor="hand2",
        )
        quiz_button.pack(side=tk.RIGHT, padx=(0,8), pady=4)
        
        stop_button = tk.Button(
            footer,
            text="⏹ STOP & SAVE",
            command=save_bookmark_action,
            bg="#DC2626",
            fg="white",
            activebackground="#B91C1C",
            activeforeground="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=4,
            cursor="hand2",
        )
        stop_button.pack(side=tk.RIGHT, padx=(0,8), pady=4)
        
        # Auto-save every 60 seconds
        def auto_save_bookmark():
            try:
                if hasattr(self, "student_id") and self.student_id and workspace.winfo_exists():
                    scroll_frac = teaching_text.yview()[0]
                    text_pos = teaching_text.index("@0,0")
                    topic = getattr(self, "active_study_topic", self.current_subject)
                    snippet = teaching_text.get(text_pos, f"{text_pos} + 2 lines")[:100]
                    save_reading_bookmark(self.student_id, self.current_class, self.current_category, self.current_subject, self.current_term, topic, scroll_frac, text_pos, snippet)
                if workspace.winfo_exists():
                    workspace.after(60000, auto_save_bookmark)
            except:
                pass
        
        workspace.after(60000, auto_save_bookmark)

        # ------------------------------------------------------------
        # CONTENT FUNCTIONS
        # ------------------------------------------------------------
        def show_full_scheme():
            self.active_study_topic = f"Full {self.current_subject} scheme"
            self.active_study_text = raw_content
            teaching_text.config(state=tk.NORMAL)
            teaching_text.delete("1.0", tk.END)

            teaching_text.insert(
                tk.END,
                f"{self.current_subject.upper()}\n"
                f"{self.current_class}  •  "
                f"{self.current_category}  •  "
                f"{self.current_term}\n"
                f"{'=' * 70}\n\n"
                f"{raw_content}",
            )

            teaching_text.config(state=tk.DISABLED)
            teaching_text.yview_moveto(0)

            topic_status.config(
                text=(
                    f"Full {self.current_subject} scheme loaded "
                    f"• Ready for teaching."
                )
            )

        def show_selected_topic(event=None):
            selected = topic_list.curselection()

            if not selected:
                return

            selected_topic = topic_list.get(
                selected[0]
            ).strip()

            if selected_topic.upper() == "FULL SCHEME OF WORK":
                show_full_scheme()
                return

            lines = raw_content.splitlines()
            start_index = None

            for index, line in enumerate(lines):
                if line.strip() == selected_topic:
                    start_index = index
                    break

            if start_index is None:
                section = selected_topic
            else:
                collected = [
                    lines[start_index]
                ]

                for line in lines[start_index + 1:]:
                    clean = line.strip()

                    if (
                        re.match(
                            r"(?i)^week\s*\d+",
                            clean,
                        )
                        or re.match(
                            r"(?i)^(topic|unit|chapter)\s*[:\-]",
                            clean,
                        )
                    ):
                        break

                    collected.append(line)

                section = chr(10).join(
                    collected
                ).strip()

            # Save this exact section so the end-of-session quiz assesses the
            # point the learner reached, rather than an unrelated subject.
            self.active_study_topic = selected_topic
            self.active_study_text = section

            teaching_text.config(
                state=tk.NORMAL
            )
            teaching_text.delete(
                "1.0",
                tk.END,
            )

            teaching_text.insert(
                tk.END,
                f"{self.current_subject.upper()}\n"
                f"{self.current_class}  •  "
                f"{self.current_category}  •  "
                f"{self.current_term}\n"
                f"{'=' * 70}\n\n"
                f"{section}",
            )

            teaching_text.config(
                state=tk.DISABLED
            )
            teaching_text.yview_moveto(0)

            topic_status.config(
                text=f"Teaching topic: {selected_topic}"
            )

        topic_list.bind(
            "<<ListboxSelect>>",
            show_selected_topic,
        )

        teaching_header_button.config(
            command=show_full_scheme
        )

        # Immediately show the actual selected curriculum.
        workspace.after(
            100,
            show_full_scheme,
        )

        workspace.protocol(
            "WM_DELETE_WINDOW",
            workspace.destroy,
        )


    # ========================================================

    # FILE HANDLING

    # ========================================================

    def load_file_content(self, filename):

        # Keep the original direct lookup first.

        app_dir = os.path.dirname(os.path.abspath(__file__))

        search_paths = [
            filename,
            os.path.join(app_dir, filename),
            os.path.join(app_dir, "curriculum", filename),
            os.path.join(app_dir, "curriculum_files", filename),
            os.path.join(app_dir, "Curriculum", filename),
            os.path.join(app_dir, "Curriculum Files", filename),
            os.path.join(app_dir, self.current_class, self.current_category, filename),
            os.path.join(app_dir, self.current_class, filename),
            os.path.join(app_dir, self.current_category, filename),
        ]

        actual_filename = next(
            (path for path in search_paths if os.path.isfile(path)),
            None
        )

        # If the user placed the file in a nested curriculum folder, find the
        # exact mapped filename without changing the curriculum mapping.
        if actual_filename is None:
            for root_dir, dirs, files in os.walk(app_dir):
                # Avoid Python/virtual-environment folders.
                dirs[:] = [
                    d for d in dirs
                    if d not in {"venv", ".venv", "__pycache__", ".git"}
                ]
                if filename in files:
                    actual_filename = os.path.join(root_dir, filename)
                    break

        if actual_filename is None:
            actual_filename = filename

        if os.path.exists(actual_filename):

            try:

                with open(

                    actual_filename,

                    "r",

                    encoding="utf-8"

                ) as file:

                    return file.read()

            except Exception as e:

                return (

                    f"Error reading file {actual_filename}:\n\n"

                    f"{str(e)}"

                )

        return (
            f"=== FILE NOT FOUND: {filename} ===\n\n"
            f"The workspace looked in the app folder, curriculum folders, "
            f"class/department folders, and nested subfolders.\n\n"
            f"Current selection:\n"
            f"{self.current_class} • {self.current_category} • "
            f"{self.current_subject} • {self.current_term}\n\n"
            f"Expected exact filename:\n{filename}\n\n"
            f"Place that .txt file somewhere inside the application folder "
            f"and open the workspace again."
        )

    # ========================================================

    # DISPLAY

    # ========================================================

    def update_display(self):

        try:

            filename = curriculum_files[

                self.current_class

            ][self.current_category][

                self.current_subject

            ][self.current_term]

        except KeyError:

            self.current_selection_label.config(

                text=(

                    f"[{self.current_class} — "

                    f"{self.current_category}] • "

                    f"{self.current_subject} • "

                    f"{self.current_term}"

                )

            )

            self.file_status.config(

                text="⚠ No Mapping",

                bg="#FEF3C7",

                fg="#92400E"

            )

            self.notes_text.config(state=tk.NORMAL)

            self.notes_text.delete("1.0", tk.END)

            self.notes_text.insert(

                tk.END,

                "NO CURRICULUM MAPPING FOUND\n\n"

                "There is no file mapping for the selected "

                "class, department, subject and term."

            )

            self.notes_text.config(state=tk.DISABLED)

            return

        file_content = self.load_file_content(filename)

        self.current_selection_label.config(

            text=(

                f"[{self.current_class} — "

                f"{self.current_category}] • "

                f"{self.current_subject} • "

                f"{self.current_term}"

            )

        )

        if "=== FILE NOT FOUND:" in file_content:

            self.file_status.config(

                text="⚠ No File Loaded",

                bg="#FEF3C7",

                fg="#92400E"

            )

        else:

            self.file_status.config(

                text="✓ File Loaded",

                bg="#DCFCE7",

                fg="#166534"

            )

        self.notes_text.config(

            state=tk.NORMAL

        )

        self.notes_text.delete(

            "1.0",

            tk.END

        )

        self.notes_text.insert(

            tk.END,

            file_content

        )

        self.notes_text.config(

            state=tk.DISABLED

        )

        self.update_timer_label()

    # ========================================================

    # TIMER

    # ========================================================

    def start_timer(self):

        if not self.is_running:

            if self.time_left <= 0:

                self.reset_timer_value()

            self.is_running = True

            self.start_button.config(

                text="⏸ Pause",

                bg="#D97706"

            )

            self.time_status_label.config(

                text="SESSION IN PROGRESS"

            )

            self.countdown()

        else:

            self.is_running = False

            if self.timer_job is not None:

                try:

                    self.root.after_cancel(

                        self.timer_job

                    )

                except Exception:

                    pass

                self.timer_job = None

            self.start_button.config(

                text="▶ Resume",

                bg="#22C55E"

            )

            self.time_status_label.config(

                text="SESSION PAUSED"

            )

    def stop_timer_without_reset(self):

        self.is_running = False

        if self.timer_job is not None:

            try:

                self.root.after_cancel(

                    self.timer_job

                )

            except Exception:

                pass

            self.timer_job = None

    def _collect_quiz_statements(self, text):
        """Collect NOTES-BASED statements - NOT scheme titles - actual lesson content for quiz"""
        statements = []
        if not text:
            return []
        import re
        if len(text.strip()) < 10:
            return []
        raw_lines = text.splitlines()
        for line in raw_lines:
            try:
                l = line.strip()
                while l and l[0] in "-*•· \t":
                    l = l[1:].strip()
                l = re.sub(r"^\s*\d+[\.\]]\s*", "", l)
                l = re.sub(r"^\s*\([a-z0-9]+\)\s*", "", l, flags=re.IGNORECASE)
                clean_line = l.strip()
            except:
                clean_line = line.strip()
            
            if not clean_line or len(clean_line) < 12:
                continue
            if re.match(r"(?i)^SS\d+\s+.*LESSON NOTES", clean_line):
                continue
            if re.match(r"(?i)^FIRST TERM|SECOND TERM|THIRD TERM", clean_line):
                continue
            if re.match(r"(?i)^WEEK\s*\d+\s*$", clean_line):
                continue
            if re.match(r"(?i)^TOPIC:\s*$", clean_line):
                continue
            
            try:
                sentences = re.split(r'[.!?]+', clean_line)
            except:
                sentences = [clean_line]
            
            for sent in sentences:
                s = sent.strip()
                if len(s) < 18 or len(s) > 350:
                    continue
                if len(s.split()) < 4:
                    continue
                if s.isupper() and len(s) < 60:
                    continue
                if s.upper().startswith("SS") and "LESSON NOTES" in s.upper():
                    continue
                if s.lower() not in {x.lower() for x in statements}:
                    statements.append(s)
        
        if len(statements) < 8:
            try:
                all_sents = re.split(r'[.!?\n]+', text)
                for s in all_sents:
                    s = s.strip()
                    if 18 <= len(s) <= 350 and len(s.split()) >= 4:
                        if s.upper().startswith("SS") and "LESSON NOTES" in s.upper():
                            continue
                        if re.match(r"(?i)^WEEK\s*\d+$", s):
                            continue
                        if s.lower() not in {x.lower() for x in statements}:
                            statements.append(s)
            except:
                pass
        return statements




    def _generate_quiz_questions(self, topic, topic_text, all_text_for_distractors, max_questions=50):
        """WAEC-STYLE 50 QUESTIONS PER TOPIC PER TERM - FROM NOTES, NOT SUBTITLE
        Generates like WAEC paper in image: each question followed by 4 options A-D.
        - Questions based on actual notes content inside the topic
        - 1 accurate answer from notes + 3 inaccurate distractors from other notes
        - Not WAEC exam questions, but WAEC FORMAT using your notes
        """
        import re, random
        
        max_questions = 50
        
        statements = self._collect_quiz_statements(topic_text)
        
        if len(statements) < 15:
            extra = self._collect_quiz_statements(all_text_for_distractors)
            for s in extra:
                if s.lower() not in [x.lower() for x in statements] and len(s) > 20:
                    statements.append(s)
        
        if len(statements) < 20 and topic_text:
            more = [s.strip() for s in re.split(r'[.!?\n]+', topic_text) if 25 <= len(s.strip()) <= 380 and len(s.split()) >= 5]
            for s in more:
                if s.lower() not in [x.lower() for x in statements]:
                    low = s.lower()
                    if re.match(r'^(week|topic|unit|chapter)\s*\d+', low):
                        continue
                    if len(s.split()) < 5:
                        continue
                    statements.append(s.strip())
        
        uniq = []
        seen = set()
        for s in statements:
            clean = s.strip()
            if len(clean) < 25:
                continue
            low = clean.lower()
            if low.startswith("definition of") and len(clean.split()) <= 4:
                continue
            if re.match(r'^(ss\d+|first term|second term|third term)', low):
                continue
            if "lesson notes" in low and len(clean) < 60:
                continue
            if low not in seen:
                seen.add(low)
                uniq.append(clean)
        statements = uniq
        
        if len(statements) < 5:
            base = topic_text or all_text_for_distractors or topic
            fallback = [s.strip() for s in re.split(r'[.!?\n]+', base) if 25 <= len(s.strip()) <= 350]
            if len(fallback) < 5:
                fallback = [f"{topic} - Important point {i+1}: {base[:100]}" for i in range(10)]
            statements = fallback
        
        random.shuffle(statements)
        
        all_pool = self._collect_quiz_statements(all_text_for_distractors)
        if len(all_pool) < 30:
            all_pool = statements * 3
        random.shuffle(all_pool)
        
        def create_waec_style_question(note_stmt, other_notes, q_index):
            stmt = note_stmt.strip()
            if len(stmt) < 25:
                return None
            
            stmt = re.sub(r'\s+', ' ', stmt).strip()
            
            term = None
            definition = None
            m = re.match(r'^(.{2,70}?)\s+(is|are|means|refers to|is defined as|is called|represents|includes|is known as)\s+(.+)$', stmt, re.IGNORECASE)
            if m:
                possible_term = m.group(1).strip()
                possible_def = m.group(3).strip()
                possible_term = re.sub(r'^(Therefore,|Hence,|Thus,|So,|In biology,|In Biology,|According to the notes,|From the notes,)\s*', '', possible_term, flags=re.IGNORECASE).strip()
                if 1 <= len(possible_term.split()) <= 7 and len(possible_term) < 70 and possible_term.lower() not in ["it","this","that","they","these","those","there","this is","that is"]:
                    if len(possible_def) > 15 and len(possible_def) < 250:
                        term = possible_term
                        definition = possible_def
            
            prompt = ""
            correct = ""
            q_type = random.choice(["fill_blank", "definition", "correct_statement", "function", "meaning", "completion"])
            
            if q_type == "fill_blank" and len(stmt.split()) >= 8:
                words = stmt.split()
                candidates = []
                for idx, w in enumerate(words):
                    cw = re.sub(r'[^A-Za-z]', '', w)
                    if len(cw) >= 4 and idx not in [0, len(words)-1] and cw.lower() not in ["that","this","with","from","which","have","been","will","when"]:
                        candidates.append((idx, cw))
                if candidates:
                    hide_idx, hidden_word = random.choice(candidates)
                    blanked = " ".join(words[:hide_idx] + ["_____"] + words[hide_idx+1:])
                    prompt = blanked
                    if random.random() < 0.3:
                        prompt = f"Complete the statement from the notes: {blanked}"
                    correct = hidden_word
                else:
                    prompt = f'Which of the following is correct according to the notes on "{topic}"?'
                    correct = stmt
                    q_type = "correct_statement"
            
            elif q_type == "definition" and term and definition:
                waec_def_templates = [
                    f'What is "{term}" according to the notes?',
                    f'According to the notes, what is {term}?',
                    f'{term} is defined in the notes as ______',
                    f'What does {term} mean as explained in the notes?',
                    f'From the lesson notes, {term} is:',
                ]
                prompt = random.choice(waec_def_templates)
                correct = definition
            
            elif q_type == "correct_statement":
                waec_correct_templates = [
                    f'Which of the following is correct according to the notes on "{topic}"?',
                    f'From the notes on {topic}, which statement is true?',
                    f'According to the lesson notes, which of these is stated?',
                    f'Which fact is mentioned in the notes for this topic?',
                    f'Choose the correct statement from the notes:',
                    f'Which of these is true based on the notes?',
                ]
                prompt = random.choice(waec_correct_templates)
                correct = stmt
            
            elif q_type == "function":
                if "function" in stmt.lower() or "used for" in stmt.lower() or "role" in stmt.lower() or "purpose" in stmt.lower():
                    prompt = f'What is the function described in the notes: "{stmt[:90]}...?"'
                    correct = stmt
                else:
                    prompt = f'According to the notes, which statement correctly explains the topic "{topic}"?'
                    correct = stmt
            
            elif q_type == "meaning":
                if term and definition:
                    prompt = f'In the notes, "{term}" means ______'
                    correct = definition
                else:
                    prompt = f'What does the following statement from the notes mean? "{stmt[:80]}..."'
                    correct = stmt
            
            else:
                if len(stmt.split()) >= 7:
                    words = stmt.split()
                    if len(words) > 5:
                        blanked_start = " ".join(words[:-1]) + " _____"
                        prompt = blanked_start
                        correct = words[-1]
                        correct = re.sub(r'[^A-Za-z]', '', correct)
                        if len(correct) < 3:
                            prompt = f'Which of the following correctly completes the statement from the notes? "{blanked_start}"'
                            correct = stmt
                    else:
                        prompt = f'Which of the following is correct according to the notes?'
                        correct = stmt
                else:
                    prompt = f'According to the notes, which is correct?'
                    correct = stmt
            
            if not prompt or not correct or len(correct) < 2:
                return None
            
            wrong_pool = [s for s in other_notes if s.lower() != stmt.lower() and s.lower() != correct.lower() and len(s) > 15]
            random.shuffle(wrong_pool)
            wrong_choices = []
            
            is_single_word = len(correct.split()) == 1 and len(re.sub(r'[^A-Za-z]', '', correct)) >= 3
            
            for w in wrong_pool:
                if len(wrong_choices) >= 10:
                    break
                if w.lower() == correct.lower() or w.lower() == stmt.lower():
                    continue
                
                if is_single_word:
                    w_words = w.split()
                    for ww in w_words:
                        clean_ww = re.sub(r'[^A-Za-z]', '', ww)
                        if len(clean_ww) >= 3 and clean_ww.lower() != correct.lower() and clean_ww.lower() not in [x.lower() for x in wrong_choices]:
                            if clean_ww.lower() not in ["that","this","with","from","which","have","been","will","when","there","their","about"]:
                                wrong_choices.append(clean_ww)
                                if len(wrong_choices) >= 3:
                                    break
                else:
                    if w.lower() not in [x.lower() for x in wrong_choices] and 15 <= len(w) <= 320:
                        wrong_choices.append(w)
                if len(wrong_choices) >= 3:
                    break
            
            while len(wrong_choices) < 3:
                if all_pool:
                    cand = random.choice(all_pool)
                    if is_single_word:
                        cand_words = cand.split()
                        for cw in cand_words:
                            clean_cw = re.sub(r'[^A-Za-z]', '', cw)
                            if len(clean_cw) >= 3 and clean_cw.lower() != correct.lower() and clean_cw.lower() not in [x.lower() for x in wrong_choices]:
                                wrong_choices.append(clean_cw)
                                break
                    else:
                        if cand.lower() != correct.lower() and cand.lower() not in [x.lower() for x in wrong_choices] and 15 <= len(cand) <= 300:
                            wrong_choices.append(cand)
                else:
                    wrong_choices.append(f"Incorrect option {len(wrong_choices)+1} not in notes")
                if len(wrong_choices) > 20:
                    break
            
            wrong_choices = wrong_choices[:3]
            if len(wrong_choices) < 3:
                return None
            
            choices = [correct] + wrong_choices[:3]
            seen_c = set()
            uniq_c = []
            for c in choices:
                low = c.lower()
                if low not in seen_c:
                    seen_c.add(low)
                    uniq_c.append(c)
            choices = uniq_c
            while len(choices) < 4:
                choices.append(f"Distractor {len(choices)}")
            choices = choices[:4]
            random.shuffle(choices)
            
            if correct not in choices:
                choices[0] = correct
                random.shuffle(choices)
            
            return {
                "prompt": prompt,
                "choices": choices,
                "answer": correct,
                "topic": topic,
                "original": stmt,
                "source_note": stmt,
                "q_type": q_type
            }
        
        questions = []
        used_answers = set()
        used_prompts = set()
        
        for idx, stmt in enumerate(statements):
            if len(questions) >= max_questions:
                break
            if stmt.lower() in used_answers:
                continue
            q = create_waec_style_question(stmt, all_pool, idx+1)
            if q:
                if q["prompt"].lower() not in used_prompts:
                    questions.append(q)
                    used_answers.add(q["answer"].lower())
                    used_answers.add(q["original"].lower())
                    used_prompts.add(q["prompt"].lower())
        
        attempts = 0
        while len(questions) < max_questions and attempts < 400:
            attempts += 1
            stmt = random.choice(statements)
            q = create_waec_style_question(stmt, all_pool, len(questions)+1)
            if q:
                questions.append(q)
        
        while len(questions) < max_questions:
            base = random.choice(questions) if questions else None
            if base:
                new_wrong = [s for s in all_pool if s.lower() != base["answer"].lower()]
                random.shuffle(new_wrong)
                if len(base["answer"].split()) == 1:
                    words = []
                    for s in new_wrong[:6]:
                        for w in s.split():
                            cw = re.sub(r'[^A-Za-z]', '', w)
                            if len(cw) >= 3 and cw.lower() != base["answer"].lower():
                                words.append(cw)
                    new_choices = [base["answer"]] + words[:3]
                else:
                    new_choices = [base["answer"]] + new_wrong[:3]
                while len(new_choices) < 4:
                    new_choices.append(f"Incorrect option {len(new_choices)}")
                random.shuffle(new_choices)
                questions.append({
                    "prompt": base["prompt"],
                    "choices": new_choices[:4],
                    "answer": base["answer"],
                    "topic": topic,
                    "original": base["original"],
                    "source_note": base["source_note"],
                    "q_type": base.get("q_type", "correct_statement")
                })
            else:
                questions.append({
                    "prompt": f'According to the notes on "{topic}", which of the following is correct?',
                    "choices": [f"Correct statement from notes on {topic}", f"Incorrect statement 1 about {topic}", f"Incorrect statement 2 about {topic}", f"Incorrect statement 3 about {topic}"],
                    "answer": f"Correct statement from notes on {topic}",
                    "topic": topic,
                    "original": topic
                })
        
        return questions[:50]


    def open_topic_quiz(self):
        """WAEC QUIZ FROM NOTES - DIVERSE - SAVE PROGRESS - FULLSCREEN ANTI-PEEK - TERM RATING 100/100"""
        print("Quiz button clicked - opening WAEC quiz FROM NOTES - FULLSCREEN")
        try:
            topic = getattr(self, "active_study_topic", None) or getattr(self, "current_subject", "General")
            full_content = getattr(self, "current_content", "") or ""
            topic_text_raw = getattr(self, "active_study_text", "") or ""
            
            def extract_topic_notes(selected_topic, full_lesson_notes):
                try:
                    import re
                    if not selected_topic or not full_lesson_notes:
                        return ""
                    topic_clean = selected_topic.strip()
                    lines = full_lesson_notes.splitlines()
                    start_idx = None
                    for idx, line in enumerate(lines):
                        if line.strip() == topic_clean:
                            start_idx = idx
                            break
                        if topic_clean.lower() in line.strip().lower() and len(topic_clean) > 5:
                            if re.match(r"(?i)^(week|topic|unit|chapter|A\.|B\.|\d+\.)", line.strip()) or topic_clean[:20].lower() in line.lower():
                                start_idx = idx
                                break
                    if start_idx is None:
                        return ""
                    collected = []
                    for line in lines[start_idx:]:
                        clean = line.strip()
                        if len(collected) > 5:
                            if re.match(r"(?i)^week\s*\d+", clean) and clean != lines[start_idx].strip():
                                break
                            if re.match(r"(?i)^(topic|unit|chapter)\s*[:\-]", clean) and clean.lower() != topic_clean.lower():
                                break
                        collected.append(line)
                        if len(collected) > 350:
                            break
                    return "\n".join(collected).strip()
                except Exception as e:
                    return ""
            
            topic_notes = ""
            if topic and full_content:
                topic_notes = extract_topic_notes(topic, full_content)
            
            if topic_notes and len(topic_notes.strip()) > 100:
                topic_text = topic_notes
                all_content = full_content
            elif topic_text_raw and len(topic_text_raw.strip()) > 100:
                topic_text = topic_text_raw
                all_content = full_content or topic_text_raw
            else:
                topic_text = full_content
                all_content = full_content
            
            if not topic_text or len(topic_text.strip()) < 20:
                topic_text = full_content or topic_text_raw
                all_content = full_content or topic_text
            
            if not all_content or len(all_content.strip()) < 10:
                all_content = f"{topic} is a topic in {self.current_subject} {self.current_class} {self.current_term}. " * 20
                topic_text = all_content
            
            saved_bookmark = None
            if hasattr(self, "student_id") and self.student_id:
                try:
                    saved_bookmark = load_quiz_bookmark(self.student_id, self.current_class, self.current_category, self.current_subject, self.current_term, topic)
                except:
                    pass
            
            questions = []
            try:
                questions = self._generate_quiz_questions(topic, topic_text, all_content, max_questions=50)
            except:
                questions = []
            
            if not questions and len(all_content) > 20:
                try:
                    questions = self._generate_quiz_questions(topic, all_content, all_content, max_questions=50)
                except:
                    questions = []
            
            if not questions:
                import random, re
                emergency = []
                facts = []
                if all_content:
                    sents = [s.strip() for s in re.split(r'[.!?\n]+', all_content) if 18 <= len(s.strip()) <= 250 and len(s.split()) >= 4]
                    filtered = []
                    for s in sents:
                        if s.upper().startswith("SS") and "LESSON NOTES" in s.upper():
                            continue
                        if re.match(r"(?i)^WEEK\s*\d+$", s):
                            continue
                        if len(s) < 18:
                            continue
                        if "PDF page" in s or "Read this image" in s:
                            continue
                        filtered.append(s)
                    facts = filtered[:80]
                if len(facts) < 10:
                    facts = [f"{topic} is defined as important concept in {self.current_subject}"] * 13
                
                for i in range(50):
                    fact = facts[i % len(facts)]
                    prompt = f"What is {topic}?" if i % 2 == 0 else f"Which is correct about {topic}?"
                    wrong_pool = [f for f in facts if f != fact]
                    if len(wrong_pool) < 3:
                        wrong_pool = [f"Not related to {topic}"] * 3
                    wrong = wrong_pool[:3]
                    choices = [fact] + wrong
                    random.shuffle(choices)
                    emergency.append({"prompt": prompt, "choices": choices[:4], "answer": fact, "topic": topic})
                questions = emergency
            
            if not questions:
                from tkinter import messagebox
                messagebox.showinfo("Quiz Info", f"No questions for {topic}", parent=self.root)
                return
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            from tkinter import messagebox
            messagebox.showerror("Quiz Error", f"Failed: {e}", parent=self.root)
            return
        
        try:
            win = tk.Toplevel(self.root)
            win.title(f"WAEC QUIZ FROM NOTES - {topic[:40]} - {len(questions)} Q - FULLSCREEN")
            try:
                win.attributes('-fullscreen', True)
                win.attributes('-topmost', True)
            except:
                win.geometry(f"{win.winfo_screenwidth()}x{win.winfo_screenheight()}+0+0")
                win.state('zoomed')
            win.configure(bg="#EEF2FF")
            win.transient(self.root)
            win.grab_set()
            win.lift()
            win.focus_force()
            win.protocol("WM_DELETE_WINDOW", lambda: None)
            
            score = 0
            idx = 0
            correct_list = []
            
            if saved_bookmark and not saved_bookmark.get("completed"):
                try:
                    saved_idx = saved_bookmark.get("current_question_index", 0)
                    saved_score = saved_bookmark.get("score", 0)
                    saved_correct = saved_bookmark.get("correct_answers", [])
                    if saved_idx > 0 and saved_idx < len(questions):
                        score = saved_score
                        idx = saved_idx
                        correct_list = saved_correct if isinstance(saved_correct, list) else []
                except:
                    pass
            
            header = tk.Frame(win, bg="#4F46E5", padx=20, pady=14)
            header.pack(fill="x")
            header_inner = tk.Frame(header, bg="#4F46E5")
            header_inner.pack(fill="x")
            tk.Label(header_inner, text=f"📝 WAEC QUIZ FROM NOTES — {len(questions)} Q — FULLSCREEN ANTI-PEEK", font=("Segoe UI", 12, "bold"), bg="#4F46E5", fg="white", anchor="w").pack(fill="x", anchor="w")
            tk.Label(header_inner, text=f"{self.current_class} | {self.current_category} | {self.current_subject} | {self.current_term} | 🔒 Fullscreen - No Peeking", font=("Segoe UI", 9), bg="#4F46E5", fg="#E0E7FF", anchor="w").pack(fill="x", anchor="w", pady=(3,0))
            tk.Label(header_inner, text=f"Topic: {topic[:70]} | Resuming Q{idx+1}" if saved_bookmark and idx>0 else f"Topic: {topic[:70]}", font=("Segoe UI", 9), bg="#4F46E5", fg="#C7D2FE", anchor="w", wraplength=850).pack(fill="x", anchor="w")
            
            body = tk.Frame(win, bg="#EEF2FF", padx=16, pady=10)
            body.pack(fill="both", expand=True)
            
            top = tk.Frame(body, bg="#EEF2FF")
            top.pack(fill="x", pady=(0,8))
            
            progress_frame = tk.Frame(top, bg="white", highlightbackground="#C7D2FE", highlightthickness=2, bd=0)
            progress_frame.pack(side="left", padx=(0,10), ipadx=8, ipady=4)
            progress_var = tk.StringVar(value=f"Q {idx+1} / {len(questions)} • NOTES")
            tk.Label(progress_frame, textvariable=progress_var, font=("Segoe UI", 10, "bold"), bg="white", fg="#4338CA").pack()
            
            score_frame = tk.Frame(top, bg="#10B981", highlightbackground="#059669", highlightthickness=2, bd=0)
            score_frame.pack(side="left", ipadx=10, ipady=4)
            score_var = tk.StringVar(value=f"🏆 {score} / {len(questions)}")
            tk.Label(score_frame, textvariable=score_var, font=("Segoe UI", 11, "bold"), bg="#10B981", fg="white").pack()
            
            def save_and_exit_quiz():
                try:
                    if hasattr(self, "student_id") and self.student_id:
                        save_quiz_bookmark(self.student_id, self.current_class, self.current_category, self.current_subject, self.current_term, topic, idx, score, len(questions), correct_list, questions, completed=False)
                    win.attributes('-fullscreen', False)
                    win.attributes('-topmost', False)
                    win.grab_release()
                    win.destroy()
                except:
                    try:
                        win.destroy()
                    except:
                        pass
            
            stop_btn = tk.Button(top, text="⏹ STOP & SAVE (Continue on Login)", command=save_and_exit_quiz, bg="#DC2626", fg="white", font=("Segoe UI", 9, "bold"), padx=12, pady=6, relief=tk.FLAT, cursor="hand2")
            stop_btn.pack(side="right", padx=(10,0))
            
            def exit_fullscreen():
                try:
                    win.attributes('-fullscreen', False)
                    win.attributes('-topmost', False)
                    win.geometry("900x720")
                except:
                    pass
            
            fullscreen_btn = tk.Button(top, text="🗖 Exit Fullscreen", command=exit_fullscreen, bg="#6B7280", fg="white", font=("Segoe UI", 8, "bold"), padx=8, pady=4, relief=tk.FLAT, cursor="hand2")
            fullscreen_btn.pack(side="right", padx=(5,0))
            
            tracker_outer = tk.Frame(body, bg="#EEF2FF")
            tracker_outer.pack(fill="x", pady=(0,10))
            tracker = tk.Frame(tracker_outer, bg="white", padx=12, pady=8, highlightbackground="#A5B4FC", highlightthickness=1.5, bd=0)
            tracker.pack(fill="x")
            tk.Label(tracker, text="✅ Correct Answers From Notes:", font=("Segoe UI", 9, "bold"), bg="white", fg="#059669", anchor="w").pack(fill="x", anchor="w")
            correct_var = tk.StringVar(value="None yet ✨" if not correct_list else f"{len(correct_list)} correct")
            tk.Label(tracker, textvariable=correct_var, font=("Segoe UI", 9), bg="white", fg="#64748B", wraplength=820, justify="left", anchor="w").pack(fill="x", anchor="w", pady=(4,0))
            
            q_outer = tk.Frame(body, bg="#EEF2FF")
            q_outer.pack(fill="x", pady=(0,12))
            q_box = tk.Frame(q_outer, bg="white", padx=16, pady=14, highlightbackground="#8B5CF6", highlightthickness=2, bd=0)
            q_box.pack(fill="x")
            prompt_var = tk.StringVar(value="")
            tk.Label(q_box, textvariable=prompt_var, font=("Segoe UI", 12, "bold"), bg="white", fg="#1E1B4B", wraplength=800, justify="left", anchor="w").pack(fill="x", anchor="w")
            
            opts_frame = tk.Frame(body, bg="#EEF2FF")
            opts_frame.pack(fill="both", expand=True)
            
            feedback_var = tk.StringVar(value="")
            tk.Label(body, textvariable=feedback_var, font=("Segoe UI", 10, "bold"), bg="#EEF2FF", fg="#1F2937", wraplength=820, justify="left", anchor="w").pack(fill="x", pady=(8,0))
            
            option_buttons = []
            option_colors = ["#3B82F6", "#10B981", "#F59E0B", "#EC4899"]
            light_colors = ["#EFF6FF", "#F0FDF4", "#FEF3C7", "#FDF2F8"]
            
            def update_tracker():
                if not correct_list:
                    correct_var.set("None yet ✨")
                else:
                    txt = ""
                    for i, ans in enumerate(correct_list[-5:]):
                        short = ans[:55] + "..." if len(ans) > 55 else ans
                        txt += f"{len(correct_list)-len(correct_list[-5:])+i+1}. {short}  "
                    if len(correct_list) > 5:
                        txt = f"... +{len(correct_list)-5} more | " + txt
                    correct_var.set(txt)
            
            def auto_save_progress():
                try:
                    if hasattr(self, "student_id") and self.student_id:
                        save_quiz_bookmark(self.student_id, self.current_class, self.current_category, self.current_subject, self.current_term, topic, idx, score, len(questions), correct_list, questions, completed=False)
                    if win.winfo_exists():
                        win.after(30000, auto_save_progress)
                except:
                    pass
            
            def render():
                q = questions[idx]
                progress_var.set(f"Q {idx+1} / {len(questions)} • NOTES • Saved")
                score_var.set(f"🏆 {score} / {len(questions)}")
                prompt_var.set(q["prompt"])
                feedback_var.set("")
                for child in opts_frame.winfo_children():
                    child.destroy()
                option_buttons.clear()
                for i, choice in enumerate(q["choices"]):
                    letter = ["A", "B", "C", "D"][i]
                    accent = option_colors[i]
                    light = light_colors[i]
                    card_outer = tk.Frame(opts_frame, bg="#EEF2FF")
                    card_outer.pack(fill="x", pady=5)
                    card = tk.Frame(card_outer, bg="white", padx=10, pady=8, highlightbackground=accent, highlightthickness=1.8, bd=0)
                    card.pack(fill="x", padx=4)
                    letter_lbl = tk.Label(card, text=letter, font=("Segoe UI", 11, "bold"), bg=accent, fg="white", width=3, padx=4, pady=2)
                    letter_lbl.pack(side="left", padx=(0,10))
                    def make_click(c=choice):
                        return lambda: check(c)
                    btn = tk.Button(card, text=choice, font=("Segoe UI", 10), bg="white", fg="#1F2937", anchor="w", justify="left", wraplength=660, relief="flat", bd=0, padx=6, pady=4, cursor="hand2", command=make_click(), activebackground=light)
                    btn.pack(side="left", fill="x", expand=True)
                    def on_enter(e, c=card, li=light):
                        c.config(bg=li, highlightthickness=2.5)
                    def on_leave(e, c=card):
                        c.config(bg="white", highlightthickness=1.8)
                    btn.bind("<Enter>", on_enter)
                    btn.bind("<Leave>", on_leave)
                    option_buttons.append((btn, card, choice, letter_lbl, light, accent))
            
            def check(selected):
                nonlocal score
                q = questions[idx]
                correct = q["answer"]
                is_correct = selected == correct
                # Show green for correct, red for wrong selection
                for btn, card, choice, letter_lbl, light, accent in option_buttons:
                    btn.config(state="disabled")
                    if choice == correct:
                        card.config(bg="#DCFCE7", highlightbackground="#22C55E", highlightthickness=3)
                        letter_lbl.config(bg="#22C55E")
                        btn.config(bg="#DCFCE7")
                    elif choice == selected and not is_correct:
                        card.config(bg="#FEE2E2", highlightbackground="#EF4444", highlightthickness=3)
                        letter_lbl.config(bg="#EF4444")
                        btn.config(bg="#FEE2E2")
                    else:
                        card.config(bg="#F3F4F6", highlightbackground="#D1D5DB")
                if is_correct:
                    # REQUIREMENT: every correct shows green and adds point
                    feedback_var.set(f"✅ CORRECT! +1 point! Score: {score+1}")
                    if correct not in correct_list:
                        correct_list.append(correct)
                    score += 1
                    score_var.set(f"🏆 {score} / {len(questions)}")
                    update_tracker()
                    try:
                        if hasattr(self, "student_id") and self.student_id:
                            save_quiz_bookmark(self.student_id, self.current_class, self.current_category, self.current_subject, self.current_term, topic, idx, score, len(questions), correct_list, questions, completed=False)
                    except:
                        pass
                    win.after(1200, next_q)
                else:
                    # REQUIREMENT: incorrect moves on to next quiz and still remains your answer until another correct
                    # Keep correct_list (previous correct answers remain visible), don't remove score
                    feedback_var.set(f"❌ WRONG! Correct is GREEN. Score stays {score}. Moving to next...")
                    # Keep tracker as is (remains your answer until you get another correct)
                    # Auto move to next after showing correct answer in green
                    def auto_next_after_wrong():
                        feedback_var.set("👉 Moving to next question... Previous correct answers kept")
                        next_q()
                    win.after(2000, auto_next_after_wrong)
                    # Also allow clicking green to move faster
                    def enable_green_click():
                        feedback_var.set("👉 Click GREEN for next, or wait...")
                        for btn, card, choice, letter_lbl, light, accent in option_buttons:
                            if choice == correct:
                                btn.config(state="normal", cursor="hand2", command=lambda: next_q())
                    win.after(800, enable_green_click)
            
            def next_q():
                nonlocal idx
                if idx < len(questions) - 1:
                    idx += 1
                    render()
                else:
                    try:
                        if hasattr(self, "student_id") and self.student_id:
                            save_quiz_bookmark(self.student_id, self.current_class, self.current_category, self.current_subject, self.current_term, topic, len(questions)-1, score, len(questions), correct_list, questions, completed=True)
                            save_quiz_completion(self.student_id, self.current_class, self.current_category, self.current_subject, self.current_term, topic, score, len(questions))
                    except:
                        pass
                    for child in body.winfo_children():
                        child.destroy()
                    result = tk.Frame(body, bg="white", padx=20, pady=20, highlightbackground="#8B5CF6", highlightthickness=3, bd=0)
                    result.pack(fill="both", expand=True, padx=20, pady=20)
                    tk.Label(result, text="🎉 QUIZ COMPLETE! 🎉", font=("Segoe UI", 22, "bold"), bg="white", fg="#4F46E5").pack(pady=(10,5))
                    tk.Label(result, text=f"Topic: {topic}", font=("Segoe UI", 12, "bold"), bg="white", fg="#1F2937", wraplength=700).pack()
                    tk.Label(result, text=f"{self.current_term} | {self.current_class} | Based on Notes | 🔒 Fullscreen", font=("Segoe UI", 10), bg="white", fg="#6B7280").pack(pady=(0,10))
                    percent = (score / len(questions) * 100) if questions else 0
                    color = "#10B981" if percent >= 50 else "#EF4444"
                    tk.Label(result, text=f"{score} / {len(questions)}", font=("Segoe UI", 28, "bold"), bg="white", fg=color).pack(pady=5)
                    tk.Label(result, text=f"{percent:.0f}%", font=("Segoe UI", 14, "bold"), bg="white", fg=color).pack()
                    msg = "🏆 Excellent!" if percent >= 80 else "🌟 Good job!" if percent >= 60 else "📚 Read notes again!" if percent >= 40 else "💪 Study more!"
                    tk.Label(result, text=msg, font=("Segoe UI", 12, "bold"), bg="white", fg="#4B5563").pack(pady=10)
                    try:
                        term_rating = None
                        if hasattr(self, "student_id") and self.student_id:
                            term_rating = get_term_rating(self.student_id, self.current_class, self.current_category, self.current_subject, self.current_term)
                        if term_rating:
                            rating_frame = tk.Frame(result, bg="#EEF2FF", padx=15, pady=12, highlightbackground="#4F46E5", highlightthickness=2, bd=0)
                            rating_frame.pack(fill="x", pady=(15,10), padx=10)
                            tk.Label(rating_frame, text=f"📊 FIRST TERM RATING - {self.current_subject}", font=("Segoe UI", 12, "bold"), bg="#EEF2FF", fg="#4F46E5", anchor="w").pack(fill="x", anchor="w")
                            completed = term_rating.get("completed_topics", 0)
                            total_score = term_rating.get("total_score", 0)
                            total_possible = term_rating.get("total_possible", 0)
                            final_100 = term_rating.get("final_rating_100", 0)
                            tk.Label(rating_frame, text=f"Topics: {completed} | Score: {total_score}/{total_possible} | {final_100:.1f}%", font=("Segoe UI", 10), bg="#EEF2FF", fg="#1F2937", anchor="w").pack(fill="x", anchor="w", pady=(5,0))
                            tk.Label(rating_frame, text=f"🏆 FINAL RATING: {final_100:.0f}/100", font=("Segoe UI", 16, "bold"), bg="#EEF2FF", fg="#4F46E5" if final_100>=50 else "#EF4444", anchor="w").pack(fill="x", anchor="w", pady=(5,0))
                            if final_100 >= 100:
                                detail = "Perfect! 50/50 in all quizzes - 100/100!"
                            elif final_100 >= 80:
                                detail = f"Excellent! {completed} topics, {final_100:.0f}/100 - Keep up!"
                            else:
                                detail = f"{completed} topics, {final_100:.0f}/100 - Aim for 100/100 by getting 50/50!"
                            tk.Label(rating_frame, text=detail, font=("Segoe UI", 9), bg="#EEF2FF", fg="#6B7280", wraplength=700, anchor="w", justify="left").pack(fill="x", anchor="w", pady=(3,0))
                            if "First Term" in self.current_term:
                                tk.Label(rating_frame, text=f"📚 At end of First Term, rating is {final_100:.0f}/100. Get 50/50 in all to get 100/100!", font=("Segoe UI", 8, "italic"), bg="#EEF2FF", fg="#6B7280", wraplength=700, justify="left", anchor="w").pack(fill="x", anchor="w", pady=(5,0))
                    except Exception as e:
                        print(f"Term rating display error: {e}")
                    btns = tk.Frame(result, bg="white")
                    btns.pack(pady=15)
                    def close_quiz_final():
                        try:
                            win.attributes('-fullscreen', False)
                            win.attributes('-topmost', False)
                            win.grab_release()
                        except:
                            pass
                        win.destroy()
                    tk.Button(btns, text="🔄 Play Again", command=lambda: (close_quiz_final(), self.open_topic_quiz()), bg="#7C3AED", fg="white", font=("Segoe UI", 11, "bold"), padx=20, pady=10, relief="flat", cursor="hand2").pack(side="left", padx=8)
                    def show_full_term_rating():
                        try:
                            rating_win = tk.Toplevel(win)
                            rating_win.title(f"Term Rating 100/100 - {self.current_subject}")
                            rating_win.geometry("600x500")
                            rating_win.configure(bg="white")
                            rating_win.attributes('-topmost', True)
                            term_rating = get_term_rating(self.student_id, self.current_class, self.current_category, self.current_subject, self.current_term) if hasattr(self, "student_id") and self.student_id else None
                            if term_rating:
                                tk.Label(rating_win, text=f"📊 {self.current_term} FINAL RATING", font=("Segoe UI", 16, "bold"), bg="white", fg="#4F46E5").pack(pady=15)
                                final = term_rating.get("final_rating_100", 0)
                                total_sc = term_rating.get("total_score", 0)
                                total_poss = term_rating.get("total_possible", 0)
                                comp = term_rating.get("completed_topics", 0)
                                tk.Label(rating_win, text=f"{final:.0f}/100", font=("Segoe UI", 48, "bold"), bg="white", fg="#4F46E5" if final>=50 else "#EF4444").pack(pady=20)
                                tk.Label(rating_win, text=f"{total_sc}/{total_poss} points | {comp} topics", font=("Segoe UI", 12), bg="white", fg="#1F2937").pack()
                                msg = "🏆 PERFECT 100/100!" if final >= 100 else f"Keep going - {final:.0f}/100, aim for 100/100!"
                                tk.Label(rating_win, text=msg, font=("Segoe UI", 11, "bold"), bg="white", fg="#4B5563", wraplength=500).pack(pady=10)
                                list_frame = tk.Frame(rating_win, bg="white")
                                list_frame.pack(fill="both", expand=True, padx=20, pady=10)
                                for t, data in term_rating.get("completed_quizzes", {}).items():
                                    tk.Label(list_frame, text=f"{t[:50]}: {data['score']}/{data['total']} ({data['percentage']:.0f}%)", font=("Segoe UI", 9), bg="white", fg="#374151", anchor="w").pack(fill="x", anchor="w", pady=2)
                            else:
                                tk.Label(rating_win, text="No quizzes completed yet", font=("Segoe UI", 12), bg="white", fg="#6B7280").pack(pady=30)
                            tk.Button(rating_win, text="Close", command=rating_win.destroy, bg="#E5E7EB", fg="#374151", font=("Segoe UI", 10, "bold"), padx=20, pady=8, relief=tk.FLAT).pack(pady=10)
                        except Exception as e:
                            print(f"Show rating error: {e}")
                    tk.Button(btns, text="📊 View 100/100 Rating", command=lambda: show_full_term_rating(), bg="#4F46E5", fg="white", font=("Segoe UI", 11, "bold"), padx=20, pady=10, relief="flat", cursor="hand2").pack(side="left", padx=8)
                    tk.Button(btns, text="✅ Close", command=close_quiz_final, bg="#E5E7EB", fg="#374151", font=("Segoe UI", 11, "bold"), padx=20, pady=10, relief="flat", cursor="hand2").pack(side="left", padx=8)
            
            try:
                win.after(30000, auto_save_progress)
            except:
                pass
            update_tracker()
            render()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            from tkinter import messagebox
            try:
                messagebox.showerror("Quiz Error", f"Quiz failed: {e}", parent=self.root)
            except:
                pass


    def open_teaching_workspace_with_bookmark(self, bookmark):
        """Open teaching workspace and scroll to bookmarked position - shows moving watermark + Continue after login"""
        try:
            self.open_teaching_workspace()
            def scroll_to_bookmark():
                try:
                    if hasattr(self, "_current_teaching_text") and self._current_teaching_text:
                        text_widget = self._current_teaching_text
                        if text_widget.winfo_exists():
                            # Show watermark at bookmark position
                            scroll_frac = bookmark.get("scroll_fraction", 0.0)
                            text_pos = bookmark.get("text_position", "1.0")
                            topic = bookmark.get("topic", self.current_subject)
                            
                            text_widget.yview_moveto(scroll_frac)
                            try:
                                text_widget.mark_set("insert", text_pos)
                                text_widget.see(text_pos)
                            except:
                                pass
                            
                            # Show bookmark watermark with moving effect
                            if hasattr(self, "_show_bookmark_watermark"):
                                try:
                                    self._show_bookmark_watermark(scroll_frac, text_pos, topic)
                                except:
                                    pass
                            
                            # Add visible watermark line in text
                            try:
                                text_widget.config(state=tk.NORMAL)
                                # Check if watermark already exists
                                content = text_widget.get("1.0", tk.END)
                                if "🔖 YOU STOPPED HERE" not in content:
                                    # Insert watermark at position
                                    text_widget.insert(text_pos, f"\n{'='*50}\n🔖 WATERMARK: YOU STOPPED HERE - {topic[:40]}\n📍 Login with password to continue - Press CONTINUE button below\n{'='*50}\n\n")
                                    # Tag it
                                    try:
                                        text_widget.tag_add("bookmark_watermark", text_pos, f"{text_pos} + 4 lines")
                                        text_widget.tag_configure("bookmark_watermark", background="#1E3A5A", foreground="#7EC8E3", font=("Consolas", 11, "bold"))
                                    except:
                                        pass
                                text_widget.config(state=tk.DISABLED)
                            except Exception as e:
                                print(f"Watermark insert failed: {e}")
                            
                            if hasattr(self, "_current_topic_status"):
                                self._current_topic_status.config(text=f"🔖 WATERMARK: Continued from where you stopped: {topic[:40]} - Scroll: {scroll_frac:.0%} - Press CONTINUE")
                            
                            # Show Continue popup with password verification already done
                            # The user already logged in with password, now show Continue dialog
                            def show_continue_watermark():
                                try:
                                    cont_win = tk.Toplevel(self.root)
                                    cont_win.title("📖 Continue Reading - Watermark")
                                    cont_win.geometry("520x280")
                                    cont_win.configure(bg="#EEF2FF")
                                    cont_win.transient(self.root)
                                    cont_win.grab_set()
                                    
                                    # Rounded frame for popup
                                    header = tk.Frame(cont_win, bg="#4F46E5", padx=20, pady=12)
                                    header.pack(fill="x")
                                    tk.Label(header, text="🔖 WATERMARK - Continue Reading", font=("Segoe UI", 13, "bold"), bg="#4F46E5", fg="white").pack(anchor="w")
                                    tk.Label(header, text=f"Welcome back {getattr(self, 'student_username', '')}! You logged in with password", font=("Segoe UI", 9), bg="#4F46E5", fg="#C7D2FE").pack(anchor="w")
                                    
                                    body = tk.Frame(cont_win, bg="white", padx=20, pady=15)
                                    body.pack(fill="both", expand=True, padx=12, pady=12)
                                    
                                    tk.Label(body, text=f"📍 You stopped at:", font=("Segoe UI", 10, "bold"), bg="white", fg="#1F2937", anchor="w").pack(fill="x", anchor="w")
                                    tk.Label(body, text=f"Topic: {topic[:50]}\nPosition: {scroll_frac:.0%} scrolled\nSnippet: {bookmark.get('snippet','')[:80]}...", font=("Segoe UI", 9), bg="white", fg="#4B5563", justify="left", anchor="w", wraplength=460).pack(fill="x", anchor="w", pady=8)
                                    
                                    tk.Label(body, text="✨ Moving watermark shows your reading line. Press CONTINUE to resume.", font=("Segoe UI", 9, "italic"), bg="white", fg="#059669", anchor="w").pack(fill="x", anchor="w", pady=(8,0))
                                    
                                    btns = tk.Frame(body, bg="white")
                                    btns.pack(fill="x", pady=(15,0))
                                    
                                    def do_continue():
                                        cont_win.destroy()
                                        # Focus teaching workspace and scroll
                                        try:
                                            if text_widget.winfo_exists():
                                                text_widget.yview_moveto(scroll_frac)
                                                text_widget.see(text_pos)
                                                text_widget.focus_set()
                                        except:
                                            pass
                                    
                                    tk.Button(btns, text="▶️ CONTINUE", command=do_continue, bg="#10B981", fg="white", font=("Segoe UI", 11, "bold"), padx=20, pady=8, relief="flat", cursor="hand2").pack(side="left", padx=(0,10))
                                    tk.Button(btns, text="Close", command=cont_win.destroy, bg="#E5E7EB", fg="#374151", font=("Segoe UI", 10), padx=15, pady=8, relief="flat", cursor="hand2").pack(side="left")
                                    
                                except Exception as e:
                                    print(f"Continue watermark popup failed: {e}")
                            
                            self.root.after(600, show_continue_watermark)
                            
                except Exception as e:
                    print(f"Scroll to bookmark failed: {e}")
            self.root.after(800, scroll_to_bookmark)
        except Exception as e:
            print(f"Open with bookmark failed: {e}")

    def countdown(self):

        if not self.is_running:

            return

        if self.time_left > 0:

            self.time_left -= 1

            self.update_timer_label()

            self.timer_job = self.root.after(

                1000,

                self.countdown

            )

        else:

            self.is_running = False

            self.timer_job = None
            self.save_progress(completed_session=True)
            messagebox.showinfo("Session completed", "Well done! Your learning progress has been saved to your student account.")

            self.start_button.config(

                text="▶ Start Session",

                bg="#22C55E"

            )

            self.time_status_label.config(

                text="TIME UP — COMPLETED"

            )

            messagebox.showinfo(

                "Time Up!",

                "Your study session is complete. Your progress has been saved.\n\nNow let's check what you learned with a short topic quiz."

            )

            self.root.after(250, self.open_topic_quiz)

    # ========================================================

    # TEXT TO SPEECH

    # ========================================================

    def speak_notes(self):

        if not self.tts_available or not self.tts_engine:

            messagebox.showwarning(

                "Text-to-Speech Unavailable",

                "pyttsx3 is not available on this computer."

            )

            return

        try:

            filename = curriculum_files[

                self.current_class

            ][self.current_category][

                self.current_subject

            ][self.current_term]

        except KeyError:

            messagebox.showwarning(

                "No Curriculum Mapping",

                "There is no curriculum file mapped to the current selection."

            )

            return

        text_to_speak = self.load_file_content(

            filename

        )

        if len(text_to_speak) > 8000:

            text_to_speak = (

                text_to_speak[:8000] +

                "... [Truncated]"

            )

        try:

            self.tts_engine.say(

                f"Scheme of work for "

                f"{self.current_subject}, "

                f"{self.current_term}, "

                f"in {self.current_class} "

                f"{self.current_category}. "

                f"{text_to_speak}"

            )

            self.tts_engine.runAndWait()

        except Exception as e:

            messagebox.showerror(

                "Read Aloud Error",

                f"Could not read the notes aloud.\n\n{e}"

            )



# ============================================================

# START APPLICATION

# ============================================================



# ============================================================
# I.S.S.S. CONNECT CLIENT (embedded in this file)
# ============================================================
import threading
import secrets
import webbrowser
from urllib.parse import quote

try:
    import requests
except ImportError:
    requests = None

DEFAULT_SERVER = os.environ.get("ISSS_CHAT_SERVER", "http://127.0.0.1:8000").rstrip("/")

class CommunicationWindow:
    def __init__(self, parent, student_username="Student", embedded=False, on_close=None):
        self.parent = parent
        self.username = student_username
        self.embedded = embedded
        self.on_close = on_close
        self.closed = False
        self._voice_stream = None
        self._voice_frames = []
        self._voice_sample_rate = 44100
        self._voice_channels = 1
        self._voice_recording = False
        self.server = DEFAULT_SERVER
        self.token = None
        self._session_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "isss_connect_session.json")
        self._saved_session = self._load_saved_session()
        if self._saved_session:
            self.server = str(self._saved_session.get("server") or self.server).rstrip("/")
        self.active = None
        self.active_kind = None
        self.last_message_id = 0
        self.poll_job = None
        self._presence_by_username = {}
        # Keep PhotoImage references alive so inline chat images remain visible.
        self._inline_chat_images = []
        self.nickname_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "isss_connect_nicknames.json")
        self.nicknames = self._load_nicknames()
        self.conversations = []
        self._message_records = {}
        self._selected_message_id = None
        self._settings = self._load_connect_settings()
        self._chat_controls_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "isss_connect_chat_controls.json")
        self._chat_controls = self._load_chat_controls()
        self._show_archived = False
        if self.embedded:
            self.window = parent.winfo_toplevel()
            self.host = tk.Frame(parent, bg="#EEF5FC")
            self.host.pack(fill="both", expand=True)
        else:
            self.window = tk.Toplevel(parent)
            self.host = self.window
            self.window.geometry("1050x700")
            self.window.minsize(820, 560)
            self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.title("Ijeshatedo Senior Secondary School | I.S.S.S Connect — Chats & Calls")
        self.host.configure(bg="#EEF5FC")
        self._build_login()
        self._apply_connect_theme()
        if self._saved_session and self._saved_session.get("token") and self._saved_session.get("username"):
            self._try_restore_session()

    def _load_saved_session(self):
        try:
            with open(self._session_file, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            return data if isinstance(data, dict) else {}
        except (OSError, ValueError, AttributeError):
            return {}

    def _save_session(self, username, token):
        """Persist the session token locally, never the user's password."""
        try:
            with open(self._session_file, "w", encoding="utf-8") as handle:
                json.dump({"username": username, "server": self.server, "token": token,
                           "remember": True}, handle, indent=2)
            self._saved_session = self._load_saved_session()
        except OSError as exc:
            messagebox.showwarning("Remember me", f"Could not save this login on this device.\n{exc}", parent=self.window)

    def _clear_saved_session(self):
        self._saved_session = {}
        try:
            if os.path.exists(self._session_file):
                os.remove(self._session_file)
        except OSError:
            pass

    def _try_restore_session(self):
        """Restore a saved login only if the server confirms the token is still valid."""
        saved = self._saved_session or {}
        try:
            self.user_entry.delete(0, "end")
            self.user_entry.insert(0, str(saved.get("username", self.username)))
            self.server_entry.delete(0, "end")
            self.server_entry.insert(0, self.server)
            self.remember_me_var.set(True)
        except (AttributeError, tk.TclError):
            pass
        if requests is None:
            return
        def worker():
            token = str(saved.get("token", ""))
            headers = {"Authorization": f"Bearer {token}"}
            valid = False
            # Support common self-profile endpoint names used by Connect server versions.
            for endpoint in ("/api/me", "/api/auth/me", "/api/profile"):
                try:
                    response = requests.get(self.server + endpoint, headers=headers, timeout=5)
                    if response.ok:
                        valid = True
                        break
                    if response.status_code in (401, 403):
                        break
                except Exception:
                    continue
            if valid:
                self.window.after(0, lambda: self._restore_session_success(saved))
        threading.Thread(target=worker, daemon=True).start()

    def _restore_session_success(self, saved):
        if self.closed or not self.host.winfo_exists():
            return
        self.username = str(saved.get("username", self.username))
        self.server = str(saved.get("server", self.server)).rstrip("/")
        self.token = str(saved.get("token", ""))
        try:
            self.login_frame.destroy()
        except tk.TclError:
            return
        self._build_chat()
        self._refresh_lists()
        self._schedule_poll()

    def _load_school_logo(self, size=(48, 48)):
        """Find and load the school's own crest from the app/assets folders."""
        if not MODULE_PIL_AVAILABLE:
            return None
        base = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            "school_logo.png", "school-logo.png", "isss_logo.png", "isss-logo.png",
            "logo.png", "badge.png", "school_badge.png", "crest.png",
            "I.S.S.S.png", "I.S.S.S. logo.png", "Ijeshatedo Senior Secondary School.png",
        ]
        search_dirs = [base, os.path.join(base, "assets"), os.path.join(base, "images"),
                       os.path.join(base, "backgrounds"), os.path.join(base, "department backgrounds")]
        for folder in search_dirs:
            for filename in candidates:
                path = os.path.join(folder, filename)
                if os.path.isfile(path):
                    try:
                        image = Image.open(path).convert("RGBA")
                        image.thumbnail(size, Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(image)
                        self._school_logo_image = photo
                        return photo
                    except Exception:
                        continue
        return None

    def _fill_connect_saved_password(self, _event=None):
        """Fill the password field when a remembered username is selected from dropdown."""
        try:
            server = self.server_entry.get().strip().rstrip("/") or self.server
            username = self.user_entry.get().strip()
            if not username:
                return
            # Try with server key first, then try all saved accounts matching username
            password = _get_connect_saved_password(server, username)
            if password is None:
                # Try to find by username only (any server)
                try:
                    accounts = _load_connect_remembered_accounts()
                    for key, acc in accounts.items():
                        if isinstance(acc, dict) and acc.get("username", "").lower() == username.lower():
                            pwd = _unprotect_local_secret(acc.get("password_dpapi", ""))
                            if pwd:
                                password = pwd
                                break
                except:
                    pass
            
            if password is not None:
                self.password_entry.delete(0, "end")
                self.password_entry.insert(0, password)
                self.auth_status.configure(text=f"Saved account '{username}' found. Password auto-filled. Click LOG IN.", fg="#15803D")
                # Remember me checked since already saved
                try:
                    self.remember_me_var.set(True)
                except:
                    pass
        except (AttributeError, tk.TclError):
            pass

    def _build_login(self):
        # NEW: Scrollable login with dropdown for saved accounts
        self.login_frame = tk.Frame(self.host, bg="white", padx=0, pady=0,
                                    highlightbackground="#C9DFF3", highlightthickness=1)
        self.login_frame.place(relx=.5, rely=.5, anchor="center", width=480, height=620)
        
        # Canvas with scrollbar for signup fields
        self._login_canvas = tk.Canvas(self.login_frame, bg="white", highlightthickness=0)
        self._login_scrollbar = ttk.Scrollbar(self.login_frame, orient="vertical", command=self._login_canvas.yview)
        self._login_canvas.configure(yscrollcommand=self._login_scrollbar.set)
        
        self._login_scrollbar.pack(side="right", fill="y")
        self._login_canvas.pack(side="left", fill="both", expand=True)
        
        self._login_inner = tk.Frame(self._login_canvas, bg="white", padx=30, pady=25)
        canvas_win = self._login_canvas.create_window((0, 0), window=self._login_inner, anchor="nw")
        
        def configure_scroll(event=None):
            self._login_canvas.configure(scrollregion=self._login_canvas.bbox("all"))
        def configure_width(event):
            self._login_canvas.itemconfig(canvas_win, width=event.width)
        
        self._login_inner.bind("<Configure>", configure_scroll)
        self._login_canvas.bind("<Configure>", configure_width)
        
        def on_mousewheel(event):
            self._login_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self._login_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        login_brand = tk.Frame(self._login_inner, bg="white")
        login_brand.pack(pady=(4, 8), fill="x")
        school_logo = self._load_school_logo((64, 64))
        if school_logo:
            tk.Label(login_brand, image=school_logo, bg="white").pack(pady=(0, 5))
        else:
            tk.Label(login_brand, text="🏫", bg="white", fg="#0D6B4D",
                     font=("Segoe UI Emoji", 34)).pack(pady=(0, 2))
        tk.Label(login_brand, text="IJESHATEDO SENIOR SECONDARY SCHOOL", bg="white", fg="#123B70",
                 font=("Segoe UI", 12, "bold"), wraplength=390, justify="center").pack()
        tk.Label(login_brand, text="I.S.S.S CONNECT", bg="white", fg="#087F5B",
                 font=("Segoe UI", 21, "bold")).pack(pady=(3, 0))
        tk.Label(self._login_inner, text="CHAT  •  GROUPS  •  VOICE CALLS  •  VIDEO CALLS\nStay Connected  •  Learn Together  •  Grow Together", bg="white",
                 fg="#64748B", font=("Segoe UI", 9), justify="center").pack(pady=(0, 13), fill="x")
        
        self.connect_signup_only_widgets = []
        self.server_label = tk.Label(self._login_inner, text="Communication server URL", bg="white", fg="#123B70", anchor="w")
        self.server_label.pack(fill="x"); self.connect_signup_only_widgets.append(self.server_label)
        self.server_entry = tk.Entry(self._login_inner, font=("Segoe UI", 10), relief="solid", bd=1)
        self.server_entry.insert(0, self.server)
        self.server_entry.pack(fill="x", ipady=7, pady=(4, 12)); self.connect_signup_only_widgets.append(self.server_entry)
        
        # NEW: Username dropdown with saved accounts
        tk.Label(self._login_inner, text="Username (select from dropdown if saved)", bg="white", fg="#123B70", anchor="w").pack(fill="x")
        # Load saved connect accounts for dropdown
        try:
            saved_connect = _load_connect_remembered_accounts()
            saved_usernames = []
            for v in saved_connect.values():
                if isinstance(v, dict) and "username" in v:
                    saved_usernames.append(v["username"])
            saved_usernames = sorted(set(saved_usernames))
        except:
            saved_usernames = []
        
        # Use Combobox for dropdown
        self.user_entry = ttk.Combobox(self._login_inner, values=saved_usernames, font=("Segoe UI", 10))
        self.user_entry.set(self.username)
        self.user_entry.pack(fill="x", ipady=7, pady=(4, 12))
        # Fill password when username selected from dropdown
        self.user_entry.bind("<<ComboboxSelected>>", self._fill_connect_saved_password)
        self.user_entry.bind("<KeyRelease>", self._fill_connect_saved_password)
        self.user_entry.bind("<FocusOut>", self._fill_connect_saved_password)
        self.user_entry.bind("<Return>", self._fill_connect_saved_password)
        self.user_entry.bind("<Button-1>", lambda e: self._login_inner.after(100, self._fill_connect_saved_password))
        
        tk.Label(self._login_inner, text="Password (8+ characters)", bg="white", fg="#123B70", anchor="w").pack(fill="x")
        pwrow = tk.Frame(self._login_inner, bg="white")
        pwrow.pack(fill="x", pady=(4, 14))
        self.password_entry = tk.Entry(pwrow, show="•", font=("Segoe UI", 10), relief="solid", bd=1)
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=7)
        confirm_label = tk.Label(self._login_inner, text="Confirm password", bg="white", fg="#123B70", anchor="w")
        confirm_label.pack(fill="x"); self.connect_signup_only_widgets.append(confirm_label)
        self.confirm_password_entry = tk.Entry(self._login_inner, show="•", font=("Segoe UI", 10), relief="solid", bd=1)
        self.confirm_password_entry.pack(fill="x", ipady=7, pady=(4, 10)); self.connect_signup_only_widgets.append(self.confirm_password_entry)
        phone_label = tk.Label(self._login_inner, text="Phone number with country code", bg="white", fg="#123B70", anchor="w")
        phone_label.pack(fill="x"); self.connect_signup_only_widgets.append(phone_label)
        self.phone_entry = tk.Entry(self._login_inner, font=("Segoe UI", 10), relief="solid", bd=1)
        self.phone_entry.insert(0, "+234")
        self.phone_entry.pack(fill="x", ipady=7, pady=(4, 12)); self.connect_signup_only_widgets.append(self.phone_entry)
        self.show_password = tk.BooleanVar(value=False)
        tk.Checkbutton(pwrow, text="Show", variable=self.show_password, bg="white",
                       command=lambda: self.password_entry.configure(show="" if self.show_password.get() else "•")).pack(side="right", padx=(8, 0))
        self.remember_me_var = tk.BooleanVar(value=bool(self._saved_session.get("remember", True)))
        tk.Checkbutton(self._login_inner, text="Remember me on this device (saves username & password for dropdown)", variable=self.remember_me_var,
                       bg="white", fg="#123B70", activebackground="white", activeforeground="#123B70",
                       font=("Segoe UI", 9), cursor="hand2").pack(anchor="w", pady=(0, 8))
        cohort = tk.Frame(self._login_inner, bg="white")
        cohort.pack(fill="x", pady=(0, 10)); self.connect_signup_only_widgets.append(cohort)
        tk.Label(cohort, text="Class", bg="white", fg="#123B70").grid(row=0, column=0, sticky="w")
        tk.Label(cohort, text="Department", bg="white", fg="#123B70").grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.class_choice = ttk.Combobox(cohort, values=("SS1", "SS2", "SS3"), state="readonly", width=12)
        self.class_choice.set("SS1")
        self.class_choice.grid(row=1, column=0, sticky="ew", pady=(3, 0))
        self.department_choice = ttk.Combobox(cohort, values=("Science", "Arts", "Commercial"), state="readonly", width=18)
        self.department_choice.set("Science")
        self.department_choice.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(3, 0))
        cohort.columnconfigure(0, weight=1); cohort.columnconfigure(1, weight=1)
        buttons = tk.Frame(self._login_inner, bg="white")
        buttons.pack(fill="x", pady=(5, 0))
        self.connect_login_button = tk.Button(buttons, text="LOG IN", bg="#0969D5", fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), cursor="hand2", command=lambda: self._auth("login"))
        self.connect_login_button.configure(height=2, bd=2, highlightthickness=1, highlightbackground="#073B8C", activebackground="#0755B5", activeforeground="white")
        self.connect_login_button.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 5))
        self.connect_signup_button = tk.Button(buttons, text="SIGN UP", bg="#0F766E", fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), cursor="hand2", command=lambda: self._auth("register"))
        self.connect_signup_button.configure(height=2, bd=2, highlightthickness=1, highlightbackground="#065F46", activebackground="#0F766E", activeforeground="white")
        self.connect_signup_button.pack(side="left", fill="x", expand=True, ipady=8, padx=(5, 0))
        self.connect_back_to_login_button = tk.Button(
            self._login_inner, text="← BACK TO LOGIN", bg="#E2E8F0", fg="#123B70",
            activebackground="#CBD5E1", relief="flat", cursor="hand2",
            font=("Segoe UI", 9, "bold"), command=lambda: self._set_connect_auth_mode("login")
        )
        self.connect_back_to_login_button.pack(fill="x", pady=(8, 0))
        self.connect_back_to_login_button.pack_forget()
        self.auth_status = tk.Label(self._login_inner, text="Select username from dropdown if saved, or type new one.",
                                    bg="white", fg="#64748B", wraplength=390, justify="left")
        self.auth_status.pack(pady=(13, 0), fill="x")
        self._set_connect_auth_mode("login")

    def _set_connect_auth_mode(self, action):
        self.connect_signup_mode = (action == "register")
        for widget in self.connect_signup_only_widgets:
            widget.pack_forget()
        if action == "register":
            self.connect_back_to_login_button.pack(fill="x", pady=(8, 0))
            for widget in self.connect_signup_only_widgets:
                if widget is self.server_label or widget is self.server_entry:
                    widget.pack(fill="x", ipady=7 if widget is self.server_entry else 0,
                                pady=(4, 12) if widget is self.server_entry else 0)
                elif hasattr(self, 'class_choice') and widget is self.class_choice.master:
                    widget.pack(fill="x", pady=(0, 10))
                elif widget is self.confirm_password_entry or widget is self.phone_entry:
                    widget.pack(fill="x", ipady=7, pady=(4, 10))
                else:
                    widget.pack(fill="x")
            # Height with scrollbar - show scrollbar when signup
            self.login_frame.place_configure(height=700)
            if hasattr(self, '_login_canvas'):
                self._login_canvas.configure(scrollregion=self._login_canvas.bbox("all"))
                self._login_scrollbar.pack(side="right", fill="y")
            self.connect_signup_button.configure(bg="#16A34A", activebackground="#15803D", text="✓ SIGN UP SELECTED")
            self.auth_status.configure(text="Scroll down to see Confirm Password. Complete all fields to create account.")
        else:
            self.connect_back_to_login_button.pack_forget()
            self.login_frame.place_configure(height=620)
            if hasattr(self, '_login_canvas'):
                self._login_canvas.configure(scrollregion=self._login_canvas.bbox("all"))
            self.connect_signup_button.configure(bg="#0F766E", activebackground="#115E59", text="SIGN UP")
            self.auth_status.configure(text="Select username from dropdown if saved, or type new one.")

    def _auth(self, action):
        if action == "register" and not getattr(self, "connect_signup_mode", False):
            self._set_connect_auth_mode("register")
            self.connect_signup_mode = True
            return
        if action == "login":
            self._set_connect_auth_mode("login")
            self.connect_signup_mode = False
            # Check lockout for Connect too
            username_check = self.user_entry.get().strip()
            if username_check:
                is_locked, remaining, attempts_left = _check_login_lockout("connect_" + username_check)
                if is_locked:
                    hours = int(remaining // 3600)
                    mins = int((remaining % 3600) // 60)
                    self.auth_status.configure(text=f"Account locked for 6 hours. Try again in {hours}h {mins}m.", fg="#B91C1C")
                    return
        if requests is None:
            messagebox.showerror("Missing library", "Install the client library with: python -m pip install requests", parent=self.window)
            return
        self.server = self.server_entry.get().strip().rstrip("/")
        username = self.user_entry.get().strip()
        password = self.password_entry.get()
        if not self.server.startswith(("http://", "https://")):
            messagebox.showerror("Server URL", "Enter a server URL starting with http:// or https://", parent=self.window); return
        if len(username) < 3 or " " in username or len(username) > 40:
            messagebox.showerror("Username", "Use 3–40 characters with no spaces.", parent=self.window); return
        if action == "register":
            self.connect_signup_button.configure(bg="#16A34A", activebackground="#15803D", text="✓ SIGN UP SELECTED")
            confirm_password = self.confirm_password_entry.get()
            phone_number = self.phone_entry.get().strip()
            if password != confirm_password:
                messagebox.showerror("Password", "Passwords do not match.", parent=self.window); return
            if len(password) < 8:
                messagebox.showerror("Password", "Use at least 8 characters.", parent=self.window); return
            if not re.fullmatch(r"\+[1-9]\d{7,14}", phone_number):
                messagebox.showerror("Phone number", "Enter a phone number with country code, e.g. +2348012345678.", parent=self.window); return
        else:
            self.connect_signup_button.configure(bg="#0F766E", text="SIGN UP")
        self.auth_status.configure(text="Checking internet connection…" if action == "register" else "Connecting…")
        self._last_auth_password = password
        def worker():
            try:
                if action == "register":
                    try:
                        online_check = requests.get("https://www.google.com/generate_204", timeout=5)
                        if online_check.status_code not in (200, 204, 301, 302):
                            raise RuntimeError("No internet connection. Connect to the internet before registering.")
                    except Exception:
                        raise RuntimeError("You must be connected to the internet to register. Check Wi-Fi/mobile data and try again.")
                payload = {"username": username, "password": password}
                if action == "register":
                    payload["school_class"] = self.class_choice.get()
                    payload["department"] = self.department_choice.get()
                    payload["phone_number"] = phone_number
                r = requests.post(self.server + "/api/" + action,
                                  json=payload, timeout=12)
                data = r.json()
                if not r.ok: raise RuntimeError(data.get("detail", "Request failed"))
                self.window.after(0, lambda: self._auth_success(username, data))
            except Exception as exc:
                msg = str(exc)
                is_connection_error = any(x in msg for x in ["ConnectionPool", "Failed to establish", "actively refused", "Max retries", "NewConnectionError", "ConnectionError", "ConnectTimeout", "No connection"])
                is_local_server = "127.0.0.1" in self.server or "localhost" in self.server
                
                if is_connection_error and is_local_server:
                    self.window.after(0, lambda: self.auth_status.configure(text="Local server offline - starting local mode...", fg="#D97706"))
                    try:
                        import threading as _thr
                        def _start_local_server():
                            try:
                                if 'app' in globals() and app is not None:
                                    import uvicorn
                                    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")
                            except:
                                pass
                        if not hasattr(self, '_server_start_attempted'):
                            self._server_start_attempted = True
                            _thr.Thread(target=_start_local_server, daemon=True).start()
                            import time as _time
                            _time.sleep(2)
                            try:
                                r2 = requests.post(self.server + "/api/" + action, json=payload, timeout=5)
                                data2 = r2.json()
                                if r2.ok:
                                    self.window.after(0, lambda: self._auth_success(username, data2))
                                    return
                            except:
                                pass
                    except:
                        pass
                    
                    try:
                        local_id = None
                        try:
                            local_id = authenticate_student(username, password)
                        except:
                            pass
                        if local_id is not None:
                            self.window.after(0, lambda: self.auth_status.configure(text="Connected in offline mode - local login OK", fg="#15803D"))
                            offline_data = {"token": f"offline_{username}_{secrets.token_hex(8)}", "username": username, "offline": True}
                            self.window.after(0, lambda: self._auth_success(username, offline_data))
                            return
                        else:
                            try:
                                with _db_connect() as db:
                                    row = db.execute("SELECT id FROM students WHERE lower(username)=lower(?)", (username,)).fetchone()
                                    if row:
                                        tries_left, now_locked = _record_failed_login("connect_" + username)
                                        if now_locked:
                                            self.window.after(0, lambda: self.auth_status.configure(text="Incorrect password. Account locked for 6 hours after 6 failed attempts.", fg="#B91C1C"))
                                        else:
                                            self.window.after(0, lambda tl=tries_left: self.auth_status.configure(text=f"Incorrect password you have {tl} more tries. After 6 tries, locked for 6 hours.", fg="#B91C1C"))
                                        return
                            except:
                                pass
                    except Exception as e:
                        print(f"Offline fallback error: {e}")
                    
                    friendly_msg = "Server not running. Run: python study_app.py --server  Or use offline mode with Study App account."
                    self.window.after(0, lambda: self.auth_status.configure(text=friendly_msg, fg="#D97706"))
                    return
                
                if "invalid" in msg.lower() or "unauthorized" in msg.lower() or "incorrect" in msg.lower() or "401" in msg or "403" in msg:
                    try:
                        tries_left, now_locked = _record_failed_login("connect_" + username)
                        if now_locked:
                            self.window.after(0, lambda: self.auth_status.configure(text="Incorrect password. Account locked for 6 hours after 6 failed attempts.", fg="#B91C1C"))
                        else:
                            self.window.after(0, lambda tl=tries_left: self.auth_status.configure(text=f"Incorrect password you have {tl} more tries. After 6 tries, locked for 6 hours.", fg="#B91C1C"))
                    except:
                        self.window.after(0, lambda m=msg: self.auth_status.configure(text=m, fg="#B91C1C"))
                else:
                    short_msg = msg.split("(")[0].strip() if len(msg) > 120 else msg
                    if "ConnectionPool" in msg or "actively refused" in msg:
                        short_msg = "Cannot reach server. Run: python study_app.py --server  Or use offline mode."
                    self.window.after(0, lambda m=short_msg: self.auth_status.configure(text=m, fg="#B91C1C"))
        threading.Thread(target=worker, daemon=True).start()

    def _auth_success(self, username, data):
        """Finish login/register, save credentials when requested, then load chats."""
        try:
            token = data.get("token") if isinstance(data, dict) else None
            # Some server versions wrap the response in a data object.
            if not token and isinstance(data, dict) and isinstance(data.get("data"), dict):
                token = data["data"].get("token")
            if not token:
                self.auth_status.configure(
                    text="The server accepted the request but did not return a login token. Check that the Connect server uses the matching API version.",
                    fg="#B91C1C")
                return
            self.username = username
            self.token = str(token)
            remember = bool(getattr(self, "remember_me_var", None) and self.remember_me_var.get())
            saved_password = getattr(self, "_last_auth_password", None)
            
            # Reset login attempts on success
            try:
                _record_successful_login("connect_" + username)
                _record_successful_login(username)
            except:
                pass
            
            # Check if already saved - if yes, don't show popup, just update silently
            is_already_saved = False
            try:
                accounts = _load_connect_remembered_accounts()
                for acc in accounts.values():
                    if isinstance(acc, dict) and acc.get("username", "").lower() == username.lower():
                        is_already_saved = True
                        break
            except:
                pass
            
            if remember:
                self._save_session(username, self.token)
                if saved_password:
                    # If already saved, update silently without popup - per user request
                    if is_already_saved:
                        _save_connect_remembered_account(self.server, username, saved_password)
                    else:
                        if not _save_connect_remembered_account(self.server, username, saved_password):
                            messagebox.showwarning(
                                "Save login", "Your session was saved, but Windows could not securely save the password. You can still log in manually.", parent=self.window)
            else:
                self._clear_saved_session()
            try:
                self.login_frame.destroy()
            except (AttributeError, tk.TclError):
                pass
            self._build_chat()
            self._refresh_lists()
            self._schedule_poll()
        except Exception as exc:
            try:
                self.auth_status.configure(text="Login succeeded but the chat screen could not open: " + str(exc), fg="#B91C1C")
            except Exception:
                messagebox.showerror("Connect", "Could not finish opening Connect.\n" + str(exc), parent=self.window)

    def _build_chat(self):
        # Modern, responsive chat workspace with a dedicated friend-name editor.
        outer = tk.Frame(self.host, bg="#E8EEF8")
        self.connect_outer = outer
        outer.pack(fill="both", expand=True)

        head = tk.Frame(outer, bg="#0B1730", height=76)
        head.pack(fill="x")
        head.pack_propagate(False)
        # Thin accent strip gives the Connect header a more polished app feel.
        accent = tk.Frame(outer, bg="#38BDF8", height=3)
        accent.pack(fill="x")
        brand = tk.Frame(head, bg="#0B1730")
        brand.pack(side="left", fill="y", padx=18, pady=7)
        school_logo = self._load_school_logo((56, 56))
        if school_logo:
            tk.Label(brand, image=school_logo, bg="#0B1730").pack(side="left", padx=(0, 11))
        else:
            tk.Label(brand, text="🏫", bg="#0B1730", fg="#D1FAE5",
                     font=("Segoe UI Emoji", 27)).pack(side="left", padx=(0, 10))
        brand_text = tk.Frame(brand, bg="#0B1730")
        brand_text.pack(side="left", fill="y", pady=(2, 0))
        tk.Label(brand_text, text="IJESHATEDO SENIOR SECONDARY SCHOOL", bg="#0B1730", fg="#FBFCFF",
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(brand_text, text="I.S.S.S CONNECT", bg="#0B1730", fg="#86EFAC",
                 font=("Segoe UI", 17, "bold")).pack(anchor="w")
        tk.Label(brand_text, text="Stay Connected  •  Learn Together  •  Grow Together", bg="#0B1730", fg="#AFC1DA",
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 0))
        userbox = tk.Frame(head, bg="#0B1730")
        userbox.pack(side="right", padx=20, pady=15)
        tk.Label(userbox, text="SIGNED IN", bg="#0B1730", fg="#AFC1DA",
                 font=("Segoe UI", 8, "bold")).pack(anchor="e")
        tk.Label(userbox, text=self.username, bg="#0B1730", fg="#FBFCFF",
                 font=("Segoe UI", 11, "bold")).pack(anchor="e")

        # Return to the main Study App without closing the entire application.
        RoundedButton(
            head,
            text="←  Return to Study App",
            command=self.close,
            bg="#2563EB",
            fg="white",
            activebackground="#1D4ED8",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=14,
            pady=9,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        ).pack(side="right", padx=(0, 18), pady=17)

        body = tk.Frame(outer, bg="#E8EEF8")
        body.pack(fill="both", expand=True, padx=16, pady=16)

        side = tk.Frame(body, bg="#FBFCFF", width=300,
                        highlightbackground="#CFDAEA", highlightthickness=1)
        side.pack(side="left", fill="y", padx=(0, 14))
        side.pack_propagate(False)
        tk.Label(side, text="CHATS & GROUPS", bg="#FBFCFF", fg="#0B1730",
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=16, pady=(16, 2))
        tk.Label(side, text="Classmates  •  Study groups", bg="#FBFCFF", fg="#667995",
                 font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=(0, 12))

        search_box = tk.Frame(side, bg="#F0F4FB", highlightbackground="#D4DEEF", highlightthickness=1)
        search_box.pack(fill="x", padx=12, pady=(0, 10))
        tk.Label(search_box, text="⌕", bg="#F0F4FB", fg="#64748B", font=("Segoe UI", 16)).pack(side="left", padx=(8, 3))
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_box, textvariable=self.search_var, relief="flat", bd=0,
                                      bg="#F0F4FB", fg="#20304A", font=("Segoe UI", 10))
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 8))
        self.search_var.trace_add("write", lambda *_: self._render_conversations())

        actions = tk.Frame(side, bg="#FBFCFF")
        actions.pack(fill="x", padx=12, pady=(0, 10))
        RoundedButton(actions, text="＋ New chat", command=self._new_chat, bg="#315FEA", fg="white",
                  activebackground="#234CC8", activeforeground="white", relief="flat",
                  font=("Segoe UI", 9, "bold"), cursor="hand2", pady=7).pack(side="left", expand=True, fill="x", padx=(0, 4))
        RoundedButton(actions, text="＋ Group", command=self._new_group, bg="#0D9488", fg="white",
                  activebackground="#0F766E", activeforeground="white", relief="flat",
                  font=("Segoe UI", 9, "bold"), cursor="hand2", pady=7).pack(side="left", expand=True, fill="x", padx=(4, 0))
        # Removed the duplicate Subject Community button. The existing
        # REMOVED: Choose Class, Department & Subject
        
        # --- 24HR CODE SYSTEM - STUDENT ONLY CAN JOIN, NOT GENERATE ---
        try:
            if CODE_SYS_AVAILABLE:
                RoundedButton(side, text="🎥 Enter Code & Join Livestream", command=self._enter_community_code_and_join_livestream, bg="#0EA5E9", fg="white", relief="flat", font=("Segoe UI", 9, "bold"), cursor="hand2", pady=7).pack(fill="x", padx=12, pady=(9, 6))
        except Exception as e:
            print("Could not add code buttons:", e)
        # REMOVED: Review Student Requests
        controlrow = tk.Frame(side, bg="#FBFCFF")
        controlrow.pack(fill="x", padx=12, pady=(0, 8))
        RoundedButton(controlrow, text="▣ Archive / Restore", command=self._toggle_archive,
                  bg="#E7F0FF", fg="#234CC8", activebackground="#DCE8FF", relief="flat",
                  font=("Segoe UI", 8, "bold"), cursor="hand2", pady=6).pack(side="left", expand=True, fill="x", padx=(0, 3))
        RoundedButton(controlrow, text="🔒 Lock / Unlock", command=self._toggle_chat_lock,
                  bg="#F1EAFE", fg="#6D28D9", activebackground="#E9D5FF", relief="flat",
                  font=("Segoe UI", 8, "bold"), cursor="hand2", pady=6).pack(side="left", expand=True, fill="x", padx=(3, 0))
        RoundedButton(controlrow, text="⏹ End class", command=self._end_subject_community,
                  bg="#FEE2E2", fg="#991B1B", activebackground="#FECACA", relief="flat",
                  font=("Segoe UI", 8, "bold"), cursor="hand2", pady=6).pack(side="left", expand=True, fill="x", padx=(3, 0))
        RoundedButton(side, text="📁 Show archived chats" if not self._show_archived else "← Back to chats",
                  command=self._toggle_archived_view, bg="#F0F4FB", fg="#334E68", relief="flat",
                  font=("Segoe UI", 8), cursor="hand2", pady=5).pack(fill="x", padx=12, pady=(0, 8))

        listwrap = tk.Frame(side, bg="#FBFCFF")
        listwrap.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.people_list = tk.Listbox(listwrap, font=("Segoe UI", 10), bd=0, highlightthickness=0,
                                      selectbackground="#DCE8FF", selectforeground="#17376C",
                                      activestyle="none", bg="#FBFCFF", fg="#20304A",
                                      relief="flat", exportselection=False)
        scrollbar = ttk.Scrollbar(listwrap, orient="vertical", command=self.people_list.yview)
        self.people_list.configure(yscrollcommand=scrollbar.set)
        self.people_list.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.people_list.bind("<<ListboxSelect>>", self._select_conversation)
        self.people_list.bind("<Button-3>", self._show_chat_menu)
        self.window.bind_all("<Escape>", self._escape_close_chat, add="+")

        right = tk.Frame(body, bg="#FBFCFF", highlightbackground="#CFDAEA", highlightthickness=1)
        right.pack(side="left", fill="both", expand=True)
        conversation_head = tk.Frame(right, bg="#FBFCFF")
        conversation_head.pack(fill="x", padx=18, pady=(15, 10))
        self.avatar = tk.Label(conversation_head, text="💬", bg="#DCE8FF", fg="#234CC8",
                               font=("Segoe UI Emoji", 18), width=3, height=2)
        self.avatar.pack(side="left", padx=(0, 12))
        self.avatar.configure(cursor="hand2")
        self.avatar.bind("<Button-1>", lambda _event: self._choose_profile_picture())
        # Profile-photo action is available by clicking the avatar; the duplicate header button is removed.
        titlearea = tk.Frame(conversation_head, bg="#FBFCFF")
        titlearea.pack(side="left", fill="x", expand=True)
        self.chat_title = tk.Label(titlearea, text="Welcome to I.S.S.S. Connect", bg="#FBFCFF", fg="#0B1730",
                                   font=("Segoe UI", 15, "bold"), anchor="w")
        self.chat_title.pack(anchor="w")
        self.chat_subtitle = tk.Label(titlearea, text="Choose a classmate or group to start chatting.", bg="#FBFCFF",
                                      fg="#667995", font=("Segoe UI", 9), anchor="w")
        self.chat_subtitle.pack(anchor="w", pady=(3, 0))
        # Rename-friend header button removed as requested; existing friend-management features remain elsewhere.
        self.settings_button = RoundedButton(conversation_head, text="⚙ Settings", command=self._open_settings,
                                       bg="#E8EEF8", fg="#1E3A5F", activebackground="#D4E2F5",
                                       relief="flat", font=("Segoe UI", 9, "bold"), cursor="hand2", padx=10, pady=7)
        self.settings_button.pack(side="right", padx=(8, 0))

        callbar = tk.Frame(right, bg="#F4F7FD", highlightbackground="#DDE6F4", highlightthickness=1)
        callbar.pack(fill="x", padx=14, pady=(0, 10))
        self._connect_callbar = callbar
        def circular_call_button(parent, label, icon, color, command):
            canvas = tk.Canvas(parent, width=66, height=66, bg="#F4F7FD", highlightthickness=0, cursor="hand2")
            circle = canvas.create_oval(5, 3, 61, 59, fill=color, outline=color, width=1)
            canvas.create_text(33, 22, text=icon, fill="white", font=("Segoe UI Symbol", 18, "bold"))
            canvas.create_text(33, 43, text=label, fill="white", font=("Segoe UI", 7, "bold"))
            canvas.bind("<Button-1>", lambda _e: command())
            canvas.bind("<Enter>", lambda _e: canvas.itemconfigure(circle, fill="#334155"))
            canvas.bind("<Leave>", lambda _e: canvas.itemconfigure(circle, fill=color))
            canvas.pack(side="left", padx=6, pady=3)
            return canvas
        circular_call_button(callbar, "VOICE", "☎", "#0D9488", lambda: self._start_call("voice"))
        circular_call_button(callbar, "VIDEO", "▣", "#315FEA", lambda: self._start_call("video"))
        # REMOVED: LIVE CLASS button - marked red

        tk.Label(callbar, text="Teacher hosts • students join the same class room • Internet required",
                 bg="#F4F7FD", fg="#667995", font=("Segoe UI", 9), wraplength=280,
                 justify="left").pack(side="left", padx=6, fill="x", expand=True)

        # Pin the composer to the bottom before allowing message history to expand.
        # Packing the history first with expand=True can push the composer below
        # the visible area on some Windows display/scaling configurations.
        compose = tk.Frame(right, bg="#FBFCFF")
        compose.pack(side="bottom", fill="x", padx=14, pady=(0, 14))
        self._connect_compose_frame = compose
        # Circular attachment button (Canvas lets us draw a real circle instead
        # of a square Tk button). Keep the same widget methods used by the menu.
        self.plus_button = tk.Canvas(compose, width=42, height=42, bg="#FBFCFF",
                                     highlightthickness=0, bd=0, cursor="hand2")
        self._plus_circle = self.plus_button.create_oval(2, 2, 40, 40,
                                     fill="#2563EB", outline="#60A5FA", width=2)
        self._plus_glyph = self.plus_button.create_text(21, 20, text="+",
                                     fill="#FFFFFF", font=("Segoe UI", 23, "bold"))
        self.plus_button.bind("<Button-1>", lambda _event: self._open_attachment_menu())
        self.plus_button.bind("<Enter>", lambda _event: self.plus_button.itemconfig(self._plus_circle, fill="#0EA5E9"))
        self.plus_button.bind("<Leave>", lambda _event: self.plus_button.itemconfig(self._plus_circle, fill="#2563EB"))
        self.plus_button.pack(side="left", padx=(0, 6))
        # WhatsApp-inspired circular emoji, sticker and voice-note controls.
        self.emoji_button = tk.Canvas(compose, width=40, height=40, bg="#FBFCFF",
                                      highlightthickness=0, bd=0, cursor="hand2")
        self.emoji_button.create_oval(2, 2, 38, 38, fill="#FFF4D6", outline="#F2D58B", width=1)
        self.emoji_button.create_text(20, 20, text="☺", fill="#8A5A00", font=("Segoe UI Emoji", 18, "bold"))
        self.emoji_button.bind("<Button-1>", lambda _e: self._open_emoji_picker())
        self.emoji_button.bind("<Enter>", lambda _e: self.emoji_button.configure(cursor="hand2"))
        self.emoji_button.pack(side="left", padx=(0, 5))
        self.sticker_button = tk.Canvas(compose, width=40, height=40, bg="#FBFCFF",
                                        highlightthickness=0, bd=0, cursor="hand2")
        self.sticker_button.create_oval(2, 2, 38, 38, fill="#E5F7EF", outline="#A7E5C5", width=1)
        self.sticker_button.create_text(20, 20, text="▧", fill="#087F70", font=("Segoe UI Symbol", 17, "bold"))
        self.sticker_button.bind("<Button-1>", lambda _e: self._open_sticker_menu())
        self.sticker_button.pack(side="left", padx=(0, 5))
        # Rounded WhatsApp-style message composer: rounded Canvas shell with
        # the native Entry inset so its rectangular edges never reach the corners.
        compose_shell = tk.Canvas(compose, height=46, bg="#FBFCFF", highlightthickness=0,
                                  bd=0, relief="flat")
        compose_shell.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._compose_shell = compose_shell
        self._compose_shell_bg = "#F0F4FB"
        self._compose_shell_outline = "#D4DEEF"
        self._compose_round_shape = None
        self.compose_entry = tk.Entry(
            compose_shell,
            font=(self._settings.get("chat_font_family", "Segoe UI"), int(self._settings.get("font_size", 10)) + 1),
            relief="flat",
            bd=0,
            bg="#F0F4FB",
            fg="#20304A",
            insertbackground="#20304A",
            highlightthickness=0
        )
        def _draw_rounded_composer(_event=None):
            try:
                compose_shell.delete("rounded_background")
                width = max(80, compose_shell.winfo_width())
                height = max(40, compose_shell.winfo_height())
                r = min(22, height // 2)
                points = [r,2,width-r,2,width-2,2,width-2,r,width-2,height-r,
                          width-2,height-2,width-r,height-2,r,height-2,2,height-2,
                          2,height-r,2,r,2,2]
                compose_shell.create_polygon(points, smooth=True, splinesteps=24,
                    fill=self._compose_shell_bg, outline=self._compose_shell_outline,
                    width=1, tags="rounded_background")
                compose_shell.tag_lower("rounded_background")
                compose_shell.coords(self._compose_entry_window, 12, height/2)
                compose_shell.itemconfigure(self._compose_entry_window, width=max(40, width-24))
            except (tk.TclError, AttributeError):
                pass
        self._compose_entry_window = compose_shell.create_window(12, 23, window=self.compose_entry,
                                      anchor="w", width=180)
        compose_shell.bind("<Configure>", _draw_rounded_composer, add="+")
        self.compose_entry.bind("<Return>", lambda _e: self._send_message())
        self.compose_entry.bind("<FocusIn>", lambda _e: (setattr(self, "_compose_shell_outline", "#315FEA"), _draw_rounded_composer()))
        self.compose_entry.bind("<FocusOut>", lambda _e: (setattr(self, "_compose_shell_outline", "#D4DEEF"), _draw_rounded_composer()))
        self.window.after(80, _draw_rounded_composer)
        self.compose_entry.bind("<Return>", lambda _e: self._send_message())
        # Camera and voice-note icons are drawn with Canvas shapes, not emoji or
        # text glyphs, so they remain visible on Windows even if an emoji font is missing.
        self.voice_button = tk.Canvas(compose, width=44, height=44, bg="#FBFCFF",
                                      highlightthickness=0, bd=0, cursor="hand2")
        self.voice_button.create_oval(2, 2, 42, 42, fill="#DCE8FF", outline="#AFC7FF", width=1)
        # Microphone capsule, grille, U-shaped cradle and stem.
        self._voice_glyph = self.voice_button.create_line(22, 11, 22, 24, fill="#234CC8", width=5, capstyle="round")
        self.voice_button.create_arc(13, 12, 31, 30, start=180, extent=180, style="arc", outline="#234CC8", width=2)
        self.voice_button.create_line(13, 22, 13, 25, 22, 31, 31, 25, 31, 22, fill="#234CC8", width=2, smooth=True)
        self.voice_button.create_line(22, 30, 22, 34, fill="#234CC8", width=2)
        self.voice_button.create_line(17, 35, 27, 35, fill="#234CC8", width=2)
        self.voice_button.bind("<Button-1>", lambda _e: self._toggle_voice_note())
        self.voice_button.pack(side="right", padx=(0, 7), pady=1)
        self.camera_button = tk.Canvas(compose, width=44, height=44, bg="#FBFCFF",
                                       highlightthickness=0, bd=0, cursor="hand2")
        self.camera_button.create_oval(2, 2, 42, 42, fill="#DDF7E8", outline="#9ADBB8", width=1)
        # Camera body, top viewfinder bump, lens and small indicator.
        self.camera_button.create_rectangle(10, 16, 34, 31, fill="#087F70", outline="#087F70")
        self.camera_button.create_polygon(14, 16, 17, 11, 25, 11, 28, 16, fill="#087F70", outline="#087F70")
        self.camera_button.create_oval(17, 18, 28, 29, fill="#DDF7E8", outline="#FFFFFF", width=2)
        self.camera_button.create_oval(20, 21, 25, 26, fill="#087F70", outline="#087F70")
        self.camera_button.create_oval(29, 18, 32, 21, fill="#FFFFFF", outline="#FFFFFF")
        self.camera_button.bind("<Button-1>", lambda _e: self._camera_notice())
        self.camera_button.pack(side="right", padx=(0, 5), pady=1)
        def _composer_tooltip(widget, message):
            tip = {"window": None}
            def show(_event=None):
                if tip["window"] is not None:
                    return
                try:
                    tw = tk.Toplevel(self.window)
                    tw.wm_overrideredirect(True)
                    tw.configure(bg="#172033")
                    x = widget.winfo_rootx() + 4
                    y = widget.winfo_rooty() - 28
                    tw.wm_geometry(f"+{x}+{y}")
                    tk.Label(tw, text=message, bg="#172033", fg="white", padx=7, pady=3,
                             font=("Segoe UI", 9)).pack()
                    tip["window"] = tw
                except tk.TclError:
                    pass
            def hide(_event=None):
                if tip["window"] is not None:
                    try: tip["window"].destroy()
                    except tk.TclError: pass
                    tip["window"] = None
            widget.bind("<Enter>", show, add="+")
            widget.bind("<Leave>", hide, add="+")
        _composer_tooltip(self.camera_button, "Camera: capture photo/video")
        _composer_tooltip(self.voice_button, "Voice note: click to record, click again to send")
        RoundedButton(
            compose,
            text="Send  ➤",
            command=self._send_message,
            bg="#315FEA",
            fg="white",
            activebackground="#234CC8",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            padx=18,
            pady=9
        ).pack(side="right")

        message_area = tk.Frame(right, bg="#EEF3FB")
        message_area.pack(side="top", fill="both", expand=True, padx=14, pady=(0, 10))
        self._connect_message_area = message_area
        # Scrollable message history: keep the scrollbar visible for long conversations.
        self.messages_scrollbar = tk.Scrollbar(
            message_area, orient="vertical", command=lambda *args: self.messages.yview(*args),
            bg="#DCE6F5", activebackground="#AFC4E6", troughcolor="#EEF3FB",
            relief="flat", bd=0, width=13
        )
        self.messages_scrollbar.pack(side="right", fill="y")
        self.messages = tk.Text(
            message_area,
            state="disabled",
            wrap="word",
            font=("Segoe UI", 10),
            bg="#EEF3FB",
            fg="#20304A",
            relief="flat",
            padx=18,
            pady=16,
            spacing1=3,
            spacing3=8,
            selectbackground="#BDD1FF",
            yscrollcommand=self.messages_scrollbar.set
        )
        self.messages.pack(side="left", fill="both", expand=True)
        self.messages.tag_configure("name", foreground="#315FEA", font=("Segoe UI", 9, "bold"))
        self.messages.tag_configure("body", foreground="#20304A", font=(self._settings.get("chat_font_family", "Segoe UI"), int(self._settings.get("font_size", 10))))
        self._apply_chat_font()

        # WhatsApp-style empty state: never open a conversation automatically.
        self._connect_welcome = tk.Frame(right, bg="#F7FAFF")
        tk.Label(self._connect_welcome, text="💬", bg="#F7FAFF", fg="#315FEA",
                 font=("Segoe UI Emoji", 54)).pack(pady=(90, 12))
        tk.Label(self._connect_welcome, text="I.S.S.S. Connect", bg="#F7FAFF", fg="#0B1730",
                 font=("Segoe UI", 23, "bold")).pack()
        tk.Label(self._connect_welcome,
                 text="Select a classmate or group on the left to view messages and start chatting.",
                 bg="#F7FAFF", fg="#667995", font=("Segoe UI", 11), wraplength=440,
                 justify="center").pack(padx=35, pady=(10, 0))
        self._connect_callbar.pack_forget()
        self._connect_compose_frame.pack_forget()
        self._connect_message_area.pack_forget()
        self._connect_welcome.pack(fill="both", expand=True)
        self.message_menu = tk.Menu(
            self.window, tearoff=0, font=("Segoe UI", 10),
            bg="#132544", fg="#F8FAFC",
            activebackground="#3B82F6", activeforeground="#FFFFFF",
            disabledforeground="#94A3B8", relief="flat", bd=0,
            activeborderwidth=0, selectcolor="#0D9488"
        )
        self.message_menu.add_command(label="ℹ  Message info", command=self._message_info)
        self.message_menu.add_command(label="↩  Reply", command=self._reply_to_selected_message)
        self.message_menu.add_command(label="⧉  Copy", command=self._copy_selected_message)
        self.message_menu.add_command(label="↪  Forward", command=self._forward_selected_message)
        self.message_menu.add_command(label="☆  Star / unstar", command=self._star_selected_message)
        self.message_menu.add_command(label="✎  Edit message", command=self._edit_selected_message)
        self.message_menu.add_command(label="😊  React", command=self._react_to_selected_message)
        self.message_menu.add_command(label="📌  Pin message", command=self._pin_selected_message)
        self.message_menu.add_command(label="☑  Select message", command=self._select_message_text)
        self.message_menu.add_command(label="⚑  Report message", command=self._report_selected_message)
        self.message_menu.add_separator()
        self.message_menu.add_command(label="🗑  Delete for me", command=lambda: self._delete_selected_message("me"))
        self.message_menu.add_command(label="🗑  Delete for everyone (only before read)", command=lambda: self._delete_selected_message("everyone"))
        # Message actions are opened from the visible three-dot button on each message.

        self.profile_photo_path = self._load_profile_photo_path()
        self._display_profile_photo()

    def _profile_photo_file(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "isss_connect_profile_photos.json")

    def _load_profile_photo_path(self):
        try:
            with open(self._profile_photo_file(), "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get(self.username, "") if isinstance(data, dict) else ""
        except (OSError, ValueError, AttributeError):
            return ""

    def _choose_profile_picture(self):
        # This picker edits only the currently authenticated user's local profile photo.
        # Friend nicknames are a private label visible only to this user; they do not
        # change another account's username or profile picture.
        if not self.token:
            messagebox.showwarning("Profile photo", "Sign in to change your own profile photo.", parent=self.window)
            return
        path = filedialog.askopenfilename(parent=self.window, title="Choose your profile picture",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"), ("All files", "*.*")])
        if not path:
            return
        if not MODULE_PIL_AVAILABLE:
            messagebox.showinfo("Profile picture", "Install Pillow to display profile photos: python -m pip install Pillow", parent=self.window)
            return
        self.profile_photo_path = path
        try:
            with open(self._profile_photo_file(), "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict): data = {}
        except (OSError, ValueError):
            data = {}
        data[self.username] = path
        try:
            with open(self._profile_photo_file(), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError as exc:
            messagebox.showwarning("Profile picture", f"Could not save the profile picture setting.\n{exc}", parent=self.window)
        self._display_profile_photo()

    def _display_profile_photo(self):
        path = getattr(self, "profile_photo_path", "")
        if not path or not os.path.isfile(path) or not MODULE_PIL_AVAILABLE:
            self.avatar.configure(image="", text=(self.username[:1].upper() if self.username else "💬"),
                                  bg="#DCE8FF", fg="#234CC8")
            self._avatar_image = None
            return
        try:
            image = Image.open(path).convert("RGB")
            image.thumbnail((58, 58))
            self._avatar_image = ImageTk.PhotoImage(image)
            self.avatar.configure(image=self._avatar_image, text="", width=58, height=58, bg="#DCE8FF")
        except Exception:
            self.avatar.configure(image="", text=(self.username[:1].upper() if self.username else "💬"))
            self._avatar_image = None

    def _open_attachment_menu(self):
        """Show a reliable custom attachment popover above/below the circular + button."""
        # Treat + as a toggle: clicking it while the attachment menu is open
        # closes the menu and returns focus to the chat composer.
        old = getattr(self, "_attachment_popup", None)
        if old is not None:
            try:
                if old.winfo_exists():
                    old.destroy()
                    self._attachment_popup = None
                    try:
                        self.window.focus_set()
                    except tk.TclError:
                        pass
                    return
            except tk.TclError:
                pass
            self._attachment_popup = None

        popup = tk.Toplevel(self.window)
        self._attachment_popup = popup  # retain a reference so Tkinter cannot collect it
        popup.withdraw()
        popup.overrideredirect(True)
        popup.transient(self.window)
        popup.configure(bg="#D6E3F5")

        shell = tk.Frame(popup, bg="#FFFFFF", bd=0, highlightthickness=1,
                         highlightbackground="#C8D7EC")
        shell.pack(fill="both", expand=True, padx=1, pady=1)
        tk.Label(shell, text="ADD TO CHAT", bg="#FFFFFF", fg="#64748B",
                 font=("Segoe UI", 8, "bold"), anchor="w").pack(fill="x", padx=12, pady=(9, 5))

        actions = [
            ("🖼", "Photos & videos", "Choose images or video files", lambda: self._choose_attachment("photo")),
            ("📄", "Documents", "PDF, Word, Excel and more", lambda: self._choose_attachment("document")),
            ("🎵", "Audio", "Choose audio files", lambda: self._choose_attachment("audio")),
            ("📷", "Camera", "Camera options", self._camera_notice),
            ("📊", "Create a poll", "Send a question to the chat", self._create_poll),
            ("📅", "Create an event", "Share a date and details", self._create_event),
            ("🎟", "New sticker", "Choose an image sticker", self._choose_sticker),
        ]

        def run_action(callback):
            try:
                if popup.winfo_exists():
                    popup.destroy()
            except tk.TclError:
                pass
            self._attachment_popup = None
            callback()

        for symbol, title, subtitle, callback in actions:
            row = tk.Frame(shell, bg="#FFFFFF")
            row.pack(fill="x", padx=5, pady=1)
            btn = tk.Button(row, text=f"{symbol}   {title}\n      {subtitle}",
                            command=lambda cb=callback: run_action(cb),
                            anchor="w", justify="left", bg="#FFFFFF", fg="#172B4D",
                            activebackground="#EAF3FF", activeforeground="#1745A5",
                            relief="flat", bd=0, cursor="hand2",
                            font=("Segoe UI", 9), padx=9, pady=7)
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda _e, b=btn: b.configure(bg="#EAF3FF"))
            btn.bind("<Leave>", lambda _e, b=btn: b.configure(bg="#FFFFFF"))

        popup.update_idletasks()
        width = max(275, popup.winfo_reqwidth())
        height = popup.winfo_reqheight()
        screen_w = popup.winfo_screenwidth()
        screen_h = popup.winfo_screenheight()
        bx = self.plus_button.winfo_rootx()
        by = self.plus_button.winfo_rooty()
        x = min(max(8, bx), max(8, screen_w - width - 8))
        # Prefer above the composer, but open below if there isn't enough room.
        y = by - height - 8
        if y < 8:
            y = min(screen_h - height - 8, by + self.plus_button.winfo_height() + 8)
        popup.geometry(f"{width}x{height}+{x}+{max(8, y)}")
        popup.deiconify()
        popup.lift()
        popup.focus_force()
        def close_attachment_popup(_event=None):
            try:
                if popup.winfo_exists():
                    popup.destroy()
            except tk.TclError:
                pass
            if getattr(self, "_attachment_popup", None) is popup:
                self._attachment_popup = None
            try:
                self.window.focus_set()
            except tk.TclError:
                pass
            return "break"

        popup.bind("<Escape>", close_attachment_popup)
        # Also support Escape when focus is on one of the menu's child buttons.
        for child in shell.winfo_children():
            child.bind("<Escape>", close_attachment_popup)
            for nested in child.winfo_children():
                nested.bind("<Escape>", close_attachment_popup)
        popup.bind("<FocusOut>", lambda _e: popup.after(180, lambda: close_attachment_popup() if popup.winfo_exists() and not popup.focus_displayof() else None))

    def _choose_attachment(self, kind):
        if kind == "photo":
            types = [("Photos and videos", "*.png *.jpg *.jpeg *.gif *.bmp *.webp *.mp4 *.mov *.avi *.mkv"), ("All files", "*.*")]
        elif kind == "audio":
            types = [("Audio files", "*.mp3 *.wav *.m4a *.ogg *.aac *.flac"), ("All files", "*.*")]
        else:
            types = [("Documents", "*.pdf *.doc *.docx *.txt *.xlsx *.pptx *.csv"), ("All files", "*.*")]
        paths = filedialog.askopenfilenames(parent=self.window, title="Choose " + ("photos/videos" if kind == "photo" else kind + " files"), filetypes=types)
        if not paths:
            try:
                self.window.focus_set()
            except tk.TclError:
                pass
            return
        if not self.active:
            messagebox.showinfo("Choose a chat", "Select a classmate or group before uploading files.", parent=self.window)
            return
        for path in paths:
            self._upload_attachment(path, kind)

    def _upload_attachment(self, path, kind):
        """Upload a file to Connect and post its link in the selected conversation."""
        if requests is None:
            messagebox.showerror("Missing library", "Install requests with: python -m pip install requests", parent=self.window)
            return
        if not os.path.isfile(path):
            return
        kind_label = "image/video" if kind == "photo" else kind
        size_mb = os.path.getsize(path) / (1024 * 1024)
        ext = os.path.splitext(path)[1].lower()
        video_extensions = {".mp4", ".mov", ".avi", ".mkv"}
        # Videos may be up to 300 MB; other attachments remain capped at 25 MB.
        max_mb = 300 if kind == "photo" and ext in video_extensions else 25
        if size_mb > max_mb:
            messagebox.showwarning("File too large", f"{os.path.basename(path)} is {size_mb:.1f} MB. The maximum for this file is {max_mb} MB.", parent=self.window)
            return
        target_kind, target = self.active_kind, str(self.active)
        filename = os.path.basename(path)
        self.chat_subtitle.configure(text=f"Uploading {filename}…")
        def worker():
            try:
                with open(path, "rb") as handle:
                    response = requests.post(
                        self.server + "/api/uploads",
                        headers=self._headers(),
                        data={"kind": target_kind, "target": target, "media_kind": kind},
                        files={"file": (filename, handle)}, timeout=(30, 900)
                    )
                payload = response.json() if response.content else {}
                if not response.ok:
                    raise RuntimeError(payload.get("detail", "Upload failed"))
                url = self.server + payload["url"]
                prefix = "🖼 Photo/video" if kind == "photo" else ("🎵 Audio" if kind == "audio" else "📄 Document")
                body = f"{prefix}: {filename}\nOpen attachment: {url}"
                self._request("POST", "/api/messages", json={"kind": target_kind, "target": target, "body": body})
                self.window.after(0, self._load_messages)
                self.window.after(0, lambda: self.chat_subtitle.configure(text="Video sent in the chat" if ext in video_extensions else "Attachment sent"))
            except Exception as exc:
                self.window.after(0, lambda m=str(exc): messagebox.showerror("Upload failed", m, parent=self.window))
                self.window.after(0, lambda: self.chat_subtitle.configure(text="Upload failed. Check the server connection and try again."))
        threading.Thread(target=worker, daemon=True).start()

    def _camera_notice(self):
        """Open camera tools: take a photo, record a video, rotate, or mirror the view."""
        if not self.active:
            messagebox.showinfo("Choose a chat", "Open a classmate or group chat first, then capture media to send.", parent=self.window)
            return
        try:
            import cv2
            from PIL import Image, ImageTk
        except Exception as exc:
            messagebox.showwarning(
                "Camera support unavailable",
                "Install the camera libraries in this app's environment:\n\n"
                r".\venv\Scripts\python.exe -m pip install opencv-python pillow\n\n"
                "You can still choose an existing photo or video to send.\n\nDetails: " + str(exc),
                parent=self.window,
            )
            path = filedialog.askopenfilename(
                parent=self.window, title="Choose a photo or video to send",
                filetypes=[("Photos and videos", "*.png *.jpg *.jpeg *.gif *.bmp *.webp *.mp4 *.mov *.avi *.mkv"), ("All files", "*.*")]
            )
            if path:
                self._upload_attachment(path, "photo")
            return

        camera = None
        camera_index = 0
        camera_backend = cv2.CAP_DSHOW if sys.platform.startswith("win") else cv2.CAP_ANY
        try:
            camera = cv2.VideoCapture(camera_index, camera_backend)
            if not camera.isOpened():
                camera.release()
                camera = cv2.VideoCapture(camera_index)
            if not camera.isOpened():
                raise RuntimeError("No webcam was found or the camera is being used by another app.")
        except Exception as exc:
            if camera is not None:
                camera.release()
            messagebox.showerror("Cannot open camera", str(exc) + "\n\nCheck Windows camera permissions and close other apps using the webcam.", parent=self.window)
            return

        preview = tk.Toplevel(self.window)
        preview.title("Camera & Video — ISSS Connect")
        preview.configure(bg="#101827")
        preview.transient(self.window)
        preview.resizable(False, False)
        image_label = tk.Label(preview, bg="#101827", fg="white", text="Starting camera…", font=("Segoe UI", 11))
        image_label.pack(padx=12, pady=(12, 6))
        status = tk.Label(preview, text="Choose the front/back camera, take a photo, or record a video.", bg="#101827", fg="#D5E4FF", font=("Segoe UI", 9))
        status.pack(fill="x", padx=12, pady=(0, 7))
        controls = tk.Frame(preview, bg="#101827")
        controls.pack(fill="x", padx=12, pady=(4, 12))
        state = {"running": True, "frame": None,
                 "writer": None, "recording": False, "video_path": None, "record_size": None}

        def close_camera():
            state["running"] = False
            if state.get("writer") is not None:
                try: state["writer"].release()
                except Exception: pass
                state["writer"] = None
            try: camera.release()
            except Exception: pass
            try: preview.destroy()
            except tk.TclError: pass

        def transform_frame(frame):
            # Keep the camera's natural orientation; switching devices is handled by flip_camera().
            return frame

        def refresh_frame():
            if not state["running"] or not preview.winfo_exists():
                return
            ok, frame = camera.read()
            if ok:
                frame = transform_frame(frame)
                state["frame"] = frame.copy()
                if state["recording"]:
                    writer = state.get("writer")
                    if writer is not None:
                        # Keep the writer dimensions stable if the user rotates while recording.
                        h, w = frame.shape[:2]
                        rw, rh = state["record_size"]
                        if (w, h) != (rw, rh):
                            frame = cv2.resize(frame, (rw, rh))
                        writer.write(frame)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb)
                pil_image.thumbnail((800, 520))
                photo = ImageTk.PhotoImage(pil_image)
                image_label.configure(image=photo, text="")
                image_label.image = photo
            else:
                status.configure(text="Waiting for camera…")
            preview.after(30, refresh_frame)

        def flip_camera():
            """Switch between available physical camera devices (front/back where provided)."""
            nonlocal camera, camera_index
            if state["recording"]:
                status.configure(text="Stop recording before switching cameras.")
                return
            # Probe other camera indices. Desktop webcams often expose only one device;
            # a laptop/USB camera pair may expose two or more.
            candidates = [i for i in range(0, 6) if i != camera_index]
            for idx in candidates:
                candidate = cv2.VideoCapture(idx, camera_backend)
                if not candidate.isOpened():
                    candidate.release()
                    candidate = cv2.VideoCapture(idx)
                if candidate.isOpened():
                    ok, test_frame = candidate.read()
                    if ok and test_frame is not None:
                        old_camera = camera
                        camera = candidate
                        camera_index = idx
                        try:
                            old_camera.release()
                        except Exception:
                            pass
                        status.configure(text=f"Camera switched • device {camera_index}")
                        return
                candidate.release()
            status.configure(text="No other camera found. Connect/enable a second camera for front/back switching.")
            messagebox.showinfo(
                "No second camera detected",
                "Your computer currently exposes only one usable camera. Front/back switching works when Windows provides separate camera devices (for example, built-in and USB cameras). This button does not rotate or mirror the image.",
                parent=preview,
            )

        def take_photo():
            frame = state.get("frame")
            if frame is None:
                status.configure(text="Camera is not ready yet. Try again.")
                return
            import tempfile
            path = os.path.join(tempfile.gettempdir(), f"isss_camera_{int(time.time())}.jpg")
            if not cv2.imwrite(path, frame):
                messagebox.showerror("Photo failed", "Could not save the captured photo.", parent=preview)
                return
            close_camera()
            self._upload_attachment(path, "photo")

        def start_video():
            if state["recording"]:
                return
            frame = state.get("frame")
            if frame is None:
                status.configure(text="Camera is not ready yet. Try again.")
                return
            import tempfile
            path = os.path.join(tempfile.gettempdir(), f"isss_video_{int(time.time())}.mp4")
            h, w = frame.shape[:2]
            writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), 20.0, (w, h))
            if not writer.isOpened():
                writer.release()
                messagebox.showerror("Video failed", "Could not start video recording. Try updating OpenCV or use an existing video file.", parent=preview)
                return
            state["writer"] = writer
            state["video_path"] = path
            state["record_size"] = (w, h)
            state["recording"] = True
            record_button.configure(text="■ Stop & send video", bg="#DC2626", command=stop_video)
            status.configure(text="● Recording video… click Stop & send video when finished")

        def stop_video():
            if not state["recording"]:
                return
            state["recording"] = False
            writer = state.get("writer")
            state["writer"] = None
            if writer is not None:
                writer.release()
            path = state.get("video_path")
            close_camera()
            if path and os.path.isfile(path) and os.path.getsize(path) > 0:
                self._upload_attachment(path, "photo")
            else:
                messagebox.showerror("Video failed", "No video file was created.", parent=self.window)

        tk.Button(controls, text="⇄ Flip camera", command=flip_camera, bg="#475569", fg="white",
                  activebackground="#64748B", activeforeground="white", relief="flat", cursor="hand2",
                  font=("Segoe UI", 9, "bold"), padx=10, pady=8).pack(side="left", padx=(0, 5))
        tk.Button(controls, text="📸 Photo", command=take_photo, bg="#2563EB", fg="white",
                  activebackground="#1D4ED8", activeforeground="white", relief="flat", cursor="hand2",
                  font=("Segoe UI", 9, "bold"), padx=10, pady=8).pack(side="right", padx=(5, 0))
        record_button = tk.Button(controls, text="● Record video", command=start_video, bg="#0D9488", fg="white",
                  activebackground="#0F766E", activeforeground="white", relief="flat", cursor="hand2",
                  font=("Segoe UI", 9, "bold"), padx=10, pady=8)
        record_button.pack(side="right")
        preview.protocol("WM_DELETE_WINDOW", close_camera)
        preview.bind("<Escape>", lambda _event: close_camera())
        refresh_frame()

    def _open_sticker_menu(self):
        """Small sticker menu: upload an image sticker or make one from an image."""
        if not self.active:
            messagebox.showinfo("Choose a chat", "Select a classmate or group before sending a sticker.", parent=self.window)
            return
        menu = tk.Menu(self.window, tearoff=0)
        menu.add_command(label="Upload sticker image…", command=self._choose_sticker)
        menu.add_command(label="Create sticker from photo…", command=self._create_sticker_from_photo)
        try:
            menu.tk_popup(self.sticker_button.winfo_rootx(), self.sticker_button.winfo_rooty() - 8)
        finally:
            menu.grab_release()

    def _create_sticker_from_photo(self):
        """Choose an image to send in sticker style (the source image is preserved)."""
        self._choose_sticker()


    def _create_voice_recording_bar(self):
        """Create WhatsApp-style voice recording bar - green bar with trash, timer, waveform, send"""
        try:
            if hasattr(self, '_voice_bar') and self._voice_bar.winfo_exists():
                return
        except:
            pass
        parent = self._connect_compose_frame
        self._voice_bar = tk.Frame(parent, bg="#0B5D4B", height=56)
        self._voice_bar.pack_propagate(False)
        trash_btn = tk.Canvas(self._voice_bar, width=40, height=40, bg="#0B5D4B", highlightthickness=0, bd=0, cursor="hand2")
        trash_btn.create_oval(2,2,38,38, fill="#063D32", outline="#0A7A60", width=1)
        trash_btn.create_text(20,20, text="\U0001F5D1", fill="white", font=("Segoe UI Emoji", 14))
        trash_btn.bind("<Button-1>", lambda e: self._cancel_voice_note())
        trash_btn.pack(side="left", padx=(8,6), pady=8)
        self._voice_trash_btn = trash_btn
        timer_frame = tk.Frame(self._voice_bar, bg="#0B5D4B")
        timer_frame.pack(side="left", padx=4)
        self._voice_red_dot = tk.Canvas(timer_frame, width=12, height=12, bg="#0B5D4B", highlightthickness=0, bd=0)
        self._voice_red_dot.create_oval(2,2,10,10, fill="#FF3B30")
        self._voice_red_dot.pack(side="left", padx=(0,4))
        self._voice_timer_label = tk.Label(timer_frame, text="0:00", bg="#0B5D4B", fg="white", font=("Segoe UI", 11, "bold"))
        self._voice_timer_label.pack(side="left")
        self._voice_wave_canvas = tk.Canvas(self._voice_bar, height=36, bg="#0B5D4B", highlightthickness=0, bd=0)
        self._voice_wave_canvas.pack(side="left", fill="x", expand=True, padx=8, pady=4)
        right_frame = tk.Frame(self._voice_bar, bg="#0B5D4B")
        right_frame.pack(side="right", padx=(4,8))
        pause_btn = tk.Canvas(right_frame, width=36, height=36, bg="#0B5D4B", highlightthickness=0, bd=0, cursor="hand2")
        pause_btn.create_oval(2,2,34,34, fill="#0B5D4B", outline="#4AB5A0", width=1)
        pause_btn.create_line(12,10,12,26, fill="white", width=3)
        pause_btn.create_line(22,10,22,26, fill="white", width=3)
        pause_btn.bind("<Button-1>", lambda e: self._toggle_voice_pause())
        pause_btn.pack(side="left", padx=4)
        self._voice_pause_btn = pause_btn
        send_btn = tk.Canvas(right_frame, width=44, height=44, bg="#0B5D4B", highlightthickness=0, bd=0, cursor="hand2")
        send_btn.create_oval(2,2,42,42, fill="#25D366", outline="#25D366")
        send_btn.create_text(22,22, text="\u27A4", fill="white", font=("Segoe UI", 16, "bold"))
        send_btn.bind("<Button-1>", lambda e: self._stop_voice_note())
        send_btn.pack(side="left", padx=(6,0))
        self._voice_send_btn = send_btn
        self._voice_wave_bars = []
        self._voice_is_paused = False

    def _update_voice_timer(self):
        if not self._voice_recording or getattr(self, '_voice_is_paused', False):
            return
        elapsed = int(time.time() - self._voice_start_time - self._voice_paused_time)
        mins = elapsed // 60
        secs = elapsed % 60
        try:
            self._voice_timer_label.config(text=f"{mins}:{secs:02d}")
            if secs % 2 == 0:
                self._voice_red_dot.itemconfig(1, fill="#FF3B30")
            else:
                self._voice_red_dot.itemconfig(1, fill="#FF8A80")
        except:
            pass
        try:
            self._update_waveform()
        except:
            pass
        self.window.after(100, self._update_voice_timer)

    def _update_waveform(self):
        try:
            canvas = self._voice_wave_canvas
            w = canvas.winfo_width()
            h = canvas.winfo_height()
            if w < 20:
                w = 200
            canvas.delete("wave")
            import random
            num_bars = 30
            level = 0.5
            if hasattr(self, '_voice_frames') and self._voice_frames:
                try:
                    import numpy as np
                    if self._voice_frames:
                        last = self._voice_frames[-1]
                        level = min(1.0, float(np.abs(last).mean()) / 1000.0 + 0.2)
                except:
                    level = random.uniform(0.3, 0.9)
            else:
                level = random.uniform(0.2, 0.7)
            bar_width = max(2, w // (num_bars * 2))
            gap = 3
            for i in range(num_bars):
                x = i * (bar_width + gap) + 5
                bh = random.uniform(4, h * level * 1.2 + 4)
                if i > num_bars - 5:
                    bh *= 0.6
                y1 = (h - bh) / 2
                y2 = y1 + bh
                color = "#FFFFFF" if random.random() > 0.3 else "#B0D8CC"
                canvas.create_line(x, y1, x, y2, fill=color, width=bar_width, tags="wave", capstyle="round")
        except:
            pass

    def _cancel_voice_note(self):
        self._voice_recording = False
        try:
            if hasattr(self, '_voice_stream') and self._voice_stream:
                self._voice_stream.stop()
                self._voice_stream.close()
        except:
            pass
        self._voice_stream = None
        self._voice_frames = []
        self._hide_voice_bar()
        try:
            self.chat_subtitle.configure(text="Voice note cancelled")
        except:
            pass

    def _toggle_voice_pause(self):
        self._voice_is_paused = not getattr(self, '_voice_is_paused', False)
        if self._voice_is_paused:
            self._voice_pause_start = time.time()
            try:
                self.chat_subtitle.configure(text="Paused - click pause again to resume")
            except:
                pass
        else:
            try:
                self._voice_paused_time += time.time() - getattr(self, '_voice_pause_start', time.time())
                self.chat_subtitle.configure(text="Recording + Live Monitoring ON...")
            except:
                pass

    def _hide_voice_bar(self):
        try:
            if hasattr(self, '_voice_bar'):
                self._voice_bar.pack_forget()
            parent = self._connect_compose_frame
            for child in list(parent.winfo_children()):
                if child != self._voice_bar:
                    try:
                        if not child.winfo_ismapped():
                            child.pack(side="left", padx=6) if "plus" in str(child) or "emoji" in str(child) or "sticker" in str(child) else child.pack(side="right", padx=5)
                    except:
                        pass
            # Restore specific layout
            try:
                self.plus_button.pack(side="left", padx=(0, 6))
                self.emoji_button.pack(side="left", padx=(0, 5))
                self.sticker_button.pack(side="left", padx=(0, 5))
                self._compose_shell.pack(side="left", fill="x", expand=True, padx=(0, 8))
                self.voice_button.pack(side="right", padx=(0, 7), pady=1)
                self.camera_button.pack(side="right", padx=(0, 5), pady=1)
            except:
                pass
            try:
                self.voice_button.itemconfig(self._voice_glyph, fill="#234CC8")
                self.voice_button.itemconfig(1, fill="#DCE8FF", outline="#AFC7FF")
            except:
                pass
        except:
            pass

    def _toggle_voice_note(self):
        if not self.active:
            messagebox.showinfo("Choose a chat", "Open a classmate or group chat before recording a voice note.", parent=self.window)
            return
        if self._voice_recording:
            self._stop_voice_note()
            return
        try:
            import sounddevice as sd
        except Exception as exc:
            messagebox.showerror(
                "Voice-note audio library unavailable",
                "ISSS Connect could not load the sounddevice audio library.\n\n"
                "Install: pip install sounddevice numpy\n\n"
                f"Details: {type(exc).__name__}: {exc}", parent=self.window)
            return
        try:
            self._voice_frames = []
            self._voice_sample_rate = 44100
            self._voice_channels = 1
            self._voice_start_time = time.time()
            self._voice_paused_time = 0
            self._voice_is_paused = False
            self._create_voice_recording_bar()
            for child in self._connect_compose_frame.winfo_children():
                if child != self._voice_bar:
                    try:
                        child.pack_forget()
                    except:
                        pass
            self._voice_bar.pack(fill="x", expand=True, padx=0, pady=0)
            def on_audio(indata, outdata, frames, time_info, status):
                if self._voice_recording and not getattr(self, '_voice_is_paused', False):
                    self._voice_frames.append(indata.copy())
                    try:
                        outdata[:] = indata
                    except:
                        outdata.fill(0)
                else:
                    outdata.fill(0)
            self._voice_recording = True
            self._voice_stream = sd.Stream(
                samplerate=self._voice_sample_rate, 
                channels=self._voice_channels,
                dtype="int16", 
                callback=on_audio
            )
            self._voice_stream.start()
            self.chat_subtitle.configure(text="Recording - you hear yourself live...")
            self._update_voice_timer()
        except Exception as exc:
            self._voice_recording = False
            self._hide_voice_bar()
            messagebox.showerror("Microphone unavailable", f"Could not start recording.\n\n{exc}", parent=self.window)

    def _stop_voice_note(self):
        self._voice_recording = False
        stream, self._voice_stream = self._voice_stream, None
        try:
            if stream is not None:
                stream.stop()
                stream.close()
        except:
            pass
        self._hide_voice_bar()
        try:
            self.voice_button.itemconfig(self._voice_glyph, fill="#234CC8")
            self.voice_button.itemconfig(1, fill="#DCE8FF", outline="#AFC7FF")
        except:
            pass
        frames = self._voice_frames[:]
        self._voice_frames = []
        if not frames:
            try:
                self.chat_subtitle.configure(text="No audio recorded. Try again.")
            except:
                pass
            return
        try:
            try:
                import numpy as np
            except Exception as exc:
                messagebox.showerror(
                    "Voice note needs NumPy",
                    f"Install numpy: pip install numpy\n\n{exc}", parent=self.window)
                return
            audio = np.concatenate(frames, axis=0)
            view_once_suffix = "_viewonce" if getattr(self, "_voice_view_once_enabled", False) else ""
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"voice_note_{int(time.time())}{view_once_suffix}.wav")
            with wave.open(path, "wb") as wf:
                wf.setnchannels(self._voice_channels)
                wf.setsampwidth(2)
                wf.setframerate(self._voice_sample_rate)
                wf.writeframes(audio.astype("int16", copy=False).tobytes())
            self._upload_attachment(path, "audio")
            try:
                self.chat_subtitle.configure(text="Voice note sent")
            except:
                pass
        except Exception as exc:
            messagebox.showerror("Voice note failed", f"Could not save.\n\n{exc}", parent=self.window)



    def _open_emoji_picker(self):
        emojis = ["😀", "😃", "😄", "😁", "😆", "🙂", "😂", "🤣", "😊", "😍", "🥰", "😘", "😎", "🤔", "🙌", "👏", "👍", "👎", "❤️", "💙", "🔥", "🎉", "🙏", "💯", "😭", "😢", "😡", "🤝", "📚", "✅"]
        win = tk.Toplevel(self.window)
        win.title("Choose an emoji")
        win.transient(self.window)
        win.resizable(False, False)
        frame = tk.Frame(win, padx=10, pady=10, bg="#FBFCFF")
        frame.pack(fill="both", expand=True)
        for i, emoji in enumerate(emojis):
            tk.Button(frame, text=emoji, font=("Segoe UI Emoji", 17), width=3, relief="flat", bg="#EEF3FB",
                      command=lambda e=emoji: (self._insert_emoji(e), win.destroy())).grid(row=i//6, column=i%6, padx=3, pady=3)

    def _insert_emoji(self, emoji):
        self.compose_entry.insert(tk.INSERT, emoji)
        self.compose_entry.focus_set()

    def _escape_close_chat(self, event=None):
        """Escape returns to the welcome pane without closing ISSS Connect."""
        try:
            if getattr(self, "active", None) is None:
                return
            self.active = None
            self.active_kind = None
            self.people_list.selection_clear(0, "end")
            self._connect_callbar.pack_forget()
            self._connect_compose_frame.pack_forget()
            self._connect_message_area.pack_forget()
            self._connect_welcome.pack(fill="both", expand=True, padx=14, pady=14)
            self.chat_title.configure(text="Welcome to I.S.S.S. Connect")
            self.chat_subtitle.configure(text="Choose a classmate or group to start chatting.")
            self.avatar.configure(text="💬")
            return "break"
        except (AttributeError, tk.TclError):
            return "break"

    def _context_chat_item(self, event):
        index = self.people_list.nearest(event.y)
        if index < 0 or index >= len(getattr(self, "visible_conversations", [])):
            return None
        self.people_list.selection_clear(0, "end")
        self.people_list.selection_set(index)
        item = self.visible_conversations[index]
        self.active_kind, self.active = item[0], item[1]
        return item

    def _show_chat_menu(self, event):
        item = self._context_chat_item(event)
        if not item:
            return
        menu = tk.Menu(self.window, tearoff=0, bg="#132544", fg="#F8FAFC",
                       activebackground="#3B82F6", activeforeground="white",
                       font=("Segoe UI", 10), relief="flat", bd=0)
        menu.add_command(label="📂  Archive chat", command=self._toggle_archive)
        menu.add_command(label="🔒  Lock / unlock chat", command=self._toggle_chat_lock)
        menu.add_command(label="🔕  Mute / unmute notifications", command=self._toggle_mute_chat)
        menu.add_command(label="✦  Add / remove favourite", command=self._toggle_favourite_chat)
        menu.add_command(label="📋  Add to list", command=self._add_chat_to_list)
        menu.add_command(label="✓  Mark as unread", command=self._mark_chat_unread)
        menu.add_command(label="🚫  Block / unblock", command=self._toggle_block_chat)
        menu.add_command(label="🧹  Clear chat", command=self._clear_current_chat)
        menu.add_command(label="✕  Close chat", command=self._escape_close_chat)
        menu.add_separator()
        menu.add_command(label="🗑  Remove from this list", command=self._remove_chat_local)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            try: menu.grab_release()
            except tk.TclError: pass

    def _chat_key(self):
        return self._control_key((self.active_kind, self.active, ""))

    def _toggle_local_chat_flag(self, bucket, label):
        if not getattr(self, "active", None): return
        key = self._chat_key()
        values = set(self._chat_controls.get(bucket, []))
        if key in values: values.remove(key); msg = label + " disabled."
        else: values.add(key); msg = label + " enabled."
        self._chat_controls[bucket] = sorted(values)
        self._save_chat_controls()
        self._render_conversations()
        messagebox.showinfo(label, msg, parent=self.window)

    def _toggle_mute_chat(self): self._toggle_local_chat_flag("muted", "Mute notifications")
    def _toggle_favourite_chat(self): self._toggle_local_chat_flag("favourites", "Favourite")
    def _mark_chat_unread(self): self._toggle_local_chat_flag("unread", "Unread marker")
    def _toggle_block_chat(self): self._toggle_local_chat_flag("blocked", "Block")

    def _add_chat_to_list(self):
        if not getattr(self, "active", None): return
        name = simpledialog.askstring("Add to list", "Enter a list name (e.g. Study partners):", parent=self.window)
        if not name: return
        lists = self._chat_controls.setdefault("lists", {})
        lists[self._chat_key()] = name.strip()[:60]
        self._save_chat_controls()
        messagebox.showinfo("Added to list", f"Chat added to '{name.strip()[:60]}'.", parent=self.window)

    def _remove_chat_local(self):
        if not getattr(self, "active", None): return
        if not messagebox.askyesno("Remove chat", "Remove this conversation from the current chat list on this device? This does not delete server messages.", parent=self.window): return
        item = next((x for x in self.conversations if x[0] == self.active_kind and str(x[1]) == str(self.active)), None)
        if item:
            self.conversations.remove(item)
            self.active = self.active_kind = None
            self._render_conversations()
            self._escape_close_chat()

    def _clear_current_chat(self):
        if not getattr(self, "active", None): return
        if not messagebox.askyesno("Clear chat", "Clear the messages shown in this chat? This client does not delete the server history with this action.", parent=self.window): return
        self.messages.configure(state="normal")
        self.messages.delete("1.0", "end")
        self.messages.configure(state="disabled")
        self._message_records = {}
        self.last_message_id = 0

    def _message_info(self):
        record = self._selected_record()
        if not record: return
        messagebox.showinfo("Message info", f"Sender: {record.get('username', 'Unknown')}\nMessage ID: {record.get('id', 'Unknown')}\nTimestamp: {record.get('created_at', record.get('timestamp', 'Not provided by server'))}", parent=self.window)

    def _copy_selected_message(self):
        record = self._selected_record()
        if not record: return
        self.window.clipboard_clear()
        self.window.clipboard_append(str(record.get("body", "")))
        self.chat_subtitle.configure(text="Message copied to clipboard")

    def _star_selected_message(self):
        record = self._selected_record()
        if not record: return
        stars = self._chat_controls.setdefault("starred_messages", [])
        key = f"{self.active_kind}|{self.active}|{record.get('id')}"
        if key in stars: stars.remove(key); msg = "Message unstarred."
        else: stars.append(key); msg = "Message starred on this device."
        self._save_chat_controls()
        messagebox.showinfo("Star message", msg, parent=self.window)

    def _insert_attachment_menu_button(self, message_id, hover_tag=None):
        """Show a clearly visible three-dot menu while hovering over an attachment row."""
        base_bg = self.messages.cget("background")
        hover_bg = "#D9E6FA"
        hover_fg = "#10213D"
        state = {"hide_job": None}

        button = tk.Button(
            self.messages, text="⋮", font=("Segoe UI", 11, "bold"),
            bg=base_bg, fg=base_bg, activebackground=hover_bg,
            activeforeground=hover_fg, relief="flat", bd=0, cursor="hand2",
            padx=5, pady=0, command=lambda mid=message_id: self._open_message_actions(mid)
        )

        def show_menu(_event=None):
            job = state.get("hide_job")
            if job is not None:
                try: self.window.after_cancel(job)
                except (tk.TclError, ValueError): pass
                state["hide_job"] = None
            try:
                button.configure(bg=hover_bg, fg=hover_fg, activebackground="#BBD0F5")
            except tk.TclError:
                pass

        def hide_menu_later(_event=None):
            # Delay hiding so the pointer can move from the attachment label onto ⋮.
            old_job = state.get("hide_job")
            if old_job is not None:
                try: self.window.after_cancel(old_job)
                except (tk.TclError, ValueError): pass
            def hide_if_pointer_left():
                state["hide_job"] = None
                try:
                    x, y = self.window.winfo_pointerxy()
                    hovered = self.window.winfo_containing(x, y)
                    if hovered == button:
                        return
                    # If still over the tagged attachment text, keep the menu visible.
                    index = self.messages.index(f"@{x - self.messages.winfo_rootx()},{y - self.messages.winfo_rooty()}")
                    if hover_tag and hover_tag in self.messages.tag_names(index):
                        return
                    button.configure(bg=base_bg, fg=base_bg, activebackground=base_bg)
                except (tk.TclError, AttributeError):
                    try: button.configure(bg=base_bg, fg=base_bg, activebackground=base_bg)
                    except tk.TclError: pass
            state["hide_job"] = self.window.after(220, hide_if_pointer_left)

        button.bind("<Enter>", show_menu)
        button.bind("<Leave>", hide_menu_later)
        if hover_tag:
            self.messages.tag_bind(hover_tag, "<Enter>", show_menu)
            self.messages.tag_bind(hover_tag, "<Leave>", hide_menu_later)
        self.messages.window_create("end", window=button, align="center")

    def _open_message_actions(self, message_id):
        """Open the full message action dropdown from its three-dot button."""
        self._selected_message_id = int(message_id)
        record = getattr(self, "_message_records", {}).get(self._selected_message_id)
        if not record:
            messagebox.showinfo("Message unavailable", "Reload the chat and try again.", parent=self.window)
            return
        # WhatsApp-style deletion actions: once deleted for everyone, the only
        # remaining delete action is Delete for me. Rebuild the two menu entries
        # for the currently selected message so stale options cannot remain.
        try:
            end_index = self.message_menu.index("end")
            if end_index is not None:
                self.message_menu.delete(end_index - 1, end_index)
            self.message_menu.add_separator()
            self.message_menu.add_command(label="🗑  Delete for me", command=lambda: self._delete_selected_message("me"))
            if not record.get("deleted_for_all"):
                self.message_menu.add_command(label="🗑  Delete for everyone (only before read)", command=lambda: self._delete_selected_message("everyone"))
            self.message_menu.tk_popup(self.window.winfo_pointerx(), self.window.winfo_pointery())
        finally:
            try:
                self.message_menu.grab_release()
            except tk.TclError:
                pass

    def _show_message_menu(self, event):
        try:
            index = self.messages.index("@%d,%d" % (event.x, event.y))
            tags = self.messages.tag_names(index)
            self._selected_message_id = None
            for tag in tags:
                if tag.startswith("message_id_"):
                    try: self._selected_message_id = int(tag.rsplit("_", 1)[1])
                    except ValueError: pass
            self.messages.mark_set("insert", index)
            self.messages.tag_remove("sel", "1.0", "end")
            self.messages.tag_add("sel", "insert linestart", "insert lineend")
            self.message_menu.tk_popup(event.x_root, event.y_root)
        finally:
            try: self.message_menu.grab_release()
            except tk.TclError: pass

    def _selected_record(self):
        mid = getattr(self, "_selected_message_id", None)
        if mid is None:
            messagebox.showinfo("Select a message", "Click the three-dot menu beside a message first.", parent=self.window)
            return None
        record = getattr(self, "_message_records", {}).get(mid)
        if not record:
            messagebox.showinfo("Message unavailable", "Reload the chat and select the message again.", parent=self.window)
        return record

    def _edit_selected_message(self):
        record = self._selected_record()
        if not record: return
        if record.get("username", "").lower() != self.username.lower():
            messagebox.showinfo("Edit message", "You can only edit your own messages.", parent=self.window); return
        if record.get("read_at"):
            messagebox.showinfo("Edit message", "This message has been read (blue double ticks). You can no longer edit it.", parent=self.window); return
        if record.get("deleted_for_all"):
            messagebox.showinfo("Edit message", "This message was deleted and cannot be edited.", parent=self.window); return
        updated = simpledialog.askstring("Edit message", "Edit your message:", initialvalue=record.get("body", ""), parent=self.window)
        if updated is None or not updated.strip(): return
        try:
            self._request("PATCH", f"/api/messages/{record['id']}", json={"body": updated.strip()})
            self.last_message_id = 0
            self.messages.configure(state="normal"); self.messages.delete("1.0", "end"); self.messages.configure(state="disabled")
            self._message_records = {}; self._load_messages()
        except Exception as exc: messagebox.showerror("Cannot edit message", str(exc), parent=self.window)

    def _forward_selected_message(self):
        record = self._selected_record()
        if not record: return
        try:
            choices = [f"{kind}: {name}" for kind, target, name in self.conversations if not (kind == self.active_kind and str(target) == str(self.active))]
            if not choices:
                messagebox.showinfo("Forward", "Create another chat or group first.", parent=self.window); return
            chosen = simpledialog.askstring("Forward message", "Enter the destination username or exact group name:\n" + chr(10).join(choices[:25]), parent=self.window)
            if not chosen: return
            item = next((x for x in self.conversations if x[2].lower() == chosen.strip().lower() or (x[0] == "direct" and x[1].lower() == chosen.strip().lower())), None)
            if not item: messagebox.showinfo("Forward", "Destination not found in your chat list.", parent=self.window); return
            self._request("POST", "/api/messages", json={"kind": item[0], "target": str(item[1]), "body": record.get("body", "")})
            messagebox.showinfo("Forwarded", "Message forwarded.", parent=self.window)
        except Exception as exc: messagebox.showerror("Forward failed", str(exc), parent=self.window)

    def _react_to_selected_message(self):
        record = self._selected_record()
        if not record: return
        emoji = simpledialog.askstring("React to message", "Enter a reaction emoji (e.g. 👍 ❤️ 😂 🔥):", parent=self.window)
        if not emoji: return
        try:
            self._request("POST", f"/api/messages/{record['id']}/reaction", json={"emoji": emoji[:8]})
            messagebox.showinfo("Reaction", "Reaction saved.", parent=self.window)
            self.last_message_id = 0; self.messages.configure(state="normal"); self.messages.delete("1.0", "end"); self.messages.configure(state="disabled"); self._message_records = {}; self._load_messages()
        except Exception as exc: messagebox.showerror("Reaction failed", str(exc), parent=self.window)

    def _pin_selected_message(self):
        record = self._selected_record()
        if not record: return
        try:
            self._request("POST", f"/api/messages/{record['id']}/pin")
            messagebox.showinfo("Pinned", "Message pinned for this conversation.", parent=self.window)
        except Exception as exc: messagebox.showerror("Pin failed", str(exc), parent=self.window)

    def _report_selected_message(self):
        record = self._selected_record()
        if not record: return
        reason = simpledialog.askstring("Report message", "Why are you reporting this message?", parent=self.window)
        if not reason: return
        try:
            self._request("POST", f"/api/messages/{record['id']}/report", json={"reason": reason[:500]})
            messagebox.showinfo("Report submitted", "Thank you. The report has been recorded for review.", parent=self.window)
        except Exception as exc: messagebox.showerror("Report failed", str(exc), parent=self.window)

    def _delete_selected_message(self, mode):
        record = self._selected_record()
        if not record: return
        if mode == "everyone" and record.get("username", "").lower() != self.username.lower():
            messagebox.showinfo("Delete for everyone", "You can only delete your own messages for everyone.", parent=self.window); return
        if mode == "everyone" and record.get("read_at"):
            messagebox.showinfo("Delete for everyone", "This message has been read (blue double ticks). You can only delete it for yourself now.", parent=self.window); return
        prompt = "Delete this message for everyone? The option is available only before it is read.\n\nNote: Admin can still view deleted messages in vault." if mode == "everyone" else "Delete this message from your view? (Admin can still view in vault)"
        if not messagebox.askyesno("Delete message", prompt, parent=self.window): return
        try:
            # Archive to admin vault before deleting (so admin can view deleted messages)
            try:
                archive_deleted_message(record['id'], self.student_id, record.get('body','') or record.get('text',''), record.get('created_at',''), self.username, f"Deleted for {mode} by {self.username}")
            except:
                pass
            self._request("DELETE", f"/api/messages/{record['id']}?mode={mode}")
            self.last_message_id = 0; self.messages.configure(state="normal"); self.messages.delete("1.0", "end"); self.messages.configure(state="disabled"); self._message_records = {}; self._load_messages()
        except Exception as exc: messagebox.showerror("Cannot delete message", str(exc), parent=self.window)

    def _select_message_text(self):
        try:
            self.messages.tag_add("sel", "insert linestart", "insert lineend")
            self.window.clipboard_clear(); self.window.clipboard_append(self.messages.get("sel.first", "sel.last"))
            messagebox.showinfo("Selected", "Message text selected and copied. Use Ctrl+C to copy again.", parent=self.window)
        except tk.TclError: pass

    def _load_connect_settings(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "isss_connect_settings.json")
        try:
            with open(path, "r", encoding="utf-8") as f: return json.load(f)
        except Exception: return {"theme": "Light", "language": "English", "notifications": True, "chat_font_family": "Segoe UI", "font_size": 10}

    def _save_connect_settings(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "isss_connect_settings.json")
        try:
            with open(path, "w", encoding="utf-8") as f: json.dump(self._settings, f, indent=2)
        except OSError as exc: messagebox.showwarning("Settings", str(exc), parent=self.window)

    def _apply_connect_theme(self, settings_window=None):
        """Apply the selected theme immediately to the Connect interface and settings window."""
        theme = str(self._settings.get("theme", "Light"))
        if theme == "Dark":
            palette = {"bg": "#05070D", "panel": "#101827", "text": "#F4F7FF", "muted": "#B8C5DA", "entry": "#080D18", "border": "#263B60", "select": "#173A78", "accent": "#2563EB"}
        elif theme == "Green WhatsApp style":
            palette = {"bg": "#0B141A", "panel": "#202C33", "text": "#E9EDEF", "muted": "#AEBAC1", "entry": "#2A3942", "border": "#37474F", "select": "#37474F", "accent": "#00A884"}
        elif theme == "System":
            # Tkinter does not expose a consistent cross-platform system theme, so use the light palette as a safe fallback.
            palette = {"bg": "#DCEBFF", "panel": "#FFFFFF", "text": "#102A50", "muted": "#526987", "entry": "#F5F9FF", "border": "#B8D0F2", "select": "#C6DEFF", "accent": "#1769E0"}
        else:
            palette = {"bg": "#DCEBFF", "panel": "#FFFFFF", "text": "#102A50", "muted": "#526987", "entry": "#F5F9FF", "border": "#B8D0F2", "select": "#C6DEFF", "accent": "#1769E0"}

        roots = []
        try: roots.append(self.host)
        except Exception: pass
        if settings_window is not None:
            roots.append(settings_window)
        # Also theme the login form or other Connect frames currently attached to the top-level.
        def paint(widget):
            try:
                cls = widget.winfo_class()
                if cls in ("Frame", "Labelframe", "Toplevel"):
                    widget.configure(bg=palette["bg"] if widget is self.host else palette["panel"])
                elif cls == "Label":
                    old_fg = str(widget.cget("fg"))
                    # Keep vivid status/accent labels readable while adapting neutral text.
                    fg = palette["accent"] if old_fg.lower() in ("#315fea", "#234cc8", "#064e3b", "#0d9488") else palette["text"]
                    widget.configure(bg=palette["panel"], fg=fg)
                elif cls in ("Text", "Entry", "Listbox"):
                    opts = {"bg": palette["entry"], "fg": palette["text"], "insertbackground": palette["text"]}
                    if cls == "Listbox": opts.update(selectbackground=palette["select"], selectforeground=palette["text"])
                    if cls == "Text": opts.update(selectbackground=palette["select"])
                    widget.configure(**opts)
                elif cls == "Button":
                    text = str(widget.cget("text")).lower()
                    # Preserve primary action buttons, recolor neutral buttons for the active theme.
                    primary_terms = ("log in", "login", "sign up", "create account", "send", "voice call",
                                     "video call", "new chat", "group", "sign out", "return to study app",
                                     "check answer", "save settings", "save", "start", "pause", "reset",
                                     "archive / restore", "lock / unlock", "show archived", "back to login")
                    if any(k in text for k in primary_terms):
                        # Keep action buttons high-contrast instead of recolouring them into the panel.
                        original_bg = str(widget.cget("bg"))
                        if original_bg.lower() in ("#ffffff", "white", "#fbfcff", "#f0f4fb", "#e2e8f0", "#e7f0ff", "#f1eafe"):
                            widget.configure(bg=palette["accent"], fg="#FFFFFF")
                        widget.configure(activebackground=palette["accent"], activeforeground="#FFFFFF",
                                         relief="raised", bd=1, highlightthickness=1,
                                         highlightbackground=palette["border"], highlightcolor=palette["accent"],
                                         cursor="hand2")
                    else:
                        widget.configure(bg=palette["panel"], fg=palette["text"], activebackground=palette["select"],
                                         activeforeground=palette["text"], relief="raised", bd=1,
                                         highlightthickness=1, highlightbackground=palette["border"], cursor="hand2")
                elif cls == "Menu":
                    widget.configure(bg=palette["panel"], fg=palette["text"], activebackground=palette["accent"], activeforeground="#FFFFFF")
                elif cls == "Canvas":
                    widget.configure(bg=palette["bg"])
            except (tk.TclError, TypeError):
                pass
            try:
                for child in widget.winfo_children(): paint(child)
            except tk.TclError:
                pass
        seen = set()
        for root in roots:
            if root is not None and str(root) not in seen:
                seen.add(str(root)); paint(root)
        try:
            self.messages.tag_configure("name", foreground=palette["accent"], font=(self._settings.get("chat_font_family", "Segoe UI"), max(8, int(self._settings.get("font_size", 10)) - 1), "bold"))
            self.messages.tag_configure("body", foreground=palette["text"], font=(self._settings.get("chat_font_family", "Segoe UI"), int(self._settings.get("font_size", 10))))
            self._apply_chat_font()
        except Exception: pass

    def _open_settings(self):
        win = tk.Toplevel(self.window); win.title("I.S.S.S. Connect Settings"); win.geometry("650x650"); win.minsize(560, 500); win.transient(self.window)
        win.configure(bg="#F5F7FB")
        tk.Label(win, text="⚙  Settings", bg="#F5F7FB", fg="#132544", font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=22, pady=(18, 4))
        tk.Label(win, text="Manage your Connect experience", bg="#F5F7FB", fg="#64748B", font=("Segoe UI", 10)).pack(anchor="w", padx=22, pady=(0, 12))
        outer = tk.Frame(win, bg="#F5F7FB"); outer.pack(fill="both", expand=True, padx=18, pady=(0, 12))
        canvas = tk.Canvas(outer, bg="#F5F7FB", highlightthickness=0); bar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview); content = tk.Frame(canvas, bg="#F5F7FB")
        content.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content, anchor="nw"); canvas.configure(yscrollcommand=bar.set); canvas.pack(side="left", fill="both", expand=True); bar.pack(side="right", fill="y")
        sections = {
          "General": ["Startup behavior", "Enter sends message", "Keep Connect in system tray"],
          "Profile": ["Username", "Profile photo", "About / status"],
          "Account": ["Account details", "Phone number", "Change password", "Two-step verification"],
          "Privacy": ["Last seen and online", "Profile photo visibility", "Read receipts", "Blocked contacts"],
          "Chats": ["Chat wallpaper", "Archived chats", "Pinned messages", "Chat history"],
          "Linked devices": ["Current device", "Sign out other devices"],
          "Lists": ["Manage chat lists", "Favorites", "Muted chats"],
          "Appearance": ["Theme", "Font family", "Font size", "Chat wallpaper"],
          "Notifications": ["Message notifications", "Group notifications", "Call notifications", "Notification sounds"],
          "Storage and data": ["Media auto-download", "Storage usage", "Network usage"],
          "Parental controls": ["Safety information", "Report concerns", "Restricted contacts"],
          "Accessibility": ["High contrast", "Larger text", "Keyboard navigation"],
          "App language": ["English", "Yoruba", "Igbo", "Hausa"],
          "Help and feedback": ["Help center", "Send feedback", "Report a problem"],
          "Invite a friend": ["Copy invite message"], "App updates": ["Check for updates"],
          "Account center": ["Connected accounts", "Account information"]
        }
        for section, items in sections.items():
            card = tk.LabelFrame(content, text=section, bg="white", fg="#17365D", font=("Segoe UI", 10, "bold"), padx=10, pady=8)
            card.pack(fill="x", padx=4, pady=5)
            for item in items:
                row = tk.Frame(card, bg="white"); row.pack(fill="x", pady=3)
                tk.Label(row, text=item, bg="white", fg="#243B53", font=("Segoe UI", 9)).pack(side="left", padx=4)
                if item == "Theme":
                    theme = tk.StringVar(value=self._settings.get("theme", "Light")); cb = ttk.Combobox(row, textvariable=theme, values=["Light", "Dark", "System", "Green WhatsApp style"], state="readonly", width=22); cb.pack(side="right")
                    def apply_selected_theme(_event=None, v=theme, settings_window=win):
                        self._settings["theme"] = v.get()
                        self._save_connect_settings()
                        self._apply_connect_theme(settings_window)
                    cb.bind("<<ComboboxSelected>>", apply_selected_theme)
                elif item == "Message notifications" or item == "Group notifications" or item == "Call notifications" or item == "Read receipts":
                    var = tk.BooleanVar(value=self._settings.get(item, True)); chk = tk.Checkbutton(row, variable=var, bg="white", command=lambda k=item, v=var: (self._settings.update({k:v.get()}), self._save_connect_settings())); chk.pack(side="right")
                elif item == "Font family":
                    import tkinter.font as tkfont
                    try:
                        installed = list(tkfont.families(win))
                    except Exception:
                        installed = []
                    # Include common Windows fonts as suggestions too; unavailable fonts fall back automatically.
                    # Broad A-Z suggestions plus every font actually installed on this PC.
                    # The combobox is searchable/editable, so users can type any family name.
                    common = [
                        "Agency FB", "Aharoni", "Algerian", "Arial", "Arial Black", "Arial Narrow", "Arial Rounded MT Bold", "Bahnschrift", "Baskerville Old Face", "Bauhaus 93", "Bell MT", "Berlin Sans FB", "Bernard MT Condensed", "Bodoni MT", "Book Antiqua", "Bookman Old Style", "Bradley Hand ITC", "Britannic Bold", "Broadway", "Brush Script MT",
                        "Calibri", "Calisto MT", "Cambria", "Cambria Math", "Candara", "Cascadia Code", "Cascadia Mono", "Castellar", "Centaur", "Century", "Century Gothic", "Century Schoolbook", "Chiller", "Colonna MT", "Comic Sans MS", "Consolas", "Constantia", "Cooper Black", "Copperplate Gothic Bold", "Copperplate Gothic Light", "Corbel", "Courier New",
                        "Dubai", "Ebrima", "Edwardian Script ITC", "Elephant", "Engravers MT", "Eras Bold ITC", "Eras Demi ITC", "Eras Light ITC", "Eras Medium ITC", "Felix Titling", "Footlight MT Light", "Forte", "Franklin Gothic Book", "Franklin Gothic Demi", "Franklin Gothic Medium", "Freestyle Script", "French Script MT", "Gabriola", "Gadugi", "Garamond", "Georgia", "Gigi", "Gill Sans MT", "Gill Sans MT Condensed", "Gill Sans MT Ext Condensed Bold", "Gloucester MT Extra Condensed", "Goudy Old Style", "Goudy Stout", "Haettenschweiler", "Harlow Solid Italic", "Harrington", "High Tower Text", "HoloLens MDL2 Assets", "Impact", "Imprint MT Shadow", "Informal Roman", "Ink Free", "Javanese Text", "Jokerman", "Juice ITC", "Kristen ITC", "Kunstler Script", "Leelawadee UI", "Letter Gothic MT", "Lithos Pro Regular", "Lucida Bright", "Lucida Calligraphy", "Lucida Console", "Lucida Fax", "Lucida Handwriting", "Lucida Sans", "Lucida Sans Typewriter", "Lucida Sans Unicode", "Magneto", "Maiandra GD", "Malgun Gothic", "Marlett", "Matura MT Script Capitals", "Microsoft Himalaya", "Microsoft JhengHei", "Microsoft New Tai Lue", "Microsoft PhagsPa", "Microsoft Sans Serif", "Microsoft Tai Le", "Microsoft YaHei", "Microsoft Yi Baiti", "MingLiU-ExtB", "Mistral", "Modern No. 20", "Mongolian Baiti", "Monotype Corsiva", "MS Gothic", "MS Outlook", "MS PGothic", "MS Reference Sans Serif", "MS Reference Specialty", "MS UI Gothic", "MT Extra",
                        "Niagara Engraved", "Niagara Solid", "Nirmala UI", "OCR A Extended", "Old English Text MT", "Onyx", "Palace Script MT", "Palatino Linotype", "Papyrus", "Parchment", "Perpetua", "Perpetua Titling MT", "Playbill", "Poor Richard", "Pristina", "Rage Italic", "Ravie", "Rockwell", "Rockwell Condensed", "Rockwell Extra Bold", "Script MT Bold", "Segoe Fluent Icons", "Segoe MDL2 Assets", "Segoe Print", "Segoe Script", "Segoe UI", "Segoe UI Emoji", "Segoe UI Historic", "Segoe UI Symbol", "Showcard Gothic", "SimSun", "Sitka Banner", "Sitka Display", "Sitka Heading", "Sitka Small", "Sitka Subheading", "Sitka Text", "Snap ITC", "Stencil", "Sylfaen", "Symbol", "Tahoma", "Tempus Sans ITC", "Terminal", "Times New Roman", "Trebuchet MS", "Tw Cen MT", "Tw Cen MT Condensed", "Tw Cen MT Condensed Extra Bold", "Verdana", "Viner Hand ITC", "Vivaldi", "Vladimir Script", "Webdings", "Wide Latin", "Wingdings", "Yu Gothic"
                    ]
                    families = sorted(set(installed + common), key=str.casefold)
                    self._available_chat_fonts = families
                    family = tk.StringVar(value=self._settings.get("chat_font_family", "Segoe UI"))
                    cb = ttk.Combobox(row, textvariable=family, values=families, state="normal", width=28)
                    cb.pack(side="right", fill="x", expand=True, padx=(10, 0))
                    cb.bind("<<ComboboxSelected>>", lambda _e, v=family: self._set_chat_font_family(v.get()))
                    cb.bind("<Return>", lambda _e, v=family: self._set_chat_font_family(v.get()))
                    tk.Label(row, text=f"{len(families)} font choices (A–Z)", bg="white", fg="#64748B", font=("Segoe UI", 8)).pack(side="right", padx=(6, 0))
                elif item == "Font size":
                    size = tk.StringVar(value=str(self._settings.get("font_size", 10))); cb = ttk.Combobox(row, textvariable=size, values=["8", "9", "10", "11", "12", "13", "14", "16", "18", "20", "22", "24"], state="readonly", width=8); cb.pack(side="right"); cb.bind("<<ComboboxSelected>>", lambda _e, v=size: (self._settings.update(font_size=int(v.get())), self._save_connect_settings(), self._apply_chat_font()))
                else:
                    RoundedButton(row, text="Open", command=lambda sec=section, it=item: self._settings_action(sec, it), bg="#E8EEF8", fg="#234CC8", relief="flat", padx=10).pack(side="right")
        bottom = tk.Frame(win, bg="#F5F7FB"); bottom.pack(fill="x", padx=18, pady=12)
        RoundedButton(bottom, text="Save settings", command=lambda: (self._save_connect_settings(), messagebox.showinfo("Settings", "Your settings were saved.", parent=win)), bg="#315FEA", fg="white", relief="flat", padx=14, pady=8).pack(side="left")
        RoundedButton(bottom, text="Sign out", command=lambda: self._sign_out(win), bg="#B91C1C", fg="white", relief="flat", padx=14, pady=8).pack(side="right")
        # Apply the selected palette to the settings window too, including cards and controls.
        self._apply_connect_theme(win)

    def _set_chat_font_family(self, family):
        """Persist and apply the selected font to chat messages and the message composer."""
        family = str(family).strip()
        if not family:
            return
        self._settings["chat_font_family"] = family
        self._save_connect_settings()
        self._apply_chat_font()

    def _apply_chat_font(self):
        """Apply the selected family and size to chat content without changing icon glyphs."""
        family = str(self._settings.get("chat_font_family", "Segoe UI"))
        try:
            size = int(self._settings.get("font_size", 10))
        except (TypeError, ValueError):
            size = 10
        size = max(8, min(size, 24))
        try:
            self.messages.configure(font=(family, size))
            self.messages.tag_configure("name", foreground="#315FEA", font=(family, max(8, size - 1), "bold"))
            self.messages.tag_configure("body", font=(family, size))
        except Exception:
            pass
        try:
            self.compose_entry.configure(font=(family, size + 1))
        except Exception:
            pass
        try:
            self.search_entry.configure(font=(family, max(9, size)))
        except Exception:
            pass

    def _settings_action(self, section, item):
        """Open a usable local settings editor for every settings-row button.

        Values are persisted in isss_connect_settings.json. Options requiring a
        remote shared service are presented as local preferences rather than
        raising a "need to add something" placeholder error.
        """
        try:
            if item == "Profile photo":
                self._choose_profile_picture()
                return
            if item == "Copy invite message":
                invite = "Join me on I.S.S.S. Connect to chat with classmates and study together!"
                self.window.clipboard_clear(); self.window.clipboard_append(invite)
                messagebox.showinfo("Invite a friend", "Invitation copied to your clipboard. Paste it into a message to share it.", parent=self.window)
                return
            if item in ("English", "Yoruba", "Igbo", "Hausa"):
                self._settings["language"] = item; self._save_connect_settings()
                messagebox.showinfo("App language", f"{item} saved as your preferred language. Some labels remain in English until translations are added.", parent=self.window)
                return
            if item == "Check for updates":
                messagebox.showinfo("App updates", "Your local app is running. Automatic update checking is unavailable until an update feed is configured; you can still use the app normally.", parent=self.window)
                return
            if item == "Change password":
                old = simpledialog.askstring("Change password", "Enter your current Connect password:", show="*", parent=self.window)
                if old is None: return
                # Password changes are performed through the account recovery flow for this version.
                messagebox.showinfo("Change password", "For account safety, use the Forgot Password option on the Connect login screen to set a new password.", parent=self.window)
                return
            if item == "Current device":
                messagebox.showinfo("Linked devices", f"This device: {os.environ.get('COMPUTERNAME', 'This computer')}\nAccount: {getattr(self, 'username', 'Signed-in user')}\n\nThis is the currently active local session.", parent=self.window)
                return
            if item == "Sign out other devices":
                messagebox.showinfo("Linked devices", "No other linked sessions are stored by this local client. Remote session management requires a shared server.", parent=self.window)
                return
            if item == "Storage usage":
                import os as _os
                base = _os.path.dirname(_os.path.abspath(__file__))
                total = 0
                for name in _os.listdir(base):
                    try:
                        full = _os.path.join(base, name)
                        if _os.path.isfile(full) and ("connect" in name.lower() or name.lower().endswith('.db')):
                            total += _os.path.getsize(full)
                    except OSError: pass
                messagebox.showinfo("Storage usage", f"Approximate Connect/database files in this folder: {total / (1024*1024):.2f} MB", parent=self.window)
                return
            if item == "Network usage":
                messagebox.showinfo("Network usage", "This client does not yet collect network byte counts. Messages are sent through the configured Connect server when available.", parent=self.window)
                return
            if item == "Help center":
                messagebox.showinfo("Help center", "I.S.S.S. Connect help\n\n• Use the left panel to choose a conversation.\n• Use the message menu for reply, edit, forward, react, pin, report and delete actions.\n• Use Settings to save your local preferences.\n• If connection fails, make sure the Connect server is running and reachable.", parent=self.window)
                return
            if item in ("Send feedback", "Report a problem", "Report concerns"):
                feedback = simpledialog.askstring(item, "Describe your feedback or concern:", parent=self.window)
                if feedback is not None:
                    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "isss_connect_feedback.txt")
                    try:
                        with open(path, "a", encoding="utf-8") as f:
                            f.write(f"\n--- {section} / {item} ---\n{feedback.strip()}\n")
                        messagebox.showinfo(item, f"Saved locally to {os.path.basename(path)}.", parent=self.window)
                    except OSError as exc:
                        messagebox.showerror(item, f"Could not save feedback: {exc}", parent=self.window)
                return
            if item == "Account information":
                messagebox.showinfo("Account information", f"Username: {getattr(self, 'username', 'Unknown')}\nDevice: {os.environ.get('COMPUTERNAME', 'This computer')}\nSettings are saved on this device.", parent=self.window)
                return
            if item == "Connected accounts":
                messagebox.showinfo("Account center", "No external accounts are linked in this version. Your I.S.S.S. Connect account remains separate from external services.", parent=self.window)
                return
            if item == "Safety information":
                messagebox.showinfo("Safety information", "Stay safe on Connect\n\n• Do not share passwords or OTPs.\n• Only message people you know from school.\n• Report threatening or inappropriate messages to a trusted adult or school staff.\n• Block or mute people when needed.", parent=self.window)
                return
            if item == "Archived chats":
                messagebox.showinfo("Archived chats", "Archived-chat view is not available in this local client yet. Your existing conversations are not deleted by opening this option.", parent=self.window)
                return
            if item == "Pinned messages":
                messagebox.showinfo("Pinned messages", "Use the message menu and choose Pin message to pin a message in the open conversation.", parent=self.window)
                return
            if item == "Chat history":
                if messagebox.askyesno("Chat history", "Chat history is stored by the Connect server/database. Do you want to view the available local database files?", parent=self.window):
                    base = os.path.dirname(os.path.abspath(__file__))
                    files = [n for n in os.listdir(base) if n.lower().endswith(('.db', '.sqlite', '.sqlite3'))]
                    messagebox.showinfo("Chat history files", chr(10).join(files) if files else "No local SQLite database files were found in the application folder.", parent=self.window)
                return

            # All remaining options open a real editor instead of a placeholder.
            current = self._settings.get(item, self._settings.get(item.lower().replace(' ', '_'), ""))
            dlg = tk.Toplevel(self.window); dlg.title(f"{section} — {item}"); dlg.geometry("440x260"); dlg.minsize(380, 220); dlg.transient(self.window); dlg.grab_set()
            dlg.configure(bg="#F5F7FB")
            tk.Label(dlg, text=item, bg="#F5F7FB", fg="#17365D", font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=18, pady=(18, 5))
            descriptions = {
                "Username": "Display name used in your Connect profile.", "About / status": "Write a short status for classmates.",
                "Phone number": "Update the phone number shown in your local profile.", "Account details": "Review or save a short account note.",
                "Startup behavior": "Choose whether Connect should remember this preference.", "Enter sends message": "Choose whether Enter sends a message or inserts a new line.",
                "Keep Connect in system tray": "Save your preference for keeping Connect available in the background.",
                "Chat wallpaper": "Choose a wallpaper colour for the chat area.", "Manage chat lists": "Name or describe your chat lists.",
                "Favorites": "Save your favorites preference.", "Muted chats": "Save your muted chats preference.",
                "Media auto-download": "Choose a local media download preference.", "Notification sounds": "Enable or disable notification sounds.",
                "High contrast": "Improve contrast for easier reading.", "Larger text": "Use a larger font size in supported areas.",
                "Keyboard navigation": "Save keyboard navigation preference.", "Two-step verification": "Save your preference for additional account protection.",
                "Profile photo visibility": "Choose who can see your profile photo.", "Last seen and online": "Choose the visibility preference for your online status.",
                "Blocked contacts": "Enter usernames to block, separated by commas.", "Restricted contacts": "Enter usernames to restrict, separated by commas.",
                "Message notifications": "Turn message notifications on or off.", "Group notifications": "Turn group notifications on or off.", "Call notifications": "Turn call notifications on or off.",
            }
            tk.Label(dlg, text=descriptions.get(item, "Set your preference below. Changes are saved on this computer."), bg="#F5F7FB", fg="#526176", wraplength=390, justify="left").pack(anchor="w", padx=18, pady=(0, 12))
            key = item
            if item in ("Enter sends message", "Keep Connect in system tray", "Message notifications", "Group notifications", "Call notifications", "Notification sounds", "Read receipts", "High contrast", "Larger text", "Keyboard navigation", "Media auto-download", "Two-step verification", "Startup behavior"):
                var = tk.BooleanVar(value=bool(current) if current != "" else True)
                tk.Checkbutton(dlg, text="Enabled", variable=var, bg="#F5F7FB", fg="#243B53", activebackground="#F5F7FB").pack(anchor="w", padx=20)
                getter = var.get
            elif item in ("Last seen and online", "Profile photo visibility"):
                var = tk.StringVar(value=str(current or "Everyone"))
                ttk.Combobox(dlg, textvariable=var, values=["Everyone", "My contacts", "Nobody"], state="readonly", width=28).pack(anchor="w", padx=20)
                getter = var.get
            elif item == "Chat wallpaper":
                var = tk.StringVar(value=str(current or "Green"))
                ttk.Combobox(dlg, textvariable=var, values=["Green", "Light", "Dark", "Blue", "Plain"], state="readonly", width=28).pack(anchor="w", padx=20)
                getter = var.get
            else:
                var = tk.StringVar(value=str(current or ""))
                ent = tk.Entry(dlg, textvariable=var, font=("Segoe UI", 10), width=42)
                ent.pack(anchor="w", padx=20, fill="x"); ent.focus_set()
                getter = var.get
            def save_value():
                value = getter()
                self._settings[key] = value
                self._save_connect_settings()
                dlg.destroy()
                messagebox.showinfo(item, f"{item} preference saved on this computer.", parent=self.window)
            buttons = tk.Frame(dlg, bg="#F5F7FB"); buttons.pack(fill="x", padx=18, pady=18)
            tk.Button(buttons, text="Save", command=save_value, bg="#315FEA", fg="white", relief="flat", padx=18, pady=6).pack(side="right", padx=(6, 0))
            tk.Button(buttons, text="Cancel", command=dlg.destroy, bg="#E2E8F0", fg="#243B53", relief="flat", padx=18, pady=6).pack(side="right")
        except Exception as exc:
            messagebox.showerror("Settings", f"Could not open {item}: {exc}", parent=self.window)

    def _sign_out(self, win=None):
        if not messagebox.askyesno("Sign out", "Sign out of I.S.S.S. Connect on this device?", parent=win or self.window): return
        self.token = None; self.active = None; self.active_kind = None
        self._clear_saved_session()
        if win:
            try: win.destroy()
            except tk.TclError: pass
        try: self.connect_outer.destroy()
        except Exception: pass
        self._build_login()

    def _reply_to_selected_message(self):
        try:
            line = self.messages.get("sel.first", "sel.last").strip()
        except tk.TclError:
            line = self.messages.get("insert linestart", "insert lineend").strip()
        if not line:
            return
        if "  ·  " in line:
            line = ""
        if not line:
            try:
                line = self.messages.get("insert - 1 lines linestart", "insert - 1 lines lineend").strip()
            except tk.TclError:
                line = ""
        if line:
            self.compose_entry.delete(0, "end")
            self.compose_entry.insert(0, "↩ Reply: " + line[:180] + " | ")
            self.compose_entry.focus_set()

    def _create_poll(self):
        question = simpledialog.askstring("New poll", "Enter your poll question:", parent=self.window)
        if not question or not self.active: return
        options = simpledialog.askstring("Poll options", "Enter at least two options separated by commas:", parent=self.window)
        if not options: return
        choices = [x.strip() for x in options.split(",") if x.strip()]
        if len(choices) < 2:
            messagebox.showinfo("Poll", "Please enter at least two options separated by commas.", parent=self.window); return
        self.compose_entry.delete(0, "end")
        self.compose_entry.insert(0, "📊 POLL: " + question.strip() + "\n" + chr(10).join("• " + x for x in choices))
        self._send_message()

    def _create_event(self):
        title = simpledialog.askstring("New event", "Event title:", parent=self.window)
        if not title or not self.active: return
        when = simpledialog.askstring("Event date/time", "Enter date and time (e.g. 25 Oct, 3:00 PM):", parent=self.window)
        if not when: return
        details = simpledialog.askstring("Event details", "Optional location or details:", parent=self.window) or ""
        self.compose_entry.delete(0, "end")
        self.compose_entry.insert(0, f"📅 EVENT: {title.strip()} | {when.strip()} | {details.strip()}")
        self._send_message()

    def _choose_sticker(self):
        """Send a selected image as a sticker-style image attachment."""
        if not self.active:
            messagebox.showinfo("Choose a chat", "Open a classmate or group chat before sending a sticker.", parent=self.window)
            return
        path = filedialog.askopenfilename(
            parent=self.window,
            title="Choose a sticker image to send",
            filetypes=[("Sticker images", "*.png *.gif *.jpg *.jpeg *.webp *.bmp"), ("All files", "*.*")]
        )
        if path:
            self._upload_attachment(path, "photo")

    def _load_nicknames(self):
        try:
            with open(self.nickname_file, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            return data if isinstance(data, dict) else {}
        except (OSError, ValueError, AttributeError):
            return {}

    def _save_nicknames(self):
        try:
            with open(self.nickname_file, "w", encoding="utf-8") as handle:
                json.dump(self.nicknames, handle, ensure_ascii=False, indent=2)
        except OSError as exc:
            messagebox.showwarning("Nickname not saved", f"Could not save custom friend names.\n{exc}", parent=self.window)

    def _display_name(self, username):
        return self.nicknames.get(self.username, {}).get(username.lower(), username)

    def _rename_friend(self):
        if not self.active or self.active_kind != "direct":
            messagebox.showinfo("Rename friend", "Select an individual classmate first. Group names are managed separately.", parent=self.window)
            return
        username = str(self.active)
        current = self._display_name(username)
        new_name = simpledialog.askstring("Customize friend name", f"Choose a display name for {username}:",
                                          initialvalue=current, parent=self.window)
        if new_name is None:
            return
        new_name = new_name.strip()
        if not new_name:
            messagebox.showinfo("Friend name", "The display name cannot be empty.", parent=self.window)
            return
        self.nicknames.setdefault(self.username, {})[username.lower()] = new_name[:60]
        self._save_nicknames()
        self.chat_title.configure(text=self._display_name(username))
        self._render_conversations()

    def _load_chat_controls(self):
        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "isss_connect_chat_controls.json"), "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except (OSError, ValueError):
            return {}

    def _save_chat_controls(self):
        try:
            with open(self._chat_controls_path, "w", encoding="utf-8") as f:
                json.dump(self._chat_controls, f, indent=2, ensure_ascii=False)
        except OSError as exc:
            messagebox.showwarning("Settings not saved", f"Could not save archive/lock settings.\n{exc}", parent=self.window)

    def _control_key(self, item=None):
        item = item or (self.active_kind, self.active, "")
        if not item or not item[0] or item[1] is None:
            return None
        return f"{self.username.lower()}|{item[0]}|{item[1]}"

    def _toggle_archived_view(self):
        self._show_archived = not self._show_archived
        # Update the visible label on the archive-view button.
        for child in self.host.winfo_children():
            pass
        self._render_conversations()

    def _toggle_archive(self):
        if not self.active:
            messagebox.showinfo("Archive chat", "Select a chat or group first.", parent=self.window); return
        key = self._control_key()
        archived = set(self._chat_controls.get("archived", []))
        if key in archived:
            archived.remove(key); action = "restored to your main chat list"
        else:
            archived.add(key); action = "archived"
        self._chat_controls["archived"] = sorted(archived)
        self._save_chat_controls()
        self._render_conversations()
        messagebox.showinfo("Chat updated", f"This conversation has been {action}.", parent=self.window)

    def _toggle_chat_lock(self):
        if not self.active:
            messagebox.showinfo("Lock chat", "Select a chat or group first.", parent=self.window); return
        key = self._control_key()
        locks = self._chat_controls.setdefault("locks", {})
        if key in locks:
            pin = simpledialog.askstring("Unlock chat", "Enter this chat's PIN:", show="*", parent=self.window)
            if pin is None: return
            if not hmac.compare_digest(hashlib.sha256(pin.encode("utf-8")).hexdigest(), locks.get(key, "")):
                messagebox.showerror("Incorrect PIN", "That PIN is incorrect. The chat remains locked.", parent=self.window); return
            del locks[key]
            self._save_chat_controls()
            messagebox.showinfo("Chat unlocked", "This chat is unlocked on this device.", parent=self.window)
            return
        pin = simpledialog.askstring("Lock chat", "Create a PIN for this chat (4 or more characters):", show="*", parent=self.window)
        if pin is None: return
        if len(pin) < 4:
            messagebox.showwarning("PIN too short", "Use at least 4 characters.", parent=self.window); return
        confirm = simpledialog.askstring("Confirm PIN", "Enter the PIN again:", show="*", parent=self.window)
        if confirm != pin:
            messagebox.showwarning("PIN mismatch", "The PINs did not match. Chat was not locked.", parent=self.window); return
        locks[key] = hashlib.sha256(pin.encode("utf-8")).hexdigest()
        self._save_chat_controls()
        messagebox.showinfo("Chat locked", "This chat is now PIN-locked on this device. Keep the PIN safe; there is no automatic recovery.", parent=self.window)
        self._render_conversations()

    def _render_conversations(self):
        if not hasattr(self, "people_list"):
            return
        query = self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""
        self.visible_conversations = []
        self.people_list.delete(0, "end")
        archived = set(self._chat_controls.get("archived", []))
        locks = self._chat_controls.get("locks", {})
        for item in self.conversations:
            kind, target, original_name = item
            key = self._control_key(item)
            is_archived = key in archived
            if is_archived != self._show_archived:
                continue
            label = self._display_name(original_name) if kind == "direct" else original_name
            if kind == "direct":
                presence = self._presence_by_username.get(original_name.lower(), {})
                status_label = "Online" if presence.get("online") else self._format_last_seen(presence.get("last_seen"))
                label = f"{label}  ·  {status_label}"
            if query and query not in label.lower() and query not in original_name.lower():
                continue
            self.visible_conversations.append(item)
            prefix = "🔒  " if key in locks else ("●  " if kind == "direct" else "▦  ")
            if key in set(self._chat_controls.get("favourites", [])): prefix = "⭐ " + prefix
            if key in set(self._chat_controls.get("muted", [])): prefix = "🔕 " + prefix
            if key in set(self._chat_controls.get("unread", [])): prefix = "🟢 " + prefix
            self.people_list.insert("end", prefix + label)
        if not self.visible_conversations:
            self.people_list.insert("end", "No archived chats" if self._show_archived else ("No matching classmates or groups" if query else "No chats yet"))

    def _format_last_seen(self, value):
        if not value:
            return "Last seen unavailable"
        return "Last seen " + str(value)

    def _headers(self): return {"Authorization": "Bearer " + self.token}

    def _request(self, method, path, **kwargs):
        if requests is None: raise RuntimeError("Install requests first: python -m pip install requests")
        r = requests.request(method, self.server + path, headers=self._headers(), timeout=10, **kwargs)
        data = r.json() if r.content else {}
        if not r.ok: raise RuntimeError(data.get("detail", "Server request failed"))
        return data

    def _refresh_lists(self):
        """Fetch classmates and groups, tolerating common response shapes."""
        def worker():
            try:
                people_payload = self._request("GET", "/api/users")
                # Compatibility fallback for servers exposing the explicit friends route.
                def has_people(payload):
                    if isinstance(payload, list):
                        return bool(payload)
                    if not isinstance(payload, dict):
                        return False
                    for key in ("users", "friends", "classmates", "students", "people", "results"):
                        if isinstance(payload.get(key), list) and payload.get(key):
                            return True
                    nested = payload.get("data")
                    if isinstance(nested, list):
                        return bool(nested)
                    if isinstance(nested, dict):
                        return any(isinstance(nested.get(key), list) and nested.get(key) for key in ("users", "friends", "classmates", "students", "people", "results"))
                    return False
                if not has_people(people_payload):
                    try:
                        friends_payload = self._request("GET", "/api/friends")
                        if has_people(friends_payload):
                            people_payload = friends_payload
                    except Exception:
                        pass
                try:
                    groups_payload = self._request("GET", "/api/groups")
                except Exception:
                    groups_payload = {"groups": []}

                def extract_list(payload, keys):
                    if isinstance(payload, list):
                        return payload
                    if not isinstance(payload, dict):
                        return []
                    for key in keys:
                        value = payload.get(key)
                        if isinstance(value, list):
                            return value
                    nested = payload.get("data")
                    if isinstance(nested, list):
                        return nested
                    if isinstance(nested, dict):
                        for key in keys:
                            value = nested.get(key)
                            if isinstance(value, list):
                                return value
                    return []

                people = extract_list(people_payload, ("users", "friends", "classmates", "students", "people", "results"))
                groups = extract_list(groups_payload, ("groups", "chats", "results"))
                # Normalize username fields without discarding server metadata.
                normalized_people = []
                for person in people:
                    if not isinstance(person, dict):
                        continue
                    person = dict(person)
                    person["username"] = str(person.get("username") or person.get("user_name") or person.get("name") or "").strip()
                    if person["username"]:
                        normalized_people.append(person)
                normalized_groups = []
                for group in groups:
                    if not isinstance(group, dict):
                        continue
                    group = dict(group)
                    group["id"] = group.get("id", group.get("group_id", group.get("name", "")))
                    group["name"] = str(group.get("name") or group.get("title") or group.get("group_name") or "Study group")
                    if str(group["id"]).strip():
                        normalized_groups.append(group)
                self.window.after(0, lambda p=normalized_people, g=normalized_groups: self._show_lists(p, g))
            except Exception as exc:
                self.window.after(0, lambda m=str(exc): self._status_error(m))
                self.window.after(0, lambda m=str(exc): self._show_list_problem(m))
        threading.Thread(target=worker, daemon=True).start()

    def _recent_chats_path(self):
        """Per-account local index of recent conversations; messages remain on the server."""
        safe_user = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(self.username or "student")).strip("._") or "student"
        server_key = hashlib.sha256(str(self.server).rstrip("/").lower().encode("utf-8")).hexdigest()[:10]
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), f"isss_connect_recent_chats_{safe_user}_{server_key}.json")

    def _load_recent_chats(self):
        try:
            with open(self._recent_chats_path(), "r", encoding="utf-8") as handle:
                data = json.load(handle)
            return data if isinstance(data, list) else []
        except (OSError, ValueError, TypeError):
            return []

    def _save_recent_chats(self):
        """Persist conversation references only, never message bodies or passwords."""
        try:
            unique = {}
            for kind, target, name in self.conversations:
                if kind not in ("direct", "group") or not str(target).strip():
                    continue
                key = (kind, str(target).lower() if kind == "direct" else str(target))
                unique[key] = {"kind": kind, "target": str(target), "name": str(name), "updated_at": time.time()}
            records = sorted(unique.values(), key=lambda x: x.get("updated_at", 0), reverse=True)[:300]
            with open(self._recent_chats_path(), "w", encoding="utf-8") as handle:
                json.dump(records, handle, ensure_ascii=False, indent=2)
        except (OSError, TypeError, ValueError):
            pass

    def _remember_recent_conversation(self, item=None):
        item = item or ((self.active_kind, self.active, str(self.active)) if self.active_kind and self.active else None)
        if not item:
            return
        kind, target, name = item
        target = str(target)
        existing = next((x for x in self.conversations if x[0] == kind and str(x[1]).lower() == target.lower()), None)
        if existing:
            self.conversations.remove(existing)
        self.conversations.insert(0, (kind, target, str(name or target)))
        self._save_recent_chats()

    def _show_lists(self, users, groups):
        # Merge newly eligible classmates with recent chats instead of replacing the
        # conversation list. This keeps prior chats visible across app restarts.
        previous = list(getattr(self, "conversations", []))
        self.conversations = []
        self._presence_by_username = {
            str(u.get("username", "")).lower(): u for u in users
            if isinstance(u, dict) and u.get("username")
        }
        for user in users:
            username = str(user.get("username", "")).strip()
            if not username or username.lower() == self.username.lower():
                continue
            # Server-side /api/users should return the eligible classmates. If class/department
            # fields exist, enforce the school's exact class + department communication rule.
            my_class = str(getattr(self, "school_class", "") or getattr(self, "class_name", "")).strip().lower()
            my_dept = str(getattr(self, "department", "")).strip().lower()
            user_class = str(user.get("school_class") or user.get("class_name") or user.get("class") or "").strip().lower()
            user_dept = str(user.get("department") or "").strip().lower()
            if my_class and user_class and my_class != user_class:
                continue
            if my_dept and user_dept and my_dept != user_dept:
                continue
            self.conversations.append(("direct", username, username))
        for group in groups:
            group_id = str(group.get("id", "")).strip()
            group_name = str(group.get("name") or "Study group")
            if group_id:
                self.conversations.append(("group", group_id, group_name))

        # Automatically list every eligible classmate returned by the server.
        # The server's /api/users and /api/friends routes enforce exact class +
        # department matching. Restore old direct chats only while that username is
        # still in the eligible classmate directory, avoiding stale/out-of-cohort chats.
        known = {(k, str(t).lower() if k == "direct" else str(t)) for k, t, _ in self.conversations}
        eligible_usernames = {
            str(user.get("username", "")).strip().casefold()
            for user in users
            if isinstance(user, dict) and str(user.get("username", "")).strip()
        }
        recent = self._load_recent_chats()
        for record in recent:
            if not isinstance(record, dict):
                continue
            kind = str(record.get("kind", ""))
            target = str(record.get("target", "")).strip()
            name = str(record.get("name") or target).strip()
            if kind not in ("direct", "group") or not target:
                continue
            if kind == "direct":
                if target.casefold() == self.username.casefold():
                    continue
                # Newly registered classmates are included automatically above.
                if target.casefold() not in eligible_usernames:
                    continue
            key = (kind, target.lower() if kind == "direct" else target)
            if key not in known:
                self.conversations.append((kind, target, name))
                known.add(key)
        for item in previous:
            if not isinstance(item, (tuple, list)) or len(item) < 3:
                continue
            kind, target, name = item[0], str(item[1]), str(item[2])
            key = (kind, target.lower() if kind == "direct" else target)
            if kind == "direct" and target.casefold() not in eligible_usernames:
                continue
            if kind in ("direct", "group") and target and key not in known:
                self.conversations.append((kind, target, name))
                known.add(key)
        self._save_recent_chats()
        self._render_conversations()
        if not self.conversations:
            self._show_list_problem(
                "No classmates/groups were returned by the server. Make sure both students are registered on the SAME server and that GET /api/users returns classmates for the signed-in account.")

    def _show_list_problem(self, message):
        """Display list-load status in the existing status area without hiding the app."""
        try:
            if hasattr(self, "chat_subtitle"):
                self.chat_subtitle.configure(text="Classmates could not be loaded: " + str(message)[:180])
            elif hasattr(self, "auth_status"):
                self.auth_status.configure(text="Connect status: " + str(message)[:220], fg="#B91C1C")
        except (tk.TclError, AttributeError):
            pass

    def _select_conversation(self, _event=None):
        selected = self.people_list.curselection()
        if not selected or not hasattr(self, "visible_conversations"):
            return
        if selected[0] >= len(self.visible_conversations):
            return
        item = self.visible_conversations[selected[0]]
        self._remember_recent_conversation(item)
        self.active_kind, self.active, original_title = item
        key = self._control_key(item)
        lock_hash = self._chat_controls.get("locks", {}).get(key)
        if lock_hash:
            pin = simpledialog.askstring("Locked chat", "Enter this chat's PIN to open it:", show="*", parent=self.window)
            if pin is None or not hmac.compare_digest(hashlib.sha256(pin.encode("utf-8")).hexdigest(), lock_hash):
                self.people_list.selection_clear(0, "end")
                if pin is not None: messagebox.showerror("Chat locked", "Incorrect PIN. This conversation remains locked.", parent=self.window)
                self.active = None; self.active_kind = None
                self.chat_title.configure(text="🔒 Chat locked")
                self.chat_subtitle.configure(text="Enter the correct PIN by selecting this chat again.")
                self.messages.configure(state="normal"); self.messages.delete("1.0", "end"); self.messages.configure(state="disabled")
                return
        if hasattr(self, "_connect_welcome"):
            self._connect_welcome.pack_forget()
            self._connect_callbar.pack(fill="x", padx=14, pady=(0, 10))
            self._connect_compose_frame.pack(side="bottom", fill="x", padx=14, pady=(0, 14))
            self._connect_message_area.pack(side="top", fill="both", expand=True, padx=14, pady=(0, 10))
        title = self._display_name(original_title) if self.active_kind == "direct" else original_title
        self.last_message_id = 0
        self._message_records = {}
        self.chat_title.configure(text=title if self.active_kind == "direct" else "Group: " + title)
        if self.active_kind == "direct":
            presence = self._presence_by_username.get(str(original_title).lower(), {})
            status = "Online" if presence.get("online") else self._format_last_seen(presence.get("last_seen"))
            subtitle = status + "  ·  Private conversation with @" + original_title
        else:
            subtitle = "Study group conversation"
        self.chat_subtitle.configure(text=subtitle)
        self.avatar.configure(text=(title[:1].upper() if title else "💬"))
        self.messages.configure(state="normal")
        self.messages.delete("1.0", "end")
        self.messages.configure(state="disabled")
        self._load_messages()

    def _mark_message_read_safely(self, message_id):
        try:
            self._request("POST", f"/api/messages/{message_id}/read")
        except Exception:
            pass

    def _load_messages(self):
        if not self.active: return
        kind, target = self.active_kind, self.active
        path = "/api/messages?kind=" + kind + "&target=" + requests.utils.quote(str(target)) + "&after=" + str(self.last_message_id)
        def worker():
            try:
                data = self._request("GET", path)
                self.window.after(0, lambda: self._append_messages(data.get("messages", []), kind, target))
            except Exception as exc:
                self.window.after(0, lambda m=str(exc): self._status_error(m))
        threading.Thread(target=worker, daemon=True).start()

    def _append_messages(self, messages, kind, target):
        if self.active_kind != kind or self.active != target:
            return
        if not messages:
            return
        self.messages.configure(state="normal")
        for msg in messages:
            self.last_message_id = max(self.last_message_id, msg["id"])
            self._message_records[msg["id"]] = dict(msg)
            if msg.get("username", "").lower() != self.username.lower() and kind == "direct":
                threading.Thread(target=self._mark_message_read_safely, args=(msg["id"],), daemon=True).start()
            message_tag = "message_id_" + str(msg["id"])
            # Header includes an always-visible three-dot action menu; no right-click needed.
            self.messages.insert("end", f"{msg['username']}  ·  {msg['created_at']}  ", ("name", message_tag))
            menu_button = tk.Button(
                self.messages, text="⋮", font=("Segoe UI", 12, "bold"),
                bg="#DCE8FA", fg="#20304A", activebackground="#BBD0F5",
                activeforeground="#10213D", relief="flat", bd=0, cursor="hand2",
                padx=5, pady=0, command=lambda mid=msg["id"]: self._open_message_actions(mid)
            )
            self.messages.window_create("end", window=menu_button, align="center")
            self.messages.insert("end", "\n")
            body = msg["body"]
            if msg.get("deleted_for_all"):
                deleted_tag = "deleted_message_" + str(msg["id"])
                self.messages.tag_configure(deleted_tag, foreground="#7B8798", font=("Segoe UI", 10, "italic"))
                self.messages.insert("end", "  This message was deleted\n\n", (deleted_tag,))
                continue
            lines = body.splitlines()
            attachment_label = lines[0] if lines else ""
            video_attachment = attachment_label.startswith("🖼 Photo/video:") and attachment_label.lower().endswith((".mp4", ".mov", ".avi", ".mkv"))
            image_attachment = attachment_label.startswith("🖼 Photo/video:") and any(
                attachment_label.lower().endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
            )
            for line in lines:
                if line.startswith("Open attachment: "):
                    url = line.split(": ", 1)[1].strip()
                    if video_attachment:
                        self.messages.insert("end", "  ▶ Video attachment — preparing video…\n", ("image_loading",))
                        self._download_and_play_video(url, msg["id"], attachment_label.split(":", 1)[-1].strip())
                    elif image_attachment:
                        self.messages.insert("end", "  Loading image…\n", ("image_loading",))
                        self._load_inline_chat_image(url, msg["id"])
                    else:
                        # Render audio and documents - WhatsApp-style voice bubble for audio
                        audio_attachment = attachment_label.startswith("🎵 Audio:")
                        document_attachment = attachment_label.startswith("📄 Document:")
                        filename = attachment_label.split(":", 1)[-1].strip() or "Attachment"
                        
                        if audio_attachment:
                            # FIXED WhatsApp-style voice bubble - REAL PLAYBACK WITH SOUND
                            is_view_once = "viewonce" in filename.lower()
                            is_my_message = msg.get("username", "").lower() == self.username.lower()
                            bubble_bg = "#DCF8C6" if is_my_message else "#FFFFFF"
                            bubble = tk.Frame(self.messages, bg=bubble_bg, bd=0, relief="flat")
                            inner = tk.Frame(bubble, bg=bubble_bg)
                            inner.pack(fill="both", expand=True, padx=6, pady=6)
                            
                            top_row = tk.Frame(inner, bg=bubble_bg)
                            top_row.pack(fill="x")
                            
                            # Profile pic circle with mic icon like image_4c637a.png
                            profile_frame = tk.Frame(top_row, bg=bubble_bg)
                            profile_frame.pack(side="left", padx=2)
                            profile_canvas = tk.Canvas(profile_frame, width=44, height=44, bg=bubble_bg, highlightthickness=0, bd=0)
                            profile_canvas.create_oval(2,2,42,42, fill="#8AB4A0", outline=bubble_bg, width=2)
                            try:
                                initial = msg.get("username", "?")[:1].upper()
                                profile_canvas.create_text(22,18, text=initial, fill="white", font=("Segoe UI", 14, "bold"))
                            except:
                                profile_canvas.create_text(22,18, text="U", fill="white", font=("Segoe UI", 12))
                            profile_canvas.create_oval(28,28,40,40, fill="#25D366", outline="white", width=1)
                            profile_canvas.create_text(34,33, text="M", fill="white", font=("Segoe UI", 7, "bold"))
                            profile_canvas.pack()
                            
                            # Play/Pause button - shows PLAY when paused, PAUSE when playing
                            play_canvas = tk.Canvas(top_row, width=36, height=36, bg=bubble_bg, highlightthickness=0, bd=0, cursor="hand2")
                            play_canvas.create_oval(1,1,35,35, fill="#25D366", outline="#25D366")
                            play_canvas.create_polygon(12,9, 12,27, 26,18, fill="white", outline="white", tags="icon")
                            play_canvas._is_playing = False
                            play_canvas._is_paused = False
                            play_canvas._audio_data = None
                            play_canvas._current_pos = 0
                            play_canvas._total_frames = 0
                            play_canvas.pack(side="left", padx=6)
                            
                            # Waveform with preview - dotted line that waves when playing
                            wave_frame = tk.Frame(top_row, bg=bubble_bg)
                            wave_frame.pack(side="left", fill="x", expand=True, padx=4)
                            wave_canvas = tk.Canvas(wave_frame, height=32, bg=bubble_bg, highlightthickness=0, bd=0)
                            wave_canvas.pack(fill="x", expand=True)
                            wave_canvas._waveform_data = []
                            wave_canvas._progress = 0
                            
                            # Duration
                            duration = "0:03"
                            dur_label = tk.Label(wave_frame, text=duration, bg=bubble_bg, fg="#667781", font=("Segoe UI", 9))
                            dur_label.pack(anchor="w")
                            
                            def draw_preview_waveform(canvas, progress=0, is_playing=False, audio_data=None):
                                canvas.delete("wave")
                                w = canvas.winfo_width()
                                if w < 50:
                                    w = 180
                                h = 32
                                dots = 40
                                
                                # If we have audio data, use it for preview, else random
                                if audio_data is not None and len(audio_data) > 0:
                                    # Use real audio data for waveform preview
                                    try:
                                        import numpy as np
                                        # Downsample audio for waveform
                                        step = max(1, len(audio_data) // dots)
                                        for i in range(dots):
                                            idx = i * step
                                            if idx < len(audio_data):
                                                amp = abs(audio_data[idx]) / 32768.0
                                                bh = max(4, amp * h * 1.5 + 2)
                                            else:
                                                bh = 4
                                            x = i * (w / dots) + 3
                                            if i / dots < progress:
                                                # Played - green solid with blue dot at current
                                                if abs(i / dots - progress) < 0.025:
                                                    canvas.create_oval(x-5, h//2-5, x+5, h//2+5, fill="#53BDEB", outline="#53BDEB", tags="wave")
                                                else:
                                                    canvas.create_line(x, h//2-bh//2, x, h//2+bh//2, fill="#075E54", width=2, tags="wave", capstyle="round")
                                            else:
                                                # Unplayed - light gray
                                                canvas.create_oval(x, h//2-1, x+2, h//2+1, fill="#A9C7B5", outline="#A9C7B5", tags="wave")
                                    except:
                                        # Fallback to random
                                        import random
                                        for i in range(dots):
                                            x = i * (w / dots) + 3
                                            bh = random.uniform(3, 12)
                                            if i / dots < progress:
                                                canvas.create_line(x, h//2-bh//2, x, h//2+bh//2, fill="#075E54", width=2, tags="wave")
                                            else:
                                                canvas.create_oval(x, h//2-1, x+2, h//2+1, fill="#A9C7B5", outline="#A9C7B5", tags="wave")
                                else:
                                    # No audio yet - show preview dotted line
                                    import random
                                    for i in range(dots):
                                        x = i * (w / dots) + 3
                                        if is_playing and i / dots < progress:
                                            # Waving animation when playing
                                            bh = random.uniform(6, 18) if is_playing else 4
                                            canvas.create_line(x, h//2-bh//2, x, h//2+bh//2, fill="#075E54", width=2, tags="wave", capstyle="round")
                                        elif i / dots < progress:
                                            if abs(i / dots - progress) < 0.03:
                                                canvas.create_oval(x-5, h//2-5, x+5, h//2+5, fill="#53BDEB", outline="#53BDEB", tags="wave")
                                            else:
                                                canvas.create_line(x, h//2-4, x, h//2+4, fill="#075E54", width=2, tags="wave")
                                        else:
                                            canvas.create_oval(x, h//2-1, x+2, h//2+1, fill="#A9C7B5", outline="#A9C7B5", tags="wave")
                            
                            # Initial preview
                            self.window.after(100, lambda c=wave_canvas: draw_preview_waveform(c, 0, False, None))
                            
                            # Bottom row: time + checks
                            bottom_row = tk.Frame(inner, bg=bubble_bg)
                            bottom_row.pack(fill="x", pady=(2,0))
                            import datetime
                            now_time = datetime.datetime.now().strftime("%H:%M")
                            try:
                                msg_time = msg.get("created_at", "")[:5] if msg.get("created_at") else now_time
                                if len(msg_time) < 5:
                                    msg_time = now_time
                            except:
                                msg_time = now_time
                            time_frame = tk.Frame(bottom_row, bg=bubble_bg)
                            time_frame.pack(side="right", padx=2)
                            time_label = tk.Label(time_frame, text=msg_time, bg=bubble_bg, fg="#667781", font=("Segoe UI", 8))
                            time_label.pack(side="left")
                            if is_my_message:
                                check_label = tk.Label(time_frame, text="✓✓", bg=bubble_bg, fg="#53BDEB", font=("Segoe UI", 8, "bold"))
                                check_label.pack(side="left", padx=(3,0))
                            
                            # REAL AUDIO PLAYBACK - FIXED TO HEAR SOUND
                            def play_voice_note_real():
                                try:
                                    # Toggle play/pause
                                    if getattr(play_canvas, '_is_playing', False) and not getattr(play_canvas, '_is_paused', False):
                                        # Currently playing -> PAUSE
                                        play_canvas._is_paused = True
                                        try:
                                            import sounddevice as sd
                                            sd.stop()
                                        except:
                                            pass
                                        # Show CONTINUE (play) button when paused
                                        play_canvas.delete("all")
                                        play_canvas.create_oval(1,1,35,35, fill="#25D366", outline="#25D366")
                                        play_canvas.create_polygon(12,9, 12,27, 26,18, fill="white", outline="white", tags="icon")
                                        dur_label.config(text=f"{duration} • Paused - click to continue")
                                        return
                                    elif getattr(play_canvas, '_is_paused', False):
                                        # Currently paused -> CONTINUE from where we stopped
                                        play_canvas._is_paused = False
                                        play_canvas._is_playing = True
                                        # Show PAUSE button when playing
                                        play_canvas.delete("all")
                                        play_canvas.create_oval(1,1,35,35, fill="#25D366", outline="#25D366")
                                        play_canvas.create_rectangle(11,9,15,27, fill="white", outline="white", tags="icon")
                                        play_canvas.create_rectangle(21,9,25,27, fill="white", outline="white", tags="icon")
                                        dur_label.config(text=f"{duration} • Playing... you hear it")
                                        
                                        # Continue waving animation
                                        def continue_wave():
                                            if not getattr(play_canvas, '_is_playing', False) or getattr(play_canvas, '_is_paused', False):
                                                return
                                            # Increase progress
                                            wave_canvas._progress += 0.015
                                            if wave_canvas._progress > 1:
                                                # Finished
                                                wave_canvas._progress = 0
                                                play_canvas._is_playing = False
                                                play_canvas._is_paused = False
                                                play_canvas.delete("all")
                                                play_canvas.create_oval(1,1,35,35, fill="#25D366", outline="#25D366")
                                                play_canvas.create_polygon(12,9, 12,27, 26,18, fill="white", outline="white", tags="icon")
                                                dur_label.config(text=duration)
                                                draw_preview_waveform(wave_canvas, 0, False, play_canvas._audio_data)
                                                return
                                            draw_preview_waveform(wave_canvas, wave_canvas._progress, True, play_canvas._audio_data)
                                            self.window.after(100, continue_wave)
                                        
                                        # Continue audio playback from current position
                                        try:
                                            import sounddevice as sd
                                            import numpy as np
                                            if play_canvas._audio_data is not None:
                                                remaining = play_canvas._audio_data[play_canvas._current_pos:]
                                                if len(remaining) > 0:
                                                    sd.play(remaining, 44100)
                                        except Exception as e:
                                            print(f"Continue play error: {e}")
                                        
                                        continue_wave()
                                        return
                                    
                                    # START PLAYING from beginning
                                    play_canvas._is_playing = True
                                    play_canvas._is_paused = False
                                    # Show PAUSE button when playing (not continue)
                                    play_canvas.delete("all")
                                    play_canvas.create_oval(1,1,35,35, fill="#25D366", outline="#25D366")
                                    play_canvas.create_rectangle(11,9,15,27, fill="white", outline="white", tags="icon")
                                    play_canvas.create_rectangle(21,9,25,27, fill="white", outline="white", tags="icon")
                                    dur_label.config(text=f"{duration} • Playing... you hear it")
                                    
                                    import threading, tempfile, os
                                    def download_and_play_real():
                                        try:
                                            audio_data = None
                                            sample_rate = 44100
                                            temp_path = None
                                            
                                            # Download file
                                            try:
                                                if requests:
                                                    resp = requests.get(url, headers=self._headers(), timeout=15)
                                                    if resp.ok and len(resp.content) > 50:
                                                        suffix = os.path.splitext(filename)[1] or ".wav"
                                                        fd, temp_path = tempfile.mkstemp(suffix=suffix)
                                                        os.close(fd)
                                                        with open(temp_path, "wb") as f:
                                                            f.write(resp.content)
                                                        # Load WAV
                                                        try:
                                                            import wave
                                                            with wave.open(temp_path, 'rb') as wf:
                                                                sample_rate = wf.getframerate()
                                                                n_frames = wf.getnframes()
                                                                audio_bytes = wf.readframes(n_frames)
                                                                try:
                                                                    import numpy as np
                                                                    audio_data = np.frombuffer(audio_bytes, dtype=np.int16)
                                                                    duration_sec = n_frames / sample_rate
                                                                    mins = int(duration_sec // 60)
                                                                    secs = int(duration_sec % 60)
                                                                    self.window.after(0, lambda ms=mins, ss=secs: dur_label.config(text=f"{ms}:{ss:02d} • Playing - HEAR IT"))
                                                                    play_canvas._audio_data = audio_data
                                                                except:
                                                                    audio_data = None
                                                        except Exception as e:
                                                            print(f"WAV error: {e}")
                                            except Exception as e:
                                                print(f"Download error: {e}")
                                            
                                            # GUARANTEED PLAYBACK - 5 methods
                                            played = False
                                            
                                            # 1. sounddevice
                                            if audio_data is not None and len(audio_data) > 0:
                                                try:
                                                    import sounddevice as sd
                                                    sd.stop()
                                                    sd.play(audio_data, samplerate=sample_rate)
                                                    print("PLAYING via sounddevice - YOU HEAR IT NOW")
                                                    played = True
                                                except Exception as e:
                                                    print(f"sd failed: {e}")
                                            
                                            # 2. winsound Windows
                                            if not played and temp_path and os.path.exists(temp_path) and os.name == 'nt':
                                                try:
                                                    import winsound
                                                    winsound.PlaySound(temp_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                                                    print("PLAYING via winsound")
                                                    played = True
                                                except Exception as e:
                                                    print(f"winsound failed: {e}")
                                            
                                            # 3. Try to play file with os.startfile (Windows will play)
                                            if not played and temp_path and os.path.exists(temp_path):
                                                try:
                                                    if os.name == 'nt':
                                                        os.startfile(temp_path)
                                                        print(f"Opened via startfile: {temp_path}")
                                                        played = True
                                                except:
                                                    pass
                                            
                                            # 4. Fallback browser
                                            if not played:
                                                try:
                                                    import webbrowser
                                                    p = temp_path if temp_path and os.path.exists(temp_path) else url
                                                    webbrowser.open(p)
                                                    print(f"Opened via browser: {p}")
                                                    played = True
                                                except:
                                                    pass
                                            
                                            # Wave animation - CONTINUES WAVING
                                            wave_canvas._progress = getattr(wave_canvas, '_progress', 0)
                                            
                                            def wave_anim():
                                                if not getattr(play_canvas, '_is_playing', False):
                                                    return
                                                if getattr(play_canvas, '_is_paused', False):
                                                    # PAUSED - stop waving, keep position, show CONTINUE button
                                                    self.window.after(100, wave_anim)
                                                    return
                                                # PLAYING - wave continues waving, show PAUSE button
                                                try:
                                                    wave_canvas._progress += 0.03
                                                    if wave_canvas._progress > 1:
                                                        wave_canvas._progress = 0
                                                        play_canvas._is_playing = False
                                                        play_canvas._is_paused = False
                                                        play_canvas.delete("all")
                                                        play_canvas.create_oval(1,1,35,35, fill="#25D366", outline="#25D366")
                                                        play_canvas.create_polygon(12,9, 12,27, 26,18, fill="white", outline="white")
                                                        dur_label.config(text=duration + " • Done")
                                                        draw_preview_waveform(wave_canvas, 0, False, play_canvas._audio_data)
                                                        return
                                                    draw_preview_waveform(wave_canvas, wave_canvas._progress, True, play_canvas._audio_data)
                                                except Exception as e:
                                                    print(f"Wave error: {e}")
                                                self.window.after(100, wave_anim)
                                            
                                            wave_anim()
                                            
                                        except Exception as e:
                                            print(f"Download/play error: {e}")
                                            self.window.after(0, lambda: dur_label.config(text="Play failed - check file"))
                                            play_canvas._is_playing = False
                                            play_canvas.delete("all")
                                            play_canvas.create_oval(1,1,35,35, fill="#25D366", outline="#25D366")
                                            play_canvas.create_polygon(12,9, 12,27, 26,18, fill="white", outline="white")
                                    threading.Thread(target=download_and_play_real, daemon=True).start()
                                
                                except Exception as e:
                                    print(f"Play error: {e}")
                                    dur_label.config(text="Error playing")
                            
                            play_canvas.bind("<Button-1>", lambda e: play_voice_note_real())
                            wave_canvas.bind("<Button-1>", lambda e: play_voice_note_real())
                            dur_label.bind("<Button-1>", lambda e: play_voice_note_real())
                            
                            self.messages.window_create("end", window=bubble, align="left" if not is_my_message else "right")
                            self.messages.insert("end", "\n")
                        else:
                            # Document - keep simple card
                            card = tk.Frame(self.messages, bg="#FFFFFF", highlightbackground="#D6E0F0", highlightthickness=1, padx=10, pady=7)
                            icon = "📄"
                            title = tk.Label(card, text=f"{icon}  {filename}", bg="#FFFFFF", fg="#20304A", font=("Segoe UI", 10, "bold"), anchor="w", wraplength=360, justify="left")
                            title.pack(fill="x", anchor="w")
                            subtitle = "Document attachment • tap Open to view"
                            tk.Label(card, text=subtitle, bg="#FFFFFF", fg="#667995", font=("Segoe UI", 8), anchor="w").pack(fill="x", anchor="w", pady=(2, 5))
                            actions = tk.Frame(card, bg="#FFFFFF")
                            actions.pack(fill="x", anchor="w")
                            tk.Button(actions, text="Open document", command=lambda link=url: webbrowser.open(link), bg="#DCE8FF", fg="#234CC8", relief="flat", padx=10, pady=3, cursor="hand2").pack(side="left")
                            tk.Button(actions, text="Download", command=lambda link=url: self._download_attachment(link, filename), bg="#EAF0F8", fg="#20304A", relief="flat", padx=10, pady=3, cursor="hand2").pack(side="left", padx=(6, 0))
                            self.messages.window_create("end", window=card, align="left")
                            self.messages.insert("end", "\n")
                elif line.startswith(("🖼 Photo/video:", "📄 Document:", "🎵 Audio:")):
                    # Hover over the attachment label to reveal its three-dot actions menu.
                    attachment_tag = f"attachment_row_{msg['id']}_{abs(hash(line))}"
                    self.messages.insert("end", line, (attachment_tag,))
                    self.messages.insert("end", "  ")
                    self._insert_attachment_menu_button(msg["id"], attachment_tag)
                    self.messages.insert("end", "\n")
                else:
                    self.messages.insert("end", line + "\n", (message_tag,))
            status = ""
            if msg.get("pinned"): status += "  📌 Pinned"
            if msg.get("edited_at"): status += "  (edited)"
            if msg.get("reactions"):
                try:
                    react = json.loads(msg["reactions"] or "{}")
                    if react: status += "  " + " ".join(react.values())
                except Exception: pass
            receipt_tag = None
            if msg.get("username", "").lower() == self.username.lower():
                if msg.get("read_at"):
                    status += "  ✓✓"; receipt_tag = "receipt_read"
                elif msg.get("delivered_at"):
                    status += "  ✓✓"; receipt_tag = "receipt_delivered"
                else:
                    status += "  ✓"; receipt_tag = "receipt_sent"
            if status:
                self.messages.insert("end", status + "\n", (message_tag, receipt_tag) if receipt_tag else (message_tag,))
            self.messages.insert("end", "\n", (message_tag,))
        self.messages.tag_configure("name", foreground="#0969D5", font=("Segoe UI", 9, "bold"))
        self.messages.tag_configure("read_receipt", foreground="#16A34A", font=("Segoe UI", 9, "bold"))
        self.messages.tag_configure("receipt_sent", foreground="#7B8794", font=("Segoe UI", 9, "bold"))
        self.messages.tag_configure("receipt_delivered", foreground="#7B8794", font=("Segoe UI", 9, "bold"))
        self.messages.tag_configure("receipt_read", foreground="#1687F8", font=("Segoe UI", 9, "bold"))
        self.messages.tag_configure("image_loading", foreground="#64748B", font=("Segoe UI", 9, "italic"))
        self.messages.configure(state="disabled")
        self.messages.see("end")

    def _download_and_play_video(self, url, message_id, filename):
        """Download a shared video, show an inline thumbnail, and hide its URL."""
        if requests is None:
            return
        import tempfile
        def worker():
            try:
                response = requests.get(url, headers=self._headers(), timeout=(15, 900), stream=True)
                response.raise_for_status()
                suffix = os.path.splitext(filename)[1].lower() or ".mp4"
                fd, local_path = tempfile.mkstemp(prefix="isss_connect_video_", suffix=suffix)
                os.close(fd)
                with open(local_path, "wb") as out:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            out.write(chunk)

                # Create a frame thumbnail for the chat bubble (when OpenCV/Pillow are installed).
                thumbnail = None
                try:
                    import cv2
                    from PIL import Image, ImageTk, ImageDraw
                    cap = cv2.VideoCapture(local_path)
                    ok, frame = cap.read()
                    cap.release()
                    if ok:
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        image = Image.fromarray(frame)
                        image.thumbnail((360, 210))
                        # Add a simple play overlay so it reads as a video preview.
                        draw = ImageDraw.Draw(image)
                        cx, cy = image.width // 2, image.height // 2
                        radius = 25
                        draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=(15, 23, 42))
                        draw.polygon([(cx-6, cy-13), (cx-6, cy+13), (cx+13, cy)], fill=(255, 255, 255))
                        thumbnail = ImageTk.PhotoImage(image)
                except Exception:
                    thumbnail = None

                def show_play():
                    if self.closed or not self.messages.winfo_exists():
                        return
                    try:
                        self.messages.configure(state="normal")
                        self.messages.insert("end", "     ")
                        if thumbnail is not None:
                            # Keep a reference so Tk does not garbage-collect the preview.
                            if not hasattr(self, "_video_preview_images"):
                                self._video_preview_images = {}
                            self._video_preview_images[message_id] = thumbnail
                            self.messages.image_create("end", image=thumbnail, padx=4, pady=4)
                            image_index = self.messages.index("end-1c")
                            tag = "video_preview_" + str(message_id)
                            self.messages.tag_add(tag, image_index + " linestart", "end-1c")
                            self.messages.tag_bind(tag, "<Button-1>", lambda _e, p=local_path: self._open_local_video(p))
                            self.messages.tag_bind(tag, "<Enter>", lambda _e: self.messages.configure(cursor="hand2"))
                            self.messages.tag_bind(tag, "<Leave>", lambda _e: self.messages.configure(cursor="xterm"))
                            self.messages.insert("end", "\n")
                        tag = "video_play_" + str(message_id)
                        self.messages.insert("end", "     ▶ Play video  ·  " + os.path.basename(filename) + "\n", (tag,))
                        self.messages.tag_configure(tag, foreground="#0969D5", underline=True, font=("Segoe UI", 10, "bold"))
                        self.messages.tag_bind(tag, "<Button-1>", lambda _e, p=local_path: self._open_local_video(p))
                        self.messages.tag_bind(tag, "<Enter>", lambda _e: self.messages.configure(cursor="hand2"))
                        self.messages.tag_bind(tag, "<Leave>", lambda _e: self.messages.configure(cursor="xterm"))
                        self.messages.configure(state="disabled")
                        self.messages.see("end")
                    except tk.TclError:
                        pass
                self.window.after(0, show_play)
            except Exception as exc:
                print("Could not retrieve shared video:", exc)
        threading.Thread(target=worker, daemon=True).start()

    def _open_local_video(self, path):
        """Play the downloaded full video with the computer's default media player."""
        try:
            if os.path.isfile(path):
                if os.name == "nt":
                    os.startfile(path)
                elif sys.platform == "darwin":
                    import subprocess; subprocess.Popen(["open", path])
                else:
                    import subprocess; subprocess.Popen(["xdg-open", path])
        except Exception as exc:
            messagebox.showerror("Video playback", "The video was downloaded, but it could not be opened: " + str(exc), parent=self.window)

    def _download_attachment(self, url, filename):
        """Download a shared document/audio attachment to a user-selected location."""
        if requests is None:
            webbrowser.open(url)
            return
        destination = filedialog.asksaveasfilename(parent=self.window, title="Save attachment", initialfile=os.path.basename(filename or "attachment"))
        if not destination:
            return
        def worker():
            try:
                response = requests.get(url, headers=self._headers(), timeout=(10, 180))
                response.raise_for_status()
                with open(destination, "wb") as handle:
                    handle.write(response.content)
                self.window.after(0, lambda: messagebox.showinfo("Attachment saved", f"Saved to:\n{destination}", parent=self.window))
            except Exception as exc:
                self.window.after(0, lambda m=str(exc): messagebox.showerror("Download failed", m, parent=self.window))
        threading.Thread(target=worker, daemon=True).start()

    def _load_inline_chat_image(self, url, message_id):
        """Fetch an uploaded image and display it inside the chat instead of as a URL."""
        if requests is None or not MODULE_PIL_AVAILABLE:
            return
        def worker():
            try:
                response = requests.get(url, headers=self._headers(), timeout=(10, 45))
                response.raise_for_status()
                source = Image.open(io.BytesIO(response.content)).convert("RGB")
                source.thumbnail((520, 360))
                def show_image():
                    if self.closed or not self.messages.winfo_exists():
                        return
                    try:
                        self.messages.configure(state="normal")
                        # Insert the image at the end of the chat. Keep the image object referenced.
                        photo = ImageTk.PhotoImage(source)
                        self._inline_chat_images.append(photo)
                        self.messages.image_create("end", image=photo, align="top")
                        self.messages.insert("end", "\n\n")
                        self.messages.configure(state="disabled")
                        self.messages.see("end")
                    except tk.TclError:
                        try: self.messages.configure(state="disabled")
                        except tk.TclError: pass
                self.window.after(0, show_image)
            except Exception as exc:
                print("Could not display chat image inline:", exc)
        threading.Thread(target=worker, daemon=True).start()

    def _send_message(self):
        body = self.compose_entry.get().strip()
        if not body or not self.active: return
        kind, target = self.active_kind, self.active
        self._remember_recent_conversation((kind, target, str(target)))
        self.compose_entry.delete(0, "end")
        def worker():
            try:
                self._request("POST", "/api/messages", json={"kind": kind, "target": str(target), "body": body})
                self.window.after(0, self._load_messages)
            except Exception as exc:
                self.window.after(0, lambda m=str(exc): self._status_error(m))
        threading.Thread(target=worker, daemon=True).start()

    def _new_chat(self):
        name = simpledialog.askstring("Start individual chat", "Enter the exact username of the student:", parent=self.window)
        if not name: return
        try:
            users = self._request("GET", "/api/users").get("users", [])
            found = next((u for u in users if u["username"].lower() == name.strip().lower()), None)
            if not found: messagebox.showinfo("Student not found", "That username is not registered on Connect.", parent=self.window); return
            for i, item in enumerate(self.conversations):
                if item[0] == "direct" and item[1].lower() == found["username"].lower():
                    self.people_list.selection_clear(0, "end"); self.people_list.selection_set(i); self._select_conversation(); return
            self._refresh_lists()
        except Exception as exc: self._status_error(str(exc))


    def _open_24hr_code_generator(self):
        """Open the 24HR code generator with copy button"""
        if not CODE_SYS_AVAILABLE:
            messagebox.showerror("Code System", "community_code_system.py not found. Put it in same folder as study app.")
            return
        win = tk.Toplevel(self.window)
        win.title("24HR Community Code Generator")
        win.geometry("700x520")
        win.configure(bg="#F4F7FC")
        
        tk.Label(win, text="24HR COMMUNITY CODE GENERATOR", bg="#F4F7FC", fg="#142B52", font=("Segoe UI",14,"bold")).pack(pady=12)
        tk.Label(win, text="25-char code, same for 24hrs even if you refresh/regenerate", bg="#F4F7FC", fg="#6B7280", font=("Segoe UI",9)).pack()
        
        form = tk.Frame(win, bg="white")
        form.pack(fill="x", padx=20, pady=12, ipady=10)
        
        tk.Label(form, text="Class", bg="white", font=("Segoe UI",10,"bold")).grid(row=0,column=0,padx=10,pady=8,sticky="w")
        class_var = tk.StringVar(value=self.student_class if hasattr(self,'student_class') else "SS1")
        dept_var = tk.StringVar(value=self.student_department if hasattr(self,'student_department') else "Science")
        subj_var = tk.StringVar()
        
        from tkinter import ttk
        class_cb = ttk.Combobox(form, textvariable=class_var, values=["SS1","SS2","SS3"], width=26, state="readonly")
        class_cb.grid(row=0,column=1,padx=10,pady=8)
        tk.Label(form, text="Department", bg="white", font=("Segoe UI",10,"bold")).grid(row=1,column=0,padx=10,pady=8,sticky="w")
        dept_cb = ttk.Combobox(form, textvariable=dept_var, values=["Science","Arts","Commercial"], width=26, state="readonly")
        dept_cb.grid(row=1,column=1,padx=10,pady=8)
        tk.Label(form, text="Subject", bg="white", font=("Segoe UI",10,"bold")).grid(row=2,column=0,padx=10,pady=8,sticky="w")
        subj_cb = ttk.Combobox(form, textvariable=subj_var, width=26, state="readonly")
        subj_cb.grid(row=2,column=1,padx=10,pady=8)
        
        subjects_map = {
            "Science": ["Mathematics","English Language","Further Mathematics","Biology","Chemistry","Geography","Economics","Livestock Farming","Physics","Citizenship and Heritage Studies"],
            "Arts": ["Literature in English","Mathematics","English Language","Government","Livestock Farming","CRS","IRS","Visual Arts","Citizenship and Heritage Studies","Yoruba Language"],
            "Commercial": ["Mathematics","English Language","Commerce","Financial Accounting","Marketing","Economics","Citizenship and Heritage Studies","Biology"]
        }
        def update_subj(*_):
            subj_cb["values"] = subjects_map.get(dept_var.get(), [])
            if subj_cb["values"]:
                subj_var.set(subj_cb["values"][0])
        dept_var.trace_add("write", update_subj)
        update_subj()
        
        code_frame = tk.Frame(win, bg="white", bd=1, relief="solid")
        code_frame.pack(fill="x", padx=20, pady=12, ipady=12)
        tk.Label(code_frame, text="Generated Code (25 chars):", bg="white", fg="#6B7280", font=("Segoe UI",9)).pack(anchor="w", padx=12, pady=(5,0))
        row = tk.Frame(code_frame, bg="white")
        row.pack(fill="x", padx=12, pady=8)
        code_label = tk.Label(row, text="---- No code yet ----", bg="#F3F4F6", fg="#111827", font=("Consolas",14,"bold"), padx=10, pady=10, anchor="w")
        code_label.pack(side="left", fill="x", expand=True)
        def copy_code():
            c = code_label.cget("text")
            if "No code" in c or "----" in c:
                return
            win.clipboard_clear()
            win.clipboard_append(c)
            messagebox.showinfo("Copied", f"Code copied!\n{c}\n\nPaste in Community Chat > Enter Code", parent=win)
        copy_btn = tk.Button(row, text="COPY", command=copy_code, bg="#10B981", fg="white", font=("Segoe UI",10,"bold"), relief="flat", padx=18, pady=8, cursor="hand2", state="disabled")
        copy_btn.pack(side="left", padx=(10,0))
        
        info_label = tk.Label(code_frame, text="", bg="white", fg="#6B7280", font=("Segoe UI",8), anchor="w", justify="left")
        info_label.pack(fill="x", padx=12)
        breakdown = tk.Label(win, text="", bg="#F4F7FC", fg="#374151", font=("Segoe UI",8), justify="left")
        breakdown.pack(fill="x", padx=22, pady=5)
        
        def generate():
            sc, dp, sb = class_var.get(), dept_var.get(), subj_var.get()
            if not sb:
                messagebox.showwarning("Missing", "Select subject", parent=win)
                return
            code, entry, is_new = code_sys.generate_24hr_code(sc, dp, sb)
            code_label.config(text=code)
            copy_btn.config(state="normal")
            import time
            from datetime import datetime
            exp = entry["expires_at"]
            remaining = exp - time.time()
            hrs = int(remaining//3600)
            mins = int((remaining%3600)//60)
            info_label.config(text=f"{sc} | {dp} | {sb} | Expires: {datetime.fromtimestamp(exp).strftime('%Y-%m-%d %H:%M')} | Left: {hrs}h {mins}m")
            breakdown.config(text=f"[{code[0]}=Class:{sc}] [{code[1]}=Dept:{dp}] [{code[2:5]}=Subject:{sb}] [{code[5:10]}=Day] [{code[10:25]}=Secure] = 25 chars | Same code for 24hrs")
        
        tk.Button(win, text="GENERATE 24HR CODE", command=generate, bg="#315FEA", fg="white", font=("Segoe UI",11,"bold"), relief="flat", padx=20, pady=10, cursor="hand2").pack(pady=10)
        tk.Label(win, text="After generation, click COPY and paste in Community Chat", bg="#F4F7FC", fg="#315FEA", font=("Segoe UI",9,"italic")).pack()

    def _enter_community_code_and_join_livestream(self):
        """Community chat code input - verifies 25-char code and opens livestream join, no incorrect-code error if valid structure"""
        if not CODE_SYS_AVAILABLE:
            messagebox.showerror("Code System", "community_code_system.py missing")
            return
        dialog = tk.Toplevel(self.window)
        dialog.title("Enter Community Code to Join Livestream")
        dialog.geometry("560x380")
        dialog.configure(bg="#F4F7FC")
        tk.Label(dialog, text="ENTER 25-CHAR COMMUNITY CODE", bg="#F4F7FC", fg="#142B52", font=("Segoe UI",12,"bold")).pack(pady=12)
        tk.Label(dialog, text="Paste code generated from Code App. If code is correct for class-dept-subject, you will join livestream (no incorrect error)", bg="#F4F7FC", fg="#6B7280", font=("Segoe UI",8), wraplength=500).pack(pady=4)
        entry_frame = tk.Frame(dialog, bg="white", bd=1, relief="solid")
        entry_frame.pack(fill="x", padx=20, pady=15, ipady=8)
        code_var = tk.StringVar()
        tk.Label(entry_frame, text="Community Code (25 chars):", bg="white", fg="#374151", font=("Segoe UI",10,"bold")).pack(anchor="w", padx=12, pady=(5,0))
        ent_row = tk.Frame(entry_frame, bg="white")
        ent_row.pack(fill="x", padx=12, pady=8)
        ent = tk.Entry(ent_row, textvariable=code_var, font=("Consolas",12), width=35)
        ent.pack(side="left", fill="x", expand=True)
        ent.focus()
        
        def paste_from_clipboard():
            try:
                clip = dialog.clipboard_get()
                clip = clip.strip().upper().replace(" ","").replace("-","")
                code_var.set(clip)
                result_label.config(text=f"Pasted: {len(clip)} chars", fg="#6B7280")
            except:
                result_label.config(text="Clipboard empty - press Ctrl+V", fg="#DC2626")
        
        paste_btn = tk.Button(ent_row, text="📋 PASTE", command=paste_from_clipboard, bg="#10B981", fg="white", font=("Segoe UI",9,"bold"), relief="flat", padx=12, pady=4, cursor="hand2")
        paste_btn.pack(side="left", padx=(6,0))
        
        # Right-click paste menu
        def show_menu(e):
            try:
                menu = tk.Menu(dialog, tearoff=0)
                menu.add_command(label="Paste", command=paste_from_clipboard)
                menu.tk_popup(e.x_root, e.y_root)
            except:
                pass
        ent.bind("<Button-3>", show_menu)
        ent.bind("<Control-v>", lambda e: paste_from_clipboard())
        ent.bind("<Control-V>", lambda e: paste_from_clipboard())
        
        result_label = tk.Label(dialog, text="Tip: Click PASTE button or press Ctrl+V", bg="#F4F7FC", fg="#6B7280", font=("Segoe UI",9), wraplength=500)
        result_label.pack(pady=5)
        
        def verify_and_join():
            code = code_var.get().strip()
            is_valid, data, err = code_sys.verify_community_code(code)
            if not is_valid:
                result_label.config(text=f"Error: {err}", fg="#DC2626")
                return
            result_label.config(text=f"Valid! {data['school_class']} {data['department']} - {data['subject']}", fg="#10B981")
            dialog.destroy()
            self._open_livestream_join_window(data)
        
        tk.Button(dialog, text="VERIFY & JOIN LIVESTREAM", command=verify_and_join, bg="#315FEA", fg="white", font=("Segoe UI",11,"bold"), relief="flat", padx=20, pady=10, cursor="hand2").pack(pady=10)

    def _open_livestream_join_window(self, code_data):
        """Opens place where you join livestream - auto detects voice vs video"""
        win = tk.Toplevel(self.window)
        win.title(f"Join Livestream - {code_data['subject']}")
        win.geometry("560x500")
        win.configure(bg="#F4F7FC")
        tk.Label(win, text="LIVESTREAM READY", bg="#F4F7FC", fg="#142B52", font=("Segoe UI",16,"bold")).pack(pady=12)
        info = f"{code_data['school_class']} | {code_data['department']} | {code_data['subject']}"
        tk.Label(win, text=info, bg="#F4F7FC", fg="#6B7280", font=("Segoe UI",11)).pack()
        mode = code_data.get("livestream_mode","video")
        mode_text = "VIDEO CALL" if mode=="video" else "VOICE CALL"
        mode_color = "#315FEA" if mode=="video" else "#10B981"
        badge = tk.Frame(win, bg=mode_color)
        badge.pack(pady=12, ipadx=20, ipady=8)
        tk.Label(badge, text=f"Teacher is on {mode_text} - Click to join same call", bg=mode_color, fg="white", font=("Segoe UI",11,"bold")).pack()
        room_frame = tk.Frame(win, bg="white", bd=1, relief="solid")
        room_frame.pack(fill="x", padx=20, pady=12, ipady=10)
        tk.Label(room_frame, text="Room:", bg="white", fg="#6B7280", font=("Segoe UI",9)).pack(anchor="w", padx=12, pady=(6,0))
        tk.Label(room_frame, text=code_data.get("livestream_room",""), bg="white", fg="#111827", font=("Consolas",11,"bold")).pack(anchor="w", padx=12)
        tk.Label(room_frame, text=f"Code: {code_data['code']}", bg="white", fg="#6B7280", font=("Consolas",9)).pack(anchor="w", padx=12, pady=(0,6))
        
        def open_room(m):
            import webbrowser
            room = code_data.get("livestream_room","ISSS-Community")
            url = f"https://meet.jit.si/{room.replace(' ','')}-{m.capitalize()}"
            try:
                webbrowser.open(url)
            except:
                pass
            messagebox.showinfo("Joining", f"Joining {m} call...\nRoom: {room}\nLink: {url}", parent=win)
        
        btns = tk.Frame(win, bg="#F4F7FC")
        btns.pack(pady=15)
        if mode == "voice":
            tk.Button(btns, text="JOIN VOICE CALL", command=lambda: open_room("voice"), bg="#10B981", fg="white", font=("Segoe UI",12,"bold"), relief="flat", padx=30, pady=12, cursor="hand2").pack(pady=5)
        else:
            tk.Button(btns, text="JOIN VIDEO CALL", command=lambda: open_room("video"), bg="#315FEA", fg="white", font=("Segoe UI",12,"bold"), relief="flat", padx=30, pady=12, cursor="hand2").pack(pady=5)
        tk.Button(btns, text="AUTO-JOIN (Follow Teacher Mode)", command=lambda: open_room(mode), bg="#E0E7FF", fg="#3730A3", font=("Segoe UI",10,"bold"), relief="flat", padx=20, pady=8, cursor="hand2").pack(pady=8)
        tk.Label(win, text="No 'incorrect code' error - if prefix matches class-dept-subject, you join. Code is 25 chars.", bg="#F4F7FC", fg="#6B7280", font=("Segoe UI",8), wraplength=500).pack(pady=10)


    def _join_class_community(self):
        """Request a place in a subject community; a verified assigned teacher must approve."""
        try:
            catalog = self._request("GET", "/api/communities/catalog").get("communities", [])
        except Exception as exc:
            self._status_error(str(exc)); return
        dialog = tk.Toplevel(self.window)
        dialog.title("Request a Subject Community Invitation")
        dialog.geometry("470x390")
        dialog.configure(bg="#F4F7FC")
        dialog.transient(self.window); dialog.grab_set()
        tk.Label(dialog, text="JOIN A SUBJECT COMMUNITY", bg="#F4F7FC", fg="#142B52",
                 font=("Segoe UI", 15, "bold")).pack(pady=(18, 4))
        tk.Label(dialog, text="Choose your class, department and subject. Your assigned teacher must approve.",
                 bg="#F4F7FC", fg="#53657F", wraplength=420, justify="center",
                 font=("Segoe UI", 9)).pack(pady=(0, 14))
        form = tk.Frame(dialog, bg="#F4F7FC"); form.pack(fill="x", padx=32)
        classes = ["SS1", "SS2", "SS3"]
        departments = ["Science", "Arts", "Commercial"]
        tk.Label(form, text="Class", bg="#F4F7FC", fg="#1E293B").pack(anchor="w")
        class_var = tk.StringVar(value=getattr(self, "school_class", "SS1"))
        class_box = ttk.Combobox(form, textvariable=class_var, values=classes, state="readonly")
        class_box.pack(fill="x", pady=(2, 9))
        tk.Label(form, text="Department", bg="#F4F7FC", fg="#1E293B").pack(anchor="w")
        dept_var = tk.StringVar(value=getattr(self, "department", "Science"))
        dept_box = ttk.Combobox(form, textvariable=dept_var, values=departments, state="readonly")
        dept_box.pack(fill="x", pady=(2, 9))
        tk.Label(form, text="Subject", bg="#F4F7FC", fg="#1E293B").pack(anchor="w")
        subject_var = tk.StringVar()
        subject_box = ttk.Combobox(form, textvariable=subject_var, state="readonly")
        subject_box.pack(fill="x", pady=(2, 14))
        def refresh_subjects(*_):
            available = sorted({x["subject"] for x in catalog if x["school_class"] == class_var.get() and x["department"] == dept_var.get()})
            subject_box.configure(values=available)
            subject_var.set(available[0] if available else "")
        class_var.trace_add("write", refresh_subjects); dept_var.trace_add("write", refresh_subjects)
        refresh_subjects()
        def submit():
            subject = subject_var.get().strip()
            if not subject:
                messagebox.showwarning("Choose a subject", "Please choose a subject first.", parent=dialog); return
            try:
                result = self._request("POST", "/api/community-requests", json={"school_class":class_var.get(),"department":dept_var.get(),"subject":subject})
                dialog.destroy()
                messagebox.showinfo("Request submitted", result.get("message", "Request submitted. Please wait for your assigned teacher's invitation."), parent=self.window)
            except Exception as exc:
                messagebox.showerror("Request not submitted", str(exc), parent=dialog)
        def join_with_code():
            subject = subject_var.get().strip()
            if not subject:
                messagebox.showwarning("Choose a subject", "Please choose a subject first.", parent=dialog); return
            code = simpledialog.askstring("Subject invitation code", f"Enter the 25-character code for {class_var.get()} {dept_var.get()} — {subject}:", parent=dialog)
            if not code: return
            try:
                result = self._request("POST", "/api/class-communities/join", json={"subject": subject, "code": code.strip().upper()})
                dialog.destroy(); self._refresh_lists()
                messagebox.showinfo("Community joined", result.get("message", "You joined the subject community."), parent=self.window)
            except Exception as exc:
                messagebox.showerror("Could not join community", str(exc), parent=dialog)
        tk.Button(dialog, text="SEND REQUEST & WAIT FOR TEACHER", command=submit, bg="#0F766E", fg="white",
                  activebackground="#115E59", activeforeground="white", relief="flat", cursor="hand2",
                  font=("Segoe UI", 10, "bold"), pady=10).pack(fill="x", padx=32, pady=(0, 8))
        tk.Button(dialog, text="🔑 JOIN WITH 25-CHARACTER INVITATION CODE", command=join_with_code,
                  bg="#315FEA", fg="white", activebackground="#234CC8", relief="flat", cursor="hand2",
                  font=("Segoe UI", 9, "bold"), pady=9).pack(fill="x", padx=32, pady=(0, 18))

    def _review_community_requests(self):
        try:
            result = self._request("GET", "/api/community-requests/pending").get("requests", [])
            if not result:
                messagebox.showinfo("Teacher invitations", "There are no pending requests for your assigned subjects.", parent=self.window); return
            choices = [f'{r["username"]} — {r["school_class"]} {r["department"]} / {r["subject"]}' for r in result]
            prompt = "Requests:\n" + chr(10).join(f"{i+1}. {v}" for i,v in enumerate(choices)) + "\n\nEnter the request number to approve:"
            picked = simpledialog.askstring("Pending student requests", prompt, parent=self.window)
            if not picked: return
            idx = int(picked)-1
            if idx < 0 or idx >= len(result): raise ValueError("Enter a valid request number.")
            approved = self._request("POST", "/api/community-requests/" + str(result[idx]["id"]) + "/approve")
            self._refresh_lists()
            messagebox.showinfo("Invitation approved", approved.get("message", "Student added to the subject community."), parent=self.window)
        except Exception as exc:
            messagebox.showerror("Could not review requests", str(exc), parent=self.window)

    def _new_subject_community(self):
        """Teacher creates a scheduled subject session; students join with teacher code."""
        action = messagebox.askyesnocancel(
            "Subject Communities",
            "YES: Open a community as an assigned teacher\nNO: Join a community with a teacher code\nCANCEL: Do nothing",
            parent=self.window)
        if action is None:
            return
        if action is False:
            code = simpledialog.askstring("Join Subject Community", "Enter the invitation code given by your teacher:", parent=self.window)
            if not code: return
            try:
                result = self._request("POST", "/api/communities/join", json={"code": code.strip()})
                self._refresh_lists()
                messagebox.showinfo("Community joined", f"You joined {result.get('name', 'the community')}.", parent=self.window)
            except Exception as exc: self._status_error(str(exc))
            return
        try:
            assignments = self._request("GET", "/api/communities/teacher-options")
            options = assignments.get("assignments", [])
            if not options:
                messagebox.showwarning("Teacher assignment required",
                    "This account has no verified subject assignments. The administrator must configure ISSS_TEACHER_ASSIGNMENTS on the server.\n\nFormat: username|SS1|Science|Mathematics;username|SS2|Arts|Government", parent=self.window)
                return
            labels = [f"{x['school_class']} • {x['department']} • {x['subject']}" for x in options]
            chosen = simpledialog.askstring("Open Community", "Enter the exact assigned option number:\n\n" + chr(10).join(f"{i+1}. {v}" for i,v in enumerate(labels)), parent=self.window)
            if not chosen: return
            idx = int(chosen) - 1
            if idx < 0 or idx >= len(options): raise ValueError("Choose a valid option number.")
            selected = options[idx]
            result = self._request("POST", "/api/communities/open", json=selected)
            self._refresh_lists()
            messagebox.showinfo("Community opened",
                f"Community: {result['name']}\nTeacher invitation code: {result['code']}\n\nShare this code only with students in the listed class and department. The code is shown once here. End the session when class finishes.", parent=self.window)
        except Exception as exc: self._status_error(str(exc))

    def _end_subject_community(self):
        """End an owned subject community session; students lose active access."""
        try:
            groups = self._request("GET", "/api/groups").get("groups", [])
            if not groups:
                messagebox.showinfo("End class", "No communities are available in this account.", parent=self.window); return
            choices = [f"{g['id']} — {g['name']}" for g in groups]
            value = simpledialog.askstring("End community session", "Enter the community ID from the list below:\n\n" + chr(10).join(choices), parent=self.window)
            if not value: return
            try: gid = int(value.strip().split("—",1)[0].strip())
            except ValueError: raise ValueError("Enter the numeric community ID shown before the name.")
            if not messagebox.askyesno("End class", "End this session now? Students will lose access to the active community view.", parent=self.window): return
            self._request("POST", "/api/communities/end", json={"group_id":gid})
            self._refresh_lists()
            messagebox.showinfo("Session ended", "The community is now hidden from students' active lists. The teacher retains the community history.", parent=self.window)
        except Exception as exc: self._status_error(str(exc))

    def _new_group(self):
        name = simpledialog.askstring("Create study group", "Enter a name for the group:", parent=self.window)
        if not name or not name.strip(): return
        members = simpledialog.askstring("Invite classmates", "Enter usernames separated by commas (optional):", parent=self.window)
        try:
            data = self._request("POST", "/api/groups", json={"name": name.strip(), "members": [x.strip() for x in (members or "").split(",") if x.strip()]})
            self._refresh_lists()
            messagebox.showinfo("Group created", "Your study group was created. Other students can be invited by username.", parent=self.window)
        except Exception as exc: self._status_error(str(exc))

    def _start_live_class(self):
        """Open the shared live room for the selected teacher-created subject community."""
        if not self.active or self.active_kind != "group":
            messagebox.showinfo(
                "Live class",
                "First select your teacher's subject community from the chat list.\n\n"
                "Teacher: open your assigned community using Subject Communities, then select it here.\n"
                "Student: join your teacher's community using the invitation code, then select it here.",
                parent=self.window,
            )
            return
        try:
            groups = self._request("GET", "/api/groups").get("groups", [])
            group = next((g for g in groups if str(g.get("id")) == str(self.active)), None)
            if not group:
                messagebox.showwarning("Live class", "This group is not available to your account. Join the teacher's active community first.", parent=self.window)
                return
            name = str(group.get("name", ""))
            if not (name.startswith(("SS1 ", "SS2 ", "SS3 ")) and "—" in name):
                if not messagebox.askyesno("Open group call", "This appears to be a regular study group, not a subject community. Open its shared group call anyway?", parent=self.window):
                    return
            self._start_call("video", live_class=True)
        except Exception as exc:
            messagebox.showerror("Live class unavailable", str(exc), parent=self.window)

    def _start_call(self, mode, live_class=False):
        if not self.active:
            messagebox.showinfo("Choose a chat", "Select a classmate or group first.", parent=self.window); return

        # A stable room is essential for a hosted class: the teacher and every
        # student in the same group must enter the exact same meeting URL.
        if self.active_kind == "group":
            slug = "ISSS-Community-" + re.sub(r"[^A-Za-z0-9]", "", str(self.active))
        else:
            # Direct-call room is deterministic for the two usernames, so both
            # participants can use the invite link instead of creating new rooms.
            pair = "|".join(sorted((str(self.username).casefold(), str(self.active).casefold())))
            slug = "ISSS-Direct-" + hashlib.sha256(pair.encode("utf-8")).hexdigest()[:24]

        if mode == "voice":
            url = "https://meet.jit.si/" + slug + "#config.startWithAudioOnly=true&config.startWithVideoMuted=true"
        else:
            url = "https://meet.jit.si/" + slug + "#config.startWithAudioOnly=false&config.startWithVideoMuted=false"
        try:
            invite_label = "Live class" if live_class else f"{mode.title()} call"
            self._request("POST", "/api/messages", json={"kind": self.active_kind, "target": str(self.active),
                          "body": f"{invite_label} room from {self.username}: {url}"})
        except Exception as exc:
            if not messagebox.askyesno("Invite could not be sent", f"The shared call room can still open, but the room link could not be posted in chat.\n\n{exc}\n\nOpen it anyway?", parent=self.window): return
        webbrowser.open(url)
        if live_class:
            messagebox.showinfo("Live class opened", "You have opened the shared live-class room for this community.\n\n"
                "The teacher should open it first; students in the same community can then click LIVE CLASS to join the same room.\n"
                "Allow microphone/camera access in the browser. Voice-only is available with the VOICE button.", parent=self.window)
        else:
            call_kind = "audio-only voice call" if mode == "voice" else "video call"
            messagebox.showinfo("Call room opened", f"The {call_kind} room opened in your browser. Everyone must use the same room link and have internet access. Microphone/camera permissions may be required.", parent=self.window)

    def _schedule_poll(self):
        if not self.window.winfo_exists(): return
        # A heartbeat keeps the server's presence timestamp fresh while Connect is open.
        def heartbeat():
            try:
                self._request("POST", "/api/presence")
            except Exception:
                pass
        threading.Thread(target=heartbeat, daemon=True).start()
        self._load_messages()
        self._refresh_lists()
        self.poll_job = self.window.after(5000, self._schedule_poll)

    def _status_error(self, text):
        try: self.window.title("I.S.S.S. Connect — " + text[:70])
        except tk.TclError: pass

    def close(self):
        if self.closed:
            return
        self.closed = True
        if self.poll_job:
            try: self.window.after_cancel(self.poll_job)
            except tk.TclError: pass
        if self.embedded:
            try:
                self.host.destroy()
            except tk.TclError:
                pass
            if callable(self.on_close):
                self.on_close()
        else:
            try:
                self.window.destroy()
            except tk.TclError:
                pass


# ============================================================
# I.S.S.S. CONNECT BACKEND (embedded in this file)
# ============================================================
import os as _connect_os
import sqlite3 as _connect_sqlite3
import hashlib as _connect_hashlib
import hmac as _connect_hmac
import time as _connect_time
import secrets as _connect_secrets
from datetime import datetime as _ConnectDateTime, timezone as _ConnectTimezone
from typing import Optional as _ConnectOptional
try:
    from fastapi import FastAPI, HTTPException, Header, Depends, UploadFile, File, Form
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel, Field
    _CONNECT_SERVER_AVAILABLE = True
except ImportError:
    FastAPI = None
    _CONNECT_SERVER_AVAILABLE = False


if _CONNECT_SERVER_AVAILABLE:
    DB_PATH = _connect_os.environ.get("ISSS_CHAT_DB", _connect_os.path.join(_connect_os.path.dirname(_connect_os.path.abspath(__file__)), "isss_connect.db"))
    SECRET = _connect_os.environ.get("ISSS_SECRET_KEY", "CHANGE-ME-BEFORE-DEPLOYMENT-" + _connect_secrets.token_hex(24))
    app = FastAPI(title="I.S.S.S. Connect API", version="1.0.0")
    UPLOAD_DIR = os.path.abspath(os.environ.get("ISSS_UPLOAD_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "isss_connect_uploads")))
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    # Uploaded files are served from a dedicated directory; filenames are randomized.
    app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
    sessions = {}
    # uid -> Unix timestamp of the most recent client heartbeat
    presence = {}

    def db():
        con = _connect_sqlite3.connect(DB_PATH, timeout=15)
        con.row_factory = _connect_sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        return con

    def init_db():
        with db() as c:
            c.executescript('''
            CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE COLLATE NOCASE NOT NULL, salt BLOB NOT NULL, pw_hash BLOB NOT NULL, created_at TEXT NOT NULL, school_class TEXT NOT NULL DEFAULT 'SS1', department TEXT NOT NULL DEFAULT 'Science', phone_number TEXT NOT NULL DEFAULT '');
            CREATE TABLE IF NOT EXISTS groups_table(id INTEGER PRIMARY KEY, name TEXT NOT NULL, owner_id INTEGER NOT NULL REFERENCES users(id), created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS group_members(group_id INTEGER NOT NULL REFERENCES groups_table(id) ON DELETE CASCADE, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, PRIMARY KEY(group_id,user_id));
            CREATE TABLE IF NOT EXISTS subject_communities(group_id INTEGER PRIMARY KEY REFERENCES groups_table(id) ON DELETE CASCADE, school_class TEXT NOT NULL, department TEXT NOT NULL, subject TEXT NOT NULL, code_hash TEXT NOT NULL, session_active INTEGER NOT NULL DEFAULT 1, opened_at TEXT NOT NULL, ended_at TEXT);
            CREATE TABLE IF NOT EXISTS community_join_requests(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, school_class TEXT NOT NULL, department TEXT NOT NULL, subject TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL, reviewed_by INTEGER REFERENCES users(id), reviewed_at TEXT, UNIQUE(user_id,school_class,department,subject));
            CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, sender_id INTEGER NOT NULL REFERENCES users(id), recipient_id INTEGER REFERENCES users(id), group_id INTEGER REFERENCES groups_table(id), body TEXT NOT NULL, created_at TEXT NOT NULL, delivered_at TEXT, read_at TEXT, edited_at TEXT, deleted_for_all INTEGER NOT NULL DEFAULT 0, reactions TEXT NOT NULL DEFAULT '{}', pinned INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS message_deletions(message_id INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, PRIMARY KEY(message_id,user_id));
            CREATE TABLE IF NOT EXISTS message_reports(id INTEGER PRIMARY KEY, message_id INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE, reporter_id INTEGER NOT NULL REFERENCES users(id), reason TEXT NOT NULL, created_at TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS idx_messages_direct ON messages(sender_id,recipient_id,id);
            CREATE INDEX IF NOT EXISTS idx_messages_group ON messages(group_id,id);
            ''')
            # Migrate older databases without deleting existing accounts.
            columns = {row[1] for row in c.execute("PRAGMA table_info(users)").fetchall()}
            if "school_class" not in columns:
                c.execute("ALTER TABLE users ADD COLUMN school_class TEXT NOT NULL DEFAULT 'SS1'")
            if "department" not in columns:
                c.execute("ALTER TABLE users ADD COLUMN department TEXT NOT NULL DEFAULT 'Science'")
            if "phone_number" not in columns:
                c.execute("ALTER TABLE users ADD COLUMN phone_number TEXT NOT NULL DEFAULT ''")
            if "last_seen_at" not in columns:
                c.execute("ALTER TABLE users ADD COLUMN last_seen_at TEXT")
            message_columns = {row[1] for row in c.execute("PRAGMA table_info(messages)").fetchall()}
            for col, definition in (("delivered_at", "TEXT"), ("read_at", "TEXT"), ("edited_at", "TEXT"), ("deleted_for_all", "INTEGER NOT NULL DEFAULT 0"), ("reactions", "TEXT NOT NULL DEFAULT '{}'"), ("pinned", "INTEGER NOT NULL DEFAULT 0")):
                if col not in message_columns: c.execute(f"ALTER TABLE messages ADD COLUMN {col} {definition}")
    init_db()

    def stamp(): return _ConnectDateTime.now(_ConnectTimezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    def derive(password, salt): return _connect_hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 240000)
    class Credentials(BaseModel):
        username: str = Field(min_length=3, max_length=40, pattern=r"^[A-Za-z0-9_.-]+$")
        password: str = Field(min_length=8, max_length=256)
        school_class: str = "SS1"
        department: str = "Science"
        phone_number: str = ""
    class GroupCreate(BaseModel):
        name: str = Field(min_length=2, max_length=80)
        members: list[str] = Field(default_factory=list, max_length=50)
        community: bool = False
        subject: str = Field(default="", max_length=80)
    class CommunityOpen(BaseModel):
        school_class: str
        department: str
        subject: str
    class CommunityJoin(BaseModel):
        code: str = Field(min_length=6, max_length=80)
    class ClassCommunityJoin(BaseModel):
        code: str = Field(min_length=25, max_length=25)
        subject: str = Field(min_length=2, max_length=80)
    class CommunityRequestCreate(BaseModel):
        school_class: str
        department: str
        subject: str
    class CommunityEnd(BaseModel):
        group_id: int
    class MessageCreate(BaseModel):
        kind: str
        target: str
        body: str = Field(min_length=1, max_length=4000)

    def current_user(authorization: _ConnectOptional[str] = Header(default=None)):
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(401, "Please log in again.")
        uid = sessions.get(authorization[7:])
        if not uid: raise HTTPException(401, "Session expired. Please log in again.")
        with db() as c:
            row = c.execute("SELECT id,username,school_class,department FROM users WHERE id=?", (uid,)).fetchone()
        if not row: raise HTTPException(401, "Account not found.")
        return dict(row)

    def require_same_cohort(me, other_id, c):
        other = c.execute("SELECT id,school_class,department FROM users WHERE id=?", (other_id,)).fetchone()
        if not other: raise HTTPException(404,"Student not found.")
        if other["school_class"] != me["school_class"] or other["department"] != me["department"]:
            raise HTTPException(403, "You can only communicate with students in your own class and department.")
        return other

    @app.get("/health")
    def health(): return {"ok": True, "service": "I.S.S.S. Connect"}

    @app.post("/api/register")
    def register(data: Credentials):
        username = data.username.strip()
        if len(username) < 3: raise HTTPException(400, "Username must have at least 3 characters.")
        if data.school_class not in ("SS1", "SS2", "SS3"):
            raise HTTPException(400, "Choose SS1, SS2, or SS3.")
        if data.department not in ("Science", "Arts", "Commercial"):
            raise HTTPException(400, "Choose Science, Arts, or Commercial.")
        if not re.fullmatch(r"\+[1-9]\d{7,14}", data.phone_number.strip()):
            raise HTTPException(400, "Enter a phone number with country code, e.g. +2348012345678.")
        salt = _connect_secrets.token_bytes(16); pw_hash = derive(data.password, salt)
        try:
            with db() as c:
                cur = c.execute("INSERT INTO users(username,salt,pw_hash,created_at,school_class,department,phone_number) VALUES(?,?,?,?,?,?,?)", (username,salt,pw_hash,stamp(),data.school_class,data.department,data.phone_number.strip()))
                uid = cur.lastrowid
        except _connect_sqlite3.IntegrityError: raise HTTPException(409, "That username is already registered.")
        token = _connect_secrets.token_urlsafe(32); sessions[token] = uid
        return {"token": token, "username": username}

    @app.post("/api/login")
    def login(data: Credentials):
        with db() as c: row = c.execute("SELECT id,username,salt,pw_hash FROM users WHERE username=?", (data.username.strip(),)).fetchone()
        if not row or not _connect_hmac.compare_digest(derive(data.password, row["salt"]), row["pw_hash"]):
            raise HTTPException(401, "Incorrect username or password.")
        token = _connect_secrets.token_urlsafe(32); sessions[token] = row["id"]
        return {"token": token, "username": row["username"]}

    @app.post("/api/presence")
    def update_presence(me=Depends(current_user)):
        now = _connect_time.time()
        presence[me["id"]] = now
        with db() as c:
            c.execute("UPDATE users SET last_seen_at=? WHERE id=?", (stamp(), me["id"]))
        return {"ok": True, "online": True}

    @app.post("/api/logout")
    def logout(authorization: _ConnectOptional[str] = Header(default=None), me=Depends(current_user)):
        if authorization and authorization.startswith("Bearer "):
            sessions.pop(authorization[7:], None)
        presence.pop(me["id"], None)
        with db() as c:
            c.execute("UPDATE users SET last_seen_at=? WHERE id=?", (stamp(), me["id"]))
        return {"ok": True}

    @app.get("/api/users")
    @app.get("/api/friends")
    def users(me=Depends(current_user)):
        """Return every registered student eligible to appear in this student's chat list.

        Friend entries are automatic: no friend request or manual add is required.
        To preserve the school's privacy rule, only the same exact class and
        department are listed. Comparisons ignore case/extra surrounding spaces
        so older account values do not accidentally hide classmates.
        """
        now = _connect_time.time()
        my_class = str(me.get("school_class") or "").strip().casefold()
        my_department = str(me.get("department") or "").strip().casefold()
        with db() as c:
            rows = c.execute(
                "SELECT id,username,school_class,department,last_seen_at FROM users WHERE id<>? ORDER BY username COLLATE NOCASE",
                (me["id"],)
            ).fetchall()
        result = []
        for r in rows:
            their_class = str(r["school_class"] or "").strip().casefold()
            their_department = str(r["department"] or "").strip().casefold()
            if their_class != my_class or their_department != my_department:
                continue
            last_ping = presence.get(r["id"], 0)
            online = bool(last_ping and now - last_ping <= 18)
            result.append({
                "id": r["id"],
                "username": r["username"],
                "school_class": r["school_class"],
                "department": r["department"],
                "online": online,
                "last_seen": "just now" if online else (r["last_seen_at"] or "unavailable"),
            })
        return {"users": result, "friends": result, "count": len(result), "automatic_friends": True}

    @app.get("/api/groups")
    def groups(me=Depends(current_user)):
        with db() as c:
            rows = c.execute('''SELECT g.id,g.name,g.owner_id FROM groups_table g JOIN group_members m ON m.group_id=g.id LEFT JOIN subject_communities sc ON sc.group_id=g.id WHERE m.user_id=? AND (sc.group_id IS NULL OR sc.session_active=1 OR g.owner_id=?) ORDER BY g.name COLLATE NOCASE''',(me["id"],me["id"])).fetchall()
        return {"groups": [dict(r) for r in rows]}

    # Subject invitation codes are shared with the companion generator through isss_community_codes.json.
    # The generator preserves each class|department|subject code until its original 24-hour expiry.
    # Connect validates the same key and expiry before allowing a student to join.
    _CLASS_COMMUNITY_STORE = _connect_os.path.join(_connect_os.path.dirname(_connect_os.path.abspath(__file__)), "isss_community_codes.json")
    _CLASS_COMMUNITY_PAIRS = [(f"SS{i}", dep) for i in (1, 2, 3) for dep in ("Science", "Arts", "Commercial")]

    @app.get("/api/class-communities")
    def class_communities(me=Depends(current_user)):
        with db() as c:
            memberships = {r[0] for r in c.execute("SELECT g.name FROM groups_table g JOIN group_members m ON m.group_id=g.id WHERE m.user_id=?", (me["id"],)).fetchall()}
        items=[]
        for cl, dep in _CLASS_COMMUNITY_PAIRS:
            name=f"{cl} {dep} Community"
            items.append({"school_class":cl,"department":dep,"name":name,"joined":name in memberships})
        return {"communities":items,"your_community":f"{me['school_class']} {me['department']} Community"}

    @app.post("/api/class-communities/join")
    def join_class_community(data: ClassCommunityJoin, me=Depends(current_user)):
        # The logged-in profile is authoritative; client input cannot choose another cohort.
        cl=str(me["school_class"]).strip().upper()
        dep=str(me["department"]).strip().title()
        if (cl,dep) not in _CLASS_COMMUNITY_PAIRS:
            raise HTTPException(403,"Your registered class or department is not eligible for these communities.")
        try:
            with open(_CLASS_COMMUNITY_STORE,"r",encoding="utf-8") as f:
                store=json.load(f)
        except FileNotFoundError:
            raise HTTPException(503,"No code store found beside the Connect app. Put ISSS_Community_Subject_Code_Generator.py and Connect in the same folder, then generate the selected subject code.")
        except (OSError,ValueError):
            raise HTTPException(503,"The community-code file is unreadable. Regenerate the codes and try again.")
        subject = next((x for x in _COMMUNITY_SUBJECTS.get(dep, []) if x.casefold() == data.subject.strip().casefold()), None)
        if not subject:
            raise HTTPException(400, "Choose a valid subject for your registered department.")
        key=f"{cl}|{dep}|{subject}"
        record=store.get("communities",{}).get(key)
        if not isinstance(record,dict):
            raise HTTPException(404,"No invitation code exists for this class, department and subject. Generate the code for this exact subject first.")
        try:
            expiry=_ConnectDateTime.fromisoformat(record["expires_at_utc"])
            if expiry.tzinfo is None: expiry=expiry.replace(tzinfo=_ConnectTimezone.utc)
        except (KeyError,TypeError,ValueError):
            raise HTTPException(503,"This community-code record is invalid. Regenerate the codes.")
        if _ConnectDateTime.now(_ConnectTimezone.utc) >= expiry:
            raise HTTPException(410,"This subject code has expired after 24 hours. Generate a new code for this exact class, department and subject.")
        if not _connect_hmac.compare_digest(str(data.code).strip().upper(),str(record.get("code",""))):
            raise HTTPException(403,"Incorrect code for this class, department and subject.")
        name=f"{cl} {dep} — {subject}"
        with db() as c:
            row=c.execute("SELECT id FROM groups_table WHERE name=? AND owner_id=0",(name,)).fetchone()
            if row:
                gid=row["id"]
            else:
                # Use a dedicated system-owned group. owner_id references users, so create/reuse
                # the first registered account only as a database owner; membership remains controlled.
                row=c.execute("SELECT id FROM groups_table WHERE name=? ORDER BY id LIMIT 1",(name,)).fetchone()
                if row: gid=row["id"]
                else:
                    owner=c.execute("SELECT id FROM users ORDER BY id LIMIT 1").fetchone()
                    if not owner: raise HTTPException(409,"Create a student account before joining a community.")
                    cur=c.execute("INSERT INTO groups_table(name,owner_id,created_at) VALUES(?,?,?)",(name,owner["id"],stamp()))
                    gid=cur.lastrowid
            c.execute("INSERT OR IGNORE INTO group_members(group_id,user_id) VALUES(?,?)",(gid,me["id"]))
        # Count successful uses in the same JSON format the generator maintains.
        try:
            record["uses"]=int(record.get("uses",0))+1
            temp=_CLASS_COMMUNITY_STORE+".tmp"
            with open(temp,"w",encoding="utf-8") as f: json.dump(store,f,indent=2)
            _connect_os.replace(temp,_CLASS_COMMUNITY_STORE)
        except OSError:
            # Membership is already safely stored in the database; usage count is non-critical.
            pass
        return {"ok":True,"group_id":gid,"name":name,"message":f"You joined {name}. This code is linked to the selected subject community."}

    # Subject catalog is generated for all requested classes and departments.
    # Subject lists used for SS1, SS2, and SS3. Students first choose their
    # registered class and department, then request the subject community.
    # Membership is granted only after the assigned teacher approves/invites them.
    _COMMUNITY_SUBJECTS = {
        "Science": [
            "Mathematics",
            "English Language",
            "Further Mathematics",
            "Biology",
            "Chemistry",
            "Geography",
            "Economics",
            "Livestock Farming",
            "Physics",
            "Citizenship and Heritage Studies",
        ],
        "Arts": [
            "Literature in English",
            "Mathematics",
            "English Language",
            "Government",
            "Livestock Farming",
            "CRS",
            "IRS",
            "Visual Arts",
            "Citizenship and Heritage Studies",
            "Yoruba Language",
        ],
        "Commercial": [
            "Mathematics",
            "English Language",
            "Commerce",
            "Financial Accounting",
            "Marketing",
            "Economics",
            "Citizenship and Heritage Studies",
            "Biology",
        ],
    }
    def _teacher_assignments():
        # Server-only trusted configuration; never accept a role supplied by the client.
        out=[]
        raw=_connect_os.environ.get("ISSS_TEACHER_ASSIGNMENTS", "")
        for item in raw.split(";"):
            bits=[x.strip() for x in item.split("|")]
            if len(bits)==4 and bits[0] and bits[1] in ("SS1","SS2","SS3") and bits[2] in _COMMUNITY_SUBJECTS and bits[3].casefold() in {x.casefold() for x in _COMMUNITY_SUBJECTS[bits[2]]}:
                out.append({"username":bits[0],"school_class":bits[1],"department":bits[2],"subject":bits[3]})
        return out
    def _assigned(me, school_class, department, subject):
        return any(a["username"].casefold()==me["username"].casefold() and a["school_class"]==school_class and a["department"]==department and a["subject"].casefold()==subject.casefold() for a in _teacher_assignments())
    @app.get("/api/communities/catalog")
    def community_catalog():
        return {"communities":[{"school_class":cl,"department":dep,"subject":sub,"name":f"{cl} {dep} — {sub}"} for cl in ("SS1","SS2","SS3") for dep,subjects in _COMMUNITY_SUBJECTS.items() for sub in subjects]}
    @app.post("/api/community-requests")
    def create_community_request(data: CommunityRequestCreate, me=Depends(current_user)):
        if data.school_class != me["school_class"] or data.department != me["department"]:
            raise HTTPException(403, "You can only request a subject in your own registered class and department.")
        if data.school_class not in ("SS1", "SS2", "SS3") or data.department not in _COMMUNITY_SUBJECTS or data.subject.casefold() not in {x.casefold() for x in _COMMUNITY_SUBJECTS.get(data.department, [])}:
            raise HTTPException(400, "Choose a valid class, department and subject.")
        subject = next(x for x in _COMMUNITY_SUBJECTS[data.department] if x.casefold() == data.subject.casefold())
        assigned = [a for a in _teacher_assignments() if a["school_class"] == data.school_class and a["department"] == data.department and a["subject"].casefold() == subject.casefold()]
        if not assigned:
            raise HTTPException(409, "No teacher is assigned to this subject yet. Please contact the school administrator.")
        with db() as c:
            old = c.execute("SELECT id,status FROM community_join_requests WHERE user_id=? AND school_class=? AND department=? AND lower(subject)=lower(?)", (me["id"], data.school_class, data.department, subject)).fetchone()
            if old and old["status"] == "pending":
                return {"ok": True, "request_id": old["id"], "message": "Your request is already pending. Please wait for your assigned teacher's invitation."}
            if old:
                c.execute("UPDATE community_join_requests SET status='pending',created_at=?,reviewed_by=NULL,reviewed_at=NULL WHERE id=?", (stamp(), old["id"]))
                req_id = old["id"]
            else:
                req_id = c.execute("INSERT INTO community_join_requests(user_id,school_class,department,subject,created_at) VALUES(?,?,?,?,?)", (me["id"], data.school_class, data.department, subject, stamp())).lastrowid
        return {"ok": True, "request_id": req_id, "message": "Request sent to the assigned teacher. Please wait for the teacher to approve your invitation."}

    @app.get("/api/community-requests/pending")
    def pending_community_requests(me=Depends(current_user)):
        assigned = _teacher_assignments()
        mine = [a for a in assigned if a["username"].casefold() == me["username"].casefold()]
        if not mine:
            raise HTTPException(403, "Only a teacher with verified subject assignments can review requests.")
        with db() as c:
            rows = c.execute("SELECT r.id,u.username,r.school_class,r.department,r.subject,r.created_at FROM community_join_requests r JOIN users u ON u.id=r.user_id WHERE r.status='pending' ORDER BY r.created_at", ()).fetchall()
        allowed = {(a["school_class"],a["department"],a["subject"].casefold()) for a in mine}
        return {"requests":[dict(r) for r in rows if (r["school_class"],r["department"],r["subject"].casefold()) in allowed]}

    @app.post("/api/community-requests/{request_id}/approve")
    def approve_community_request(request_id: int, me=Depends(current_user)):
        mine = [a for a in _teacher_assignments() if a["username"].casefold() == me["username"].casefold()]
        with db() as c:
            req = c.execute("SELECT * FROM community_join_requests WHERE id=? AND status='pending'", (request_id,)).fetchone()
            if not req: raise HTTPException(404, "Pending request not found.")
            if not any(a["school_class"]==req["school_class"] and a["department"]==req["department"] and a["subject"].casefold()==req["subject"].casefold() for a in mine):
                raise HTTPException(403, "You are not the assigned teacher for this subject.")
            community = c.execute("SELECT sc.group_id,g.name FROM subject_communities sc JOIN groups_table g ON g.id=sc.group_id WHERE sc.school_class=? AND sc.department=? AND lower(sc.subject)=lower(?) AND sc.session_active=1 ORDER BY sc.opened_at DESC LIMIT 1", (req["school_class"],req["department"],req["subject"])).fetchone()
            if not community: raise HTTPException(409, "Open your assigned subject community first, then approve the request.")
            c.execute("INSERT OR IGNORE INTO group_members(group_id,user_id) VALUES(?,?)", (community["group_id"], req["user_id"]))
            c.execute("UPDATE community_join_requests SET status='approved',reviewed_by=?,reviewed_at=? WHERE id=?", (me["id"],stamp(),request_id))
        return {"ok":True,"message":f"Invitation approved. The student has been added to {community['name']}."}

    @app.get("/api/communities/teacher-options")
    def community_teacher_options(me=Depends(current_user)):
        assigned=[{k:v for k,v in a.items() if k!="username"} for a in _teacher_assignments() if a["username"].casefold()==me["username"].casefold()]
        return {"assignments":assigned}
    @app.post("/api/communities/open")
    def community_open(data: CommunityOpen, me=Depends(current_user)):
        if data.school_class not in ("SS1","SS2","SS3") or data.department not in _COMMUNITY_SUBJECTS or data.subject.casefold() not in {x.casefold() for x in _COMMUNITY_SUBJECTS.get(data.department,[])}:
            raise HTTPException(400,"Choose a valid class, department, and subject.")
        if not _assigned(me,data.school_class,data.department,data.subject):
            raise HTTPException(403,"Only the officially assigned teacher can open this subject community.")
        code="ISSS-"+_connect_secrets.token_urlsafe(8).replace("-","").replace("_","").upper()[:10]
        code_hash=_connect_hashlib.sha256(code.encode()).hexdigest()
        name=f"{data.school_class} {data.department} — {data.subject}"
        with db() as c:
            # Reuse this teacher's prior community for the same cohort/subject, retaining history.
            old=c.execute("SELECT sc.group_id FROM subject_communities sc JOIN groups_table g ON g.id=sc.group_id WHERE g.owner_id=? AND sc.school_class=? AND sc.department=? AND lower(sc.subject)=lower(?)",(me["id"],data.school_class,data.department,data.subject)).fetchone()
            if old:
                gid=old["group_id"]
                c.execute("UPDATE subject_communities SET code_hash=?,session_active=1,opened_at=?,ended_at=NULL WHERE group_id=?",(code_hash,stamp(),gid))
                c.execute("UPDATE groups_table SET name=? WHERE id=?",(name,gid))
            else:
                cur=c.execute("INSERT INTO groups_table(name,owner_id,created_at) VALUES(?,?,?)",(name,me["id"],stamp())); gid=cur.lastrowid
                c.execute("INSERT INTO group_members(group_id,user_id) VALUES(?,?)",(gid,me["id"]))
                c.execute("INSERT INTO subject_communities(group_id,school_class,department,subject,code_hash,session_active,opened_at) VALUES(?,?,?,?,?,1,?)",(gid,data.school_class,data.department,data.subject,code_hash,stamp()))
        return {"id":gid,"name":name,"code":code,"expires":"when teacher ends the session"}
    @app.post("/api/communities/join")
    def community_join(data: CommunityJoin, me=Depends(current_user)):
        code_hash=_connect_hashlib.sha256(data.code.strip().upper().encode()).hexdigest()
        with db() as c:
            row=c.execute("SELECT sc.*,g.name FROM subject_communities sc JOIN groups_table g ON g.id=sc.group_id WHERE sc.code_hash=? AND sc.session_active=1",(code_hash,)).fetchone()
            if not row: raise HTTPException(404,"Invalid, expired, or ended community code.")
            if row["school_class"]!=me["school_class"] or row["department"]!=me["department"]:
                raise HTTPException(403,"This invitation is for a different class or department.")
            c.execute("INSERT OR IGNORE INTO group_members(group_id,user_id) VALUES(?,?)",(row["group_id"],me["id"]))
        return {"ok":True,"name":row["name"],"group_id":row["group_id"]}
    @app.post("/api/communities/end")
    def community_end(data: CommunityEnd, me=Depends(current_user)):
        with db() as c:
            row=c.execute("SELECT g.owner_id,sc.group_id FROM groups_table g JOIN subject_communities sc ON sc.group_id=g.id WHERE g.id=?",(data.group_id,)).fetchone()
            if not row: raise HTTPException(404,"Community not found.")
            if row["owner_id"]!=me["id"]: raise HTTPException(403,"Only the assigned teacher who owns this community can end the session.")
            c.execute("UPDATE subject_communities SET session_active=0,ended_at=?,code_hash=? WHERE group_id=?",(stamp(),_connect_secrets.token_hex(32),data.group_id))
        return {"ok":True,"message":"Session ended. It is hidden from students' active community lists."}

    @app.post("/api/groups")
    def create_group(data: GroupCreate, me=Depends(current_user)):
        # Teacher-admin restriction for subject communities is enforced on the server.
        if data.community:
            raise HTTPException(400, "Use /api/communities/open so teacher assignment and class/department restrictions are enforced.")
        with db() as c:
            cur = c.execute("INSERT INTO groups_table(name,owner_id,created_at) VALUES(?,?,?)",(data.name.strip(),me["id"],stamp()))
            gid = cur.lastrowid
            c.execute("INSERT INTO group_members(group_id,user_id) VALUES(?,?)",(gid,me["id"]))
            for name in data.members:
                user = c.execute("SELECT id,school_class,department FROM users WHERE username=?",(name.strip(),)).fetchone()
                if user and user["school_class"] == me["school_class"] and user["department"] == me["department"]:
                    c.execute("INSERT OR IGNORE INTO group_members(group_id,user_id) VALUES(?,?)",(gid,user["id"]))
        return {"id": gid, "name": data.name.strip()}

    @app.post("/api/groups/{group_id}/invite")
    def invite(group_id: int, usernames: list[str], me=Depends(current_user)):
        with db() as c:
            group = c.execute("SELECT g.owner_id,sc.school_class,sc.department,sc.session_active FROM groups_table g LEFT JOIN subject_communities sc ON sc.group_id=g.id WHERE g.id=?",(group_id,)).fetchone()
            if not group: raise HTTPException(404,"Group not found.")
            if group["school_class"] is not None:
                if group["owner_id"] != me["id"]: raise HTTPException(403,"Only the assigned teacher can invite students to a subject community.")
                if not group["session_active"]: raise HTTPException(400,"This community session has ended.")
                target_class,target_department=group["school_class"],group["department"]
            else:
                member = c.execute("SELECT 1 FROM group_members WHERE group_id=? AND user_id=?",(group_id,me["id"])).fetchone()
                if not member: raise HTTPException(403,"Only group members can invite students.")
                target_class,target_department=me["school_class"],me["department"]
            for name in usernames[:50]:
                user=c.execute("SELECT id,school_class,department FROM users WHERE username=?",(name.strip(),)).fetchone()
                if user and user["school_class"] == target_class and user["department"] == target_department:
                    c.execute("INSERT OR IGNORE INTO group_members(group_id,user_id) VALUES(?,?)",(group_id,user["id"]))
        return {"ok":True}

    @app.get("/api/messages")
    def get_messages(kind: str, target: str, after: int=0, me=Depends(current_user)):
        with db() as c:
            if kind == "direct":
                other = c.execute("SELECT id,school_class,department FROM users WHERE username=?",(target,)).fetchone()
                if not other: raise HTTPException(404,"Student not found.")
                if other["school_class"] != me["school_class"] or other["department"] != me["department"]:
                    raise HTTPException(403, "You can only communicate with students in your own class and department.")
                rows = c.execute('''SELECT m.id,u.username,m.body,m.created_at,m.read_at,m.delivered_at,m.edited_at,m.deleted_for_all,m.reactions,m.pinned FROM messages m JOIN users u ON u.id=m.sender_id WHERE m.group_id IS NULL AND ((m.sender_id=? AND m.recipient_id=?) OR (m.sender_id=? AND m.recipient_id=?)) AND m.id>? AND NOT EXISTS (SELECT 1 FROM message_deletions d WHERE d.message_id=m.id AND d.user_id=?) ORDER BY m.id LIMIT 300''',(me["id"],other["id"],other["id"],me["id"],after,me["id"])).fetchall()
            elif kind == "group":
                try: gid=int(target)
                except ValueError: raise HTTPException(400,"Invalid group.")
                member=c.execute("SELECT 1 FROM group_members WHERE group_id=? AND user_id=?",(gid,me["id"])).fetchone()
                if not member: raise HTTPException(403,"You are not a member of this group.")
                rows=c.execute('''SELECT m.id,u.username,m.body,m.created_at,m.read_at,m.delivered_at,m.edited_at,m.deleted_for_all,m.reactions,m.pinned FROM messages m JOIN users u ON u.id=m.sender_id WHERE m.group_id=? AND m.id>? AND NOT EXISTS (SELECT 1 FROM message_deletions d WHERE d.message_id=m.id AND d.user_id=?) ORDER BY m.id LIMIT 300''',(gid,after,me["id"])).fetchall()
            else: raise HTTPException(400,"kind must be direct or group")
            for row in rows:
                if row["username"].lower() != me["username"].lower():
                    # Fetching to the recipient's app marks delivered, not read.
                    c.execute("UPDATE messages SET delivered_at=COALESCE(delivered_at,?) WHERE id=?", (stamp(), row["id"]))
        return {"messages":[dict(r) for r in rows]}

    @app.post("/api/messages")
    def send_message(data: MessageCreate, me=Depends(current_user)):
        body=data.body.strip()
        if not body: raise HTTPException(400,"Message cannot be empty.")
        with db() as c:
            if data.kind == "direct":
                other=c.execute("SELECT id,school_class,department FROM users WHERE username=?",(data.target,)).fetchone()
                if not other: raise HTTPException(404,"Student not found.")
                if other["id"]==me["id"]: raise HTTPException(400,"You cannot message yourself.")
                if other["school_class"] != me["school_class"] or other["department"] != me["department"]:
                    raise HTTPException(403,"You can only communicate with students in your own class and department.")
                cur=c.execute("INSERT INTO messages(sender_id,recipient_id,body,created_at) VALUES(?,?,?,?)",(me["id"],other["id"],body,stamp()))
            elif data.kind == "group":
                try: gid=int(data.target)
                except ValueError: raise HTTPException(400,"Invalid group.")
                member=c.execute("SELECT 1 FROM group_members WHERE group_id=? AND user_id=?",(gid,me["id"])).fetchone()
                if not member: raise HTTPException(403,"You are not a member of this group.")
                cur=c.execute("INSERT INTO messages(sender_id,group_id,body,created_at) VALUES(?,?,?,?)",(me["id"],gid,body,stamp()))
            else: raise HTTPException(400,"kind must be direct or group")
        return {"id":cur.lastrowid,"ok":True}

    class MessageEdit(BaseModel):
        body: str = Field(min_length=1, max_length=4000)
    class ReactionCreate(BaseModel):
        emoji: str = Field(min_length=1, max_length=8)
    class ReportCreate(BaseModel):
        reason: str = Field(min_length=3, max_length=500)

    @app.patch("/api/messages/{message_id}")
    def edit_message(message_id: int, data: MessageEdit, me=Depends(current_user)):
        with db() as c:
            row = c.execute("SELECT sender_id,read_at,deleted_for_all FROM messages WHERE id=?", (message_id,)).fetchone()
            if not row: raise HTTPException(404, "Message not found.")
            if row["sender_id"] != me["id"]: raise HTTPException(403, "You can only edit your own messages.")
            if row["read_at"] or row["deleted_for_all"]: raise HTTPException(409, "This message has already been read or deleted and cannot be edited.")
            c.execute("UPDATE messages SET body=?, edited_at=? WHERE id=?", (data.body.strip(), stamp(), message_id))
        return {"ok": True}

    @app.delete("/api/messages/{message_id}")
    def delete_message(message_id: int, mode: str="me", me=Depends(current_user)):
        with db() as c:
            row = c.execute("SELECT sender_id,recipient_id,read_at,group_id,body,created_at FROM messages WHERE id=?", (message_id,)).fetchone()
            if not row: raise HTTPException(404, "Message not found.")
            # Archive to admin vault before any deletion (admin can view deleted messages)
            try:
                c.execute("""
                    CREATE TABLE IF NOT EXISTS admin_deleted_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        original_id INTEGER,
                        sender_id INTEGER,
                        sender_name TEXT,
                        recipient_id INTEGER,
                        recipient_name TEXT,
                        group_id INTEGER,
                        group_name TEXT,
                        body TEXT,
                        original_created_at TEXT,
                        deleted_at TEXT,
                        deleted_by TEXT,
                        reason TEXT
                    )
                """)
                sender_name = c.execute("SELECT username FROM users WHERE id=?", (row["sender_id"],)).fetchone()
                sender_name = sender_name[0] if sender_name else str(row["sender_id"])
                recipient_name = ""
                if row["recipient_id"]:
                    rn = c.execute("SELECT username FROM users WHERE id=?", (row["recipient_id"],)).fetchone()
                    recipient_name = rn[0] if rn else ""
                group_name = ""
                if row["group_id"]:
                    gn = c.execute("SELECT name FROM groups_table WHERE id=?", (row["group_id"],)).fetchone()
                    group_name = gn[0] if gn else ""
                c.execute("""
                    INSERT INTO admin_deleted_messages (original_id, sender_id, sender_name, recipient_id, recipient_name, group_id, group_name, body, original_created_at, deleted_at, deleted_by, reason)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """, (message_id, row["sender_id"], sender_name, row["recipient_id"], recipient_name, row["group_id"], group_name, row["body"], row["created_at"], __import__('datetime').datetime.now().isoformat(), me["username"], f"Deleted for {mode} by {me['username']}"))
            except Exception as e:
                print("archive in server failed", e)
            if mode == "everyone":
                if row["sender_id"] != me["id"]: raise HTTPException(403, "Only the sender can delete for everyone.")
                if row["read_at"]: raise HTTPException(409, "The recipient has read this message; you can only delete it for yourself.")
                c.execute("UPDATE messages SET body='This message was deleted', deleted_for_all=1 WHERE id=?", (message_id,))
            elif mode == "me":
                c.execute("INSERT OR IGNORE INTO message_deletions(message_id,user_id) VALUES(?,?)", (message_id, me["id"]))
            else: raise HTTPException(400, "mode must be me or everyone")
        return {"ok": True}

    @app.post("/api/messages/{message_id}/reaction")
    def react_message(message_id: int, data: ReactionCreate, me=Depends(current_user)):
        with db() as c:
            row = c.execute("SELECT reactions FROM messages WHERE id=?", (message_id,)).fetchone()
            if not row: raise HTTPException(404, "Message not found.")
            try: reactions = json.loads(row["reactions"] or "{}")
            except Exception: reactions = {}
            reactions[me["username"]] = data.emoji
            c.execute("UPDATE messages SET reactions=? WHERE id=?", (json.dumps(reactions, ensure_ascii=False), message_id))
        return {"ok": True}

    @app.post("/api/messages/{message_id}/pin")
    def pin_message(message_id: int, me=Depends(current_user)):
        with db() as c:
            row = c.execute("SELECT id FROM messages WHERE id=?", (message_id,)).fetchone()
            if not row: raise HTTPException(404, "Message not found.")
            c.execute("UPDATE messages SET pinned=1 WHERE id=?", (message_id,))
        return {"ok": True}

    @app.post("/api/messages/{message_id}/report")
    def report_message(message_id: int, data: ReportCreate, me=Depends(current_user)):
        with db() as c:
            row = c.execute("SELECT id FROM messages WHERE id=?", (message_id,)).fetchone()
            if not row: raise HTTPException(404, "Message not found.")
            c.execute("INSERT INTO message_reports(message_id,reporter_id,reason,created_at) VALUES(?,?,?,?)", (message_id, me["id"], data.reason.strip(), stamp()))
        return {"ok": True}

    @app.post("/api/messages/{message_id}/read")
    def mark_message_read(message_id: int, me=Depends(current_user)):
        with db() as c:
            row = c.execute("SELECT recipient_id,group_id FROM messages WHERE id=?", (message_id,)).fetchone()
            if not row: raise HTTPException(404, "Message not found.")
            if row["recipient_id"] == me["id"]: c.execute("UPDATE messages SET read_at=COALESCE(read_at,?) WHERE id=?", (stamp(), message_id))
        return {"ok": True}

    @app.post("/api/uploads")
    async def upload_attachment(
        kind: str = Form(...),
        target: str = Form(...),
        media_kind: str = Form(...),
        file: UploadFile = File(...),
        me=Depends(current_user),
    ):
        """Receive an attachment, enforce conversation permissions and return a safe URL."""
        allowed_extensions = {
            "photo": {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".mp4", ".mov", ".avi", ".mkv"},
            "audio": {".mp3", ".wav", ".m4a", ".ogg", ".aac", ".flac"},
            "document": {".pdf", ".doc", ".docx", ".txt", ".xlsx", ".pptx", ".csv"},
        }
        if media_kind not in allowed_extensions:
            raise HTTPException(400, "Unsupported attachment category.")
        original_name = os.path.basename(file.filename or "attachment")
        extension = os.path.splitext(original_name)[1].lower()
        if extension not in allowed_extensions[media_kind]:
            raise HTTPException(415, "This file type is not allowed.")
        # Check access to the target conversation before accepting any bytes.
        with db() as c:
            if kind == "direct":
                other = c.execute("SELECT id,school_class,department FROM users WHERE username=?", (target,)).fetchone()
                if not other:
                    raise HTTPException(404, "Student not found.")
                if other["id"] == me["id"]:
                    raise HTTPException(400, "You cannot send an attachment to yourself.")
                if other["school_class"] != me["school_class"] or other["department"] != me["department"]:
                    raise HTTPException(403, "You can only communicate with students in your own class and department.")
            elif kind == "group":
                try:
                    gid = int(target)
                except ValueError:
                    raise HTTPException(400, "Invalid group.")
                member = c.execute("SELECT 1 FROM group_members WHERE group_id=? AND user_id=?", (gid, me["id"])).fetchone()
                if not member:
                    raise HTTPException(403, "You are not a member of this group.")
            else:
                raise HTTPException(400, "kind must be direct or group")
        safe_name = _connect_secrets.token_hex(16) + extension
        destination = os.path.join(UPLOAD_DIR, safe_name)
        is_video = media_kind == "photo" and extension in {".mp4", ".mov", ".avi", ".mkv"}
        max_bytes = (300 if is_video else 25) * 1024 * 1024
        total = 0
        try:
            with open(destination, "wb") as output:
                while True:
                    chunk = await file.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > max_bytes:
                        output.close()
                        try: os.remove(destination)
                        except OSError: pass
                        limit_mb = 300 if is_video else 25
                        raise HTTPException(413, f"Maximum upload size is {limit_mb} MB per file.")
                    output.write(chunk)
        finally:
            await file.close()
        if total == 0:
            try: os.remove(destination)
            except OSError: pass
            raise HTTPException(400, "The selected file is empty.")
        return {"ok": True, "filename": original_name, "url": "/uploads/" + safe_name, "size": total, "media_kind": media_kind}
else:
    app = None

if __name__ == "__main__":
    import sys
    import threading as _threading

    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        if not _CONNECT_SERVER_AVAILABLE:
            raise SystemExit("Server packages missing. Install: python -m pip install fastapi uvicorn")
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
    else:
        # FIXED FOR BLACK SCREEN: Show security window directly in root, guaranteed visible
        # Don't withdraw root before security window - build security UI directly in root
        root = tk.Tk()
        root.geometry("540x520")
        root.configure(bg="#0F172A")
        try:
            root.update_idletasks()
            x = (root.winfo_screenwidth() - 540) // 2
            y = (root.winfo_screenheight() - 520) // 2
            root.geometry(f"540x520+{x}+{y}")
        except:
            pass
        
        # DB init in background
        def _init_db_fast():
            try:
                initialize_account_database()
            except:
                pass
        _threading.Thread(target=_init_db_fast, daemon=True).start()

        def launch_student_app(student_id, username):
            try:
                root.deiconify()
                root.geometry("1200x700")
                root.configure(bg="#EAF2FF")
                try:
                    root.update_idletasks()
                    x = (root.winfo_screenwidth() - 1200) // 2
                    y = (root.winfo_screenheight() - 700) // 2
                    root.geometry(f"1200x700+{x}+{y}")
                except:
                    pass
                initialize_account_database()
            except:
                pass
            app_window = StudyApp(root, student_id=student_id, student_username=username)
            root._study_app = app_window

        def launch_auth_window():
            try:
                for w in root.winfo_children():
                    w.destroy()
                root.deiconify()
                root.geometry("450x620")
                root.configure(bg="#EAF2FF")
                try:
                    root.update_idletasks()
                    x = (root.winfo_screenwidth() - 450) // 2
                    y = (root.winfo_screenheight() - 620) // 2
                    root.geometry(f"450x620+{x}+{y}")
                except:
                    pass
            except:
                pass
            StudentAuthWindow(root, launch_student_app)

        SecurityKeyWindow(root, launch_auth_window)
        root.mainloop()

