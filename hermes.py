import sys, os
import time
import colorama
import json
from typing import List
from hashlib import sha1

start = time.time()
cwd = os.getcwd()
sysargs = sys.argv

superverbose = '-vv' in sysargs
verbose = ('-v' in sysargs) or (superverbose)

platform = 'mac'
if 'win32' in sys.platform : platform = 'win'
elif 'linux' in sys.platform : platform = 'lin'

macfolder = ""
winfolder = "C:\\hermes\\"
linfolder = "/etc/hermes/"

template = {
    "compiler" : "",
    "inputs" : [],
    "includes" : [],
    "run" : False,
    "flags" : [],
    "output" : "",
}

changedfiles = []

projecthermes = template.copy()


#adding build optimizations
opt = 0
if '-b' in sys.argv : opt = 1
if '-bb' in sys.argv : opt = 2
if '-bbb' in sys.argv : opt = 3
if opt and verbose:
    print(
        colorama.Style.BRIGHT + colorama.Fore.YELLOW +
        f"Build optimizations level O{opt} enabled!" + colorama.Style.RESET_ALL
    )
opt = f"-O{opt}" if opt else ''
if '-saikou' in sysargs: opt = '-Ofast'
if (opt == '-Ofast') and verbose:
    print(
        colorama.Style.BRIGHT + colorama.Fore.BLUE +
        "最高(Saikou) mode enabled!\n⚡Applying fastest possible optimizations..." + colorama.Style.RESET_ALL
    )



def fixfolderstructure():
    global cwd

    try : os.mkdir(f"{cwd}/.hermes")
    except FileExistsError : pass
    except Exception as e:
        print(
            colorama.Fore.RED + "Error in fixing folder structure!\n" + str(e) + colorama.Style.RESET_ALL
        )
        sys.exit(1)
    
    try : os.mkdir(f"{cwd}/.hermes/objs")
    except FileExistsError : pass
    except Exception as e:
        print(
            colorama.Fore.RED + "Error in fixing folder structure!\n" + str(e) + colorama.Style.RESET_ALL
        )
        sys.exit(1)
    
    try : os.mkdir(f"{cwd}/.hermes/debug")
    except FileExistsError : pass
    except Exception as e:
        print(
            colorama.Fore.RED + "Error in fixing folder structure!\n" + str(e) + colorama.Style.RESET_ALL
        )
        sys.exit(1)

def processglobalcommand(index : int):
    """
    Processes the global command line args passed into hermes
    Index is the index of 'global' keyword in the commandline args.
    """
    global start, cwd, sysargs, superverbose, verbose, platform, template, macfolder, winfolder, linfolder

    op, key, value = None, sysargs[index], None
    
    try:
        op = sysargs[index + 1].lower()
        if op != 'show':
            key = sysargs[index + 2].lower()
            value = sysargs[index + 3].lower()
    except IndexError:
        if superverbose:print(sysargs)
        print(colorama.Fore.RED + colorama.Style.BRIGHT + 
              "Invalid syntax for changing globals!" + colorama.Style.RESET_ALL)
        sys.exit(1)
    
    if (op != 'show') and (key not in template.keys()):
        print(colorama.Fore.RED + colorama.Style.BRIGHT +
                f'"{key}" is not a valid key for global config!' + colorama.Style.RESET_ALL)
        sys.exit(1)

    #setting default values
    if value == '.':
        if type(template[key]) == str: value = ""
        elif type(template[key]) == list: value = []
        elif type(template[key]) == bool: value = 'False'

    gfolder = macfolder
    if platform == 'win' : gfolder = winfolder
    elif platform == 'lin' : gfolder = linfolder

    original = template.copy()
    del original['output']

    try:
        with open(f"{gfolder}/globals.json", 'r') as file:
            try : original = json.load(file)
            except Exception as e: pass
            
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
            newfile.write(json.dumps(original, indent=4))

        print(colorama.Fore.GREEN + colorama.Style.BRIGHT + 
                        "Globals generated successfully" + colorama.Style.RESET_ALL)
        sys.exit(0)

def inithermesproject():
    global cwd
    #make hermes json
    with open(f'{cwd}/hermes.json', 'w') as file:
        file.write(json.dumps(template, indent = 4))
    
    #making folders for hermes stuff
    fixfolderstructure()

    #trackers file
    with open(f'{cwd}/.hermes/tracker.json', 'w') as file:
        file.write("{}")
    
    print(colorama.Style.BRIGHT + colorama.Fore.GREEN +
          "Hermes project initialised successfully!" + colorama.Style.RESET_ALL)

