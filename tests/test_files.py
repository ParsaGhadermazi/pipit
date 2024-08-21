import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from pipit import files  # Replace 'your_module' with the actual module name

@pytest.fixture
def mock_path():
    mock_path = MagicMock(spec=Path)
    mock_path.glob.return_value = [
        Path("sample1_1.fastq.gz"),
        Path("sample1_2.fastq.gz"),
        Path("sample2_1.fastq.gz"),
        Path("sample2_2.fastq.gz")
    ]
    return mock_path
    
def test_group_files(mock_path):
    # Mock the Path object and its methods
    
    
    # Define the parameters
    separator = "_"
    group_on = [1]
    extension = ".fastq.gz"
    
    # Call the function
    result = files.group_files(mock_path, separator, group_on, extension)
    
    # Define the expected result
    expected_result = {
        str(Path("sample1_1.fastq.gz").absolute()):1,
        str(Path("sample1_2.fastq.gz").absolute()):2,
        str(Path("sample2_1.fastq.gz").absolute()):1,
        str(Path("sample2_2.fastq.gz").absolute()):2

    }
    
    # Assert the result
    assert result == expected_result
    
    group_on = [0]
    result = files.group_files(mock_path, separator, group_on, extension)
    expected_result = {
        str(Path("sample1_1.fastq.gz").absolute()):1,
        str(Path("sample1_2.fastq.gz").absolute()):1,
        str(Path("sample2_1.fastq.gz").absolute()):2,
        str(Path("sample2_2.fastq.gz").absolute()):2

    }
    assert result == expected_result
    
    
def test_cat_files_():
    paths=["sample1_1.fastq.gz",
           "sample1_2.fastq.gz",
           "sample2_1.fastq.gz",
           "sample2_2.fastq.gz"]
    command=files.cat_files_(paths, "mered.fastq.gz")
    assert command=="cat sample1_1.fastq.gz sample1_2.fastq.gz sample2_1.fastq.gz sample2_2.fastq.gz > mered.fastq.gz"
        
if __name__ == "__main__":
    test_cat_files_(mock_path)