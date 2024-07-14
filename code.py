from tkinter import *
import tkinter as tk
import pymsgbox
from tkinter import messagebox
from tkinter import filedialog, colorchooser
from datetime import datetime
from pathlib import Path
import re
import json
import ctypes
import os
import customtkinter 
from tklinenums import TkLineNumbers
from typing import Tuple
from pynput.keyboard import Controller,Key

class TkLineNumbers(tk.Canvas):
    def __init__(self, master, textwidget, *args, **kwargs):
        """
        Initializes the TkLineNumbers widget.

        Parameters:
        master (tk.Widget): The parent widget.
        textwidget (tk.Text): The text widget for which line numbers are displayed.
        *args: Additional positional arguments passed to the Canvas constructor.
        **kwargs: Additional keyword arguments passed to the Canvas constructor.
            - font (tuple): The font used for line numbers. Default is ('Times New Roman', 12).
            - width (int): The width of the line number canvas. Default is 40.
            - colors (tuple): A tuple containing two color values. The first color is used for line numbers, and the second color is a secondary color. Default is ("#C79D50", "#808080").
        """
        super().__init__(master, *args, **kwargs)
        self.text_widget = textwidget
        self.font = kwargs.get('font', ('Times New Roman', 12))  # Adjust font size as needed
        self.width = kwargs.get('width', 50)  # Adjust the width of line numbers as needed
        self.colors = kwargs.get('colors', ("#C77F50", "#808080"))  # Colors for line numbers  # Colors for line number

    def configure_font(self, font):
    
        self.font = font
        self.redraw()

    def redraw(self, *args):
        self.delete("all")
        i = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(self.width, y, anchor="ne", text=linenum, font=self.font, fill=self.colors[0])
            i = self.text_widget.index(f"{i}+1line")
        
        self.config(width=self.width)  # Adjust the canvas width



