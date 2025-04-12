import nbformat as nbf
import papermill as pm
import yaml
from typing import Dict, List
#from bookmill.src.Chapter import Chapter

# TODO : figure out how we will run papermill with parameter injection, as this is needed (even for scope checking)

class NotebookGenerator():
    def __init__(self, nb_path: str, chapters_path: str, kernel: str = 'R', **kwargs) -> None:
        # TODO : kernel should be bound to/specified by the chapter metadata
        self._params_setup(**kwargs)
        self.nb_path = nb_path
        self.kernel = kernel
        self.chapters = load_chapters(chapters_path)
        self.current_scope = []
        
    def _params_setup(self, **kwargs) -> None:
        self.params = {}
        self.params.update(kwargs)
        self.rpl_vals = {}
        
    def build_notebook(self):
        # initialize empty
        self.nb = nbf.v4.new_notebook()
        # set kernel
        #### TODO
        if self.kernel == 'R':
            self.nb['metadata'] = {
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
        else:
            raise NotImplementedError(f"Not compatible with passed kernel type: {self.kernel}")
        # add chapters
        for chapterName in self.chapters.keys():
            self._append_chapter(self.chapters[chapterName])
            
    def write_notebook(self):
        # Check if nb exists
        if not self.nb:
            raise ValueError("Notebook does note exist. Must generate notebook before writing.")
        # write notebook
        with open(self.nb_path) as f:
            nbf.write(self.nb, f)
            
    def _append_chapter(self, chapter: dict) -> None:
        # ensure all Requires vars are in current_scope
        for var in chapter['Requires']:
            if not var in self.current_scope:
                print(f"Could not add chapter, missing requirement: {var}")
                return
        # get scope additions
        self._get_scope_additions(chapter['New Cells'])
        # check variables added to scope
        success = True
        for var in chapter['Defines']:
            if not var in self.current_scope:
                # if not all variables defined successfully, add failure condition cells
                success = False
                self.nb = add_cells_to_notebook(self.nb, chapter['Failure Cells'])
                break
        # if all variables are present, add success condition cells
        if success:
            self.nb = add_cells_to_notebook(self.nb, chapter['Success Cells'])
        # extract any defined outputs ("Computes" values)
        self.rpl_vals.update(self._extract_computed_values(chapter))
        # try replacing any Replaces values
        self._replace_strings()
        # check for more Replace values, and tag markdown cells with "rpl" if they exist
        self._tag_replace_strings()

    def _get_scope_additions(self, chaptercells: List[dict]) -> List[str]:
        initial_scope = self._get_nb_scope()
        self.nb = add_cells_to_notebook(self.nb, chaptercells)
        final_scope = self._get_nb_scope()
        # remove jupyter internals
        scopediff = set([v for v in list(set(final_scope) - set(initial_scope)) if not v.startswith('_')])

        return scopediff

    def _get_nb_scope(self):
        # define variable scope cell
        # TODO : move this to a config file
        # TODO : make this a Cell object
        if self.kernel == "python":
            scope_cell = {
                'cell_type': 'code',
                'source': 'locals()',
                'tags': ['scope', 'trim']
            }
        elif self.kernel == "R":
            scope_cell = {
                'cell_type': 'code',
                'source': 'ls()',
                'tags': ['scope', 'trim']
            }
        else:
            raise NotImplementedError(f"Scope checking not compatible with specified kernel: {self.kernel}")
        tmp_pth = 'tmp.ipynb'
        # TODO : add execution parameters here if they exist
        nb2 = pm.execute_notebook(add_cell_to_notebook(self.nb, scope_cell), tmp_pth)
        # Ignore any variables that are assigned as None
        if self.kernel == "python":
            scope_dict = {s.split(': ')[0].replace("'",""): s.split(': ')[1] 
                for s in nb2['cells'][-1]['outputs'][0]['data']['text/plain'][1:-1].split(",\n ")
                if not s.split(': ')[1] == "None"
            }
            scope_vars = list(scope_dict.keys())
        elif self.kernel == "R":
            scope_vars = nb2['cells'][-1]['outputs'][0]['data']['text/plain'].replace(
                '[1] ', ''
                ).replace(
                    "'",""
                ).replace(
                    '"',''
                ).split(' ')
        # Remove scope_cell from notebook
        self.nb['cells'].pop(-1)
        return scope_vars
        
    
    
        
        
        
        
        
        
        
        
        
        
        
        

def create_cell_from_dict(celldata: dict) -> nbf.NotebookNode:
    if celldata['cell type'] == 'code':
        newcell = nbf.v4.new_code_cell(source = celldata['source'])
    elif celldata['cell type'] == 'markdown':
        newcell = nbf.v4.new_markdown_cell(source = celldata['source'])
    newcell['metadata']['tags'] = celldata['tags']

    return newcell

def add_cell_to_notebook(nb: nbf.NotebookNode, celldata: dict) -> nbf.NotebookNode:
    newcell = create_cell_from_dict(celldata)
    nb['cells'].append(newcell)
    return nb

def add_cells_to_notebook(nb: nbf.NotebookNode, chaptercells: List[dict]) -> nbf.NotebookNode:
    for celldata in chaptercells:
        nb = add_cell_to_notebook(nb, celldata)
    return nb

def append_chapter(
    nb: nbf.NotebookNode,
    chapter: dict,
    current_scope: List[str]
) -> nbf.NotebookNode:
    # ensure all Requires vars are in current_scope
    # else return nb (skip adding Chapter)
    # TODO : readout when we can't add the Chapter?
    # add new cells
    # get scope additions
    # check variables added to scope
    # if all variables are present, add success condition cells
    # else, add fail condition cells
    # extract any defined outputs ("Computes" values)
    # try replacing any Replaces values
    # check for more Replace values, and tag markdown cells with "rpl" if they exist
    # return notebook
    pass

def build_notebook(chapters: List[dict], output_path) -> nbf.NotebookNode:
    # initialize empty
    current_scope = []
    nb = nbf.v4.new_notebook()
    # add chapters
    for chapter in chapters:
        nb = append_chapter(nb, chapter, current_scope)
        
    # write notebook
    with open(output_path) as f:
        nbf.write(nb, f)
        
def load_chapters(chapter_yaml_path: str) -> dict:
    with open(chapter_yaml_path) as stream:
        try:
            chapters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print("Error loading in Chapters, please check the Chapters YAML file.")
            raise
    return chapters
    

    


