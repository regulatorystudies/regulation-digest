import asyncio
from datetime import date
from dateutil.relativedelta import relativedelta, TH

from pandas import DataFrame
from shiny import reactive
from shiny.express import input, render, ui

from regdigest.retrieve_documents import retrieve_documents

TODAY = date.today()

# start date
LAST_THU = TODAY + relativedelta(weekday=TH(-1))

SHOW_COLUMNS = ["publication_date", "parent_agency_names", "title", "action", "citation", "url", "significant", "3f1_significant", ]

ui.page_opts(title="Retrieve FR Clips for the Regulation Digest", fillable=True)

ui.input_date_range(
    "input_dates", 
    "Date range:", 
    start=LAST_THU, 
    end=TODAY, 
    ) #, width="100%")


@render.download(label="Download Data as CSV", filename=f"federal_register_clips_{TODAY}.csv")
async def download():
    await asyncio.sleep(0.25)
    yield get_data().to_csv(index=False)


ui.input_action_button("view", "Browse Data", )


@render.data_frame
@reactive.event(input.view)
def table_of_rules():
    df = get_data()
    return render.DataGrid(df.loc[:, [c for c in SHOW_COLUMNS if c in df.columns]], width="100%")


@reactive.calc
def get_data():
    results = retrieve_documents(*input.input_dates(), input_path=None)
    if results is None:
        return DataFrame(columns=SHOW_COLUMNS)
    else:
        results = results.reset_index()
        results.loc[:, "url"] = [fr"https://www.federalregister.gov/d/{r}" for r in results["document_number"].to_list()]
        return results
