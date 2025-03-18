import nbformat as nbf
import papermill
from Chapter import Chapter

def create_cell_from_dict(celldata: dict) -> nbf.NotebookNode:
    if celldata['celltype'] == 'code':
        newcell = nbf.v4.new_code_cell(source = celldata['source'])
    elif celldata['celltype'] == 'markdown':
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
