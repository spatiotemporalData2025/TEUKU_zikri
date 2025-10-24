# Report
R-tree a dynamic index structure for spatial searching by Anthonin Guttman and Michel stonebreaker

sebenarnya ketika paper R-tree ini dilakukan saya tidak terlalu paham konteks nya seperti apa,
tapi sepertinya terdapat algoritma searching lain sebelum ini seoerti B-tree.

pertama saya akan mencoba memahami isi paper tersebut terlebih dahulu:


pada introduction the author melakukan mention kepada beberapa algoritma sebelumnya dan kekurangnaya:
"indexing structures are not appropriate to spatial searchmg multi-dimensional Structures based on exact matchmg of values, such as hash tables, are not useful because a range search 1s requed Structures using one- dimenslonal ordering of key values, such as B-trees and ISAM mdexes, do not work because the search dimensional" 


tampaknya Pada awal 1980-an, sistem basis data seperti INGRES atau System R hanya mendukung metode indeks klasik,
B-tree / ISAM → bagus untuk data satu dimensi
Hash table → bagus untuk pencarian exact match



