
import json, hashlib, sys, os, glob, time

from rich import print as rprint
from rich.panel import Panel


from dataclasses import dataclass


template = {
    "name" : "",
    "compiler" : "clang",
    "inputs" : {
        "exe" : [],
        "lib" : []
    },
    "libincdirs" : [],
    "libs" : [],
    "libdirs" : [],
    "target" : {
        "type" : "exe",
        "run" : True,
        "exeout" : ".hermes/output.exe",
        "libout" : ".hermes/libout",
        "incdirs" : [],
    },
    "submodules" : {
        'assrcs' : [],
        'aslibs' : [],
    },
    'copts' : [],
    'lopts' : [],
}

platform = 'mac'
if 'win32' in sys.platform : platform = 'win'
elif 'linux' in sys.platform : platform = 'lin'


@dataclass
class BuildModule:
    root : str
    config : dict[str, list[str] | str | bool]
    debug : bool
    verbose : bool
    force : bool = False


class LinkerError(Exception):
    def __init__(self, message, cmd, debug : bool = False):
        super().__init__(message)
        self.debug = debug
        self.cmd = cmd

class CompileError(Exception):
    def __init__(self, message, cmd, debug : bool = False):
        super().__init__(message)
        self.debug = debug
        self.cmd = cmd

class StaticLibCompileError(Exception):
    def __init__(self, message, cmd, debug : bool = False):
        super().__init__(message)
        self.debug = debug
        self.cmd = cmd



def trackspath(bm : BuildModule):
    return os.path.join(bm.root, '.hermes', 'tracks.json')
def mappingspath(bm : BuildModule):
    return os.path.join(bm.root, '.hermes', 'mappings.json')
def objectspath(bm : BuildModule):
    return os.path.join(bm.root, '.hermes', 'objects')

def get_hex_digest(data : str) -> str:
    return hashlib.sha1(
        data.strip().encode()
    ).hexdigest() 


def compile_unit(bm : BuildModule, unit : str, target : str):
    cmd = (
        bm.config['compiler'] + ' ' + 
        ' '.join([f'-I"{os.path.abspath(x)}"' for x in bm.config['libincdirs']]) + 
        ' ' +
        f'-c "{unit}" ' +
        f'-o "{target}" ' +
        ' '.join([f'-{x}' for x in bm.config['copts']])
    )
    if bm.verbose : rprint(cmd)
    res = os.system(cmd)
    if res:
        raise CompileError(f"Compile error in unit `{unit}`", cmd, bm.debug)
        

def link(bm : BuildModule, objects : list[str]):
    cmd = (
        bm.config['compiler'] + ' ' +
        '-o "' + bm.config['target']['exeout'] + '" ' +
        ' '.join([f'"{os.path.join(objectspath(bm), x)}.o"' for x in objects]) + ' ' +
        ' '.join([f'-l{x}' for x in bm.config['libs']]) + ' ' +
        ' '.join([f'-L"{x}"' for x in bm.config['libdirs']]) + ' ' +
        ' '.join([f'-{x}' for x in bm.config['lopts']])
    )
    if bm.verbose: rprint(cmd)
    res = os.system(cmd)
    if res:
        raise LinkerError(f"Linker error!", cmd, bm.debug)



def llvm_lib_cmd(bm : BuildModule, objects : list[str]):
    cmd = (
        f"llvm-lib /OUT:{bm.config['target']['libout']}.lib " +
        ' '.join([f'"{os.path.join(objectspath(bm), x)}.o"' for x in objects]) + " " +
        ' '.join([f'-l{x}' for x in bm.config['libs']]) + ' ' +
        ' '.join([f'-L"{x}"' for x in bm.config['libdirs']])
    )
    if bm.verbose:
        rprint(cmd)
    res = os.system(cmd)
    if res:
        raise StaticLibCompileError(f"Static Lib Compile failed!", cmd, bm.debug)



def extract_includes(code : str) -> list[str]:
    includes = []
    for each in code.splitlines():
        if each.strip().startswith('#include'):
            header = each.strip().split(' ')[-1]
            if header[0] == '"':
                includes.append(header[1:-1])
    return includes





