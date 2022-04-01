from graphviz import Digraph, Graph

class TimeTree:
    def __init__(self, name: str, versions : 'dict[int, list[TimeTreeVersion]]' = {}):
        self.name = name
        self.versions = versions
        self.time_tree_versions = {}

        for version_number, dependencies in versions.items():
            for dependency in dependencies:
                dependency.add_parent(self.get_version(version_number))

    def get_version(self, version : int):
        if version not in self.time_tree_versions:
            self.time_tree_versions[version] = TimeTreeVersion(self, version, self.versions[version])
        return self.time_tree_versions[version]

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return str(self)

    def __getitem__(self, i):
        return self.get_version(i)

class TimeTreeVersion:
    def __init__(self, time_tree: 'TimeTreeVersion', version : int, dependencies : 'list[TimeTreeVersion]'):
        self.time_tree = time_tree
        self.version = version
        self.dependencies = dependencies
        self.parents : 'list[TimeTree]' = []

    def add_parent(self, parent : TimeTree):
        self.parents.append(parent)

    @property
    def name(self):
        return self.time_tree.name

    def __repr__(self) -> str:
        return str(self)

    def __str__(self):
        return f"{self.time_tree.name} {self.version}"
    
    def __eq__(self, o: object) -> bool:
        return (o.time_tree.name == self.time_tree.name and o.version == self.version)

    def __hash__(self) -> int:
        return hash((self.version, self.time_tree.name))

    '''
    Get all descendents of the current time tree.
    '''
    def get_all_dependency_versions(self):
        to_return = set()
        for dependency in self.dependencies:
            to_return.add(dependency)
            to_return.update(dependency.get_all_dependency_versions())
        return to_return
    
    '''
    Get all contradictions under this time tree.
    A contradiction is when two versions of the same time tree are under the same parent.
    '''
    def get_contradictions(self):
        all_dependencies = {}
        contraditions = set()
        for dependency in self.get_all_dependency_versions():
            if (dependency.name not in all_dependencies):
                all_dependencies[dependency.name] = set()
            all_dependencies[dependency.name].add(dependency.version)
            if len(all_dependencies[dependency.name]) > 1:
                contraditions.add(dependency.time_tree)
        
        return contraditions

    '''
    Get all nodes for whom this node is a descendant.
    '''
    def get_ancestors(self):
        ancestors = []
        for i in self.parents:
            ancestors.append(i)
            ancestors+=i.get_ancestors()
        return ancestors

    '''
    Get all nodes that have both the current node and the other node as a descendant.
    '''
    def find_commonalities(self, other : 'TimeTreeVersion') -> 'set[TimeTreeVersion]':
        return set(self.get_ancestors()).intersection(set(other.get_ancestors()))

    '''
    Get all nodes under the current node that have both a and b as descendents.
    '''
    def find_commonalities_under(self, a: 'TimeTreeVersion', b: 'TimeTreeVersion') -> 'set[TimeTreeVersion]':
        to_return = set(self.get_all_dependency_versions()).intersection(a.find_commonalities(b))
        if (len(to_return) != 0):
            to_return.add(self)
        return to_return

    '''
    Get all nodes under the current node for whom all of the below is true:
    1. Have A and B as descendents (see find_commonalities_under)
    2. One of the following is true:
        a. There are no other commonalities beneath it
        b. There is 1+ commonality beneath it, but there is also a node that is an ancestor of either a or b that is not a commonality beneath it and not part of the contradition
    '''
    def find_lowest_commonalities(self, a: 'TimeTreeVersion', b: 'TimeTreeVersion') -> 'set[TimeTreeVersion]':
        commonalities = self.find_commonalities_under(a, b)
        a_ancestors = a.get_ancestors()
        b_ancestors = b.get_ancestors()
        to_return = []

        for commonality in commonalities:
            commonality_as_child = False
            ancestor_as_child = False
            for child in commonality.dependencies:
                if child in commonalities:
                    commonality_as_child = True
                elif child in a_ancestors or child in b_ancestors:
                    ancestor_as_child = True
            
            if (ancestor_as_child or not commonality_as_child):
                to_return.append(commonality)
        return to_return

def draw_simple_time_tree(time_tree_version : 'TimeTreeVersion', show_contradictions = True, contradictions: 'list[TimeTree]' = None, dot : 'Digraph' = None):
    if contradictions is None:
        if show_contradictions:
            contradictions = time_tree_version.get_contradictions()
        else:
            contradictions = []
            
    if (dot is None):
        dot = Digraph()
        dot.node(name=str(time_tree_version), label=str(time_tree_version))
        

    for child in time_tree_version.dependencies:
        color = "red" if child.time_tree in contradictions and show_contradictions else "black"
        dot.node(name=str(child), label=str(child), color=color)
        dot.edge(str(time_tree_version), str(child))
        dot = draw_simple_time_tree(child, dot=dot, contradictions = contradictions)
    
    return dot

def draw_total_time_tree(all_time_trees : 'list[TimeTree]'):
    dot = Digraph(strict=True)

    for time_tree in all_time_trees:
        dot.node(name=str(time_tree), label=str(time_tree), shape="triangle")
        for version_number in time_tree.versions.keys():
            version = time_tree.get_version(version_number)
            dot.node(name = str(version), label = str(version))
            dot.edge(str(time_tree), str(version), style="dashed", arrowhead="none")
            draw_simple_time_tree(version, show_contradictions=False, dot = dot)
    
    return dot

d = TimeTree("D", versions = {1: [], 2: []})
c = TimeTree("C", versions = {1: [d[1], d[2]]})
b = TimeTree("B", versions= {1 : [c[1]]})
a = TimeTree("A", versions = {1 : [b[1]]})

print(a[1].find_lowest_commonalities(d[1], d[2]))