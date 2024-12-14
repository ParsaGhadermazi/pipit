from textual.app import App
from textual.widgets import Header, Footer, Tabs,Tab, TextArea, Button
from textual.containers import Container
from bioplumber import (configs,
                        bining,
                        files,
                        qc,
                        assemble,
                        slurm,
                        alignment)

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

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
            self.mount(TextArea(text=json.dumps(data,indent=4)))
        except Exception:
            self.mount(TextArea(text="Make Sure you have access to slurm"))    
    
class TabManager(Tabs):
    
    def compose(self):
        yield Tabs(
            Tab("Script Generator", id="sg"),
            Tab("Operation", id="op"),
            Tab("Job monitor", id="jm"),
            Tab("Slurm template", id="st"),
            id="all_tabs"
        )

class Bioplumber(App):
    CSS_PATH = "tui_css.tcss"
    BINDINGS=[
        ("d", "toggle_dark","Toggle dark mode")
    ]
    def compose(self):
        
        yield Header(show_clock=True)
        yield TabManager()
        yield Container(id="tab_contents")
        yield Footer()
 
    def on_mount(self):
        """Load initial content for the first tab."""
        self.load_tab_content("sg")
        
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
            
        else:
        # Add placeholder content for other tabs
            container.mount(TextArea(text=f"Content for {tab_id} tab."))



if __name__ == "__main__":
    main()