# utils/splash_screen.py
# Discord BLUE - Python Tkinter Splash Screen
# Author: bluemanhst

import tkinter as tk
import os
import sys

from utils.paths import resource_path

try:
    from language import translate
    _HAS_TRANSLATE = True
except ImportError:
    _HAS_TRANSLATE = False

DEFAULT_SLOGAN = 'Automated Discord Bot'


class DiscordBLUE_SplashScreen:
    def __init__(self, root, on_finish_callback=None):
        self.root = root
        self.on_finish = on_finish_callback
        self.progress = 0
        self._logo_img = None

        self.width = 520
        self.height = 268

        self.splash = tk.Toplevel(self.root)
        self.splash.overrideredirect(True)
        self.splash.configure(bg='#000000')
        self.splash.attributes('-topmost', True)

        screen_w = self.splash.winfo_screenwidth()
        screen_h = self.splash.winfo_screenheight()
        pos_x = (screen_w - self.width) // 2
        pos_y = (screen_h - self.height) // 2
        self.splash.geometry(f'{self.width}x{self.height}+{pos_x}+{pos_y}')

        self.container = tk.Frame(
            self.splash,
            bg='#000000',
            highlightthickness=1,
            highlightbackground='#242E3D',
            highlightcolor='#3B82F6',
        )
        self.container.pack(fill='both', expand=True)

        logo_path = self._find_logo()
        if logo_path:
            try:
                from PIL import Image, ImageTk

                img = Image.open(logo_path)
                # Giữ đúng tỉ lệ ảnh logo_blue_labs 1302x800 -> 250x154 như Template C#
                logo_w = 250
                base_w, base_h = img.size
                logo_h = int(logo_w * base_h / base_w) if base_w else 154
                resample = getattr(getattr(Image, 'Resampling', Image), 'LANCZOS', Image.BICUBIC)
                img = img.resize((logo_w, logo_h), resample)
                self._logo_img = ImageTk.PhotoImage(img)
                tk.Label(self.container, image=self._logo_img, bg='#000000').pack(pady=(14, 10))
            except Exception:
                self._draw_fallback_text()
        else:
            self._draw_fallback_text()

        self.bar_w = 440
        self.bar_h = 8
        self.canvas = tk.Canvas(
            self.container,
            width=self.bar_w,
            height=self.bar_h,
            bg='#000000',
            highlightthickness=0,
        )
        self.canvas.pack(pady=(0, 10))

        self.info_frame = tk.Frame(self.container, bg='#000000', width=self.bar_w)
        self.info_frame.pack(fill='x', padx=40)

        self.lbl_status = tk.Label(
            self.info_frame,
            text='Loading framework...',
            font=('Segoe UI', 10, 'bold'),
            fg='#00f0ff',
            bg='#000000',
            anchor='w',
        )
        self.lbl_status.pack(side='left')

        self.lbl_pct = tk.Label(
            self.info_frame,
            text='0%',
            font=('Segoe UI', 10, 'bold'),
            fg='#00f0ff',
            bg='#000000',
            anchor='e',
        )
        self.lbl_pct.pack(side='right')

        self._draw_progress()
        self.splash.after(25, self._step)

    def _find_logo(self):
        try:
            rp = resource_path('assets', 'logo_blue_labs.png')
            if rp and os.path.isfile(rp):
                return rp
        except Exception:
            pass
        base = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            os.path.normpath(os.path.join(base, '..', 'assets', 'logo_blue_labs.png')),
            os.path.normpath(os.path.join(base, '..', '..', 'assets', 'logo_blue_labs.png')),
        ]
        try:
            if hasattr(sys, '_MEIPASS'):
                meipass = sys._MEIPASS
                candidates.append(os.path.join(meipass, 'assets', 'logo_blue_labs.png'))
                candidates.append(os.path.join(meipass, '..', 'assets', 'logo_blue_labs.png'))
            else:
                import ctypes
                buf = ctypes.create_unicode_buffer(260)
                ctypes.windll.shell32.SHGetFolderPathW(0, 0x0000, 0, 0, buf)
                desk = buf.value
                if desk:
                    candidates.append(os.path.join(desk, 'Discord BLUE', 'assets', 'logo_blue_labs.png'))
                    candidates.append(os.path.join(desk, 'Template SplashScreen', 'Logo', 'logo_blue_labs.png'))
        except Exception:
            pass
        for p in candidates:
            if os.path.isfile(p):
                return p
        return None

    def _draw_fallback_text(self):
        tk.Label(
            self.container,
            text='Discord BLUE',
            font=('Segoe UI', 24, 'bold'),
            fg='#3B82F6',
            bg='#000000',
        ).pack(pady=(36, 4))
        tk.Label(
            self.container,
            text=DEFAULT_SLOGAN,
            font=('Segoe UI', 11, 'italic'),
            fg='#8BA0BE',
            bg='#000000',
        ).pack(pady=(0, 20))

    def _get_status_text(self, p):
        if not _HAS_TRANSLATE:
            return self._default_status(p)
        try:
            if p < 25:
                key = 'splash_screen.status.loading'
            elif p < 50:
                key = 'splash_screen.status.connecting'
            elif p < 75:
                key = 'splash_screen.status.checking'
            elif p < 95:
                key = 'splash_screen.status.initializing'
            else:
                key = 'splash_screen.status.ready'

            text = translate(key)
            if text and text != key:
                return text
        except Exception:
            pass
        return self._default_status(p)

    def _default_status(self, p):
        if p < 25:
            return 'Loading...'
        if p < 50:
            return 'Connecting to Discord...'
        if p < 75:
            return 'Checking configuration...'
        if p < 95:
            return 'Initializing bot...'
        return 'Ready to launch!'

    def _draw_progress(self):
        self.canvas.delete('all')
        self.canvas.create_rectangle(
            0, 0, self.bar_w, self.bar_h,
            fill='#12161E',
            outline='#242E3E',
        )
        if self.progress > 0:
            fill_w = max(4, int(self.bar_w * (self.progress / 100.0)))
            self.canvas.create_rectangle(
                0, 0, fill_w, self.bar_h,
                fill='#3B82F6',
                outline=''
            )

    def _step(self):
        if self.progress < 100:
            self.progress += 2
            if self.progress > 100:
                self.progress = 100

            self.lbl_status.config(text=self._get_status_text(self.progress))
            self.lbl_pct.config(text=f'{self.progress}%')
            self._draw_progress()
            self.splash.after(25, self._step)
        else:
            self.splash.destroy()
            if self.on_finish:
                self.on_finish()


def show_splash_screen(root, on_finish_callback=None):
    return DiscordBLUE_SplashScreen(root, on_finish_callback)
