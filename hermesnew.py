import sys, os
import time
import colorama
import json

start = time.time()
cwd = os.getcwd()
sysargs = sys.argv

superverbose = '-vv' in sysargs
verbose = ('-v' in sysargs) or (superverbose)

platform = 'mac'
if 'win32' in sys.platform : platform = 'win'
elif 'linux' in sys.platform : platform = 'lin'

template = {
    "compiler" : "",
    "inputs" : [],
    "includes" : [],
    "run" : False,
    "flags" : [],
}

templatestr = '''
{
    //full compiler path or equivalent command line command (eg "c++" or "gcc")
    "compiler" : "",

    //input *.c and *.cxx files (both internal and external to the project folder)
    "inputs" : [],

    //external header files
    "includes" : [],

    //run program automatically after building
    "run" : false,

    //any additional flags, added to compiler command as is
    "flags" : []
}
'''


def processglobalcommand(index):
    global start, cwd, sysargs, superverbose, verbose, platform

    op, key, value = None, sysargs[index], None
    
    try:
        op = sysargs[index + 1]
        if op != 'show':
            key = sysargs[index + 2]
            value = sysargs[index + 3]
    except IndexError:
        if superverbose:print(sysargs)
        print(colorama.Fore.RED + colorama.Style.BRIGHT + 
              "Invalid syntax for changing globals!" + colorama.Style.RESET_ALL)
        sys.exit(1)
    
    if key == 'output':
        print(colorama.Fore.RED + colorama.Style.BRIGHT +
                '"output" is not a valid key for global config!' + colorama.Style.RESET_ALL)
        sys.exit(1)

    if value == '.':
        if type(template[key]) == str: value = ""
        elif type(template[key]) == list: value = []
        elif type(template[key]) == bool: value = 'False'

    gfolder = ""
    if platform == 'win' : gfolder = "C:\\hermes"
    elif platform == 'lin' : gfolder = "/etc/hermes/"

    try:
        with open(f"{gfolder}/globals.json", 'r') as file:
            try : original = json.load(file)
            except Exception as e:
                # print(e)
                original = {
                    "compiler" : "",
                    "inputs" : [],
                    "includes" : [],
                    # "output" : "",
                    "run" : False,
                    "flags" : [],
                }
            
        with open(f"{gfolder}/globals.json", 'w') as file:
            if (op == 'change'):
                if type(original[key]) == str : original[key] = value
                elif type(original[key]) == list : original[key] = [value] if type(value) != list else value
                elif type(original[key]) == bool : original[key] = ('true' == value.lower())
                
                file.write(json.dumps(original, indent=4))
                
                print(colorama.Fore.GREEN + colorama.Style.BRIGHT + 
                "Value changed successfully" + colorama.Style.RESET_ALL)
                sys.exit(0)
            elif (op == 'append'):
                try:
                    original[key].append(value)
                    
                    file.write(json.dumps(original, indent=4))
                    
                    print(colorama.Fore.GREEN + colorama.Style.BRIGHT + 
                        "Value appended successfully" + colorama.Style.RESET_ALL)
                    sys.exit(0)
                except AttributeError as e:
                    print(e)
                    print(colorama.Fore.RED + colorama.Style.BRIGHT +
                        "Appending not supported on the given key!" + colorama.Style.RESET_ALL)
                    sys.exit(1)
            elif (op == 'show'):
                print(json.dumps(original, indent = 4))
                file.write(json.dumps(original, indent = 4))
                sys.exit(0)
    except FileNotFoundError as e:
        print(f"Globals folder does not exist yet, generating at {gfolder}...")
        
        os.mkdir(gfolder)
        with open(f"{gfolder}/globals.json", 'w') as newfile:
            newfile.write(json.dumps({
                "compiler" : "",
                "inputs" : [],
                "includes" : [],
                # "output" : "",
                "run" : False,
                "flags" : [],
            }, indent=4))

        print(colorama.Fore.GREEN + colorama.Style.BRIGHT + 
                        "Globals folder generated successfully" + colorama.Style.RESET_ALL)
        sys.exit(0)