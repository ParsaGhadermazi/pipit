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
                             Pretty,
                             Input,
                             DirectoryTree,
                             Static,
                             Collapsible,
                             Select,
                             SelectionList,
                              TabbedContent,
                              TabPane,
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
from textual import on, work

from textual.validation import Function, Number, ValidationResult, Validator
import math
import json
import os
import pandas as pd
import inspect
from dataclasses import dataclass
import datetime
import pathlib
import shutil
import time

def get_available_functions():
    am=[]
    for module in [bining,files,qc,assemble,alignment]:
        am.append((module.__name__,[i for i in dir(module) if i.endswith("_") and not i.startswith("__")]))
    return dict(am)
        
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
editor_text="#add your functions here below\nimport pandas as pd\nio_table=pd.DataFrame({'col1':[1,2,3],'col2':[4,5,6]})"
avail_modules=get_available_functions()
funcs_tobe_used=None

io_table_data=None

def process_for_md_table(text):
    return text.replace("-","_").replace(" ","").lower()
def main():
    app = Bioplumber()
    app.run()


    
class Run:
    
    def __init__(self,
                 run_id:str,
                 project_dir:str,
                 date_created:datetime.datetime,
                 all_commands:list=list(),
                 io_table:pd.DataFrame=pd.DataFrame(),
                 slurm_commands:list=list()
                 ):
        self._run_id=run_id
        self.project_dir=project_dir
        self.all_commands=all_commands
        self.date_created=date_created
        self.io_table=io_table
        self.slurm_commands=slurm_commands
        self.io_script=editor_text
        self.save_dir=pathlib.Path(self.project_dir).joinpath("runs").joinpath(self.run_id)/f"{self.run_id}.run"
        self.func_match_text={}
        

    @property
    def run_id(self):
        return self._run_id
    
    def save_state(self):
        state={}
        state["run_id"]=self.run_id
        state["all_commands"]=self.all_commands
        state["io_table"]=self.io_table
        state["date_created"]=self.date_created.strftime("%Y-%m-%d %H:%M:%S")
        state["slurm_commands"]=self.slurm_commands
        state["io_script"]=self.io_script
        os.makedirs(pathlib.Path(self.save_dir).parent,exist_ok=True)
        with open(self.save_dir,"w") as f:
            json.dump(state,f)
            

    @classmethod
    def load_run(self,project_dir:str,run_id:str):
        file_path=pathlib.Path(project_dir).joinpath("runs").joinpath(run_id)/f"{run_id}.run"
        with open(file_path,"r") as f:
            state=json.load(f)
        run=Run(
            run_id=run_id,
            project_dir=project_dir,
            date_created=datetime.datetime.strptime(state["date_created"],"%Y-%m-%d %H:%M:%S"),
            all_commands=state["all_commands"],
            io_table=pd.DataFrame.from_dict(state["io_table"]),
            slurm_commands=state["slurm_commands"]
        )
        run.io_script=state["io_script"]
        return run
        
        

class Project:
    def __init__(self,
                 name:str,
                 creator_name:str,
                 creator_email:str,
                 description:str,
                 directory:str,
                 time_created:datetime.datetime
                 ):
        
        self.name=name
        self.creator_name=creator_name
        self.creator_email=creator_email
        self.description=description
        self.directory=directory
        self.time_created=time_created
        self.runs:list[Run]=[]
    
    
    def add_run(self,run:Run):
        self.runs.append(run)
    
    
    def generate_report(self):
        pass
    
    @classmethod
    def load_project(cls,project_dir:str):
        with open(os.path.join(project_dir,"project_metadata.json"),"r") as f:
            project_dict=json.load(f)
        project=cls(**{k:v for k,v in project_dict.items() if k!="runs"})
        run_dir=pathlib.Path(project_dir).joinpath("runs")
        for run in run_dir.rglob("*.run"):
            project.add_run(Run.load_run(project.directory,run.name.split(".")[0]))
        return project
    
    def save_state(self):
        with open(os.path.join(self.directory,"project_metadata.json"),"w") as f:
            json.dump({k:v for k,v in self.__dict__.items() if k!="runs"},f)

    
    def make_markdown_report(self):
        txt=f"# Project Name: {self.name}\n\n"
        txt+=f"## Creator: {self.creator_name} ({self.creator_email})\n"
        txt+=f"## Table of Contents:\n"
        txt+="- [Time Created](#time_created)\n"
        txt+="- [Description](#description)\n"
        txt+="- [Runs](#runs)\n"
        for run in self.runs:
            txt+=f"- [{run.run_id}](#{process_for_md_table(run.run_id)})\n"
            txt+=""  
        txt+=f"## Time Created: {self.time_created}\n"
        txt+="## Description: \n\n"
        txt+=f"{self.description}\n"
        txt+="## Runs:\n"
        for run in self.runs:
            txt+=f"### {run.run_id}\n"
            txt+=f"#### Time Created: {run.date_created.strftime('%Y-%m-%d %H:%M:%S')}\n"
            txt+=f"IOTABLE and command placeholder\n"
        return txt
            
