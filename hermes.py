
from typing import Annotated

import typer, os, rich, json, shutil, traceback, time

from lib import *
from rich.prompt import Prompt, Confirm 
from rich.panel import Panel
from rich.console import Console
from rich.traceback import Traceback


app = typer.Typer(help='A simple no nonsense build system for C/C++')

hermes_file_path = os.path.join(os.path.curdir, 'hermes.json')
hermes_dir_path  = os.path.join(os.path.curdir, '.hermes')



@app.command()
def init():
    """Initialises a hermes build module in current folder"""
    if os.path.exists(hermes_file_path):
        res = Confirm.ask(
            "Hermes config file already exists; reset?",
            default=False
        )
        if res:
            with open(hermes_file_path, 'w') as file:
                file.write(json.dumps(template, indent=4))
    else:
        with open(hermes_file_path, 'w') as file:
            file.write(json.dumps(template, indent=4))
    
    if os.path.exists(hermes_dir_path):
        res = Confirm.ask("Hermes data already exists; reset?", default=False)
        if res:
            try : shutil.rmtree(hermes_dir_path)
            except OSError as e:
                Panel.fit(f'{e.filename}:\n{e.strerror}')
                typer.Exit(-1)
    else:
        os.mkdir(hermes_dir_path)
        
    gif = os.path.join(os.path.curdir, '.gitignore')
    if os.path.exists(gif):
        with open(gif, 'a') as file:
            file.write('\n\n')
            file.write('#----- hermes -----\n')
            file.write('.hermes/\n')
            file.write('#------------------\n')
            file.write('\n\n')
    


@app.command()
def build(
        debug : Annotated[bool, typer.Option(
            help='Outputs debug info'
        )] = False,
        verbose : Annotated[bool, typer.Option(
            help='Outputs debug info + commands and everything'
        )] = False,
        force : Annotated[bool, typer.Option(
            help='Forces recompilation of all files, ignoring tracks'
        )] = False,
    ):
    """Builds the current hermes module"""
    if not os.path.exists(hermes_file_path):
        raise FileNotFoundError(
            "Not a hermes module! (Use `hermes init` to make one here)"
        )
    with open(hermes_file_path, 'r') as file:
        bm = BuildModule(
            root=os.path.abspath(os.path.curdir),
            config=json.loads(file.read()),
            debug=debug or verbose, verbose=verbose,
            force=force
        )
    
    start = time.time()
    build_module(bm)
    end = time.time()
    rich.print(f"[dim]Finished building in[/] [yellow]{end - start:.2f}s[/]")
    
    
    if (bm.config['target']['type'] == 'exe') and bm.config['target']['run']:
        print()
        start = time.time()
        try:
            code = os.system(os.path.abspath(bm.config['target']['exeout']))
        except KeyboardInterrupt:
            pass
        end = time.time()

        clr = 'red' if code else 'green'
        rprint(
            f"\n[dim]Finished execution with[/] [{clr}]exit code {code}[/] "
            f"[dim]in[/] [yellow]{end-start:.2f}s[/]"
        )
    

@app.command()
def run():
    """Runs the module executable, if it exists"""
    if not os.path.exists(hermes_file_path):
        raise FileNotFoundError(
            "Not a hermes module! (Use `hermes init` to make one here)"
        )
    with open(hermes_file_path, 'r') as file:
        bm = BuildModule(
            root=os.path.abspath(os.path.curdir),
            config=json.loads(file.read()),
            debug=False, verbose=False,
            force=False
        )
    
    eo = bm.config['target']['exeout']
    eo = os.path.abspath(eo)
    if not os.path.exists(eo):
        rprint(
            "[red]Module doesn't have an executable; "
            "set target type to `exe` and run `hermes build`[/]"
        )
        return
    
    start = time.time()
    try:
        code = os.system(eo)
    except KeyboardInterrupt:
        pass
    end = time.time()

    clr = 'red' if code else 'green'
    rprint(
        f"\n[dim]Finished execution with[/] [{clr}]exit code {code}[/] "
        f"[dim]in[/] [yellow]{end-start:.2f}s[/]"
    )



console = Console()
def main():
    try: app()
    except Exception as e:
        exc_type, exc_value, traceback = sys.exc_info()
        
        while traceback.tb_next:
            traceback = traceback.tb_next
        
        sl = False
        if hasattr(e, 'bm'):
            sl = e.bm.verbose
        
        rich_tb = Traceback.from_exception(
            exc_type, exc_value, traceback,
            show_locals= sl ,
            # theme="monokai",
            theme="inkpot",
            extra_lines=3
        )
        
        if hasattr(e, 'debug'):
            if e.debug:
                console.print(rich_tb)
        else:
            console.print(rich_tb)
        
        typer.Exit(-1)