def fitspattern(string : str, pattern : str) -> bool:
    if pattern == '*': return True

    splat = pattern.split('*')
    l = len(splat) - 1

    # print(splat)

    for i, each in enumerate(splat):
        if not each : continue
        # print(f"searching for {each} in {string}")
        if each in string:
            # print("found")
            ind = string.index(each)
            if i == 0:
                if pattern[0] != '*':
                    if ind != 0:
                        # print("exiting there")
                        return False
            if i == l:
                if pattern[-1] != '*':
                    if ind != (len(string) - len(each)):
                        # print("exiting here")
                        return False
            string = string[ind + len(each):]
        else:
            return False
    
    return True

def getallmatchingin(dir : str, pattern : str) -> List[str]:
    # print('received:', dir, 'pattern:', pattern)
    stuff = os.listdir(dir)
    if pattern == '*':
        matching = stuff
        matching = list(map(lambda x: f"{dir}/{x}", matching))
        return matching

    files = list(filter(lambda x: os.path.isfile(f"{dir}/{x}"), stuff))
    dirs = list(filter(lambda x: os.path.isdir(f"{dir}/{x}"), stuff))

    # print(stuff)
    # print(files)
    # print(dirs)

    matching = []

    if pattern[-1] == '/':
        matching = list(filter(lambda x:fitspattern(x, pattern[:-1]), dirs))
    else:
        matching = list(filter(lambda x:fitspattern(x, pattern), files))
    
    matching = list(map(lambda x: f"{dir}/{x}", matching))

    return matching

def processpathsetting(path : str) -> List[str]:
    # print("received:", path)
    if './' == path[:2]:
        path = f"{cwd}/{path[2:]}"
    
    path = "/".join(path.split('\\')).split('/')
    processed = []
    for each in (path):
        if each == '.': pass
        elif each == '..': processed.pop()
        else: processed.append(each)
    
    path = '/'.join(processed)

    if '*' not in path : return [path]

    path = path.split('/')

    paths = []

    later = ''
    for i, each in enumerate(path):
        if '*' in each:
            dir = "/".join(path[:i])
            if i < (len(path) - 1):
                each += '/'
                later = '/'.join(path[i + 1:])
                # print("processing:", each, "dir:", dir, "later:", later)
                paths = list(map(lambda x: f"{x}/{later}", getallmatchingin(dir, each)))
            else:
                # print("processing:", each, "dir:", dir)
                paths = getallmatchingin(dir, each)
            break

    
    processed = []

    for each in paths:
        processed += processpathsetting(each)
    # print("paths:", paths)
    # print("processed:", processed)
    return processed

def combineglobals():
    global projecthermes, macfolder, winfolder, linfolder

    globals = None
    
    gfolder = macfolder
    if platform == 'win' : gfolder = winfolder
    elif platform == 'lin' : gfolder = linfolder

    try:
        with open(f"{gfolder}/globals.json", 'r') as file:
            globals = json.load(file)
    except FileNotFoundError as e:
        if superverbose: print("Globals not found, skipping...")
        return
    
    for each in globals.keys():
        if each in projecthermes.keys():
            if type(globals[each]) == str:
                if not projecthermes[each] : projecthermes[each] = globals[each]
            elif type(globals[each]) == list:
                projecthermes[each] += globals[each]
            elif type(globals[each]) == False:
                pass
            else:
                pass
        else:
            projecthermes[each] = globals[each]

def getfilename(path: str) -> str:
    return path.split('/')[-1].split('\\')[-1]

def getheaders(code : str) -> List[str]:
    lines = list(filter(lambda x: x, map(lambda x:x.strip(), code.strip().split('\n'))))
    headers = []
    for each in lines:
        if '#include' in each:
            headers.append(each[len('#include'):].strip()[1:-1])
    return headers

