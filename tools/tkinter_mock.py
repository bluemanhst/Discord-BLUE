# tools/tkinter_mock.py
# Gia lap tkinter + cac module UI de nap main.pyw that trong test (khong can man hinh).

import sys
import types


class _Var:
    def __init__(self, value=None):
        self._v = value

    def get(self):
        return self._v

    def set(self, v):
        self._v = v

    def trace_add(self, mode, callback=None):
        # Test khong can callback; giu ky nop de code gan trace khong crash
        return None

    def trace_remove(self, *a, **k):
        return None

    def trace_info(self, *a, **k):
        return []

    def trace(self, mode, callback=None):
        # API cu tkinter (van con dung o mot cho)
        return None


class _Widget:
    def __init__(self, *a, **k):
        # Widget that: tham so dau tien la parent (giong tkinter that) -> can cho .master
        self.master = a[0] if a else None
        self._text = ""
        self._cfg = dict(k)
        self._children = []

    def pack(self, *a, **k):
        return None

    def pack_forget(self, *a, **k):
        return None

    def grid_forget(self, *a, **k):
        return None

    def grid(self, *a, **k):
        return None

    def place(self, *a, **k):
        return None

    def grid_columnconfigure(self, *a, **k):
        return None

    def grid_rowconfigure(self, *a, **k):
        return None

    def columnconfigure(self, *a, **k):
        return None

    def rowconfigure(self, *a, **k):
        return None

    def bind(self, *a, **k):
        return None

    def bind_all(self, *a, **k):
        return None

    def config(self, *a, **k):
        self._cfg.update(k)
        return None

    configure = config

    def cget(self, k):
        return self._cfg.get(k, "")

    def __getitem__(self, key):
        # Widget that ho tro truy cap kieu dict: widget["bg"]
        return self._cfg.get(key, "")

    def __setitem__(self, key, value):
        self._cfg[key] = value

    def get(self, *a, **k):
        return self._text

    def insert(self, *a, **k):
        return None

    def delete(self, *a, **k):
        return None

    def see(self, *a, **k):
        return None

    def tag_config(self, *a, **k):
        return None

    def tag_add(self, *a, **k):
        return None

    def image_create(self, *a, **k):
        return 0

    def create_rectangle(self, *a, **k):
        return 1

    def create_polygon(self, *a, **k):
        return 1

    def create_text(self, *a, **k):
        return 1

    def create_oval(self, *a, **k):
        return 1

    def winfo_children(self):
        return []

    def winfo_ismapped(self):
        return False

    def after(self, *a, **k):
        return 0

    def set(self, *a, **k):
        return None

    def get_children(self, *a, **k):
        return []

    def add(self, *a, **k):
        return None

    def heading(self, *a, **k):
        return None

    def column(self, *a, **k):
        return None

    def destroy(self):
        self._destroyed = True
        return None

    def withdraw(self):
        return None

    def deiconify(self):
        return None

    def lift(self):
        return None

    def focus_force(self):
        return None

    def title(self, *a):
        return None

    def iconbitmap(self, *a, **k):
        return None

    def focus_set(self, *a, **k):
        return None

    def geometry(self, *a):
        return None

    def minsize(self, *a):
        return None

    def protocol(self, *a):
        return None

    def mainloop(self):
        return None

    def itemconfig(self, *a, **k):
        return None

    def create_window(self, *a, **k):
        return 0

    def bbox(self, *a):
        return (0, 0, 10, 10)

    def yview(self, *a):
        return None

    def yview_scroll(self, *a):
        return None

    # ===== Cac method ma splash_screen.py / UI that can dung =====
    _pending_after = []

    def after(self, ms=None, func=None, *a, **k):
        # Mo phong: hang doi callback, update() se chay (giong vong lap event tkinter)
        if callable(func):
            _Widget._pending_after.append(func)
        return 0

    def update(self):
        # Chay toan bo callback dang cho (splash.after(25, self._step)...).
        # Gioi han so lan de callback tu requeue (pump_log_queue...) khong treo test.
        n = 0
        while _Widget._pending_after and n < 500:
            n += 1
            cb = _Widget._pending_after.pop(0)
            try:
                cb()
            except Exception:
                pass
        return None

    def update_idletasks(self):
        return None

    def overrideredirect(self, *a, **k):
        return None

    def attributes(self, *a, **k):
        return None

    wm_attributes = attributes

    def winfo_screenwidth(self):
        return 1920

    def winfo_screenheight(self):
        return 1080

    def winfo_exists(self):
        return not getattr(self, "_destroyed", False)

    def create_rectangle(self, *a, **k):
        return 1

    def coords(self, *a, **k):
        return None

    def resizable(self, *a, **k):
        return None

    def pack_propagate(self, flag=True):
        return None

    def grid_propagate(self, flag=True):
        return None

    def selection_set(self, *a, **k):
        return None

    def selection_clear(self, *a, **k):
        return None

    def selection_toggle(self, *a, **k):
        return None

    def selection(self):
        return ()

    def curselection(self):
        return ()

    def index(self, *a, **k):
        return 0

    def item(self, *a, **k):
        # Treeview.item(iid, "values") -> tuple rong; setter -> None
        if len(a) > 1 or (not a and "values" in k):
            return None
        return ()

    def exists(self, *a, **k):
        return False

    def parent(self, *a, **k):
        return ""

    def detach(self, *a, **k):
        return None

    def size(self):
        return 0

    def add_command(self, *a, **k):
        return None

    def add_separator(self, *a, **k):
        return None

    def entryconfig(self, *a, **k):
        return None

    def entryconfigure(self, *a, **k):
        return None

    def tk_popup(self, *a, **k):
        return None

    def winfo_rootx(self):
        return 0

    def winfo_rooty(self):
        return 0

    def winfo_height(self):
        return 0


