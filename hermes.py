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


def fixfolderstructure(folder : str):

    try : os.mkdir(f"{folder}/.hermes")
    except FileExistsError : pass
    except Exception as e:
        print(
            colorama.Fore.RED + "❌ Error in fixing folder structure!\n" + str(e) + colorama.Style.RESET_ALL
        )
        sys.exit(1)
    
    try : os.mkdir(f"{folder}/.hermes/objs")
    except FileExistsError : pass
    except Exception as e:
        print(
            colorama.Fore.RED + "❌ Error in fixing folder structure!\n" + str(e) + colorama.Style.RESET_ALL
        )
        sys.exit(1)
    
    try : os.mkdir(f"{folder}/.hermes/debug")
    except FileExistsError : pass
    except Exception as e:
        print(
            colorama.Fore.RED + "❌ Error in fixing folder structure!\n" + str(e) + colorama.Style.RESET_ALL
        )
        sys.exit(1)

def processglobalcommand(index : int): 
    """
    Processes the global command line args passed into hermes
    Index is the index of 'global' keyword in the commandline args.
    """
    # global start, cwd, sysargs, superverbose, verbose, platform, template, macfolder, winfolder, linfolder

    op, key, value = None, sysargs[index], None
    
    try:
        op = sysargs[index + 1].lower()
        if op != 'show':
            key = sysargs[index + 2].lower()
            value = sysargs[index + 3].lower()
    except IndexError:
        if superverbose:print(sysargs)
        print(colorama.Fore.RED + colorama.Style.BRIGHT + 
              "❌ Invalid syntax for changing globals!" + colorama.Style.RESET_ALL)
        sys.exit(1)
    
    if (op != 'show') and (key not in template.keys()):
        print(colorama.Fore.RED + colorama.Style.BRIGHT +
                f'🙅 "{key}" is not a valid key for global config!' + colorama.Style.RESET_ALL)
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
                "👌 Value changed successfully" + colorama.Style.RESET_ALL)
                sys.exit(0)
            elif (op == 'append'):
                try:
                    original[key].append(value)
                    
                    file.write(json.dumps(original, indent=4))
                    
                    print(colorama.Fore.GREEN + colorama.Style.BRIGHT + 
                        "👌 Value appended successfully" + colorama.Style.RESET_ALL)
                    sys.exit(0)
                except AttributeError as e:
                    print(e)
                    print(colorama.Fore.RED + colorama.Style.BRIGHT +
                        "🙅 Appending not supported on the given key!" + colorama.Style.RESET_ALL)
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
                        "👌 Globals generated successfully" + colorama.Style.RESET_ALL)
        sys.exit(0)

def inithermesproject(folder : str):
    #make hermes json
    with open(f'{folder}/hermes.json', 'w') as file:
        file.write(json.dumps(template, indent = 4))
    
    #making folders for hermes stuff
    fixfolderstructure(folder)

    #trackers file
    with open(f'{folder}/.hermes/tracker.json', 'w') as file:
        file.write("{}")
    
    print(colorama.Style.BRIGHT + colorama.Fore.GREEN +
          "👌 Hermes project initialised successfully!" + colorama.Style.RESET_ALL)

def fitspattern(string : str, pattern : str) -> bool:
    if pattern == '*': return True

    splat = pattern.split('*')
    l = len(splat) - 1


    for i, each in enumerate(splat):
        if not each : continue
        if each in string:
            ind = string.index(each)
            if i == 0:
                if pattern[0] != '*':
                    if ind != 0:
                        return False
            if i == l:
                if pattern[-1] != '*':
                    if ind != (len(string) - len(each)):
                        return False
            string = string[ind + len(each):]
        else:
            return False
    
    return True

def getallmatchingin(dir : str, pattern : str) -> List[str]:
    stuff = os.listdir(dir)
    if pattern == '*':
        matching = stuff
        matching = list(map(lambda x: f"{dir}/{x}", matching))
        return matching

    files = list(filter(lambda x: os.path.isfile(f"{dir}/{x}"), stuff))
    dirs = list(filter(lambda x: os.path.isdir(f"{dir}/{x}"), stuff))


    matching = []

    if pattern[-1] == '/':
        matching = list(filter(lambda x:fitspattern(x, pattern[:-1]), dirs))
    else:
        matching = list(filter(lambda x:fitspattern(x, pattern), files))
    
    matching = list(map(lambda x: f"{dir}/{x}", matching))

    return matching

def processpathsetting(folder : str, path : str) -> List[str]:
    if './' == path[:2]:
        path = f"{folder}/{path[2:]}"
    
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
                paths = list(map(lambda x: f"{x}/{later}", getallmatchingin(dir, each)))
            else:
                paths = getallmatchingin(dir, each)
            break

    
    processed = []

    for each in paths:
        processed += processpathsetting(folder, each)
    return processed

def getfilename(path: str) -> str:
    return path.split('/')[-1].split('\\')[-1]