def trackfiles():
    global projecthermes, changedfiles, verbose, superverbose, cwd

    headers = []
    included = []

    try:
        with open(f"{cwd}/.hermes/tracker.json", 'r') as file:
            tracks = json.load(file)
    except FileNotFoundError as e:
        tracks = dict()
    
    for eachfile in projecthermes['inputs']:
        filecontents = None
        with open(eachfile, 'r') as file:
            filecontents = file.read()
        
        hexcode = sha1(filecontents.strip().encode()).hexdigest()
        
        if eachfile not in tracks.keys():
            tracks[eachfile] = hexcode
            changedfiles.append(eachfile)
            fileheaders = getheaders(filecontents)
            for eachheader in fileheaders:
                for folder in ([cwd] + projecthermes['includes']):
                    if f"{folder}/{eachheader}" in tracks.keys():
                        with open(f"{folder}/{eachheader}", 'r') as file:
                            hashcode = sha1(file.read().strip().encode()).hexdigest()
                        if eachfile not in tracks[f"{folder}/{eachheader}"]['files']:
                            tracks[f"{folder}/{eachheader}"]['files'].append(eachfile)
                        if hashcode != tracks[f"{folder}/{eachheader}"]['hash']:
                            tracks[f"{folder}/{eachheader}"]['hash'] = hashcode
                            if verbose:
                                print(colorama.Style.BRIGHT +
                                    f"Updating header track `{folder}/{eachheader}`" +
                                    colorama.Style.RESET_ALL)
                            changedfiles += list(filter(lambda x: x not in changedfiles,
                                                        tracks[f"{folder}/{eachheader}"]['files']))
                    else:
                        try:
                            with open(f"{folder}/{eachheader}", 'r') as file:
                                hashcode = sha1(file.read().strip().encode()).hexdigest()
                            if verbose:
                                print(colorama.Style.BRIGHT +
                                    f"Updating header track `{folder}/{eachheader}`" +
                                    colorama.Style.RESET_ALL)
                            tracks[f"{folder}/{eachheader}"] = {
                                "hash" : hashcode,
                                "files" : [eachfile]
                            }
                        except FileNotFoundError : pass
            
        else:
            if tracks[eachfile] != hexcode:
                tracks[eachfile] = hexcode
                changedfiles.append(eachfile)
                fileheaders = getheaders(filecontents)
                for each in fileheaders:
                    if each not in included:
                        included.append(each)
                        headers.append((eachfile, each))

                fileheaders = getheaders(filecontents)
                for eachheader in fileheaders:
                    for folder in ([cwd] + projecthermes['includes']):
                        if f"{folder}/{eachheader}" in tracks.keys():
                            with open(f"{folder}/{eachheader}", 'r') as file:
                                hashcode = sha1(file.read().strip().encode()).hexdigest()
                            if eachfile not in tracks[f"{folder}/{eachheader}"]['files']:
                                tracks[f"{folder}/{eachheader}"]['files'].append(eachfile)
                            if hashcode != tracks[f"{folder}/{eachheader}"]['hash']:
                                tracks[f"{folder}/{eachheader}"]['hash'] = hashcode
                                if verbose:
                                    print(colorama.Style.BRIGHT +
                                        f"Updating header `{folder}/{eachheader}`" +
                                        colorama.Style.RESET_ALL)
                                changedfiles += list(filter(lambda x: x not in changedfiles,
                                                            tracks[f"{folder}/{eachheader}"]['files']))
                        else:
                            try:
                                with open(f"{folder}/{eachheader}", 'r') as file:
                                    hashcode = sha1(file.read().strip().encode()).hexdigest()
                                if verbose:
                                    print(colorama.Style.BRIGHT +
                                    f"Updating header track `{folder}/{eachheader}`" +
                                    colorama.Style.RESET_ALL)
                                tracks[f"{folder}/{eachheader}"] = {
                                    "hash" : hashcode,
                                    "files" : [eachfile]
                                }
                            except FileNotFoundError : pass
    
    for eachtrack in tracks.keys():
        if type(tracks[eachtrack]) == dict:
            with open(eachtrack, 'r') as file:
                hashcode = sha1(file.read().strip().encode()).hexdigest()
            if tracks[eachtrack]['hash'] != hashcode:
                tracks[eachtrack]['hash'] = hashcode
                if verbose:
                    print(colorama.Style.BRIGHT +
                        f"Updating header track `{eachtrack}`" +
                        colorama.Style.RESET_ALL)
                changedfiles += list(filter(lambda x: x not in changedfiles,
                                            tracks[eachtrack]['files']))


    if verbose:
        for eachfile in changedfiles:
            print(
                colorama.Fore.GREEN + f"Updating objs for `{eachfile}`" + colorama.Style.RESET_ALL
            )

    if superverbose:print(json.dumps(tracks, indent = 4))

    with open(f"{cwd}/.hermes/tracker.json", 'w') as file:
        file.write(json.dumps(tracks, indent = 4))

