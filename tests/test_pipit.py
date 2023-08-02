from pipit import __version__
from pipit import core
from pytest import fixture
import pathlib
import os 
import multiprocessing
import time

FILE_DIR=os.path.dirname(os.path.abspath(__file__))

def test_version():
    assert __version__ == '0.1.0'
    
@fixture
def return_true_reads():
    return {
        "reads_1":pathlib.Path(FILE_DIR,"io_files_test","reads_1.fa"),
        "reads_2":pathlib.Path(FILE_DIR,"io_files_test","reads_2.fa")
    }
@fixture    
def return_false_reads():
    return {
        "reads_1":pathlib.Path(FILE_DIR,"io_files_test","reads_1.fa"),
        "reads_2":pathlib.Path(FILE_DIR,"io_files_test","reads_2.fa"),
        "reads_3":pathlib.Path(FILE_DIR,"io_files_test","reads_3.fa")
    }
    
    
def test_io_input_ready_valid(return_true_reads):
    outputs={
        "reads":pathlib.Path(FILE_DIR,"io_files_test","reads.fa")
    }
    io=core.IO(inputs=return_true_reads,
               outputs=outputs,
               validate=False,
                notifier_input=multiprocessing.Condition(),
                notifier_output=multiprocessing.Condition())
    try:
        io._validate()
    except FileNotFoundError:
        assert False
    else:
        assert True

def test_io_input_ready_invalid(return_false_reads):
    outputs={
        "reads":pathlib.Path(FILE_DIR,"io_files_test","reads.fa")
    }
    io=core.IO(inputs=return_false_reads,
               outputs=outputs,
               validate=False,
                notifier_input=multiprocessing.Condition(),
                notifier_output=multiprocessing.Condition())
    try:
        io._validate()
    except FileNotFoundError:
        assert True
    else:
        assert False

def test_io_input_empty():
    outputs={
        "reads":pathlib.Path(FILE_DIR,"io_files_test","reads.fa")
    }
    io=core.IO(inputs={},
               outputs=outputs,
               validate=False,
                notifier_input=multiprocessing.Condition(),
                notifier_output=multiprocessing.Condition())
    try:
        io._validate()
    except FileNotFoundError:
        assert False
    else:
        assert True

def test_notify_io_object_valid(return_true_reads):
    outputs={
        "reads":pathlib.Path(FILE_DIR,"io_files_test","reads.fa")
    }
    io=core.IO(inputs=return_true_reads,
               outputs=outputs,
               validate=False,
                notifier_input=multiprocessing.Condition(),
                notifier_output=multiprocessing.Condition())
    
    core._notify_for_input([io])
    io()
    
    assert True
    
def test_notify_io_object_valid_verbose(return_true_reads, capsys):
    outputs={
        "reads":pathlib.Path(FILE_DIR,"io_files_test","reads.fa")
    }
    io=core.IO(inputs=return_true_reads,
               outputs=outputs,
               validate=False,
                notifier_input=multiprocessing.Condition(),
                notifier_output=multiprocessing.Condition())
    output_log=capsys.readouterr()
    core._notify_for_input([io])
    io(verbose=True)
    output_log=capsys.readouterr() 
    assert output_log.out.rstrip("\n")==f"{io.__str__()} is ready."

def test_notify_io_object_invalid(return_false_reads):
    outputs={
        "reads":pathlib.Path(FILE_DIR,"io_files_test","reads.fa")
    }
    io=core.IO(inputs=return_false_reads,
               outputs=outputs,
               validate=False,
                notifier_input=multiprocessing.Condition(),
                notifier_output=multiprocessing.Condition())
    try:
        core._notify_for_input([io])
    except FileNotFoundError:
        assert True
    else:
        assert False

def test_io_can_wait(return_true_reads):
    outputs={
        "reads":pathlib.Path(FILE_DIR,"io_files_test","reads.fa")
    }
    io=core.IO(inputs=return_true_reads,
               outputs=outputs,
               validate=False,
                notifier_input=multiprocessing.Condition(),
                notifier_output=multiprocessing.Condition())
    with io._notifier_input:
        core._notify_for_input([io])
        io()
        
        
    assert True

def test_io_can_wait_timout(return_true_reads):
    outputs={
        "reads":pathlib.Path(FILE_DIR,"io_files_test","reads.fa")
    }
    io=core.IO(inputs=return_true_reads,
               outputs=outputs,
               validate=False,
                notifier_input=multiprocessing.Condition(),
                notifier_output=multiprocessing.Condition())
    with io._notifier_input:
        io(time_out=0.00001)
    assert True