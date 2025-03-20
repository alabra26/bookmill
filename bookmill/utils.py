import nbformat as nbf
import papermill
from Chapter import Chapter

def create_cell_from_dict(celldata: dict) -> nbf.NotebookNode:
    if celldata['cell_type'] == 'code':
        newcell = nbf.v4.new_code_cell(source = celldata['source'])
    elif celldata['cell_type'] == 'markdown':
        newcell = nbf.v4.new_markdown_cell(source = celldata['source'])
    newcell['tags'] = celldata['tags']

    return newcell

def add_cell_to_notebook(nb: nbf.NotebookNode, celldata: dict) -> nbf.NotebookNode:
    newcell = create_cell_from_dict(celldata)
    nb['cells'].append(newcell)
    return nb

def add_chapter_to_notebook(nb: nbf.NotebookNode, chaptercells: list[dict]) -> nbf.NotebookNode:
    for celldata in chaptercells:
        nb = add_cell_to_notebook(nb, celldata)
    nb = papermill.execute_notebook(nb)
    return nb

def get_nb_scope(nb: nbf.NotebookNode):
    # define variable scope cell
    # TODO : move this to a config file
    # TODO : make this a Chapter object
    scope_cell = {
        'cell_type': 'code',
        'source': 'locals()',
        'tags': ['scope', 'trim']
    }
    nb = add_cell_to_notebook(nb, scope_cell)
    # TODO : determine the json structure to access the outputs
    scope = nb['cells'][-1]['outputs']['data']['text/plain'].split()
    return scope
    

def get_scope_additions(nb: nbf.NotebookNode, chaptercells: list[dict]) -> list[str]:
    initial_scope = get_nb_scope(nb)
    nb = add_chapter_to_notebook(nb, chaptercells)
    final_scope = get_nb_scope(nb)
    scopediff = set(final_scope) - set(initial_scope)
    # return
    return scopediff
