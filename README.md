# regulation-digest

Federal Register documents for the GW Regulatory Studies Center Regulation Digest

## Instructions

### Agency Rulemaking Highlights

Use the code in `retrieve_register_clips.py` to retrieve data on rulemakings from the past week. Follow these steps:

1. Open command prompt or terminal and change the directory to the folder where the Python script, `retrieve_register_clips.py`, is contained.

2. Run `python retrieve_register_clips.py` in the terminal.

3. When prompted, enter the beginning date for the range of FR documents you want to retrieve (eg, yyyy-mm-dd). Starting at this date, the program will return all documents published from that date to the present FR issue. If the url does not open automatically, copy it from the terminal and paste it into a web browser.

4. Download the returned csv file and create new columns for "notes" and "category."

5. Work through the spreadsheet, categorizing the documents as blue, green, yellow, or red entries (ie, b, g, y, r). Then filter the documents by those categorized entries and paste them into an xlsx workbook. Add notes as appropriate.

6. Sort by category and agency_names. Color the remaining entries by category, then delete the columns for category, significant, and correction_of.

7. Share the document!

## Installation

Two options:
  1. Download a Python interpreter, create the environment, and run script.
  2. Download compiled program zip file and run (Python not required).

## Usage

### Python Interpreter

TBD

### Compiled Program

1. Download the zip file containing the program.

