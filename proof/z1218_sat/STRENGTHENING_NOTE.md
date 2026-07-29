# Row-8 branch strengthening

If a hypothetical 109-edge `12 x 18` matrix has a degree-8 row, deleting that row leaves a 101-edge `11 x 18` K3,3-free matrix. Since `Z(11,17,3,3)=96`, every column of the deleted-row matrix has degree at least `101-96=5`; otherwise deleting that column would leave at least 97 edges on `11 x 17` rows and columns. The SAT generator therefore enforces at least five old incidences in every column of the `row8` branch.
