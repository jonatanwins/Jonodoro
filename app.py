import tkinter as tk
from tkinter import messagebox
import time
import matplotlib.pyplot as plt
from datetime import datetime


class TimerApp:
    def __init__(self, master):
        self.master = master
        master.title("Jonodoro")

        self.start_time = None
        self.timer_running = False
        self.break_timer_running = False
        self.break_end_time = None
        # Store tuples of (work_time, break_time)
        self.sessions = []

        # Bind spacebar to start/stop
        master.bind('<space>', lambda e: self.handle_spacebar())

        self.label = tk.Label(master, text="00:00:00", font=("Arial", 24))
        self.label.pack(pady=20)

        self.start_button = tk.Button(
            master, text="Start Work", command=self.start_or_end_timer
        )
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(
            master, text="Stop Work", command=self.stop_timer, state=tk.DISABLED
        )
        self.stop_button.pack(pady=10)

        self.show_graph_button = tk.Button(
            master, text="Show Sessions Graph", command=self.show_graph
        )
        self.show_graph_button.pack(pady=10)

        self.fraction_label = tk.Label(master, text="Break fraction (e.g., 1/3):")
        self.fraction_label.pack(pady=5)

        self.fraction_entry = tk.Entry(master)
        self.fraction_entry.insert(0, "1/3")
        self.fraction_entry.pack(pady=5)

    def handle_spacebar(self):
        if self.timer_running:
            self.stop_timer()
        elif self.break_timer_running:
            self.end_break()
        else:
            self.start_timer()

    def start_or_end_timer(self):
        if self.break_timer_running:
            self.end_break()
        else:
            self.start_timer()

    def start_timer(self):
        self.start_time = time.time()
        self.timer_running = True
        self.break_timer_running = False
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.update_timer()

    def stop_timer(self):
        if self.timer_running:
            self.timer_running = False
            elapsed_time = time.time() - self.start_time
            self.current_work_time = elapsed_time  # Store work time for this session
            self.start_button.config(state=tk.NORMAL, text="Start Work")
            self.stop_button.config(state=tk.DISABLED)
            self.start_break(elapsed_time)

    def update_timer(self):
        if self.timer_running:
            elapsed_time = time.time() - self.start_time
            time_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
            self.label.config(text=time_str)
            self.master.after(1000, self.update_timer)
        elif self.break_timer_running:
            remaining_time = max(0, self.break_end_time - time.time())
            time_str = time.strftime("%H:%M:%S", time.gmtime(remaining_time))
            self.label.config(text=f"Break: {time_str}")
            if remaining_time > 0:
                self.master.after(1000, self.update_timer)
            else:
                self.break_timer_running = False
                self.start_button.config(state=tk.NORMAL, text="Start Work")
                # Save session when break is complete
                self.sessions.append((self.current_work_time, self.current_break_time))
                messagebox.showinfo(
                    "Break Finished", "Break time is over. Ready to start working?"
                )

    def start_break(self, elapsed_time):
        try:
            fraction = eval(self.fraction_entry.get())
            break_time = elapsed_time * fraction
            self.current_break_time = break_time  # Store break time for this session
            self.break_end_time = time.time() + break_time
            self.break_timer_running = True
            self.start_button.config(state=tk.NORMAL, text="End Break")
            self.update_timer()
        except:
            messagebox.showerror(
                "Error", "Invalid fraction. Please enter a valid fraction (e.g., 1/3)"
            )
            self.start_button.config(state=tk.NORMAL, text="Start Work")

    def end_break(self):
        remaining_break_time = self.break_end_time - time.time()
        # Adjust break time if ended early
        self.current_break_time -= remaining_break_time
        # Save session when break is ended early
        self.sessions.append((self.current_work_time, self.current_break_time))
        self.break_timer_running = False
        self.start_timer()

    def show_graph(self):
        if not self.sessions:
            messagebox.showinfo("No Data", "No sessions recorded yet!")
            return
            
        work_times = [session[0]/60 for session in self.sessions]  # Convert to minutes
        break_times = [session[1]/60 for session in self.sessions]  # Convert to minutes
        
        plt.figure(figsize=(10, 6))
        
        # Create bar positions
        positions = range(len(self.sessions))
        
        # Create stacked bar chart with new colors
        plt.bar(positions, work_times, label='Work Time', color='#FF968A')  # Pastel light red
        plt.bar(positions, break_times, bottom=work_times, label='Break Time', color='#A2E1DB')  # Pastel light blue
        
        plt.title('Work and Break Sessions')
        plt.xlabel('Session Number')
        plt.ylabel('Duration (minutes)')
        plt.legend()
        
        # Set x-axis ticks to show session numbers starting from 1
        plt.xticks(positions, [f'Session {i+1}' for i in positions])
        plt.tight_layout()
        plt.show()


root = tk.Tk()
app = TimerApp(root)
root.mainloop()
