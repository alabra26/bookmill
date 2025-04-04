from collections.abc import Callable
from typing import Set, List

# TODO : we need to implement __hash__ and __eq__ if we want to use this class as a dictionary key
class FuncNode(Object):
    def __init__(self, func: Callable, params: List[str], reqs: Set[str], outVar: str):
        self._parents = []
        self._children = []

        self._code = func
        self._params = params
        self._outVar = outVar
        self._reqs  = reqs

    @property
    def reqs(self):
        return self._reqs

    @property
    def outVar(self):
        return self._outVar

    @property
    def code(self):
        return self._code

    @property
    def parents(self):
        return self._parents

    @property
    def children(self):
        return self._children

    @property
    def params(self):
        return self._params

    def addParent(self, parent: FuncNode) -> None:
        self._parents.append(parent)

    def addChild(self, child: FuncNode) -> None:
        self._children.append(child)