def getfilepath(path: str) -> str:
    p = '/'.join(path.split('\\')).split('/')
    if '.' in p[-1] : return '/'.join(p[:-1])
    else : return '/'.join(p)

def combineglobals():
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

def getheaders(code : str) -> List[str]:
    lines = list(filter(lambda x: x, map(lambda x:x.strip(), code.strip().split('\n'))))
    insidecomment = False
    for i, each in enumerate(lines):
        if '/*' in each:
            # print('trigged here', i, each)
            insidecomment = True
            lines[i] = each[:each.index('/*')]
        elif '*/' in each:
            # print('trigged there', i, each)
            insidecomment = False
            lines[i] = each[each.index('*/') + 2:]
        elif insidecomment:
            # print('trigged where', i, each)
            lines[i] = ''
    
    lines = list(filter(lambda x : x, lines))
    headers = []
    for each in lines:
        if ('#include' in each) and ('//' != each[:2]):
            h = each[len('#include'):].strip()
            if (h[0] == h[-1]) and (h[0] == '"') : headers.append(h[1:-1])
    return headers

def haschanged(filename : str, tracks : dict) -> bool:
    if filename not in tracks: return True

    filehex = None
    try:
        with open(filename, 'r') as file:
            filehex = sha1(file.read().strip().encode()).hexdigest()
    except Exception as e:
        print(
            colorama.Fore.RED + colorama.Style.BRIGHT +
            f'🔍 Error in reading file `{filename}`!'
        )
        return
    
    if tracks[filename] != filehex : return True

    with open(filename, 'r') as file:
        heads = getheaders(file.read().strip())

    path = getfilepath(filename)
    heads = list(map(
        lambda x : f"{path}/{x}",
        heads
    ))

    heads = list(map(
        lambda x : haschanged(x, tracks),
        heads
    ))

    # for each in heads:
    #     if haschanged(each, tracks):
    #         with open() as file:
    #             tracks[each] = sha1(file.read().strip().encode()).hexdigest()
    
    # return (heads != [])

    for each in heads:
        if each : return True
    
    return False

def updatetracks(filename : str, tracks : dict) -> dict:
    filehex = None
    try:
        with open(filename, 'r') as file:
            filehex = sha1(file.read().strip().encode()).hexdigest()
    except Exception as e:
        print(
            colorama.Fore.RED + colorama.Style.BRIGHT +
            f'🔍 Error in reading file `{filename}`!'
        )
        return
    
    tracks[filename] = filehex

    with open(filename, 'r') as file:
        heads = getheaders(file.read().strip())

    path = getfilepath(filename)
    heads = list(map(
        lambda x : (f"{path}/{x}"),
        heads
    ))

    for eachhead in heads:
        updatetracks(eachhead, tracks)

def makeobj(filename : str, settings : dict) -> int:
    command = f"{settings['compiler']} -o {cwd}/.hermes/objs/{getfilename(filename).split('.')[0]}.o -c {filename} "
    for each in settings['includes']:
        command += f" -I {each} "
    command += ' '.join(settings['flags'])
    command += f' {opt} '


    if os.system(command):
        print(
            colorama.Fore.RED + colorama.Style.BRIGHT + 
            f"❌ Compilation error in `{filename}`!" + colorama.Style.RESET_ALL
        )
        print()
        return 1
    return 0













