from graphviz import Digraph, Graph

class TimeTree:
    def __init__(self, name: str, versions : 'dict[int, list[TimeTreeVersion]]' = {}):
        self.name = name
        self.versions = versions
    
    def get_version(self, version : int):
        return TimeTreeVersion(self, version, self.versions[version])

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return str(self)

class TimeTreeVersion:
    def __init__(self, time_tree: 'TimeTreeVersion', version : int, dependencies : 'list[TimeTreeVersion]'):
        self.time_tree = time_tree
        self.version = version
        self.dependencies = dependencies

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

    def get_all_dependency_versions(self):
        to_return = set()
        for dependency in self.dependencies:
            to_return.add(dependency)
            to_return.update(dependency.get_all_dependency_versions())
        return to_return
    
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

def draw_simple_time_tree(time_tree_version : 'TimeTreeVersion', contradictions: 'list[TimeTree]' = None, dot : 'Digraph' = None):
    if contradictions is None:
        contradictions = time_tree_version.get_contradictions()

    if (dot is None):
        dot = Digraph()
        dot.node(name=str(time_tree_version), label=str(time_tree_version))
        

    for child in time_tree_version.dependencies:
        color = "red" if child.time_tree in contradictions else "black"
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
            draw_simple_time_tree(version, dot = dot)
    
    return dot

d = TimeTree("D", versions = {1: []})
b = TimeTree("B", versions = {1 : [d.get_version(1)], 2: [d.get_version(1)]})
c = TimeTree("C", versions = {1 : [d.get_version(1)]})
a = TimeTree("A", versions = {1 : [b.get_version(1), c.get_version(1)], 2: [b.get_version(2)]})

print(a.get_version(1).get_contradictions())