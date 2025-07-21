import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import defaultdict
import threading
import json
import zipfile
import shutil
from datetime import datetime
import webbrowser
import tempfile
import sv_ttk
import platform
import sys
import re
import time
import concurrent.futures
import gc
from functools import wraps
from resource_path import resource_path

class ModConflictChecker(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("RDR2 LML Mod Conflict Checker")
        self.geometry("1400x900")
        self.minsize(1000, 700)
        
        self.path_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="All")
        self.conflicts = {}
        self.excluded_files = set()
        self.is_scanning = False
        self.dark_mode = True
        self.mod_colors = {}
        self.backup_folder = None
        self.file_type_toggles = {}
        self.toggle_visible = tk.BooleanVar(value=False)
        self.current_tab = "conflicts"
        
        self.update_debounce_timer = None
        
        self.center_window()
        
        sv_ttk.set_theme("dark" if self.dark_mode else "light")
        self.set_dark_title_bar()
        
        self.create_header()
        self.create_controls()
        self.create_notebook()
        self.create_summary_panel()
        self.create_donation_button()
        
        self.bind_context_menus()
        
        self.optimize_memory()
        
        
    def resource_path(relative_path):
        try:
            
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)
        
    def create_donation_button(self):
        """Add a Ko-fi donation button to the bottom right of the application"""
     
        status_frame = ttk.Frame(self)
        status_frame.pack(side="bottom", fill="x", padx=10, pady=5)
        
     
        kofi_button = tk.Button(
            status_frame,
            text="Support me on Ko-fi",
            bg="#72a4f2",  
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            relief="flat",
            padx=10,
            pady=5,
            command=lambda: webbrowser.open("https://ko-fi.com/W7W41IBL6D")
        )
        kofi_button.pack(side="right", padx=5)
        
   
        ttk.Label(
            status_frame,
            text="Find this tool helpful?",
            font=("Segoe UI", 8)
        ).pack(side="right", padx=(0, 5))
        
    
        self.kofi_button = kofi_button
        
   
        self.create_kofi_tooltip(kofi_button, "Support the development of this app with a donation")

    def create_kofi_tooltip(self, widget, text):
        """Create a tooltip for the Ko-fi button"""
        def enter(event):
            x = widget.winfo_rootx() + widget.winfo_width() // 2
            y = widget.winfo_rooty() - 5
            
 
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{x}+{y}")
            

            tooltip_frame = ttk.Frame(tooltip, relief="solid", borderwidth=1)
            tooltip_frame.pack()
            
            label = ttk.Label(
                tooltip_frame, 
                text=text,
                background="#ffffe0", 
                font=("Segoe UI", 8),
                padding=(5, 3)
            )
            label.pack()
            

            widget._tooltip = tooltip
            
        def leave(event):
            if hasattr(widget, "_tooltip"):
                widget._tooltip.destroy()
                delattr(widget, "_tooltip")
                
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    
    def optimize_memory(self):
        gc.collect()
        self.after(60000, self.optimize_memory)
        
    def debounce(self, wait_time):
        def decorator(func):
            @wraps(func)
            def debounced(*args, **kwargs):
                if hasattr(self, f"_debounce_timer_{func.__name__}"):
                    timer = getattr(self, f"_debounce_timer_{func.__name__}")
                    if timer:
                        self.after_cancel(timer)
                
                timer_id = self.after(wait_time, lambda: func(*args, **kwargs))
                setattr(self, f"_debounce_timer_{func.__name__}", timer_id)
            return debounced
        return decorator
        
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def set_dark_title_bar(self):
        if platform.system() == 'Windows':
            try:
                from ctypes import windll, byref, sizeof, c_int
                
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                set_window_attribute = windll.dwmapi.DwmSetWindowAttribute
                
                hwnd = windll.user32.GetParent(self.winfo_id())
                
                value = c_int(1 if self.dark_mode else 0)
                set_window_attribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, byref(value), sizeof(value))
                
            except Exception as e:
                print(f"Failed to set dark title bar: {e}")
                
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        sv_ttk.set_theme("dark" if self.dark_mode else "light")
        self.set_dark_title_bar()
        
        self.theme_btn.config(text="🌙" if self.dark_mode else "☀️")
        
        if hasattr(self, 'kofi_button'):
            if self.dark_mode:
                self.kofi_button.config(bg="#5a94e6")  
            else:
                self.kofi_button.config(bg="#72a4f2")  

               
        if hasattr(self, 'gxt2_warning'):
            if self.dark_mode:
                self.gxt2_warning.configure(background='#3a3321')
                for widget in self.gxt2_warning.winfo_children():
                    widget.configure(background='#3a3321')
                    if isinstance(widget, tk.Label) and widget.cget("text") != "⚠️":
                        widget.configure(foreground='#ffd700')
                    else:
                        widget.configure(foreground='#ffffff')
            else:
                self.gxt2_warning.configure(background='#fff3cd')
                for widget in self.gxt2_warning.winfo_children():
                    widget.configure(background='#fff3cd')
                    if isinstance(widget, tk.Label) and widget.cget("text") != "⚠️":
                        widget.configure(foreground='#856404')
                    else:
                        widget.configure(foreground='#000000')
        
        self.update_tree()
        self.update_excluded_tree()
        self.apply_tree_tags()
        
    def create_header(self):
        header_frame = ttk.Frame(self, padding=30)
        header_frame.pack(fill='x')
        
        title_row = ttk.Frame(header_frame)
        title_row.pack(fill='x')
        
        title_label = ttk.Label(title_row, 
                               text="RDR2 LML Mod Conflict Checker",
                               font=('Segoe UI', 18, 'bold'))
        title_label.pack(side='left')
        
        self.theme_btn = ttk.Button(title_row,
                                  text="🌙" if self.dark_mode else "☀️",
                                  width=3)
        self.theme_btn.config(command=self.toggle_theme)
        self.theme_btn.pack(side='right')
        
        subtitle_label = ttk.Label(header_frame,
                                 text="Detect file conflicts between your installed mods",
                                 font=('Segoe UI', 10))
        subtitle_label.pack(pady=(5, 0))
        
    def create_controls(self):
        controls_frame = ttk.Frame(self, padding=20)
        controls_frame.pack(fill='x', padx=20, pady=10)
        
        path_row = ttk.Frame(controls_frame)
        path_row.pack(fill='x', pady=(0, 15))
        
        ttk.Label(path_row, text="LML Folder:").pack(side='left')
        
        path_entry_frame = ttk.Frame(path_row)
        path_entry_frame.pack(side='left', fill='x', expand=True, padx=(10, 0))
        
        self.path_entry = ttk.Entry(path_entry_frame, 
                                textvariable=self.path_var,
                                font=('Segoe UI', 10))
        self.path_entry.pack(side='left', fill='x', expand=True)
        
        browse_button = ttk.Button(path_row, 
                                text="Browse",
                                style='Accent.TButton')
        browse_button.config(command=lambda: self.browse_folder())
        browse_button.pack(side='right', padx=(10, 0))
        
        search_row = ttk.Frame(controls_frame)
        search_row.pack(fill='x', pady=(0, 15))
        
        search_frame = ttk.Frame(search_row)
        search_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(search_frame, text="Search:").pack(side='left')
        search_entry = ttk.Entry(search_frame, 
                            textvariable=self.search_var,
                            font=('Segoe UI', 10))
        search_entry.pack(side='left', fill='x', expand=True, padx=(10, 0))
        search_entry.bind("<KeyRelease>", lambda e: self.debounced_update_tree())
        
        action_row = ttk.Frame(controls_frame)
        action_row.pack(fill='x')
        
        left_buttons = ttk.Frame(action_row)
        left_buttons.pack(side='left')
        
        self.scan_btn = ttk.Button(left_buttons,
                                text="Scan for Conflicts",
                                style='Accent.TButton')
        self.scan_btn.config(command=lambda: self.scan_conflicts_threaded())
        self.scan_btn.pack(side='left')
        
        self.backup_btn = ttk.Button(left_buttons,
                                text="Create Backup")
        self.backup_btn.config(command=lambda: self.create_backup())
        self.backup_btn.pack(side='left', padx=(10, 0))
        
        self.restore_btn = ttk.Button(left_buttons,
                                    text="Restore Backup",
                                    state='disabled')
        self.restore_btn.config(command=lambda: self.restore_backup())
        self.restore_btn.pack(side='left', padx=(10, 0))
        
        right_buttons = ttk.Frame(action_row)
        right_buttons.pack(side='right')
        
        self.copy_btn = ttk.Button(right_buttons,
                                text="Copy to Clipboard")
        self.copy_btn.config(command=lambda: self.copy_to_clipboard())
        self.copy_btn.pack(side='right')
        
        self.export_json_btn = ttk.Button(right_buttons,
                                        text="Export JSON")
        self.export_json_btn.config(command=lambda: self.export_to_json())
        self.export_json_btn.pack(side='right', padx=(0, 10))
        
        self.export_html_btn = ttk.Button(right_buttons,
                                        text="Export HTML")
        self.export_html_btn.config(command=lambda: self.export_to_html())
        self.export_html_btn.pack(side='right', padx=(0, 10))
        
        self.export_btn = ttk.Button(right_buttons,
                                text="Export TXT")
        self.export_btn.config(command=lambda: self.export_to_txt())
        self.export_btn.pack(side='right', padx=(0, 10))

    
    def create_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        self.conflicts_tab = ttk.Frame(self.notebook)
        self.excluded_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.conflicts_tab, text="Conflicts")
        self.notebook.add(self.excluded_tab, text="Excluded Files")
        
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        self.create_conflicts_tab()
        self.create_excluded_tab()
        
    def on_tab_changed(self, event):
        tab_id = self.notebook.select()
        tab_name = self.notebook.tab(tab_id, "text")
        
        if tab_name == "Conflicts":
            self.current_tab = "conflicts"
        elif tab_name == "Excluded Files":
            self.current_tab = "excluded"
            self.update_excluded_tree()
        
    def create_conflicts_tab(self):
        main_paned = ttk.PanedWindow(self.conflicts_tab, orient='horizontal')
        main_paned.pack(fill='both', expand=True)
        
        left_frame = ttk.Frame(main_paned, padding=10)
        main_paned.add(left_frame, weight=1)
        
        file_types_header = ttk.Frame(left_frame)
        file_types_header.pack(fill='x', pady=(0, 10))
        
        ttk.Label(file_types_header, 
                 text="Conflicts by File Type",
                 font=('Segoe UI', 12, 'bold')).pack(side='left')
        
        self.type_tree = ttk.Treeview(left_frame, height=15)
        self.type_tree.heading("#0", text="File Types")
        self.type_tree.bind("<<TreeviewSelect>>", self.on_type_select)
        
        type_scroll = ttk.Scrollbar(left_frame, orient="vertical", command=self.type_tree.yview)
        self.type_tree.configure(yscrollcommand=type_scroll.set)
        
        self.type_tree.pack(side='left', fill='both', expand=True)
        type_scroll.pack(side='right', fill='y')
        
        right_frame = ttk.Frame(main_paned, padding=10)
        main_paned.add(right_frame, weight=2)
        
        self.gxt2_warning = tk.Frame(right_frame, padx=10, pady=10)
        self.gxt2_warning.pack(fill='x', pady=(0, 10))
        self.gxt2_warning.pack_forget()
        
        if self.dark_mode:
            self.gxt2_warning.configure(background='#3a3321')
        else:
            self.gxt2_warning.configure(background='#fff3cd')
        
        warning_icon = tk.Label(self.gxt2_warning, text="⚠️", font=('Segoe UI', 16))
        warning_icon.pack(side='left', padx=(0, 10))
        
        if self.dark_mode:
            warning_icon.configure(background='#3a3321', foreground='#ffffff')
        else:
            warning_icon.configure(background='#fff3cd', foreground='#000000')
        
        warning_text = tk.Label(
            self.gxt2_warning, 
            text="Warning: GXT2 files typically do not conflict and may result in false positives. Modify only if you understand what you're doing.",
            wraplength=600,
            font=('Segoe UI', 10),
            justify='left'
        )
        warning_text.pack(side='left', fill='x', expand=True)
        
        if self.dark_mode:
            warning_text.configure(background='#3a3321', foreground='#ffd700')
        else:
            warning_text.configure(background='#fff3cd', foreground='#856404')
        
        results_header = ttk.Frame(right_frame)
        results_header.pack(fill='x', pady=(0, 10))
        
        ttk.Label(results_header, 
                 text="Detailed Conflicts",
                 font=('Segoe UI', 12, 'bold')).pack(side='left')
        
        self.toggle_btn = ttk.Button(results_header,
                                   text="Show File Type Filters")
        self.toggle_btn.config(command=self.toggle_file_type_filters)
        self.toggle_btn.pack(side='right', padx=(10, 0))
        
        self.results_count = ttk.Label(results_header, text="0 conflicts found")
        self.results_count.pack(side='right')
        
        self.filter_panel = ttk.Frame(right_frame, padding=5)
        self.filter_panel.pack(fill='x', pady=(0, 10))
        self.filter_panel.pack_forget()
        
        tree_frame = ttk.Frame(right_frame)
        tree_frame.pack(fill='both', expand=True)
        
        columns = ("file", "mods", "count", "severity")
        self.tree = ttk.Treeview(tree_frame, 
                               columns=columns,
                               show="headings")
        
        self.tree.heading("file", text="File Path", command=lambda: self.sort_column("file"))
        self.tree.heading("mods", text="Conflicting Mods", command=lambda: self.sort_column("mods"))
        self.tree.heading("count", text="Count", command=lambda: self.sort_column("count"))
        self.tree.heading("severity", text="Severity", command=lambda: self.sort_column("severity"))
        
        self.tree.column("file", width=300, anchor='w', minwidth=200)
        self.tree.column("mods", width=250, anchor='w', minwidth=150)
        self.tree.column("count", width=80, anchor='center', minwidth=60)
        self.tree.column("severity", width=100, anchor='center', minwidth=80)
        
        v_scrollbar = ttk.Scrollbar(tree_frame, 
                                  orient="vertical",
                                  command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame,
                                  orient="horizontal", 
                                  command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set,
                          xscrollcommand=h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.apply_tree_tags()
        
    def create_excluded_tab(self):
        excluded_frame = ttk.Frame(self.excluded_tab, padding=10)
        excluded_frame.pack(fill='both', expand=True)
        
        header_frame = ttk.Frame(excluded_frame)
        header_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(header_frame, 
                 text="Excluded Files",
                 font=('Segoe UI', 12, 'bold')).pack(side='left')
        
        self.excluded_count = ttk.Label(header_frame, text="0 files excluded")
        self.excluded_count.pack(side='right')
        
        tree_frame = ttk.Frame(excluded_frame)
        tree_frame.pack(fill='both', expand=True)
        
        columns = ("file", "mods", "count", "severity")
        self.excluded_tree = ttk.Treeview(tree_frame, 
                                        columns=columns,
                                        show="headings")
        
        self.excluded_tree.heading("file", text="File Path", command=lambda: self.sort_excluded_column("file"))
        self.excluded_tree.heading("mods", text="Conflicting Mods", command=lambda: self.sort_excluded_column("mods"))
        self.excluded_tree.heading("count", text="Count", command=lambda: self.sort_excluded_column("count"))
        self.excluded_tree.heading("severity", text="Severity", command=lambda: self.sort_excluded_column("severity"))
        
        self.excluded_tree.column("file", width=300, anchor='w', minwidth=200)
        self.excluded_tree.column("mods", width=250, anchor='w', minwidth=150)
        self.excluded_tree.column("count", width=80, anchor='center', minwidth=60)
        self.excluded_tree.column("severity", width=100, anchor='center', minwidth=80)
        
        v_scrollbar = ttk.Scrollbar(tree_frame, 
                                  orient="vertical",
                                  command=self.excluded_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame,
                                  orient="horizontal", 
                                  command=self.excluded_tree.xview)
        
        self.excluded_tree.configure(yscrollcommand=v_scrollbar.set,
                                   xscrollcommand=h_scrollbar.set)
        
        self.excluded_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
    def create_summary_panel(self):
        summary_frame = ttk.Frame(self, padding=10)
        summary_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ttk.Label(summary_frame, 
                 text="Summary",
                 font=('Segoe UI', 11, 'bold')).pack(side='left')
        
        self.summary_label = ttk.Label(summary_frame, text="No scan performed yet")
        self.summary_label.pack(side='left', padx=(20, 0))
        
    def bind_context_menus(self):
        self.tree.bind("<Button-3>", self.show_conflict_context_menu)
        self.excluded_tree.bind("<Button-3>", self.show_excluded_context_menu)
        
    def show_conflict_context_menu(self, event):
        if not self.tree.identify_row(event.y):
            return
            
        item = self.tree.identify_row(event.y)
        self.tree.selection_set(item)
        
        file_path = self.tree.item(item, "values")[0]
        mods = self.conflicts.get(file_path, [])
        
        context_menu = tk.Menu(self, tearoff=0)
        
        if len(mods) >= 2:
            mod_menu = tk.Menu(context_menu, tearoff=0)
            
            mod_pairs = []
            for i, mod1 in enumerate(mods):
                for mod2 in mods[i+1:]:
                    mod_pairs.append((mod1, mod2))
            
            for mod1, mod2 in mod_pairs:
                mod_menu.add_command(
                    label=f"Compare {mod1} vs {mod2}",
                    command=lambda m1=mod1, m2=mod2, fp=file_path: self.compare_mods(fp, m1, m2)
                )
                
            context_menu.add_cascade(label="Compare Mods", menu=mod_menu)
            context_menu.add_separator()
            
        context_menu.add_command(
            label="Exclude File",
            command=lambda: self.exclude_file(file_path)
        )
        
        context_menu.post(event.x_root, event.y_root)
        
    def show_excluded_context_menu(self, event):
        if not self.excluded_tree.identify_row(event.y):
            return
            
        item = self.excluded_tree.identify_row(event.y)
        self.excluded_tree.selection_set(item)
        
        file_path = self.excluded_tree.item(item, "values")[0]
        
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(
            label="Restore File",
            command=lambda: self.restore_file(file_path)
        )
        
        context_menu.post(event.x_root, event.y_root)
        
    def exclude_file(self, file_path):
        if file_path in self.conflicts:
            self.excluded_files.add(file_path)
            self.update_tree()
            self.update_excluded_tree()
            self.update_summary()
            
            if self.current_tab == "conflicts":
                messagebox.showinfo("File Excluded", f"'{file_path}' has been excluded from conflicts.")
            
    def restore_file(self, file_path):
        if file_path in self.excluded_files:
            self.excluded_files.remove(file_path)
            self.update_tree()
            self.update_excluded_tree()
            self.update_summary()
            
            if self.current_tab == "excluded":
                messagebox.showinfo("File Restored", f"'{file_path}' has been restored to conflicts.")
                
    def compare_mods(self, file_path, mod1, mod2):
        lml_dir = self.path_var.get().strip()
        if not os.path.isdir(lml_dir):
            messagebox.showerror("Error", "Please select a valid LML directory first.")
            return
            
        mod1_path = os.path.join(lml_dir, mod1, file_path)
        mod2_path = os.path.join(lml_dir, mod2, file_path)
        
        if not os.path.exists(mod1_path):
            messagebox.showerror("Error", f"File not found in {mod1}: {mod1_path}")
            return
            
        if not os.path.exists(mod2_path):
            messagebox.showerror("Error", f"File not found in {mod2}: {mod2_path}")
            return
            
        self.open_comparison_window(file_path, mod1, mod2, mod1_path, mod2_path)
        
    def open_comparison_window(self, file_path, mod1, mod2, mod1_path, mod2_path):
        import re
        import threading
        
        # Create window immediately
        compare_window = tk.Toplevel(self)
        compare_window.title(f"Compare: {file_path}")
        compare_window.geometry("1200x800")
        compare_window.minsize(800, 600)
        
        # Set up colors based on theme
        if self.dark_mode:
            sv_ttk.set_theme("dark")
            bg_color = "#1a1a1a"
            text_color = "#ffffff"
            line_number_bg = "#2d2d2d"
            line_number_fg = "#888888"
            diff_add_color = "#213a21"
            diff_remove_color = "#3a2121"
            diff_change_color = "#2d2d3a"
            search_highlight = "#5e4c10"
        else:
            sv_ttk.set_theme("light")
            bg_color = "#ffffff"
            text_color = "#000000"
            line_number_bg = "#f0f0f0"
            line_number_fg = "#888888"
            diff_add_color = "#e8f5e8"
            diff_remove_color = "#f8d7da"
            diff_change_color = "#e8eaf5"
            search_highlight = "#fff2cc"
        
        # Create main layout immediately
        main_frame = ttk.Frame(compare_window, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Show loading indicator
        loading_frame = ttk.Frame(main_frame)
        loading_frame.pack(fill='both', expand=True)
        
        loading_label = ttk.Label(loading_frame, 
                                text="Loading comparison...",
                                font=('Segoe UI', 14))
        loading_label.pack(expand=True)
        
        progress = ttk.Progressbar(loading_frame, mode='indeterminate')
        progress.pack(fill='x', padx=100, pady=10)
        progress.start()
        
        status_var = tk.StringVar(value="Initializing comparison...")
        status_label = ttk.Label(loading_frame, textvariable=status_var)
        status_label.pack(pady=10)
        
        compare_window.update()
        
        # Function to build UI with content
        def build_ui(mod1_content, mod2_content, is_binary=False):
            # Remove loading indicator
            loading_frame.destroy()
            
            # Create header
            header_frame = ttk.Frame(main_frame)
            header_frame.pack(fill='x', pady=(0, 10))
            
            ttk.Label(header_frame, 
                    text=f"Comparing: {file_path}",
                    font=('Segoe UI', 12, 'bold')).pack(side='top', anchor='w')
            
            info_frame = ttk.Frame(header_frame)
            info_frame.pack(fill='x', pady=(5, 0))
            
            ttk.Label(info_frame, text=f"Left: {mod1}").pack(side='left')
            ttk.Label(info_frame, text=f"Right: {mod2}").pack(side='right')
            
            # Create search controls
            search_frame = ttk.Frame(main_frame)
            search_frame.pack(fill='x', pady=(0, 10))
            
            left_search_frame = ttk.Frame(search_frame)
            left_search_frame.pack(side='left', fill='x', expand=True, padx=(0, 5))
            
            right_search_frame = ttk.Frame(search_frame)
            right_search_frame.pack(side='right', fill='x', expand=True, padx=(5, 0))
            
            left_search_var = tk.StringVar()
            right_search_var = tk.StringVar()
            left_search_count = tk.StringVar(value="0 matches")
            right_search_count = tk.StringVar(value="0 matches")
            
            ttk.Label(left_search_frame, text="Search Left:").pack(side='left')
            left_search_entry = ttk.Entry(left_search_frame, textvariable=left_search_var)
            left_search_entry.pack(side='left', fill='x', expand=True, padx=(5, 5))
            
            left_search_prev = ttk.Button(left_search_frame, text="◀", width=2)
            left_search_prev.pack(side='left')
            
            left_search_next = ttk.Button(left_search_frame, text="▶", width=2)
            left_search_next.pack(side='left', padx=(2, 5))
            
            ttk.Label(left_search_frame, textvariable=left_search_count).pack(side='left')
            
            ttk.Label(right_search_frame, text="Search Right:").pack(side='left')
            right_search_entry = ttk.Entry(right_search_frame, textvariable=right_search_var)
            right_search_entry.pack(side='left', fill='x', expand=True, padx=(5, 5))
            
            right_search_prev = ttk.Button(right_search_frame, text="◀", width=2)
            right_search_prev.pack(side='left')
            
            right_search_next = ttk.Button(right_search_frame, text="▶", width=2)
            right_search_next.pack(side='left', padx=(2, 5))
            
            ttk.Label(right_search_frame, textvariable=right_search_count).pack(side='left')
            
            # Options
            options_frame = ttk.Frame(main_frame)
            options_frame.pack(fill='x', pady=(0, 10))
            
            sync_scroll_var = tk.BooleanVar(value=True)
            backup_before_save_var = tk.BooleanVar(value=True)
            
            ttk.Checkbutton(options_frame, text="Sync Scrolling", variable=sync_scroll_var).pack(side='left')
            ttk.Checkbutton(options_frame, text="Backup Before Saving", variable=backup_before_save_var).pack(side='left', padx=(10, 0))
            
            # Editor panes
            paned_window = ttk.PanedWindow(main_frame, orient='horizontal')
            paned_window.pack(fill='both', expand=True)
            
            left_frame = ttk.Frame(paned_window)
            right_frame = ttk.Frame(paned_window)
            
            paned_window.add(left_frame, weight=1)
            paned_window.add(right_frame, weight=1)
            
            # Left editor with line numbers
            left_editor_frame = ttk.Frame(left_frame)
            left_editor_frame.pack(fill='both', expand=True)
            
            left_line_numbers = tk.Text(left_editor_frame, width=6, padx=5, pady=5, takefocus=0,
                                    bg=line_number_bg, fg=line_number_fg,
                                    border=0, font=('Consolas', 10))
            left_line_numbers.pack(side='left', fill='y')
            
            left_text = tk.Text(left_editor_frame, wrap='none', padx=5, pady=5,
                            bg=bg_color, fg=text_color, font=('Consolas', 10),
                            undo=True, maxundo=1000)
            left_text.pack(side='left', fill='both', expand=True)
            
            left_scroll_y = ttk.Scrollbar(left_editor_frame, orient='vertical', command=left_text.yview)
            left_scroll_y.pack(side='right', fill='y')
            
            left_scroll_x = ttk.Scrollbar(left_frame, orient='horizontal', command=left_text.xview)
            left_scroll_x.pack(side='bottom', fill='x')
            
            left_text.configure(yscrollcommand=left_scroll_y.set, xscrollcommand=left_scroll_x.set)
            left_line_numbers.configure(yscrollcommand=left_scroll_y.set)
            
            # Right editor with line numbers
            right_editor_frame = ttk.Frame(right_frame)
            right_editor_frame.pack(fill='both', expand=True)
            
            right_line_numbers = tk.Text(right_editor_frame, width=6, padx=5, pady=5, takefocus=0,
                                    bg=line_number_bg, fg=line_number_fg,
                                    border=0, font=('Consolas', 10))
            right_line_numbers.pack(side='left', fill='y')
            
            right_text = tk.Text(right_editor_frame, wrap='none', padx=5, pady=5,
                            bg=bg_color, fg=text_color, font=('Consolas', 10),
                            undo=True, maxundo=1000)
            right_text.pack(side='left', fill='both', expand=True)
            
            right_scroll_y = ttk.Scrollbar(right_editor_frame, orient='vertical', command=right_text.yview)
            right_scroll_y.pack(side='right', fill='y')
            
            right_scroll_x = ttk.Scrollbar(right_frame, orient='horizontal', command=right_text.xview)
            right_scroll_x.pack(side='bottom', fill='x')
            
            right_text.configure(yscrollcommand=right_scroll_y.set, xscrollcommand=right_scroll_x.set)
            right_line_numbers.configure(yscrollcommand=right_scroll_y.set)
            
            # Configure tags
            left_text.tag_configure("add", background=diff_add_color)
            left_text.tag_configure("remove", background=diff_remove_color)
            left_text.tag_configure("change", background=diff_change_color)
            left_text.tag_configure("search", background=search_highlight)
            left_text.tag_configure("current_search", background=search_highlight, underline=1)
            
            right_text.tag_configure("add", background=diff_add_color)
            right_text.tag_configure("remove", background=diff_remove_color)
            right_text.tag_configure("change", background=diff_change_color)
            right_text.tag_configure("search", background=search_highlight)
            right_text.tag_configure("current_search", background=search_highlight, underline=1)
            
            # Button frame
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill='x', pady=(10, 0))
            
            left_buttons = ttk.Frame(button_frame)
            left_buttons.pack(side='left', fill='x', expand=True)
            
            right_buttons = ttk.Frame(button_frame)
            right_buttons.pack(side='right', fill='x', expand=True)
            
            # Save functions
            def save_file(path, content):
                if backup_before_save_var.get():
                    backup_path = path + ".bak"
                    try:
                        shutil.copy2(path, backup_path)
                    except Exception as e:
                        messagebox.showerror("Backup Error", f"Failed to create backup: {str(e)}")
                        return
                
                try:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    messagebox.showinfo("Save Successful", f"File saved: {path}")
                except Exception as e:
                    messagebox.showerror("Save Error", f"Failed to save file: {str(e)}")
            
            def save_file_as(content):
                save_path = filedialog.asksaveasfilename(
                    defaultextension=os.path.splitext(file_path)[1],
                    filetypes=[("All Files", "*.*")],
                    title="Save File As"
                )
                
                if not save_path:
                    return
                    
                try:
                    with open(save_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    messagebox.showinfo("Save Successful", f"File saved as: {save_path}")
                except Exception as e:
                    messagebox.showerror("Save Error", f"Failed to save file: {str(e)}")
            
            # Save buttons
            save_left_btn = ttk.Button(left_buttons, text="Save", style='Accent.TButton')
            save_left_btn.config(command=lambda: save_file(mod1_path, left_text.get("1.0", "end-1c")))
            save_left_btn.pack(side='left')
            
            save_left_as_btn = ttk.Button(left_buttons, text="Save As")
            save_left_as_btn.config(command=lambda: save_file_as(left_text.get("1.0", "end-1c")))
            save_left_as_btn.pack(side='left', padx=(5, 0))
            
            save_right_btn = ttk.Button(right_buttons, text="Save", style='Accent.TButton')
            save_right_btn.config(command=lambda: save_file(mod2_path, right_text.get("1.0", "end-1c")))
            save_right_btn.pack(side='right')
            
            save_right_as_btn = ttk.Button(right_buttons, text="Save As")
            save_right_as_btn.config(command=lambda: save_file_as(right_text.get("1.0", "end-1c")))
            save_right_as_btn.pack(side='right', padx=(0, 5))
            
            # Handle binary files
            if is_binary:
                left_text.insert(tk.END, f"Binary file from {mod1}\n")
                left_text.insert(tk.END, f"Cannot display content - binary files cannot be compared as text.")
                
                right_text.insert(tk.END, f"Binary file from {mod2}\n")
                right_text.insert(tk.END, f"Cannot display content - binary files cannot be compared as text.")
                
                left_text.config(state='disabled')
                right_text.config(state='disabled')
                return
            
            # Insert content directly (much faster than chunking for most files)
            left_text.insert("1.0", mod1_content)
            right_text.insert("1.0", mod2_content)
            
            # Update line numbers
            def update_line_numbers(text_widget, line_numbers):
                line_count = text_widget.get("1.0", "end").count("\n")
                line_numbers_text = "\n".join(str(i) for i in range(1, line_count + 1))
                line_numbers.config(state='normal')
                line_numbers.delete("1.0", "end")
                line_numbers.insert("1.0", line_numbers_text)
                line_numbers.config(state='disabled')
            
            update_line_numbers(left_text, left_line_numbers)
            update_line_numbers(right_text, right_line_numbers)
            
            # Sync scrolling
            def sync_scroll_y(*args):
                if sync_scroll_var.get():
                    left_text.yview_moveto(args[0])
                    right_text.yview_moveto(args[0])
                    left_line_numbers.yview_moveto(args[0])
                    right_line_numbers.yview_moveto(args[0])
            
            left_text.config(yscrollcommand=lambda *args: sync_scroll_y(*args) or left_scroll_y.set(*args))
            right_text.config(yscrollcommand=lambda *args: sync_scroll_y(*args) or right_scroll_y.set(*args))
            
            # Search functionality
            left_search_matches = []
            right_search_matches = []
            left_current_match = tk.IntVar(value=-1)
            right_current_match = tk.IntVar(value=-1)
            
            def search_text(text_widget, search_var, count_var):
                search_term = search_var.get()
                text_widget.tag_remove("search", "1.0", "end")
                text_widget.tag_remove("current_search", "1.0", "end")
                
                if not search_term:
                    count_var.set("0 matches")
                    return []
                
                matches = []
                start_pos = "1.0"
                
                while True:
                    start_pos = text_widget.search(search_term, start_pos, stopindex="end", nocase=True)
                    if not start_pos:
                        break
                        
                    end_pos = f"{start_pos}+{len(search_term)}c"
                    text_widget.tag_add("search", start_pos, end_pos)
                    matches.append(start_pos)
                    start_pos = end_pos
                
                count_var.set(f"{len(matches)} matches")
                return matches
            
            def navigate_search(text_widget, matches, current_match, direction, search_term):
                if not matches:
                    return
                    
                total = len(matches)
                if direction == "next":
                    new_index = (current_match.get() + 1) % total
                else:
                    new_index = (current_match.get() - 1) % total
                    
                current_match.set(new_index)
                match_pos = matches[new_index]
                
                text_widget.see(match_pos)
                
                text_widget.tag_remove("current_search", "1.0", "end")
                end_pos = f"{match_pos}+{len(search_term)}c"
                text_widget.tag_add("current_search", match_pos, end_pos)
            
            # Configure search buttons
            left_search_var.trace_add("write", lambda *args: 
                compare_window.after(300, lambda: 
                    setattr(compare_window, '_left_matches', search_text(left_text, left_search_var, left_search_count))))
                    
            right_search_var.trace_add("write", lambda *args: 
                compare_window.after(300, lambda: 
                    setattr(compare_window, '_right_matches', search_text(right_text, right_search_var, right_search_count))))
            
            left_search_next.config(command=lambda: navigate_search(
                left_text, getattr(compare_window, '_left_matches', []), left_current_match, "next", left_search_var.get()))
            left_search_prev.config(command=lambda: navigate_search(
                left_text, getattr(compare_window, '_left_matches', []), left_current_match, "previous", left_search_var.get()))
            
            right_search_next.config(command=lambda: navigate_search(
                right_text, getattr(compare_window, '_right_matches', []), right_current_match, "next", right_search_var.get()))
            right_search_prev.config(command=lambda: navigate_search(
                right_text, getattr(compare_window, '_right_matches', []), right_current_match, "previous", right_search_var.get()))
            
            # Create a status bar for highlighting progress
            status_frame = ttk.Frame(main_frame)
            status_frame.pack(fill='x', pady=(5, 0))
            
            highlight_progress = ttk.Progressbar(status_frame, mode='determinate')
            highlight_progress.pack(fill='x', expand=True)
            
            highlight_status = ttk.Label(status_frame, text="Analyzing differences...")
            highlight_status.pack(pady=(2, 0))
            
            # Highlight differences directly in the main thread for better reliability
            def highlight_differences():
                left_lines = mod1_content.splitlines()
                right_lines = mod2_content.splitlines()
                
                min_len = min(len(left_lines), len(right_lines))
                total_lines = max(len(left_lines), len(right_lines))
                
                # Update progress bar
                highlight_progress['maximum'] = total_lines
                highlight_progress['value'] = 0
                
                # Process in batches
                batch_size = 50
                
                def process_batch(start_idx=0):
                    end_idx = min(start_idx + batch_size, min_len)
                    
                    # Update progress
                    highlight_progress['value'] = start_idx
                    highlight_status.config(text=f"Analyzing differences... ({start_idx}/{total_lines} lines)")
                    
                    # Process this batch
                    for i in range(start_idx, end_idx):
                        if left_lines[i] != right_lines[i]:
                            left_text.tag_add("change", f"{i+1}.0", f"{i+1}.end+1c")
                            right_text.tag_add("change", f"{i+1}.0", f"{i+1}.end+1c")
                    
                    # Schedule next batch or finish
                    if end_idx < min_len:
                        compare_window.after(1, lambda: process_batch(end_idx))
                    else:
                        # Handle different lengths
                        if len(left_lines) > len(right_lines):
                            for i in range(min_len, len(left_lines)):
                                left_text.tag_add("add", f"{i+1}.0", f"{i+1}.end+1c")
                        elif len(right_lines) > len(left_lines):
                            for i in range(min_len, len(right_lines)):
                                right_text.tag_add("add", f"{i+1}.0", f"{i+1}.end+1c")
                        
                        # Complete
                        highlight_progress['value'] = total_lines
                        highlight_status.config(text=f"Completed - {total_lines} lines analyzed")
                        
                        # Hide progress after a delay
                        compare_window.after(1000, lambda: status_frame.pack_forget())
                
                # Start processing
                process_batch()
            
            # Start highlighting after a short delay to let the UI render
            compare_window.after(100, highlight_differences)
        
        # Load files in background thread
        def load_files_thread():
            try:
                status_var.set("Checking file types...")
                
                # Check if file is binary
                def is_binary(file_path):
                    try:
                        with open(file_path, 'rb') as f:
                            chunk = f.read(1024)
                            return b'\0' in chunk
                    except:
                        return True
                
                is_binary_file = is_binary(mod1_path) or is_binary(mod2_path)
                
                if is_binary_file:
                    compare_window.after(0, lambda: build_ui("", "", True))
                    return
                
                status_var.set("Loading files...")
                
                # Load files directly - much faster than using ThreadPoolExecutor for most files
                try:
                    with open(mod1_path, 'r', encoding='utf-8', errors='replace') as f:
                        mod1_content = f.read()
                    with open(mod2_path, 'r', encoding='utf-8', errors='replace') as f:
                        mod2_content = f.read()
                    
                    compare_window.after(0, lambda: build_ui(mod1_content, mod2_content))
                except Exception as e:
                    compare_window.after(0, lambda: messagebox.showerror("Error", f"Failed to load files: {str(e)}"))
                    compare_window.after(0, lambda: compare_window.destroy())
                
            except Exception as e:
                compare_window.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
                compare_window.after(0, lambda: compare_window.destroy())
        
        # Start loading files
        threading.Thread(target=load_files_thread, daemon=True).start()

        
    def apply_tree_tags(self):
        if hasattr(self, 'type_tree'):
            self.type_tree.tag_configure('file_item', foreground='#4a9eff')
        
        if hasattr(self, 'tree'):
            if self.dark_mode:
                self.tree.tag_configure('low_conflict', background='#213a21')
                self.tree.tag_configure('medium_conflict', background='#3a3321')
                self.tree.tag_configure('high_conflict', background='#3a2121')
                self.tree.tag_configure('gxt2_file', background='#3a3321')
            else:
                self.tree.tag_configure('low_conflict', background='#e8f5e8')
                self.tree.tag_configure('medium_conflict', background='#fff3cd')
                self.tree.tag_configure('high_conflict', background='#f8d7da')
                self.tree.tag_configure('gxt2_file', background='#fff3cd')
                
        if hasattr(self, 'excluded_tree'):
            if self.dark_mode:
                self.excluded_tree.tag_configure('low_conflict', background='#213a21')
                self.excluded_tree.tag_configure('medium_conflict', background='#3a3321')
                self.excluded_tree.tag_configure('high_conflict', background='#3a2121')
                self.excluded_tree.tag_configure('gxt2_file', background='#3a3321')
            else:
                self.excluded_tree.tag_configure('low_conflict', background='#e8f5e8')
                self.excluded_tree.tag_configure('medium_conflict', background='#fff3cd')
                self.excluded_tree.tag_configure('high_conflict', background='#f8d7da')
                self.excluded_tree.tag_configure('gxt2_file', background='#fff3cd')
                
    def toggle_file_type_filters(self):
        if self.toggle_visible.get():
            self.filter_panel.pack_forget()
            self.toggle_btn.config(text="Show File Type Filters")
            self.toggle_visible.set(False)
        else:
            self.filter_panel.pack(fill='x', pady=(0, 10))
            self.toggle_btn.config(text="Hide File Type Filters")
            self.toggle_visible.set(True)
            self.update_file_type_toggles()
            
    def update_file_type_toggles(self):
        for widget in self.filter_panel.winfo_children():
            widget.destroy()
            
        if not self.conflicts:
            return
            
        type_counts = {}
        for path in self.conflicts.keys():
            if path in self.excluded_files:
                continue
            ext = os.path.splitext(path)[1] or "No Extension"
            type_counts[ext] = type_counts.get(ext, 0) + 1
        
        grid_frame = ttk.Frame(self.filter_panel)
        grid_frame.pack(fill='x', expand=True)
        
        num_types = len(type_counts)
        max_columns = min(6, max(1, num_types // 2))
        
        row, col = 0, 0
        
        for ext in sorted(type_counts.keys()):
            if ext not in self.file_type_toggles:
                self.file_type_toggles[ext] = tk.BooleanVar(value=True)
                
            check = ttk.Checkbutton(
                grid_frame, 
                text=f"{ext} ({type_counts[ext]})",
                variable=self.file_type_toggles[ext],
                command=self.debounced_update_tree
            )
            check.grid(row=row, column=col, sticky='w', padx=5, pady=2)
            
            col += 1
            if col >= max_columns:
                col = 0
                row += 1
    
    def on_type_select(self, event):
        selection = self.type_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        item_text = self.type_tree.item(item, "text")
        parent_id = self.type_tree.parent(item)
        
        if item_text == "All File Types":
            self.filter_var.set("All")
            self.search_var.set("")
            
            for var in self.file_type_toggles.values():
                var.set(True)
                
        elif parent_id == "":
            self.filter_var.set(item_text)
        else:
            parent_text = self.type_tree.item(parent_id, "text")
            
            selected_file = None
            for path in self.conflicts.keys():
                if os.path.basename(path) == item_text and path.endswith(parent_text):
                    selected_file = path
                    break
            
            if selected_file:
                self.search_var.set(selected_file)
                self.filter_var.set("All")
                
        self.update_tree()
    
    @property
    def debounced_update_tree(self):
        if not hasattr(self, '_update_tree_timer'):
            self._update_tree_timer = None
            
        def debounced():
            if self._update_tree_timer:
                self.after_cancel(self._update_tree_timer)
            self._update_tree_timer = self.after(300, self.update_tree)
            
        return debounced
            
    def update_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not self.conflicts:
            self.results_count.config(text="0 conflicts found")
            return
            
        search_term = self.search_var.get().lower()
        file_filter = self.filter_var.get()
        
        filtered_conflicts = []
        
        for path, mods in sorted(self.conflicts.items()):
            if path in self.excluded_files:
                continue
                
            ext = os.path.splitext(path)[1] or "No Extension"
            if ext in self.file_type_toggles and not self.file_type_toggles[ext].get():
                continue
                
            if search_term:
                if (search_term not in path.lower() and 
                    not any(search_term in m.lower() for m in mods)):
                    continue
                    
            severity = self.get_conflict_severity(path, mods)
            
            if file_filter == "High Severity" and severity != "High":
                continue
            elif file_filter == "Medium Severity" and severity != "Medium":
                continue
            elif file_filter == "Low Severity" and severity != "Low":
                continue
            elif file_filter.startswith(".") and not path.endswith(file_filter):
                continue
            elif file_filter not in ["All", "High Severity", "Medium Severity", "Low Severity"] and not file_filter.startswith("."):
                continue
                
            filtered_conflicts.append((path, mods, severity))
        
        batch_size = 100
        total_items = len(filtered_conflicts)
        
        def process_batch(start_idx):
            end_idx = min(start_idx + batch_size, total_items)
            batch = filtered_conflicts[start_idx:end_idx]
            
            for path, mods, severity in batch:
                count = len(mods)
                
                item_id = self.tree.insert("", tk.END, 
                                         values=(path, ", ".join(mods), count, severity))
                
                if severity == "High":
                    self.tree.set(item_id, "severity", "🔴 High")
                    tags = ('high_conflict',)
                elif severity == "Medium":
                    self.tree.set(item_id, "severity", "🟡 Medium")
                    tags = ('medium_conflict',)
                else:
                    self.tree.set(item_id, "severity", "🟢 Low")
                    tags = ('low_conflict',)
                    
                if path.endswith('.gxt2'):
                    tags = tags + ('gxt2_file',)
                    
                self.tree.item(item_id, tags=tags)
            
            if end_idx < total_items:
                self.after(1, lambda: process_batch(end_idx))
            else:
                self.apply_tree_tags()
                self.results_count.config(text=f"{total_items} conflicts found")
        
        if filtered_conflicts:
            process_batch(0)
        else:
            self.results_count.config(text="0 conflicts found")
            
    def update_excluded_tree(self):
        for item in self.excluded_tree.get_children():
            self.excluded_tree.delete(item)
            
        if not self.excluded_files:
            self.excluded_count.config(text="0 files excluded")
            return
            
        excluded_conflicts = []
        
        for path in self.excluded_files:
            if path in self.conflicts:
                mods = self.conflicts[path]
                severity = self.get_conflict_severity(path, mods)
                excluded_conflicts.append((path, mods, severity))
        
        batch_size = 100
        total_items = len(excluded_conflicts)
        
        def process_batch(start_idx):
            end_idx = min(start_idx + batch_size, total_items)
            batch = excluded_conflicts[start_idx:end_idx]
            
            for path, mods, severity in batch:
                count = len(mods)
                
                item_id = self.excluded_tree.insert("", tk.END, 
                                                  values=(path, ", ".join(mods), count, severity))
                
                if severity == "High":
                    self.excluded_tree.set(item_id, "severity", "🔴 High")
                    tags = ('high_conflict',)
                elif severity == "Medium":
                    self.excluded_tree.set(item_id, "severity", "🟡 Medium")
                    tags = ('medium_conflict',)
                else:
                    self.excluded_tree.set(item_id, "severity", "🟢 Low")
                    tags = ('low_conflict',)
                    
                if path.endswith('.gxt2'):
                    tags = tags + ('gxt2_file',)
                    
                self.excluded_tree.item(item_id, tags=tags)
            
            if end_idx < total_items:
                self.after(1, lambda: process_batch(end_idx))
            else:
                self.apply_tree_tags()
                self.excluded_count.config(text=f"{total_items} files excluded")
        
        if excluded_conflicts:
            process_batch(0)
        else:
            self.excluded_count.config(text="0 files excluded")
            
    def update_type_tree(self):
        for item in self.type_tree.get_children():
            self.type_tree.delete(item)
            
        if not self.conflicts:
            return
            
        type_groups = defaultdict(list)
        active_conflicts = {path: mods for path, mods in self.conflicts.items() 
                          if path not in self.excluded_files}
        
        for path, mods in active_conflicts.items():
            ext = os.path.splitext(path)[1] or "No Extension"
            type_groups[ext].append((path, mods))
            
        all_item = self.type_tree.insert("", "end", text="All File Types", 
                                       values=[f"({len(active_conflicts)} conflicts)"])
        
        def add_file_types():
            for ext, conflicts in sorted(type_groups.items()):
                parent = self.type_tree.insert("", "end", text=ext, 
                                             values=[f"({len(conflicts)} conflicts)"])
                
                batch_size = 50
                total_files = len(conflicts)
                
                def add_files_batch(start_idx, parent_id):
                    end_idx = min(start_idx + batch_size, total_files)
                    batch = conflicts[start_idx:end_idx]
                    
                    for path, mods in sorted(batch):
                        filename = os.path.basename(path)
                        
                        self.type_tree.insert(parent_id, "end", text=filename, 
                                            values=[f"({len(mods)} mods)"],
                                            tags=('file_item',))
                    
                    if end_idx < total_files:
                        self.after(1, lambda: add_files_batch(end_idx, parent_id))
                
                add_files_batch(0, parent)
        
        self.after(10, add_file_types)
        
    def sort_column(self, col):
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        
        if col == "count":
            data.sort(key=lambda x: int(x[0]) if x[0].isdigit() else 0, reverse=True)
        else:
            data.sort(key=lambda x: x[0].lower())
        
        batch_size = 100
        total_items = len(data)
        
        def move_batch(start_idx):
            end_idx = min(start_idx + batch_size, total_items)
            batch = data[start_idx:end_idx]
            
            for i, (val, child) in enumerate(batch, start=start_idx):
                self.tree.move(child, '', i)
            
            if end_idx < total_items:
                self.after(1, lambda: move_batch(end_idx))
        
        if data:
            move_batch(0)
            
    def sort_excluded_column(self, col):
        data = [(self.excluded_tree.set(child, col), child) for child in self.excluded_tree.get_children('')]
        
        if col == "count":
            data.sort(key=lambda x: int(x[0]) if x[0].isdigit() else 0, reverse=True)
        else:
            data.sort(key=lambda x: x[0].lower())
        
        batch_size = 100
        total_items = len(data)
        
        def move_batch(start_idx):
            end_idx = min(start_idx + batch_size, total_items)
            batch = data[start_idx:end_idx]
            
            for i, (val, child) in enumerate(batch, start=start_idx):
                self.excluded_tree.move(child, '', i)
            
            if end_idx < total_items:
                self.after(1, lambda: move_batch(end_idx))
        
        if data:
            move_batch(0)
        
    def get_conflict_severity(self, path, mods):
        count = len(mods)
        if path.endswith('.meta') or count > 4:
            return "High"
        elif count > 2 or path.endswith(('.xml', '.dat', '.ydd')):
            return "Medium"
        elif path.endswith('.ytd'):
            return "High" if count > 2 else "Medium"
        else:
            return "Low"
            
    def update_summary(self):
        if not self.conflicts:
            self.summary_label.config(text="No conflicts found")
            return
            
        active_conflicts = {path: mods for path, mods in self.conflicts.items() if path not in self.excluded_files}
        total_conflicts = len(active_conflicts)
        affected_mods = len(set(mod for mods in active_conflicts.values() for mod in mods))
        
        high_severity = sum(1 for path, mods in active_conflicts.items() 
                           if self.get_conflict_severity(path, mods) == "High")
        
        texture_conflicts = sum(1 for path in active_conflicts if path.endswith('.ytd'))
        excluded_count = len(self.excluded_files)
        
        summary_text = f"Total: {total_conflicts} conflicts | Affected mods: {affected_mods} | High severity: {high_severity} | Texture conflicts: {texture_conflicts} | Excluded: {excluded_count}"
        self.summary_label.config(text=summary_text)
        
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select LML Folder")
        if folder:
            self.path_var.set(folder)
            
    def scan_conflicts_threaded(self):
        if self.is_scanning:
            return
            
        lml_dir = self.path_var.get().strip()
        if not os.path.isdir(lml_dir):
            messagebox.showerror("Error", f"'{lml_dir}' is not a valid directory.")
            return
            
        self.is_scanning = True
        self.scan_btn.config(text="Scanning...", state='disabled')
        self.config(cursor="watch")
        self.update_idletasks()
        
        threading.Thread(target=self.scan_conflicts, args=(lml_dir,), daemon=True).start()
        
    def scan_conflicts(self, lml_dir):
        try:
            cache_file = os.path.join(tempfile.gettempdir(), "rdr2_mod_cache.json")
            use_cache = False
            
            if os.path.exists(cache_file):
                cache_time = os.path.getmtime(cache_file)
                if time.time() - cache_time < 3600:
                    try:
                        with open(cache_file, 'r') as f:
                            cache_data = json.load(f)
                            
                        if cache_data.get("lml_dir") == lml_dir:
                            files_map = cache_data.get("files_map", {})
                            use_cache = True
                    except:
                        pass
            
            if not use_cache:
                files_map = self.gather_mod_files_optimized(lml_dir)
                
                try:
                    cache_data = {
                        "lml_dir": lml_dir,
                        "files_map": files_map,
                        "timestamp": time.time()
                    }
                    with open(cache_file, 'w') as f:
                        json.dump(cache_data, f)
                except:
                    pass
            
            self.conflicts = {path: mods for path, mods in files_map.items() if len(mods) > 1}
            
            all_mods = set()
            for mods in self.conflicts.values():
                all_mods.update(mods)
            
            colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', 
                     '#ff9ff3', '#54a0ff', '#5f27cd', '#00d2d3', '#ff9f43']
            
            self.mod_colors = {}
            for i, mod in enumerate(sorted(all_mods)):
                self.mod_colors[mod] = colors[i % len(colors)]
            
            self.after(0, self.scan_complete)
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.after(0, self.scan_complete)
            
    def gather_mod_files_optimized(self, mods_dir):
        files_map = defaultdict(list)
        
        mods = [d for d in os.listdir(mods_dir) if os.path.isdir(os.path.join(mods_dir, d))]
        total_mods = len(mods)
        
        def process_mod(mod_name):
            mod_files = {}
            mod_path = os.path.join(mods_dir, mod_name)
            
            for root, _, files in os.walk(mod_path):
                for fname in files:
                    rel_root = os.path.relpath(root, mod_path)
                    rel_path = fname if rel_root == '.' else os.path.join(rel_root, fname)
                    mod_files[rel_path] = mod_name
            
            return mod_files
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 4)) as executor:
            futures = {executor.submit(process_mod, mod): mod for mod in mods}
            
            for future in concurrent.futures.as_completed(futures):
                mod = futures[future]
                try:
                    mod_files = future.result()
                    for rel_path, _ in mod_files.items():
                        files_map[rel_path].append(mod)
                except Exception as e:
                    print(f"Error processing mod {mod}: {e}")
        
        return files_map
        
    def scan_complete(self):
        self.is_scanning = False
        self.scan_btn.config(text="Scan for Conflicts", state='normal')
        self.config(cursor="")
        
        self.update_tree()
        self.update_type_tree()
        self.update_summary()
        
        has_gxt2 = any(path.endswith('.gxt2') for path in self.conflicts)
        if has_gxt2:
            self.gxt2_warning.pack(fill='x', pady=(0, 10))
        else:
            self.gxt2_warning.pack_forget()
        
        if not self.conflicts:
            messagebox.showinfo("No Conflicts", "No conflicts detected in your mods!")
            
    def create_backup(self):
        lml_dir = self.path_var.get().strip()
        if not os.path.isdir(lml_dir):
            messagebox.showerror("Error", "Please select a valid LML directory first.")
            return
            
        try:
            # Ask for backup name
            backup_name_dialog = tk.Toplevel(self)
            backup_name_dialog.title("Backup Name")
            backup_name_dialog.geometry("400x150")
            backup_name_dialog.transient(self)
            backup_name_dialog.grab_set()
            backup_name_dialog.resizable(False, False)
            
            ttk.Label(backup_name_dialog, text="Enter a name for this backup:", font=('Segoe UI', 11)).pack(pady=(20, 10))
            
            # Default name with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"LML_Backup_{timestamp}"
            
            name_var = tk.StringVar(value=default_name)
            name_entry = ttk.Entry(backup_name_dialog, textvariable=name_var, width=40)
            name_entry.pack(padx=20, fill='x')
            name_entry.select_range(0, 'end')
            name_entry.focus_set()
            
            button_frame = ttk.Frame(backup_name_dialog)
            button_frame.pack(fill='x', pady=(15, 10), padx=20)
            
            def on_cancel():
                backup_name_dialog.destroy()
                
            def on_confirm():
                backup_name = name_var.get().strip()
                if not backup_name:
                    messagebox.showerror("Error", "Please enter a valid backup name.")
                    return
                    
                # Replace invalid filename characters
                backup_name = "".join(c for c in backup_name if c.isalnum() or c in "._- ")
                
                backup_name_dialog.destroy()
                self.perform_backup(lml_dir, backup_name)
            
            ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side='left')
            ttk.Button(button_frame, text="Create Backup", style='Accent.TButton', command=on_confirm).pack(side='right')
            
            # Center the dialog
            backup_name_dialog.update_idletasks()
            width = backup_name_dialog.winfo_width()
            height = backup_name_dialog.winfo_height()
            x = (self.winfo_screenwidth() // 2) - (width // 2)
            y = (self.winfo_screenheight() // 2) - (height // 2)
            backup_name_dialog.geometry(f'{width}x{height}+{x}+{y}')
            
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to create backup: {str(e)}")

    def perform_backup(self, lml_dir, backup_name):
        """Perform the actual backup operation with the given name"""
        try:
            # Create backups directory if it doesn't exist
            backups_dir = os.path.join(os.path.dirname(lml_dir), "LML_Backups")
            os.makedirs(backups_dir, exist_ok=True)
            
            # Create backup file path
            backup_path = os.path.join(backups_dir, f"{backup_name}.zip")
            
            # Check if file already exists
            if os.path.exists(backup_path):
                result = messagebox.askyesno(
                    "Backup Exists", 
                    f"A backup with the name '{backup_name}' already exists. Overwrite?",
                    icon="warning"
                )
                if not result:
                    return
            
            # Show progress dialog
            progress_window = tk.Toplevel(self)
            progress_window.title("Creating Backup")
            progress_window.geometry("400x150")
            progress_window.transient(self)
            progress_window.grab_set()
            
            ttk.Label(progress_window, text="Creating backup...", font=('Segoe UI', 12)).pack(pady=(20, 10))
            progress = ttk.Progressbar(progress_window, mode='indeterminate')
            progress.pack(fill='x', padx=20)
            progress.start()
            
            status_var = tk.StringVar(value="Preparing...")
            ttk.Label(progress_window, textvariable=status_var).pack(pady=10)
            
            # Update UI
            progress_window.update()
            
            # Create backup in background thread
            def create_backup_thread():
                try:
                    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        total_files = sum([len(files) for _, _, files in os.walk(lml_dir)])
                        processed = 0
                        
                        for root, dirs, files in os.walk(lml_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arc_name = os.path.relpath(file_path, lml_dir)
                                zipf.write(file_path, arc_name)
                                
                                processed += 1
                                if processed % 10 == 0:  # Update status every 10 files
                                    self.after(0, lambda: status_var.set(f"Processing file {processed}/{total_files}"))
                    
                    # Create metadata file inside the zip
                    with tempfile.NamedTemporaryFile(mode='w', delete=False) as meta_file:
                        meta_data = {
                            "name": backup_name,
                            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "lml_dir": lml_dir,
                            "file_count": total_files
                        }
                        json.dump(meta_data, meta_file)
                        meta_file_path = meta_file.name
                    
                    # Add metadata to zip
                    with zipfile.ZipFile(backup_path, 'a') as zipf:
                        zipf.write(meta_file_path, "backup_metadata.json")
                    
                    # Clean up temp file
                    os.unlink(meta_file_path)
                    
                    self.backup_folder = backup_path
                    self.after(0, lambda: self.restore_btn.config(state='normal'))
                    self.after(0, lambda: progress_window.destroy())
                    self.after(0, lambda: messagebox.showinfo("Backup Complete", f"Backup '{backup_name}' created successfully."))
                    
                except Exception as e:
                    self.after(0, lambda: progress_window.destroy())
                    self.after(0, lambda: messagebox.showerror("Backup Error", f"Failed to create backup: {str(e)}"))
            
            threading.Thread(target=create_backup_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to create backup: {str(e)}")

    def restore_backup(self):
        """Restore from a selected backup file"""
        lml_dir = self.path_var.get().strip()
        if not os.path.isdir(lml_dir):
            messagebox.showerror(
                "Error", "Please select a valid LML directory first."
            )
            return

        # Look for backups directory
        backups_dir = os.path.join(os.path.dirname(lml_dir), "LML_Backups")
        if os.path.isdir(backups_dir):
            backup_files = [f for f in os.listdir(backups_dir) if f.endswith('.zip')]
        else:
            backup_files = []
        
        if not backup_files:
            # No backups found in the default location, ask user to select a file
            backup_file = filedialog.askopenfilename(
                filetypes=[("ZIP files", "*.zip")],
                title="Select Backup File"
            )
            if not backup_file:
                return
            self.select_backup_to_restore(backup_file)
        else:
            # Show backup selection dialog
            self.show_backup_selection_dialog(backups_dir, backup_files)

    def show_backup_selection_dialog(self, backups_dir, backup_files):
        """Show a dialog to select which backup to restore"""
        backup_dialog = tk.Toplevel(self)
        backup_dialog.title("Select Backup to Restore")
        backup_dialog.geometry("500x400")
        backup_dialog.transient(self)
        backup_dialog.grab_set()
        
        ttk.Label(backup_dialog, text="Select a backup to restore:", font=('Segoe UI', 12, 'bold')).pack(pady=(15, 5), padx=15, anchor='w')
        
        # Create a frame for the list with scrollbar
        list_frame = ttk.Frame(backup_dialog)
        list_frame.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Create treeview for backups
        columns = ("name", "date", "size")
        backup_tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        
        backup_tree.heading("name", text="Backup Name")
        backup_tree.heading("date", text="Date Created")
        backup_tree.heading("size", text="Size")
        
        backup_tree.column("name", width=200, anchor='w')
        backup_tree.column("date", width=150, anchor='w')
        backup_tree.column("size", width=100, anchor='e')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=backup_tree.yview)
        backup_tree.configure(yscrollcommand=scrollbar.set)
        
        backup_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Populate the list
        backup_info = []
        for file in backup_files:
            file_path = os.path.join(backups_dir, file)
            file_size = os.path.getsize(file_path)
            file_size_str = f"{file_size / (1024*1024):.1f} MB"
            
            # Try to get metadata from zip
            try:
                with zipfile.ZipFile(file_path, 'r') as zipf:
                    if "backup_metadata.json" in zipf.namelist():
                        with zipf.open("backup_metadata.json") as meta_file:
                            meta_data = json.load(meta_file)
                            name = meta_data.get("name", os.path.splitext(file)[0])
                            date = meta_data.get("created", "Unknown")
                    else:
                        # Get info from filename and modification time
                        name = os.path.splitext(file)[0]
                        date = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
            except:
                # Fallback if metadata can't be read
                name = os.path.splitext(file)[0]
                date = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
            
            backup_info.append((name, date, file_size_str, file_path))
        
        # Sort by date (newest first)
        backup_info.sort(key=lambda x: x[1], reverse=True)
        
        # Add to tree
        for name, date, size, path in backup_info:
            backup_tree.insert("", "end", values=(name, date, size), tags=(path,))
        
        # Select the first item
        if backup_info:
            first_item = backup_tree.get_children()[0]
            backup_tree.selection_set(first_item)
            backup_tree.focus(first_item)
        
        # Button frame
        button_frame = ttk.Frame(backup_dialog)
        button_frame.pack(fill='x', pady=15, padx=15)
        
        def on_cancel():
            backup_dialog.destroy()
        
        def on_select():
            selected_items = backup_tree.selection()
            if not selected_items:
                messagebox.showerror("Error", "Please select a backup to restore.")
                return
            
            selected_item = selected_items[0]
            selected_path = backup_tree.item(selected_item, "tags")[0]
            
            backup_dialog.destroy()
            self.select_backup_to_restore(selected_path)
        
        def on_browse():
            backup_file = filedialog.askopenfilename(
                filetypes=[("ZIP files", "*.zip")],
                title="Select Backup File"
            )
            if backup_file:
                backup_dialog.destroy()
                self.select_backup_to_restore(backup_file)
        
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side='left')
        ttk.Button(button_frame, text="Browse for Backup", command=on_browse).pack(side='left', padx=10)
        ttk.Button(button_frame, text="Restore Selected", style='Accent.TButton', command=on_select).pack(side='right')
        
        # Double-click to select
        backup_tree.bind("<Double-1>", lambda e: on_select())
        
        # Center the dialog
        backup_dialog.update_idletasks()
        width = backup_dialog.winfo_width()
        height = backup_dialog.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        backup_dialog.geometry(f'{width}x{height}+{x}+{y}')

    def select_backup_to_restore(self, backup_path):
        """Confirm and perform the restore operation"""
        lml_dir = self.path_var.get().strip()
        
        # Try to get backup name from metadata
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                if "backup_metadata.json" in zipf.namelist():
                    with zipf.open("backup_metadata.json") as meta_file:
                        meta_data = json.load(meta_file)
                        backup_name = meta_data.get("name", os.path.basename(backup_path))
                else:
                    backup_name = os.path.basename(backup_path)
        except:
            backup_name = os.path.basename(backup_path)
        
        result = messagebox.askyesno(
            "Confirm Restore",
            f"This will replace all files in the LML directory with backup '{backup_name}'.\n\n"
            f"Do you want to create a backup of the current state before restoring?",
            icon="warning"
        )
        
        if result:
            # Create a backup of current state first
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.perform_backup(lml_dir, f"Pre_Restore_Backup_{timestamp}")
        
        # Confirm final restore
        final_confirm = messagebox.askyesno(
            "Final Confirmation",
            f"Ready to restore from backup '{backup_name}'.\n\n"
            f"This will overwrite all files in:\n{lml_dir}\n\n"
            f"Continue with restore?",
            icon="warning"
        )
        
        if not final_confirm:
            return
        
        # Show progress dialog
        progress_window = tk.Toplevel(self)
        progress_window.title("Restoring Backup")
        progress_window.geometry("400x150")
        progress_window.transient(self)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text="Restoring from backup...", font=('Segoe UI', 12)).pack(pady=(20, 10))
        progress = ttk.Progressbar(progress_window, mode='indeterminate')
        progress.pack(fill='x', padx=20)
        progress.start()
        
        status_var = tk.StringVar(value="Removing existing files...")
        ttk.Label(progress_window, textvariable=status_var).pack(pady=10)
        
        # Update UI
        progress_window.update()
        
        # Restore in background thread
        def restore_thread():
            try:
                # Remove existing files
                for item in os.listdir(lml_dir):
                    item_path = os.path.join(lml_dir, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
                
                # Extract backup
                self.after(0, lambda: status_var.set("Extracting backup files..."))
                with zipfile.ZipFile(backup_path, "r") as zipf:
                    # Filter out metadata file
                    file_list = [f for f in zipf.namelist() if f != "backup_metadata.json"]
                    zipf.extractall(lml_dir, members=file_list)
                
                self.after(0, lambda: progress_window.destroy())
                self.after(0, lambda: messagebox.showinfo("Restore Complete", f"LML folder has been restored from backup '{backup_name}'."))
                
            except Exception as e:
                self.after(0, lambda: progress_window.destroy())
                self.after(0, lambda: messagebox.showerror("Restore Error", f"Failed to restore backup: {str(e)}"))
        
        threading.Thread(target=restore_thread, daemon=True).start()


            
    def copy_to_clipboard(self):
        if not self.conflicts:
            messagebox.showinfo("No Data", "No conflict data to export to clipboard.")
            return
        
        clipboard_text = "RDR2 LML Mod Conflict Report\n"
        clipboard_text += "=" * 40 + "\n\n"
        clipboard_text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        clipboard_text += f"LML Directory: {self.path_var.get()}\n\n"
        
        active_conflicts = {path: mods for path, mods in self.conflicts.items() if path not in self.excluded_files}
        clipboard_text += f"Total Conflicts: {len(active_conflicts)}\n"
        clipboard_text += f"Excluded Files: {len(self.excluded_files)}\n\n"
        
        clipboard_text += "ACTIVE CONFLICTS:\n"
        clipboard_text += "-" * 40 + "\n\n"
        
        for path, mods in sorted(active_conflicts.items()):
            severity = self.get_conflict_severity(path, mods)
            clipboard_text += f"File: {path}\n"
            clipboard_text += f"Severity: {severity}\n"
            clipboard_text += f"Conflicting Mods ({len(mods)}):\n"
            for mod in sorted(mods):
                clipboard_text += f"  - {mod}\n"
            clipboard_text += "\n"
            
        if self.excluded_files:
            clipboard_text += "EXCLUDED FILES:\n"
            clipboard_text += "-" * 40 + "\n\n"
            
            for path in sorted(self.excluded_files):
                if path in self.conflicts:
                    mods = self.conflicts[path]
                    severity = self.get_conflict_severity(path, mods)
                    clipboard_text += f"File: {path}\n"
                    clipboard_text += f"Severity: {severity}\n"
                    clipboard_text += f"Conflicting Mods ({len(mods)}):\n"
                    for mod in sorted(mods):
                        clipboard_text += f"  - {mod}\n"
                    clipboard_text += "\n"
        
        self.clipboard_clear()
        self.clipboard_append(clipboard_text)
        messagebox.showinfo("Success", "Conflict data copied to clipboard.")
        
    def export_to_txt(self):
        if not self.conflicts:
            messagebox.showinfo("No Data", "No conflict data to export.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Export Conflicts as Text"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("RDR2 LML Mod Conflict Report\n")
                f.write("=" * 40 + "\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"LML Directory: {self.path_var.get()}\n\n")
                
                active_conflicts = {path: mods for path, mods in self.conflicts.items() if path not in self.excluded_files}
                f.write(f"Total Conflicts: {len(active_conflicts)}\n")
                f.write(f"Excluded Files: {len(self.excluded_files)}\n\n")
                
                f.write("ACTIVE CONFLICTS:\n")
                f.write("-" * 40 + "\n\n")
                
                for path, mods in sorted(active_conflicts.items()):
                    severity = self.get_conflict_severity(path, mods)
                    f.write(f"File: {path}\n")
                    f.write(f"Severity: {severity}\n")
                    f.write(f"Conflicting Mods ({len(mods)}):\n")
                    for mod in sorted(mods):
                        f.write(f"  - {mod}\n")
                    f.write("\n")
                    
                if self.excluded_files:
                    f.write("EXCLUDED FILES:\n")
                    f.write("-" * 40 + "\n\n")
                    
                    for path in sorted(self.excluded_files):
                        if path in self.conflicts:
                            mods = self.conflicts[path]
                            severity = self.get_conflict_severity(path, mods)
                            f.write(f"File: {path}\n")
                            f.write(f"Severity: {severity}\n")
                            f.write(f"Conflicting Mods ({len(mods)}):\n")
                            for mod in sorted(mods):
                                f.write(f"  - {mod}\n")
                            f.write("\n")
                    
            messagebox.showinfo("Export Complete", f"Conflict data exported to:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export text: {str(e)}")
            
    def export_to_json(self):
        if not self.conflicts:
            messagebox.showinfo("No Data", "No conflict data to export.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Export Conflicts as JSON"
        )
        
        if not file_path:
            return
            
        try:
            active_conflicts = {path: mods for path, mods in self.conflicts.items() if path not in self.excluded_files}
            
            json_data = {
                "metadata": {
                    "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "lml_directory": self.path_var.get(),
                    "total_conflicts": len(active_conflicts),
                    "excluded_files": len(self.excluded_files)
                },
                "active_conflicts": {},
                "excluded_files": {}
            }
            
            for path, mods in active_conflicts.items():
                severity = self.get_conflict_severity(path, mods)
                json_data["active_conflicts"][path] = {
                    "mods": list(mods),
                    "count": len(mods),
                    "severity": severity
                }
                
            for path in self.excluded_files:
                if path in self.conflicts:
                    mods = self.conflicts[path]
                    severity = self.get_conflict_severity(path, mods)
                    json_data["excluded_files"][path] = {
                        "mods": list(mods),
                        "count": len(mods),
                        "severity": severity
                    }
                
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=4)
                
            messagebox.showinfo("Export Complete", f"Conflict data exported to:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export JSON: {str(e)}")
            
    def export_to_html(self):
        if not self.conflicts:
            messagebox.showinfo("No Data", "No conflict data to export.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")],
            title="Export Conflicts as HTML"
        )
        
        if not file_path:
            return
            
        try:
            html_content = self.generate_html_report()
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
                
            result = messagebox.askyesno("Export Complete", 
                                    f"HTML report exported to:\n{file_path}\n\nOpen in browser?")
            if result:
                webbrowser.open(f"file://{os.path.abspath(file_path)}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export HTML: {str(e)}")
            
    def generate_html_report(self):
        active_conflicts = {path: mods for path, mods in self.conflicts.items() if path not in self.excluded_files}
        
        severity_counts = {"High": 0, "Medium": 0, "Low": 0}
        type_groups = defaultdict(list)
        excluded_type_groups = defaultdict(list)
        
        ytd_count = sum(1 for path in active_conflicts if path.endswith('.ytd'))
        ydd_count = sum(1 for path in active_conflicts if path.endswith('.ydd'))
        meta_count = sum(1 for path in active_conflicts if path.endswith('.meta'))
        gxt2_count = sum(1 for path in active_conflicts if path.endswith('.gxt2'))
        
        for path, mods in active_conflicts.items():
            severity = self.get_conflict_severity(path, mods)
            severity_counts[severity] += 1
            
            ext = os.path.splitext(path)[1] or "No Extension"
            type_groups[ext].append((path, mods, severity))
            
        for path in self.excluded_files:
            if path in self.conflicts:
                mods = self.conflicts[path]
                severity = self.get_conflict_severity(path, mods)
                
                ext = os.path.splitext(path)[1] or "No Extension"
                excluded_type_groups[ext].append((path, mods, severity))
            
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RDR2 LML Mod Conflict Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        h1, h2 {{
            color: #333;
            border-bottom: 3px solid #4a9eff;
            padding-bottom: 10px;
        }}
        h1 {{
            text-align: center;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #4a9eff;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .summary-card .number {{
            font-size: 2em;
            font-weight: bold;
            color: #4a9eff;
        }}
        .file-type-section {{
            margin: 30px 0;
        }}
        .file-type-header {{
            background: #4a9eff;
            color: white;
            padding: 15px;
            border-radius: 8px 8px 0 0;
            cursor: pointer;
            user-select: none;
        }}
        .file-type-content {{
            border: 1px solid #ddd;
            border-top: none;
            border-radius: 0 0 8px 8px;
        }}
        .conflict-item {{
            padding: 15px;
            border-bottom: 1px solid #eee;
        }}
        .conflict-item:last-child {{
            border-bottom: none;
        }}
        .file-path {{
            font-weight: bold;
            color: #333;
            margin-bottom: 8px;
        }}
        .severity {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            margin-bottom: 8px;
        }}
        .severity-high {{
        background: #ff4757;
        color: white;
        }}
        .severity-medium {{
            background: #ffa502;
            color: white;
        }}
        .severity-low {{
            background: #2ed573;
            color: white;
        }}
        .mod-list {{
            margin-left: 20px;
        }}
        .mod-item {{
            color: #666;
            margin: 2px 0;
        }}
        .collapsible-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }}
        .collapsible-content.active {{
            max-height: 2000px;
        }}
        .toggle-icon {{
            float: right;
            transition: transform 0.3s ease;
        }}
        .toggle-icon.rotated {{
            transform: rotate(180deg);
        }}
        .special-types {{
            display: flex;
            justify-content: space-between;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        .special-type {{
            background: #e9f5ff;
            padding: 15px;
            border-radius: 8px;
            flex: 1;
            margin: 0 10px 10px 0;
            min-width: 200px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        .special-type h4 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .special-type .count {{
            font-size: 1.5em;
            font-weight: bold;
            color: #4a9eff;
        }}
        .warning-box {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .warning-box h4 {{
            color: #856404;
            margin-top: 0;
        }}
        .tab-buttons {{
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid #ddd;
        }}
        .tab-button {{
            padding: 10px 20px;
            background: #f8f9fa;
            border: 1px solid #ddd;
            border-bottom: none;
            border-radius: 5px 5px 0 0;
            margin-right: 5px;
            cursor: pointer;
        }}
        .tab-button.active {{
            background: #4a9eff;
            color: white;
            border-color: #4a9eff;
        }}
        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>RDR2 LML Mod Conflict Report</h1>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Active Conflicts</h3>
                <div class="number">{len(active_conflicts)}</div>
            </div>
            <div class="summary-card">
                <h3>Excluded Files</h3>
                <div class="number">{len(self.excluded_files)}</div>
            </div>
            <div class="summary-card">
                <h3>High Severity</h3>
                <div class="number">{severity_counts['High']}</div>
            </div>
            <div class="summary-card">
                <h3>Medium Severity</h3>
                <div class="number">{severity_counts['Medium']}</div>
            </div>
        </div>
        
        <div class="special-types">
            <div class="special-type">
                <h4>Texture Conflicts (.ytd)</h4>
                <div class="count">{ytd_count}</div>
            </div>
            <div class="special-type">
                <h4>Drawable Conflicts (.ydd)</h4>
                <div class="count">{ydd_count}</div>
            </div>
            <div class="special-type">
                <h4>Metadata Conflicts (.meta)</h4>
                <div class="count">{meta_count}</div>
            </div>
            <div class="special-type">
                <h4>GXT2 Conflicts</h4>
                <div class="count">{gxt2_count}</div>
            </div>
        </div>
        
        {f'''
        <div class="warning-box">
            <h4>Warning about GXT2 Files</h4>
            <p>GXT2 files typically do not conflict and may result in false positives. Modify only if you understand what you're doing.</p>
        </div>
        ''' if gxt2_count > 0 else ''}
        
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>LML Directory:</strong> {self.path_var.get()}</p>
        
        <div class="tab-buttons">
            <div class="tab-button active" onclick="showTab('active-conflicts')">Active Conflicts</div>
            <div class="tab-button" onclick="showTab('excluded-files')">Excluded Files</div>
        </div>
        
        <div id="active-conflicts" class="tab-content active">
            <h2>Active Conflicts</h2>
"""
        
        for ext, conflicts in sorted(type_groups.items()):
            section_id = ext.replace('.', 'dot')
            html += f"""
            <div class="file-type-section">
                <div class="file-type-header" onclick="toggleSection('active-{section_id}')">
                    <span>{ext} Files ({len(conflicts)} conflicts)</span>
                    <span class="toggle-icon" id="icon-active-{section_id}">▼</span>
                </div>
                <div class="file-type-content">
                    <div class="collapsible-content" id="content-active-{section_id}">
"""
            
            for path, mods, severity in sorted(conflicts):
                severity_class = f"severity-{severity.lower()}"
                html += f"""
                        <div class="conflict-item">
                            <div class="file-path">{path}</div>
                            <span class="severity {severity_class}">{severity} Severity</span>
                            <div class="mod-list">
                                <strong>Conflicting Mods ({len(mods)}):</strong>
"""
                for mod in mods:
                    html += f'                                <div class="mod-item">• {mod}</div>\n'
                    
                html += """
                            </div>
                        </div>
"""
            
            html += """
                    </div>
                </div>
            </div>
"""
        
        html += """
        </div>
        
        <div id="excluded-files" class="tab-content">
            <h2>Excluded Files</h2>
"""
        
        if not self.excluded_files:
            html += """
            <p>No files have been excluded.</p>
"""
        else:
            for ext, conflicts in sorted(excluded_type_groups.items()):
                section_id = ext.replace('.', 'dot')
                html += f"""
                <div class="file-type-section">
                    <div class="file-type-header" onclick="toggleSection('excluded-{section_id}')">
                        <span>{ext} Files ({len(conflicts)} excluded)</span>
                        <span class="toggle-icon" id="icon-excluded-{section_id}">▼</span>
                    </div>
                    <div class="file-type-content">
                        <div class="collapsible-content" id="content-excluded-{section_id}">
"""
                
                for path, mods, severity in sorted(conflicts):
                    severity_class = f"severity-{severity.lower()}"
                    html += f"""
                            <div class="conflict-item">
                                <div class="file-path">{path}</div>
                                <span class="severity {severity_class}">{severity} Severity</span>
                                <div class="mod-list">
                                    <strong>Conflicting Mods ({len(mods)}):</strong>
"""
                    for mod in mods:
                        html += f'                                    <div class="mod-item">• {mod}</div>\n'
                        
                    html += """
                                </div>
                            </div>
"""
                
                html += """
                        </div>
                    </div>
                </div>
"""
        
        html += """
        </div>
    </div>
    
    <script>
        function toggleSection(sectionId) {
            const content = document.getElementById('content-' + sectionId);
            const icon = document.getElementById('icon-' + sectionId);
            
            if (content.classList.contains('active')) {
                content.classList.remove('active');
                icon.classList.remove('rotated');
            } else {
                content.classList.add('active');
                icon.classList.add('rotated');
            }
        }
        
        function showTab(tabId) {
            const tabContents = document.getElementsByClassName('tab-content');
            for (let i = 0; i < tabContents.length; i++) {
                tabContents[i].classList.remove('active');
            }
            
            const tabButtons = document.getElementsByClassName('tab-button');
            for (let i = 0; i < tabButtons.length; i++) {
                tabButtons[i].classList.remove('active');
            }
            
            document.getElementById(tabId).classList.add('active');
            
            const clickedButton = event.target;
            clickedButton.classList.add('active');
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            const contents = document.querySelectorAll('.collapsible-content');
            const icons = document.querySelectorAll('.toggle-icon');
            
            contents.forEach(content => content.classList.add('active'));
            icons.forEach(icon => icon.classList.add('rotated'));
        });
    </script>
</body>
</html>
"""
        
        return html

if __name__ == '__main__':
    app = ModConflictChecker()
    app.mainloop()