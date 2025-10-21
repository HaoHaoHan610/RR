import tkinter as tk
from initializing_process import par_initializing



root = tk.Tk()

ProcessNumber = tk.StringVar()
def intitializing_process():
    n = int(ProcessNumber.get())
    par_initializing(n)

root.geometry("500x200")


# frame = tk.Frame(master=root)

label1 = tk.Label(master=root,text="Enter amount of process")
label1.pack()
entry1 = tk.Entry(master=root, textvariable=ProcessNumber)
entry1.pack()

button1 = tk.Button(master=root, text= "Agree",command=intitializing_process)
button1.pack()

root.mainloop()