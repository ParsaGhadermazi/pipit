import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from bioplunger import files


@patch("pathlib.Path.rglob")
def test_group_files(mock_rglob):
    # Mock the Path object and its methods
    mock_rglob.return_value = [
        Path("sample1_1.fastq.gz"),
        Path("sample1_2.fastq.gz"),
        Path("sample2_1.fastq.gz"),
        Path("sample2_2.fastq.gz")
    ]
    
    # Define the parameters
    separator = "_"
    group_on = [1]
    extension = ".fastq.gz"
    
    # Call the function
    result = files.group_files("some_file_dir", separator, group_on, extension)
    
    # Define the expected result
    expected_result = {
        1: [str(Path("sample1_1.fastq.gz").absolute()), str(Path("sample2_1.fastq.gz").absolute())],
        2: [str(Path("sample1_2.fastq.gz").absolute()), str(Path("sample2_2.fastq.gz").absolute())]
    }
    
    # Assert the result
    assert result == expected_result
    
    group_on = [0]
    result = files.group_files("some_file_dir", separator, group_on, extension)
    expected_result = {
        1: [str(Path("sample1_1.fastq.gz").absolute()), str(Path("sample1_2.fastq.gz").absolute())],
        2: [str(Path("sample2_1.fastq.gz").absolute()), str(Path("sample2_2.fastq.gz").absolute())]
    }
    assert result == expected_result
    
    
def test_cat_files_():
    paths=["sample1_1.fastq.gz",
           "sample1_2.fastq.gz",
           "sample2_1.fastq.gz",
           "sample2_2.fastq.gz"]
    command=files.cat_files_(paths, "merged.fastq.gz")
    assert command==("cat sample1_1.fastq.gz sample1_2.fastq.gz sample2_1.fastq.gz sample2_2.fastq.gz > "+str((Path(paths[0]).parent/"merged.fastq.gz").absolute()))
        

