from dataclasses import dataclass
from typing import List, Any, Tuple, Optional

@dataclass
class Rect:
    xmin: float
    ymin: float
    xmax: float
    ymax: float

    def area(self) -> float:
        return max(0.0, self.xmax - self.xmin) * max(0.0, self.ymax - self.ymin)

    def union(self, other: "Rect") -> "Rect":
        return Rect(
            xmin=min(self.xmin, other.xmin),
            ymin=min(self.ymin, other.ymin),
            xmax=max(self.xmax, other.xmax),
            ymax=max(self.ymax, other.ymax),
        )

    def enlarge_area_needed(self, other: "Rect") -> float:
        new_rect = self.union(other)
        return new_rect.area() - self.area()

    def intersects(self, other: "Rect") -> bool:
        return not (
            self.xmax < other.xmin or self.xmin > other.xmax or
            self.ymax < other.ymin or self.ymin > other.ymax
        )


class RTreeNode:
    def __init__(self, leaf: bool = True, parent: "RTreeNode" = None):
        self.leaf = leaf
        self.entries: List[Tuple[Rect, Any]] = []
        self.parent: Optional["RTreeNode"] = parent

    def mbr(self) -> Optional[Rect]:
        if not self.entries:
            return None
        r = self.entries[0][0]
        for rect, _ in self.entries[1:]:
            r = r.union(rect)
        return r


class RTree:
    def __init__(self, max_entries: int = 8, min_entries: int = 4):
        assert 1 < min_entries <= max_entries // 2
        self.M = max_entries
        self.m = min_entries
        self.root = RTreeNode(leaf=True)

    def insert(self, rect: Rect, obj: Any):
        leaf = self._choose_leaf(self.root, rect)
        leaf.entries.append((rect, obj))
        self._adjust_tree(leaf)

    def search_range(self, query: Rect) -> List[Any]:
        res: List[Any] = []
        self._search_node(self.root, query, res)
        return res

    def _choose_leaf(self, node: RTreeNode, rect: Rect) -> RTreeNode:
        if node.leaf:
            return node
        best_entry = None
        best_increase = None
        best_area = None
        for r, child in node.entries:
            inc = r.enlarge_area_needed(rect)
            area = r.area()
            if (best_increase is None or
                inc < best_increase or
                (inc == best_increase and area < best_area)):
                best_increase = inc
                best_area = area
                best_entry = (r, child)
        _, child = best_entry
        return self._choose_leaf(child, rect)

    def _adjust_tree(self, node: RTreeNode):
        while True:
            if len(node.entries) > self.M:
                node, new_node = self._split_node(node)
                if node.parent is None:
                    new_root = RTreeNode(leaf=False)
                    node.parent = new_root
                    new_node.parent = new_root
                    new_root.entries = [
                        (node.mbr(), node),
                        (new_node.mbr(), new_node),
                    ]
                    self.root = new_root
                    return
                else:
                    parent = node.parent
                    for i, (r, child) in enumerate(parent.entries):
                        if child is node:
                            parent.entries[i] = (node.mbr(), node)
                            break
                    parent.entries.append((new_node.mbr(), new_node))
                    node = parent
                    continue
            else:
                parent = node.parent
                while parent is not None:
                    for i, (r, child) in enumerate(parent.entries):
                        if child is node:
                            parent.entries[i] = (node.mbr(), node)
                            break
                    node = parent
                    parent = node.parent
                return

    def _split_node(self, node: RTreeNode):
        entries = list(node.entries)
        s1, s2 = self._pick_seeds(entries)
        node1 = node
        node1.entries = [entries[s1]]
        node2 = RTreeNode(leaf=node.leaf, parent=node.parent)
        node2.entries = [entries[s2]]
        used = {s1, s2}
        n = len(entries)
        for i in range(n):
            if i in used:
                continue
            rect, obj = entries[i]
            remaining = n - len(used)
            if len(node1.entries) + remaining == self.m:
                node1.entries.append((rect, obj))
                used.add(i)
                continue
            if len(node2.entries) + remaining == self.m:
                node2.entries.append((rect, obj))
                used.add(i)
                continue
            mbr1 = node1.mbr()
            mbr2 = node2.mbr()
            inc1 = mbr1.enlarge_area_needed(rect)
            inc2 = mbr2.enlarge_area_needed(rect)
            if inc1 < inc2:
                node1.entries.append((rect, obj))
            elif inc2 < inc1:
                node2.entries.append((rect, obj))
            else:
                if mbr1.area() < mbr2.area():
                    node1.entries.append((rect, obj))
                else:
                    node2.entries.append((rect, obj))
            used.add(i)
        if not node1.leaf:
            for _, child in node1.entries:
                child.parent = node1
        if not node2.leaf:
            for _, child in node2.entries:
                child.parent = node2
        return node1, node2

    def _pick_seeds(self, entries: List[Tuple[Rect, Any]]):
        max_d = -1.0
        seed1, seed2 = 0, 1
        n = len(entries)
        for i in range(n):
            for j in range(i + 1, n):
                r1 = entries[i][0]
                r2 = entries[j][0]
                u = r1.union(r2)
                d = u.area() - r1.area() - r2.area()
                if d > max_d:
                    max_d = d
                    seed1, seed2 = i, j
        return seed1, seed2

    def _search_node(self, node: RTreeNode, query: Rect, res: List[Any]):
        for rect, child in node.entries:
            if rect.intersects(query):
                if node.leaf:
                    res.append(child)
                else:
                    self._search_node(child, query, res)
