# CSV Export Contract

This contract defines the first Plan2Print export format for Riedel Bau plan
processing. It focuses on WDB and DDB openings detected from imported PDFs.

## Required Columns

| Column                       | Type   | Description                                                               |
| ---------------------------- | ------ | ------------------------------------------------------------------------- |
| Floor                        | string | Floor identifier, for example `U1`.                                       |
| Construction phase/Plan name | string | Source plan or construction phase name.                                   |
| Length/cm                    | number | Rectangular opening length. For round openings, this equals the diameter. |
| Width/cm                     | number | Rectangular opening width. For round openings, this equals the diameter.  |
| Height/cm                    | number | Slab or opening height, usually from the associated `d=` marking.         |
| Geometry                     | string | `round` or `rectangular`.                                                 |
| Type                         | string | `Ceiling`, `Wall`, or `Unknown`.                                          |
| Number                       | number | Deduplicated quantity for this grouped opening.                           |
| Weight/kg                    | number | Estimated weight per grouped row, rounded to one decimal place.           |

## Audit Columns

| Column          | Type   | Description                                          |
| --------------- | ------ | ---------------------------------------------------- |
| Source PDF      | string | Imported PDF file name.                              |
| Grid coordinate | string | Approximate grid coordinate, or `grid_unknown`.      |
| Color zone      | string | Detected colored zone identifier, or `zone_unknown`. |
| Confidence      | number | Confidence from `0` to `1`.                          |
| Review status   | string | `ready`, `review_required`, or `split_recommended`.  |

## Round Opening Mapping

Round openings use the detected diameter for both `Length/cm` and `Width/cm`.
For example, `DDB Ø15` exports as `Length/cm = 15`, `Width/cm = 15`,
`Geometry = round`.

## Missing And Ambiguous Values

- Unknown text fields use `unknown`.
- Unknown numeric fields are left blank in CSV output.
- Rows with uncertain type, duplicate risk, missing height, or weight above
  `25 kg` use `Review status = review_required` or `split_recommended`.

## Sample Rows

```csv
Floor,Construction phase/Plan name,Length/cm,Width/cm,Height/cm,Geometry,Type,Number,Weight/kg,Source PDF,Grid coordinate,Color zone,Confidence,Review status
U1,BFS_88160_A_T_5_SP_U1_0001_06,10,10,30,round,Ceiling,3,5.8,SP_U1_0001.pdf,M-21,zone-001,0.92,ready
U1,BFS_88160_A_T_5_SP_U1_0001_06,20,50,25,rectangular,Ceiling,2,20.2,SP_U1_0001.pdf,H-17,zone-002,0.88,ready
U1,BFS_88160_A_T_5_SP_U1_0002_06,65,35,25,rectangular,Wall,1,24.0,SP_U1_0002.pdf,R-24,zone-004,0.74,review_required
```