class FunctionArgSelector(Screen):
    def __init__(self,func_name:str,run:Run):
        super().__init__()
        self.func_name=func_name
        self.run=run
        self.func_args=[i for i in inspect.signature(getattr(eval(func_name.split("|")[0]),func_name.split("|")[1])).parameters if i!="kwargs"]
        
        
    def compose(self):
        
        yield Vertical(
            Header(show_clock=True),
            Vertical(
                Label(f"Function: {self.func_name}",id="func_name"),
                Vertical(
                    *[Horizontal(Label(argname,classes="SelectIOtitles"),Select(zip(self.run.io_table.keys(),self.run.io_table.keys()),classes="SelectIOpts",id=argname)) for argname in self.func_args ]
                    ,id="funcargselects"
                ),
                Horizontal(
                    Button("Add",id="add_arg"),
                    Button("Back",id="back_arg"),
                    id="funcarglowbutsett"
                    ),
                id="funcargscontainer"
                ),
            Footer(),
            id="funcargall"
            )
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "back_arg":
            self.app.pop_screen()
            
        if event.button.id == "add_arg":
            try:
                args={i:self.query_one("#"+i).value for i in self.func_args}
                self.run.func_match_text[self.func_name]=args
                self.dismiss()
            except Exception as e:
                self.mount(Label(f"[red]Error adding arguments\n{e}"))
            
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

class ManageSteps(Container):
    def compose(self):
        
        yield Horizontal(
                    TextArea(id="step_info",read_only=True),
                    )
        

