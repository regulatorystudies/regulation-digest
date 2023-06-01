cd ".\Box Sync\_MF\Reg Digest\regulation-digest\regdigest\"

conda activate regdigest

python -m nuitka --standalone --remove-output retrieve_documents.py
