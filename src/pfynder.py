#!/usr/bin/env python
# coding: utf-8


import os,sys

from subprocess import *
from subprocess import Popen
import platform

# In/Out-puts
# package: Subpackage/Module/Submodule/Class/Method/Function
# package.subpackage: Module/Submodule/Class/Method/Function
# package.subpackage.module: Submodule/Class/Method/Function
# package. ... Module: Submodule/Class/Method/Function
# package. ... Class: Method/Function
# * : Subpackage/Module/Submodule/Class/Method/Function
# * : Module: Submodule/Class/Method/Function
# * : Class: Method/Function

def verbprint(verb):
    def meth(text):
        if verb:
            print(text)            
        return None    
    return meth


def check_path(path):
    # filter the path to ensure it will contain what you want
    return (path != "") & \
           ((".zip" not in path) & \
            (".ipython" not in path) & \
            ("extensions" not in path)) & \
            ('packages' in path)


def get_directory(path, pack_name, pyvers, verbose=False):
    
    # 
    vprint = verbprint(verbose)
    
    p1 = Popen(["find", path, "-type", "d", "-name", pack_name], stdout=PIPE)
    p2 = Popen(["grep", f"python{pyvers}"], stdin=p1.stdout, stdout=PIPE)
    p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.

    output = p2.communicate()[0]

    dirs_to_search = [s for s in output.decode("utf-8").split('\n') if s != '']    

    return dirs_to_search


def find_mod(directory, pack_name, mod_name, verbose=False):
    """
    """
    
    vprint = verbprint(verbose)
    
    p1 = Popen(["find", directory, "-type", "d", "-name", mod_name], stdout=PIPE)
    output = p1.communicate()[0]
    
    locations = [s.split("/"+pack_name+"/")[1] for s in output.decode("utf-8").split('\n') if s != '']
    
    # Print out the results    
    if len(locations) != 0:
        
        print(f"{pack_name}")
        for l in locations:
            print(f"\t{l}")
    
    return None


def find_fnc(directory, pack_name, fnc_name, verbose=False):
    """
    """
    
    vprint = verbprint(verbose)
    
    p1 = Popen(["find", directory, "-type", "f", "-name", "*.py"], stdout=PIPE)
    p2 = Popen(["xargs", "grep", fnc_name], stdin=p1.stdout, stdout=PIPE)
    p3 = Popen(["grep", "def "], stdin=p2.stdout, stdout=PIPE)
    p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    p2.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    
    output = p3.communicate()[0]
    vprint(output)
    
    locations = [s.split("/"+pack_name+"/")[1] for s in output.decode("utf-8").split('\n') if s != '']
    vprint(locations)
    
    
    
    dc = {}
    for l in locations:

        # Get the module (path) and func_name name
        # NOTE: the parsing is tailored to the outputs of the `find` and `grep`        
        if '/' in l:
            module, func_name = check_meth(directory, l)
            
        else:

            module = l.split('.py:')[0]
            func_name = l.split('def ')[1].split("(")[0]

        if module in dc.keys():
            dc[module].append(func_name)
        else:
            dc[module]= [func_name]
    
    # Print out the results
    if len(dc.keys()) != 0:
        print(f"{pack_name}")
        for k,v in dc.items():
            print(f"\t{k}:")
            for vv in v:
                print(f"\t\t{vv}")
    
    return None


def pfynd_mod(package_to_check, mod_name):
    
    pfynder(package_to_check, mod_name, True)
    
    return None


def pfynd_fnc(package_to_check, fnc_name):
    
    pfynder(package_to_check, fnc_name, False)
    
    return None


def get_numb(numb, numbs):
    
    for n in numbs[::-1]:
        if numb < n: return n
    
    return numbs[-1]


def check_meth(dir_to_search, modulename):
    
    
    # NOTE: this is an _ugly_ solution.
    # This function compares the line numbers to 
    # identify when a method belongs to a class
    #
    # TODO: get methods in the module which match criterion
    
    
    # Get the module name as before
    module = modulename.split('.py:')[0]
    func = modulename.split('def ')[1].split("(")[0]

    location = f"{dir_to_search}/{module}"+".py"

    # Check for all class names and their line numbers
    p1 = Popen(["grep", "-n", "^class", location], stdout=PIPE)
    output = p1.communicate()[0]                

    classdic = [s.split(':class ') for s in output.decode("utf-8").split('\n') if s != '']
    classdic = {int(pp[0]):pp[-1].split("(")[0] for pp in classdic}
    classkeys = sorted(classdic.keys())

    p1 = Popen(["grep", "-n", "^    def", location], stdout=PIPE)
    output = p1.communicate()[0]                

    methdic = [s.split(':    def ') for s in output.decode("utf-8").split('\n') if func in s]
    methdic = {int(pp[0]):pp[-1].split("(")[0] for pp in methdic}
    methkeys = sorted(methdic.keys())
    #print(methdic)

    module += "."+classdic[[get_numb(kk, classkeys) for kk in methkeys ][0]]
    module = module.replace('/','.')
    
    return module, func


def pfynd(package_to_check, item_to_find, ismodule=False, verbose=False):
    """
    
    Examples:
    
    Module:
    >>> pfynder("sklearn", "svm", True)
    >>>
    
    Function
    >>> pfynder("sklearn", "covariance", False)
    >>>
    
    """
    
    # 0. inputs: module name and function name to search for
    # 1. find local of current python; effectively want `/usr/local/lib/pythonX.X/` where "pythonX.X" is the current version of the notebook
    # 2. find the correct dir with the package's name, _ie_ "sklearn"
    # 3. search through all `.py`-scripts using grep to find the function name
    #     - **Note** it could be in multiple modules, , filter to get those with "def"
    # 4. output the results
    
    vprint = verbprint(verbose)
    
    # Get the version of the currently-running python kernel
    pyvers = ".".join(platform.python_version_tuple()[:2])
    
    # 
    paths = [p for p in sys.path if check_path(p)]
    
    vprint(paths)
    
    not_found = []
    
    for path in paths:
        
        dirs_to_search = get_directory(path, package_to_check, pyvers)
        
        if dirs_to_search == []:
            not_found.append(f"\n\t\'{package_to_check}\' not found in {path}\n")
            continue
        vprint(dirs_to_search)
        
        dir_to_search = dirs_to_search[0]        
        vprint(dir_to_search)
        
        if ismodule:
            find_mod(dir_to_search, package_to_check, item_to_find)
        else:
            find_fnc(dir_to_search, package_to_check, item_to_find)
    
    show_fail = True
    if show_fail:
        vprint(not_found)
        
    return None
