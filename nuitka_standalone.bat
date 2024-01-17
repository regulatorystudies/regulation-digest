conda activate regdigest

python -m nuitka --standalone --remove-output --include-data-files=./regdigest/data/agencies_endpoint_metadata.json=./data/agencies_endpoint_metadata.json ./regdigest/retrieve_clips_program.py

python create_program_zip.py
