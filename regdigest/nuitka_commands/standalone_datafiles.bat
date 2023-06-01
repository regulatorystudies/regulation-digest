cd ".\Box Sync\_MF\Reg Digest\regulation-digest\regdigest\"

conda activate regdigest

python -m nuitka --standalone --remove-output --include-data-files=./data/agencies_endpoint_metadata.json=data/agencies_endpoint_metadata.json retrieve_documents.py
