import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta

class RecoveryTracker:
    def __init__(self, parent, conn):
        self.parent = parent
        self.conn = conn
        self.cursor = conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS recovery_logs (
                id INTEGER PRIMARY KEY,
                date TEXT,
                energy_level INTEGER,
                sleep_hours REAL,
                physical_activity TEXT,
                recovery_activity TEXT,
                notes TEXT
            )
        ''')
        
        self.setup_ui()
        self.load_recovery_data()

    def setup_ui(self):
        # Main container with left and right panes
        container = ttk.PanedWindow(self.parent, orient=tk.HORIZONTAL)
        container.pack(fill=tk.BOTH, expand=True)

        # Left pane for data entry
        left_frame = ttk.Frame(container)
        container.add(left_frame)

        # Energy level slider
        ttk.Label(left_frame, text="Energy Level (1-10):").pack(pady=5)
        self.energy_var = tk.IntVar(value=5)
        energy_scale = ttk.Scale(left_frame, from_=1, to=10, variable=self.energy_var, orient=tk.HORIZONTAL)
        energy_scale.pack(fill=tk.X, padx=20)

        # Sleep hours
        ttk.Label(left_frame, text="Sleep Hours:").pack(pady=5)
        self.sleep_var = tk.StringVar(value="8.0")
        sleep_entry = ttk.Entry(left_frame, textvariable=self.sleep_var)
        sleep_entry.pack(fill=tk.X, padx=20)

        # Physical activity
        ttk.Label(left_frame, text="Physical Activity:").pack(pady=5)
        self.activity_var = tk.StringVar()
        activity_combo = ttk.Combobox(left_frame, textvariable=self.activity_var,
                                    values=['Light', 'Moderate', 'Intense', 'Rest'])
        activity_combo.pack(fill=tk.X, padx=20)

        # Recovery activity
        ttk.Label(left_frame, text="Recovery Activity:").pack(pady=5)
        self.recovery_var = tk.StringVar()
        recovery_combo = ttk.Combobox(left_frame, textvariable=self.recovery_var,
                                    values=['Stretching', 'Meditation', 'Light Walk', 'None'])
        recovery_combo.pack(fill=tk.X, padx=20)

        # Notes
        ttk.Label(left_frame, text="Notes:").pack(pady=5)
        self.notes_text = tk.Text(left_frame, height=4)
        self.notes_text.pack(fill=tk.X, padx=20)

        # Save button
        ttk.Button(left_frame, text="Save Log", command=self.save_recovery_log).pack(pady=20)

        # Right pane for visualization
        right_frame = ttk.Frame(container)
        container.add(right_frame)

        # Energy level trend chart
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def save_recovery_log(self):
        self.cursor.execute('''
            INSERT INTO recovery_logs 
            (date, energy_level, sleep_hours, physical_activity, recovery_activity, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().strftime('%Y-%m-%d'),
            self.energy_var.get(),
            float(self.sleep_var.get()),
            self.activity_var.get(),
            self.recovery_var.get(),
            self.notes_text.get("1.0", tk.END.strip())
        ))
        self.conn.commit()
        self.load_recovery_data()

    def load_recovery_data(self):
        self.cursor.execute('''
            SELECT date, energy_level, sleep_hours 
            FROM recovery_logs 
            ORDER BY date DESC 
            LIMIT 14
        ''')
        data = self.cursor.fetchall()
        
        if data:
            dates = [row[0] for row in data]
            energy = [row[1] for row in data]
            sleep = [row[2] for row in data]
            
            self.ax.clear()
            self.ax.plot(dates, energy, 'b-', label='Energy Level')
            self.ax.plot(dates, sleep, 'r-', label='Sleep Hours')
            self.ax.set_xlabel('Date')
            self.ax.set_ylabel('Level')
            self.ax.legend()
            self.ax.tick_params(axis='x', rotation=45)
            self.fig.tight_layout()
            self.canvas.draw()