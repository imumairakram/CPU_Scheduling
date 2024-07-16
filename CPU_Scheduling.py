import tkinter as tk
from tkinter import ttk, messagebox
import queue

class ProcessSchedulingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Calculator")
        self.root.geometry("1000x700")
        
        self.processes = []
        
        # GUI Elements
        self.create_widgets()
        self.show_instructions()

    def create_widgets(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=20)

        # Algorithm selection
        tk.Label(self.frame, text="Algorithm", font=('Arial', 12)).grid(row=0, column=0, padx=10, pady=5)
        self.algorithm = tk.StringVar()
        self.algorithm_dropdown = ttk.Combobox(self.frame, textvariable=self.algorithm, values=["FCFS", "SJF", "RR", "Preemptive FCFS", "Preemptive SJF", "Non-Preemptive Priority", "Preemptive Priority"], font=('Arial', 12))
        self.algorithm_dropdown.grid(row=0, column=1, padx=10, pady=5)

        # Arrival Times
        tk.Label(self.frame, text="Arrival Times", font=('Arial', 12)).grid(row=1, column=0, padx=10, pady=5)
        self.arrival_times_entry = tk.Entry(self.frame, font=('Arial', 12))
        self.arrival_times_entry.grid(row=1, column=1, padx=10, pady=5)

        # Burst Times
        tk.Label(self.frame, text="Burst Times", font=('Arial', 12)).grid(row=2, column=0, padx=10, pady=5)
        self.burst_times_entry = tk.Entry(self.frame, font=('Arial', 12))
        self.burst_times_entry.grid(row=2, column=1, padx=10, pady=5)

        # Priority
        tk.Label(self.frame, text="Priority (Optional)", font=('Arial', 12)).grid(row=3, column=0, padx=10, pady=5)
        self.priority_entry = tk.Entry(self.frame, font=('Arial', 12))
        self.priority_entry.grid(row=3, column=1, padx=10, pady=5)
        
        # Quantum Time (only for RR)
        self.quantum_label = tk.Label(self.frame, text="Time Quantum", font=('Arial', 12))
        self.quantum_entry = tk.Entry(self.frame, font=('Arial', 12))

        # Update visibility of Quantum Time input based on algorithm selection
        self.algorithm.trace("w", self.update_quantum_visibility)
        
        # Solve Button
        self.solve_button = tk.Button(self.frame, text="Solve", command=self.execute, font=('Arial', 12))
        self.solve_button.grid(row=5, column=0, columnspan=2, pady=20)

        # Result Display
        self.result_frame = tk.Frame(self.root)
        self.result_frame.pack(pady=20)
        
        self.gantt_chart_label = tk.Label(self.result_frame, text="Gantt Chart", font=('Arial', 12))
        self.gantt_chart_label.grid(row=0, column=0, columnspan=2)

        self.gantt_canvas = tk.Canvas(self.result_frame, height=150, bg='white')
        self.gantt_canvas.grid(row=1, column=0, columnspan=2, pady=10)

        columns = ("Job", "Arrival Time", "Burst Time", "Priority", "Finish Time", "Turnaround Time", "Waiting Time")
        self.result_table = ttk.Treeview(self.result_frame, columns=columns, show='headings')
        for col in columns:
            self.result_table.heading(col, text=col)
            self.result_table.column(col, anchor=tk.CENTER)

        self.result_table.grid(row=2, column=0, columnspan=2, pady=10)
        
    def update_quantum_visibility(self, *args):
        algorithm = self.algorithm.get()
        if algorithm == "RR":
            self.quantum_label.grid(row=4, column=0, padx=10, pady=5)
            self.quantum_entry.grid(row=4, column=1, padx=10, pady=5)
            self.solve_button.grid(row=5, column=0, columnspan=2, pady=20)
        else:
            self.quantum_label.grid_remove()
            self.quantum_entry.grid_remove()
            self.solve_button.grid(row=4, column=0, columnspan=2, pady=20)

    def show_instructions(self):
        instruction_message = (
            "Instructions:\n\n"
            "1. Select a scheduling algorithm (FCFS, SJF, RR, Preemptive FCFS, Preemptive SJF, Non-Preemptive Priority, Preemptive Priority).\n"
            "2. Enter the arrival times of the processes, separated by spaces.\n"
            "3. Enter the burst times of the processes, separated by spaces.\n"
            "4. Enter the priority of the processes (optional), separated by spaces.\n"
            "5. If Round Robin (RR) is selected, enter the time quantum.\n"
            "6. Press the 'Solve' button to see the results.\n\n"
            "Press OK to close this pop-up."
        )
        messagebox.showinfo("Instructions", instruction_message)
        
    def execute(self):
        algorithm = self.algorithm.get()
        arrival_times = list(map(int, self.arrival_times_entry.get().split()))
        burst_times = list(map(int, self.burst_times_entry.get().split()))
        priority = list(map(int, self.priority_entry.get().split())) if self.priority_entry.get() else [0] * len(arrival_times)
        
        if len(arrival_times) != len(burst_times) or len(arrival_times) != len(priority):
            messagebox.showerror("Error", "Arrival, Burst times and Priority must have the same length")
            return
        
        self.processes = [(chr(65+i), arrival_times[i], burst_times[i], priority[i]) for i in range(len(arrival_times))]
        
        if algorithm == "FCFS":
            self.fcfs()
        elif algorithm == "SJF":
            self.sjf()
        elif algorithm == "RR":
            quantum = int(self.quantum_entry.get())
            self.rr(quantum)
        elif algorithm == "Preemptive FCFS":
            self.preemptive_fcfs()
        elif algorithm == "Preemptive SJF":
            self.preemptive_sjf()
        elif algorithm == "Non-Preemptive Priority":
            self.non_preemptive_priority()
        elif algorithm == "Preemptive Priority":
            self.preemptive_priority()
        else:
            messagebox.showerror("Error", "Please select a scheduling algorithm")
            
    def fcfs(self):
        self.processes.sort(key=lambda x: x[1])  # Sort by arrival time
        current_time = 0
        results = []
        gantt_chart = []

        for pid, arrival, burst, priority in self.processes:
            if current_time < arrival:
                current_time = arrival
            start_time = current_time
            current_time += burst
            end_time = current_time
            turnaround_time = end_time - arrival
            waiting_time = start_time - arrival
            results.append((pid, arrival, burst, priority, end_time, turnaround_time, waiting_time))
            gantt_chart.append((pid, start_time, end_time))

        self.display_results(results, gantt_chart)
        
    def sjf(self):
        self.processes.sort(key=lambda x: (x[1], x[2]))  # Sort by arrival time, then burst time
        current_time = 0
        results = []
        remaining_processes = self.processes[:]
        gantt_chart = []

        while remaining_processes:
            available_processes = [p for p in remaining_processes if p[1] <= current_time]
            if not available_processes:
                current_time = remaining_processes[0][1]
                continue
            shortest_job = min(available_processes, key=lambda x: x[2])
            remaining_processes.remove(shortest_job)
            pid, arrival, burst, priority = shortest_job
            start_time = current_time
            current_time += burst
            end_time = current_time
            turnaround_time = end_time - arrival
            waiting_time = start_time - arrival
            results.append((pid, arrival, burst, priority, end_time, turnaround_time, waiting_time))
            gantt_chart.append((pid, start_time, end_time))

        self.display_results(results, gantt_chart)
        
    def rr(self, quantum):
        q = queue.Queue()
        current_time = 0
        results = []
        gantt_chart = []
        remaining_burst_times = {pid: burst for pid, _, burst, _ in self.processes}
        process_dict = {pid: (arrival, burst, priority) for pid, arrival, burst, priority in self.processes}

        for pid, arrival, burst, priority in sorted(self.processes, key=lambda x: x[1]):
            q.put(pid)
        
        while not q.empty():
            pid = q.get()
            arrival, burst, priority = process_dict[pid]

            if current_time < arrival:
                current_time = arrival
            
            time_slice = min(quantum, remaining_burst_times[pid])
            start_time = current_time
            current_time += time_slice
            remaining_burst_times[pid] -= time_slice
            gantt_chart.append((pid, start_time, current_time))

            if remaining_burst_times[pid] > 0:
                q.put(pid)
            else:
                end_time = current_time
                turnaround_time = end_time - arrival
                waiting_time = turnaround_time - burst
                results.append((pid, arrival, burst, priority, end_time, turnaround_time, waiting_time))

        self.display_results(results, gantt_chart)

    def preemptive_fcfs(self):
        self.processes.sort(key=lambda x: x[1])
        current_time = 0
        results = []
        gantt_chart = []
        ready_queue = queue.Queue()

        for pid, arrival, burst, priority in self.processes:
            while not ready_queue.empty() and current_time < arrival:
                current_process = ready_queue.get()
                if current_time + current_process[2] > arrival:
                    remaining_burst = current_time + current_process[2] - arrival
                    ready_queue.put((current_process[0], current_time, remaining_burst, current_process[3]))
                    gantt_chart.append((current_process[0], current_time, arrival))
                    current_time = arrival
                else:
                    current_time += current_process[2]
                    end_time = current_time
                    turnaround_time = end_time - current_process[1]
                    waiting_time = end_time - current_process[1] - current_process[2]
                    results.append((current_process[0], current_process[1], current_process[2], current_process[3], end_time, turnaround_time, waiting_time))
                    gantt_chart.append((current_process[0], current_time - current_process[2], end_time))
            
            ready_queue.put((pid, arrival, burst, priority))

        while not ready_queue.empty():
            current_process = ready_queue.get()
            current_time += current_process[2]
            end_time = current_time
            turnaround_time = end_time - current_process[1]
            waiting_time = end_time - current_process[1] - current_process[2]
            results.append((current_process[0], current_process[1], current_process[2], current_process[3], end_time, turnaround_time, waiting_time))
            gantt_chart.append((current_process[0], current_time - current_process[2], end_time))

        self.display_results(results, gantt_chart)

    def preemptive_sjf(self):
        self.processes.sort(key=lambda x: x[1])  # Sort by arrival time
        current_time = 0
        results = []
        gantt_chart = []
        ready_queue = []
        process_dict = {pid: (arrival, burst, priority) for pid, arrival, burst, priority in self.processes}
        remaining_burst_times = {pid: burst for pid, _, burst, _ in self.processes}
        remaining_processes = self.processes[:]

        while remaining_processes or ready_queue:
            while remaining_processes and remaining_processes[0][1] <= current_time:
                pid, arrival, burst, priority = remaining_processes.pop(0)
                ready_queue.append((pid, remaining_burst_times[pid], priority))
                ready_queue.sort(key=lambda x: x[1])  # Sort by remaining burst time

            if not ready_queue:
                current_time = remaining_processes[0][1]
                continue

            current_process = ready_queue.pop(0)
            pid, remaining_burst, priority = current_process

            if remaining_processes and remaining_processes[0][1] <= current_time + remaining_burst:
                next_process_arrival = remaining_processes[0][1]
                time_slice = next_process_arrival - current_time
                current_time = next_process_arrival
                remaining_burst_times[pid] -= time_slice
                gantt_chart.append((pid, current_time - time_slice, current_time))
                if remaining_burst_times[pid] > 0:
                    ready_queue.append((pid, remaining_burst_times[pid], priority))
                    ready_queue.sort(key=lambda x: x[1])
            else:
                time_slice = remaining_burst
                current_time += time_slice
                gantt_chart.append((pid, current_time - time_slice, current_time))
                end_time = current_time
                turnaround_time = end_time - process_dict[pid][0]
                waiting_time = turnaround_time - process_dict[pid][1]
                results.append((pid, process_dict[pid][0], process_dict[pid][1], priority, end_time, turnaround_time, waiting_time))

        self.display_results(results, gantt_chart)

    def non_preemptive_priority(self):
        self.processes.sort(key=lambda x: (x[1], x[3]))  # Sort by arrival time, then priority
        current_time = 0
        results = []
        remaining_processes = self.processes[:]
        gantt_chart = []

        while remaining_processes:
            available_processes = [p for p in remaining_processes if p[1] <= current_time]
            if not available_processes:
                current_time = remaining_processes[0][1]
                continue
            highest_priority = min(available_processes, key=lambda x: x[3])
            remaining_processes.remove(highest_priority)
            pid, arrival, burst, priority = highest_priority
            start_time = current_time
            current_time += burst
            end_time = current_time
            turnaround_time = end_time - arrival
            waiting_time = start_time - arrival
            results.append((pid, arrival, burst, priority, end_time, turnaround_time, waiting_time))
            gantt_chart.append((pid, start_time, end_time))

        self.display_results(results, gantt_chart)

    def preemptive_priority(self):
        self.processes.sort(key=lambda x: x[1])  # Sort by arrival time
        current_time = 0
        results = []
        gantt_chart = []
        ready_queue = []
        process_dict = {pid: (arrival, burst, priority) for pid, arrival, burst, priority in self.processes}
        remaining_burst_times = {pid: burst for pid, _, burst, _ in self.processes}
        remaining_processes = self.processes[:]

        while remaining_processes or ready_queue:
            while remaining_processes and remaining_processes[0][1] <= current_time:
                pid, arrival, burst, priority = remaining_processes.pop(0)
                ready_queue.append((pid, remaining_burst_times[pid], priority))
                ready_queue.sort(key=lambda x: x[2])  # Sort by priority

            if not ready_queue:
                current_time = remaining_processes[0][1]
                continue

            current_process = ready_queue.pop(0)
            pid, remaining_burst, priority = current_process

            if remaining_processes and remaining_processes[0][1] <= current_time + remaining_burst:
                next_process_arrival = remaining_processes[0][1]
                time_slice = next_process_arrival - current_time
                current_time = next_process_arrival
                remaining_burst_times[pid] -= time_slice
                gantt_chart.append((pid, current_time - time_slice, current_time))
                if remaining_burst_times[pid] > 0:
                    ready_queue.append((pid, remaining_burst_times[pid], priority))
                    ready_queue.sort(key=lambda x: x[2])
            else:
                time_slice = remaining_burst
                current_time += time_slice
                gantt_chart.append((pid, current_time - time_slice, current_time))
                end_time = current_time
                turnaround_time = end_time - process_dict[pid][0]
                waiting_time = turnaround_time - process_dict[pid][1]
                results.append((pid, process_dict[pid][0], process_dict[pid][1], priority, end_time, turnaround_time, waiting_time))

        self.display_results(results, gantt_chart)

    def display_results(self, results, gantt_chart):
    	for i in self.result_table.get_children():
        	self.result_table.delete(i)
        
    	for row in results:
        	self.result_table.insert('', tk.END, values=row)
        
    	self.gantt_canvas.delete("all")
    
    	# Calculate total time and time unit
    	total_time = gantt_chart[-1][2]
    	time_unit = 15  # Adjust this value for spacing between time units
    
    	# Adjust canvas width based on total time and time unit
    	canvas_width = max(900, total_time * time_unit)  # Ensure canvas is at least 900 pixels wide
    	self.gantt_canvas.config(width=canvas_width, height=150)
    
    	#Draw Gantt chart
    	chart_height = 40
    	for i, (pid, start, end) in enumerate(gantt_chart):
        	start_x = start * time_unit
        	end_x = end * time_unit
        	self.gantt_canvas.create_rectangle(start_x, 20, end_x, 20 + chart_height, fill="lightblue")
        	self.gantt_canvas.create_text((start_x + end_x) / 2, 20 + chart_height / 2, text=pid, font=('Arial', 10))

    	# Add time unit markers below the Gantt chart
    	for t in range(total_time + 1):
        	x = t * time_unit
        	self.gantt_canvas.create_line(x, 20 + chart_height, x, 20 + chart_height + 10)
        	self.gantt_canvas.create_text(x, 20 + chart_height + 20, text=str(t), font=('Arial', 10))

        
	
       

if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessSchedulingApp(root)
    root.mainloop()