class _Tk(_Widget):
    pass


class _Style:
    """Gia lap ttk.Style - du de configure_ttk_styles() chay trong test."""

    def __init__(self, *a, **k):
        # ttk.Style(master) - nhan ca tham so root
        self.master = a[0] if a else None

    def theme_names(self):
        return ["clam"]

    def theme_use(self, *a, **k):
        return None

    def configure(self, *a, **k):
        return None

    def map(self, *a, **k):
        return None


def _install():
    tk = types.ModuleType("tkinter")
    for name in ["Frame", "Label", "Button", "Entry", "Text", "Canvas",
                 "Scrollbar", "Checkbutton", "Toplevel", "Tk", "PhotoImage",
                 "Listbox", "Menu", "LabelFrame", "Spinbox", "Radiobutton"]:
        setattr(tk, name, _Widget if name != "Tk" else _Tk)
    tk.BooleanVar = _Var
    tk.StringVar = _Var
    tk.END = "end"
    tk.ttk = types.SimpleNamespace(
        Combobox=_Widget, Notebook=_Widget, Treeview=_Widget,
        Frame=_Widget, Label=_Widget, Scrollbar=_Widget, Style=_Style
    )
    sys.modules["tkinter"] = tk
    sys.modules["tkinter.ttk"] = tk.ttk
    st = types.ModuleType("tkinter.scrolledtext")
    st.ScrolledText = _Widget
    sys.modules["tkinter.scrolledtext"] = st
    mb = types.ModuleType("tkinter.messagebox")
    mb.showinfo = lambda *a, **k: None
    mb.showwarning = lambda *a, **k: None
    mb.showerror = lambda *a, **k: None
    mb.askyesno = lambda *a, **k: False
    sys.modules["tkinter.messagebox"] = mb
    tk.messagebox = mb
    tk.scrolledtext = st
    fd = types.ModuleType("tkinter.filedialog")
    fd.asksaveasfilename = lambda *a, **k: ""
    fd.askopenfilename = lambda *a, **k: ""
    sys.modules["tkinter.filedialog"] = fd
    tk.filedialog = fd


_install()

