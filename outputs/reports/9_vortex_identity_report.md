# 9-Vortex Identity Report

- Matrix file: `data/anna-matrix/Anna_Matrix.xlsx`
- Matrix hash: `6006c6650a9dab69901a9420a7dbd64703d7f6849ff95300677160c9f193ca6d`

| Radius | Identity | Public Key | Checksum valid |
| --- | --- | --- | --- |
| 18 | `UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF` | `b069ad4209dcf538af6cf193f921948b64bd85130793af2913a20786ccdc8267` | True |
| 44 | `HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD` | `ed15cf997523c065ab393dfb4b02ad026727db3bc4b5e7625d5300ccb50519c1` | True |
| 66 | `JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL` | `09c9ff18cc91d289b84381e502efcd318ab721ac34fa1d505636509ff0812362` | True |
| 82 | `XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK` | `cb71959191ccb437b8d8b804630121a3105fefddebc84eb6226f37dd5157117e` | True |

## Notes

- Only the first 56 letters per ring are used as the identity body, checksum derived afterwards. I sampled cells in a spiral pattern starting from different radii (18, 44, 66, 82).
- Published suffixes from diagonal extraction do not apply here, all four rings produce auto-derived checksums. The vortex pattern gives different identities than the diagonal method.
- Visualization highlights the angular ordering of sampled cells - you can see the spiral path in the plots.