class CompilerApp:

    def __init__(self) -> None:

        self.root = Tk()
        self.shown = 0
        self.root.title(string="Python Compiler")
        self.root.state(newstate="zoomed")
        self.control = Controller()

        # Buttons and Widgets
        customtkinter.CTkButton(master=self.root, width=100, height=30, corner_radius=20, text="Open", command=self.open).place(x=0, y=2)
        customtkinter.CTkButton(master=self.root, width=100, height=30, corner_radius=20, text="Save", command=self.save).place(x=100, y=2)
        customtkinter.CTkButton(master=self.root, width=100, height=30, corner_radius=20, text="Change color", command=self.change_color).place(x=200, y=2)
        customtkinter.CTkButton(master=self.root, width=100, height=30, corner_radius=20, text="Clear Code", command=self.clear_code).place(x=305, y=2)
        customtkinter.CTkButton(master=self.root, width=90, height=30, corner_radius=20, text="Run", command=self.run_code).place(x=405, y=2)

        self.option = IntVar(master=self.root)
        customtkinter.CTkCheckBox(master=self.root, width=30, height=30, text_color="#000000", text="Ignore case",
                                  onvalue=1, variable=self.option, command=self.search_word).place(x=500, y=2)
        
        self.search_box = customtkinter.CTkEntry(master=self.root, width=250, height=30, corner_radius=20, placeholder_text="Search")
        self.search_box.place(x=600, y=2)
        self.search_box.bind("<KeyRelease>", self.search_word)
        self.search_box.bind("<Return>",self.show)
        self.search_box.bind("<FocusOut>",self.set_show)

        self.count = customtkinter.CTkLabel(master=self.root, width=30, height=30, corner_radius=50, fg_color="#808080", text="0")
        self.count.place(x=850, y=2)

        self.replace_box = customtkinter.CTkEntry(master=self.root, width=250, height=30, corner_radius=20, placeholder_text="Replace")
        self.replace_box.place(x=970, y=2)

        customtkinter.CTkButton(master=self.root, width=100, height=30, corner_radius=20, text="Replace", command=lambda: self.replace(replace_all=False)).place(x=1220, y=2)
        customtkinter.CTkButton(master=self.root, width=100, height=30, corner_radius=20, text="Replace All", command=lambda: self.replace(replace_all=True)).place(x=1320, y=2)
        customtkinter.CTkButton(master=self.root, width=100, height=30, corner_radius=20, text="Clear Terminal", command=self.clear_terminal).place(x=1420, y=2)

        self.main = customtkinter.CTkTextbox(master=self.root, width=1480, height=808, corner_radius=15,
                                             border_color="#50C777", bg_color="#50C777", text_color="#4fb5bd", border_width=5, 
                                             font=("TimesNewRoman", 20), activate_scrollbars=True, undo=True, wrap='none')
        self.main.insert(index=1.0, text='print("Hello world")')
        self.main.bind("<KeyPress>", self.check_for_brackets)
        self.main.bind("<KeyRelease>", self.search_word)
        self.main.bind("<Control-/>", self.comments)
        self.main.bind("<BackSpace>",self.backspace)
        self.main.bind("<Shift-Tab>",self.hot_key_shift_tab)
        self.main.bind("<Return>",self.enter_key)
        self.main.bind("<<Paste>>",self.on_paste)
        self.main.place(x=55, y=35)

        self.line_numbers = TkLineNumbers(master=self.root, textwidget=self.main)
        self.line_numbers.place(x=0, y=55,width=55,height=785)
        self.every_100_ms()

        self.root.bind("<Control-s>",self.save)
        self.root.bind("<Control-o>",self.open)
        self.root.protocol("WM_DELETE_WINDOW",self.on_close)

        self.root.mainloop()

    def on_close(self) -> None:
        tilte = self.root.title()
        if tilte == "Python Compiler":
            x = pymsgbox.confirm(text="Text not saved\n Do you want to save",icon=pymsgbox.WARNING)
            if x == "Cancel":
                self.root.destroy()

            
        self.save()
        self.root.destroy()
            
    def every_100_ms(self) -> None:
        "calls every_100_ms"
    
        self.line_numbers.redraw()
        self.main.after(100,self.every_100_ms)

    def check_for_brackets(self, event: tk.Event) -> None:
        """
        Automatically inserts the closing bracket or quote when an opening bracket or quote is typed.
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

        elif event.keycode == 9: # tab keypress
            current_row_index,current_column_index = self.main.index(tk.INSERT).split(".")
            try:
                index1 = int(self.main.index(SEL_FIRST).split(".")[0])
                index2 = int(self.main.index(SEL_LAST).split(".")[0]) + 1

                for i in range(index1, index2):
                    self.main.insert(index=f"{i}.0", text=" "*4)
                
            except Exception as e:
                self.main.insert(index=index1, text=" "*4)
            
            finally:
                return "break"
        

        self.main.mark_set(mark=tk.INSERT, index=index1)
        self.main.focus()

    def information(self) -> Tuple[str,str,str,str]:
        """
        Returns the information at the selected index
        """
        current_row_index,current_column_index = self.main.index(tk.INSERT).split('.')
        text = self.main.get(f"{current_row_index}.0", f"{current_row_index}.end")
        indent = re.match(pattern=r"\s*",string=text).group()

        return(current_row_index,current_column_index,text,indent)
    def backspace(self, event:Event) -> None:
        
        current_row_index,current_column_index,text,indent = self.information()

        self.is_indent = False
        if indent.count(" "):
            self.is_indent = True

        if text.strip() == "" and self.is_indent:
            self.control.press(Key.shift_l)
            self.control.press(Key.tab)

            self.control.release(Key.shift_l)
            self.control.release(Key.tab)
    def on_paste(self,event:Event) -> None:
        self.control.tap(Key.enter)
    def enter_key(self, event:Event) -> str:

        current_row_index,current_column_index,text,indent = self.information()

        self.is_indent = False
        if indent.count(" "):
            self.is_indent = True

        index1 = f"{current_row_index}.{current_column_index}"
        check_for_colun = current_row_index + "." + str(int(current_column_index)-1)

        if self.main.get(index1=check_for_colun) == ":":
            self.main.insert(index=index1, text="\n" + indent + " " * 4)
        else:
            white_spaces_count = indent.count(" ")
            if text.strip() != "" and not self.is_indent:
                self.main.insert(index=index1, text="\n")
            else:
                self.main.insert(index=index1, text="\n" + " "*white_spaces_count)

            self.main.see(index=index1)
            self.main.focus()

            self.is_indent = False    
       
        return "break"
    def hot_key_shift_tab(self,event:Event) -> str:

        current_row_index,current_column_index,text,indent = self.information()

        try:
            index1 = int(self.main.index(SEL_FIRST).split(".")[0])
            index2 = int(self.main.index(SEL_LAST).split(".")[0]) + 1
        except Exception as e:
            index1 = int(current_row_index)
            index2 = int(current_row_index) + 1
        finally:
            for i in range(index1, index2):
                text = self.main.get(index1=f"{i}.0", index2=f"{i}.end")
                indent = re.match(pattern=r"\s{0,}",string=text).group()

                total_whitespcaes = indent.count(" ")
                rem = total_whitespcaes % 4
                removing_whitespaces = 4 if rem == 0 else rem
        
                after_replacement,_ = re.subn(pattern=r"\s", repl="", string=text, count=removing_whitespaces)
                self.main.delete(index1=f"{i}.0", index2=f"{i}.end")
                self.main.insert(index=f"{i}.0", text=after_replacement)

            return "break"

    def replace(self, replace_all: bool = False) -> None:
        """
        Replaces occurrences of the search string with the replacement string in the main text box.
        """
        text = self.main.get(index1="1.0", index2=END)
        original_string = self.adding_backslashes()
        replacement_string = self.replace_box.get()
        
        if replacement_string == "" or original_string == "" or text == "":
            return
        
        self.main.focus()
        total_lines = float(self.main.index(END))
        for i in range(1, int(total_lines)):

            line = self.main.get(str(i) + '.0', str(i) + '.end')

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

    def comments(self, event: tk.Event = None) -> str:
        """
        Toggles comments on the selected lines in the main text box.
        """
        current_row_index,current_column_index,text,indent = self.information()

        if text.strip() == "":
            return "break"

        try:
            index1 = int(self.main.index(SEL_FIRST).split(".")[0])
            index2 = int(self.main.index(SEL_LAST).split(".")[0]) + 1
        except Exception as e:
            index1 = int(current_row_index)
            index2 = int(current_row_index) + 1
        finally:
            for i in range(index1, index2):
                text = self.main.get(index1=f"{i}.0", index2=f"{i}.end")

                if text.startswith("# "):
                    self.main.delete(index1=f"{i}.0", index2=f"{i}.2")
                else:
                    self.main.insert(index=f"{i}.0", text="# ")
            return "break"

    def run_code(self) -> None:
        """
        Executes the code written in the main text box and displays the output in the terminal text box.
        """
        code_text = self.main.get(index1="1.0", index2=END)

        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd != 0:
            # Bring the window to the foreground
            ctypes.windll.user32.ShowWindow(hwnd, 5)  # SW_SHOW
            ctypes.windll.user32.SetForegroundWindow(hwnd)
        
        print(">> ",end="")
        exec(code_text)
        print()

    def clear_terminal(self) -> None:
        """
        Clears the terminal text box.
        """
        os.system("cls")
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
            print(str(e))

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
    
    def show(self,event):
        l = self.get_indexes()
        self.main.see(index=l[self.shown])
        self.shown += 1
        if self.shown == len(self.get_indexes()):
            self.set_show()
    
    def set_show(self,event:Event=None):
        self.shown = 0
    
    def get_indexes(self) -> list[int]:
        l = []
        search_text = self.adding_backslashes()
        total_lines = float(self.main.index(END))
        for i in range(1, int(total_lines)):
            line_text = self.main.get(f"{i}.0", f"{i}.end")
            flags = re.MULTILINE if self.option.get() == 0 else re.IGNORECASE | re.MULTILINE
            for match in re.finditer(search_text, line_text, flags=flags):
                index1 = f"{i}.{match.start()}"
                index2 = f"{i}.{match.end()}"
                l.append(index1)
        
        return l
            
    def search_word(self, event: tk.Event = None) -> None:
        """
        Highlights occurrences of the search string in the main text box and updates the count label.
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

    def save(self,event:Event=None,) -> None:
        """
        Saves the content of the main text box to a Python file and associated tags to a JSON file.
        """
        try:
            if self.root.title() == "Python Compiler":
                self.code_file_path = filedialog.asksaveasfile(mode='w', defaultextension=".py", title="Save Python File", filetypes=[("Python", "*.py")]).name
                self.json_file_path = self.generate_json_file(self.code_file_path)

            self.root.title(string=Path(self.code_file_path).name)

            code_text = self.main.get(index1="1.0", index2=END)

            with open(self.code_file_path, 'w') as code_file:
                code_file.write(code_text)

            tag_data = []
            for tag_name in self.main.tag_names():
                if tag_name not in ["sel", "found"] and self.main.tag_ranges(tagName=tag_name):
                    
                    fg_color = self.main.tag_cget(tagName=tag_name, option="foreground")
                    index1,index2 = self.main.tag_ranges(tagName=tag_name)
                    tag_data.append({"tag": tag_name, "range": (str(index1),str(index2)), "fg": fg_color})

            with open(self.json_file_path, "w") as json_file:
                json.dump(obj=tag_data, fp=json_file)

        except Exception as e:
            print(str(e))

    def generate_json_file(self, code_file_path: str) -> str:
        """
        Generates a JSON file path based on the provided code file path.
        Returns:
        str: Path to the corresponding JSON file.
        """
        base_path = os.path.dirname(code_file_path)
        json_file_name = Path(code_file_path).stem + ".json"
        json_file_path = os.path.join(base_path, json_file_name)
        return json_file_path

    def open(self,event:Event=None) -> None:
        """
        Opens a Python file and associated tags from a JSON file into the main text box.
        """
        try:
            self.code_file_path = filedialog.askopenfile(mode='r', title="Open Python File", filetypes=[("Python", "*.py")]).name
            self.json_file_path = self.generate_json_file(self.code_file_path)

            self.root.title(string=Path(self.code_file_path).name)

            with open(self.code_file_path, 'r') as code_file:
                code_text = code_file.read()
                self.main.delete(index1="1.0", index2=END)
                self.main.insert(index="1.0", text=code_text)

            with open(self.json_file_path, "r") as json_file:
                tag_data = json.load(json_file)
                for tag_info in tag_data:
                    tag_name = tag_info['tag']
                    index1,index2 = tag_info['range']
                    fg_color = tag_info['fg']

                    self.main.tag_add(tagName=tag_name,index1=index1,index2=index2)
                    self.main.tag_config(tagName=tag_name, foreground=fg_color)
                    
            self.main.see(END)
        except Exception as e:
            print(str(e))

if __name__ == "__main__":
    CompilerApp()
