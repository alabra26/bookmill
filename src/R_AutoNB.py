import nbformat as nbf
import papermill as pm
import yaml
from copy import deepcopy
import re

# TODO : template MUST be an ordered object, but also needs easy access to the parameters_cell Unit. Likely requires a custom class

# define globals, which would be class variables in an OOP setting
# NB : tags are not used for this cell because we make a deep copy
scope_check_cell_R = {
                'cell type': 'code',
                'source': 'ls()',
                'tags': ['scope', 'trim']
            }
replace_tag = 'replace'
replace_vars = {}

# NB : you will need to define your own main() function that ingests parameters from a CLI i.e. argparse.ArgumentParser
# and then calls NTBK()
def ntbk(path_to_template: str, output_path: str, parameters: dict) -> None:
    # load template
    # TODO : we need an easy way to access the parameters Unit from the template
    # The current coded solution requires the template to be a dictionary of Units where each Unit has a key name (and we rely on the 'parameters_cell' name)
    template = load_template(path_to_template)
    
    nb = new_R_nb()
    # TODO : we shouldn't have to re-pass the parameters every time we do a pm.execute_notebook()
    # since after the first time, the parameter cell will be created and persisted
    nb = add_parameters_cell(nb, template, parameters)
    
    for name, unit in template.items():
        nb = append_unit(nb, unit)
    
    for index, cell in enumerate(nb['cells']):
        if replace_tag in cell['metadata']['tags']:
            nb['cells'][i] = cell_string_replacement(cell, replace_vars)

    # save notebook
    with open(output_path) as f:
        nbf.write(nb, f)

    print("Notebook generated B)")

def cell_string_replacement(cell: dict, replace_vars: dict) -> dict:
    newstr = cell['source']
    for replace_str, replace_value in replace_vars.items():
        newstr = newstr.replace(replace_str, replace_value)
    cell['source'] = newstr
    return cell

def add_parameters_cell(nb: nbf.NotebookNode, template: dict, params: dict) -> nbf.NotebookNode:
    # TODO : confirm New Cells has only one cell
    # TODO : confirm that parameters_cell has tag 'parameters'
    parameters_cell = template['parameters_cell']['New Cells'][0]
    del template['parameters_cell']
    if not 'parameters' in parameters_cell['tags']:
        raise ValueError(f"Parameter injection cell (name 'parameters_cell') must have tag 'parameters'. Current tags are {parameters_cell['tags']}.")
    nb = add_cell(nb, parameters_cell)
    nb = pm.execute_notebook(nb, 'tmp.ipynb', parameters=params)
    for ind, cell in enumerate(nb['cells']):
        if 'parameters' in cell['tags']:
            nb['cells'].pop(ind)
            return nb
    raise KeyError(f"Could not find any cell tagged 'parameters' in notebook cells: {nb.cells}")

def new_R_nb() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    nb['metadata'] = {
        "kernelspec": {
            "disply_name": "R",
            "language": "R",
            "name": "ir"
        },
        "language_info": {
            "codemirror_mode": "r",
            "file_extension": ".r",
            "mimetype": "text/x-r-source",
            "name": "R",
            "pygments_lexer": "r",
            "version": "4.4.2",
        },
    }
    return nb

def load_template(yaml_path: str) -> dict:
    with open(yaml_path) as stream:
        try:
            chapters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print("Error loading in Chapters, please check the Chapters YAML file.")
            raise
    return chapters

def get_namespace_vars(nb: nbf.NotebookNode) -> nbf.NotebookNode:
    namespace_nb = deepcopy(nb)
    namespace_nb = add_cell(namespace_nb, scope_check_cell_R)
    namespace_nb = pm.execute_notebook(namespace_nb, 'tmp.ipynb')
    scope_vars = namespace_nb['cells'][-1]['outputs'][0]['data']['text/plain'].replace(
            '[1] ', ''
            ).replace(
                "'",""
            ).replace(
                '"',''
            ).split(' ')
    return scope_vars
    


def append_unit(nb: nbf.NotebookNode, Unit: dict) -> nbf.NotebookNode:
    # get namespace
    curr_namespace = get_namespace_vars(nb)
    # compare namespace to unit.requires
    for varname in Unit['Requires']:
        if not varname in curr_namespace:
            # do not have sufficient context to add unit, we return
            return nb
    # for cell in unit.NewCells: add cell
    for cell in Unit['New Cells']:
        nb = add_cell(nb, cell)
    # run new cells (papermill w/ parameter injections)
    nb = pm.execute_notebook(nb, 'tmp.ipynb')
    # check for unit.Defines: add fail cells ? add success cells
    new_namespace = get_namespace_vars(nb)
    for varname in Unit['Defines']:
        if varname not in new_namespace:
            # add fail cells
            for cell in Unit['Failure Cells']:
                nb = add_cell(nb, cell)
            return nb
    for cell in Unit['Success Cells']:
        nb = add_cell(nb, cell)
    return nb


def create_cell_from_dict(celldata: dict) -> nbf.NotebookNode:
    if celldata['cell type'] == 'code':
        newcell = nbf.v4.new_code_cell(source = celldata['source'])
    elif celldata['cell type'] == 'markdown':
        newcell = nbf.v4.new_markdown_cell(source = celldata['source'])
    newcell['metadata']['tags'] = celldata['tags']

    return newcell

def add_cell(nb: nbf.NotebookNode, celldata: dict) -> nbf.NotebookNode:
    newcell = create_cell_from_dict(celldata)
    nb['cells'].append(newcell)
    # TODO : add execution and variable recovery
    nb = pm.execute_notebook(nb, 'tmp.ipynb')
    if celldata['Computes']:
        computed_string = re.search(pattern, nb['cells'][-1]['outputs'][0]['data']['text/plain'])
        if not computed_string:
            print(f"Could not rescue variable {celldata['Computes']} from cell output: {nb['cells'][-1]['outputs'][0]['data']['text/plain']}\nConfirm that regex is working correctly.")
        replace_vars.update({celldata['Computes']: computed_string})
    return nb
    