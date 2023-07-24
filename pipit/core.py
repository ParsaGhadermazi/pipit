import conf
from typing import Iterable
from collections import namedtuple
from time import sleep
class IO:
    pass

class Command:
    pass

class Layer:
    pass

class State:
    pass

class Task:
    
    def __init__(self,name:str,
                 command:Command,
                 inputs:IO,
                 outputs:IO,
                 ):
        self.name = name
        self.command = command
        self.inputs = inputs,
        self.outputs = outputs
        self.id = None
        self._output_available = False
        self.state="Not Started"
        
        
    def submit(sel,executor:str="local"):
        pass
    def save_task(self,path:str):
        pass
        
    
    def _valdate_inputs(self):
        pass
        
    def _outputs_ready(self):
        pass

class Pipeline:
    def __init__(self,steps:list[Layer],config:conf.PipelineConfig):
        self.steps = steps
        self.config = config


    def __call__(self):
        pass
    
    def __str__(self):
        pass

def load_pipeline(path:str)->Pipeline:
    pass

def load_step(path:str)->Task:
    pass

def dump_pipeline(pipeline:Pipeline,path:str)->dict:
    pass

class TaskManager:
    def __init__(self,tasks:Iterable[Task]):
        self._tasks = tasks
        self.done = False
        self._get_current_state()
        
    
    @property
    def tasks(self):
        return self._tasks
    
    @tasks.setter
    def tasks(self,item):
        raise AttributeError("Task Manager objects are not supposed to be modified after creation.")
    
    def _get_current_state(self):
        state={
            "Pending":[],
            "Running":[],
            "Finished":[],
            "Failed":[],
            "Waiting":[],
            "Ready_to_Start":[],
            "Not Started":[],
        }
        
        for task in self.tasks:
            match task.state:
                case "Pending":
                    state["Pending"].append(task)
                case "Running":
                    state["Running"].append(task)
                case "Finished":
                    state["Finished"].append(task)
                case "Failed":
                    state["Failed"].append(task)
                case "Not Started":
                    state["Not Started"].append(task)
                case "Ready to Start":
                    state["Ready_to_Start"].append(task)
                case _:
                    raise ValueError(f"Task {task.name} has an invalid state: {task.state}")
        self.state = state
    
    def busy_loop(self,interval:int=30):
        while not self.done:
            self._get_current_state()
            if len(self.state["Finished"]) == len(self.tasks):
                self.done = True
            if self.state["Failed"]:
                raise RuntimeError("One or more tasks failed.")
            sleep(interval)
    
    
                
            
        