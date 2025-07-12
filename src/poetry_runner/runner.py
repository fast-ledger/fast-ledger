from pathlib import Path
import subprocess
import runpy
import sys
import os

f_path = Path(__file__)
f_path_list = f_path.parts
bd_index = f_path_list.index("src")
base_dir = "\\".join(f_path_list[:bd_index])
os.chdir(base_dir)

print("\npoetry install\n----------------------------------------------------")

process = subprocess.Popen(
    ["poetry", "install"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    universal_newlines=True,
)
for line in process.stdout:
    print(line, end="")

print("----------------------------------------------------")

path = Path(sys.argv[1]).resolve()
path_list = path.parts
index = path_list.index("src")
module = ".".join(path_list[index:]).replace(".py", "")

print(f"\nMoved to {base_dir}")

if path == f_path:
    print("Stop running this file")
else:
    runpy.run_module(module, run_name="__main__")
