import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime
import seaborn as sns

class GoalTracker:
    def __init__(self, parent, conn):
        self.parent = parent
        self.conn = conn
        self.cursor = conn.cursor()
        self.date_format = '%Y-%m-%d'
        
        # Set up the style for matplotlib
        plt.style.use('dark_background')
        self.setup_ui()
        self.load_goals()

    def setup_ui(self):
        # Main container with modern styling
        self.container = ctk.CTkFrame(self.parent)
        self.container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header
        header_frame = ctk.CTkFrame(self.container)
        header_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        ctk.CTkLabel(
            header_frame,
            text="Goal Tracking Dashboard",
            font=('Helvetica', 20, 'bold')
        ).pack(side=tk.LEFT, pady=10, padx=10)

        # Add goal button with modern styling
        add_btn = ctk.CTkButton(
            header_frame,
            text="+ New Goal",
            command=self.show_add_goal_dialog,
            fg_color="#4CAF50",
            hover_color="#45a049",
            height=35
        )
        add_btn.pack(side=tk.RIGHT, pady=10, padx=10)

        # Split container
        self.split_container = ctk.CTkFrame(self.container)
        self.split_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left frame for goals list
        left_frame = ctk.CTkFrame(self.split_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Goals list with modern styling
        columns = ('title', 'target_date', 'progress')
        self.goal_tree = ttk.Treeview(left_frame, columns=columns, show='headings', style="Custom.Treeview")
        
        # Configure treeview columns
        self.goal_tree.heading('title', text='Goal')
        self.goal_tree.heading('target_date', text='Target Date')
        self.goal_tree.heading('progress', text='Progress')
        
        self.goal_tree.column('title', width=200)
        self.goal_tree.column('target_date', width=100)
        self.goal_tree.column('progress', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.goal_tree.yview)
        self.goal_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the treeview and scrollbar
        self.goal_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.goal_tree.bind('<<TreeviewSelect>>', self.update_visualizations)

        # Right frame for visualizations
        right_frame = ctk.CTkFrame(self.split_container)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Create tabs for different visualizations
        self.viz_notebook = ttk.Notebook(right_frame)
        self.viz_notebook.pack(fill=tk.BOTH, expand=True)

        # Progress Chart Tab
        self.progress_frame = ctk.CTkFrame(self.viz_notebook)
        self.viz_notebook.add(self.progress_frame, text='Progress')

        # Create modern progress chart
        self.fig_progress, self.ax_progress = plt.subplots(figsize=(8, 6))
        self.canvas_progress = FigureCanvasTkAgg(self.fig_progress, master=self.progress_frame)
        self.canvas_progress.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Timeline Chart Tab
        self.timeline_frame = ctk.CTkFrame(self.viz_notebook)
        self.viz_notebook.add(self.timeline_frame, text='Timeline')

        self.fig_timeline, self.ax_timeline = plt.subplots(figsize=(8, 6))
        self.canvas_timeline = FigureCanvasTkAgg(self.fig_timeline, master=self.timeline_frame)
        self.canvas_timeline.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add right-click menu binding
        self.goal_tree.bind("<Button-3>", self.show_context_menu)
        
        # Create context menu
        self.context_menu = tk.Menu(self.parent, tearoff=0)
        self.context_menu.add_command(label="Update Progress", command=self.show_update_progress_dialog)
        self.context_menu.add_command(label="Edit Goal", command=self.show_edit_goal_dialog)
        self.context_menu.add_command(label="Delete Goal", command=self.delete_goal)
        
    def show_add_goal_dialog(self):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Add New Goal")
        dialog.geometry("500x650")
        
        # Make dialog modal
        dialog.transient(self.parent)
        dialog.grab_set()

        # Content frame
        content = ctk.CTkFrame(dialog)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(content, text="Goal Title:", font=('Helvetica', 12, 'bold')).pack(pady=(0, 5))
        title_entry = ctk.CTkEntry(content, width=300)
        title_entry.pack(pady=(0, 15))

        # Description
        ctk.CTkLabel(content, text="Description:", font=('Helvetica', 12, 'bold')).pack(pady=(0, 5))
        desc_text = ctk.CTkTextbox(content, height=100)
        desc_text.pack(fill=tk.X, pady=(0, 15))

        # Target Date
        ctk.CTkLabel(content, text="Target Date:", font=('Helvetica', 12, 'bold')).pack(pady=(0, 5))
        date_frame = ctk.CTkFrame(content)
        date_frame.pack(fill=tk.X, pady=(0, 15))
        target_date = DateEntry(date_frame, width=30, background='darkblue', foreground='white')
        target_date.pack()

        # Initial Progress
        ctk.CTkLabel(content, text="Initial Progress:", font=('Helvetica', 12, 'bold')).pack(pady=(0, 5))
        
        # Changed from StringVar to DoubleVar
        progress_var = tk.DoubleVar(value=0.0)
        progress_slider = ctk.CTkSlider(
            content,
            from_=0,
            to=100,
            number_of_steps=100,
            variable=progress_var
        )
        progress_slider.pack(fill=tk.X, pady=(0, 5))
        
        # Progress label (convert to integer for display)
        progress_label = ctk.CTkLabel(
            content,
            text="0%",  # Initial text
        )
        progress_label.pack(pady=(0, 20))

        # Update label when slider moves
        def update_progress_label(*args):
            progress_label.configure(text=f"{int(progress_var.get())}%")
        
        progress_var.trace_add("write", update_progress_label)

        def save_goal():
            if not title_entry.get():
                tk.messagebox.showwarning("Input Required", "Please enter a goal title")
                return
                
            # Format the date properly before saving
            selected_date = datetime.strptime(target_date.get(), '%m/%d/%y')
            formatted_date = selected_date.strftime(self.date_format)
                
            self.cursor.execute('''
                INSERT INTO goals (title, description, target_date, progress)
                VALUES (?, ?, ?, ?)
            ''', (
                title_entry.get(),
                desc_text.get("1.0", tk.END),
                formatted_date,
                float(progress_var.get())
            ))
            self.conn.commit()
            self.load_goals()
            dialog.destroy()

        def cancel():
            dialog.destroy()

        # Button frame
        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(fill=tk.X, pady=(0, 10), padx=10)

        # Cancel button
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=cancel,
            fg_color="#ff4444",
            hover_color="#cc0000",
            width=120,
            height=35
        ).pack(side=tk.LEFT, padx=5)

        # Save button
        ctk.CTkButton(
            button_frame,
            text="✓ Save Goal",
            command=save_goal,
            fg_color="#4CAF50",
            hover_color="#45a049",
            width=120,
            height=35
        ).pack(side=tk.RIGHT, padx=5)

        # Set focus to title entry
        title_entry.focus_set()

        # Bind Enter key to save
        dialog.bind('<Return>', lambda e: save_goal())
        dialog.bind('<Escape>', lambda e: cancel())

    def load_goals(self):
        for item in self.goal_tree.get_children():
            self.goal_tree.delete(item)

        self.cursor.execute('SELECT * FROM goals ORDER BY target_date')
        for goal in self.cursor.fetchall():
            self.goal_tree.insert('', tk.END, values=(
                goal[1],  # title
                goal[3],  # target_date
                f"{goal[4]}%"  # progress
            ))
        
        self.update_visualizations()
    
    def show_context_menu(self, event):
        item = self.goal_tree.identify_row(event.y)
        if item:
            self.goal_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)


    def update_visualizations(self, event=None):
        # Clear previous plots
        self.ax_progress.clear()
        self.ax_timeline.clear()

        # Get all goals data
        self.cursor.execute('SELECT title, progress, target_date FROM goals ORDER BY target_date')
        goals_data = self.cursor.fetchall()

        if goals_data:
            titles = [goal[0] for goal in goals_data]
            progress = [goal[1] for goal in goals_data]
            
            # Handle different date formats
            target_dates = []
            for goal in goals_data:
                try:
                    # Try parsing as YYYY-MM-DD first
                    date = datetime.strptime(goal[2], self.date_format)
                except ValueError:
                    try:
                        # Try parsing as MM/DD/YY
                        date = datetime.strptime(goal[2], '%m/%d/%y')
                    except ValueError:
                        # If both fail, use today's date as fallback
                        date = datetime.now()
                target_dates.append(date)

            # Rest of the visualization code remains the same
            colors = plt.cm.viridis(np.linspace(0, 1, len(titles)))
            
            # Progress Chart
            bars = self.ax_progress.barh(titles, progress, color=colors)
            for bar in bars:
                width = bar.get_width()
                self.ax_progress.text(
                    width, 
                    bar.get_y() + bar.get_height()/2,
                    f'{int(width)}%',
                    va='center',
                    ha='left' if width < 50 else 'right',
                    color='white'
                )

            self.ax_progress.set_xlabel('Progress (%)')
            self.ax_progress.set_title('Goal Progress Overview')
            self.ax_progress.grid(True, alpha=0.3)
            
            # Timeline Chart
            y_positions = range(len(titles))
            self.ax_timeline.scatter(target_dates, y_positions, c=colors, s=100)
            self.ax_timeline.set_yticks(y_positions)
            self.ax_timeline.set_yticklabels(titles)
            self.ax_timeline.set_xlabel('Target Date')
            self.ax_timeline.set_title('Goal Timeline')
            self.ax_timeline.grid(True, alpha=0.3)

            # Rotate date labels for better readability
            plt.setp(self.ax_timeline.get_xticklabels(), rotation=45, ha='right')

        # Adjust layout and display
        self.fig_progress.tight_layout()
        self.fig_timeline.tight_layout()
        self.canvas_progress.draw()
        self.canvas_timeline.draw()
    
    
    def show_update_progress_dialog(self):
        selected_item = self.goal_tree.selection()
        if not selected_item:
            return
            
        goal_id = self.get_selected_goal_id()
        current_progress = self.get_goal_progress(goal_id)
        
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Update Progress")
        dialog.geometry("400x250")
        
        # Make dialog modal
        dialog.transient(self.parent)
        dialog.grab_set()
        
        content = ctk.CTkFrame(dialog)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            content,
            text="Update Progress:",
            font=('Helvetica', 12, 'bold')
        ).pack(pady=(0, 10))
        
        progress_var = tk.DoubleVar(value=current_progress)
        progress_slider = ctk.CTkSlider(
            content,
            from_=0,
            to=100,
            number_of_steps=100,
            variable=progress_var
        )
        progress_slider.pack(fill=tk.X, pady=(0, 5))
        
        progress_label = ctk.CTkLabel(
            content,
            text=f"{int(current_progress)}%"
        )
        progress_label.pack(pady=(0, 20))
        
        def update_progress_label(*args):
            progress_label.configure(text=f"{int(progress_var.get())}%")
        
        progress_var.trace_add("write", update_progress_label)
        
        def save_progress():
            self.cursor.execute('''
                UPDATE goals 
                SET progress = ?
                WHERE id = ?
            ''', (float(progress_var.get()), goal_id))
            self.conn.commit()
            self.load_goals()
            dialog.destroy()
        
        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ctk.CTkButton(
            button_frame,
            text="Save Progress",
            command=save_progress,
            fg_color="#4CAF50",
            hover_color="#45a049"
        ).pack(expand=True)

    def show_edit_goal_dialog(self):
        selected_item = self.goal_tree.selection()
        if not selected_item:
            return
            
        goal_id = self.get_selected_goal_id()
        goal_data = self.get_goal_data(goal_id)
        
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Edit Goal")
        dialog.geometry("500x650")
        
        # Make dialog modal
        dialog.transient(self.parent)
        dialog.grab_set()
        
        content = ctk.CTkFrame(dialog)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(content, text="Goal Title:", font=('Helvetica', 12, 'bold')).pack(pady=(0, 5))
        title_entry = ctk.CTkEntry(content, width=300)
        title_entry.insert(0, goal_data['title'])
        title_entry.pack(pady=(0, 15))
        
        # Description
        ctk.CTkLabel(content, text="Description:", font=('Helvetica', 12, 'bold')).pack(pady=(0, 5))
        desc_text = ctk.CTkTextbox(content, height=100)
        desc_text.insert("1.0", goal_data['description'])
        desc_text.pack(fill=tk.X, pady=(0, 15))
        
        # Target Date
        ctk.CTkLabel(content, text="Target Date:", font=('Helvetica', 12, 'bold')).pack(pady=(0, 5))
        date_frame = ctk.CTkFrame(content)
        date_frame.pack(fill=tk.X, pady=(0, 15))
        target_date = DateEntry(date_frame, width=30, background='darkblue', foreground='white')
        target_date.set_date(datetime.strptime(goal_data['target_date'], '%Y-%m-%d'))
        target_date.pack()
        
        def save_changes():
            # Format the date properly before saving
            selected_date = datetime.strptime(target_date.get(), '%m/%d/%y')
            formatted_date = selected_date.strftime(self.date_format)
            
            self.cursor.execute('''
                UPDATE goals 
                SET title = ?, description = ?, target_date = ?
                WHERE id = ?
            ''', (
                title_entry.get(),
                desc_text.get("1.0", tk.END),
                formatted_date,
                goal_id
            ))
            self.conn.commit()
            self.load_goals()
            dialog.destroy()
        
        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Save Changes button
        ctk.CTkButton(
            button_frame,
            text="Save Changes",
            command=save_changes,
            fg_color="#4CAF50",
            hover_color="#45a049"
        ).pack(expand=True)

    def delete_goal(self):
        selected_item = self.goal_tree.selection()
        if not selected_item:
            return
            
        goal_id = self.get_selected_goal_id()
        if tk.messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this goal?"):
            self.cursor.execute('DELETE FROM goals WHERE id = ?', (goal_id,))
            self.conn.commit()
            self.load_goals()

    def get_selected_goal_id(self):
        selected_item = self.goal_tree.selection()[0]
        self.cursor.execute('SELECT id FROM goals WHERE title = ?', 
                        (self.goal_tree.item(selected_item)['values'][0],))
        return self.cursor.fetchone()[0]

    def get_goal_data(self, goal_id):
        self.cursor.execute('SELECT * FROM goals WHERE id = ?', (goal_id,))
        goal = self.cursor.fetchone()
        return {
            'title': goal[1],
            'description': goal[2],
            'target_date': goal[3],
            'progress': goal[4]
        }

    def get_goal_progress(self, goal_id):
        self.cursor.execute('SELECT progress FROM goals WHERE id = ?', (goal_id,))
        return self.cursor.fetchone()[0]

    def load_goals(self):
        # Clear existing items
        for item in self.goal_tree.get_children():
            self.goal_tree.delete(item)
        
        self.cursor.execute('SELECT * FROM goals ORDER BY target_date')
        for goal in self.cursor.fetchall():
            self.goal_tree.insert('', tk.END, values=(
                goal[1],  # title
                goal[3],  # target_date
                f"{goal[4]}%"  # progress
            ))
        
        self.update_visualizations()