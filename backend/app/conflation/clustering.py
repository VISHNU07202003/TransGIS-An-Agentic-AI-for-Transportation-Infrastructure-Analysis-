class ConstrainedClustering:
    def __init__(self):
        self.parent = {}
        self.constraints = set() # Set of tuples (node1, node2) that cannot be linked
        self.source_map = {} # Maps entity to its dataset source to prevent same-source merges

    def find(self, i):
        if self.parent.setdefault(i, i) == i:
            return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def add_cannot_link_constraint(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        self.constraints.add((root_i, root_j))
        self.constraints.add((root_j, root_i))

    def set_source(self, entity, source):
        self.source_map[entity] = source

    def validate_merge(self, root_i, root_j):
        if root_i == root_j:
            return True
            
        # 1. Cannot-link explicit constraint
        if (root_i, root_j) in self.constraints:
            return False
            
        # 2. Same-source constraint (e.g., two distinct FDOT segments shouldn't cluster into one canonical edge if they represent different physical lanes not meant to merge)
        # For simplicity in this logic, we assume checking all children
        source_set_i = {self.source_map.get(node) for node, p in self.parent.items() if self.find(node) == root_i}
        source_set_j = {self.source_map.get(node) for node, p in self.parent.items() if self.find(node) == root_j}
        
        # Remove Nones
        source_set_i.discard(None)
        source_set_j.discard(None)
        
        # If there's an intersection, it means two items from the SAME source are being clustered together.
        # This is a false merge (e.g. FDOT-1 and FDOT-2 merging into the same canonical entity).
        if source_set_i.intersection(source_set_j):
            return False
            
        return True

    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        
        if root_i != root_j:
            if self.validate_merge(root_i, root_j):
                self.parent[root_i] = root_j
                
                # Update constraints for the new merged root
                new_constraints = set()
                for c1, c2 in self.constraints:
                    if c1 == root_i: new_constraints.add((root_j, c2))
                    if c2 == root_i: new_constraints.add((c1, root_j))
                self.constraints.update(new_constraints)
                return True
            else:
                return False
        return True

    def get_clusters(self):
        clusters = {}
        for node in self.parent:
            root = self.find(node)
            clusters.setdefault(root, []).append(node)
        return list(clusters.values())
