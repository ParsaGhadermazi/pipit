from textual.app import App
from textual.widgets import (Header,
                             Footer,
                             ListItem,
                             ListView,
                             TextArea,
                             Button,
                             DataTable,
                             Input,
                             DirectoryTree,
                             Static,
                             Collapsible,
                             Select,
                             MarkdownViewer,
                              TabbedContent,
                             Label)
import bioplumber
from textual.screen import Screen
from textual.containers import Container,Horizontal,Vertical
from bioplumber import (configs,
                        bining,
                        files,
                        qc,
                        assemble,
                        slurm,
                        abundance,
                        taxonomy,
                        alignment,
                        dereplication)
from textual import on, work
from textual.binding import Binding
from textual.validation import Number
import math
import json
import os
import pandas as pd
import inspect
import datetime
import pathlib
import shutil

    
class DirectoryReference(Container):
    def compose(self):
        yield Vertical(
        Container(
                Vertical(
                    Input(placeholder="Base Directory",id="base_dir_input"),
                    DirectoryTree("/",id="folder_tree"),
                    TextArea(id="selected_dir")
                        )
                ))
    
    def on_input_changed(self, event: Input.Changed):
        try:
            self.query_one("#folder_tree").path=event.value
        except Exception as e:
            pass
    
    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected):
        self.query_one("#selected_dir").text=str(event.path)
        

class MGRScreen(Screen):
    
    def compose(self):
        yield Vertical(
            Header(show_clock=True),
            Horizontal(TextArea.code_editor(text="",
                                            language="python",
                                            id="io_code_editor",
                                            show_line_numbers=True),
                                            DirectoryReference(id="dir_ref")),
            Horizontal(
                 Input(placeholder="Variable Name",id="variable_input_render")
                 ,Button("Render Variable",id="render_button"),
                 id="render_variable"
            ),
            DataTable(id="output_text"),
            Horizontal(
                 Input(placeholder="Save Directory",id="variable_input_save"),
                 Button("Save",id="save_button"),
                 id="save_variable"
            ),
            Footer()    
            )
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "render_button":
            try:
            
                code = self.query_one("#io_code_editor").text
                variable=self.query_one("#variable_input_render").value
                sc={}
                exec(code,locals=sc)
                data=sc[variable]
                if isinstance(data, pd.DataFrame):
                    temp_data = data.to_dict(orient="list")
                    table = self.query_one("#output_text")
                    table.remove_children()
                    table.clear(columns=True)
                    table.add_columns(*[str(i) for i in temp_data.keys()])
                    table.add_rows(list(zip(*temp_data.values())))

                else:
                    table=self.query_one("#output_text")
                    table.remove_children()
                    table.clear(columns=True) 
                    table.add_columns("Variable Name","Value")
                    table.add_rows([(variable,data)])
                    
                    
            except Exception as e:
                self.query_one("#output_text").mount(TextArea(text=f"Error rendering variable\n{e}"))
                
        if event.button.id == "save_button":
            try:
                code = self.query_one("#io_code_editor").text
                variable=self.query_one("#variable_input_render").value
                sc={}
                exec(code,locals=sc)
                data=sc[variable]
                if isinstance(data, pd.DataFrame):
                    data.to_csv(self.query_one("#variable_input_save").value,index=False)
                else:
                    with open(self.query_one("#variable_input_save").value,"w") as f:
                        f.write(str(data))
            except Exception as e:
                self.query_one("#output_text").mount(TextArea(text=f"Error saving variable\n{e}"))
           
        
        

class FileManager(App):
    CSS_PATH = "tui_css.tcss"
    
    def on_mount(self):
        self.theme="gruvbox"
        self.push_screen(MGRScreen(),"mgr-screen" )

def main():
    mgr=FileManager()
    mgr.run()
    
if __name__ == '__main__':
    main()


