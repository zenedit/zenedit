import tkinter as tk
from tkinter import filedialog, colorchooser, font, simpledialog, messagebox
import json
import os

class ZenEdit:
    def __init__(self, root):
        self.root = root
        self.root.geometry("800x495")
        self.root.title("ZenEdit")
        self.config_file = "editor_config.json"
        self.auto_save_file = "default_autosave.txt"
        self.auto_save_enabled = tk.BooleanVar(value=True)
        self.auto_save_enabled.trace('w', self.update_config_auto_save)
        self.auto_save_interval = 5000
        self.default_config = {
            "root_bg_color": "#1e1e1e",
            "font_family": "Arial",
            "font_size": 16,
            "font_bold": False,
            "font_italic": False,
            "bg_color": "#1e1e1e",
            "fg_color": "#ffffff",
            "caret_cursor_color": "white",
            "selection_color": "#3399ff",
            "selection_text_color": "#ffffff",
            "caret_cursor": False,
            "text_width": 800,
            "text_height": 945,
            "line_spacing": 4,
            "border_thickness": 1,
            "border_color": "#ffffff",
            "padding": 0,
            "insertwidth": 2
        }
        self.config = self.default_config.copy()
        self.fullScreenState = False
        self.root_bg_image_visible = False
        self.load_config()
        self.setup_ui()

    def load_config(self):
        try:
            with open(self.config_file, "r") as file:
                file_config = json.load(file)
                self.config.update(file_config)
        except FileNotFoundError:
            self.config = self.default_config.copy()

    def setup_ui(self):
        self.setup_icon()
        self.setup_frame_and_text_area()
        self.setup_menus()
        self.setup_bindings()
        self.auto_save()

    def setup_icon(self):
        try:
            script_dir = os.path.dirname(os.path.realpath(__file__))
            icon_path = os.path.join(script_dir, 'zenedit.png')
            img = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(False, img)
        except Exception:
            pass

    def setup_frame_and_text_area(self):
        self.frame = tk.Frame(self.root, bg=self.config["bg_color"])
        self.frame.pack(expand=True)
        self.frame.config(width=self.config["text_width"], height=self.config["text_height"])
        self.frame.pack_propagate(False)

        self.current_font = font.Font(
            family=self.config["font_family"],
            size=self.config["font_size"],
            weight="bold" if self.config["font_bold"] else "normal",
            slant="italic" if self.config["font_italic"] else "roman"
        )

        self.text_area = tk.Text(
            self.frame,
            font=self.current_font,
            undo=True,
            bg=self.config["bg_color"],
            fg=self.config["fg_color"],
            insertbackground=self.config["caret_cursor_color"],
            insertwidth=self.config["insertwidth"],
            spacing3=self.config["line_spacing"],
            borderwidth=0,
            wrap=tk.WORD,
            highlightthickness=self.config["border_thickness"],
            highlightbackground=self.config["border_color"],
            highlightcolor=self.config["border_color"],
            selectbackground=self.config["selection_color"],
            selectforeground=self.config["selection_text_color"]
        )
        self.text_area.pack(side="top", fill="both", expand=True)

    def update_config_auto_save(self, *args):
        self.update_config("auto_save_enabled", self.auto_save_enabled.get())

    def update_config(self, key, value):
        self.config[key] = value
        self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as file:
            json.dump(self.config, file, indent=4)

    def setup_bindings(self):
        self.text_area.bind("<Control-s>", self.save_file)
        self.text_area.bind("<Control-S>", self.save_file)
        self.text_area.bind("<Control-z>", self.undo_text)
        self.text_area.bind("<Control-Z>", self.undo_text)
        self.text_area.bind("<Control-y>", self.redo_text)
        self.text_area.bind("<Control-Y>", self.redo_text)
        self.text_area.bind("<Control-a>", self.select_all)
        self.text_area.bind("<Control-A>", self.select_all)
        self.text_area.bind("<Control-x>", self.cut_text)
        self.text_area.bind("<Control-X>", self.cut_text)
        self.text_area.bind("<Control-c>", self.copy_text)
        self.text_area.bind("<Control-C>", self.copy_text)
        self.text_area.bind("<Control-v>", self.paste_text)
        self.text_area.bind("<Control-V>", self.paste_text)
    
        self.root.bind("<Control-q>", lambda event: self.quit())
        self.root.bind("<Control-Q>", lambda event: self.quit())
        self.root.bind("<F2>", lambda event: self.toggle_border_visibility())
        self.root.bind("<F5>", lambda event: self.toggle_line_numbers())
        self.root.bind("<Control-Shift-g>", lambda event: self.show_word_char_count())
        self.root.bind("<Control-Shift-G>", lambda event: self.show_word_char_count())
        self.root.bind("<F3>", self.search_text)
        self.root.bind("<Control-f>", lambda event: self.search_text())
        self.root.bind("<Control-F>", lambda event: self.search_text())
        self.root.bind("<Control-g>", lambda event: self.goto_line())
        self.root.bind("<Control-G>", lambda event: self.goto_line())
        self.root.bind("<Control-h>", self.replace_text)
        self.root.bind("<Control-H>", self.replace_text)
        self.root.bind("<Control-n>", lambda event: self.new_file())
        self.root.bind("<Control-N>", lambda event: self.new_file())
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-O>", lambda event: self.open_file())
        self.root.bind("<F10>", lambda event: self.toggle_menu_view())
        self.root.bind("<F11>", self.toggle_full_screen)
        self.root.bind("<Control-Alt-s>", lambda event: self.save_file())
        self.root.bind("<Control-Alt-S>", lambda event: self.save_file())

    def setup_menus(self):
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu, bg=self.config["root_bg_color"])

        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.edit_menu = tk.Menu(self.menu, tearoff=0)
        self.view_menu = tk.Menu(self.menu, tearoff=0)
        self.format_menu = tk.Menu(self.menu, tearoff=0)
        self.settings_menu = tk.Menu(self.menu, tearoff=0)

        self.file_menu.add_command(label="New (CTRL+N)", command=self.new_file)
        self.file_menu.add_command(label="Open (CTRL+O)", command=self.open_file)
        self.file_menu.add_command(label="Save (CTRL+S)", command=self.save_file)
        self.file_menu.add_command(label="Save As... (CTRL+ALT+S)", command=self.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit (CTRL+Q)", command=self.quit)

        self.edit_menu.add_command(label="Undo (CTRL+Z)", command=self.undo_text)
        self.edit_menu.add_command(label="Redo (CTRL+Y)", command=self.redo_text)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Copy (CTRL+C)", command=self.copy_text)
        self.edit_menu.add_command(label="Cut (CTRL+X)", command=self.cut_text)
        self.edit_menu.add_command(label="Paste (CTRL+V)", command=self.paste_text)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Select All (CTRL+A)", command=self.select_all)
        self.edit_menu.add_command(label="Search (F3)", command=self.search_text)
        self.edit_menu.add_command(label="Replace (Control-H)", command=self.replace_text)
        self.edit_menu.add_command(label="Go to Line... (CTRL+G)", command=self.goto_line)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Toggle Line Numbers (F5)", command=self.toggle_line_numbers)

        self.view_menu.add_command(label="FullScreen (F11)", command=self.toggle_full_screen)
        self.view_menu.add_separator()
        self.view_menu.add_command(label="Word/Character Count (CTRL+SHIFT+G)", command=self.show_word_char_count)
        self.view_menu.add_command(label="Set Text Area Size", command=self.set_text_area_size)
        self.view_menu.add_command(label="Set Padding", command=self.set_padding)
        self.view_menu.add_separator()
        self.view_menu.add_command(label="Toggle Text Blink", command=self.toggle_text_blink)
        self.view_menu.add_command(label="Toggle Menu Visibility (F10)", command=self.toggle_menu_view)
        self.view_menu.add_command(label="Toggle Border Visibility (F2)", command=self.toggle_border_visibility)
        self.view_menu.add_command(label="Toggle Mouse Cursor Visibility", command=self.toggle_mouse_cursor_visibility)
        self.view_menu.add_command(label="Toggle Caret Cursor Visibility", command=self.toggle_caret_cursor_visibility)
        self.view_menu.add_command(label="Toggle Caret Cursor Blink", command=self.toggle_caret_cursor_blink)
        self.view_menu.add_command(label="Set Caret Cursor Blink Speed", command=self.set_caret_cursor_blink_speed)
        
        self.format_menu.add_command(label="Change Font", command=self.change_font)
        self.format_menu.add_command(label="Change Font Size", command=self.change_font_size)
        self.format_menu.add_separator()
        self.format_menu.add_command(label="Set Line Spacing", command=self.set_line_spacing)
        self.format_menu.add_separator()
        self.format_menu.add_command(label="Align Left", command=self.align_left)
        self.format_menu.add_command(label="Center", command=self.align_center)
        self.format_menu.add_command(label="Align Right", command=self.align_right)

        self.settings_menu.add_command(label="Toggle Root Background Image", command=self.toggle_root_background_image)
        self.settings_menu.add_command(label="Change Root Background Color", command=self.change_root_bg_color)
        self.settings_menu.add_command(label="Change Text Area Background Color", command=self.change_text_area_bg_color)
        self.settings_menu.add_command(label="Change Text Color", command=self.change_fg_color)
        self.settings_menu.add_command(label="Change Caret Cursor Color", command=self.change_caret_cursor_color)
        self.settings_menu.add_command(label="Change Selection Color", command=self.change_selection_color)
        self.settings_menu.add_command(label="Change Selection Text Color", command=self.change_selection_text_color,)
        self.settings_menu.add_command(label="Change Border Color", command=self.change_border_color)
        self.settings_menu.add_separator()
        self.settings_menu.add_command(label="Set Border Thickness", command=self.set_border_thickness)
        self.settings_menu.add_command(label="Set Caret Cursor Thickness", command=self.set_caret_cursor_thickness)
        self.settings_menu.add_separator()
        self.settings_menu.add_command(label="Reset to Default Theme", command=self.reset_to_default_theme)
        self.settings_menu.add_separator()
        self.settings_menu.add_checkbutton(label="Enable Autosave", onvalue=True, offvalue=False, variable=self.auto_save_enabled, command=self.toggle_auto_save)

        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.menu.add_cascade(label="Edit", menu=self.edit_menu)
        self.menu.add_cascade(label="View", menu=self.view_menu)
        self.menu.add_cascade(label="Format", menu=self.format_menu)
        self.menu.add_cascade(label="Settings", menu=self.settings_menu)
        self.menu.add_command(label="About", command=self.show_about)

    def auto_save(self):
            if self.auto_save_enabled.get():  
                filepath = self.current_file_path if hasattr(self, 'current_file_path') and self.current_file_path else self.auto_save_file
                with open(filepath, "w") as file:
                    file.write(self.text_area.get(1.0, tk.END))
            self.root.after(self.auto_save_interval, self.auto_save)
#File
    def new_file(self):
        response = None
        if self.text_area.edit_modified():
            response = messagebox.askyesnocancel(
                "Save changes", "Do you want to save changes to the current file?"
            )
        if response is True:
            self.save_file()
            self.text_area.delete(1.0, tk.END)
        elif response is False:
            self.text_area.delete(1.0, tk.END)
            self.text_area.edit_modified(False)

    def open_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not filepath:
            return
        try:
            with open(filepath, "r") as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())
            self.current_file_path = filepath  
            self.root.title(f"ZenEdit - {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Open File", f"Failed to open file: {e}")

    def save_file(self, event=None):
        filepath = self.current_file_path if hasattr(self, 'current_file_path') and self.current_file_path else None
        if not filepath:
            filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
            if not filepath:
                return
            self.current_file_path = filepath 

        try:
            with open(filepath, "w") as file:
                file.write(self.text_area.get(1.0, tk.END))
            self.root.title(f"ZenEdit - {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Save File", f"Failed to save file: {e}")

    def save_as_file(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not filepath:
            return
        try:
            with open(filepath, "w") as file:
                file.write(self.text_area.get(1.0, tk.END))
            self.current_file_path = filepath  
            self.root.title(f"ZenEdit - {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Save As File", f"Failed to save file: {e}")

    def quit(self):
        response = False
        if self.text_area.edit_modified():
            response = messagebox.askyesnocancel("Save on Exit", "Do you want to save the changes before exiting?")
        if response is True:
            self.save_file()
        elif response is None:
            return
        if response is not None:
            self.root.destroy()

#Edit
    def undo_text(self, event=None):
        try:
            self.text_area.edit_undo()
        except tk.TclError:
            pass
        return "break"

    def redo_text(self, event=None):
        try:
            self.text_area.edit_redo()
        except tk.TclError:
            pass
        return "break"

    def copy_text(self, event=None):
            self.text_area.event_generate("<<Copy>>")
            return "break"

    def cut_text(self, event=None):
        self.text_area.event_generate("<<Cut>>")
        return "break"

    def paste_text(self, event=None):
        self.text_area.event_generate("<<Paste>>")
        return "break"

    def select_all(self, event=None):
        self.text_area.tag_add("sel", "1.0", "end")
        return "break"

    def search_text(self, event=None):
            search_window = tk.Toplevel(self.root)
            search_window.title("Search")
            tk.Label(search_window, text="Find:").pack(side="left")
            search_entry = tk.Entry(search_window)
            search_entry.pack(side="left", fill="x", expand=True)
            search_entry.focus_set()
            case_sensitive = tk.BooleanVar(value=False)
            tk.Checkbutton(search_window, text="Case Sensitive", variable=case_sensitive).pack(side="left")
            highlight_tag = "search_highlight"
            highlight_background = self.text_area.cget("selectbackground")
            highlight_foreground = self.text_area.cget("selectforeground")
            self.text_area.tag_configure(highlight_tag, background=highlight_background, foreground=highlight_foreground)

            def do_search(next=False):
                search_query = search_entry.get()
                if not search_query:
                    return
                start_idx = '1.0' if not next else self.text_area.index(tk.INSERT) + '+1c'
                search_args = {'nocase': not case_sensitive.get(), 'regexp': False}
                self.text_area.tag_remove(highlight_tag, "1.0", tk.END) 
                search_idx = self.text_area.search(search_query, start_idx, stopindex=tk.END, **search_args)
                if not search_idx and next:
                    search_idx = self.text_area.search(search_query, "1.0", stopindex=tk.END, **search_args)
                if search_idx:
                    end_idx = f"{search_idx}+{len(search_query)}c"
                    self.text_area.tag_add(highlight_tag, search_idx, end_idx)
                    self.text_area.mark_set(tk.INSERT, end_idx)
                    self.text_area.see(search_idx)

                    self.last_search_start = search_idx
                    self.last_search_end = end_idx
                else:
                    messagebox.showinfo("Search", "Text not found.")

            def close_search():
                self.text_area.tag_remove(highlight_tag, "1.0", tk.END)
                if hasattr(self, 'last_search_start') and hasattr(self, 'last_search_end'):
                    self.text_area.tag_add(tk.SEL, self.last_search_start, self.last_search_end)
                    self.text_area.mark_set(tk.INSERT, self.last_search_end)
                    self.text_area.see(self.last_search_start)
                search_window.destroy()
            search_window.protocol("WM_DELETE_WINDOW", close_search)
            tk.Button(search_window, text="Find", command=do_search).pack(side="left")
            tk.Button(search_window, text="Next", command=lambda: do_search(next=True)).pack(side="left")
            tk.Button(search_window, text="Close", command=close_search).pack(side="left")
            search_entry.bind("<Return>", lambda event: do_search(next=True))

    def replace_text(self, event=None):
        replace_window = tk.Toplevel(self.root)
        replace_window.title("Replace Text")
        tk.Label(replace_window, text="Find what:").pack(side=tk.LEFT)
        find_entry = tk.Entry(replace_window)
        find_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(replace_window, text="Replace with:").pack(side=tk.LEFT)
        replace_entry = tk.Entry(replace_window)
        replace_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        case_sensitive = tk.BooleanVar(value=False)
        tk.Checkbutton(replace_window, text="Case Sensitive", variable=case_sensitive).pack(side=tk.LEFT)

        def do_replace():
            search_query = find_entry.get()
            replacement = replace_entry.get()
            if search_query and replacement is not None:
                all_text = self.text_area.get("1.0", tk.END)
                count = 0

                if case_sensitive.get():
                    count = all_text.count(search_query)
                    updated_text = all_text.replace(search_query, replacement)
                else:
                    lower_text = all_text.lower()
                    lower_query = search_query.lower()
                    count = lower_text.count(lower_query)
                    
                    updated_text = all_text[:0]
                    start = 0
                    while True:
                        idx = lower_text.find(lower_query, start)
                        if idx == -1:
                            updated_text += all_text[start:]
                            break
                        updated_text += all_text[start:idx] + replacement
                        start = idx + len(search_query)

                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", updated_text)
                messagebox.showinfo("Replace", f"Replaced {count} occurrences of '{search_query}' with '{replacement}'.")
                replace_window.destroy()
        replace_button = tk.Button(replace_window, text="Replace All", command=do_replace)
        replace_button.pack(side=tk.LEFT)
        close_button = tk.Button(replace_window, text="Close", command=replace_window.destroy)
        close_button.pack(side=tk.LEFT)
        find_entry.focus_set()
        replace_window.bind('<Return>', lambda e: do_replace())

        find_entry.focus_set()

    def goto_line(self):
            line_number = simpledialog.askinteger("Go to Line", "Enter line number:")
            if line_number is not None and line_number > 0:
                index = f"{line_number}.0"
                if self.text_area.compare(index, "<=", "end"):
                    self.text_area.see(index)
                    self.text_area.mark_set("insert", index)
                    self.text_area.tag_remove(tk.SEL, "1.0", tk.END)
                    self.text_area.tag_add(tk.SEL, index, f"{index} lineend")
#View
    def toggle_full_screen(self, event=None):
        self.fullScreenState = not self.fullScreenState
        self.root.attributes("-fullscreen", self.fullScreenState)
        if self.fullScreenState:
            self.root.config(menu="")
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            width = 800
            height = 495
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            self.root.geometry(f"{width}x{height}+{x}+{y}")
        else:
            self.root.config(menu=self.menu)
            self.root.geometry("800x495")
            self.root.update_idletasks()

    def toggle_line_numbers(self):
            lines = self.text_area.get('1.0', 'end-1c').split('\n')
            if lines[0].split(".")[0].isdigit():
                stripped_lines = [line.split('. ', 1)[-1] if '. ' in line else line for line in lines]
            else:
                stripped_lines = [f"{i+1}. {line}" for i, line in enumerate(lines)]
            self.text_area.delete('1.0', 'end')
            self.text_area.insert('1.0', '\n'.join(stripped_lines))

    def show_word_char_count(self):
            text_content = self.text_area.get(1.0, "end-1c")
            words = len(text_content.split())
            characters = len(text_content)
            messagebox.showinfo(
                "Word/Character Count", f"Words: {words}\nCharacters: {characters}"
            )

    def set_text_area_size(self):
        current_dimensions = f"{self.frame.winfo_width()}x{self.frame.winfo_height()}"
        dimensions = simpledialog.askstring("Text Area Size", "Enter size in pixels (width x height):", initialvalue=current_dimensions)
        if dimensions:
            try:
                pixel_width, pixel_height = map(int, dimensions.split('x'))
                if pixel_width > 0 and pixel_height > 0:
                    self.frame.config(width=pixel_width, height=pixel_height)
                    self.frame.pack_propagate(False)
                    self.text_area.config(width=pixel_width, height=pixel_height)
                    self.config["text_width"] = pixel_width
                    self.config["text_height"] = pixel_height
                    self.save_config()
                else:
                    messagebox.showerror("Invalid Size", "Width and height must be positive integers.")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid size in the format width x height.")

    def set_padding(self):
        padding = simpledialog.askinteger("Padding", "Enter padding size:", minvalue=0)
        if padding is not None and padding >= 0:
            self.text_area.config(padx=padding, pady=padding)
            self.config["padding"] = padding
            self.save_config()
        else:
            messagebox.showerror("Invalid Padding", "Padding must be a non-negative integer.")
                
    def toggle_border_visibility(self):
        current_thickness = self.text_area.cget("highlightthickness")
        if current_thickness > 0:
            self.config['border_thickness'] = current_thickness
            self.text_area.config(highlightthickness=0)
        else:
            self.text_area.config(highlightthickness=self.config['border_thickness'])

        self.save_config()
    
    def toggle_mouse_cursor_visibility(self):
        if self.text_area["cursor"] in ["", "xterm"]:
            self.text_area.config(cursor="none")
        else:
            self.text_area.config(cursor="xterm")

    def toggle_caret_cursor_visibility(self):
        if self.text_area['insertwidth'] > 1:
            self.config['insertwidth'] = self.text_area['insertwidth']
            self.text_area.config(insertwidth=0)
        else:
            insertwidth = self.config.get('insertwidth', 2)
            self.text_area.config(insertwidth=insertwidth)

    def toggle_caret_cursor_blink(self):
            if self.text_area['insertofftime'] == 0:
                self.text_area.config(insertofftime=300, insertontime=600)
            else:
                self.text_area.config(insertofftime=0, insertontime=0)
    
    def set_caret_cursor_blink_speed(self):
            blink_time = simpledialog.askinteger(
                "Cursor Blink Speed",
                "Enter blink speed in milliseconds (0 for no blink):",
                minvalue=0
            )
            if blink_time is not None:
                self.text_area.config(insertofftime=blink_time, insertontime=blink_time)

#Format
    def change_font(self):
        font_window = tk.Toplevel(self.root)
        font_window.title("Choose Font")
        font_window.geometry("500x310")
        font_listbox = tk.Listbox(font_window, width=30, height=10, exportselection=False)
        font_listbox.pack(side="left", fill="y")
        scrollbar = tk.Scrollbar(font_window, command=font_listbox.yview)
        scrollbar.pack(side="left", fill="y")
        font_listbox.config(yscrollcommand=scrollbar.set)
        preview_text = "The quick brown fox jumps over the lazy dog"
        preview_label = tk.Label(font_window, text=preview_text)
        preview_label.pack(pady=10)
        is_bold = tk.BooleanVar(value=self.config.get("font_bold", False))
        is_italic = tk.BooleanVar(value=self.config.get("font_italic", False))
        font_size = tk.IntVar(value=self.config.get("font_size", 12))
        tk.Checkbutton(font_window, text="Bold", variable=is_bold).pack()
        tk.Checkbutton(font_window, text="Italic", variable=is_italic).pack()
        size_entry = tk.Spinbox(font_window, from_=8, to=72, textvariable=font_size, wrap=True)
        size_entry.pack()

        def update_preview(*args):
            if font_listbox.curselection():
                index = font_listbox.curselection()[0]
                font_name = font_listbox.get(index)
            else:
                font_name = self.config["font_family"]
            bold = 'bold' if is_bold.get() else 'normal'
            italic = 'italic' if is_italic.get() else 'roman'
            size = font_size.get()
            preview_font = font.Font(family=font_name, size=size, weight=bold, slant=italic)
            preview_label.config(font=preview_font)

        def apply_font(*args): 
            self.config["font_family"] = font_listbox.get(font_listbox.curselection()) or self.config.get("font_family", "Arial")
            self.config["font_size"] = font_size.get()
            self.config["font_bold"] = is_bold.get()
            self.config["font_italic"] = is_italic.get()
            self.current_font = font.Font(
                family=self.config["font_family"],
                size=self.config["font_size"],
                weight='bold' if self.config.get("font_bold", False) else 'normal',
                slant='italic' if self.config.get("font_italic", False) else 'roman',
            )
            self.text_area.config(font=self.current_font)
            self.save_config()
            font_window.destroy()
        font_listbox.bind("<<ListboxSelect>>", update_preview)
        is_bold.trace('w', update_preview)
        is_italic.trace('w', update_preview)
        font_size.trace('w', update_preview)
        font_window.bind('<Return>', apply_font)
        for fnt in font.families():
            font_listbox.insert(tk.END, fnt)
        apply_button = tk.Button(font_window, text="Apply", command=apply_font)
        apply_button.pack(pady=10)

        update_preview() 

    def change_font_size(self):
            font_size = simpledialog.askinteger(
                "Font Size", "Enter font size:", initialvalue=self.config["font_size"]
            )
            if font_size:
                self.config["font_size"] = font_size
                self.current_font = font.Font(
                    family=self.config["font_family"],
                    size=font_size,
                    weight="bold" if self.config.get("font_bold", False) else "normal",
                    slant="italic" if self.config.get("font_italic", False) else "roman",
                )
                self.text_area.config(font=self.current_font)
                self.save_config()

    def set_line_spacing(self):
        spacing = simpledialog.askfloat(
            "Line Spacing",
            "Enter line spacing:",
            initialvalue=self.config.get("line_spacing", 4),
        )
        if spacing is not None and spacing > 0:
            self.config["line_spacing"] = spacing
            self.text_area.config(spacing3=spacing)
            self.save_config()
        else:
            messagebox.showerror("Invalid Spacing", "Line spacing must be a positive number.")

    def align_left(self):
            self.text_area.tag_configure("left", justify="left")
            self.apply_tag_to_selection("left")
    
    def align_center(self):
            self.text_area.tag_configure("center", justify="center")
            self.apply_tag_to_selection("center")

    def align_right(self):
            self.text_area.tag_configure("right", justify="right")
            self.apply_tag_to_selection("right")

    def apply_tag_to_selection(self, tag):
            self.clear_alignment_tags()
            start_index = (
                self.text_area.index("sel.first")
                if self.text_area.tag_ranges("sel")
                else "1.0"
            )
            end_index = (
                self.text_area.index("sel.last")
                if self.text_area.tag_ranges("sel")
                else "end"
            )
            self.text_area.tag_add(tag, start_index, end_index)
    
    def clear_alignment_tags(self):
            self.text_area.tag_remove("left", "1.0", "end")
            self.text_area.tag_remove("center", "1.0", "end")
            self.text_area.tag_remove("right", "1.0", "end")

#Settings

    def toggle_root_background_image(self):
            if not self.root_bg_image_visible:
                image_path = filedialog.askopenfilename(
                    filetypes=[("PNG Files", "*.png"), ("GIF Files", "*.gif"), ("All Files", "*.*")]
                )
                if not image_path:
                    return
                try:
                    self.bg_image = tk.PhotoImage(file=image_path)
                    if hasattr(self, 'bg_label'):
                        self.bg_label.configure(image=self.bg_image)
                    else:
                        self.bg_label = tk.Label(self.root, image=self.bg_image)
                        self.bg_label.place(relx=0.5, rely=0.5, anchor='center')
                    self.bg_label.lower()
                    self.root_bg_image_visible = True
                except tk.TclError:
                    messagebox.showerror("Error", "Unsupported image format. Please select a PNG or GIF file.")
            else:
                if hasattr(self, 'bg_label'):
                    self.bg_label.configure(image='')
                    self.root_bg_image_visible = False

    def change_root_bg_color(self):
            color = colorchooser.askcolor(title="Choose root background color")[1]
            if color:
                self.config["root_bg_color"] = color
                self.root.config(bg=color)
                self.save_config()

    def change_text_area_bg_color(self):
        color = colorchooser.askcolor(title="Choose background color")[1]
        if color:
            self.config["bg_color"] = color
            self.text_area.config(bg=color)
            self.frame.config(bg=color)
            self.save_config()

    def change_fg_color(self):
            color = colorchooser.askcolor(title="Choose text color")[1]
            if color:
                self.config["fg_color"] = color
                self.text_area.config(fg=color)
                self.save_config()

    def change_caret_cursor_color(self):
            color = colorchooser.askcolor(title="Choose cursor color")[1]
            if color:
                self.config["caret_cursor_color"] = color
                self.text_area.config(insertbackground=color)
                self.save_config()

    def change_selection_color(self):
            color = colorchooser.askcolor(title="Choose selection color")[1]
            if color:
                self.config["selection_color"] = color
                self.text_area.config(selectbackground=color)
                self.save_config()

    def change_selection_text_color(self):
            color = colorchooser.askcolor(title="Choose selection text color")[1]
            if color:
                self.config["selection_text_color"] = color
                self.text_area.config(selectforeground=color)
                self.save_config()

    def change_border_color(self):
            color = colorchooser.askcolor(title="Choose border color")[1]
            if color:
                self.config["border_color"] = color
                self.text_area.config(highlightbackground=color, highlightcolor=color)
                self.save_config()

    def set_border_thickness(self):
        thickness = simpledialog.askinteger("Set Border Thickness", "Enter border thickness:", minvalue=0)
        if thickness is not None and thickness >= 0:
            self.config["border_thickness"] = thickness
            self.text_area.config(highlightthickness=thickness)
            self.save_config()
        else:
            messagebox.showerror("Invalid Thickness", "Border thickness must be a non-negative integer.")

    def set_caret_cursor_thickness(self):
        thickness = simpledialog.askinteger("Caret Cursor Thickness", "Enter caret cursor thickness:", initialvalue=self.config.get("insertwidth", 2), minvalue=1)
        if thickness is not None and thickness > 0:
            self.config["insertwidth"] = thickness
            self.text_area.config(insertwidth=thickness)
            self.save_config()
        else:
            messagebox.showerror("Invalid Thickness", "Caret cursor thickness must be a positive integer.")

    def reset_to_default_theme(self):
                if os.path.exists(self.config_file):
                    os.remove(self.config_file)
                self.config = self.default_config.copy()
                self.apply_config()
                self.save_config()
                messagebox.showinfo("Reset to Default", "The theme has been reset to default.")

    def apply_config(self):
                self.root.config(bg=self.config["root_bg_color"])

                current_font = font.Font(family=self.config["font_family"],
                                        size=self.config["font_size"],
                                        weight="bold" if self.config["font_bold"] else "normal",
                                        slant="italic" if self.config["font_italic"] else "roman")
                self.text_area.config(font=current_font,
                                    bg=self.config["bg_color"],
                                    fg=self.config["fg_color"],
                                    insertbackground=self.config["caret_cursor_color"],
                                    selectbackground=self.config["selection_color"],
                                    selectforeground=self.config["selection_text_color"],
                                    highlightbackground=self.config["border_color"],
                                    highlightcolor=self.config["border_color"],
                                    spacing3=self.config["line_spacing"],
                                    highlightthickness=self.config["border_thickness"],
                                    insertwidth=self.config["insertwidth"])

                self.frame.config(width=self.config["text_width"], height=self.config["text_height"])
                self.frame.pack_propagate(False) 
                self.text_area.config(width=self.config["text_width"], height=self.config["text_height"])
    
    def toggle_auto_save(self):
            if self.auto_save_enabled.get():
                messagebox.showinfo("Autosave Enabled", "Autosave feature has been enabled.")
            else:
                messagebox.showinfo("Autosave Disabled", "Autosave feature has been disabled.")

    def show_about(self):
        messagebox.showinfo("About ZenEdit", "ZenEdit v1.0\nA simple text editor built with Tkinter. by Seehrum")

    def toggle_text_blink(self, event=None):
        if hasattr(self, 'is_blinking') and self.is_blinking:
            self.is_blinking = False
            if hasattr(self, 'blink_id'):
                self.root.after_cancel(self.blink_id)
                del self.blink_id
            self.text_area.tag_remove("blink", "1.0", "end")
        else:
            blink_speed = simpledialog.askinteger("Blink Speed", "Enter blink speed in milliseconds:", initialvalue=500)
            if blink_speed is not None:
                self.blink_speed = blink_speed
                self.is_blinking = True
                self.start_blinking()

    def start_blinking(self):
        if not self.is_blinking:
            return
        bg_color = self.config["bg_color"]
        fg_color = self.config["fg_color"]

        current_fg_color = self.text_area.tag_cget("blink", "foreground")
        new_color = fg_color if current_fg_color == bg_color else bg_color

        self.text_area.tag_configure("blink", foreground=new_color, background=bg_color)
        self.text_area.tag_add("blink", "1.0", "end")

        self.blink_id = self.root.after(self.blink_speed, self.start_blinking)

    def toggle_menu_view(self):
        if not self.fullScreenState:
            if self.root.cget('menu'):
                self.root.config(menu='') 
            else:
                self.root.config(menu=self.menu)

    def save_config(self):
        with open(self.config_file, 'w') as file:
            json.dump(self.config, file, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    editor = ZenEdit(root)
    root.protocol("WM_DELETE_WINDOW", editor.quit)
    root.mainloop()
            