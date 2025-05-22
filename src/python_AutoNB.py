import nbformat as nbf
import papermill as pm
import yaml
# from typing import Dict, List
import re

# TODO : implement cell_not_executed and confirm trimming does not modify inplace

class NBWriter(object):
    def __init__(self, template_path: str, report_savepath: str = None):
        # TODO : compatibility for a passed file object, filepath string, S3 URI string, etc.
        with open(chapter_yaml_path) as stream:
        try:
            self.chapters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print("Error loading in Chapters, please check the passed Notebook Template file.")
            raise
        # TODO : validate chapters?

        self.report_savepath = report_savepath

    def populate_template(self):
        """Creates an nbformat object from self.chapters into self.template """
        self.template = nbf.v4.new_notebook()
        newcell = nbf.v4.new_code_cell(
            source = """from magics.skip_magics import RequireVarsMagic, MissingVarsMagic
requires = RequireVarsMagic.register()
check_missing = MissingVarsMagic.register()"""
        )
        newcell['metadata']['tags'] = ['trim']
        self.template['cells'].append(newcell)
        for chapter in self.chapters:
            self._append_chapter(chapter)

    def _append_chapter(self, chapter) -> nbf.NotebookNode:
        for cell in chapter['cells']:
            newcell = self._create_cell_from_dict(celldata)
            self.template['cells'].append(newcell)

    def _create_cell_from_dict(self, celldata: dict) -> nbf.NotebookNode:
        # add necessary magics
        # TODO : confirm that we don't need a third magic (Replaces?)
        src = celldata['source']
        if celldata['Requires']:
            src = self._append_requires_magic(src, celldata['Requires'])
        if celldata['Excludes']:
            src = self._append_check_missing_magic(src, celldata['Excludes'])
            
        if celldata['cell type'] == 'code':
            newcell = nbf.v4.new_code_cell(source = src)
        elif celldata['cell type'] == 'markdown':
            newcell = nbf.v4.new_markdown_cell(source = src)
        else:
            raise ValueError(f"Tried to create cell with unsupported type: {celldata['cell type']}. Only compatible with 'code' or 'markdown'")
        newcell['metadata']['tags'] = celldata['tags']
    
        return newcell

    def _append_requires_magic(self, source:str, params: list) -> nbf.NotebookNode:
        return f"%%requires {' '.join(params)}\n{source}"

    def _append_check_missing_magic(self, source:str, params: list) -> nbf.NotebookNode:
        return f"%%check_missing {' '.join(params)}\n{source}"
        
    def save_nb(self, savepth: str = None):
        """Saves self.report into savepath or self.savepath"""
        savepath = savepth or self.report_savepath
        if savepath:
            if not savepath.endswith(".ipynb"):
                raise ValueError(f"Incompatible file extension in report savepath {savepath}. Must use .ipynb")
            with open(savepath) as f:
                nbf.write(self.report, f)
            print(f"Saved notebook to {savepath}")
        else:
            raise NameError("Please define `report_savepath` before saving, or pass a .ipynb path string to `save_nb`.")
    def trim_nb(self):
        """Trims nbformat object self.notebook and yields self.report"""
        tmp = trim_unexecuted_cells(self.notebook)
        self.report = trim_custom_magics(tmp)

    def execute_nb(self, params: dict):
        """Executes nbformat object in self.template using params and creates self.notebook"""
        self.notebook = pm.execute_notebook(self.template, parameters = params, 'tmp.ipynb')

    def run(self, params, savepath = None):
        if not self.template:
            self.populate_template()
        self.execute_nb(params)
        self.trim_nb()
        self.save_nb(savepath)
        
def cell_not_executed(cell: dict) -> bool:
    pass

def trim_unexecuted_cells(nb: nbf.NotebookNode) -> nbf.NotebookNode:
    # TODO : confirm that this does not modify inplace (NBWriter.notebook)
    for ind, cell in reversed(list(enumerate(nb['cells']))):
        if cell_not_executed(cell):
            del nb['cells'][ind]
        elif 'trim' in cell['metadata']['tags']:
            del nb['cells'][ind]
    return nb

def trim_custom_magics(nb: nbf.NotebookNode) -> nbf.NotebookNode:
    requires_str = r"%%defines(?: [\w]+)+ ?\n" # TODO : we might not need the trailing space, if it is determined that breaks our magic
    checkmissing_str = r"%%check_missing(?: [\w]+)+ ?\n" # TODO : confirm ?: is the correct python re syntax for a non-capturing group

    for cell in nb['cells']:
        cell['source'] = re.sub(requires_str, '', cell['source'])
        cell['source'] = re.sub(checkmissing_str, '', cell['source'])
    return nb

