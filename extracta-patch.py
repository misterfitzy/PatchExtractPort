"""

    Taken, with love, from: https://pastebin.com/VjwNV23n
    by Greg Linares: https://twitter.com/laughing_mantis/status/842100719385698305

    Ported to Python3 for use on a Mac M1, here goes

    - misterfitzy 16/March/2021
    
"""

banner = """ ____     ______   ______  ____     __  __     
/\  _`\  /\  _  \ /\__  _\/\  _`\  /\ \/\ \    
\ \ \L\ \\\\ \ \L\ \\\\/_/\ \/\ \ \/\_\\\\ \ \_\ \   
 \ \ ,__/ \ \  __ \  \ \ \ \ \ \/_/_\ \  _  \  
  \ \ \/   \ \ \/\ \  \ \ \ \ \ \L\ \\\\ \ \ \ \ 
   \ \_\    \ \_\ \_\  \ \_\ \ \____/ \ \_\ \_\\
    \/_/     \/_/\/_/   \/_/  \/___/   \/_/\/_/
                                               
                                               
 ____     __   __   ______  ____     ______   ____     ______   
/\  _`\  /\ \ /\ \ /\__  _\/\  _`\  /\  _  \ /\  _`\  /\__  _\  
\ \ \L\_\\\\ `\`\/'/'\/_/\ \/\ \ \L\ \\\\ \ \L\ \\\\ \ \/\_\\\\/_/\ \/  
 \ \  _\L `\/ > <     \ \ \ \ \ ,  / \ \  __ \\\\ \ \/_/_  \ \ \  
  \ \ \L\ \  \/'/\`\   \ \ \ \ \ \\\\ \ \ \ \/\ \\\\ \ \L\ \  \ \ \ 
   \ \____/  /\_\\\\ \_\  \ \_\ \ \_\ \_\\\\ \_\ \_\\\\ \____/   \ \_\\
    \/___/   \/_/ \/_/   \/_/  \/_/\/ / \/_/\/_/ \/___/     \/_/
                                                                
                                                                
 __  __      _          __     
/\ \/\ \   /' \       /'__`\   - Python3 port by misterfitzy
\ \ \ \ \ /\_, \     /\_\L\ \  
 \ \ \ \ \\\\/_/\ \    \/_/_\_<_ 
  \ \ \_/ \  \ \ \  __ /\ \L\ \\
   \ `\___/   \ \_\/\_\\\\ \____/
    `\/__/     \/_/\/_/ \/___/ 
 """

from colorama import Fore, Style
import argparse, sys, os
from os import path
import subprocess
import shlex
import glob
import shutil

parser=argparse.ArgumentParser()

parser.add_argument('--patch', help="""[REQUIRED] [NO DEFAULT] - Specifies the MSU file that will be extracted to the specified PATH folder and then organized into the x86, x64, WOW, JUNK, and BIN folders specified
    Extract command will be "expand -F:* <PATCH> <PATH>"
    Non MSU files have not been tested however if the extraction does not generate a CAB file of the same name (indicator of successful extraction of MSU files)
    the script assumes extraction failed.""")
parser.add_argument('--path',help="""[REQUIRED] [NO DEFAULT] - Specified the folder that the PATCH file will be extracted and organized into
    If the specified folders does not exist yet, the user will be prompted if they want to create it.
    Relative paths '.\POST' can be used but it has not extensively been tested.
    ***New in Version 1.1***
    The -PATH variable may be now omitted to expand to current directory""")
parser.add_argument('--x86', default='x86', help="""[OPTIONAL] [DEFAULT=\'x86\'] - Specifies the folder name within $PATH to store x86 patch binaries
    example: --x86 32bit""")
parser.add_argument('--x64', default='x64', help="""[REQUIRED] [DEFAULT=\'x64\'] - Specifies the folder name within $PATH to store x64 patch binaries
    example: --x64 64bit""")
parser.add_argument('--wow', default='WOW64', help="""[OPTIONAL] [DEFAULT=\'WOW64\'] - Specifies the folder name within $PATH to store wow64 type patch binaries
    example: --wow sysWOW64""")
