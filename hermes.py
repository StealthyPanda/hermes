import json, os, sys
import colorama
import time
from hashlib import sha1



cwd = os.getcwd()

start = time.time()

superverbose = '-vv' in sys.argv
verbose = ('-v' in sys.argv) or superverbose

finalcommand = []

windowsglobal = "C:\\hermes"
linuxglobal = "/etc/hermes/"
macglobal = ""

if 'win32' in sys.platform : gfolder = windowsglobal
elif 'linux' in sys.platform : gfolder = linuxglobal
else : gfolder = macglobal

template = {
    "compiler" : "",
    "inputs" : [],
    "includes" : [],
    # "output" : "",
    "run" : False,
    "flags" : [],
}

#-----------------------------------------------------
#dealing with the global commands and stuff
if "global" in sys.argv:
    index = sys.argv.index('global')
    try:
        op = sys.argv[index + 1]
        if op != 'show':
            key = sys.argv[index + 2]
            if key == 'output':
                print(colorama.Fore.RED + colorama.Style.BRIGHT +
                      '"output" is not a valid key for global config!' + colorama.Style.RESET_ALL)
                sys.exit(1)
        if op != 'show':
            value = sys.argv[index + 3]
            if value == '.':
                if type(template[key]) == str: value = ""
                elif type(template[key]) == list: value = []
                elif type(template[key]) == bool: value = 'False'

    except IndexError:
        print(sys.argv)
        print(colorama.Fore.RED + colorama.Style.BRIGHT + 
              "Invalid syntax for changing globals!" + colorama.Style.RESET_ALL)
        sys.exit(1)

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


#load/generate hermes.json
try:
    with open(f"{cwd}/hermes.json", 'r') as file:
        config = json.load(file)
except FileNotFoundError as e:
    print("Generating hermes.json...")
    with open(f"{cwd}/hermes.json", 'w') as file:
        file.write(json.dumps({
            "compiler" : "",
            "inputs" : [],
            "includes" : [],
            "output" : "",
            "run" : False,
            "flags" : [],
        }, indent=4))
    try:
        os.mkdir(f"{cwd}/.hermes")
        os.mkdir(f"{cwd}/.hermes/objs")
        with open(f"{cwd}/.hermes/tracker.json", 'w') as file:
            json.dump(dict(), file, indent = 4)
    except FileExistsError: pass
    print(colorama.Fore.LIGHTGREEN_EX + colorama.Style.BRIGHT + 
        "Project config JSON file successfully generated! Hermes project initialized." + colorama.Style.RESET_ALL)
    sys.exit(0)

#-----------------------------------------------------------------------------------------
# dealing with default config values
# - default compiler is c++
# - default output file is *firstinputfilename*_output

defaults = None
try:
    with open(f"{gfolder}/globals.json", 'r') as file:
        defaults = json.load(file)
except FileNotFoundError:
    if verbose : print("Globals not found! Resorting to classic default values...")


run = config.pop('run', False if defaults is None else defaults['run'])

if 'flags' not in config.keys(): config['flags'] = []
if defaults is not None: config['flags'] += defaults['flags']

if 'includes' not in config.keys(): config['includes'] = []
if defaults is not None: config['includes'] += defaults['includes']

if not(config['inputs']):
    print("No input files given!")
    sys.exit(1)

if defaults is not None: config['inputs'] += defaults['inputs']

if not(config['includes']):
    pass

if not(config['compiler']): config['compiler'] = ('c++' if defaults is None else defaults['compiler'])
if not(config['compiler']): config['compiler'] = 'c++'

if not(config['output']):
    config['output'] = f"{config['inputs'][0].split('.')[1][1:]}_output"
config['output'] = f"{cwd}\\debug\\{config['output']}"

if verbose:pinp = colorama.Fore.LIGHTCYAN_EX +     f"Input Files       : {' '.join(config['inputs'])}" + colorama.Style.RESET_ALL

config['inputs'] = list(map(

    lambda x: f"{cwd}\\{x[2:]}" if (x[:2] == './' and x[-1] != '*') else x,
    # lambda x: f"{cwd}\\{x[2:]}" if (x[:2] == './') else x,

config['inputs']))
breakable = True