class IOManager(Container):

    
    def __init__(self,run:Run, **kwargs):
        super().__init__(**kwargs)
        self._submitted_io_table = None
        self.run=run
        
    def compose(self):
        
        
        yield Vertical(
                Horizontal(
                        TextArea.code_editor(text=self.run.io_script,
                                             language="python",
                                             id="io_code_editor",
                                             ),
                        DataTable(id="io_table"),
                        id="io_area"
                        ),
                Horizontal(
                    Button("Save Script", id="save_io_script"),
                    Button("Render I/O table", id="io_render"),
                    Button("Submit I/O table", id="io_submit"),
                    id="io_buttons")
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
            try:
                code = self.query_one("#io_code_editor").text
                exec(code)
                self.run.io_table =locals()["io_table"].to_dict(orient="list")
                self.run.save_state()
                table = self.query_one("#io_table")
                table.remove_children()
                table.mount(Container(Static("[green]Table submitted successfully!",)))
            except Exception as e:
                table=self.query_one("#io_table")
                table.remove_children()
                table.mount(TextArea(text=f"Error submitting table\n{e}"))
        elif event.button.id == "save_io_script":
            try:
                code = self.query_one("#io_code_editor").text
                with open(self.run.save_dir,'r') as f:
                    state=json.load(f)
                state["io_script"]=code
                with open(self.run.save_dir,'w') as f:
                    json.dump(state,f)
            except Exception as e:
                self.mount(TextArea(text=f"Error saving script\n{e}"))
        

    

class FunctionSelector(Container):
    def __init__(self,avail_funcs,run:Run, **kwargs):
        super().__init__(**kwargs)
        self.avail_funcs=avail_funcs
        self.run=run

    def compose(self):
        yield(
            Vertical(
                    Horizontal(
                        ListView(*[ListItem(Static(i+"|"+j)) for i in self.avail_funcs.keys() for j in self.avail_funcs[i]],id="module_list"),
                        TextArea.code_editor(id="func_display",language="python"),
                        id="func_panel"
                        ),
                    Button("Add Step",id="add_step_button"),
                    ManageSteps(),
                    Horizontal(
                        Button("Verify",id="verify_match"),
                        Button("Submit",id="submit_match")
                        ),
                    
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
        
        
    @work
    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "verify_match":
            try:
                matches=self.run.func_match_text
                for k,v in matches.items():
                    mod_name,func_name=k.split("|")
                    if (set(v.values())-set(self.run.io_table.keys())):
                        missing=set(v.values())-set(self.run.io_table.keys())
                        raise ValueError(f"All of the inputs must be selected from the IO table {missing}")
                    for argument in zip(*[self.run.io_table[j] for _,j in v.items()]):
                        keyword_arguments=dict(zip(v.keys(),argument))
                        getattr(eval(mod_name),func_name)(**keyword_arguments)
                self.mount(Label("[green]All inputs/outputs matched with functions successfully!"))
            except Exception as e:
                self.mount(Label("[red]Verification failed\n"+str(e)+"\n"))
        
        elif event.button.id == "submit_match":
            try:
                cmds=[]
                matches=self.run.func_match_text
                cmd_per_chain=len(matches)
                num_args=pd.DataFrame(self.run.io_table).shape[0]
                for r in range(num_args):
                    for k,v in matches.items():
                        mod_name,func_name=k.split("|")
                        keyword_arguments=dict(zip(v.keys(),[self.run.io_table[j][r] for _,j in v.items()]))
                        cmds.append(getattr(eval(mod_name),func_name)(**keyword_arguments))

                self.run.all_commands=[cmds[i:i+cmd_per_chain] for i in range(0,len(cmds),cmd_per_chain)]
                
                self.mount(Label("[green] Functions submitted successfully!"))
            except Exception as e:
                self.mount(Label(f"Error submitting functions\n{e}"))
            
        elif event.button.id == "add_step_button":
            selected_func=self.query_one("#module_list").highlighted_child
            if selected_func:
                await self.app.push_screen_wait(FunctionArgSelector(selected_func.children[0].renderable,self.run))
                self.query_one("#step_info").remove_children()
                self.query_one("#step_info").mount(ListView(*[ListItem(Static(f"{k}")) for k,v in self.run.func_match_text.items()]))
                self.app.query_children("#num_chains").node.renderable=f"Number of chains:[bold] {len(self.run.all_commands)}"
            

    

                    
class OperationManager(Container):
    def __init__(self,run:Run, **kwargs):
        super().__init__(**kwargs)
        self.run=run

    def compose(self):
        
        try:
            yield Vertical(
                    Horizontal(
                            Label(f"Number of chains:[bold] {len(self.run.all_commands)}", id="num_chains"),
                            Label(f"Number of commands per chain:[bold] {len(self.run.all_commands[0])}", id="num_cmds"),
                            Input(
                          placeholder="Number of batches",
                          validators=[
                                      Number(minimum=1, maximum=len(self.run.all_commands)),
                                     ],
                            id="num_batches"
                        ),
                            id="chain_info"),
                    
                    Container(id="batch_area"),
                    Horizontal(
                        Button("Save Scripts",id="save_scripts"),
                        Button("Submit Jobs",id="submit_jobs"),
                        id="operation_buttons"
                        ),
                    
                    )

            
        except Exception as e:
            yield TextArea(f"Error rendering operations\n{e}")


    def on_input_changed(self, event: Input.Changed):
        try:
            with open(os.path.join(SCRIPT_DIR,"slurm_template.txt"),"r") as file:
                slurm_template=file.read()
            num_batches=int(event.value)
            self.query_one("#batch_area").remove_children()
            self.run.slurm_commands=[]
            for i in range(0,len(self.run.all_commands),math.ceil(len(self.run.all_commands)/num_batches)):
                batch=self.run.all_commands[i:i+math.ceil(len(self.run.all_commands)/num_batches)]
                cmds=""
                for j in batch:
                    for k in j:
                        cmds+=k+"\n"
                slurm_template_=slurm_template.replace("<command>",cmds)
                slurm_template_=slurm_template_.replace("<job_name>",self.run.run_id+f"_batch_{i+1}")
                self.query_one("#batch_area").mount(Collapsible(Label(f"Batch {i}"),TextArea(slurm_template_),title=f"Batch {i+1}"))
                self.run.slurm_commands.append(slurm_template_)
        
        except Exception as e:
            self.query_one("#batch_area").remove_children()
            self.query_one("#batch_area").mount(Label("[red]Number of batches must be a number between 1 and the number of chains\n"+str(e)))
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "save_scripts":
            try:
                save_dir=pathlib.Path(self.run.save_dir).parent/"batch_scripts"
                os.makedirs(save_dir,exist_ok=True)
                for i,cmd in enumerate(self.run.slurm_commands):
                    with open(save_dir/f"Batch_{i+1}.batch","w") as f:
                        f.write(cmd)
                self.mount(Label("[green]Scripts saved successfully!"))
            except Exception as e:
                self.mount(Label(f"[red]Error saving scripts\n{e}"))
        
        elif event.button.id == "submit_jobs":
            pass
        
class NewProject(Screen):
    def compose(self):
        yield Vertical(
            Header(show_clock=True),
            Container(
                Vertical(
                    Input(placeholder="Project Name",id="project_name"),
                    Input(placeholder="Project Description",id="project_description"),
                    Input(placeholder="Project Directory",id="project_dir"),
                    Input(placeholder="Creator Name",id="creator_name"),
                    Input(placeholder="Creator Email",id="creator_email")

                    ),
                Button("Create Project",id="create_project")
                ),
            Footer(Label("Developed by [bold]Parsa Ghadermazi")))
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "create_project":
            project_name=self.query_one("#project_name").value
            project_description=self.query_one("#project_description").value
            project_dir=self.query_one("#project_dir").value
            creator_name=self.query_one("#creator_name").value
            creator_email=self.query_one("#creator_email").value
            project=Project(name=project_name,
                            creator_name=creator_name,
                            creator_email=creator_email,
                            description=project_description,
                            directory=project_dir,
                            time_created=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            if os.path.exists(project_dir):
                self.app.push_screen(ProjectAlreadyExists(project),"project_already_exists")

            else:
                os.makedirs(os.path.join(project_dir,"runs"))
                with open(os.path.join(project_dir,"project_metadata.json"),"w") as f:
                    json.dump(project.__dict__,f)
                self.app.push_screen(RunStation(project),"run_screen")

        
class LoadProject(Screen):
    def compose(self):
        yield Vertical(
            Container(
                Vertical(
                    Input(placeholder="Base Directory",id="project_dir_input"),
                    DirectoryTree("/",id="project_dir_tree"),
                    Button("Load Project",id="load_project")
                    )))

    def on_input_changed(self, event: Input.Changed):
        try:
            self.query_one("#project_dir_tree").path=event.value
        except Exception as e:
            pass
    
    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected):
        
        self.load_dir=event.path
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "load_project":
            try:
                if hasattr(self,"load_dir"):
                    project_dir=self.load_dir
                else:
                    project_dir=self.query_one("#project_dir_input").value

                project=Project.load_project(project_dir)
                self.app.push_screen(RunStation(project),"run_screen")
            except Exception as e:
                if self.query("#project_load_error"):
                    self.remove_children("#project_load_error")
                else:
                    self.mount(Label(f"[red]Selected folder is not a valid project",id="project_load_error"))
            
            


class WelcomeScreen(Screen):
    def compose(self):
        yield Vertical(
            Header(show_clock=True),
            Container(
                Static("How would you like to proceed?",classes="question"),
                Horizontal(
                    Button("New Project",id="new_project",classes="buttons"),
                    Button("Load Project",id="load_project",classes="buttons"),
                    id="welcome_screen_buttons"),
                id="welcome_screen"
                ),
            Footer(),id="welcome_screen_all")
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "new_project":
            self.app.push_screen(NewProject(),"new_project_screen")
        elif event.button.id == "load_project":
            self.app.push_screen(LoadProject(),"load_project_screen")
                    
 
class ProjectAlreadyExists(Screen):
    def __init__(self,project:Project):
        super().__init__()
        self.project=project

        
    def compose(self):
        yield Vertical(
            Static("[bold]Project already exists! Are you sure you want to overwrite it?",id="project_overwrite_question"),
            Horizontal(
                Button("Yes",id="yes_overwrite"),
                Button("No",id="no_overwrite"),
                id="project_overwrite_buttons"
                ),
            id="project_overwrite_screen"
            )
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "yes_overwrite":
            with open(os.path.join(self.project.directory,"project_metadata.json"),"w") as f:
                        json.dump(self.project.__dict__,f)
            if os.path.exists(os.path.join(self.project.directory,"runs")):
                shutil.rmtree(os.path.join(self.project.directory,"runs"))
                os.makedirs(os.path.join(self.project.directory,"runs"))
                
            self.app.pop_screen()
            self.app.push_screen(RunStation(self.project),"run_screen")
        elif event.button.id == "no_overwrite":
            self.app.pop_screen()

class RunScreen(Screen):
    BINDINGS=[
        ("ctrl+r","run_menu","Runs menu"),
        ("ctrl+t","projects_menu","Projects menu"),
        ("ctrl+w","welcome_menu","Welcome menu")
    ]

    def __init__(self,run:Run):
        super().__init__()
        self.ev=EditableFileViewer(os.path.join(SCRIPT_DIR,"slurm_template.txt"))
        self.sm=SlurmManager()
        self.fs=FunctionSelector(avail_funcs=avail_modules,run=run,id="func_selector")
        self.om=OperationManager(run,id="operation_manager")
        self.io=IOManager(run,id="io_manager")
        self.run=run
    
    def compose(self):
        
        yield Header(show_clock=True)      
        with TabbedContent("Input/Output","Script generator","Operation","Slurm template","Job monitor",id="tabs"):
                yield self.io
                yield self.fs
                yield self.om
                yield self.ev
                yield self.sm
        yield Footer()
    
    @on(TabbedContent.TabActivated)
    async def refreshnums(self) -> None:
        await self.query_one("#operation_manager").recompose()
            

    def action_run_menu(self):
        self.app.pop_screen()
    
    def action_projects_menu(self):
        self.app.pop_screen()
        self.app.pop_screen()
        
    def action_welcome_menu(self):
        self.app.pop_screen()
        self.app.pop_screen()
        self.app.pop_screen()
        
class RunStation(Screen):
    
    def __init__(self,project:Project):
        super().__init__()
        self.project=project
    
    def compose(self):
        yield Vertical(
            Header(show_clock=True),
            Container(
                Vertical(
                    Label(f"Existing Runs in {self.project.name}:",id="existing_run_label"),
                    ListView(*[ListItem(Static(run.run_id)) for run in self.project.runs],id="run_list"),
                        )
                    ),
            Container(
                Vertical(
                    Label("Create New Run", id="create_new_run_label"),
                    Input(placeholder="Run ID",id="run_id"),
                    Horizontal(
                               Button("Enter Run Station",id="create_run"),
                               Button("Update Notebook",id="update_notebook")
                               )
                        ),
                    Button("Back",id="back"),
                    ))
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "create_run":
            run_id=self.query_one("#run_id").value
            if run_id=="":
                self.mount(Label("[red]Run ID cannot be empty!"))
            else:    
                if run_id in [run.run_id for run in self.project.runs]:
                    run=Run.load_run(project_dir=self.project.directory,run_id=run_id)
                else:
                    run=Run(run_id=run_id,
                            project_dir=self.project.directory,
                            date_created=datetime.datetime.now(),)
                    run.save_state()
                    self.project.add_run(run)

                self.app.push_screen(RunScreen(run),"run_screen")
            
        elif event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "update_notebook":
            with open(os.path.join(self.project.directory,"project_notebook.md"),"w") as f:
                f.write(self.project.make_markdown_report())
    
    def on_list_view_selected(self, event: ListView.Selected):
        run_id=event.item.children[0].renderable
        self.query_one("#run_id").value=run_id
        
        
    
            


class Bioplumber(App):
    CSS_PATH = "tui_css.tcss"

    
    def on_mount(self):
        self.theme="gruvbox"
        self.push_screen(WelcomeScreen(),"welcome_screen" )
    
    
    
    
    # def on_button_pressed(self, event: Button.Pressed):
    #     if event.button.id == "new_project":
    #         self.push_screen(RunScreen(),"run_screen")
    #     elif event.button.id == "load_project":
    #         pass
        

    

    






if __name__ == "__main__":
    main()