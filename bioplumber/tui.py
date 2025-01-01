from textual.app import App
from textual.widget import Widget
from textual.widgets import (Header,
                             Footer,
                             Tabs,
                             Tab,
                             ListItem,
                             ListView,
                             TextArea,
                             Button,
                             DataTable,
                             Rule,
                             Static,
                             SelectionList,
                             Label)

from textual.screen import Screen
import bioplumber
from textual.widgets.selection_list import Selection
from textual.containers import Container,Horizontal,Vertical,Grid
from bioplumber import (configs,
                        bining,
                        files,
                        qc,
                        assemble,
                        slurm,
                        alignment)
import json
import os
import pandas as pd
import inspect

def get_available_functions():
    am=[]
    for module in [bining,files,qc,assemble,alignment]:
        am.append((module.__name__,[i for i in dir(module) if i.endswith("_") and not i.startswith("__")]))
    return dict(am)
        
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
editor_text="#add your functions here below\nimport pandas as pd\nio_table=pd.DataFrame({'col1':[1,2,3],'col2':[4,5,6]})"
avail_modules=get_available_functions()
funcs_tobe_used=None
func_match_text="{}"

io_table_data=None
def main():
    app = Bioplumber()
    app.run()




            
class EditableFileViewer(Container):
    """Widget to edit and save the contents of a text file."""

    def __init__(self, file_path: str, **kwargs):
        super().__init__(**kwargs)
        self.file_path = file_path
        self.text_area = TextArea(id="slurm_editor")  # Editable area
        self.save_button = Button("Save", id="save_button")
        
    def on_mount(self):
        """Load the file content into the text area."""
        self.mount(self.text_area, self.save_button)

        try:
            with open(self.file_path, "r") as file:
                content = file.read()
            self.text_area.text = content
        except Exception as e:
            self.text_area.text = f"Error loading file: {e}"

    def on_button_pressed(self, event: Button.Pressed):
        """Handle save button click."""
        if event.button.id == "save_button":
            try:
                with open(self.file_path, "w") as file:
                    file.write(self.text_area.text)
                self.text_area.insert("File saved successfully!\n",(0,0),  maintain_selection_offset=False)
            except Exception as e:
                self.text_area.insert( f"Error saving file: {e}\n",(0,0), maintain_selection_offset=False)
                

class SlurmManager(Container):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def on_mount(self):
        try:
            data=slurm.query_squeue()
            table=DataTable()
            table.add_columns(*[i for i in data.keys()])
            table.add_rows(list(zip(*data.values())))
            self.mount(table)

        except Exception as e:
            self.mount(Label(f"[bold white]Make sure you have access slurm[red]\nlog:\n[red]{e}"))
    
class TabManager(Tabs):
    
    def compose(self):
        yield Tabs(
            Tab("Input/Output", id="io"),
            Tab("Script generator", id="sg"),
            Tab("Slurm template", id="st"),
            Tab("Operation", id="op"),
            Tab("Job monitor", id="jm"),
            id="all_tabs"
        )

class IOManager(Container):

    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._submitted_io_table = None
        
    def on_mount(self):
        
        self.mount(
            Vertical(
                Horizontal(
                        TextArea.code_editor(editor_text,
                                             language="python",
                                             id="io_code_editor",
                                             ),
                        DataTable(id="io_table"),
                        id="io_area"
                        ),
                Horizontal(
                    Button("Save Script", id="io_save"),
                    Button("Render I/O table", id="io_render"),
                    Button("Submit I/O table", id="io_submit"),
                    id="io_buttons")
                    )   
        )
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "io_render":
            try:
                code = self.query_one("#io_code_editor").text
                exec(code)
                data = locals()["io_table"].to_dict(orient="list")
                self._temp_data = data.copy()
                table = self.query_one("#io_table")
                table.remove_children()
                table.clear(columns=True)  # Clear the existing data
                table.add_columns(*[i for i in data.keys()])
                table.add_rows(list(zip(*data.values())))
            except Exception as e:
                table=self.query_one("#io_table")
                table.remove_children()
                table.mount(TextArea(text=f"Error rendering table\n{e}"))
        
        elif event.button.id == "io_submit":
            global editor_text
            global io_table_data
            try:
                code = self.query_one("#io_code_editor").text
                exec(code)
                io_table_data =locals()["io_table"].to_dict(orient="list")
                table = self.query_one("#io_table")
                table.remove_children()
                table.mount(Container(Static("[green]Table submitted successfully!",)))
            except Exception as e:
                table=self.query_one("#io_table")
                table.remove_children()
                table.mount(TextArea(text=f"Error submitting table\n{e}"))
        
        elif event.button.id == "io_save":
            try:
                editor_text= self.query_one("#io_code_editor").text
            except Exception as e:
                table=self.query_one("#io_table")
                table.remove_children()
                table.mount(TextArea(text=f"Error saving code\n{e}"))
    

    

        
                
