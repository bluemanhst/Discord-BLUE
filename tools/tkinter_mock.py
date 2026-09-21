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


class _Widget:
    def __init__(self, *a, **k):
        self._text = ""
        self._cfg = dict(k)

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


class _Tk(_Widget):
    pass


def _install():
    tk = types.ModuleType("tkinter")
    for name in ["Frame", "Label", "Button", "Entry", "Text", "Canvas",
                 "Scrollbar", "Checkbutton", "Toplevel", "Tk", "PhotoImage"]:
        setattr(tk, name, _Widget if name != "Tk" else _Tk)
    tk.BooleanVar = _Var
    tk.StringVar = _Var
    tk.END = "end"
    tk.ttk = types.SimpleNamespace(Combobox=_Widget, Notebook=_Widget, Treeview=_Widget)
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

