from typing import List, Set, Dict
from collections.abc import Callable
from FuncNode import FuncNode

# TODO : use TypedDict from typing for e.g. self._namespaceVars that must be {str: FuncNode}
class FuncTree(Object):
    def __init__(self, root: FuncNode):
        self._root = root
        self._namespaceVars = {} #{str: FuncNode} for all connected nodes
        self._brokenNodes = {} # {FuncNode: [str]} all broken nodes -> their missing reqs
        self._brokenVars = {} # {str: FuncNode} for all broken nodes (reqs that won't get defined in the current execution graph)

    @property
    def root(self) -> FuncNode:
        return self._root

    @property
    def namespaceVars(self) -> Dict[str, FuncNode]:
        return self._namespaceVars

    @property
    def brokenNodes(self) -> Dict[FuncNode: Set[str]]:
        return self._brokenNodes

    @property
    def brokenVars(self) -> Dict[str, FuncNode]:
        return self._brokenVars

    def getNamespace(self) -> List[str]:
        return list(self._namespaceVars.keys())

    def addNode(self, newNode: FuncNode) -> None:
        missingReqs = self._connectNewNode(newNode)
        if missingReqs:
            self._brokenNodes[newNode.outVar] = newNode
        else:
            self._namespaceVars[newNode.outVar] = newNode
        # check if any broken nodes require the new outVar
        self._connectBrokenNodes(newNode)


    def _connectNewNode(self, newNode: FuncNode) -> List[str]:
        missingReqs = []
        for req in newNode.reqs:
            if req in self._namespaceVars.keys():
                newNode.addParent(self._namespaceVars[var])
                self._namespaceVars[var].addChild(newNode)
            elif req in self._brokenVars.keys():
                newNode.addParent(self._brokenVars[var])
                self._brokenVars[var].addChild(newNode)
            else:
                missingReqs.append(req)
        return missingReqs

    def _connectBrokenNodes(self, newNode) -> None:
        for node in list(self._brokenNodes.keys()):
            if newNode.outVar in self._brokenNodes[node]:
                node.addParent(newNode)
                newNode.addChild(node)
                self._brokenNodes[node].pop(newNode.outVar)
                # if no more missing reqs, promote node to namespaceVars
                if not self._brokenNodes[node]:
                    self._namespaceVars[node.outVar] = node
                    del self._brokenNodes[node]



