#import os
from pathlib import Path
from pandas import DataFrame, read_csv
from regdigest.preprocessing import filter_actions

FILTER_ROUTINE = [  # title filters for routine actions
    r"^Privacy\sAct\sof\s1974", 
    r"^Airworthiness\sDirectives", 
    r"^Airworthiness\sCriteria", 
    r"^Fisheries\sof\sthe\s[\w]+;", 
    r"^Submission\sfor\sOMB\sReview;", 
    r"^Sunshine\sAct\sMeetings", 
    r"^Agency\sInformation\sCollection\sActivit[\w]+", 
    r"Notice\sof\sClosed\sMeetings$", 
    r"^Environmental\sImpact\sStatements;\sNotice\sof\sAvailability", 
    r"^Combined\sNotice\sof\sFilings", 
    r"Coastwise\sEndorsement\sEligibility\sDetermination\s[.]+\sVessel", 
    r"^Safety\sZone[\w]*", 
    r"^Air\sPlan\sApproval", 
    r"^Drawbridge\sOperation\sRegulation", 
    ]

test_dir = Path(__file__).parents[1].joinpath("output")
with open(test_dir / "federal_register_clips_2023-05-30(2).csv", "r") as f:
    df = read_csv(f)

df2 = filter_actions(df, filters=FILTER_ROUTINE, columns=("title", ))

print(len(df), len(df2))

