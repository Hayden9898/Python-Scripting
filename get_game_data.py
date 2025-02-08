import os 
import json
import shutil
from subprocess import PIPE, run
import sys

GAME_DIR_PATTERN = "game"
GAME_CODE_EXTENSION = ".go"
GAME_COMPILE_COMMAND = ["go", "build"]

#Strip pathnames of the game ending
def get_name_from_paths(paths, to_strip): 
    newnames = []
    for path in paths:
        _, dir_name = os.path.split(path)
        new_dir_name = dir_name.replace(to_strip, "")
        newnames.append(new_dir_name)
    return newnames

def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)

#function to recursively overwrite any preexisting files 
def copy_and_overwrite(source, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(source, dest)

def find_all_game_paths(source):
    game_paths = []
    #recursively search through the source file
    for root, dirs, files in os.walk(source): 
        for directory in dirs:
            if GAME_DIR_PATTERN in directory:
                path = os.path.join(source, directory)
                game_paths.append(path)
        #break since we only want to search the top floor of the directory, ignore all files outside of directories
        break 

    return game_paths

def make_json_metadata_file(path, game_dirs):
    data = {
        "gameNames": game_dirs,
        "numberOfGames": len(game_dirs)
    }
    #open the file in write mode and add JSON data, then file automatically closes after function exectures
    with open(path, "w") as f:
        json.dump(data, f)

#Search only the root level directory for files with .go extension and break after first occurance
def compile_game_code(path):
    code_file_name = None
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(GAME_CODE_EXTENSION):
                code_file_name = file
                break
        break

    if code_file_name is None:
        return
    command = GAME_COMPILE_COMMAND + [code_file_name]
    run_command(command, path)

#Change into path directory, run the code by going through a pipeline that connects the script to the processor, then go back to original directory
def run_command(command, path):
    cwd = os.getcwd()
    os.chdir(path)

    result = run(command, stdout=PIPE, stdin=PIPE, universal_newlines=True)
    print("compile result", result)

    os.chdir(cwd)

def main(source, target):
    cwd = os.getcwd()
    source_path = os.path.join(cwd, source)
    target_path = os.path.join(cwd, target)

    game_paths = find_all_game_paths(source)
    new_game_dirs = get_name_from_paths(game_paths, "_game")
    create_dir(target_path)

    for src, dest in zip(game_paths, new_game_dirs):
        des_path = os.path.join(target_path, dest)
        copy_and_overwrite(src, des_path)
        compile_game_code(des_path)

    json_path = os.path.join(target_path, "metadata.json")
    make_json_metadata_file(json_path, new_game_dirs)


if __name__ == "__main__":
    args = sys.argv
    if len(args) != 3:
        raise Exception("You must pass a source and target directory - only")
    
    source, target = args[1:]
    main(source,target)