def build_module(bm : BuildModule):
    if bm.debug:
        rprint(f"[dim]Building `{bm.config['name']}`...[/]")
        
    
    for submod in bm.config['submodules']['assrcs']:
        hp = (os.path.join(submod, 'hermes.json'))
        if not os.path.exists(hp):
            rprint(
                f'[yellow]Folder `{hp}` is not a module (missing hermes.json), skipping...'
            )
            continue
        
        with open(hp, 'r') as file:
            subbm = BuildModule(
                root=submod,
                config=json.loads(file.read()),
                debug = bm.debug, verbose=bm.verbose,
                force=bm.force
            )
        
        bm.config['inputs'][bm.config['target']['type']] += subbm.config['inputs']['lib']
        bm.config['libincdirs'] += subbm.config['libincdirs']
        bm.config['libs'] += subbm.config['libs']
        bm.config['libdirs'] += subbm.config['libdirs']
    
    for submod in bm.config['submodules']['aslibs']:
        hp = (os.path.join(submod, 'hermes.json'))
        if not os.path.exists(hp):
            rprint(
                f'[yellow]Folder `{hp}` is not a module (missing hermes.json), skipping...'
            )
            continue
        
        with open(hp, 'r') as file:
            subbm = BuildModule(
                root=submod,
                config=json.loads(file.read()),
                debug=bm.debug, verbose=bm.verbose,
                force=bm.force
            )
        
        subbm.config['target']['type'] = 'lib'
        build_module(subbm)
        
        bm.config['libincdirs'] += subbm.config['target']['incdirs']
        lo = subbm.config['target']['libout']
        libdir = os.path.dirname(os.path.abspath(lo))
        lib = os.path.basename(os.path.abspath(lo))
        
        bm.config['libs'].append(lib)
        bm.config['libdirs'].append(libdir)
        
        
        
    
    
    tp = trackspath(bm)
    op = objectspath(bm)
    mp = mappingspath(bm)
    
    os.makedirs(os.path.dirname(tp), exist_ok=True)
    os.makedirs(op, exist_ok=True)
    
    file_mapping : dict[str, str] = dict()
    if os.path.exists(mp):
        with open(mp, 'r') as file:
            file_mapping = json.loads(file.read())
    
    tracks = dict()
    if os.path.exists(tp):
        with open(tp, 'r') as file:
            tracks = json.loads(file.read())
    
    
    all_files = []
    for each in bm.config['inputs'][bm.config['target']['type']]:
        sub = glob.glob(each, recursive=True, root_dir=bm.root)
        sub = list(filter(lambda x: os.path.isfile(x), sub))
        all_files += sub
    
    all_files = [os.path.abspath(x) for x in all_files]
    all_headers = []
    if bm.verbose:
        rprint('allfiles')
        rprint(all_files)
    
    file_hashes = dict()
    for each in all_files:
        with open(each, 'r') as data:
            unit_data = data.read()
            file_hashes[each] = get_hex_digest(unit_data)
            
            headers = extract_includes(unit_data)
            headers = [os.path.abspath(os.path.join(os.path.dirname(each), x)) for x in headers]
            
            if bm.verbose:
                rprint('headers')
                rprint(headers)
            
            all_headers += headers
            
            for h in headers:
                with open(h, 'r') as hf:
                    file_hashes[h] = get_hex_digest(hf.read())
            
    if bm.verbose:
        rprint(file_hashes)
        rprint(tracks)
    
    changed_files : list[str] = [
        x for x in all_files + all_headers
        if ( tracks[x] != file_hashes[x] if x in tracks else True )
    ]
    
    changed_files : set[str] = set(changed_files)
    
    for each in all_files:
        with open(each, 'r') as file:
            headers = extract_includes(file.read())
            headers = [os.path.abspath(os.path.join(os.path.dirname(each), x)) for x in headers]
            
            if bm.verbose:
                rprint(f'checking header changes for `{each}`')
                rprint(headers)
            
            headers = [(x in changed_files) for x in headers]
            if bm.verbose: rprint(headers)
                
            if any(headers):
                if bm.verbose: rprint(f"Headers changed in `{each}`")
                changed_files.add(each)
    
    exts = ['c', 'cpp']
    
    changed_files = list(filter(
        lambda x: os.path.basename(x).split('.')[-1].lower() in exts,
        changed_files
    ))
    
    if bm.force:
        changed_files = list(filter(
            lambda x: os.path.basename(x).split('.')[-1].lower() in exts,
            all_files
        ))
    
    if bm.verbose:
        rprint('changed files:')
        rprint(changed_files)
    
    for eachfile in changed_files:
        if eachfile not in file_mapping:
            file_mapping[eachfile] = get_hex_digest(eachfile)
    
    
    for each in changed_files:
        compile_unit(bm, each, os.path.join(op, f'{file_mapping[each]}.o'))
    
    if bm.config['target']['type'] == 'exe':
        link(bm, [file_mapping[x] for x in file_mapping])
    elif bm.config['target']['type'] == 'lib':
        llvm_lib_cmd(bm, [file_mapping[x] for x in file_mapping])
    
    tracks = file_hashes
    
    with open(tp, 'w') as file:
        file.write(json.dumps(tracks, indent=4))
    
    with open(mp, 'w') as file:
        file.write(json.dumps(file_mapping, indent=4))
    
    if bm.debug:
        rprint(f"[green bold]Built `{bm.config['name']}`[/] :white_check_mark:")
    
        
