import tkinter as tk
from tkinter import ttk
import sqlite3
from ttkthemes import ThemedTk
from PIL import Image, ImageTk
import sv_ttk

class ModernApp:
    def __init__(self):
        self.root = ThemedTk(theme="arc")
        self.root.title("Personal Management Tool")
        self.root.geometry("1200x800")
        
        # Apply material theme
        sv_ttk.set_theme("dark")
        
        # Configure root window grid
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        self.setup_styles()
        self.create_header()
        self.create_navigation()
        self.create_main_content()
        self.init_database()

    def setup_styles(self):
        style = ttk.Style()
        
        # Modern styling for frames
        style.configure(
            "Nav.TFrame",
            background="#1a1a1a"
        )
        
        # Header style
        style.configure(
            "Header.TLabel",
            font=('Helvetica', 16, 'bold'),
            foreground="#ffffff",
            background="#1a1a1a"
        )
        
        # Button style
        style.configure(
            "Nav.TButton",
            padding=10,
            font=('Helvetica', 10),
            background="#4CAF50",
            foreground="white"
        )

    def create_header(self):
        header = ttk.Frame(self.root, style="Nav.TFrame")
        header.pack(fill=tk.X, pady=0)

        # App title with logo
        title_frame = ttk.Frame(header, style="Nav.TFrame")
        title_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Create logo label
        logo_label = ttk.Label(
            title_frame,
            text="🎯",  # Unicode logo
            font=('Helvetica', 24),
            style="Header.TLabel"
        )
        logo_label.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(
            title_frame,
            text="Personal Management Tool",
            style="Header.TLabel"
        ).pack(side=tk.LEFT, padx=10)

        # Theme toggle using ttk instead of customtkinter
        self.theme_var = tk.BooleanVar(value=True)
        theme_toggle = ttk.Checkbutton(
            header,
            text="Dark Mode",
            variable=self.theme_var,
            command=self.toggle_theme,
            style="Nav.TCheckbutton"
        )
        theme_toggle.pack(side=tk.RIGHT, padx=20)

    def create_navigation(self):
        nav_frame = ttk.Frame(self.root, style="Nav.TFrame")
        nav_frame.pack(fill=tk.X, pady=0)

        buttons = [
            ("Tasks", "📋", self.show_tasks),
            ("Goals", "🎯", self.show_goals),
            ("Routines", "⏰", self.show_routines),
            ("Recovery", "🌿", self.show_recovery),
            ("Analytics", "📊", self.show_analytics)
        ]

        for text, icon, command in buttons:
            btn = ttk.Button(
                nav_frame,
                text=f"{icon} {text}",
                command=command,
                style="Nav.TButton"
            )
            btn.pack(side=tk.LEFT, padx=5, pady=5)

    def create_main_content(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Welcome message
        welcome_frame = ttk.Frame(self.main_frame)
        welcome_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        # Welcome header
        welcome_header = ttk.Label(
            welcome_frame,
            text="Welcome to Personal Management Tool",
            font=('Helvetica', 24),
            wraplength=800
        )
        welcome_header.pack(pady=20)

        # Welcome description
        welcome_desc = ttk.Label(
            welcome_frame,
            text="Track your tasks, goals, routines, and recovery all in one place.",
            font=('Helvetica', 12),
            wraplength=600
        )
        welcome_desc.pack(pady=10)

    def toggle_theme(self):
        if self.theme_var.get():
            sv_ttk.set_theme("dark")
        else:
            sv_ttk.set_theme("light")

    def init_database(self):
        self.conn = sqlite3.connect('personal_management.db')
        self.cursor = self.conn.cursor()
        self.create_tables()


    def create_tables(self):
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                priority TEXT,
                due_date TEXT,
                completed BOOLEAN DEFAULT 0
            )
        ''')
        # First, create a backup of tasks table if it exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks_backup AS
            SELECT * FROM tasks WHERE 1=0
        ''')
        
        # Copy existing data if the table exists
        try:
            self.cursor.execute('INSERT INTO tasks_backup SELECT * FROM tasks')
            self.cursor.execute('DROP TABLE tasks')
        except sqlite3.OperationalError:
            pass  # Table doesn't exist yet, which is fine
        
        # Create new tasks table with updated schema
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                priority TEXT,
                due_date TEXT,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Restore data from backup if it exists
        try:
            self.cursor.execute('''
                INSERT INTO tasks (id, title, description, category, priority, due_date)
                SELECT id, title, description, category, priority, due_date
                FROM tasks_backup
            ''')
            self.cursor.execute('DROP TABLE tasks_backup')
        except sqlite3.OperationalError:
            pass  # No backup table exists, which is fine for new installations
        
        # Goals table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                target_date TEXT,
                progress REAL DEFAULT 0
            )
        ''')
        
        self.conn.commit()

    def show_tasks(self):
        from task_manager import TaskManager
        self.clear_main_frame()
        TaskManager(self.main_frame, self.conn)

    def show_goals(self):
        from goal_tracker import GoalTracker
        self.clear_main_frame()
        GoalTracker(self.main_frame, self.conn)

    def show_routines(self):
        from routine_scheduler import RoutineScheduler
        self.clear_main_frame()
        RoutineScheduler(self.main_frame, self.conn)

    def show_recovery(self):
        from recovery_tracker import RecoveryTracker
        self.clear_main_frame()
        RecoveryTracker(self.main_frame, self.conn)

    def show_analytics(self):
        from analytics import Analytics
        self.clear_main_frame()
        Analytics(self.main_frame, self.conn)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernApp()
    app.run()