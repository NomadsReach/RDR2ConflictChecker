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

class ModernConflictChecker(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("RDR2 LML Mod Conflict Checker")
        self.geometry("1400x900")
        self.minsize(1000, 700)
        
        self.path_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="All")
        self.conflicts = {}
        self.is_scanning = False
        self.dark_mode = True
        self.mod_colors = {}
        self.backup_folder = None
        
        self.center_window()
        
        self.setup_theme()
        
        self.create_header()
        self.create_controls()
        self.create_results_section()
        self.create_summary_panel()
        
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_theme(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        if self.dark_mode:
            self.colors = {
                'bg_dark': '#1a1a1a',
                'bg_medium': '#2d2d2d',
                'bg_light': '#3d3d3d',
                'accent': '#4a9eff',
                'accent_hover': '#66b3ff',
                'text_primary': '#ffffff',
                'text_secondary': '#cccccc',
                'text_muted': '#888888',
                'danger': '#ff4757',
                'warning': '#ffa502',
                'success': '#2ed573',
                'border': '#404040'
            }
        else:
            self.colors = {
                'bg_dark': '#f0f0f0',
                'bg_medium': '#ffffff',
                'bg_light': '#fafafa',
                'accent': '#0078d4',
                'accent_hover': '#106ebe',
                'text_primary': '#000000',
                'text_secondary': '#333333',
                'text_muted': '#666666',
                'danger': '#d13438',
                'warning': '#ff8c00',
                'success': '#107c10',
                'border': '#d1d1d1'
            }
        
        self.configure(bg=self.colors['bg_dark'])
        self.apply_styles()
        
    def apply_styles(self):
        self.style.configure('Modern.TFrame', 
                           background=self.colors['bg_medium'],
                           relief='flat',
                           borderwidth=0)
                           
        self.style.configure('Header.TFrame',
                           background=self.colors['bg_dark'],
                           relief='flat')
                           
        self.style.configure('Modern.TLabel',
                           background=self.colors['bg_medium'],
                           foreground=self.colors['text_primary'],
                           font=('Segoe UI', 10))
                           
        self.style.configure('Header.TLabel',
                           background=self.colors['bg_dark'],
                           foreground=self.colors['text_primary'],
                           font=('Segoe UI', 18, 'bold'))
                           
        self.style.configure('Subtitle.TLabel',
                           background=self.colors['bg_dark'],
                           foreground=self.colors['text_secondary'],
                           font=('Segoe UI', 10))
                           
        self.style.configure('Modern.TEntry',
                           fieldbackground=self.colors['bg_light'],
                           borderwidth=2,
                           relief='flat',
                           foreground=self.colors['text_primary'],
                           insertcolor=self.colors['text_primary'])
                           
        self.style.configure('Modern.TButton',
                           background=self.colors['accent'],
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           font=('Segoe UI', 9, 'bold'))
                           
        self.style.map('Modern.TButton',
                      background=[('active', self.colors['accent_hover']),
                                ('pressed', self.colors['accent'])])
                                
        self.style.configure('Success.TButton',
                           background=self.colors['success'],
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           font=('Segoe UI', 9, 'bold'))
                           
        self.style.configure('Warning.TButton',
                           background=self.colors['warning'],
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           font=('Segoe UI', 9, 'bold'))
                           
        self.style.configure('Danger.TButton',
                           background=self.colors['danger'],
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           font=('Segoe UI', 9, 'bold'))
                           
        self.style.configure('Modern.TCombobox',
                           fieldbackground=self.colors['bg_light'],
                           background=self.colors['bg_light'],
                           foreground=self.colors['text_primary'],
                           arrowcolor=self.colors['text_primary'],
                           borderwidth=2,
                           relief='flat')
                           
        self.style.configure('Modern.Treeview',
                           background=self.colors['bg_light'],
                           foreground=self.colors['text_primary'],
                           fieldbackground=self.colors['bg_light'],
                           borderwidth=0,
                           font=('Segoe UI', 9))
                           
        self.style.configure('Modern.Treeview.Heading',
                           background=self.colors['bg_medium'],
                           foreground=self.colors['text_primary'],
                           borderwidth=1,
                           relief='flat',
                           font=('Segoe UI', 10, 'bold'))
                           
        self.style.map('Modern.Treeview',
                      background=[('selected', self.colors['accent'])])
                      
        self.style.configure('Modern.Vertical.TScrollbar',
                           background=self.colors['bg_medium'],
                           troughcolor=self.colors['bg_light'],
                           borderwidth=0,
                           arrowcolor=self.colors['text_muted'])
                           
        self.style.configure('Modern.Horizontal.TScrollbar',
                           background=self.colors['bg_medium'],
                           troughcolor=self.colors['bg_light'],
                           borderwidth=0,
                           arrowcolor=self.colors['text_muted'])
    
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.setup_theme()
        self.update_tree()
        
    def create_header(self):
        header_frame = ttk.Frame(self, style='Header.TFrame', padding=30)
        header_frame.pack(fill='x')
        
        title_row = ttk.Frame(header_frame, style='Header.TFrame')
        title_row.pack(fill='x')
        
        title_label = ttk.Label(title_row, 
                               text="RDR2 LML Mod Conflict Checker",
                               style='Header.TLabel')
        title_label.pack(side='left')
        
        theme_btn = ttk.Button(title_row,
                              text="🌙" if self.dark_mode else "☀️",
                              command=self.toggle_theme,
                              style='Modern.TButton',
                              width=3)
        theme_btn.pack(side='right')
        
        subtitle_label = ttk.Label(header_frame,
                                 text="Detect file conflicts between your installed mods",
                                 style='Subtitle.TLabel')
        subtitle_label.pack(pady=(5, 0))
        
    def create_controls(self):
        controls_frame = ttk.Frame(self, style='Modern.TFrame', padding=20)
        controls_frame.pack(fill='x', padx=20, pady=10)
        
        path_row = ttk.Frame(controls_frame, style='Modern.TFrame')
        path_row.pack(fill='x', pady=(0, 15))
        
        ttk.Label(path_row, text="LML Folder:", style='Modern.TLabel').pack(side='left')
        
        path_entry_frame = ttk.Frame(path_row, style='Modern.TFrame')
        path_entry_frame.pack(side='left', fill='x', expand=True, padx=(10, 0))
        
        self.path_entry = ttk.Entry(path_entry_frame, 
                                   textvariable=self.path_var,
                                   style='Modern.TEntry',
                                   font=('Segoe UI', 10))
        self.path_entry.pack(side='left', fill='x', expand=True)
        
        ttk.Button(path_row, 
                  text="Browse",
                  style='Modern.TButton',
                  command=self.browse_folder).pack(side='right', padx=(10, 0))
        
        filter_row = ttk.Frame(controls_frame, style='Modern.TFrame')
        filter_row.pack(fill='x', pady=(0, 15))
        
        search_frame = ttk.Frame(filter_row, style='Modern.TFrame')
        search_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(search_frame, text="Search:", style='Modern.TLabel').pack(side='left')
        search_entry = ttk.Entry(search_frame, 
                               textvariable=self.search_var,
                               style='Modern.TEntry',
                               font=('Segoe UI', 10))
        search_entry.pack(side='left', fill='x', expand=True, padx=(10, 0))
        search_entry.bind("<KeyRelease>", lambda e: self.update_tree())
        
        filter_frame = ttk.Frame(filter_row, style='Modern.TFrame')
        filter_frame.pack(side='right', padx=(20, 0))
        
        ttk.Label(filter_frame, text="Filter:", style='Modern.TLabel').pack(side='left')
        filter_combo = ttk.Combobox(filter_frame,
                                  textvariable=self.filter_var,
                                  values=["All", "High Severity", "Medium Severity", "Low Severity", 
                                         ".meta", ".xml", ".ytd", ".ymt", ".ydd", ".dat"],
                                  state="readonly",
                                  style='Modern.TCombobox',
                                  width=15)
        filter_combo.pack(side='left', padx=(10, 0))
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self.update_tree())
        
        action_row = ttk.Frame(controls_frame, style='Modern.TFrame')
        action_row.pack(fill='x')
        
        left_buttons = ttk.Frame(action_row, style='Modern.TFrame')
        left_buttons.pack(side='left')
        
        self.scan_btn = ttk.Button(left_buttons,
                                  text="Scan for Conflicts",
                                  style='Modern.TButton',
                                  command=self.scan_conflicts_threaded)
        self.scan_btn.pack(side='left')
        
        self.backup_btn = ttk.Button(left_buttons,
                                   text="Create Backup",
                                   style='Warning.TButton',
                                   command=self.create_backup)
        self.backup_btn.pack(side='left', padx=(10, 0))
        
        self.restore_btn = ttk.Button(left_buttons,
                                    text="Restore Backup",
                                    style='Danger.TButton',
                                    command=self.restore_backup,
                                    state='disabled')
        self.restore_btn.pack(side='left', padx=(10, 0))
        
        right_buttons = ttk.Frame(action_row, style='Modern.TFrame')
        right_buttons.pack(side='right')
        
        self.copy_btn = ttk.Button(right_buttons,
                                 text="Copy to Clipboard",
                                 style='Modern.TButton',
                                 command=self.copy_to_clipboard)
        self.copy_btn.pack(side='right')
        
        self.export_json_btn = ttk.Button(right_buttons,
                                        text="Export JSON",
                                        style='Success.TButton',
                                        command=self.export_to_json)
        self.export_json_btn.pack(side='right', padx=(0, 10))
        
        self.export_html_btn = ttk.Button(right_buttons,
                                        text="Export HTML",
                                        style='Success.TButton',
                                        command=self.export_to_html)
        self.export_html_btn.pack(side='right', padx=(0, 10))
        
        self.export_btn = ttk.Button(right_buttons,
                                   text="Export TXT",
                                   style='Success.TButton',
                                   command=self.export_to_txt)
        self.export_btn.pack(side='right', padx=(0, 10))
        
    def create_results_section(self):
        main_paned = ttk.PanedWindow(self, orient='horizontal')
        main_paned.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        left_frame = ttk.Frame(main_paned, style='Modern.TFrame', padding=10)
        main_paned.add(left_frame, weight=1)
        
        ttk.Label(left_frame, 
                 text="Conflicts by File Type",
                 style='Modern.TLabel',
                 font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        self.type_tree = ttk.Treeview(left_frame, style='Modern.Treeview', height=15)
        self.type_tree.heading("#0", text="File Types")
        self.type_tree.bind("<<TreeviewSelect>>", self.on_type_select)
        
        type_scroll = ttk.Scrollbar(left_frame, orient="vertical", command=self.type_tree.yview)
        self.type_tree.configure(yscrollcommand=type_scroll.set)
        
        self.type_tree.pack(side='left', fill='both', expand=True)
        type_scroll.pack(side='right', fill='y')
        
        right_frame = ttk.Frame(main_paned, style='Modern.TFrame', padding=10)
        main_paned.add(right_frame, weight=2)
        
        results_header = ttk.Frame(right_frame, style='Modern.TFrame')
        results_header.pack(fill='x', pady=(0, 10))
        
        ttk.Label(results_header, 
                 text="Detailed Conflicts",
                 style='Modern.TLabel',
                 font=('Segoe UI', 12, 'bold')).pack(side='left')
        
        self.results_count = ttk.Label(results_header,
                                     text="0 conflicts found",
                                     style='Modern.TLabel')
        self.results_count.pack(side='right')
        
        tree_frame = ttk.Frame(right_frame, style='Modern.TFrame')
        tree_frame.pack(fill='both', expand=True)
        
        columns = ("file", "mods", "count", "severity")
        self.tree = ttk.Treeview(tree_frame, 
                               columns=columns,
                               show="headings",
                               style='Modern.Treeview')
        
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
                                  command=self.tree.yview,
                                  style='Modern.Vertical.TScrollbar')
        h_scrollbar = ttk.Scrollbar(tree_frame,
                                  orient="horizontal", 
                                  command=self.tree.xview,
                                  style='Modern.Horizontal.TScrollbar')
        
        self.tree.configure(yscrollcommand=v_scrollbar.set,
                          xscrollcommand=h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
    def create_summary_panel(self):
        summary_frame = ttk.Frame(self, style='Modern.TFrame', padding=10)
        summary_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ttk.Label(summary_frame, 
                 text="Summary",
                 style='Modern.TLabel',
                 font=('Segoe UI', 11, 'bold')).pack(side='left')
        
        self.summary_label = ttk.Label(summary_frame,
                                     text="No scan performed yet",
                                     style='Modern.TLabel')
        self.summary_label.pack(side='left', padx=(20, 0))
        
    def sort_column(self, col):
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        
        if col == "count":
            data.sort(key=lambda x: int(x[0]) if x[0].isdigit() else 0, reverse=True)
        else:
            data.sort(key=lambda x: x[0].lower())
        
        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)
            
    def on_type_select(self, event):
        selection = self.type_tree.selection()
        if selection:
            item = selection[0]
            file_type = self.type_tree.item(item, "text")
            if file_type != "All File Types":
                self.filter_var.set(file_type)
                self.update_tree()
        
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
        
        thread = threading.Thread(target=self.scan_conflicts, args=(lml_dir,))
        thread.daemon = True
        thread.start()
        
    def scan_conflicts(self, lml_dir):
        try:
            files_map = self.gather_mod_files(lml_dir)
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
            
    def scan_complete(self):
        self.is_scanning = False
        self.scan_btn.config(text="Scan for Conflicts", state='normal')
        
        self.update_tree()
        self.update_type_tree()
        self.update_summary()
        
        if not self.conflicts:
            messagebox.showinfo("No Conflicts", "No conflicts detected in your mods!")
            
    def update_type_tree(self):
        for item in self.type_tree.get_children():
            self.type_tree.delete(item)
            
        if not self.conflicts:
            return
            
        type_groups = defaultdict(list)
        for path, mods in self.conflicts.items():
            ext = os.path.splitext(path)[1] or "No Extension"
            type_groups[ext].append((path, mods))
            
        all_item = self.type_tree.insert("", "end", text="All File Types", 
                                       values=[f"({len(self.conflicts)} conflicts)"])
        
        for ext, conflicts in sorted(type_groups.items()):
            severity_counts = {"High": 0, "Medium": 0, "Low": 0}
            for path, mods in conflicts:
                severity = self.get_conflict_severity(path, mods)
                severity_counts[severity] += 1
                
            parent = self.type_tree.insert("", "end", text=ext, 
                                         values=[f"({len(conflicts)} conflicts)"])
            
            for severity, count in severity_counts.items():
                if count > 0:
                    self.type_tree.insert(parent, "end", text=f"{severity} Severity", 
                                        values=[f"({count} conflicts)"])
        
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
            
        total_conflicts = len(self.conflicts)
        affected_mods = len(set(mod for mods in self.conflicts.values() for mod in mods))
        
        high_severity = sum(1 for path, mods in self.conflicts.items() 
                           if self.get_conflict_severity(path, mods) == "High")
        
        texture_conflicts = sum(1 for path in self.conflicts if path.endswith('.ytd'))
        
        summary_text = f"Total: {total_conflicts} conflicts | Affected mods: {affected_mods} | High severity: {high_severity} | Texture conflicts: {texture_conflicts}"
        self.summary_label.config(text=summary_text)
        
    def gather_mod_files(self, mods_dir):
        files_map = defaultdict(list)
        
        for mod_name in sorted(os.listdir(mods_dir)):
            mod_path = os.path.join(mods_dir, mod_name)
            if not os.path.isdir(mod_path):
                continue
                
            for root, _, files in os.walk(mod_path):
                for fname in files:
                    rel_root = os.path.relpath(root, mod_path)
                    rel_path = fname if rel_root == '.' else os.path.join(rel_root, fname)
                    files_map[rel_path].append(mod_name)
                    
        return files_map
        
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
            if search_term:
                if (search_term not in path.lower() and 
                    not any(search_term in m.lower() for m in mods)):
                    continue
                    
            severity = self.get_conflict_severity(path, mods)
            ext = os.path.splitext(path)[1]
            
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
            
        for path, mods, severity in filtered_conflicts:
            count = len(mods)
            
            colored_mods = []
            for mod in mods:
                colored_mods.append(mod)
                
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
                
            self.tree.item(item_id, tags=tags)
                           
        if self.dark_mode:
            self.tree.tag_configure('low_conflict', background='#2d4a2d')
            self.tree.tag_configure('medium_conflict', background='#4a3d2d')
            self.tree.tag_configure('high_conflict', background='#4a2d2d')
        else:
            self.tree.tag_configure('low_conflict', background='#e8f5e8')
            self.tree.tag_configure('medium_conflict', background='#fff3cd')
            self.tree.tag_configure('high_conflict', background='#f8d7da')
        
        self.results_count.config(text=f"{len(filtered_conflicts)} conflicts found")
        
    def create_backup(self):
        lml_dir = self.path_var.get().strip()
        if not os.path.isdir(lml_dir):
            messagebox.showerror("Error", "Please select a valid LML directory first.")
            return
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"LML_Backup_{timestamp}.zip"
            backup_path = filedialog.asksaveasfilename(
                defaultextension=".zip",
                filetypes=[("ZIP files", "*.zip")],
                initialfile=backup_name,
                title="Save Backup As"
            )
            
            if not backup_path:
                return
                
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(lml_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, lml_dir)
                        zipf.write(file_path, arc_name)
                        
            self.backup_folder = backup_path
            self.restore_btn.config(state='normal')
            
            messagebox.showinfo("Backup Complete", f"Backup created successfully:\n{backup_path}")
            
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to create backup: {str(e)}")
            
    def restore_backup(self):
        if not self.backup_folder or not os.path.exists(self.backup_folder):
            backup_file = filedialog.askopenfilename(
                filetypes=[("ZIP files", "*.zip")],
                title="Select Backup File"
            )
            if not backup_file:
                return
            self.backup_folder = backup_file
            
        lml_dir = self.path_var.get().strip()
        if not os.path.isdir(lml_dir):
            messagebox.showerror("Error", "Please select a valid LML directory first.")
            return
            
        result = messagebox.askyesno("Confirm Restore",
                                   "This will replace all files in the LML directory with the backup. Continue?",
                                   icon='warning')
        if not result:
            return
            
        try:
            for item in os.listdir(lml_dir):
                item_path = os.path.join(lml_dir, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                    
            with zipfile.ZipFile(self.backup_folder, 'r') as zipf:
                zipf.extractall(lml_dir)
                
            messagebox.showinfo("Restore Complete", "LML folder has been restored from backup.")
            
        except Exception as e:
            messagebox.showerror("Restore Error", f"Failed to restore backup: {str(e)}")
            
    def copy_to_clipboard(self):
        if not self.conflicts:
            messagebox.showinfo("No Data", "No conflict data to copy.")
            return
            
        try:
            clipboard_text = "RDR2 LML Mod Conflicts\n" + "="*30 + "\n\n"
            
            for item in self.tree.get_children():
                values = self.tree.item(item, 'values')
                file_path, mods, count, severity = values
                clipboard_text += f"File: {file_path}\n"
                clipboard_text += f"Severity: {severity}\n"
                clipboard_text += f"Conflicting Mods ({count}):\n"
                for mod in mods.split(", "):
                    clipboard_text += f"  • {mod}\n"
                clipboard_text += "\n"
                
            self.clipboard_clear()
            self.clipboard_append(clipboard_text)
            messagebox.showinfo("Copied", "Conflict data copied to clipboard!")
            
        except Exception as e:
            messagebox.showerror("Copy Error", f"Failed to copy to clipboard: {str(e)}")
            
    def export_to_txt(self):
        if not self.conflicts:
            messagebox.showinfo("No Data", "No conflict data to export.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Export Conflicts as TXT"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("RDR2 LML Mod Conflict Report\n")
                f.write("=" * 40 + "\n\n")
                f.write(f"Generated: {self.get_timestamp()}\n")
                f.write(f"Total conflicts found: {len(self.conflicts)}\n")
                
                severity_counts = {"High": 0, "Medium": 0, "Low": 0}
                for path, mods in self.conflicts.items():
                    severity = self.get_conflict_severity(path, mods)
                    severity_counts[severity] += 1
                    
                f.write(f"High severity: {severity_counts['High']}\n")
                f.write(f"Medium severity: {severity_counts['Medium']}\n")
                f.write(f"Low severity: {severity_counts['Low']}\n\n")
                
                ytd_count = sum(1 for path in self.conflicts if path.endswith('.ytd'))
                ydd_count = sum(1 for path in self.conflicts if path.endswith('.ydd'))
                meta_count = sum(1 for path in self.conflicts if path.endswith('.meta'))
                
                f.write(f"Texture conflicts (.ytd): {ytd_count}\n")
                f.write(f"Drawable conflicts (.ydd): {ydd_count}\n")
                f.write(f"Metadata conflicts (.meta): {meta_count}\n\n")
                
                type_groups = defaultdict(list)
                for path, mods in self.conflicts.items():
                    ext = os.path.splitext(path)[1] or "No Extension"
                    type_groups[ext].append((path, mods))
                    
                for ext, conflicts in sorted(type_groups.items()):
                    f.write(f"\n{ext} Files ({len(conflicts)} conflicts)\n")
                    f.write("-" * 30 + "\n")
                    
                    for path, mods in sorted(conflicts):
                        severity = self.get_conflict_severity(path, mods)
                        f.write(f"\nFile: {path}\n")
                        f.write(f"Severity: {severity}\n")
                        f.write(f"Conflicts ({len(mods)} mods):\n")
                        for mod in mods:
                            f.write(f"  • {mod}\n")
                    
            messagebox.showinfo("Export Complete", f"Conflicts exported to:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
            
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
            export_data = {
                "metadata": {
                    "generated": self.get_timestamp(),
                    "total_conflicts": len(self.conflicts),
                    "lml_directory": self.path_var.get()
                },
                "summary": {
                    "by_severity": {},
                    "by_file_type": {}
                },
                "conflicts": []
            }
            
            severity_counts = {"High": 0, "Medium": 0, "Low": 0}
            type_counts = defaultdict(int)
            
            for path, mods in self.conflicts.items():
                severity = self.get_conflict_severity(path, mods)
                severity_counts[severity] += 1
                
                ext = os.path.splitext(path)[1] or "No Extension"
                type_counts[ext] += 1
                
                export_data["conflicts"].append({
                    "file_path": path,
                    "severity": severity,
                    "mod_count": len(mods),
                    "conflicting_mods": mods,
                    "file_extension": ext
                })
                
            export_data["summary"]["by_severity"] = severity_counts
            export_data["summary"]["by_file_type"] = dict(type_counts)
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
                
            messagebox.showinfo("Export Complete", f"Conflicts exported to:\n{file_path}")
            
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
        severity_counts = {"High": 0, "Medium": 0, "Low": 0}
        type_groups = defaultdict(list)
        
        ytd_count = sum(1 for path in self.conflicts if path.endswith('.ytd'))
        ydd_count = sum(1 for path in self.conflicts if path.endswith('.ydd'))
        meta_count = sum(1 for path in self.conflicts if path.endswith('.meta'))
        
        for path, mods in self.conflicts.items():
            severity = self.get_conflict_severity(path, mods)
            severity_counts[severity] += 1
            
            ext = os.path.splitext(path)[1] or "No Extension"
            type_groups[ext].append((path, mods, severity))
            
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
        h1 {{
            color: #333;
            text-align: center;
            border-bottom: 3px solid #4a9eff;
            padding-bottom: 10px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minwidth(200px, 1fr));
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
    </style>
</head>
<body>
    <div class="container">
        <h1>RDR2 LML Mod Conflict Report</h1>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Total Conflicts</h3>
                <div class="number">{len(self.conflicts)}</div>
            </div>
            <div class="summary-card">
                <h3>High Severity</h3>
                <div class="number">{severity_counts['High']}</div>
            </div>
            <div class="summary-card">
                <h3>Medium Severity</h3>
                <div class="number">{severity_counts['Medium']}</div>
            </div>
            <div class="summary-card">
                <h3>Low Severity</h3>
                <div class="number">{severity_counts['Low']}</div>
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
        </div>
        
        <p><strong>Generated:</strong> {self.get_timestamp()}</p>
        <p><strong>LML Directory:</strong> {self.path_var.get()}</p>
"""
        
        for ext, conflicts in sorted(type_groups.items()):
            section_id = ext.replace('.', 'dot')
            html += f"""
        <div class="file-type-section">
            <div class="file-type-header" onclick="toggleSection('{section_id}')">
                <span>{ext} Files ({len(conflicts)} conflicts)</span>
                <span class="toggle-icon" id="icon-{section_id}">▼</span>
            </div>
            <div class="file-type-content">
                <div class="collapsible-content" id="content-{section_id}">
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
                    html += f'                            <div class="mod-item">• {mod}</div>\n'
                    
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
        
    def get_timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == '__main__':
    app = ModernConflictChecker()
    app.mainloop()    