parser.add_argument('--msil', default='MSIL', help="""<STRING:Foldername> [OPTIONAL] [DEFAULT=\'MSIL\'] *** New in Version 1.1***
    Specifies the folder name within $PATH to store .NET type patch binaries
    example: --msil dotnet
""")
parser.add_argument('--junk', default='JUNK', help="""<STRING:Foldername> [OPTIONAL] [DEFAULT=\'JUNK\'] - Specifies the folder name within $PATH to store resource, catalog, and other generally useless for diffing patch binaries
    example: --junk res""")
parser.add_argument('--bin', default='PATCH',  help="""<STRING:Foldername> [OPTIONAL] [DEFAULT=\'PATCH\'] - Specifies the folder name within $PATH to store extraction xml and original patch msu and cab files
    example: --bin bin""")

args=parser.parse_args()

def print_banner():
    print(Fore.MAGENTA)
    print(banner)
    print(Style.RESET_ALL)

def file_dir_exists(filepath):
    if(os.path.exists(filepath)):
        return True
    else:
        return False

def execute_shell(cmd):
    cmd_list = shlex.split(cmd)    
    process = subprocess.run(cmd_list, check=True, stdout=subprocess.PIPE, universal_newlines=True, shell=False)
    output = process.stdout

    return output

def is_ms_cabinet_file(filepath):
    cab_banner = "Microsoft Cabinet archive data"
    shell_output = execute_shell("file {}".format(filepath))

    if cab_banner in shell_output:
        return True
    else:
        return False 

def print_options_summary(patch_file, patch_output_dir, x86, x64, wow, msil, junk, _bin):
    print("Options summary")
    print("Patch to Extract: {}".format(patch_file))
    print("Extraction Path: {}".format(patch_output_dir))
    print("x86 File Storage Folder Name: {}".format(x86))
    print("x64 File Storage Folder Name: {}".format(x64))
    print("WOW64 File Storage Folder Name: {}".format(wow))
    print("MSIL File Storage Folder Name: {}".format(msil))
    print("Junk File Storage Folder Name: {}".format(junk))
    print("Orignal Patch File Storage Folder Name: {}".format(_bin))

def verify_or_create_dir(dir_path):
    if not file_dir_exists(dir_path):
        # Create the directory as it doesn't exist 
        try:
            os.mkdir(dir_path)
        except OSError:
            print ("Creation of the directory {} failed".format(path))
    else:
        # Directory exists
        print("Dir {} already exists.".format(dir_path))

def move_file(src, dst):
    try: 
        shutil.move(src, dst) 
    except Exception as e:
        # print("{} already exists in {}...".format(cab, bin_dir))
        print(e)

def rename_and_move_folders(folder_type, target_dir): 
    # msil 
    root, dirs, files = next(os.walk(target_dir))
    for sub_dir in dirs:
        if '{}_microsoft-windows-'.format(folder_type) in sub_dir:
            newfolder = sub_dir.replace("{}_microsoft-windows-".format(folder_type), "")
            newname = newfolder.split("_")[0]
            version = newfolder.split("_")[2]
            newfolder_name = newname + "_" + version
            move_file(os.path.join(target_dir, sub_dir), os.path.join(target_dir, newfolder_name))
        elif '{}_'.format(folder_type) in sub_dir:
            newfolder = sub_dir.replace("{}_".format(folder_type), "")
            newname = newfolder.split("_")[0]
            version = newfolder.split("_")[2]
            newfolder_name = newname + "_" + version
            move_file(os.path.join(target_dir, sub_dir), os.path.join(target_dir, newfolder_name))

    # manifest
