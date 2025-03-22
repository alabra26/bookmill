import nbformat as nbf

from bookmill.src.utils import get_scope_additions
import os

test_new_cell = {
    'cell_type': 'code',
    'source': 'b = 2',
    'tags': []
}

def test_get_scope_additions():
    nb = nbf.read('tests/data/scope_tracking.ipynb', nbf.NO_CONVERT)
    scopediff = get_scope_additions(nb, [test_new_cell])
    assert scopediff == set('b')
    
