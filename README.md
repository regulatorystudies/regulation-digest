# regulation-digest

Retrieving and processing Federal Register documents for the GW Regulatory Studies Center [Regulation Digest](https://regulatorystudies.columbian.gwu.edu/newsletters).

## Installation

There are two options for running the program:

  1. Download a Python interpreter, create the environment, and run script (Python required).
  2. Download the compiled program file (created using Nuitka), unzip, and run (Python not required).

This README document focuses on approach 1. Please reach out to <mfebrizio@gwu.edu> for access to the compiled program.

First, install a Python interpreter to run the code. Some suggested download options are from [Anaconda](https://www.anaconda.com/download) or [Python.org](https://www.python.org/downloads/). The program was developed using Python 3.10, so that is the recommended version.

Second, download the code by [cloning](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) this Github repository.

Third, create a separate environment for running the program. This is easy to do with conda using the environment.yml contained in this repository. Enter the following commands in Anaconda Powershell Prompt:

```{cmd}
cd "PATH/TO/YOUR/DIRECTORY/WITH/YML"

conda env create -f environment.yml
```

Your environment can be activated from the command line using `conda activate regdigest`, and the program is now ready to run on your computer. Run the program with your choice of IDE or from the command line, `python retrieve_documents.py`.

## Directory Structure

The main repository directory should contain several folders, including:

- input
- output
- regdigest

The `input/` sub-folder is where you place the input file, if it is being used. Only one input file should be included in the folder at a time because the program will use the first file (alphabetically). The input file must be an Excel workbook or a CSV file, but it can be named anything.

The `output/` sub-folder is where the output data will be located. It creates data files in comma separated values (CSV) format with the naming convention `federal_register_clips_YYYY-MM-DD`, where the date is the current date. If more than one file is created in a day, it will be overwritten. If the output folder does not exist at runtime, it will be automatically created for you.

The `regdigest/` sub-folder is the module where the program itself is located. There are many files and sub-directories within it, but you do not need to do anything with them (except leave them be!). These files are required for the program to run without installing Python on your computer. The only file you need to access within this folder is `retrieve_documents.exe`. This is the executable that runs the compiled program.

## Usage

After running the program, a window with a text field will open on your computer. It may take several seconds to appear. Initially, the dialog box will read:
> `Use input file? [yes/no]:`

Decide whether you want to use an input file to supply document numbers to the program, or whether you want to retrieve documents within a date range. If you want to use the input file, ensure it is in the `input/` sub-folder, then type `yes` or `y`. If not, type `no` or `n`. If an invalid response is received, the program will ask again.

If you are using a date range, the dialog box will read:
> `Input start date [yyyy-mm-dd]:`

Supply the start date in yyyy-mm-dd format (e.g., 2023-05-25 for May 25, 2023). If an invalid response is received, the program will ask again.

Next, the program will ask:
> `Input end date [yyyy-mm-dd]. Or just press enter to use today as the end date:`

Either supply the end date or press enter to proceed. If an invalid response is received, the program will ask again.

Finally, the program will retrieve the documents from the Federal Register, format them, and create an CSV file with today's date in the `output/` sub-folder.
