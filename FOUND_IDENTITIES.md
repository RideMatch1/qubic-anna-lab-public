# Found Identities - Public Documentation

This document lists all identities found in the Anna Matrix. These are public keys (Qubic identities) that exist on-chain and can be verified independently.

## Layer-1 Identities (From Matrix)

### Diagonal Identities

1. `AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR`
2. `GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ`
3. `ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV`
4. `GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC`

### Vortex Identities

5. `UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF`
6. `HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD`
7. `JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL`
8. `XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK`

## Verification

All 8 identities can be verified on-chain using:

```bash
docker run --rm -it -v "$PWD":/workspace -w /workspace qubic-proof \
 python scripts/verify/rpc_check.py
```

Or check individually using Qubic RPC:

```python
from qubipy.rpc import rpc_client
rpc = rpc_client.QubiPy_RPC()
balance = rpc.get_balance("AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR")
```

## Seeds Derived from Identities

Each identity body (first 56 characters) can be converted to a seed using:
`seed = identity.lower()[:55]`

### Seeds from Diagonal Identities

1. `aqiosqqmacybpxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxddrdwo`
2. `gwuxommmmfmtbwfzsngmukwbiltxqdkmmmmnypeftamronjmablhtrrroh`
3. `acgjgqqyilbpxdrborfgwfzbbbnlqnhgddelvlxxxlbnnnfbllpbnnnlj`
4. `giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbhthk`

### Seeds from Vortex Identities

5. `uufeemuuibiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobmlkm`
6. `hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcbna`
7. `jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscwcd`
8. `xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirjmxclfa`

## Layer-2 Identities (Derived from Seeds)

When these seeds are used to derive identities, they produce additional on-chain identities. See `scripts/verify/identity_deep_scan.py` for full details.

## Important Notes

- **These are public keys, not private keys** - Anyone can verify they exist on-chain
- **Seeds are derived from identities** - We found identities first, then discovered they contain valid seeds
- **All identities have balance 0** - They exist but have no funds
- **All identities are verifiable** - Use the scripts provided to check independently

## Extraction Method

Identities were extracted using:
- Base-26 encoding of matrix values
- Diagonal patterns (4 identities)
- Vortex patterns (4 identities)

See `analysis/21_base26_identity_extraction.py` and `analysis/71_9_vortex_extraction.py` for details.