def updateobjs():
    global projecthermes, cwd, changedfiles, start, verbose, superverbose, opt

    slash = ord('\\')

    includesection = " ".join(
        list(map(
            lambda x: f'-I"{x if (x[-1] != "/") and (x[-1] != chr(slash)) else x[:-1]}"' if x else '',
            projecthermes['includes']
        ))
    )

    if superverbose:
        print("includesection:")
        print(includesection)
        print("changedfiles:")
        print(changedfiles)


    for each in changedfiles:
        if verbose:
            print(colorama.Fore.GREEN + colorama.Style.BRIGHT +
                f"Compiling object for `{getfilename(each)}`" + colorama.Style.RESET_ALL)
        comm = f"{projecthermes['compiler']} -c {each} -o {cwd}/.hermes/objs/{getfilename(each).split('.')[0]}.o {includesection} {opt}"
        if superverbose:
            print(comm)
        c = os.system(comm)
        if c:
            print(colorama.Fore.RED +
                  f"Build failed in {str(time.time() - start)[:4]}s with exit code {c}!"
                  + colorama.Style.RESET_ALL)
            sys.exit(1)

def buildfinalapp():
    global projecthermes, cwd, opt

    finalcommand = f"{projecthermes['compiler']} "

    for each in projecthermes['inputs']:
        finalcommand += f"{cwd}/.hermes/objs/{getfilename(each).split('.')[0]}.o "
    
    flags = projecthermes['flags']
    flags = " ".join(flags)

    finalcommand += f"-o {cwd}/.hermes/debug/{projecthermes['output']} {flags} {opt}"

    if superverbose:
        print("Final command:")
        print(finalcommand)
    
    c = os.system(finalcommand)
    if c:
        end = time.time()
        print(colorama.Style.BRIGHT + colorama.Fore.RED +
                f"Compilation Failed! Build failed in {str(end - start)[:4]}s" + colorama.Style.RESET_ALL)
        print(colorama.Style.DIM + colorama.Fore.RED +
                f"This was a linker error, most likely caused by missing object (.a, .o), .dll, .lib or .cxx files.\nEnsure all headers have their corresponding declarations, and all library flags are added." + colorama.Style.RESET_ALL)
        sys.exit(1)
    else:
        end = time.time()
        print(colorama.Style.BRIGHT + colorama.Fore.GREEN +
                f"Compilation Successful! Build succeeded in {str(end - start)[:4]}s\n" + colorama.Style.RESET_ALL)




#process global command if any
if 'global' in sysargs:
    processglobalcommand(sysargs.index('global'))
    sys.exit(0)

#initialising hermes
if 'hermes.json' not in os.listdir(cwd):
    inithermesproject()
    sys.exit(0)

fixfolderstructure()

with open(f"{cwd}/hermes.json", 'r') as file:
    projecthermes = json.load(file)
if not projecthermes['compiler']:
    projecthermes['compiler'] = 'c++'
projecthermes['inputs'] = list(filter(lambda x:x, projecthermes['inputs']))
if not projecthermes['inputs']:
    print(
        colorama.Fore.RED + colorama.Style.BRIGHT + 
        "Error! No input files provided!" + colorama.Style.RESET_ALL
    )
    sys.exit(1)

combineglobals()

#deal with wildcards and stuff
for each in projecthermes.keys():
    if type(projecthermes[each]) == list:
        processed = []
        for string in projecthermes[each]:
            processed += processpathsetting(string)
        projecthermes[each] = processed

if not projecthermes['output']:
    projecthermes['output'] = f"{getfilename(projecthermes['inputs'][0]).split('.')[0]}_output"

if superverbose:print(json.dumps(projecthermes, indent = 4))

#track file changes
if ('-redo' not in sysargs) and ('-force' not in sysargs) : trackfiles()
else : changedfiles = projecthermes['inputs']


#compile to objs
updateobjs()

#build final executable
buildfinalapp()

#run auto
if projecthermes['run']:
    start = time.time()
    c = os.system(f"{cwd}/.hermes/debug/{projecthermes['output']}.exe")
    end = time.time()
    
    print(f"\nExecution finished with " + 
          (colorama.Fore.GREEN if not c else colorama.Fore.RED) + f"exit code {c}" +
          colorama.Style.RESET_ALL + 
          f" in {str(end-start)[:4]}s!")

