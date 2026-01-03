import tkinter as tk
from tkinter import ttk, messagebox, font
import api_client
import storage
import threading
import time

import sys
import platform

class EmailApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Temp Mail Generator (Mail.tm)")
        self.root.geometry("1400x900")
        
        # --- Cross-platform High DPI Awareness & Fonts ---
        self.is_mac = platform.system() == "Darwin"
        
        # Base font configurations - MUCH LARGER for readability
        base_family = "Helvetica" if self.is_mac else "Segoe UI"
        
        # Scaling factor rough estimate (manual adjustments for better visual)
        self.uifont = (base_family, 12)
        self.header_font = (base_family, 16, "bold")
        self.title_font = (base_family, 24, "bold")
        self.listbox_font = (base_family, 13)
        self.code_font = ("Consolas", 14)
        self.message_font = (base_family, 16) # Larger for reading content
        
        self.search_placeholder = "🔍 Search..."

        # Data
        self.current_email = None
        self.current_password = None
        self.current_token = None
        self.selected_saved_address = None 
        self.is_auto_refreshing = False
        self.is_fetching_msgs = False
        self.is_editing_saved = False
        self.is_dark_mode = True 
        
        # Styles
        self.style = ttk.Style()
        self.style.theme_use('clam') # 'clam' allows better color customization than 'aqua' or 'vista' usually
        
        # Layout
        self.create_widgets()
        self.apply_theme() 
        
        # Initial Load
        self.load_saved_emails()
        self.email_var.set("Click 'Generate New' or select saved")
        self.root.update()
        
        # Start Polling
        self.start_polling()

    def run_in_thread(self, target, args=(), callback=None):
        """Helper to run a task in a background thread and call callback safely."""
        def wrapper():
            try:
                result = target(*args)
                if callback:
                    self.root.after(0, lambda: callback(result))
            except Exception as e:
                print(f"Thread error: {e}")
        
        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()

    def apply_theme(self):
        # Premium/Modern Color Palettes
        if self.is_dark_mode:
            self.colors = {
                "bg": "#1e1e1e",           # Deep dark grey, almost black
                "fg": "#e0e0e0",           # Soft white
                "accent": "#4cc9f0",       # Cyan/Blue accent
                "accent_hover": "#4895ef",
                "input_bg": "#2d2d2d",     # Lighter grey for inputs
                "input_fg": "#ffffff",
                "select_bg": "#3f3f46",    # Selection color (zinc-700ish)
                "select_fg": "#ffffff",
                "border": "#3f3f46",
                "success": "#4ade80",      # Green
                "warning": "#fca5a5"       # Red/Pink
            }
        else:
            self.colors = {
                "bg": "#f8f9fa",           # Off-white/light grey similar to modern web
                "fg": "#1f2937",           # Dark charcoal (not pure black)
                "accent": "#2563eb",       # Vivid blue
                "accent_hover": "#1d4ed8",
                "input_bg": "#ffffff",
                "input_fg": "#000000",
                "select_bg": "#e5e7eb",    # Light grey selection
                "select_fg": "#000000",
                "border": "#d1d5db",
                "success": "#16a34a",
                "warning": "#dc2626"
            }
            
        self.root.configure(bg=self.colors["bg"])
        
        # Configure TTK Styles with padding and modern look
        self.style.configure("TFrame", background=self.colors["bg"])
        self.style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["fg"], font=self.uifont)
        
        # Modern Buttons
        self.style.configure("TButton", 
            font=self.uifont, 
            borderwidth=0, 
            focuscolor="none",
            padding=(15, 10)) # Horizontal, Vertical padding
            
        self.style.map("TButton",
            background=[('active', self.colors['accent_hover']), ('!active', self.colors['input_bg'])], # Flat style attempt
            foreground=[('active', 'white'), ('!active', self.colors['fg'])],
            relief=[('pressed', 'flat'), ('!pressed', 'flat')])

        # Specific accent button style if needed, but for now applying generic clean look
        
        self.style.configure("Action.TButton", background=self.colors['accent'], foreground='white') # For main actions if we split styles later
        
        self.style.configure("Header.TLabel", font=self.header_font)
        self.style.configure("Title.TLabel", font=self.title_font, foreground=self.colors["accent"])
        
        self.style.configure("TLabelframe", background=self.colors["bg"], foreground=self.colors["fg"], bordercolor=self.colors["border"])
        self.style.configure("TLabelframe.Label", background=self.colors["bg"], foreground=self.colors["fg"], font=self.header_font)
        
        self.style.configure("TPanedwindow", background=self.colors["bg"])
        
        # Treeview styles - Essential for modern look
        row_height = 35 # Significantly taller used for touch/readability
        self.style.configure("Treeview", 
            background=self.colors["input_bg"], 
            foreground=self.colors["input_fg"],
            fieldbackground=self.colors["input_bg"],
            font=self.listbox_font,
            rowheight=row_height,
            borderwidth=0)
            
        self.style.configure("Treeview.Heading", 
            font=self.uifont, 
            background=self.colors["bg"], 
            foreground=self.colors["fg"],
            padding=(10, 10))
            
        self.style.map("Treeview", 
            background=[('selected', self.colors["select_bg"])], 
            foreground=[('selected', self.colors["select_fg"])])
            
        self.style.configure("Unread.Treeview", font=(self.listbox_font[0], self.listbox_font[1], "bold")) 
        self.saved_tree.tag_configure('active', foreground=self.colors['success'], font=(self.listbox_font[0], self.listbox_font[1], "bold"))
        
        # Manual Widget Updates
        if hasattr(self, 'msg_text'):
            self.msg_text.config(
                bg=self.colors["input_bg"], 
                fg=self.colors["input_fg"], 
                insertbackground=self.colors["fg"], 
                font=self.message_font,
                padx=20, pady=20, # Text area internal padding
                selectbackground=self.colors["accent"],
                selectforeground="white"
            )
            
        # Entry styling via configure isn't enough for padding usually in standard ttk
        # We handle Entry font in creation, but colors here
        if hasattr(self, 'email_entry'):
             self.email_entry.config(style="TEntry") 
        if hasattr(self, 'search_entry'):
             self.search_entry.config(style="TEntry")

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def create_widgets(self):
        # --- Top Bar ---
        # Increased padding for layout 'breathing room'
        top_bar = ttk.Frame(self.root, padding="20 20 20 10") # Left Top Right Bottom
        top_bar.pack(fill=tk.X)
        
        # Title with more space
        ttk.Label(top_bar, text="TempMail", style="Title.TLabel").pack(side=tk.LEFT, padx=(0, 30))
        
        # Control Container for better grouping
        controls_frame = ttk.Frame(top_bar)
        controls_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.email_var = tk.StringVar(value="Generating...")
        self.email_entry = ttk.Entry(controls_frame, textvariable=self.email_var, font=self.code_font, state="readonly", width=35, cursor="hand2")
        self.email_entry.pack(side=tk.LEFT, padx=(0, 15), ipady=5) 
        self.email_entry.bind('<Button-1>', self.copy_to_clipboard)
        
        # Modern Buttons with spacing
        btn_generate = ttk.Button(controls_frame, text="✨ Generate", command=self.generate_new_email)
        btn_generate.pack(side=tk.LEFT, padx=5)
        
        # Copy button removed (click header)
        
        self.btn_save = ttk.Button(controls_frame, text="💾 Save", command=self.save_current_email)
        self.btn_save.pack(side=tk.LEFT, padx=5)
        
        btn_theme = ttk.Button(top_bar, text="🌗 Theme", command=self.toggle_theme)
        btn_theme.pack(side=tk.RIGHT, padx=5)
        
        # separator
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', padx=20, pady=5)

        # --- Main Content ---
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Sidebar (Saved Emails)
        sidebar_frame = ttk.LabelFrame(main_paned, text=" Saved Addresses ", padding="15")
        main_paned.add(sidebar_frame, weight=1)
        
        search_frame = ttk.Frame(sidebar_frame)
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.search_var = tk.StringVar(value=self.search_placeholder)
        self.search_var.trace("w", self.filter_saved_emails)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=self.uifont)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        # Placeholder events
        self.search_entry.bind("<FocusIn>", self.on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self.on_search_focus_out)
        
        # Clear button logic update for placeholder
        btn_clear_search = ttk.Button(search_frame, text="✕", width=3, 
            command=lambda: [self.search_var.set(""), self.search_entry.focus()])
        btn_clear_search.pack(side=tk.LEFT, padx=(5, 0))
        
        btn_open_folder = ttk.Button(search_frame, text="📂", width=4, command=storage.open_storage_folder)
        btn_open_folder.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Treeview Scrollbar
        tree_frame = ttk.Frame(sidebar_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.saved_tree = ttk.Treeview(tree_frame, columns=("Address", "Stage", "Prod", "Name"), show="headings", selectmode="browse", yscrollcommand=tree_scroll.set)
        tree_scroll.config(command=self.saved_tree.yview)
        
        self.saved_tree.heading("Address", text="Address")
        self.saved_tree.heading("Stage", text="Stage")
        self.saved_tree.heading("Prod", text="Prod")
        self.saved_tree.heading("Name", text="Name")
        
        self.saved_tree.column("Address", width=200)
        self.saved_tree.column("Stage", width=70)
        self.saved_tree.column("Prod", width=70)
        self.saved_tree.column("Name", width=100)
        
        self.saved_tree.pack(fill=tk.BOTH, expand=True)
        self.saved_tree.bind('<<TreeviewSelect>>', self.on_saved_email_select)
        self.saved_tree.bind('<Triple-Button-1>', self.login_to_saved_email)
        self.saved_tree.bind('<Double-1>', self.on_saved_email_double_click)
        
        # Drag and Drop Bindings
        self.saved_tree.bind('<ButtonPress-1>', self.on_drag_start)
        self.saved_tree.bind('<B1-Motion>', self.on_drag_motion)
        self.saved_tree.bind('<ButtonRelease-1>', self.on_drag_release)
        
        btn_delete_saved = ttk.Button(sidebar_frame, text="Trash Selected", command=self.delete_saved_email)
        btn_delete_saved.pack(fill=tk.X, pady=10)

        # Right Side (Inbox & Message View)
        right_paned = ttk.PanedWindow(main_paned, orient=tk.VERTICAL)
        main_paned.add(right_paned, weight=3)
        
        # Inbox List
        inbox_frame = ttk.LabelFrame(right_paned, text=" Inbox ", padding="15")
        right_paned.add(inbox_frame, weight=1)
        
        inbox_tree_frame = ttk.Frame(inbox_frame)
        inbox_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        inbox_scroll = ttk.Scrollbar(inbox_tree_frame)
        inbox_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(inbox_tree_frame, columns=("Sender", "Subject", "Date"), show="headings", selectmode="browse", yscrollcommand=inbox_scroll.set)
        inbox_scroll.config(command=self.tree.yview)
        
        self.tree.heading("Sender", text="Sender")
        self.tree.heading("Subject", text="Subject")
        self.tree.heading("Date", text="Date")
        
        self.tree.column("Sender", width=200)
        self.tree.column("Subject", width=400)
        self.tree.column("Date", width=150)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_message_select)
        
        # Message Content
        content_frame = ttk.LabelFrame(right_paned, text=" Message ", padding="15")
        right_paned.add(content_frame, weight=3) # Give more weight to reading area
        
        self.msg_text = tk.Text(content_frame, font=self.message_font, wrap=tk.WORD, state="disabled", highlightthickness=0, borderwidth=0)
        self.msg_text.pack(fill=tk.BOTH, expand=True)

    def generate_new_email(self):
        self.email_var.set("Generating...")
        
        def on_done(account):
            if account:
                self.set_current_account(account['address'], account['password'], account['token'])
            else:
                messagebox.showerror("Error", "Failed to generate email.")
                self.email_var.set("Error")
        
        self.run_in_thread(api_client.create_account, callback=on_done)


    def set_current_account(self, address, password, token):
        self.current_email = address
        self.current_password = password
        self.current_token = token
        
        self.email_var.set(address)
        
        # Clear UI
        self.tree.delete(*self.tree.get_children())
        self.msg_text.config(state="normal")
        self.msg_text.delete(1.0, tk.END)
        self.msg_text.config(state="disabled")
        
        self.load_saved_emails() # Refresh to update active highlight
        self.refresh_inbox(force=True)

    def refresh_inbox(self, force=False):
        if not self.current_token or self.is_fetching_msgs:
            return

        self.is_fetching_msgs = True
        
        def task():
            try:
                return api_client.get_messages(self.current_token)
            except Exception as e:
                print(f"Error fetching messages: {e}")
                return None

        def on_done(msgs):
            self.is_fetching_msgs = False
            if msgs is None: return
            
            existing_ids = {self.tree.item(item)['values'][3] for item in self.tree.get_children()}
            new_ids = {m['id'] for m in msgs}
            
            if existing_ids == new_ids and not force:
                 # Update tags for read/unread
                 for msg in msgs:
                     item_id = next((i for i in self.tree.get_children() if self.tree.item(i)['values'][3] == msg['id']), None)
                     if item_id:
                         current_tags = self.tree.item(item_id, 'tags')
                         is_seen = msg.get('seen', False)
                         if not is_seen and 'unread' not in current_tags:
                             self.tree.item(item_id, tags=('unread',))
                         elif is_seen and 'unread' in current_tags:
                             self.tree.item(item_id, tags=())
                 return
                
            self.tree.delete(*self.tree.get_children())
            for msg in msgs:
                raw_date = msg.get('createdAt', '')
                date_str = raw_date.replace('T', ' ')[:16] if 'T' in raw_date else raw_date
                sender_name = msg.get('from', {}).get('name') or msg.get('from', {}).get('address')
                is_seen = msg.get('seen', False)
                tags = ('unread',) if not is_seen else ()
                self.tree.insert("", "end", values=(sender_name, msg.get('subject'), date_str, msg.get('id')), tags=tags)
            
            self.tree.tag_configure('unread', font=(self.listbox_font[0], self.listbox_font[1], 'bold'))

        self.run_in_thread(task, callback=on_done)

    def on_message_select(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
            
        item = self.tree.item(selected_item)
        msg_id = item['values'][3]
        
        self.tree.item(selected_item, tags=()) 
        threading.Thread(target=self.mark_as_read_async, args=(msg_id,), daemon=True).start()
        
        self.load_message_content(msg_id)

    def mark_as_read_async(self, msg_id):
        try:
            api_client.mark_message_as_seen(self.current_token, msg_id)
        except:
            pass

    def load_message_content(self, msg_id):
        self.msg_text.config(state="normal")
        self.msg_text.delete(1.0, tk.END)
        self.msg_text.insert(tk.END, "Loading message content...")
        self.msg_text.config(state="disabled")
        
        def task():
            try:
                return api_client.get_message_content(self.current_token, msg_id)
            except:
                return None

        def on_done(full_msg):
            self.msg_text.config(state="normal")
            self.msg_text.delete(1.0, tk.END)
            
            if full_msg:
                text_content = full_msg.get('text', '') or full_msg.get('intro', '')
                if not text_content:
                    text_content = "(This email contains only HTML content. Open in a full email client to view.)"
                
                from_name = full_msg.get('from', {}).get('name', '')
                from_addr = full_msg.get('from', {}).get('address', '')
                
                self.msg_text.insert(tk.END, f"FROM: {from_name} <{from_addr}>\n")
                self.msg_text.insert(tk.END, f"SUBJECT: {full_msg.get('subject')}\n")
                self.msg_text.insert(tk.END, f"DATE: {full_msg.get('createdAt')}\n")
                self.msg_text.insert(tk.END, "_"*50 + "\n\n")
                self.msg_text.insert(tk.END, text_content)
            else:
                self.msg_text.insert(tk.END, "Failed to load message content.")
                
            self.msg_text.config(state="disabled")

        self.run_in_thread(task, callback=on_done)

    def copy_to_clipboard(self, event=None):
        if self.current_email:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_email)
            
            # Feedback on Entry
            original_text = self.current_email
            self.email_var.set("✔ Copied!")
            self.root.after(1200, lambda: self.reset_email_text_safe(original_text))

    def reset_email_text_safe(self, text):
        # Only reset if we are still on the same email (checking basic state)
        # If user generated new one, current_email would change. 
        # But for UI consistency, we usually just want to revert execution unless changed.
        if self.email_var.get() == "✔ Copied!":
            self.email_var.set(self.current_email if self.current_email else text)

    def save_current_email(self):
        if self.current_email and self.current_password:
            if storage.save_email(self.current_email, self.current_password):
                self.load_saved_emails()
                self.show_save_feedback(success=True)
            else:
                self.show_save_feedback(success=False)

    def show_save_feedback(self, success=True):
        if hasattr(self, 'btn_save'):
            original_text = "💾 Save"
            if success:
                self.btn_save.config(text="✔ Saved!")
            else:
                self.btn_save.config(text="⚠ Exists")
            
            # Revert after 1.5 seconds
            self.root.after(1500, lambda: self.btn_save.config(text=original_text))

    def load_saved_emails(self, force=False):
        if self.is_editing_saved and not force:
            return
            
        self.saved_tree.delete(*self.saved_tree.get_children())
        emails = storage.load_emails()
        
        # Handle placeholder
        raw_search = self.search_var.get() if hasattr(self, 'search_var') else ""
        if raw_search == self.search_placeholder:
            filter_text = ""
        else:
            filter_text = raw_search.lower()
        
        for email_data in emails:
            addr = email_data.get('address', 'Unknown')
            stage = email_data.get('stage_id', '')
            prod = email_data.get('prod_id', '')
            name = email_data.get('name', '')
            
            if (filter_text in addr.lower() or 
                filter_text in str(stage).lower() or 
                filter_text in str(prod).lower() or
                filter_text in str(name).lower()):
                
                tags = ('active',) if addr == self.current_email else ()
                self.saved_tree.insert("", "end", values=(addr, stage, prod, name), tags=tags)
        
        self.autosize_saved_columns()

    def autosize_saved_columns(self):
        font_obj = font.Font(font=self.listbox_font)
        columns = ["Address", "Stage", "Prod", "Name"]
        
        # Set a minimum width for headers
        min_widths = {"Address": 150, "Stage": 60, "Prod": 60, "Name": 80}
        
        for col in columns:
            # Start with header width
            max_width = font_obj.measure(col) + 20 
            if max_width < min_widths.get(col, 50):
                max_width = min_widths.get(col, 50)
            
            for item in self.saved_tree.get_children():
                # Get the value for this column
                # columns list matches values index: Address=0, Stage=1, Prod=2, Name=3
                val_idx = columns.index(col)
                val = self.saved_tree.item(item, "values")[val_idx]
                
                val_width = font_obj.measure(str(val)) + 25 # + padding
                if val_width > max_width:
                    max_width = val_width
            
            # Cap at reasonable max to prevent screen takeover
            if max_width > 800: max_width = 800
                
            self.saved_tree.column(col, width=max_width)

    def filter_saved_emails(self, *args):
        # Debounce filter to avoid heavy resizing on every keystroke
        if hasattr(self, '_search_after_id'):
            self.root.after_cancel(self._search_after_id)
        self._search_after_id = self.root.after(200, self.load_saved_emails)

    def on_search_focus_in(self, event):
        if self.search_var.get() == self.search_placeholder:
            self.search_var.set("")
            
    def on_search_focus_out(self, event):
        if self.search_var.get() == "":
            self.search_var.set(self.search_placeholder)

    # --- Drag and Drop Reordering ---
    def on_drag_start(self, event):
        item = self.saved_tree.identify_row(event.y)
        if item:
            self.drag_item = item
            self.drag_occurred = False
        else:
            self.drag_item = None

    def on_drag_motion(self, event):
        if not self.drag_item:
            return
            
        target = self.saved_tree.identify_row(event.y)
        if target and target != self.drag_item:
            # Check if filtered
            search_text = self.search_var.get().strip()
            if search_text and search_text != self.search_placeholder:
                # Avoid reordering filtered list confusingly
                return
                
            self.drag_occurred = True
            
            # Move visually
            index = self.saved_tree.index(target)
            self.saved_tree.move(self.drag_item, "", index)

    def on_drag_release(self, event):
        if not hasattr(self, 'drag_item') or not self.drag_item:
            return
            
        if self.drag_occurred:
            # Filter check
            search_text = self.search_var.get().strip()
            if search_text and search_text != self.search_placeholder:
                messagebox.showwarning("Reorder Disabled", "Please clear the search filter to reorder addresses.")
                self.load_saved_emails(force=True) # Reset order
                self.drag_item = None
                self.drag_occurred = False
                return

            # Save new order
            new_order_data = []
            all_current_emails = storage.load_emails()
            # Map address to data
            email_map = {e['address']: e for e in all_current_emails}
            
            children = self.saved_tree.get_children()
            for child in children:
                addr = self.saved_tree.item(child, 'values')[0]
                if addr in email_map:
                    new_order_data.append(email_map[addr])
            
            # Check if we lost anything (shouldn't if no filter)
            if len(new_order_data) == len(all_current_emails):
                storage.save_all_emails(new_order_data)
                # print("Order saved")
            else:
                # Fallback if something went wrong
                print("Mismatch in count, not saving order")
                self.load_saved_emails()

        self.drag_item = None
        self.drag_occurred = False

    def on_saved_email_double_click(self, event):
        region = self.saved_tree.identify("region", event.x, event.y)
        if region != "cell":
            return
            
        column = self.saved_tree.identify_column(event.x)
        item_id = self.saved_tree.identify_row(event.y)
        
        if not item_id:
            return
            
        col_map = {"#2": "stage_id", "#3": "prod_id", "#4": "name"}
        val_idx_map = {"#2": 1, "#3": 2, "#4": 3}
        
        if column not in col_map:
            return
            
        self.is_editing_saved = True # Lock refreshes
        current_values = self.saved_tree.item(item_id, "values")
        current_val = current_values[val_idx_map[column]]
        bbox = self.saved_tree.bbox(item_id, column)
        
        if not bbox:
            return
            
        # Create In-Place Editor
        entry = tk.Entry(self.saved_tree, width=bbox[2], 
                         bg=self.colors["input_bg"], 
                         fg=self.colors["input_fg"], 
                         insertbackground=self.colors["fg"],
                         selectbackground=self.colors["accent"],
                         selectforeground="white",
                         font=self.listbox_font,
                         relief="solid", borderwidth=1)
                         
        entry.place(x=bbox[0], y=bbox[1], w=bbox[2], h=bbox[3])
        entry.insert(0, current_val)
        entry.select_range(0, tk.END)
        entry.focus()
        
        def commit(e=None):
            new_val = entry.get()
            address = current_values[0]
            field = col_map[column]
            
            stage = current_values[1]
            prod = current_values[2]
            name = current_values[3]
            
            if field == "stage_id": stage = new_val
            elif field == "prod_id": prod = new_val
            elif field == "name": name = new_val
            
            if storage.update_email_metadata(address, stage, prod, name):
                if self.saved_tree.exists(item_id):
                    new_values = list(current_values)
                    new_values[val_idx_map[column]] = new_val
                    self.saved_tree.item(item_id, values=new_values)
            
            self.is_editing_saved = False
            entry.destroy()

        def cancel(e=None):
            self.is_editing_saved = False
            entry.destroy()
            
        entry.bind("<Return>", commit)
        entry.bind("<Escape>", cancel)
        entry.bind("<FocusOut>", commit)

    def on_saved_email_select(self, event):
        selection = self.saved_tree.selection()
        if selection:
            item = self.saved_tree.item(selection[0])
            address = item['values'][0]
            self.selected_saved_address = address

    def login_to_saved_email(self, event=None):
        if event:
            column = self.saved_tree.identify_column(event.x)
            if column != "#1":
                return # Only log in if Address column is clicked
                
        selection = self.saved_tree.selection()
        if not selection:
             # handle empty area clicks if needed
             pass
        
        if selection:
            item = self.saved_tree.item(selection[0])
            address = item['values'][0]
            
            emails = storage.load_emails()
            creds = next((e for e in emails if e['address'] == address), None)
            
            if creds:
                self.email_var.set(f"Logging in to {address}...")
                
                def task():
                    return api_client.get_token(creds['address'], creds['password'])
                
                def on_done(token):
                    if token:
                        self.set_current_account(creds['address'], creds['password'], token)
                    else:
                        messagebox.showerror("Auth Error", "Could not login. Account might be deleted by server.")
                        self.email_var.set(creds['address']) # Revert text
                
                self.run_in_thread(task, callback=on_done)

    def delete_saved_email(self):
        selection = self.saved_tree.selection()
        if selection:
            item = self.saved_tree.item(selection[0])
            email = item['values'][0]
            if storage.delete_email(email):
                self.load_saved_emails()
            else:
                messagebox.showerror("Error", "Could not delete.")

    def start_polling(self):
        if not self.is_auto_refreshing:
            self.is_auto_refreshing = True
            self.poll()
            
    def poll(self):
        try:
            self.refresh_inbox()
        except Exception:
            pass
        self.root.after(5000, self.poll) 

if __name__ == "__main__":
    # --- High DPI Windows Fix ---
    if platform.system() == "Windows":
        try:
            from ctypes import windll
            # 2 = process per monitor DPI aware
            windll.shcore.SetProcessDpiAwareness(2) 
        except Exception:
            try:
                # 1 = process system DPI aware
                windll.shcore.SetProcessDpiAwareness(1)
            except:
                pass
                
    root = tk.Tk()
    
    # Try to set app icon if exists
    try:
        # Check standard locations/formats
        if platform.system() == 'Windows':
             root.iconbitmap("ico.ico")
        # macOS app bundles handle icons differently, usually via Info.plist, 
        # but we can try setting tk image if needed.
    except:
        pass

    app = EmailApp(root)
    root.mainloop()
