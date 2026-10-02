"""
Largest File Finder
------------------
A modern, responsive Windows desktop utility to scan, analyze, and manage disk-hogging files.

Author: ByteWhisker (https://github.com/bytewhisker)
License: MIT
Version: 1.0.0
"""

import os
import subprocess
import pyperclip
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font as tkFont
import threading
import queue

class LargestFileFinderApp(tk.Tk):
    """
    A Tkinter-based GUI app to scan, display, and manage the largest files in a selected folder.
    """
    def __init__(self):
        super().__init__()
        self.title("Largest File Finder")
        self.geometry("700x739")
        self.minsize(600, 400)
        self.configure(bg="#2E2E2E")
        # Set window icon using relative path to file location
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon128.ico")
            self.iconbitmap(icon_path)
        except Exception:
            pass
        self.version = "v1.0.0"
        self.developer = "Developed by ByteWhisker"
        self._setup_styles()
        self._setup_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TButton', font=('Segoe UI', 12), background="#1E1E1E", foreground="#FFFFFF", padding=8, relief="flat")
        style.map('TButton', background=[('active', '#333333')], foreground=[('active', '#FFFFFF')])
        style.configure('TLabel', font=('Segoe UI', 12), background="#2E2E2E", foreground="#E0E0E0")
        style.configure('Treeview', background="#2E2E2E", foreground="#FFFFFF", fieldbackground="#2E2E2E", rowheight=28)
        style.configure('Treeview.Heading', font=('Segoe UI', 12, 'bold'), background="#1E1E1E", foreground="#FFFFFF", relief="flat", padding=6)
        style.map('Treeview.Heading', background=[('active', '#1E1E1E')], foreground=[('active', '#FF6600')])
        style.map('Treeview', background=[('selected', '#333333')])
        style.configure('TProgressbar', background="#FF6600")
        style.map('Treeview', background=[('!selected', '#2E2E2E'), ('selected', '#333333')])
        style.layout('Treeview', [('Treeview.treearea', {'sticky': 'nswe'})])

    def _setup_ui(self):
        # Main Frame
        main_frame = tk.Frame(self, bg="#2E2E2E")
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        for i in range(0, 12):
            main_frame.grid_rowconfigure(i, weight=0)
        main_frame.grid_rowconfigure(8, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Title with logo
        header_frame = tk.Frame(main_frame, bg="#2E2E2E")
        header_frame.grid(row=0, column=0, pady=10, sticky="ew")
        try:
            from PIL import Image, ImageTk
            logo_path = os.path.join(os.path.dirname(__file__), "assets", "icon128.png")
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((32, 32), Image.LANCZOS)
            logo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(header_frame, image=logo, bg="#2E2E2E")
            logo_label.image = logo
            logo_label.pack(side=tk.LEFT, padx=(0, 10))
        except Exception:
            logo_label = None
        header = tk.Label(header_frame, text="Largest File Finder", font=('Segoe UI', 18, 'bold'), bg="#2E2E2E", fg="#FFFFFF")
        header.pack(side=tk.LEFT)

        # Select folder and scan buttons
        self.selected_path_label = ttk.Label(main_frame, text="No folder selected", font=('Segoe UI', 12), foreground="#888888")
        self.selected_path_label.grid(row=1, column=0, pady=10, sticky="ew")

        folder_button = ttk.Button(main_frame, text="Select Folder", command=self.select_folder)
        folder_button.grid(row=2, column=0, pady=10, sticky="ew")

        scan_button = ttk.Button(main_frame, text="Start Scan", command=self.start_scan, state=tk.DISABLED)
        scan_button.grid(row=3, column=0, pady=10, sticky="ew")
        self.scan_button = scan_button

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, orient="horizontal", length=400, mode="determinate", style='TProgressbar')
        self.progress.grid(row=4, column=0, pady=(5, 2), sticky="ew")

        # Scanning label
        self.scanning_label = tk.Label(main_frame, text="", font=('Segoe UI', 11), fg="#FF6600", bg="#2E2E2E")
        self.scanning_label.grid(row=5, column=0, pady=(0, 0), sticky="ew")
        self.update_idletasks()

        # For threading
        self.scan_queue = queue.Queue()
        self.scanning = False
        self.scanning_messages = [
            "Scanning files…",
            "Crunching numbers…",
            "Hunting for the biggest files…",
            "Almost there…",
            "Finalizing results…"
        ]
        self.scanning_msg_index = 0

        # Treeview to display files
        columns = ("File Name", "Size", "Path")
        tree_frame = tk.Frame(main_frame, bg="#2E2E2E")
        tree_frame.grid(row=8, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(8, weight=1)
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8, selectmode="extended")
        self.tree.heading("File Name", text="File Name")
        self.tree.heading("Size", text="Size")
        self.tree.heading("Path", text="Full Path")
        self.tree.column("File Name", width=200)
        self.tree.column("Size", width=100, anchor=tk.CENTER)
        self.tree.column("Path", width=300)
        self.tree.grid(row=0, column=0, sticky="nsew")

        tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        tree_scroll_y.grid(row=0, column=1, sticky="ns")
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        tree_scroll_x.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Delete button
        delete_button = ttk.Button(main_frame, text="Delete File(s)", command=self.delete_selected_file, state=tk.DISABLED)
        delete_button.grid(row=6, column=0, pady=10, sticky="ew")
        self.delete_button = delete_button

        # File type filter dropdown
        self.file_types = [
            ('All', []),
            ('Video', ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm']),
            ('Audio', ['.mp3', '.wav', '.aac', '.flac', '.ogg']),
            ('Image', ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp']),
            ('Archive', ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso', '.cab']),
            ('Document', ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.md', '.rtf']),
            ('Executable', ['.exe', '.msi', '.bat', '.cmd', '.sh', '.app', '.apk']),
            ('mp4', ['.mp4']),
            ('mov', ['.mov']),
            ('zip', ['.zip']),
            ('rar', ['.rar']),
            ('exe', ['.exe']),
            ('7z', ['.7z'])
        ]
        self.selected_type = tk.StringVar(value='All')
        filter_frame = tk.Frame(main_frame, bg="#232323", highlightbackground="#444", highlightthickness=1)
        filter_frame.grid(row=6, column=0, sticky="ew", pady=(0, 2), padx=0)
        filter_frame.grid_columnconfigure(1, weight=1)
        filter_label = tk.Label(filter_frame, text="Show:", bg="#232323", fg="#E0E0E0", font=('Segoe UI', 11))
        filter_label.grid(row=0, column=0, padx=(8, 2), pady=4, sticky="w")
        type_menu = ttk.Combobox(filter_frame, textvariable=self.selected_type, values=[ft[0] for ft in self.file_types], state="readonly", width=14)
        type_menu.grid(row=0, column=1, padx=(2, 8), pady=4, sticky="w")
        type_menu.bind('<<ComboboxSelected>>', lambda e: self.update_treeview_with_filter())
        self.all_files_data = []

        # Footer with version and developer credits
        footer = tk.Frame(self, bg="#2E2E2E")
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        footer.grid_columnconfigure(0, weight=1)
        footer.grid_columnconfigure(1, weight=0)
        footer.grid_columnconfigure(2, weight=0)
        links_frame = tk.Frame(footer, bg="#2E2E2E")
        links_frame.grid(row=0, column=2, sticky="e", padx=(0, 10))
        about_link = tk.Label(links_frame, text="Developer", font=('Segoe UI', 10, 'underline'), fg="#3399FF", bg="#2E2E2E", cursor="hand2", anchor="e")
        about_link.pack(side=tk.LEFT, padx=(0, 10))
        about_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/bytewhisker"))
        donate_link = tk.Label(links_frame, text="Support", font=('Segoe UI', 10, 'underline'), fg="#33CC66", bg="#2E2E2E", cursor="hand2", anchor="e")
        donate_link.pack(side=tk.LEFT)
        donate_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/bytewhisker"))
        version_label = ttk.Label(footer, text="v1.0.0", font=('Segoe UI', 10), foreground="#888888", anchor="w")
        version_label.grid(row=0, column=0, sticky="w", padx=(10, 0))

        self.context_menu = None

    def select_folder(self):
        """Prompt the user to select a folder and enable scan."""
        path = filedialog.askdirectory(title="Select Folder or Drive")
        if path:
            self.selected_path_label.config(text=path)
            self.scan_button.config(state=tk.NORMAL)

    def start_scan(self):
        """Start scanning the selected folder for largest files."""
        path = self.selected_path_label.cget("text")
        if path == "No folder selected" or not os.path.exists(path):
            messagebox.showwarning("Warning", "Please select a folder first!")
            return
        self.progress["value"] = 0
        self.progress.config(mode="indeterminate")
        self.progress.start(10)
        self.scan_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
        self.scanning = True
        self.last_msg_index = -1
        self.scanning_label.config(text="Initializing scan…")
        self.after(500, lambda: threading.Thread(target=self.scan_and_display_largest_files_threaded, args=(path,), daemon=True).start())
        self.after(100, self.process_scan_queue)

    def update_scanning_message(self):
        if self.scanning:
            msg = self.scanning_messages[self.scanning_msg_index % len(self.scanning_messages)]
            self.scanning_label.config(text=msg)
            self.scanning_msg_index += 1
            self.after(2000, self.update_scanning_message)
        else:
            self.scanning_label.config(text="")

    def human_readable_size(self, size_bytes):
        """Convert bytes to a human-readable string."""
        if size_bytes >= 1024 ** 3:
            return f"{size_bytes / (1024 ** 3):.2f} GB"
        elif size_bytes >= 1024 ** 2:
            return f"{size_bytes / (1024 ** 2):.2f} MB"
        elif size_bytes >= 1024:
            return f"{size_bytes / 1024:.2f} KB"
        else:
            return f"{size_bytes} B"

    def get_file_type(self, filename):
        ext = os.path.splitext(filename)[1].lower()
        if ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm']:
            return 'Video'
        elif ext in ['.mp3', '.wav', '.aac', '.flac', '.ogg']:
            return 'Audio'
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp']:
            return 'Image'
        elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso', '.cab']:
            return 'Archive'
        elif ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.md', '.rtf']:
            return 'Document'
        elif ext in ['.exe', '.msi', '.bat', '.cmd', '.sh', '.app', '.apk']:
            return 'Executable'
        elif ext in ['.py', '.js', '.java', '.c', '.cpp', '.cs', '.rb', '.php', '.html', '.css', '.json', '.xml']:
            return 'Code'
        else:
            return ext[1:].upper() if ext else 'Other'

    def scan_and_display_largest_files_threaded(self, root_path):
        file_list = []
        total_files = 0
        for _, _, files in os.walk(root_path):
            total_files += len(files)
        self.scan_queue.put(("counted", total_files))
        processed_files = 0
        for dirpath, dirnames, filenames in os.walk(root_path):
            for fname in filenames:
                try:
                    fpath = os.path.join(dirpath, fname)
                    fsize = os.path.getsize(fpath)
                    file_list.append((fname, fsize, fpath))
                except Exception:
                    continue
                processed_files += 1
                if processed_files % 10 == 0 or processed_files == total_files:
                    progress = (processed_files / total_files) * 100 if total_files > 0 else 0
                    self.scan_queue.put(("progress", progress))
        file_list.sort(key=lambda x: x[1], reverse=True)
        top_files = file_list[:20]
        self.scan_queue.put(("results", top_files))
        self.scan_queue.put(("done", None))

    def process_scan_queue(self):
        while not self.scan_queue.empty():
            msg, data = self.scan_queue.get()
            if msg == "counted":
                self.progress.stop()
                self.progress.config(mode="determinate")
                self.progress["value"] = 0
                self.update_idletasks()
            elif msg == "progress":
                self.progress["value"] = data
                msg_index = 0
                if data < 30:
                    msg_index = 0
                elif data < 60:
                    msg_index = 1
                elif data < 90:
                    msg_index = 2
                elif data < 99:
                    msg_index = 3
                else:
                    msg_index = 4
                if getattr(self, 'last_msg_index', -1) != msg_index:
                    self.scanning_label.config(text=self.scanning_messages[msg_index])
                    self.last_msg_index = msg_index
                self.update_idletasks()
            elif msg == "results":
                for row in self.tree.get_children():
                    self.tree.delete(row)
                self.all_files_data = data
                self.update_treeview_with_filter()
            elif msg == "done":
                self.progress["value"] = 100
                self.scanning = False
                self.scanning_label.config(text=self.scanning_messages[-1])
                self.update_idletasks()
                self.scan_button.config(state=tk.NORMAL)
                self.delete_button.config(state=tk.NORMAL)
                self.after(1000, lambda: self.scanning_label.config(text=""))
        if self.scanning:
            self.after(100, self.process_scan_queue)

    def delete_selected_file(self):
        """Delete the selected file(s) from disk and the table."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("No File Selected", "Please select one or more files to delete.")
            return
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {len(selected_items)} file(s)?")
        if not confirm:
            return
        for selected_item in selected_items:
            file_path = self.tree.item(selected_item, 'values')[2]
            if not os.path.exists(file_path):
                messagebox.showwarning("File Not Found", f"The file at {file_path} does not exist.")
                continue
            try:
                os.remove(file_path)
                self.tree.delete(selected_item)
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete the file: {str(e)}")
        messagebox.showinfo("Files Deleted", "The selected files have been deleted.")

    def show_context_menu(self, event):
        if event.type == '4':
            item = self.tree.identify_row(event.y)
            if item:
                self.tree.selection_set(item)
            if self.context_menu:
                self.context_menu.unpost()
            self.context_menu = tk.Menu(self, tearoff=0)
            self.context_menu.add_command(label="Copy Path", command=self.copy_file_path)
            self.context_menu.add_command(label="Open Location", command=self.open_file_location)
            self.context_menu.add_command(label="Delete File(s)", command=self.delete_selected_file)
            self.context_menu.add_separator()
            self.context_menu.add_command(label="About Developer", command=self.open_developer_link)
            self.context_menu.post(event.x_root, event.y_root)

    def copy_file_path(self):
        """Copy the selected file's path to the clipboard."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No File Selected", "Please select a file to copy its path.")
            return
        file_path = self.tree.item(selected_item, 'values')[2]
        pyperclip.copy(file_path)
        messagebox.showinfo("Path Copied", "The file path has been copied to the clipboard.")

    def open_file_location(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No File Selected", "Please select a file to open its location.")
            return

        file_path = self.tree.item(selected_item, 'values')[2]
        if not os.path.exists(file_path):
            messagebox.showwarning("File Not Found", f"The file at {file_path} does not exist.")
            return

        try:
            file_path = os.path.normpath(file_path)
            subprocess.run([
                'explorer.exe',
                '/select,',
                file_path
            ], capture_output=True, text=True)
            return
        except Exception:
            try:
                escaped_path = file_path.replace('"', '""')
                os.system(f'explorer /select,"{escaped_path}"')
                return
            except Exception:
                try:
                    subprocess.Popen([
                        'C:\\Windows\\explorer.exe',
                        '/select,',
                        file_path
                    ])
                    return
                except Exception:
                    try:
                        folder_path = os.path.dirname(file_path)
                        os.startfile(folder_path)
                    except Exception as err:
                        messagebox.showerror("Error", f"Could not open file location: {str(err)}")

    def open_developer_link(self):
        """Open the developer's GitHub profile in the default browser."""
        webbrowser.open("https://github.com/bytewhisker")

    def on_close(self):
        """Handle window close event."""
        self.destroy()

    def update_treeview_with_filter(self):
        selected = self.selected_type.get()
        exts = []
        for label, extlist in self.file_types:
            if label == selected:
                exts = extlist
                break
        filtered = []
        for fname, fsize, fpath in self.all_files_data:
            ext = os.path.splitext(fname)[1].lower()
            if not exts or ext in exts:
                filtered.append((fname, fsize, fpath))
        filtered.sort(key=lambda x: x[1], reverse=True)
        for row in self.tree.get_children():
            self.tree.delete(row)
        for i, (fname, fsize, fpath) in enumerate(filtered):
            size_str = self.human_readable_size(fsize)
            tags = ('evenrow',) if i % 2 == 0 else ('oddrow',)
            self.tree.insert('', 'end', values=(fname, size_str, fpath), tags=tags)
        for col in ("File Name", "Size", "Path"):
            self.tree.column(col, width=tkFont.Font().measure(col), stretch=True)
            max_width = self.tree.column(col, width=None)
            for item in self.tree.get_children():
                cell_value = self.tree.set(item, col)
                cell_width = tkFont.Font().measure(cell_value)
                if cell_width > max_width:
                    max_width = cell_width
            self.tree.column(col, width=max_width + 20)
        if self.tree.get_children():
            self.tree.see(self.tree.get_children()[0])

if __name__ == "__main__":
    app = LargestFileFinderApp()
    app.mainloop()