while breakable:
    breakable = False
    for i, each in enumerate(config['inputs']):
        if each[-1] == '*':
            folder = f"{cwd}\\{each[2:-1]}" if each[:2] == './' else f"{each[:-1]}"
            files = os.listdir(folder)
            for file in files:
                if '.' in file:
                    config['inputs'].append(f"{folder}{file}")
                else:
                    config['inputs'].append(f"{folder}{file}/*")
                    breakable = True
            del config['inputs'][i]




try:
    os.mkdir(f"{cwd}\\debug")
    print(colorama.Fore.GREEN + "Created `debug` folder" + colorama.Style.RESET_ALL)
except FileExistsError as e:
    pass

#-----------------------------------------------------------------------------------------


#----------------------------------------------------
#file tracking stuff

changes = []

tracks = None
try:
    with open(f'{cwd}/.hermes/tracker.json', 'r') as file : tracks = json.load(file)
except:
    tracks = dict()

if superverbose:
    print("File tracking hashes:")
    for each in tracks.keys():
        print(each, tracks[each])

for eachfile in config['inputs']:
    if eachfile in tracks.keys():
        with open(eachfile, 'r') as file:
            code = sha1(file.read().strip().encode()).hexdigest()
        if code != tracks[eachfile]:
            changes.append(eachfile)
            if superverbose: print(f"Changes in {eachfile}")
            tracks[eachfile] = code
    else:
        changes.append(eachfile)
        if superverbose: print(f"Changes in {eachfile}")
        with open(eachfile, 'r') as file:
            tracks[eachfile] = sha1(file.read().strip().encode()).hexdigest()

try:
    with open(f'{cwd}/.hermes/tracker.json', 'w') as file:
        file.write(json.dumps(tracks, indent=4))
except FileNotFoundError:
    os.mkdir(f"{cwd}/.hermes")
    os.mkdir(f"{cwd}/.hermes/objs")
    with open(f'{cwd}/.hermes/tracker.json', 'w') as file:
        file.write(json.dumps(tracks, indent=4))

# for eachchange in changes:
#     filename = eachchange.split('\\')[-1].split('/')[-1]
#     filename = filename.split('.')[0]
#     if superverbose: print(filename)
#     os.system()

if '-redo' in sys.argv : changes = config['inputs']

#----------------------------------------------------

#adding build optimizations
opt = 0
if '-b' in sys.argv : opt = 1
if '-bb' in sys.argv : opt = 2
if '-bbb' in sys.argv : opt = 3


argflags = {
    'includes' : '-I',
    'inputs'   : '',
    'output'   : '-o',
    'flags'    : '',
}


#--------------------------------------------------------------------------------------------------
#obj stuff

includesection = ""
for each in config['includes']:
    includesection += f'-I"{each}"'

if superverbose:print(f"Include section:\n{includesection}")

objsnames = []
for eachchange in changes:
    filename = eachchange.split('\\')[-1].split('/')[-1].split('.')[0]
    if verbose:
        print(colorama.Fore.GREEN +
            f"Updating objects for `{filename}`" + colorama.Style.RESET_ALL)
    if filename in objsnames: filename = f"{filename}1"
    
    objcomm = (f"{config['compiler']} -c {eachchange} -o {cwd}/.hermes/objs/{filename}.o {includesection} " +
        f"{['-O1', '-O2', '-O3'][opt - 1] if opt > 0 else ('-Ofast' if '-saikyou' in sys.argv else '')}")
    
    if superverbose:print(objcomm)

    if os.system(objcomm):
        end = time.time()
        print(colorama.Style.BRIGHT + colorama.Fore.RED +
              f"Compilation Failed! Error in `{filename}` Build failed in {str(end - start)[:4]}s" + colorama.Style.RESET_ALL)
        sys.exit(1)


#--------------------------------------------------------------------------------------------------



if verbose:
    print(colorama.Fore.LIGHTBLUE_EX +     f"Compiler          : {config['compiler']}" + colorama.Style.RESET_ALL)
    print(pinp)
    print(colorama.Fore.LIGHTYELLOW_EX +   f"Include Files     : {' '.join(config['includes'])}" + colorama.Style.RESET_ALL)
    print(colorama.Fore.LIGHTMAGENTA_EX +  f"Output file       : {config['output']}" + colorama.Style.RESET_ALL)
    print(colorama.Fore.LIGHTRED_EX +      f"Auto launch       : {run}" + colorama.Style.RESET_ALL)
    print(colorama.Fore.LIGHTCYAN_EX +     f"Additional flags  : {' '.join(config['flags'])}" + colorama.Style.RESET_ALL)
    print()



