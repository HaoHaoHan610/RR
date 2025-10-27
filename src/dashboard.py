import customtkinter as ctk
from tkinter import ttk, messagebox
from collections import deque
import tkinter as tk
from initializing_process import seg_initializing

ctk.set_appearance_mode("dark")

class Proc:
    def __init__ (self,pid,arrival,burst,start = None,complete = None):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.start = start
        self.complete = complete
        self.remain = self.burst

class Segment:
    def __init__(self,pid,start,end,kind):
        self.pid = pid
        self.start = start
        self.end = end
        self.kind = kind

def CalculateRR(processes, quantum,cs):
    procs = {p.pid: p for p in processes}
    arrivals = sorted(processes,key=lambda p: p.arrival)
    # To sort on arrival time 

    time = 0
    i = 0
    ready = deque()
    segments: list[Segment] = []
    total_runtime = 0

    def flush_arrivals(upto_time):
        nonlocal i, ready # use directly index and ready in function
        while i < len(arrivals) and arrivals[i].arrival <= upto_time:
            ready.append(arrivals[i])
            i += 1 #add arrival time of process

    flush_arrivals(time)

    while True:
        if all(p.remain == 0 for p in procs.values()):
            break # ALL DONE

        if not ready:
            if i < len(arrivals):
                next_t = arrivals[i].arrival
                if next_t > time:
                    segments.append(Segment(None, time,next_t,'idle'))
                    time = next_t
                flush_arrivals(time)
            else:   
                break

        if not ready:
            continue

        p = ready.popleft()

        if p.start is None:
            p.start = time
        
        slice_len = min(quantum,p.remain)
        seg_start = time
        seg_end = time + slice_len
        segments.append(Segment(p.pid,seg_start,seg_end,'run'))
        total_runtime += slice_len
        time = seg_end
        p.remain -= slice_len

        flush_arrivals(time)

        if p.remain > 0:
            ready.append(p)
        else:
            p.end = time
        
        more_head = any(q.remain > 0 for q in procs.values())
        if cs > 0 and more_head:
            segments.append(Segment(None,time,time + cs, 'cs'))
            time += cs
            flush_arrivals(time)
    makespan = segments[-1].end if segments else 0

    stats = {}
    for pid, p in procs.items():
        ct = p.end 
        tat = ct - p.arrival
        wt = tat - p.burst
        rt = (p.start - p.arrival) if p.start is not None else 0
        stats[pid] = dict(CT = ct, WT=wt, TAT = tat,RT = rt)

    totals = dict(
        avg_wt = sum(s["WT"] for s in stats.values())/len(stats) if stats else 0.0,
        avg_tat = sum(s["TAT"] for s in stats.values())/len(stats) if stats else 0.0,
        throughput = (len(processes)/makespan) if makespan>0 else 0.0,
        cpu_util = (total_runtime/makespan*100.0) if makespan>0 else 0.0,
        makespan = makespan
    )
    return segments, stats, totals


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1000x600")
        self.title("ROUND ROBIN ALGORITHM")
        self.configure(fg_color="#0F0E0E")
        # self._set_appearance_mode("dark")

        self.processes: list[Proc] = []
        self.segments: list[Segment] = []
        self.stats: dict = {}
        self.totals: dict = {}
        self.anim_idx = 0
        self.animating = False
        self.scale_px = 70
        self.row_height = 80
        self.colors = {}
        self.palette = [
            "#4CC9F0", "#F72585", "#7209B7", "#3A0CA3", "#4361EE",
            "#4895EF", "#F15BB5", "#43AA8B", "#F9C74F", "#90BE6D",
        ]

        self.bg_dark = "#111418"
        self.fg = "#E6E6E6"
        self.cs_color = "#666A73"
        self.idle_color = "#2B2F36"

        self.configure(bg = self.bg_dark)
        style = ttk.Style(self)
        # Customizing the style of theme
        try:
            style.theme_use("clam")
        except:
            pass

        style.configure("TLabel",foreground = self.fg,background =self.bg_dark)
        style.configure("TFrame",background = self.bg_dark)
        style.configure("TLabelframe",background = self.bg_dark,foreground = self.fg)
        style.configure("TButton",padding = 6)
        style.configure("Treeview",
                        background="#1A1F25", foreground=self.fg, fieldbackground="#1A1F25",
                        rowheight=26)
        style.configure("Vertical.TScrollbar", background="#222")

        self.build_left_panel()
        self.build_center_canvas()
        self.build_right_panel()
    
    def build_left_panel(self):
        # self.geometry("200x600")
        
        side = [(2,2),(5 ,5)]

        left = ctk.CTkFrame(self)
        
        left.configure(fg_color="#0F0E0E")
        
        left.pack(side=ctk.LEFT, fill='y') 

        # left._set_appearance_mode("dark")

        label = ctk.CTkLabel(left, text="INPUT", font=("Helvetica", 20,"bold"))
        label.pack()

        frm = ctk.CTkFrame(left)
        frm.configure(fg_color = "#0F0E0E")
        frm.pack(fill='x', padx=6, pady=0)

        # left._set_appearance_mode("dark")
        label1 = ctk.CTkLabel(master=frm,
                               text="Process ID",
                               fg_color="#468A9A",
                               width= 50,
                               text_color="white",
                               corner_radius=10)
        label1.grid(row=1, column=0, sticky='ew',padx = side[0],pady = side[1])

        label2 = ctk.CTkLabel(master=frm,
                               text="Arrival Time",
                               fg_color="#468A9A",
                               text_color="white",
                               corner_radius=10)
        label2.grid(row=1, column=1, sticky='ew',padx = side[0],pady = side[1])

        label3 = ctk.CTkLabel(master=frm,
                               text="Burst Time",
                               fg_color="#468A9A",
                               text_color="white",
                               corner_radius=10)
        label3.grid(row=1, column=2, sticky='ew',padx = side[0],pady = side[1])

        self.ent_pid = ctk.CTkEntry(frm)
        self.ent_arr = ctk.CTkEntry(frm)
        self.ent_burst = ctk.CTkEntry(frm)
        # self.ent_rand = ctk.CTkEntry(frm)

        self.ent_pid.grid(row = 2, column = 0,sticky = 'w',padx = side[0],pady = side[1])
        self.ent_arr.grid(row = 2, column = 1,sticky = 'w',padx = side[0],pady = side[1])
        self.ent_burst.grid(row = 2, column = 2,sticky = 'w',padx = side[0],pady = side[1])

        btns = ctk.CTkFrame(left,corner_radius=8)
        btns.configure(fg_color="#0F0E0E")
        btns.pack(fill = 'x', padx=6, pady=6)
        ctk.CTkButton(btns, text="Add", command=self.add_proc).pack(side = ctk.LEFT,padx = side[0],pady = side[1])
        ctk.CTkButton(btns, text="Remove", command=self.remove_selected).pack(side = ctk.LEFT,padx = side[0],pady = side[1])
        ctk.CTkButton(btns, text="Clear", command=self.clear_list).pack(side = ctk.LEFT,padx = side[0],pady = side[1])

        self.lst = tk.Listbox(left, height=8, bg="#0F0E0E", fg=self.fg, selectmode=tk.SINGLE, borderwidth=8)
        self.lst.pack(fill=tk.BOTH, expand=True, padx=side[0], pady=side[1])
        
        cf = ctk.CTkFrame(left,corner_radius=8,border_width=2)
        cf.configure(fg_color="#0F0E0E")
        cf.pack(fill = ctk.X,padx=(6,6), pady=6)

        r1 = ctk.CTkFrame(cf)
        r1.configure(fg_color="#0F0E0E")
        r1.pack(fill=tk.X, padx=(6,6), pady=6)

        ctk.CTkLabel(r1, text="Quantum").pack(side=tk.LEFT)
        self.sp_q = tk.Spinbox(r1, from_=1, to=100, width=6)
        self.sp_q.delete(0, tk.END); self.sp_q.insert(0, "3")
        self.sp_q.pack(side=tk.LEFT, padx=(6,14))

        ctk.CTkLabel(r1, text="Context switch").pack(side=tk.LEFT)
        self.sp_cs = tk.Spinbox(r1, from_=0, to=20, width=6)
        self.sp_cs.delete(0, tk.END); self.sp_cs.insert(0, "0")
        self.sp_cs.pack(side=tk.LEFT, padx=(6,0))

        r2 = ctk.CTkFrame(cf)
        r2.configure(fg_color="#0F0E0E")
        r2.pack(fill=tk.X, padx=6, pady=4)
        ctk.CTkLabel(r2, text="Tốc độ (ms/segment)").pack(side=tk.LEFT)
        self.sp_speed = tk.Spinbox(r2, from_=1, to=2000, width=6)
        self.sp_speed.delete(0, tk.END); self.sp_speed.insert(0, "250")
        self.sp_speed.pack(side=tk.LEFT, padx=(6,0))

        # ACTION
        af = ctk.CTkFrame(left)
        af.pack(fill=tk.X, pady=(6,0))
        ctk.CTkButton(af, text="Run", command=self.run_schedule).grid(row = 1, column = 0,sticky = 'w',padx = side[0],pady = side[1])
        ctk.CTkButton(af, text="Step", command=self.step_once).grid(row = 1, column = 1,sticky = 'w',padx = side[0],pady = side[1])
        self.btn_pause = ctk.CTkButton(af, text="Pause", command=self.toggle_pause, state=tk.DISABLED)
        self.btn_pause.grid(row = 1, column = 2,sticky = 'w',padx = side[0],pady = side[1])
        ctk.CTkButton(af, text="Reset", command=self.reset_all).grid(row = 2, column = 0,sticky = 'w',padx = side[0],pady = side[1])

        ctk.CTkButton(af, text="ADD", command=self.addNnum).grid(row = 2, column = 1,sticky = 'w',padx = side[0],pady = side[1])
        self.ent_add = ctk.CTkEntry(af)
        self.ent_add.grid(row = 2, column = 2,sticky = 'w',padx = side[0],pady = side[1])



    def build_center_canvas(self):
        mid = ctk.CTkFrame(self)
        mid.configure(fg_color="#0F0E0E")
        mid.pack(side=ctk.LEFT, fill=ctk.BOTH, expand = True,pady = 0)

        title = ctk.CTkLabel(mid, text="GANT CHART", font=("Helvetica", 20,"bold"))
        title.pack()

        cv_frame = ctk.CTkFrame(mid)
        cv_frame.pack(fill = ctk.BOTH,expand = True)

        self.canvas = ctk.CTkCanvas(cv_frame, bg="#3C3D37", height=200, highlightthickness=0)
        self.hbar = ctk.CTkScrollbar(cv_frame, orientation=ctk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.hbar.set)

        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.hbar.pack(fill=tk.X)

        # INFO

        info = ctk.CTkFrame(mid)
        info.pack(fill=tk.X, pady=(8,0))
        self.lbl_now = ctk.CTkLabel(info, text="t = 0")
        self.lbl_now.pack(side=tk.LEFT, padx=4)
        self.lbl_queue = ctk.CTkLabel(info, text="Ready: []")
        self.lbl_queue.pack(side=tk.LEFT, padx=14)

    def build_right_panel(self):
        right = ctk.CTkFrame(self)
        right.configure(fg_color="#0F0E0E")
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        title = ctk.CTkLabel(right, text="TOTAL", font=("Helvetica", 20,"bold"))
        title.pack()
        # Totals
        tf = ctk.CTkFrame(right)
        tf.pack(fill=tk.X)

        self.var_wt = tk.StringVar(value="0.00")
        self.var_tat = tk.StringVar(value="0.00")
        self.var_util = tk.StringVar(value="0.00%")
        self.var_tp = tk.StringVar(value="0.00/s")

        row = ctk.CTkFrame(tf,corner_radius=8);
        row.pack(fill=tk.X, padx=6, pady=4)
        ctk.CTkLabel(row, text="Avg Waiting:",height=20).pack(side=tk.LEFT)
        ctk.CTkLabel(row, textvariable=self.var_wt,height=20).pack(side=tk.RIGHT)

        row = ctk.CTkFrame(tf); row.pack(fill=tk.X, padx=6, pady=4)
        ctk.CTkLabel(row, text="Avg Turnaround:",height=20).pack(side=tk.LEFT)
        ctk.CTkLabel(row, textvariable=self.var_tat,height=20).pack(side=tk.RIGHT)

        row = ctk.CTkFrame(tf); row.pack(fill=tk.X, padx=6, pady=4)
        ctk.CTkLabel(row, text="CPU Utilization:",height=20).pack(side=tk.LEFT)
        ctk.CTkLabel(row, textvariable=self.var_util,height=20).pack(side=tk.RIGHT)

        row = ctk.CTkFrame(tf); row.pack(fill=tk.X, padx=6, pady=4)
        ctk.CTkLabel(row, text="Throughput:",height=20).pack(side=tk.LEFT)
        ctk.CTkLabel(row, textvariable=self.var_tp,height=20).pack(side=tk.RIGHT)

        # Table
        tblf = ttk.Labelframe(right, text="RESULT ALL OF PROCESSES")
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

    def addNnum(self):
        try:
            n = int(self.ent_add.get().strip())
        except ValueError:
            messagebox.showerror("ERRROR", "AN AMOUNT OF PROCESSES MUST BE INT")
            return
        pids, arrs, burs = seg_initializing(n)
        for i in range(n):
            self.processes.append(Proc(pids[i], arrs[i], burs[i]))
            self.lst.insert(tk.END, f"{pids[i]} - A={arrs[i]}  B={burs[i]}")
            if pids[i] not in self.colors:
                self.colors[pids[i]] = self.palette[(len(self.colors)) % len(self.palette)]

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
    
    def clear_list(self):
        self.lst.delete(0, tk.END)
        self.processes.clear()

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
        self.segments, self.stats, self.totals = CalculateRR(cloned, q, cs)
        self.update_totals()
        self.populate_table()
        self.prepare_canvas()
        self.anim_idx = 0
        self.animating = True
        self.btn_pause.configure(state=tk.NORMAL, text="Pause")
        self.animate_step()

    def step_once(self):
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
    
    def prepare_canvas(self):
        self.canvas.delete("all")
        # Auto scale to fit to ~1200px wide if can
        makespan = self.segments[-1].end if self.segments else 0
        if makespan <= 0:
            self.scale_px = 50
        else:
            target = 1400
            self.scale_px = max(8, min(100, int(target / max(1, makespan))))
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



app = App()
app.mainloop()