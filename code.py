from tkinter import *
import tkinter as tk
from tkinter import filedialog, colorchooser
from datetime import datetime
from pathlib import Path
import re
import json
import io
import sys
import os
import customtkinter 

class CompilerApp:
    """
    Python Compiler GUI application using Tkinter.
    """

    def __init__(self) -> None:
        """
        Initializes the compiler GUI application.
        Sets up the main window, buttons, text boxes, and other widgets.
        """
        self.root = Tk()
        self.root.title(string="Python Compiler")
        self.root.state(newstate="zoomed")

        # Buttons and Widgets
        customtkinter.CTkButton(master=self.root, width=150, height=30, corner_radius=20, text="Change color", command=self.change_color).place(x=10, y=2)
        customtkinter.CTkButton(master=self.root, width=150, height=30, corner_radius=20, text="Clear Code", command=self.clear_code).place(x=165, y=2)
        customtkinter.CTkButton(master=self.root, width=150, height=30, corner_radius=20, text="Run", command=self.run_code).place(x=320, y=2)

        self.option = IntVar(master=self.root)
        customtkinter.CTkCheckBox(master=self.root, width=30, height=30, text_color="#000000", text="Ignore case",
                                  onvalue=1, variable=self.option, command=self.search_word).place(x=625, y=2)
        
        self.search_box = customtkinter.CTkEntry(master=self.root, width=250, height=30, corner_radius=20, placeholder_text="Search")
        self.search_box.place(x=725, y=2)
        self.search_box.bind("<KeyRelease>", self.search_word)

        self.count = customtkinter.CTkLabel(master=self.root, width=30, height=30, corner_radius=50, fg_color="#808080", text="0")
        self.count.place(x=910, y=35)

        self.replace_box = customtkinter.CTkEntry(master=self.root, width=250, height=30, corner_radius=20, placeholder_text="Replace")
        self.replace_box.place(x=975, y=2)

        customtkinter.CTkButton(master=self.root, width=150, height=30, corner_radius=20, text="Clear Terminal", command=self.clear_terminal).place(x=1380, y=2)

        self.main = customtkinter.CTkTextbox(master=self.root, width=900, height=800, corner_radius=15,
                                             border_color="#000000", bg_color="#808080", text_color="#4fb5bd", font=("TimesNewRoman", 20),
                                             activate_scrollbars=True, undo=True, wrap='none')
        self.main.insert(index=1.0, text='print("Hello world")')
        self.main.bind("<KeyPress>", self.check_for_brackets)
        self.main.bind("<KeyRelease>", self.search_word)
        self.main.bind("<Control-/>", self.commands)
        self.main.place(x=10, y=35)

        customtkinter.CTkButton(master=self.root, width=150, height=30, corner_radius=20, text="Replace", command=lambda: self.replace(replace_all=False)).place(x=910, y=80)
        customtkinter.CTkButton(master=self.root, width=150, height=30, corner_radius=20, text="Replace All", command=lambda: self.replace(replace_all=True)).place(x=910, y=120)
        customtkinter.CTkButton(master=self.root, width=150, height=30, corner_radius=20, text="Save", command=self.save).place(x=910, y=200)
        customtkinter.CTkButton(master=self.root, width=150, height=30, corner_radius=20, text="Open", command=self.open).place(x=910, y=240)

        self.terminal = customtkinter.CTkTextbox(master=self.root, width=500, height=800, corner_radius=15,
                                                 text_color="#FFFFFF", font=("TimesNewRoman", 20), state=DISABLED)
        self.terminal.place(x=1060, y=35)

        self.root.mainloop()

    def check_for_brackets(self, event: tk.Event) -> None:
        """
        Automatically inserts the closing bracket or quote when an opening bracket or quote is typed.
        
        Parameters:
        event (tk.Event): The event object containing information about the key press event.
        """
        index1 = self.main.index(tk.INSERT)

        if event.char == "[":
            self.main.insert(index1, text=']')
        elif event.char == "(":
            self.main.insert(index1, text=')')
        elif event.char == '{':
            self.main.insert(index1, text='}')
        elif event.char == '"':
            self.main.insert(index1, text='"')
        elif event.char == "'":
            self.main.insert(index1, text="'")
        elif event.char == "`":
            self.main.insert(index1, text="`")
        elif event.char == ":":
            current_line_index = self.main.index(tk.INSERT).split('.')[0]
            indent = re.match(r"\s*", self.main.get(f"{current_line_index}.0", f"{current_line_index}.end")).group()
            self.main.insert(index1, ":\n" + indent + " " * 4)

        self.main.mark_set(mark=tk.INSERT, index=index1)
        self.main.focus()

    def replace(self, replace_all: bool = False) -> None:
        """
        Replaces occurrences of the search string with the replacement string in the main text box.
        
        Parameters:
        replace_all (bool): If True, replaces all occurrences. If False, replaces only the first occurrence.
        """
        text = self.main.get(index1="1.0", index2=END)
        original_string = self.adding_backslashes()
        replacement_string = self.replace_box.get()
        
        if replacement_string == "" or original_string == "":
            return
        
        total_lines = float(self.main.index(END))
        for i in range(1, int(total_lines)):

            line = self.main.get(str(i) + '.0', str(i) + '.end')

            if text != "":
                flags = re.MULTILINE if self.option.get() == 0 else re.IGNORECASE | re.MULTILINE
                for _ in re.finditer(pattern=original_string, string=line, flags=flags):
                    if _.string != "":
                        index1 = f"{i}.{_.start()}"
                        index2 = f"{i}.{_.end()}"

                        self.main.see(index=index2)
                        self.main.delete(index1=index1, index2=index2)
                        self.main.insert(index=index1, text=replacement_string)

                        self.search_word()  # update the counter
                        if not replace_all:
                            return  # for single replacement

        if self.count.cget("text") == "0":
            self.search_box.delete(first_index=0, last_index=END)
            self.replace_box.delete(first_index=0, last_index=END)
            self.main.focus()

    def commands(self, event: tk.Event = None) -> None:
        """
        Toggles comments on the selected lines in the main text box.
        
        Parameters:
        event (tk.Event): The event object containing information about the key press event.
        """
        try:
            index1 = int(self.main.index(SEL_FIRST).split(".")[0])
            index2 = int(self.main.index(SEL_LAST).split(".")[0]) + 1

            for i in range(index1, index2):
                text = self.main.get(index1=f"{i}.0", index2=f"{i}.end")

                if text.startswith("# "):
                    self.main.delete(index1=f"{i}.0", index2=f"{i}.2")
                else:
                    self.main.insert(index=f"{i}.0", text="# ")

        except Exception as e:
            self.print_to_terminal(str(e))

    def run_code(self) -> None:
        """
        Executes the code written in the main text box and displays the output in the terminal text box.
        """
        code_text = self.main.get(index1="1.0", index2=END)
        
        # Redirect stdout to capture print statements
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()
        try:
            exec(code_text)
        except Exception as e:
            self.print_to_terminal(str(e))
        else:
            self.terminal.configure(state=NORMAL)
            self.terminal.insert(index=END, text=f">> {redirected_output.getvalue()}\n")
            self.terminal.configure(state=DISABLED)
        
        # Reset stdout redirect.
        sys.stdout = old_stdout

    def clear_terminal(self) -> None:
        """
        Clears the terminal text box.
        """
        self.terminal.configure(state=NORMAL)
        self.terminal.delete(index1="1.0", index2=END)
        self.terminal.configure(state=DISABLED)

    def clear_code(self) -> None:
        """
        Clears the main text box.
        """
        self.main.delete(index1="1.0", index2=END)

    def change_color(self) -> None:
        """
        Changes the color of the selected text or the entire text in the main text box.
        """
        try:
            selected_text = self.main.selection_get()
            index1 = self.main.index(SEL_FIRST)
            index2 = self.main.index(SEL_LAST)
        except Exception as e:
            selected_text = None
            self.print_to_terminal(str(e))

        rgb_color, hex_color = colorchooser.askcolor(title="Select Color")
        
        if not hex_color:
            return
        
        if selected_text:
            tag_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.main.tag_add(tagName=tag_name, index1=index1, index2=index2)
            self.main.tag_config(tagName=tag_name, foreground=hex_color)
        else:
            self.main.configure(text_color=hex_color)

    def adding_backslashes(self) -> str:
        """
        Adds backslashes to special characters in the search string to escape them.
        
        Returns:
        str: The escaped search string.
        """
        search_text = self.search_box.get()
        escaped_text = re.escape(search_text)
        return escaped_text

    def search_word(self, event: tk.Event = None) -> None:
        """
        Highlights occurrences of the search string in the main text box and updates the count label.
        
        Parameters:
        event (tk.Event): The event object containing information about the key press event.
        """
        count = 0
        self.main.tag_remove(tagName="found", index1="1.0", index2=END)

        search_text = self.adding_backslashes()

        total_lines = float(self.main.index(END))
        for i in range(1, int(total_lines)):
            
            line_text = self.main.get(f"{i}.0", f"{i}.end")
            
            if search_text != "":
                flags = re.MULTILINE if self.option.get() == 0 else re.IGNORECASE | re.MULTILINE
                for match in re.finditer(search_text, line_text, flags=flags):
                    index1 = f"{i}.{match.start()}"
                    index2 = f"{i}.{match.end()}"
                    count += 1
                    self.main.tag_add(tagName="found", index1=index1, index2=index2)
                    self.main.tag_config(tagName="found", background="yellow")

        self.count.configure(text=f"{count:,}")

    def save(self) -> None:
        """
        Saves the content of the main text box to a Python file and associated tags to a JSON file.
        """
        try:
            code_file_path = filedialog.asksaveasfile(mode='w', defaultextension=".py", title="Save Python File", filetypes=[("Python", "*.py")]).name
            json_file_path = self.generate_json_file(code_file_path)

            code_text = self.main.get(index1="1.0", index2=END)

            with open(code_file_path, 'w') as code_file:
                code_file.write(code_text)

            tag_data = []
            for tag_name in self.main.tag_names():
                if tag_name not in ["sel", "found"]:
                    fg_color = self.main.tag_cget(tagName=tag_name, option="foreground")
                    tag_range = self.main.tag_ranges(tagName=tag_name)
                    tag_data.append({"tag": tag_name, "range": tag_range, "fg": fg_color})

            with open(json_file_path, "w") as json_file:
                json.dump(obj=tag_data, fp=json_file)

        except Exception as e:
            self.print_to_terminal(str(e))

    def generate_json_file(self, code_file_path: str) -> str:
        """
        Generates a JSON file path based on the provided code file path.

        Parameters:
        code_file_path (str): Path to the Python code file.

        Returns:
        str: Path to the corresponding JSON file.
        """
        base_path = os.path.dirname(code_file_path)
        json_file_name = Path(code_file_path).stem + ".json"
        json_file_path = os.path.join(base_path, json_file_name)
        return json_file_path

    def open(self) -> None:
        """
        Opens a Python file and associated tags from a JSON file into the main text box.
        """
        try:
            code_file_path = filedialog.askopenfile(mode='r', title="Open Python File", filetypes=[("Python", "*.py")]).name
            json_file_path = self.generate_json_file(code_file_path)

            with open(code_file_path, 'r') as code_file:
                code_text = code_file.read()
                self.main.delete(index1="1.0", index2=END)
                self.main.insert(index="1.0", text=code_text)

            with open(json_file_path, "r") as json_file:
                tag_data = json.load(json_file)
                for tag_info in tag_data:
                    tag_name = tag_info['tag']
                    index1,index2 = tag_info['range']
                    fg_color = tag_info['fg']

                    self.main.tag_add(tagName=tag_name,index1=index1,index2=index2)
                    self.main.tag_config(tagName=tag_name, foreground=fg_color)

        except Exception as e:
            self.print_to_terminal(str(e))

    def print_to_terminal(self, message: str) -> None:
        """
        Prints a message to the terminal text box.
        
        Parameters:
        message (str): The message to print.
        """
        self.terminal.configure(state=NORMAL)
        self.terminal.insert(index=END, text=f">> {message}\n\n")
        self.terminal.configure(state=DISABLED)

    def recursive(self, path: Path) -> str:
        """
        Recursive function to handle file paths.

        Parameters:
        path (Path): Path to process.

        Returns:
        str: Processed path.
        """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath('.')

        return os.path.join(base_path, path)

if __name__ == "__main__":
    CompilerApp()