#------------------------------------------------------------------------------------------------------------------------------------------------
#force rebuilding the whole thing

if ('-f' in sys.argv) or ('-force' in sys.argv) or ('-release' in sys.argv):
    print(colorama.Style.BRIGHT + colorama.Fore.YELLOW +
          "Release mode, building application..." + colorama.Style.RESET_ALL)
    
    for each in config:
        if superverbose : print(each, config[each])
        if each == 'compiler':
            finalcommand.append(config[each])
            continue
        
        if config[each]:
            finalcommand.append(argflags[each])
            if type(config[each]) == list:
                for i, val in enumerate(config[each]):
                    if i: finalcommand.append(argflags[each])
                    if each != 'flags' : finalcommand.append(f"\"{val}\"")
                    else : finalcommand.append(f"{val}")
            else : finalcommand.append(f"\"{config[each]}\"")


    finalcommand = list(filter(lambda x:x, finalcommand))

    #--------------------------------------------------------------
    #build optimizations

    if opt:
        print(colorama.Style.BRIGHT + colorama.Fore.YELLOW +
            f"\nOptimizations O{opt} enabled! Building application..." + colorama.Style.RESET_ALL)
        finalcommand.append(f'-O{opt}')

    if ('-saikyou' in sys.argv) or ('-release' in sys.argv):
        print(
            colorama.Style.BRIGHT + colorama.Fore.BLUE +
            f"\nApplying fastest possible optimizations! Building application..." + colorama.Style.RESET_ALL
        )
        finalcommand.append('-Ofast')

    #--------------------------------------------------------------


    if superverbose:
        print()
        print(finalcommand)

    finalcommand = " ".join(finalcommand)

    if os.system(finalcommand) == 0:

        end = time.time()

        print(colorama.Fore.GREEN + colorama.Style.BRIGHT + f"Compilation successful! Build completed in {str(end - start)[:4]}s" + colorama.Style.RESET_ALL)

    else:
        end = time.time()
        print(colorama.Fore.RED + f"Compilation Failed! Build failed in {str(end - start)[:4]}s" + colorama.Style.RESET_ALL)
        sys.exit(1)

#------------------------------------------------------------------------------------------------------------------------------------------------


#---------------------------------------------------------------------------------------------------------------
#compiling all objects into final executable

foc = f"{config['compiler']} {cwd}/.hermes/objs/*.o -o {config['output']}"

for eachflag in config['flags']:
    foc += eachflag
    foc += ' '


if opt:
    print(colorama.Style.BRIGHT + colorama.Fore.YELLOW +
        f"\nOptimizations O{opt} enabled! Building application..." + colorama.Style.RESET_ALL)
    foc += (f'-O{opt}')

if '-saikyou' in sys.argv:
    print(
        colorama.Style.BRIGHT + colorama.Fore.BLUE +
        f"\nApplying fastest possible optimizations! Building application..." + colorama.Style.RESET_ALL
    )
    foc += ('-Ofast')

if superverbose:print(foc)
if os.system(foc):
    end = time.time()
    print(colorama.Style.BRIGHT + colorama.Fore.RED +
            f"Compilation Failed! Build failed in {str(end - start)[:4]}s" + colorama.Style.RESET_ALL)
    sys.exit(1)

end = time.time()
print(colorama.Style.BRIGHT + colorama.Fore.GREEN +
            f"Compilation Successful! Build succeeded in {str(end - start)[:4]}s" + colorama.Style.RESET_ALL)

#---------------------------------------------------------------------------------------------------------------



if run:
    print()
    start = time.time()
    code = os.system(f"{config['output']}.exe")
    end = time.time()

    code = (colorama.Fore.RED if code else colorama.Fore.GREEN) + f"code {code}" + colorama.Style.RESET_ALL

    print(f"\nExecution finished with exit {code} in {str(end - start)[:4]}s")
    os.system("pause")