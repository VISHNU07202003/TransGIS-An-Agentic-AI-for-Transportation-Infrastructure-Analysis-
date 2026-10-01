import pytest
from app.conflation.clustering import ConstrainedClustering

def test_transitive_trap_avoidance():
    # Scenario: A ≈ B, B ≈ C, A !≈ C
    # e.g., Parallel roads where FDOT segment matches both directions slightly, but the directions shouldn't merge.
    
    cc = ConstrainedClustering()
    
    # A and C are from the SAME source dataset (e.g. FDOT-Dir1 and FDOT-Dir2)
    # They shouldn't be merged into the same cluster.
    cc.set_source("A", "FDOT")
    cc.set_source("C", "FDOT")
    cc.set_source("B", "OSM")
    
    # Merge A and B (Success)
    assert cc.union("A", "B") == True
    
    # Merge B and C (Fails because it would transitively merge A and C, which have the same source)
    assert cc.union("B", "C") == False
    
    clusters = cc.get_clusters()
    
    # Verify A and C are separated
    root_A = cc.find("A")
    root_C = cc.find("C")
    assert root_A != root_C
    
def test_explicit_cannot_link_constraint():
    cc = ConstrainedClustering()
    
    cc.add_cannot_link_constraint("North_St", "South_St")
    
    # Attempt direct merge
    assert cc.union("North_St", "South_St") == False
    
    # Attempt transitive merge
    assert cc.union("North_St", "Main_St") == True
    assert cc.union("South_St", "Main_St") == False # Rejected by transitive constraint

def test_naive_transitive_grouping_would_fail():
    # Demonstrating the baseline union find
    class NaiveUF:
        def __init__(self):
            self.parent = {}
        def find(self, i):
            if self.parent.setdefault(i, i) == i: return i
            self.parent[i] = self.find(self.parent[i])
            return self.parent[i]
        def union(self, i, j):
            self.parent[self.find(i)] = self.find(j)
            
    uf = NaiveUF()
    uf.union("A", "B")
    uf.union("B", "C")
    assert uf.find("A") == uf.find("C") # The trap occurred!
