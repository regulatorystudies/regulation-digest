from pathlib import Path
import subprocess

import oyaml as yaml

# base call to create env yml
base_call = ["conda", "env", "export", "-f"]

# no builds flag removes build information from yml
no_builds = ["environment_no_builds.yml", "--no-builds"]
subprocess.run(base_call + no_builds, shell=True)

# from history flag only documents packages explicitly imported
from_history = ["environment_from_history.yml", "--from-history"]
subprocess.run(base_call + from_history, shell=True)

p = Path(__file__).parent
files = (no_builds[0], from_history[0])
envs = []
for file in files:
    file = p / file
    with open(file, "r") as f:
        env_yml = yaml.safe_load(f)
    envs.append(env_yml)
    
    # remove extra env files
    if file.exists():
        file.unlink()

all_with_versions = envs[0].get("dependencies")
history_no_versions = envs[1].get("dependencies")

conda_list = [dep for dep in all_with_versions if (isinstance(dep, str)) and ((dep.split("=")[0] in history_no_versions) or (dep.startswith("pip")))]
#pip_version = [dep for dep in all_with_versions if (isinstance(dep, str)) and dep.startswith("pip")]
pip_list = [dep for dep in all_with_versions if (isinstance(dep, dict))]
#[pip for dep in all_with_versions if (isinstance(dep, dict)) for pip in dep.get("pip")]
env_list = conda_list + pip_list

new_yml = envs[0].copy()
new_yml.update({"dependencies": env_list})

new_file = p / "environment.yml"
with open(new_file, "w") as f:
    yaml.dump(new_yml, stream=f)