def main():
    #dealing with global commands
    if 'global' in sysargs:
        processglobalcommand(sysargs.index('global'))
        sys.exit(0)

    #checking if hermes has been initialised. if not, then initialise.
    projecthermes = dict()
    try:
        with open(f'{cwd}/hermes.json', 'r') as file : projecthermes = json.load(file)
    except FileNotFoundError:
        inithermesproject(cwd)
        sys.exit(0)
    except json.decoder.JSONDecodeError:
        print(
            colorama.Fore.RED + "❌ Invalid hermes JSON file!" + colorama.Style.RESET_ALL
        )
        sys.exit(0)

    if '-r' in sysargs:
        try:
            projecthermes['inputs'] = [sysargs[sysargs.index('-r') + 1]]
        except IndexError:
            print(
                colorama.Fore.RED + colorama.Style.BRIGHT + "🤷 No input files to run!" +
                colorama.Style.RESET_ALL
            )
            sys.exit(0)

    if '-run' in sysargs:
        try:
            projecthermes['inputs'] = [sysargs[sysargs.index('-run') + 1]]
        except IndexError:
            print(
                colorama.Fore.RED + colorama.Style.BRIGHT + "🤷 No input files to run!" +
                colorama.Style.RESET_ALL
            )
            sys.exit(0)

    if not projecthermes['inputs']:
        print(
            colorama.Fore.RED + colorama.Style.BRIGHT + "🤷 No input files provided!" +
            colorama.Style.RESET_ALL
        )
        sys.exit(0)




    #dealing with wildcards, spicy paths etc.
    for each in projecthermes.keys():
        if type(template[each]) == list:
            processed = []
            for x in projecthermes[each]:
                processed += processpathsetting(cwd, x)
            projecthermes[each] = processed


    #defaults here
    if (not 'output' in projecthermes.keys()) or (not projecthermes['output']):
        defaultname = getfilename(projecthermes['inputs'][0]).split('.')[0]
        projecthermes['output'] = f"{cwd}/.hermes/debug/{defaultname}_output"

    if (not 'flags' in projecthermes.keys()) or (not projecthermes['flags']):
        projecthermes['flags'] = []

    if (not 'run' in projecthermes.keys()) or (not projecthermes['run']):
        projecthermes['run'] = False

    if (not 'includes' in projecthermes.keys()) or (not projecthermes['includes']):
        projecthermes['includes'] = []

    if (not 'compiler' in projecthermes.keys()) or (not projecthermes['compiler']):
        projecthermes['compiler'] = 'g++'

    #adding globals
    combineglobals()

    if superverbose : print(json.dumps(projecthermes, indent=4))

    #reading tracks
    tracks = dict()
    try:
        with open(f'{cwd}/.hermes/tracker.json', 'r') as file:
            tracks = json.load(file)
    except:
        print(
            colorama.Fore.YELLOW + '🔍Error reading tracker.json, using empty tracks...' +
            colorama.Style.RESET_ALL
        )
        fixfolderstructure(cwd)

    changedfiles = list(filter(
        lambda x : haschanged(x, tracks),
        projecthermes['inputs']
    ))

    if ('-redo' in sysargs) or ('-force' in sysargs): changedfiles = projecthermes['inputs']

    allok = True
    for each in changedfiles:
        if verbose:
            print(
                colorama.Fore.LIGHTGREEN_EX +
                f"📄 Changes detected in `{each}`..." + colorama.Style.RESET_ALL
            )

        if makeobj(each, projecthermes):
            allok = False
        else:
            if verbose:
                print(
                    colorama.Fore.GREEN +
                    f"🪶  Updating objs for `{each}`..." + colorama.Style.RESET_ALL
                )
            updatetracks(each, tracks)
        
        if superverbose : print(json.dumps(tracks, indent = 4))



    linkercommand = f"{projecthermes['compiler']} -o {projecthermes['output']} "
    for each in projecthermes['inputs']:
        linkercommand += f" {cwd}/.hermes/objs/{getfilename(each).split('.')[0]}.o "
    linkercommand += ' '.join(projecthermes['flags'])
    linkercommand += f' {opt} '

    if superverbose:
        print("Linker command:")
        print(linkercommand)

    if allok:
        if os.system(linkercommand):
            allok = False
            print(
                colorama.Fore.RED + colorama.Style.DIM +
                "🔗 This was a linker error, most likely caused by missing object (.a, .o), .dll, .lib or .cxx files.\nEnsure all headers have their corresponding declarations, and all library flags are added."+
                colorama.Style.RESET_ALL
            )


    end = time.time()
    if allok:
        try:
            with open(f'{cwd}/.hermes/tracker.json', 'w') as file:
                file.write(json.dumps(tracks, indent = 4))
        except:
            fixfolderstructure(cwd)
            with open(f'{cwd}/.hermes/tracker.json', 'w') as file:
                file.write(json.dumps(tracks, indent = 4))
        print(
            colorama.Style.BRIGHT + colorama.Fore.GREEN +
            f"👍 Build complete successfully! Compilation completed in {str(end - start)[:4]}s!" +
            colorama.Style.RESET_ALL
        )
    else:
        print(
            colorama.Style.BRIGHT + colorama.Fore.RED +
            f"🤮 Build failed! Compilation completed in {str(end - start)[:4]}s!" +
            colorama.Style.RESET_ALL
        )
        sys.exit(1)


    if projecthermes['run']:
        start = time.time()
        if ('-r' in sysargs) or ('-run' in sysargs): 
            print(
                colorama.Style.BRIGHT + colorama.Fore.YELLOW +
                f"🏃 Running `{getfilename(projecthermes['inputs'][0])}`..." +
                colorama.Style.RESET_ALL
            )
        else:
            print(
                colorama.Style.BRIGHT + colorama.Fore.YELLOW +
                f"🏃 Running app..." +
                colorama.Style.RESET_ALL
            )
        print()

        try:
            code = os.system(projecthermes['output'])
        except KeyboardInterrupt:
            pass

        end = time.time()
        print()
        print(
            colorama.Style.DIM + colorama.Fore.YELLOW +
            f"🏁 Execution finished with {(colorama.Fore.RED if code else colorama.Fore.GREEN) + colorama.Style.NORMAL + ('exit code ' + str(code)) + colorama.Style.DIM + colorama.Fore.YELLOW} in {str(end - start)[:4]}s!" +
            colorama.Style.RESET_ALL
        )
    