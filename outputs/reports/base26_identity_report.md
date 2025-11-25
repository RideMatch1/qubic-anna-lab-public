# Base-26 Diagonal Identity Report

- Matrix file: `data/anna-matrix/Anna_Matrix.xlsx`
- Matrix hash: `6006c6650a9dab69901a9420a7dbd64703d7f6849ff95300677160c9f193ca6d`
- Total identities: 4

## Manual (CFB) identities

| Label | Identity | Public Key | Checksum valid |
| --- | --- | --- | --- |
| Diagonal #1 (CFB published) | `AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRMDCK` | `100399d2bdcde33af76860d15d7f1e3346193a89ac6ea63b801e8b0a1d3e884d` | False |
| Diagonal #2 (CFB published) | `GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRRDGKC` | `8a5bea5f8813d7f77fbe16119314b2310e71878b901d6d19d607588eadecc660` | False |
| Diagonal #3 (CFB published) | `ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLDPHO` | `54dcbf7ef88586865bdce9c14a13088c625b920e597d709a5f46e24c0790aa8c` | False |
| Diagonal #4 (CFB published) | `GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHXMTI` | `7e69a8a83d23355f3730d983a1e2bead70df1efa43c510eaebc17dabed2e8d0a` | False |

## Auto-derived checksums

| Label | Identity | Public Key | Checksum valid |
| --- | --- | --- | --- |
| Diagonal #1 (valid checksum) | `AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR` | `100399d2bdcde33af76860d15d7f1e3346193a89ac6ea63b801e8b0a1d3e884d` | True |
| Diagonal #2 (valid checksum) | `GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ` | `8a5bea5f8813d7f77fbe16119314b2310e71878b901d6d19d607588eadecc660` | True |
| Diagonal #3 (valid checksum) | `ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV` | `54dcbf7ef88586865bdce9c14a13088c625b920e597d709a5f46e24c0790aa8c` | True |
| Diagonal #4 (valid checksum) | `GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC` | `7e69a8a83d23355f3730d983a1e2bead70df1efa43c510eaebc17dabed2e8d0a` | True |

## Notes

- Each identity body (56 letters) comes from the diagonal walk inside one 32×32 window. I extracted these by walking diagonally through 4 different 32x32 blocks in the matrix.
- Suffixes published by CFB do not match the KangarooTwelve checksum, so wallet validation fails if used directly. Auto-derived versions were generated to address this.
- Auto-derived variants keep the same public key but reintroduce a valid checksum for reference. The public key is what matters for on-chain verification.