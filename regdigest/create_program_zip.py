from pathlib import Path
import shutil


def move_zip_dist(program_name: str):
    
    p = Path(__file__)
    dist_path = p.parents[1].joinpath(f"{program_name}.dist")
    new_dist_path = p.parents[1].joinpath(program_name, f"{program_name}.dist")
    program_path = p.parents[1].joinpath(program_name)
    
    if dist_path.exists() and program_path.exists():
        dir_res = shutil.copytree(dist_path, new_dist_path, dirs_exist_ok=True)
        zip_res = shutil.make_archive(program_name, "zip", program_path)
        if new_dist_path.exists():
            shutil.rmtree(dist_path)
        print(
            f"Copied {Path(dir_res).name} to new directory and deleted old directory.", 
            f"Created zip file at {zip_res}.", 
            sep="\n"
            )


if __name__ == "__main__":

    move_zip_dist("retrieve_clips_program")
