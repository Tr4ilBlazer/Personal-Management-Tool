import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import sqlite3

class TaskManager:
    def __init__(self, parent, conn):
        self.parent = parent
        self.conn = conn
        self.cursor = conn.cursor()
        
        self.setup_ui()
        self.load_tasks()

    def setup_ui(self):
        # Task list frame
        list_frame = ttk.Frame(self.parent)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Create task button
        add_btn = ttk.Button(
            list_frame,
            text="Add Task",
            command=self.show_add_task_dialog
        )
        add_btn.pack(pady=10)
        
        # Task list
        columns = ('id', 'title', 'category', 'priority', 'due_date', 'status')
        self.task_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Configure columns
        self.task_tree.heading('id', text='ID')
        self.task_tree.heading('title', text='Title')
        self.task_tree.heading('category', text='Category')
        self.task_tree.heading('priority', text='Priority')
        self.task_tree.heading('due_date', text='Due Date')
        self.task_tree.heading('status', text='Status')
        
        # Hide ID column
        self.task_tree.column('id', width=0, stretch=False)
        
        self.task_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_tree.configure(yscrollcommand=scrollbar.set)

        # Bind right-click event
        self.task_tree.bind("<Button-3>", self.show_context_menu)
        
        # Create context menu
        self.context_menu = tk.Menu(self.parent, tearoff=0)
        self.context_menu.add_command(label="Mark Complete", command=lambda: self.update_task_status("completed"))
        self.context_menu.add_command(label="Mark Abandoned", command=lambda: self.update_task_status("abandoned"))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Edit Task", command=self.edit_task)
        self.context_menu.add_command(label="Delete Task", command=self.delete_task)

    def show_context_menu(self, event):
        # Get the item under cursor
        item = self.task_tree.identify_row(event.y)
        if item:
            # Select the item
            self.task_tree.selection_set(item)
            # Show context menu
            self.context_menu.post(event.x_root, event.y_root)

    def update_task_status(self, status):
        selected_item = self.task_tree.selection()
        if not selected_item:
            return
        
        task_id = self.task_tree.item(selected_item[0])['values'][0]
        
        self.cursor.execute('''
            UPDATE tasks 
            SET status = ?
            WHERE id = ?
        ''', (status, task_id))
        
        self.conn.commit()
        self.load_tasks()

    def edit_task(self):
        selected_item = self.task_tree.selection()
        if not selected_item:
            return
            
        task_id = self.task_tree.item(selected_item[0])['values'][0]
        
        # Fetch task details
        self.cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        task = self.cursor.fetchone()
        
        self.show_edit_task_dialog(task)

    def show_edit_task_dialog(self, task):
        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Task")
        dialog.geometry("400x500")
        
        # Task details entry fields
        ttk.Label(dialog, text="Title:").pack(pady=5)
        title_entry = ttk.Entry(dialog)
        title_entry.insert(0, task[1])
        title_entry.pack(fill=tk.X, padx=20)
        
        ttk.Label(dialog, text="Description:").pack(pady=5)
        desc_entry = ttk.Entry(dialog)
        desc_entry.insert(0, task[2])
        desc_entry.pack(fill=tk.X, padx=20)
        
        ttk.Label(dialog, text="Category:").pack(pady=5)
        category_combo = ttk.Combobox(dialog, values=['Work', 'Personal', 'Study'])
        category_combo.set(task[3])
        category_combo.pack(fill=tk.X, padx=20)
        
        ttk.Label(dialog, text="Priority:").pack(pady=5)
        priority_combo = ttk.Combobox(dialog, values=['High', 'Medium', 'Low'])
        priority_combo.set(task[4])
        priority_combo.pack(fill=tk.X, padx=20)
        
        ttk.Label(dialog, text="Due Date:").pack(pady=5)
        due_date = DateEntry(dialog)
        due_date.set_date(datetime.strptime(task[5], '%Y-%m-%d'))
        due_date.pack(fill=tk.X, padx=20)
        
        def save_changes():
            self.cursor.execute('''
                UPDATE tasks 
                SET title = ?, description = ?, category = ?, 
                    priority = ?, due_date = ?
                WHERE id = ?
            ''', (
                title_entry.get(),
                desc_entry.get(),
                category_combo.get(),
                priority_combo.get(),
                due_date.get(),
                task[0]
            ))
            self.conn.commit()
            self.load_tasks()
            dialog.destroy()
        
        ttk.Button(dialog, text="Save Changes", command=save_changes).pack(pady=20)

    def delete_task(self):
        selected_item = self.task_tree.selection()
        if not selected_item:
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
            task_id = self.task_tree.item(selected_item[0])['values'][0]
            self.cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            self.conn.commit()
            self.load_tasks()

    def show_add_task_dialog(self):
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add New Task")
        dialog.geometry("400x500")
        
        # Task details entry fields
        ttk.Label(dialog, text="Title:").pack(pady=5)
        title_entry = ttk.Entry(dialog)
        title_entry.pack(fill=tk.X, padx=20)
        
        ttk.Label(dialog, text="Description:").pack(pady=5)
        desc_entry = ttk.Entry(dialog)
        desc_entry.pack(fill=tk.X, padx=20)
        
        ttk.Label(dialog, text="Category:").pack(pady=5)
        category_combo = ttk.Combobox(dialog, values=['Work', 'Personal', 'Study'])
        category_combo.pack(fill=tk.X, padx=20)
        
        ttk.Label(dialog, text="Priority:").pack(pady=5)
        priority_combo = ttk.Combobox(dialog, values=['High', 'Medium', 'Low'])
        priority_combo.pack(fill=tk.X, padx=20)
        
        ttk.Label(dialog, text="Due Date:").pack(pady=5)
        due_date = DateEntry(dialog)
        due_date.pack(fill=tk.X, padx=20)
        
        def save_task():
            self.cursor.execute('''
                INSERT INTO tasks (title, description, category, priority, due_date, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                title_entry.get(),
                desc_entry.get(),
                category_combo.get(),
                priority_combo.get(),
                due_date.get(),
                'pending'
            ))
            self.conn.commit()
            self.load_tasks()
            dialog.destroy()
        
        ttk.Button(dialog, text="Save", command=save_task).pack(pady=20)

    def load_tasks(self):
        # Clear existing items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Load tasks from database
        self.cursor.execute('SELECT * FROM tasks ORDER BY due_date')
        for task in self.cursor.fetchall():
            self.task_tree.insert('', tk.END, values=(
                task[0],  # id
                task[1],  # title
                task[3],  # category
                task[4],  # priority
                task[5],  # due_date
                task[6] if task[6] else 'pending'  # status
            ))