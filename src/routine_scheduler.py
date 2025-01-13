import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from datetime import datetime, timedelta
import calendar
import sv_ttk

class ModernCalendar(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.date = datetime.now()
        self.selected_date = self.date
        self.callback = None
        self.setup_calendar()

    def setup_calendar(self):
        # Header with month and year
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        ctk.CTkButton(
            header_frame,
            text="←",
            width=40,
            command=self.prev_month,
            fg_color="#4CAF50",
            hover_color="#45a049"
        ).pack(side=tk.LEFT, padx=5)

        self.header_label = ctk.CTkLabel(
            header_frame,
            text=self.date.strftime("%B %Y"),
            font=("Helvetica", 16, "bold")
        )
        self.header_label.pack(side=tk.LEFT, expand=True)

        ctk.CTkButton(
            header_frame,
            text="→",
            width=40,
            command=self.next_month,
            fg_color="#4CAF50",
            hover_color="#45a049"
        ).pack(side=tk.RIGHT, padx=5)

        # Weekday headers
        days_frame = ctk.CTkFrame(self)
        days_frame.pack(fill=tk.BOTH, expand=True)
        
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(weekdays):
            days_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(
                days_frame,
                text=day,
                font=("Helvetica", 12, "bold")
            ).grid(row=0, column=i, pady=5)

        # Calendar days
        self.days_frame = ctk.CTkFrame(self)
        self.days_frame.pack(fill=tk.BOTH, expand=True)
        self.update_calendar()

    def update_calendar(self):
        # Clear previous calendar
        for widget in self.days_frame.winfo_children():
            widget.destroy()

        # Configure grid
        for i in range(7):
            self.days_frame.grid_columnconfigure(i, weight=1)

        # Get calendar for current month
        cal = calendar.monthcalendar(self.date.year, self.date.month)
        
        # Update header
        self.header_label.configure(text=self.date.strftime("%B %Y"))

        # Create day buttons
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day != 0:
                    day_date = datetime(self.date.year, self.date.month, day)
                    
                    # Style for current day
                    if day_date.date() == datetime.now().date():
                        fg_color = "#4CAF50"
                        hover_color = "#45a049"
                    else:
                        fg_color = "transparent"
                        hover_color = "#e0e0e0"

                    # Style for selected day
                    if day_date.date() == self.selected_date.date():
                        fg_color = "#2196F3"
                        hover_color = "#1976D2"

                    btn = ctk.CTkButton(
                        self.days_frame,
                        text=str(day),
                        width=40,
                        height=40,
                        corner_radius=20,
                        fg_color=fg_color,
                        hover_color=hover_color,
                        command=lambda d=day_date: self.select_date(d)
                    )
                    btn.grid(row=week_num, column=day_num, padx=2, pady=2)

    def select_date(self, date):
        self.selected_date = date
        if self.callback:
            self.callback(date)
        self.update_calendar()

    def prev_month(self):
        self.date = self.date.replace(day=1) - timedelta(days=1)
        self.update_calendar()

    def next_month(self):
        self.date = self.date.replace(day=28) + timedelta(days=5)
        self.date = self.date.replace(day=1)
        self.update_calendar()

class RoutineScheduler:
    def __init__(self, parent, conn):
        self.parent = parent
        self.conn = conn
        self.cursor = conn.cursor()
        
        self.setup_database()
        self.setup_ui()
        self.load_routines()

    def setup_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS routines (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                frequency TEXT,
                time TEXT,
                days TEXT,
                last_completed TEXT,
                color TEXT
            )
        ''')
        self.conn.commit()

    def setup_ui(self):
        # Main container with modern styling
        self.main_container = ctk.CTkFrame(self.parent)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left panel with calendar and routines list
        left_panel = ctk.CTkFrame(self.main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Modern calendar
        self.calendar = ModernCalendar(left_panel)
        self.calendar.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        self.calendar.callback = self.on_date_selected

        # Routines list with modern styling
        list_frame = ctk.CTkFrame(left_panel)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Routines header
        header_frame = ctk.CTkFrame(list_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        ctk.CTkLabel(
            header_frame,
            text="Today's Routines",
            font=("Helvetica", 16, "bold")
        ).pack(side=tk.LEFT)

        ctk.CTkButton(
            header_frame,
            text="+ Add Routine",
            command=self.show_add_routine_dialog,
            fg_color="#4CAF50",
            hover_color="#45a049"
        ).pack(side=tk.RIGHT)

        # Routines list
        self.routines_frame = ctk.CTkScrollableFrame(list_frame)
        self.routines_frame.pack(fill=tk.BOTH, expand=True)

    def show_add_routine_dialog(self):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Add New Routine")
        dialog.geometry("400x600")

        ctk.CTkLabel(dialog, text="Title:", font=("Helvetica", 12, "bold")).pack(pady=(20, 5))
        title_entry = ctk.CTkEntry(dialog, width=300)
        title_entry.pack(pady=(0, 15))

        ctk.CTkLabel(dialog, text="Frequency:", font=("Helvetica", 12, "bold")).pack(pady=5)
        frequency_var = tk.StringVar(value="Daily")
        frequency_frame = ctk.CTkFrame(dialog)
        frequency_frame.pack(pady=(0, 15))

        frequencies = ["Daily", "Weekly", "Monthly"]
        for freq in frequencies:
            ctk.CTkRadioButton(
                frequency_frame,
                text=freq,
                variable=frequency_var,
                value=freq
            ).pack(side=tk.LEFT, padx=10)

        ctk.CTkLabel(dialog, text="Time:", font=("Helvetica", 12, "bold")).pack(pady=5)
        time_frame = ctk.CTkFrame(dialog)
        time_frame.pack(pady=(0, 15))
        
        hour_var = tk.StringVar(value="00")
        minute_var = tk.StringVar(value="00")
        
        ctk.CTkOptionMenu(
            time_frame,
            variable=hour_var,
            values=[f"{i:02d}" for i in range(24)]
        ).pack(side=tk.LEFT, padx=5)
        
        ctk.CTkLabel(time_frame, text=":").pack(side=tk.LEFT)
        
        ctk.CTkOptionMenu(
            time_frame,
            variable=minute_var,
            values=[f"{i:02d}" for i in range(0, 60, 5)]
        ).pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(dialog, text="Days:", font=("Helvetica", 12, "bold")).pack(pady=5)
        days_frame = ctk.CTkFrame(dialog)
        days_frame.pack(pady=(0, 15))
        
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        day_vars = [tk.BooleanVar() for _ in days]
        
        for day, var in zip(days, day_vars):
            ctk.CTkCheckBox(
                days_frame,
                text=day,
                variable=var
            ).pack(side=tk.LEFT, padx=5)

        # Color picker
        ctk.CTkLabel(dialog, text="Color:", font=("Helvetica", 12, "bold")).pack(pady=5)
        color_var = tk.StringVar(value="#4CAF50")
        colors = ["#4CAF50", "#2196F3", "#FF9800", "#E91E63", "#9C27B0"]
        color_frame = ctk.CTkFrame(dialog)
        color_frame.pack(pady=(0, 15))

        for color in colors:
            ctk.CTkButton(
                color_frame,
                text="",
                width=30,
                height=30,
                fg_color=color,
                command=lambda c=color: color_var.set(c)
            ).pack(side=tk.LEFT, padx=5)

        def save_routine():
            selected_days = ','.join(
                day for day, var in zip(days, day_vars) if var.get()
            )
            
            time = f"{hour_var.get()}:{minute_var.get()}"
            
            self.cursor.execute('''
                INSERT INTO routines (title, frequency, time, days, color)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                title_entry.get(),
                frequency_var.get(),
                time,
                selected_days,
                color_var.get()
            ))
            self.conn.commit()
            self.load_routines()
            dialog.destroy()

        ctk.CTkButton(
            dialog,
            text="Save",
            command=save_routine,
            fg_color="#4CAF50",
            hover_color="#45a049"
        ).pack(pady=20)

    def on_date_selected(self, date):
        self.load_routines(date)

    def load_routines(self, date=None):
        if date is None:
            date = datetime.now()

        # Clear existing routines
        for widget in self.routines_frame.winfo_children():
            widget.destroy()

        # Load routines for selected date
        self.cursor.execute('SELECT * FROM routines')
        routines = self.cursor.fetchall()

        for routine in routines:
            routine_frame = ctk.CTkFrame(self.routines_frame)
            routine_frame.pack(fill=tk.X, pady=5)

            complete_btn = ctk.CTkCheckBox(
                routine_frame,
                text="",
                command=lambda r=routine: self.toggle_routine(r)
            )
            complete_btn.pack(side=tk.LEFT, padx=10)

            color_indicator = ctk.CTkButton(
                routine_frame,
                text="",
                width=20,
                height=20,
                fg_color=routine[6] or "#4CAF50"
            )
            color_indicator.pack(side=tk.LEFT, padx=5)

            ctk.CTkLabel(
                routine_frame,
                text=routine[1],
                font=("Helvetica", 12)
            ).pack(side=tk.LEFT, padx=5)

            ctk.CTkLabel(
                routine_frame,
                text=routine[3],
                font=("Helvetica", 10)
            ).pack(side=tk.RIGHT, padx=10)

    def toggle_routine(self, routine):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('''
            UPDATE routines 
            SET last_completed = ?
            WHERE id = ?
        ''', (now, routine[0]))
        self.conn.commit()
        self.load_routines()