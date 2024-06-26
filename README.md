# regulation-digest

Retrieving and processing Federal Register (FR) documents for the GW Regulatory Studies Center [Regulation Digest](https://regulatorystudies.columbian.gwu.edu/newsletters).

## Installation

There are two options for running the program:

  1. Download a Python interpreter, create the virtual environment, and run script (Python required).
  2. Access the [web app](https://regulatorystudies.shinyapps.io/regulation-digest/) and either browse or download the FR documents in .csv format (Python not required).

This README document focuses on option 1.

First, install a Python interpreter to run the code. Some suggested download options are from [Anaconda](https://www.anaconda.com/download) or [Python.org](https://www.python.org/downloads/). The program requires Python 3.10 or higher.

Second, download the code by [cloning](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) this Github repository.

Third, create a separate virtual environment for running the program. This is easy to do with the `venv` module in the [Python standard library](https://docs.python.org/3/library/venv.html) and the `requirements.txt` file in this repository. Enter the following commands in the terminal / command line:

```{cmd}
cd "PATH/TO/YOUR/LOCAL/PROJECT/DIRECTORY/"

python -m venv myenv  # where myenv is your virtual environment's name

myvenv/scripts/activate  # activate on Windows
source myvenv/bin/activate  # activate on macOS/linux

python -m pip install -r requirements.txt
```

After activating your virtual environment and installing the requirements, the program is now ready to run on your computer. You can run the program with your choice of IDE or from the command line using one of the following approaches:

- Run `retrieve_documents.py` as a script from an IDE or the command line:

    ```{cmd}
    cd "PATH/TO/PROJECT/ROOT"

    python "./regdigest/retrieve_documents.py"
    ```

- Run `regdigest` as a module (command line only):

    ```{cmd}
    cd "PATH/TO/PROJECT/ROOT"

    python -m regdigest
    ```

## Directory Structure

The main repository directory should contain several folders, including:

- input
- output
- regdigest

The `input/` sub-folder is where you place the input file, if it is being used. Only one input file should be included in the folder at a time because the program will use the first file (alphabetically). The input file must be an Excel workbook or a CSV file, but it can be named anything.

The `output/` sub-folder is where the output data will be located. It creates data files in comma separated values (CSV) format with the naming convention `federal_register_clips_YYYY-MM-DD`, where the date is the current date. If more than one file is created in a day, it will be overwritten. If the output folder does not exist at runtime, it will be automatically created for you.

The `regdigest/` sub-folder is the module where the program itself is located. The file, `retrieve_documents.py`, contains the code needed to run the program.

## Usage

After running the program, a window with a text field will open on your computer. It may take several seconds to appear. Initially, the dialog box will read:
> `Use input file containing document numbers or urls? [yes/no]:`

Decide whether you want to use an input file to supply document numbers to the program, or whether you want to retrieve documents within a date range. The program searches the input file for either a column named "document_number" (which contains the document numbers of Federal Register documents) or a column named "html_url" (which contains the url link to the Federal Register document).

If you want to use the input file, ensure it is in the `input/` sub-folder, then type `yes` or `y`. If not, type `no` or `n`. If an invalid response is received, the program will ask again.

If you are using a date range, the dialog box will read:
> `Input start date [yyyy-mm-dd]:`

Supply the start date in yyyy-mm-dd format (e.g., 2023-05-25 for May 25, 2023). If an invalid response is received, the program will ask again.

Next, the program will ask:
> `Input end date [yyyy-mm-dd]. Or just press enter to use today as the end date:`

Either supply the end date or press enter to proceed. If an invalid response is received, the program will ask again.

Finally, the program will retrieve the documents from the Federal Register, format them, and create an CSV file with today's date in the `output/` sub-folder.

## Deploying the Web App

The program was developed as a [web app](https://regulatorystudies.shinyapps.io/regulation-digest/) for distribution using the [Shiny for Python](https://shiny.posit.co/py/) package. The app is deployed using the [shinyapps.io hosted service](https://regulatorystudies.shinyapps.io/regulation-digest/).

After installing and configuring the `rsconnect-python` package (see instructions [here](https://docs.posit.co/shinyapps.io/guide/getting_started/#working-with-shiny-for-python)), you can deploy updates to the app using the `deploy.bat` script in the repository.

## Contact

Please reach out to <mfebrizio@gwu.edu> with feedback or questions or open an issue on this repository.