def extract_cab_at(dest_dir, cab_path, bin_dir, junk_dir, x86_dir, x64_dir, wow64_dir, msil_dir):
    #  cabextract -d windows10.0-kb4565351-x64_e4f46f54ab78b4dd2dcef193ed573737661e5a10 windows10.0-kb4565351-x64_e4f46f54ab78b4dd2dcef193ed573737661e5a10.msu
    extract_cmd = "cabextract -d {} {}".format(dest_dir, cab_path)

    print(extract_cmd)
    execute_shell(extract_cmd)

    # Get the sub cabs, but not WSUSSCAN.cab
    cabs = glob.glob(os.path.join(dest_dir, '*.cab'))
    cabs = [cab for cab in cabs if 'WSUSSCAN.cab' not in cab]

    # And extract...
    for cab in cabs:
        # print(cab)
        extract_cmd = "cabextract -d {} {}".format(dest_dir, cab)

        print(extract_cmd)
        execute_shell(extract_cmd)
   
        try: 
            shutil.move(cab, bin_dir) 
        except Exception as e:
            # print("{} already exists in {}...".format(cab, bin_dir))
            print(e)
            
    # Tidy up the expanded files
    root, dirs, files = next(os.walk(dest_dir))
    # print(dirs) 
    for cab_dir in dirs:
        # print(cab_dir)
        if '.resources_' in cab_dir:
            move_file(os.path.join(dest_dir, cab_dir), junk_dir)  
            continue
        if 'x86_' in cab_dir:
            move_file(os.path.join(dest_dir, cab_dir), x86_dir)  
            continue
        if 'amd64_' in cab_dir:
            move_file(os.path.join(dest_dir, cab_dir), x64_dir)  
            continue
        if 'wow64_' in cab_dir:
            move_file(os.path.join(dest_dir, cab_dir), wow64_dir)  
            continue
        if 'msil_' in cab_dir:
            move_file(os.path.join(dest_dir, cab_dir), msil_dir)  
            continue

    # Rename and move the directories
    rename_and_move_folders('x86', x86_dir)
    rename_and_move_folders('amd64', x64_dir)
    rename_and_move_folders('wow64', wow64_dir)
    rename_and_move_folders('msil', msil_dir)

    # manifest
    root, dirs, files = next(os.walk(dest_dir))
    for sub_dir in files:
        if '.manifest' in sub_dir or '.cat' in sub_dir or '.mum' in sub_dir:
            move_file(os.path.join(dest_dir, sub_dir), os.path.join(junk_dir, sub_dir))
    
    # WSUSSCAN.cab
    root, dirs, files = next(os.walk(dest_dir))
    for sub_dir in files:
        if 'WSUSSCAN.cab' in sub_dir:
            move_file(os.path.join(dest_dir, sub_dir), os.path.join(bin_dir, sub_dir))


def main():
    if args.patch is None:
        print("Error: No PATCH file specified.  Specify a valid Microsoft MSU Patch with the --patch argument")
        sys.exit(1)

    # Get the patch file full path
    patch_filename = args.patch
    cwd = os.getcwd()
    patch_file = os.path.join(cwd, patch_filename)
    print(patch_file)

    # Check the provided patch file exists
    if not file_dir_exists(patch_file):
        print("The patch at [{}] could not be found.".format(patch_file))
        sys.exit(1)

    # Get the patch output directory
    if args.path is None:
        print("No PATH folder specified.")
        sys.exit(1)

    patch_output_path = args.path
    patch_output_dir = os.path.join(cwd, patch_output_path)
    print(patch_output_dir)
    patch_dir = os.path.join(cwd, patch_output_dir)

    # Check the provided output dir exists
    if not file_dir_exists(patch_dir):
        print("The path folder you set [{}] does not exist.".format(patch_dir))
        sys.exit(1)

    # Check the type of the MSU file to make sure it's good to go
    if not is_ms_cabinet_file(patch_file):
        print("The MSU does not appear to be a valid Microsoft cabinet archive.")
        sys.exit(1)
   
    print(args) 
    print_options_summary(patch_file, patch_output_dir, args.x86, args.x64, args.wow, args.msil, args.junk, args.bin)    
    bin_dir = os.path.join(patch_dir, args.bin)
    junk_dir = os.path.join(patch_dir, args.junk)
    x86_dir = os.path.join(patch_dir, args.x86)
    x64_dir = os.path.join(patch_dir, args.x64)
    wow64_dir = os.path.join(patch_dir, args.wow)
    msil_dir = os.path.join(patch_dir, args.msil)

    verify_or_create_dir(patch_dir)
    verify_or_create_dir(x86_dir)
    verify_or_create_dir(x64_dir)
    verify_or_create_dir(wow64_dir)
    verify_or_create_dir(msil_dir)
    verify_or_create_dir(junk_dir)
    verify_or_create_dir(bin_dir)

    extract_cab_at(patch_dir, patch_file, bin_dir, junk_dir, x86_dir, x64_dir, wow64_dir, msil_dir)

if __name__ == "__main__":
    print_banner()
    main()


