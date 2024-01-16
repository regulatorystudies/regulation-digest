from pathlib import Path
import shutil


class MissingPathError(Exception):
    pass


def move_dist(program_name: str):
    
    p = Path(__file__)
    dist_path = p.parents[1].joinpath(f"{program_name}.dist")
    new_dist_path = p.parents[1].joinpath(program_name, f"{program_name}.dist")
    program_path = p.parents[1].joinpath(program_name)
    
    if not program_path.exists():
        program_path.mkdir()
    
    if dist_path.exists():
        dir_res = shutil.copytree(dist_path, new_dist_path, dirs_exist_ok=True)
        print(f"Copied {Path(dir_res).name} to new directory and deleted old directory.")
        return {
            "dist_path": dist_path, 
            "new_dist_path": new_dist_path, 
            "program_path": program_path
            }
    else:
        print("No program to copy.")


def create_zip(program_name: str, path_dict: dict = None, supply_path: bool = False, **kwargs):
    
    if supply_path:
        program_path = kwargs.get("program_path")
    elif (not supply_path) and (path_dict is not None):
        program_path = path_dict.get("program_path")
    else:
        raise MissingPathError("No program path supplied.")
    
    zip_res = shutil.make_archive(program_name, "zip", program_path)
    if Path(zip_res).exists():
        print(f"Created zip file at {zip_res}.")
        return True
    else:
        return False


def main(program_name: str, zip_only_ok: bool = True):
    
    path_dict = move_dist(program_name)
    if path_dict is not None:
        zipped = create_zip(program_name, path_dict)
        dist_path = path_dict.get("dist_path")
        shutil.rmtree(dist_path)
    elif (path_dict is None) and zip_only_ok:
        program_path = Path(__file__).parents[1].joinpath(program_name)
        zipped = create_zip(program_name, supply_path=True, program_path=program_path)
    else:
        zipped = False
        print("Failed to create zip file.")
    return zipped


if __name__ == "__main__":

    main("retrieve_clips_program")
