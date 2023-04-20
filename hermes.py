import json, os, sys
import colorama
import time

start = time.time()

verbose = ('-v' in sys.argv)

finalcommand = []

cwd = os.getcwd()

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
    sys.exit(0)

#-----------------------------------------------------------------------------------------
# dealing with default config values
# - default compiler is g++
# - default output file is *firstinputfilename*_output
run = config.pop('run', False)

if 'flags' not in config.keys(): config['flags'] = []
if 'includes' not in config.keys(): config['includes'] = []

if not(config['inputs']):
    print("No input files given!")
    sys.exit(1)


if not(config['includes']):
    pass

if not(config['compiler']):
    config['compiler'] = 'g++'

if not(config['output']):
    config['output'] = f"{config['inputs'][0].split('.')[1][1:]}_output"
config['output'] = f"{cwd}\\debug\\{config['output']}"

pinp = colorama.Fore.LIGHTCYAN_EX +     f"Input Files       : {' '.join(config['inputs'])}" + colorama.Style.RESET_ALL

config['inputs'] = list(map(

    lambda x: f"{cwd}\\{x[2:]}" if (x[:2] == './' and x[-1] != '*') else x,

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
                    config['inputs'].append(f"{folder}/{file}")
                else:
                    config['inputs'].append(f"{folder}/{file}/*")
                    breakable = True
            del config['inputs'][i]


try:
    os.mkdir(f"{cwd}\\debug")
    print(colorama.Fore.GREEN + "Created `debug` folder" + colorama.Style.RESET_ALL)
except FileExistsError as e:
    pass

#-----------------------------------------------------------------------------------------

argflags = {
    'includes' : '-I',
    'inputs'   : '',
    'output'   : '-o',
    'flags'    : '',
}


for each in config:
    if verbose : print(each, config[each])
    if each == 'compiler':
        finalcommand.append(config[each])
        continue
    
    if config[each]:
        finalcommand.append(argflags[each])
        if type(config[each]) == list:
            for val in config[each]:
                if each != 'flags' : finalcommand.append(f"\"{val}\"")
                else : finalcommand.append(f"{val}")
        else : finalcommand.append(f"\"{config[each]}\"")


finalcommand = list(filter(lambda x:x, finalcommand))


if verbose:
    print()
    print(finalcommand)

finalcommand = " ".join(finalcommand)

if '-no' not in sys.argv:
    print(colorama.Fore.LIGHTBLUE_EX +     f"Compiler          : {config['compiler']}" + colorama.Style.RESET_ALL)
    print(pinp)
    print(colorama.Fore.LIGHTYELLOW_EX +   f"Include Files     : {' '.join(config['includes'])}" + colorama.Style.RESET_ALL)
    print(colorama.Fore.LIGHTMAGENTA_EX +  f"Output file       : {config['output']}" + colorama.Style.RESET_ALL)
    print(colorama.Fore.LIGHTRED_EX +      f"Auto launch       : {run}" + colorama.Style.RESET_ALL)
    print(colorama.Fore.LIGHTCYAN_EX +     f"Additional flags  : {' '.join(config['flags'])}" + colorama.Style.RESET_ALL)
    print()

if os.system(finalcommand) == 0:

    end = time.time()

    print(colorama.Fore.GREEN + colorama.Style.BRIGHT + f"Compilation successful! Build completed in {str(end - start)[:4]}s" + colorama.Style.RESET_ALL)

    if run:
        print()
        start = time.time()
        code = os.system(f"{config['output']}.exe")
        end = time.time()

        code = (colorama.Fore.RED if code else colorama.Fore.GREEN) + f"code {code}" + colorama.Style.RESET_ALL

        print(f"\nExecution finished with exit {code} in {str(end - start)[:4]}s")
        os.system("pause")

else:
    end = time.time()
    print(colorama.Fore.RED + f"Compilation Failed! Build failed in {str(end - start)[:4]}s" + colorama.Style.RESET_ALL)
