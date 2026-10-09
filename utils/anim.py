# utils/anim.py
# Vong lap animation nhe (lerp + easing) - mo phong AnimEngine cua Roblox BLUE
# Chi chay khi con task; tu dung khi hoan thanh de khong ton CPU.

import time


def lerp(a, b, t):
    """Noi suy tuy tinh giua 2 gia tri voi t trong [0, 1]."""
    if t <= 0:
        return a
    if t >= 1:
        return b
    return a + (b - a) * t


def ease_out_cubic(x):
    """Ease-out cubic - chay nhanh dau, cham cuoi (giong Roblox BLUE)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    inv = 1.0 - x
    return 1.0 - inv * inv * inv


class AnimLoop:
    """Chay on_step(p) moi ~16ms tu p=0 -> p=1 trong duration_ms.

    owner: widget Tk (dung .after); on_step(nhan p da easing); on_done goi 1 lan khi xong.
    Goi .start() nhieu lan se huy lan truoc - an toan khi bam lien tuc.
    """

    def __init__(self, owner, duration_ms=180, on_step=None, on_done=None):
        self.owner = owner
        self.duration_ms = max(1, int(duration_ms))
        self.on_step = on_step
        self.on_done = on_done
        self._after_id = None
        self._t0 = 0.0

    def _alive(self):
        try:
            if hasattr(self.owner, "winfo_exists"):
                return bool(self.owner.winfo_exists())
        except Exception:
            return False
        return True

    def cancel(self):
        if self._after_id is not None:
            try:
                self.owner.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def start(self):
        self.cancel()
        self._t0 = time.monotonic()
        self._tick()

    def _tick(self):
        if not self._alive():
            self._after_id = None
            return
        elapsed_ms = (time.monotonic() - self._t0) * 1000.0
        p = elapsed_ms / self.duration_ms
        if p >= 1.0:
            self._after_id = None
            if self.on_step:
                try:
                    self.on_step(1.0)
                except Exception:
                    pass
            if self.on_done:
                try:
                    self.on_done()
                except Exception:
                    pass
            return
        if self.on_step:
            try:
                self.on_step(ease_out_cubic(p))
            except Exception:
                pass
        try:
            self._after_id = self.owner.after(16, self._tick)
        except Exception:
            self._after_id = None
