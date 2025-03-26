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

class ConfigsEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, configs.Configs):
            return obj.__dict__
        return super().default(obj)

class Run:
    def __init__(self,
                 run_id:str,
                 project_dir:str,
                 description:str,
                 date_created:datetime.datetime,
                 tables:list[str]=None,
                 notes:dict[str,str]=None
                 ):
        self._run_id=run_id
        self.table_gen_script="#Generate your tables here"
        self.project_dir=project_dir
        self.description=description
        self.date_created=date_created
        self.save_dir=pathlib.Path(self.project_dir).joinpath("runs").joinpath(self.run_id)/f"{self.run_id}.run"
        self.save_dir.parent.mkdir(parents=True,exist_ok=True)
        if tables is None:
            self.tables=[]
        else:
            self.tables=tables
            
        if notes is None:
            self.notes={}
        else:
            self.notes=notes
        

    @property
    def run_id(self):
        return self._run_id
    
    def save_state(self):
        state={}
        state["run_id"]=self.run_id
        state["date_created"]=self.date_created.strftime("%Y-%m-%d %H:%M:%S")
        state["table_gen_script"]=self.table_gen_script
        state["tables"]=self.tables
        state["notes"]=self.notes
        state["description"]=self.description

            
        os.makedirs(pathlib.Path(self.save_dir).parent,exist_ok=True)
        with open(self.save_dir,"w") as f:
            json.dump(state,f,cls=ConfigsEncoder)
        
            

    @classmethod
    def load_run(self,project_dir:str,run_id:str):
        file_path=pathlib.Path(project_dir).joinpath("runs").joinpath(run_id)/f"{run_id}.run"
        with open(file_path,"r") as f:
            state=json.load(f)
        run=Run(
            run_id=run_id,
            project_dir=project_dir,
            description=state["description"],
            date_created=datetime.datetime.strptime(state["date_created"],"%Y-%m-%d %H:%M:%S"),
            tables=state["tables"],
            notes=state["notes"]
        )    
        return run  
    

class Workflow:
    pass 


class NFManager(App):
    CSS_PATH = "tui_css.tcss"
    
    def on_mount(self):
        self.theme="gruvbox"


def main():
    mgr=NFManager()
    mgr.run()
    
if __name__ == '__main__':
    main()


