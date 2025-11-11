# Report

slides:
https://spatiotemporaldata2025.github.io/TEUKU_zikri/Algo2

**R-tree: A Dynamic Index Structure for Spatial Searching**
by Antonin Guttman and Michael Stonebraker

## Introduction

When this R-tree paper was written, I did not fully understand the research context at that time, but it seems there were already several existing search algorithms such as B-trees.

To start, I tried to understand the content of the paper itself.

In the introduction, the author mentioned several earlier indexing methods and their limitations:

<!-- 
"indexing structures are not appropriate to spatial searching. 
Multi-dimensional structures based on exact matching of values, 
such as hash tables, are not useful because a range search is required. 
Structures using one-dimensional ordering of key values, 
such as B-trees and ISAM indexes, do not work because the search is multi-dimensional."
-->

![alt text](image_1.png)

In the early 1980s, database systems such as **INGRES** and **System R** only supported classical indexing methods:

* **B-tree / ISAM** → suitable for one-dimensional ordered data
* **Hash table** → suitable for exact match searches

However, there was no efficient method for:

* Multi-dimensional data (2D, 3D, etc.)
* Objects with actual size (not just points, but areas such as rectangles or polygons)
* Searches based on position or area (range / spatial search)

As a result, when handling spatial data such as maps, chip layouts, or CAD designs, finding “all objects within 20 km of a given point” required checking every record linearly.
This was very slow for large datasets containing millions of objects.

In other words, the authors wanted a database system capable of answering spatial queries such as:

* Which objects are inside this region?
* Which objects are near point (x, y)?
* Which parts of the map overlap with a given area?

Without scanning the entire table.

---

## Application Context

The paper also mentioned several major application areas for spatial indexing.

![alt text](image_2.png)

* **Computer-Aided Design (CAD):** finding circuit parts in a specific layout area.
* **Geographic Information Systems (GIS):** locating map regions within a certain radius.
* **General spatial databases:** storing building footprints, rivers, zones, and other region-based data.

---

## Concept of R-Tree

![alt text](image_3.png)

The **R-Tree** organizes spatial data into a **hierarchy of bounding rectangles**.

* Each node represents a region that covers several child objects.
* **Leaf nodes** store the actual spatial objects.
* **Non-leaf nodes** store bounding boxes that enclose all their children.
* All leaf nodes exist at the same level, keeping the tree balanced like a B-tree.

With this structure, searches do not need to scan all data; only the branches whose bounding boxes overlap with the query region are explored.

Efficiency is achieved because the search process only visits nodes whose bounding boxes intersect with the query area.
Nodes that do not intersect are ignored without being accessed.

---

## Comparison with Previous Methods

| **Method**           | **Advantage**                                                           | **Disadvantage**                                                                  |
| -------------------- | ----------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| **Hash Table**       | Very fast for exact-match lookups                                       | Cannot perform range or spatial queries                                           |
| **B-tree / ISAM**    | Efficient for one-dimensional ordered data                              | Cannot handle multi-dimensional data; no concept of spatial proximity             |
| **R-Tree**           | Dynamic, balanced hierarchy of bounding boxes; efficient spatial search | More complex to implement and maintain than traditional B-trees                   |

---

## Conclusion

The **R-Tree** successfully addressed the shortcomings of earlier indexing structures by combining the hierarchical efficiency of B-trees with true multi-dimensional spatial capability.
It provides a **dynamic and efficient index structure** for spatial and range-based searches.

Key findings from the paper include:

1. The **linear R-tree algorithm** performs almost as well as more complex and computationally expensive methods. Slightly less optimal splits do not significantly affect query performance.
2. The **R-tree** proved to be a highly useful structure for managing spatial data, especially in secondary storage (disk). It was later adopted by the **IBM Informix system** as an efficient spatial indexing method.
3. Beyond spatial databases, **R-trees** can also be applied to other types of multi-dimensional data, such as numerical value combinations or temporal data (time intervals).

In summary, the R-tree plays a key role in improving **search efficiency for spatial data** by:

* Reducing the number of nodes accessed using bounding-box overlap pruning
* Maintaining a balanced tree structure for logarithmic search time
* Supporting dynamic insertion and deletion of multi-dimensional data

This structure has become the foundation of modern spatial database systems, GIS engines, and any applications requiring fast search over multi-dimensional or geometric data.


# Implementation
I plan to implement an R-tree for the robot’s behavior.
In this case, I represent it using Pygame, where the robot (blue box) must go to the target (green dot) while avoiding obstacles (red boxes). Each time a target is reached, a new target will appear.

![alt text](image.png)

However, there is a problem: sometimes in `robot_1.py`, the target appears too close to an obstacle or even right inside an obstacle, making it impossible to reach and causing the program to get stuck (a bug).

![alt text](image1.png)

I apply the R-tree algorithm in `robot_2.py` to detect whether there are nearby obstacles before setting a new movement target, so now the target will always be possible to reach.

![alt text](image2.png)

But there is another issue: when obstacles are generated, sometimes they are too close to each other, making the map less interesting. Some areas are too crowded while others are too empty. I want to make them more spread out, so I apply an R-tree in `robot_3.py` to detect nearby obstacles before generating a new one. As a result, the map is more interesting and looks like this:

![alt text](image3.png)

In summary, starting from a naive baseline, adding an R-tree first ensures targets are always reachable and then helps distribute obstacles more evenly. This simple spatial index makes queries faster and the simulation more robust.