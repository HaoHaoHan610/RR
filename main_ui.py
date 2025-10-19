# rr_gui.py
# Minimal Round Robin visualizer (pure Tkinter)
# Python 3.10+ recommended

import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
from dataclasses import dataclass, field

@dataclass
class Proc:
    pid: str
    arrival: int
    burst: int
    remaining: int = field(init=False)
    first_start: int = field(default=None)
    completion: int = field(default=None)

    def __post_init__(self):
        self.remaining = self.burst

@dataclass
class Segment:
    pid: str | None     # None -> context switch / idle
    start: int
    end: int
    kind: str           # 'run' | 'cs' | 'idle'

def compute_rr(processes, quantum: int, cs: int):
    """
    Compute RR schedule.
    Returns: segments (list[Segment]), procs_stats (dict pid -> Proc), totals (dict)
    """
    procs = {p.pid: p for p in processes}
    arrivals = sorted(processes, key=lambda p: p.arrival)

    time = 0
    i = 0  # index over arrivals
    ready = deque()
    segments: list[Segment] = []
    total_run_time = 0

    def flush_arrivals(upto_time):
        nonlocal i, ready
        while i < len(arrivals) and arrivals[i].arrival <= upto_time:
            ready.append(arrivals[i])
            i += 1

    # Prime arrivals
    flush_arrivals(time)

    while True:
        # All done?
        if all(p.remaining == 0 for p in procs.values()):
            break

        # If no ready, jump to next arrival (idle gap)
        if not ready:
            if i < len(arrivals):
                next_t = arrivals[i].arrival
                if next_t > time:
                    segments.append(Segment(None, time, next_t, 'idle'))
                    time = next_t
                flush_arrivals(time)
            else:
                # Shouldn't happen (since loop would have broken), but safe-guard
                break

        if not ready:
            continue

        p = ready.popleft()

        # Record first response
        if p.first_start is None:
            p.first_start = time

        # Run slice
        slice_len = min(quantum, p.remaining)
        seg_start = time
        seg_end = time + slice_len
        segments.append(Segment(p.pid, seg_start, seg_end, 'run'))
        total_run_time += slice_len
        time = seg_end
        p.remaining -= slice_len

        # New arrivals during this run
        flush_arrivals(time)

        # If not finished, requeue
        if p.remaining > 0:
            ready.append(p)
        else:
            p.completion = time

        # Context switch if there's more work ahead
        more_ahead = any(q.remaining > 0 for q in procs.values())
        if cs > 0 and more_ahead:
            segments.append(Segment(None, time, time + cs, 'cs'))
            time += cs
            flush_arrivals(time)

    makespan = segments[-1].end if segments else 0
    # Stats
    stats = {}
    for pid, p in procs.items():
        ct = p.completion
        tat = ct - p.arrival
        wt  = tat - p.burst
        rt  = (p.first_start - p.arrival) if p.first_start is not None else 0
        stats[pid] = dict(CT=ct, TAT=tat, WT=wt, RT=rt)

    totals = dict(
        avg_wt = sum(s["WT"] for s in stats.values())/len(stats) if stats else 0.0,
        avg_tat = sum(s["TAT"] for s in stats.values())/len(stats) if stats else 0.0,
        throughput = (len(processes)/makespan) if makespan>0 else 0.0,
        cpu_util = (total_run_time/makespan*100.0) if makespan>0 else 0.0,
        makespan = makespan
    )
    return segments, stats, totals

# -------------------- UI --------------------

class RRApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Round Robin Scheduler (Tkinter)")
        self.geometry("1100x640")
        self.minsize(980, 560)

        # State
        self.processes: list[Proc] = []
        self.segments: list[Segment] = []
        self.stats: dict = {}
        self.totals: dict = {}
        self.anim_idx = 0
        self.animating = False
        self.scale_px = 24  # px per time unit (auto-adjust later)
        self.row_height = 34
        self.colors = {}
        self.palette = [
            "#4CC9F0", "#F72585", "#7209B7", "#3A0CA3", "#4361EE",
            "#4895EF", "#F15BB5", "#43AA8B", "#F9C74F", "#90BE6D",
        ]
        self.bg_dark = "#111418"
        self.fg = "#E6E6E6"
        self.cs_color = "#666A73"
        self.idle_color = "#2B2F36"

        self.configure(bg=self.bg_dark)
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except:
            pass
        style.configure("TLabel", foreground=self.fg, background=self.bg_dark)
        style.configure("TFrame", background=self.bg_dark)
        style.configure("TLabelframe", background=self.bg_dark, foreground=self.fg)
        style.configure("TButton", padding=6)
        style.configure("Treeview",
                        background="#1A1F25", foreground=self.fg, fieldbackground="#1A1F25",
                        rowheight=26)
        style.configure("Vertical.TScrollbar", background="#222")

        self.build_left_panel()
        self.build_center_canvas()
        self.build_right_panel()

        # Preset demo
        self.add_demo()

    # ---- Layout builders ----
    def build_left_panel(self):
        left = ttk.Frame(self)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        lf = ttk.Labelframe(left, text="Nhập tiến trình")
        lf.pack(fill=tk.X, pady=(0,10))

        frm = ttk.Frame(lf)
        frm.pack(fill=tk.X, padx=6, pady=6)

        ttk.Label(frm, text="PID").grid(row=0, column=0, sticky="w")
        ttk.Label(frm, text="Arrival").grid(row=0, column=1, sticky="w", padx=(8,0))
        ttk.Label(frm, text="Burst").grid(row=0, column=2, sticky="w", padx=(8,0))

        self.ent_pid = ttk.Entry(frm, width=6)
        self.ent_arr = ttk.Entry(frm, width=6)
        self.ent_burst = ttk.Entry(frm, width=6)
        self.ent_pid.grid(row=1, column=0, sticky="w")
        self.ent_arr.grid(row=1, column=1, sticky="w", padx=(8,0))
        self.ent_burst.grid(row=1, column=2, sticky="w", padx=(8,0))

        btns = ttk.Frame(lf)
        btns.pack(fill=tk.X, padx=6, pady=(4,6))
        ttk.Button(btns, text="Add", command=self.add_proc).pack(side=tk.LEFT)
        ttk.Button(btns, text="Remove", command=self.remove_selected).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Clear", command=self.clear_list).pack(side=tk.LEFT)

        self.lst = tk.Listbox(lf, height=8, bg="#1A1F25", fg=self.fg, selectmode=tk.SINGLE)
        self.lst.pack(fill=tk.BOTH, expand=True, padx=6, pady=(4,6))

        # Controls
        cf = ttk.Labelframe(left, text="Thiết lập")
        cf.pack(fill=tk.X, pady=(0,10))

        r1 = ttk.Frame(cf); r1.pack(fill=tk.X, padx=6, pady=4)
        ttk.Label(r1, text="Quantum").pack(side=tk.LEFT)
        self.sp_q = tk.Spinbox(r1, from_=1, to=100, width=6)
        self.sp_q.delete(0, tk.END); self.sp_q.insert(0, "3")
        self.sp_q.pack(side=tk.LEFT, padx=(6,14))

        ttk.Label(r1, text="Context switch").pack(side=tk.LEFT)
        self.sp_cs = tk.Spinbox(r1, from_=0, to=20, width=6)
        self.sp_cs.delete(0, tk.END); self.sp_cs.insert(0, "0")
        self.sp_cs.pack(side=tk.LEFT, padx=(6,0))

        r2 = ttk.Frame(cf); r2.pack(fill=tk.X, padx=6, pady=4)
        ttk.Label(r2, text="Tốc độ (ms/segment)").pack(side=tk.LEFT)
        self.sp_speed = tk.Spinbox(r2, from_=1, to=2000, width=6)
        self.sp_speed.delete(0, tk.END); self.sp_speed.insert(0, "250")
        self.sp_speed.pack(side=tk.LEFT, padx=(6,0))

        # Actions
        af = ttk.Frame(left); af.pack(fill=tk.X, pady=(6,0))
        ttk.Button(af, text="Run", command=self.run_schedule).pack(side=tk.LEFT)
        ttk.Button(af, text="Step", command=self.step_once).pack(side=tk.LEFT, padx=6)
        self.btn_pause = ttk.Button(af, text="Pause", command=self.toggle_pause, state=tk.DISABLED)
        self.btn_pause.pack(side=tk.LEFT, padx=6)
        ttk.Button(af, text="Reset", command=self.reset_all).pack(side=tk.LEFT, padx=6)

    def build_center_canvas(self):
        mid = ttk.Frame(self)
        mid.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)

        title = ttk.Label(mid, text="Gantt Chart", font=("Segoe UI", 11, "bold"))
        title.pack(anchor="w", padx=4, pady=(0,6))

        cv_frame = ttk.Frame(mid)
        cv_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(cv_frame, bg="#0D1117", height=280, highlightthickness=0)
        self.hbar = ttk.Scrollbar(cv_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.hbar.set)

        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.hbar.pack(fill=tk.X)

        # Info row
        info = ttk.Frame(mid); info.pack(fill=tk.X, pady=(8,0))
        self.lbl_now = ttk.Label(info, text="t = 0")
        self.lbl_now.pack(side=tk.LEFT, padx=4)

        self.lbl_queue = ttk.Label(info, text="Ready: []")
        self.lbl_queue.pack(side=tk.LEFT, padx=14)

    def build_right_panel(self):
        right = ttk.Frame(self)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # Totals
        tf = ttk.Labelframe(right, text="Chỉ số tổng")
        tf.pack(fill=tk.X)

        self.var_wt = tk.StringVar(value="0.00")
        self.var_tat = tk.StringVar(value="0.00")
        self.var_util = tk.StringVar(value="0.00%")
        self.var_tp = tk.StringVar(value="0.00/s")

        row = ttk.Frame(tf); row.pack(fill=tk.X, padx=6, pady=4)
        ttk.Label(row, text="Avg Waiting:").pack(side=tk.LEFT)
        ttk.Label(row, textvariable=self.var_wt).pack(side=tk.RIGHT)

        row = ttk.Frame(tf); row.pack(fill=tk.X, padx=6, pady=4)
        ttk.Label(row, text="Avg Turnaround:").pack(side=tk.LEFT)
        ttk.Label(row, textvariable=self.var_tat).pack(side=tk.RIGHT)

        row = ttk.Frame(tf); row.pack(fill=tk.X, padx=6, pady=4)
        ttk.Label(row, text="CPU Utilization:").pack(side=tk.LEFT)
        ttk.Label(row, textvariable=self.var_util).pack(side=tk.RIGHT)

        row = ttk.Frame(tf); row.pack(fill=tk.X, padx=6, pady=4)
        ttk.Label(row, text="Throughput:").pack(side=tk.LEFT)
        ttk.Label(row, textvariable=self.var_tp).pack(side=tk.RIGHT)

        # Table
        tblf = ttk.Labelframe(right, text="Kết quả từng tiến trình")
        tblf.pack(fill=tk.BOTH, expand=True, pady=(10,0))

        self.tbl = ttk.Treeview(tblf, columns=("ct","wt","tat","rt"), show="headings")
        self.tbl.heading("ct", text="CT")
        self.tbl.heading("wt", text="WT")
        self.tbl.heading("tat", text="TAT")
        self.tbl.heading("rt", text="RT")
        self.tbl.column("ct", width=60, anchor="center")
        self.tbl.column("wt", width=60, anchor="center")
        self.tbl.column("tat", width=60, anchor="center")
        self.tbl.column("rt", width=60, anchor="center")
        self.tbl.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

    # ---- Data ops ----
    def add_proc(self):
        pid = self.ent_pid.get().strip() or f"P{len(self.processes)+1}"
        try:
            arr = int(self.ent_arr.get().strip())
            bur = int(self.ent_burst.get().strip())
        except ValueError:
            messagebox.showerror("Lỗi", "Arrival/Burst phải là số nguyên.")
            return
        if arr < 0 or bur <= 0:
            messagebox.showerror("Lỗi", "Arrival >= 0 và Burst > 0.")
            return
        if any(p.pid == pid for p in self.processes):
            messagebox.showerror("Lỗi", "PID đã tồn tại.")
            return
        self.processes.append(Proc(pid, arr, bur))
        self.lst.insert(tk.END, f"{pid} - A={arr}  B={bur}")

        # color map
        if pid not in self.colors:
            self.colors[pid] = self.palette[(len(self.colors)) % len(self.palette)]

    def remove_selected(self):
        sel = self.lst.curselection()
        if not sel: return
        idx = sel[0]
        pid = self.processes[idx].pid
        self.lst.delete(idx)
        del self.processes[idx]
        # keep color mapping (helps when re-adding)

    def clear_list(self):
        self.lst.delete(0, tk.END)
        self.processes.clear()
        # do not clear colors so demos keep colors

    def add_demo(self):
        demo = [Proc("P1",0,7), Proc("P2",2,4), Proc("P3",4,1)]
        for p in demo:
            self.processes.append(p)
            self.lst.insert(tk.END, f"{p.pid} - A={p.arrival}  B={p.burst}")
            if p.pid not in self.colors:
                self.colors[p.pid] = self.palette[(len(self.colors)) % len(self.palette)]

    # ---- Scheduling & animation ----
    def run_schedule(self):
        if self.animating:
            return
        if not self.processes:
            messagebox.showinfo("Thông báo","Hãy thêm ít nhất 1 tiến trình.")
            return
        try:
            q = int(self.sp_q.get())
            cs = int(self.sp_cs.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Quantum/CS phải là số.")
            return
        # deep copy processes for compute (keep original list intact)
        cloned = [Proc(p.pid, p.arrival, p.burst) for p in self.processes]
        self.segments, self.stats, self.totals = compute_rr(cloned, q, cs)
        self.update_totals()
        self.populate_table()
        self.prepare_canvas()
        self.anim_idx = 0
        self.animating = True
        self.btn_pause.configure(state=tk.NORMAL, text="Pause")
        self.animate_step()

    def step_once(self):
        # step through precomputed segments one by one
        if not self.segments:
            self.run_schedule()
            return
        if self.anim_idx >= len(self.segments):
            return
        self.draw_segment(self.segments[self.anim_idx])
        self.anim_idx += 1
        self.lbl_now.configure(text=f"t = {self.segments[self.anim_idx-1].end}")

    def toggle_pause(self):
        if not self.animating:
            # resume auto animation
            self.animating = True
            self.btn_pause.configure(text="Pause")
            self.animate_step()
        else:
            self.animating = False
            self.btn_pause.configure(text="Resume")

    def reset_all(self):
        self.anim_idx = 0
        self.animating = False
        self.btn_pause.configure(state=tk.DISABLED, text="Pause")
        self.canvas.delete("all")
        self.lbl_now.configure(text="t = 0")
        self.lbl_queue.configure(text="Ready: []")
        self.tbl.delete(*self.tbl.get_children())
        self.var_wt.set("0.00")
        self.var_tat.set("0.00")
        self.var_util.set("0.00%")
        self.var_tp.set("0.00/s")
        self.segments = []
        self.stats = {}
        self.totals = {}

    def animate_step(self):
        if not self.animating:
            return
        if self.anim_idx >= len(self.segments):
            self.animating = False
            self.btn_pause.configure(state=tk.DISABLED, text="Pause")
            return
        seg = self.segments[self.anim_idx]
        self.draw_segment(seg)
        self.anim_idx += 1
        self.lbl_now.configure(text=f"t = {seg.end}")
        try:
            delay = int(self.sp_speed.get())
        except:
            delay = 250
        self.after(max(1, delay), self.animate_step)

    # ---- Canvas drawing ----
    def prepare_canvas(self):
        self.canvas.delete("all")
        # Auto scale to fit to ~1200px wide if can
        makespan = self.segments[-1].end if self.segments else 0
        if makespan <= 0:
            self.scale_px = 24
        else:
            target = 1400
            self.scale_px = max(8, min(40, int(target / max(1, makespan))))
        # Axis
        self.canvas.create_text(10, 12, anchor="w", fill="#9AA0A6",
                                text="Thời gian (đơn vị)")
        # baseline
        self.canvas.create_line(0, 40, 9999, 40, fill="#2A2F36")

    def draw_segment(self, seg: Segment):
        # y bands: we draw everything on a single band for simplicity
        y0 = 60
        y1 = y0 + self.row_height

        x0 = seg.start * self.scale_px + 10
        x1 = seg.end   * self.scale_px + 10

        if seg.kind == 'run' and seg.pid:
            color = self.colors.get(seg.pid, "#4895EF")
            rect = self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, width=0)
            self.canvas.create_text((x0+x1)//2, (y0+y1)//2, text=seg.pid, fill="white")
        elif seg.kind == 'cs':
            # context switch as striped/gray bar
            rect = self.canvas.create_rectangle(x0, y0, x1, y1, fill=self.cs_color, width=0)
            self.canvas.create_text((x0+x1)//2, (y0+y1)//2, text="CS", fill="#EDEDED")
        else:
            # idle gap
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=self.idle_color, width=0)
            self.canvas.create_text((x0+x1)//2, (y0+y1)//2, text="IDLE", fill="#C9D1D9")

        # ticks
        for t in range(seg.start, seg.end+1):
            X = t*self.scale_px + 10
            self.canvas.create_line(X, y1+1, X, y1+6, fill="#2A2F36")
            if t % 5 == 0:
                self.canvas.create_text(X, y1+16, text=str(t), fill="#9AA0A6")

        # Scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # Auto-scroll to show the latest part
        self.canvas.xview_moveto(max(0.0, (x1-600)/max(1, (self.canvas.bbox("all")[2]-600))))

        # Update “Ready” label (approx): show queue after this segment
        # Quick preview: collect the next contiguous run PIDs
        q_preview = []
        for j in range(self.anim_idx+1, min(self.anim_idx+1+6, len(self.segments))):
            s = self.segments[j]
            if s.kind == 'run' and s.pid:
                q_preview.append(s.pid)
        self.lbl_queue.configure(text=f"Ready: {q_preview}")

    # ---- Totals & table ----
    def update_totals(self):
        if not self.totals: return
        self.var_wt.set(f"{self.totals['avg_wt']:.2f}")
        self.var_tat.set(f"{self.totals['avg_tat']:.2f}")
        self.var_util.set(f"{self.totals['cpu_util']:.2f}%")
        self.var_tp.set(f"{self.totals['throughput']:.2f}/u")

    def populate_table(self):
        self.tbl.delete(*self.tbl.get_children())
        for pid in sorted(self.stats.keys()):
            s = self.stats[pid]
            self.tbl.insert("", tk.END, values=(s["CT"], s["WT"], s["TAT"], s["RT"]))

if __name__ == "__main__":
    app = RRApp()
    app.mainloop()
