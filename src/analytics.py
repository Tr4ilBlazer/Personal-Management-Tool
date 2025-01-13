import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np

class Analytics:
    def __init__(self, parent, conn):
        self.parent = parent
        self.conn = conn
        self.cursor = conn.cursor()
        self.setup_style()
        self.setup_ui()
        self.load_analytics()

    def setup_style(self):
        # Modern color palette
        self.colors = ['#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0']
        plt.style.use('ggplot')  # Using built-in modern style

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs with modern styling
        self.task_frame = ttk.Frame(self.notebook)
        self.goals_frame = ttk.Frame(self.notebook)
        self.recovery_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.task_frame, text='📊 Task Analytics')
        self.notebook.add(self.goals_frame, text='🎯 Goal Progress')
        self.notebook.add(self.recovery_frame, text='📈 Recovery Insights')

        self.setup_task_analytics()
        self.setup_goals_analytics()
        self.setup_recovery_analytics()

    def setup_task_analytics(self):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), facecolor='none')
        fig.patch.set_facecolor('none')
        canvas = FigureCanvasTkAgg(fig, self.task_frame)
        
        # Task completion donut chart
        self.cursor.execute('''
            SELECT category, COUNT(*) as total,
            SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed
            FROM tasks GROUP BY category
        ''')
        data = self.cursor.fetchall()

        if data:
            categories = [row[0] for row in data]
            completed = [row[2] for row in data]
            total = [row[1] for row in data]
            
            # Create donut chart
            wedges, texts, autotexts = ax1.pie(
                completed, 
                labels=categories,
                colors=self.colors,
                autopct='%1.1f%%',
                wedgeprops=dict(width=0.5)
            )
            ax1.set_title('Task Completion by Category', pad=20, color='#333333')

            # Create stacked bar chart
            df = pd.DataFrame({
                'Category': categories,
                'Completed': completed,
                'Remaining': np.array(total) - np.array(completed)
            })
            
            df.plot(
                kind='bar',
                stacked=True,
                ax=ax2,
                color=[self.colors[0], '#E0E0E0']
            )
            ax2.set_title('Task Status Overview', color='#333333')
            ax2.legend(loc='upper right')
            ax2.set_xlabel('')
            ax2.tick_params(colors='#333333')
            
        fig.tight_layout()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def setup_goals_analytics(self):
        fig = plt.figure(figsize=(12, 5), facecolor='none')
        fig.patch.set_facecolor('none')
        canvas = FigureCanvasTkAgg(fig, self.goals_frame)

        self.cursor.execute('SELECT title, progress FROM goals')
        data = self.cursor.fetchall()

        if data:
            titles = [row[0] for row in data]
            progress = [row[1] for row in data]
            
            ax = fig.add_subplot(111)
            bars = ax.barh(titles, progress, height=0.5)
            
            # Add progress percentage inside bars
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(
                    min(width + 2, 95),
                    bar.get_y() + bar.get_height()/2,
                    f'{progress[i]}%',
                    va='center',
                    color='white' if width > 30 else '#333333'
                )
                
            # Style the chart
            ax.set_xlim(0, 100)
            ax.set_title('Goal Progress Overview', pad=20, color='#333333')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.tick_params(colors='#333333')
            
            # Add gradient colors
            for bar, color in zip(bars, self.colors):
                bar.set_color(color)
                
        fig.tight_layout()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def setup_recovery_analytics(self):
        fig = plt.figure(figsize=(12, 6), facecolor='none')
        fig.patch.set_facecolor('none')
        canvas = FigureCanvasTkAgg(fig, self.recovery_frame)
        
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
            
            # Create area chart
            ax = fig.add_subplot(111)
            ax.fill_between(dates, energy, alpha=0.3, color=self.colors[0], label='Energy Level')
            ax.plot(dates, energy, color=self.colors[0], linewidth=2, marker='o')
            
            # Add sleep duration as circles
            ax2 = ax.twinx()
            ax2.scatter(dates, sleep, color=self.colors[1], s=100, label='Sleep Hours', alpha=0.7)
            ax2.plot(dates, sleep, color=self.colors[1], alpha=0.3, linestyle='--')
            
            # Style the chart
            ax.set_title('Energy Levels & Sleep Duration', pad=20, color='#333333')
            ax.spines['top'].set_visible(False)
            ax.tick_params(axis='x', rotation=45, colors='#333333')
            ax2.tick_params(colors='#333333')
            
            # Add legends
            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
            
        fig.tight_layout()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def load_analytics(self):
        # Create modern stats cards using ttk frames
        stats_frame = ttk.Frame(self.parent)
        stats_frame.pack(fill=tk.X, pady=10, padx=10)

        self.cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed
            FROM tasks
        ''')
        task_stats = self.cursor.fetchone()
        completion_rate = (task_stats[1] / task_stats[0] * 100) if task_stats[0] > 0 else 0
        
        # Create modern stat cards
        cards_data = [
            ("Task Completion Rate", f"{completion_rate:.1f}%"),
            ("Total Tasks", str(task_stats[0])),
            ("Completed Tasks", str(task_stats[1]))
        ]
        
        for title, value in cards_data:
            card = ttk.Frame(stats_frame, style='Card.TFrame', padding=10)
            card.pack(side=tk.LEFT, padx=5, expand=True)
            
            ttk.Label(
                card,
                text=title,
                font=('Helvetica', 10),
            ).pack()
            
            ttk.Label(
                card,
                text=value,
                font=('Helvetica', 20, 'bold'),
            ).pack(pady=5)