class FunctionSelector(Container):
    def __init__(self,avail_funcs, **kwargs):
        super().__init__(**kwargs)
        self.avail_funcs=avail_funcs

    def compose(self):
        global func_match_text
        yield(
            Vertical(
                    Horizontal(
                        ListView(*[ListItem(Static(i+"|"+j)) for i in self.avail_funcs.keys() for j in self.avail_funcs[i]],id="module_list"),
                        TextArea.code_editor(id="func_display",language="python"),
                        id="func_panel"
                        ),
                    Rule(line_style="dashed"),
                    TextArea(text=f"{func_match_text}",id="func_match"),
                    Horizontal(
                        Button("Save",id="save_match"),
                        Button("Verify",id="verify_match"),
                        Button("Submit",id="submit_match")
                        )
                    )
        )
    
    def on_list_view_selected(self, event: ListView.Selected):
        try:
            mod_func_name= event.item.children[0].renderable.split("|")
            mod_name=mod_func_name[0]
            func_name=mod_func_name[1]
            func_text=inspect.getsource(getattr(eval(mod_name),func_name))
            self.query_one("#func_display").text=func_text
            
            
        except Exception as e:
            self.mount(TextArea(text=f"Error displaying function{e}"))
        
        
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "verify_match":
            try:
                code=self.query_one("#func_match").text
                matches=json.loads(code)
                for k,v in matches.items():
                    mod_name,func_name=k.split("|")
                    if (set(v.values())-set(io_table_data.keys())):
                        missing=set(v.values())-set(io_table_data.keys())
                        raise ValueError(f"All of the inputs must be selected from the IO table {missing}")
                    for argument in zip(*[io_table_data[j] for _,j in v.items()]):
                        keyword_arguments=dict(zip(v.keys(),argument))
                        getattr(eval(mod_name),func_name)(**keyword_arguments)
                self.mount(Label("[green]All input/output matched with functions successfully!"))
            except Exception as e:
                self.mount(Label("[red]Verification failed\n"+str(e)+"\n"))
        
        elif event.button.id == "save_match":
            global func_match_text
            func_match_text=self.query_one("#func_match").text
        
        elif event.button.id == "submit_match":
            global funcs_tobe_used
            func_name={}
            try:
                funcs_tobe_used=json.loads(self.query_one("#func_match").text).items()
                self.mount(Label("[green] Functions submitted successfully!"))
            except Exception as e:
                self.mount(Label(f"Error submitting functions\n{e}"))
                    
                    
                    
class OperationManager(Container):
    def __call__(self, *args, **kwds):
        return super().__call__(*args, **kwds)
    
    def on_mount(self):
        global funcs_tobe_used
        if funcs_tobe_used is not None:
            for k,v in funcs_tobe_used:
                mod_name,func_name=k.split("|")
                getattr(eval(mod_name),func_name)(*v)
            self.mount(Label("[green] All input/output matched with functions successfully!"))
        else:
            self.mount(Label("[red] No functions to be executed"))
            
        


class Bioplumber(App):
    CSS_PATH = "tui_css.tcss"

    
    def compose(self):
        
        yield Header(show_clock=True)
        yield TabManager(name="tabs")
        yield Container(name="tab contents",id="tab_contents")
        yield Footer()
 
    def on_mount(self):
        """Load initial content for the first tab."""
        self.load_tab_content("io")
        
    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
    
    
    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle tab activation events."""
        tab_id = event.tab.id
        self.load_tab_content(tab_id)
        
        
    def load_tab_content(self, tab_id: str):
        """Dynamically load content based on the selected tab."""
        container = self.query_one("#tab_contents")
        container.remove_children()
        print(tab_id)
        if tab_id == "st":
            # Add the editable file viewer content
            container.mount(EditableFileViewer(os.path.join(SCRIPT_DIR,"slurm_template.txt")))  # Replace with your file path
        
        elif tab_id == "jm":
            container.mount(SlurmManager())
        
        elif tab_id == "io":
            try:
                container.mount(container.query_one("#io_manager"))
            except:   
                container.mount(IOManager(id="io_manager"))
            
        elif tab_id == "sg":
            container.mount(FunctionSelector(avail_funcs=avail_modules))
            
        elif tab_id == "op":
            container.mount(OperationManager())
    






if __name__ == "__main__":
    main()