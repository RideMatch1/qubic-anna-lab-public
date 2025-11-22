# 100 Seeds and Identities - Public Documentation

This document contains 100 seeds and their corresponding Qubic identities found in the Anna Matrix.

## Format

- **Seed**: 55-character lowercase string (derived from identity using `identity.lower()[:55]`)
- **Identity**: 60-character uppercase Qubic identity (public key)
- **Balance**: Current balance on-chain (as of scan date)

## Important Notes

- These are **public keys**, not private keys
- Seeds are derived from identities using the formula: `seed = identity.lower()[:55]`
- All identities exist on-chain and can be verified independently
- These are the first 100 from the comprehensive scan (22,522+ on-chain identities found)

## Verification

You can verify these identities on-chain using:

```bash
docker run --rm -it -v "$PWD":/workspace -w /workspace qubic-proof \
  python scripts/verify/rpc_check.py
```

Or check individually:

```python
from qubipy.rpc import rpc_client
rpc = rpc_client.QubiPy_RPC()
balance = rpc.get_balance("IDENTITY_HERE")
```

---

## Seeds and Identities

| # | Seed | Identity | Balance |
|---|------|----------|---------|
| 1 | `aaaaaaaaaewamanayeyaaaaaywrlaebhiepesefaeejreqtremjchof` | `AAAAAAAAAEWAMANAYEYAAAAAYWRLAEBHIEPESEFAEEJREQTREMJCHOFFIFHJ` | 0 QU |
| 2 | `aaaaaaaccccuacaaaaaaaccccuacaaaaaaaccccuacaaaaaaaccccua` | `AAAAAAACCCCUACAAAAAAACCCCUACAAAAAAACCCCUACAAAAAAACCCCUACJUCI` | 0 QU |
| 3 | `aaaaaaauoxauycaaaaaaauoxauycaaaaaaauoxauycaaaaaaauoxauy` | `AAAAAAAUOXAUYCAAAAAAAUOXAUYCAAAAAAAUOXAUYCAAAAAAAUOXAUYCJOLF` | 0 QU |
| 4 | `aaaaaaeesbrjuaaaaaaaeesbrjuaaaaaaaeesbrjuaaaaaaaeesbrju` | `AAAAAAEESBRJUAAAAAAAEESBRJUAAAAAAAEESBRJUAAAAAAAEESBRJUAOMGC` | 0 QU |
| 5 | `aaaaaaewamanayeyaaaaaywrlaebhiepesefaeejreqtremjchoffvm` | `AAAAAAEWAMANAYEYAAAAAYWRLAEBHIEPESEFAEEJREQTREMJCHOFFVMJXZNI` | 0 QU |
| 6 | `aaaaacaccsacamamcaacaccccuaccsgmisecaagciswuaochnuaccxh` | `AAAAACACCSACAMAMCAACACCCCUACCSGMISECAAGCISWUAOCHNUACCXHSCNRC` | 0 QU |
| 7 | `aaaaaceouoosqwaaaaaceouoosqwaaaaaceouoosqwaaaaaceouoosq` | `AAAAACEOUOOSQWAAAAACEOUOOSQWAAAAACEOUOOSQWAAAAACEOUOOSQWGSVH` | 0 QU |
| 8 | `aaaaacgccsycacaccaacaccccuacckamaaaaacaccsacamamcaacacc` | `AAAAACGCCSYCACACCAACACCCCUACCKAMAAAAACACCSACAMAMCAACACCCZEZE` | 0 QU |
| 9 | `aaaaacgccsycageccaacaggccuacckamammmmcaccemommamcaacacc` | `AAAAACGCCSYCAGECCAACAGGCCUACCKAMAMMMMCACCEMOMMAMCAACACCCDFPK` | 0 QU |
| 10 | `aaaaaeeeykggwuaaaaaeeeykggwuaaaaaeeeykggwuaaaaaeeeykggw` | `AAAAAEEEYKGGWUAAAAAEEEYKGGWUAAAAAEEEYKGGWUAAAAAEEEYKGGWUCPDB` | 0 QU |
| 11 | `aaaaaeeykggwuyaaaaaeeykggwuyaaaaaeeykggwuyaaaaaeeykggwu` | `AAAAAEEYKGGWUYAAAAAEEYKGGWUYAAAAAEEYKGGWUYAAAAAEEYKGGWUYOYCO` | 0 QU |
| 12 | `aaaaaewamanayeyaaaaaywrlaebhiepesefaeejreqtremjchoffvmj` | `AAAAAEWAMANAYEYAAAAAYWRLAEBHIEPESEFAEEJREQTREMJCHOFFVMJNZIXA` | 0 QU |
| 13 | `aaaaaewzdvdponaaaaaewzdvdponaaaaaewzdvdponaaaaaewzdvdpo` | `AAAAAEWZDVDPONAAAAAEWZDVDPONAAAAAEWZDVDPONAAAAAEWZDVDPONAHKB` | 0 QU |
| 14 | `aaaaagkccaacakqkkkakakgmaaaaakkmkkakamamcaacaqqsqqekgse` | `AAAAAGKCCAACAKQKKKAKAKGMAAAAAKKMKKAKAMAMCAACAQQSQQEKGSESAYGO` | 0 QU |
| 15 | `aaaaakkmkkakamamcaacaqqsqqekgsesiwecewgawkgmawwqqueccqq` | `AAAAAKKMKKAKAMAMCAACAQQSQQEKGSESIWECEWGAWKGMAWWQQUECCQQMCPIF` | 0 QU |
| 16 | `aaaaauwnwmenauukuyelaguvxlwrriimiukiknijmfwviisjymsjlng` | `AAAAAUWNWMENAUUKUYELAGUVXLWRRIIMIUKIKNIJMFWVIISJYMSJLNGBCXPA` | 0 QU |
| 17 | `aaaaauwyeyyygyaaaaauwyeyyygyaaaaauwyeyyygyaaaaauwyeyyyg` | `AAAAAUWYEYYYGYAAAAAUWYEYYYGYAAAAAUWYEYYYGYAAAAAUWYEYYYGYMUXJ` | 0 QU |
| 18 | `aaaaaywjhqkuuyaaaaaywjhqkuuyaaaaaywjhqkuuyaaaaaywjhqkuu` | `AAAAAYWJHQKUUYAAAAAYWJHQKUUYAAAAAYWJHQKUUYAAAAAYWJHQKUUYQQCJ` | 0 QU |
| 19 | `aaaaaywrlaebhiepesefaeejreqtremjchoffvmjnvfvpaeaaaaaaee` | `AAAAAYWRLAEBHIEPESEFAEEJREQTREMJCHOFFVMJNVFVPAEAAAAAAEELJRAB` | 0 QU |
| 20 | `aaaacaccsacamamcaacaccccuaccsgmisecaagciswuaochnuaccxhs` | `AAAACACCSACAMAMCAACACCCCUACCSGMISECAAGCISWUAOCHNUACCXHSFEICA` | 0 QU |
| 21 | `aaaacefqtsheqmaaaacefqtsheqmaaaacefqtsheqmaaaacefqtsheq` | `AAAACEFQTSHEQMAAAACEFQTSHEQMAAAACEFQTSHEQMAAAACEFQTSHEQMAHZM` | 0 QU |
| 22 | `aaaacgccsycacaccaacaccccuacckamaaaaacaccsacamamcaacaccc` | `AAAACGCCSYCACACCAACACCCCUACCKAMAAAAACACCSACAMAMCAACACCCCNFKM` | 0 QU |
| 23 | `aaaacgccsycageccaacaggccuacckamammmmcaccemommamcaacaccc` | `AAAACGCCSYCAGECCAACAGGCCUACCKAMAMMMMCACCEMOMMAMCAACACCCCMRBB` | 0 QU |
| 24 | `aaaaeelfjhnfnlaaaaeelfjhnfnlaaaaeelfjhnfnlaaaaeelfjhnfn` | `AAAAEELFJHNFNLAAAAEELFJHNFNLAAAAEELFJHNFNLAAAAEELFJHNFNLEWCI` | 0 QU |
| 25 | `aaaaeezlfjhnfnaaaaeezlfjhnfnaaaaeezlfjhnfnaaaaeezlfjhnf` | `AAAAEEZLFJHNFNAAAAEEZLFJHNFNAAAAEEZLFJHNFNAAAAEEZLFJHNFNWTNN` | 0 QU |
| 26 | `aaaaewafwvvyuuaaaaewafwvvyuuaaaaewafwvvyuuaaaaewafwvvyu` | `AAAAEWAFWVVYUUAAAAEWAFWVVYUUAAAAEWAFWVVYUUAAAAEWAFWVVYUUKVKM` | 0 QU |
| 27 | `aaaaewamanayeyaaaaaywrlaebhiepesefaeejreqtremjchoffvmjn` | `AAAAEWAMANAYEYAAAAAYWRLAEBHIEPESEFAEEJREQTREMJCHOFFVMJNVAGDN` | 0 QU |
| 28 | `aaaagkccaacakqkkkakakgmaaaaakkmkkakamamcaacaqqsqqekgses` | `AAAAGKCCAACAKQKKKAKAKGMAAAAAKKMKKAKAMAMCAACAQQSQQEKGSESIOJOO` | 0 QU |
| 29 | `aaaakkmkkakamamcaacaqqsqqekgsesiwecewgawkgmawwqqueccqqm` | `AAAAKKMKKAKAMAMCAACAQQSQQEKGSESIWECEWGAWKGMAWWQQUECCQQMQUXPJ` | 0 QU |
| 30 | `aaaakuodsycakmcyweeezbmnwwyextxxxqrmnvxvqmfmkmlkwewadkm` | `AAAAKUODSYCAKMCYWEEEZBMNWWYEXTXXXQRMNVXVQMFMKMLKWEWADKMKGRSB` | 0 QU |
| 31 | `aaaamaaaewnsmmfaqwtsmaaaawrybifmuobosaaktavivatglmtvuab` | `AAAAMAAAEWNSMMFAQWTSMAAAAWRYBIFMUOBOSAAKTAVIVATGLMTVUABDVLNL` | 0 QU |
| 32 | `aaaamaaaieciqeaaaamaaaieciqeaaaamaaaieciqeaaaamaaaieciq` | `AAAAMAAAIECIQEAAAAMAAAIECIQEAAAAMAAAIECIQEAAAAMAAAIECIQEOZDH` | 0 QU |
| 33 | `aaaamaaamaaammhaaanamanacwtnamnfmonkmwnkhanjkanylojfhax` | `AAAAMAAAMAAAMMHAAANAMANACWTNAMNFMONKMWNKHANJKANYLOJFHAXFTZZG` | 0 QU |
| 34 | `aaaamaaamajammvaakckmkckdobvdwnvcuaqccrqdgdrbgdcaupeqgd` | `AAAAMAAAMAJAMMVAAKCKMKCKDOBVDWNVCUAQCCRQDGDRBGDCAUPEQGDASYUB` | 0 QU |
| 35 | `aaaamaacawalcuaaaamaacawalcuaaaamaacawalcuaaaamaacawalc` | `AAAAMAACAWALCUAAAAMAACAWALCUAAAAMAACAWALCUAAAAMAACAWALCUURPI` | 0 QU |
| 36 | `aaaamaaggeigeeaaaamaaggeigeeaaaamaaggeigeeaaaamaaggeige` | `AAAAMAAGGEIGEEAAAAMAAGGEIGEEAAAAMAAGGEIGEEAAAAMAAGGEIGEESZPE` | 0 QU |
| 37 | `aaaamaagzhjqqsaaaamaagzhjqqsaaaamaagzhjqqsaaaamaagzhjqq` | `AAAAMAAGZHJQQSAAAAMAAGZHJQQSAAAAMAAGZHJQQSAAAAMAAGZHJQQSHLEC` | 0 QU |
| 38 | `aaaamaajxxmaacaaaamaajxxmaacaaaamaajxxmaacaaaamaajxxmaa` | `AAAAMAAJXXMAACAAAAMAAJXXMAACAAAAMAAJXXMAACAAAAMAAJXXMAACWJQE` | 0 QU |
| 39 | `aaaamaammmmcgcaaaamaammmmcgcaaaamaammmmcgcaaaamaammmmcg` | `AAAAMAAMMMMCGCAAAAMAAMMMMCGCAAAAMAAMMMMCGCAAAAMAAMMMMCGCDJBJ` | 0 QU |
| 40 | `aaaamaawalcuacaaaamaawalcuacaaaamaawalcuacaaaamaawalcua` | `AAAAMAAWALCUACAAAAMAAWALCUACAAAAMAAWALCUACAAAAMAAWALCUACKONF` | 0 QU |
| 41 | `aaaauwnpwzdvdpaaaauwnpwzdvdpaaaauwnpwzdvdpaaaauwnpwzdvd` | `AAAAUWNPWZDVDPAAAAUWNPWZDVDPAAAAUWNPWZDVDPAAAAUWNPWZDVDPOOVG` | 0 QU |
| 42 | `aaaauwnwmenauukuyelaguvxlwrriimiukiknijmfwviisjymsjlngb` | `AAAAUWNWMENAUUKUYELAGUVXLWRRIIMIUKIKNIJMFWVIISJYMSJLNGBLQRWF` | 0 QU |
| 43 | `aaaauwtrxbzxvvaaaauwtrxbzxvvaaaauwtrxbzxvvaaaauwtrxbzxv` | `AAAAUWTRXBZXVVAAAAUWTRXBZXVVAAAAUWTRXBZXVVAAAAUWTRXBZXVVOAGM` | 0 QU |
| 44 | `aaaawrybifmuobosaaktavivatglmtvuabdxsxffffbaeaamaaaqede` | `AAAAWRYBIFMUOBOSAAKTAVIVATGLMTVUABDXSXFFFFBAEAAMAAAQEDEMQSZE` | 0 QU |
| 45 | `aaaawrycnjxjzgaaaawrycnjxjzgaaaawrycnjxjzgaaaawrycnjxjz` | `AAAAWRYCNJXJZGAAAAWRYCNJXJZGAAAAWRYCNJXJZGAAAAWRYCNJXJZGVGOO` | 0 QU |
| 46 | `aaaawwpnpwzdvdaaaawwpnpwzdvdaaaawwpnpwzdvdaaaawwpnpwzdv` | `AAAAWWPNPWZDVDAAAAWWPNPWZDVDAAAAWWPNPWZDVDAAAAWWPNPWZDVDOSQH` | 0 QU |
| 47 | `aaaaywrlaebhiepesefaeejreqtremjchoffvmjnvfvpaeaaaaaaeel` | `AAAAYWRLAEBHIEPESEFAEEJREQTREMJCHOFFVMJNVFVPAEAAAAAAEELEUNSL` | 0 QU |
| 48 | `aaaaywrxbzxvvtaaaaywrxbzxvvtaaaaywrxbzxvvtaaaaywrxbzxvv` | `AAAAYWRXBZXVVTAAAAYWRXBZXVVTAAAAYWRXBZXVVTAAAAYWRXBZXVVTKABG` | 0 QU |
| 49 | `aaaburknwrnkexesgxczelvbstrzcjrvcfhnfbvvpvdyeyaaaaacefe` | `AAABURKNWRNKEXESGXCZELVBSTRZCJRVCFHNFBVVPVDYEYAAAAACEFEMBKWO` | 0 QU |
| 50 | `aaaburkyjtvcqcaaaburkyjtvcqcaaaburkyjtvcqcaaaburkyjtvcq` | `AAABURKYJTVCQCAAABURKYJTVCQCAAABURKYJTVCQCAAABURKYJTVCQCYVCF` | 0 QU |
| 51 | `aaacaccsacamamcaacaccccuaccsgmisecaagciswuaochnuaccxhsf` | `AAACACCSACAMAMCAACACCCCUACCSGMISECAAGCISWUAOCHNUACCXHSFUQAKI` | 0 QU |
| 52 | `aaacefeoukkcakaaacefeoukkcakaaacefeoukkcakaaacefeoukkca` | `AAACEFEOUKKCAKAAACEFEOUKKCAKAAACEFEOUKKCAKAAACEFEOUKKCAKZBWE` | 0 QU |
| 53 | `aaacgccsycacaccaacaccccuacckamaaaaacaccsacamamcaacacccc` | `AAACGCCSYCACACCAACACCCCUACCKAMAAAAACACCSACAMAMCAACACCCCUXXGL` | 0 QU |
| 54 | `aaacgccsycageccaacaggccuacckamammmmcaccemommamcaacacccc` | `AAACGCCSYCAGECCAACAGGCCUACCKAMAMMMMCACCEMOMMAMCAACACCCCULGVG` | 0 QU |
| 55 | `aaacwnsqzzmnuuaaacwnsqzzmnuuaaacwnsqzzmnuuaaacwnsqzzmnu` | `AAACWNSQZZMNUUAAACWNSQZZMNUUAAACWNSQZZMNUUAAACWNSQZZMNUUPOFC` | 0 QU |
| 56 | `aaacwqsqsayaucaaacwqsqsayaucaaacwqsqsayaucaaacwqsqsayau` | `AAACWQSQSAYAUCAAACWQSQSAYAUCAAACWQSQSAYAUCAAACWQSQSAYAUCHHAD` | 0 QU |
| 57 | `aaacwqsynivjweaaacwqsynivjweaaacwqsynivjweaaacwqsynivjw` | `AAACWQSYNIVJWEAAACWQSYNIVJWEAAACWQSYNIVJWEAAACWQSYNIVJWETTTN` | 0 QU |
| 58 | `aaacwxseemsquzqcshshurwtidguchcqqlaugncaqrsdebcxyrqnsnf` | `AAACWXSEEMSQUZQCSHSHURWTIDGUCHCQQLAUGNCAQRSDEBCXYRQNSNFNIPQL` | 0 QU |
| 59 | `aaacwxsuuyucbqaaacwxsuuyucbqaaacwxsuuyucbqaaacwxsuuyucb` | `AAACWXSUUYUCBQAAACWXSUUYUCBQAAACWXSUUYUCBQAAACWXSUUYUCBQHIGM` | 0 QU |
| 60 | `aaadaoebtrebqbobylobpxlxhrubpkuveguryhkvvhghvtctvhkvvfv` | `AAADAOEBTREBQBOBYLOBPXLXHRUBPKUVEGURYHKVVHGHVTCTVHKVVFVTAGDB` | 0 QU |
| 61 | `aaadaoeqgwwuayaaadaoeqgwwuayaaadaoeqgwwuayaaadaoeqgwwua` | `AAADAOEQGWWUAYAAADAOEQGWWUAYAAADAOEQGWWUAYAAADAOEQGWWUAYFXLG` | 0 QU |
| 62 | `aaaeciqmuovkvvsacaksvkugusolsxwwyemzzlymyopvxxxxhbnnpvx` | `AAAECIQMUOVKVVSACAKSVKUGUSOLSXWWYEMZZLYMYOPVXXXXHBNNPVXYZFXF` | 0 QU |
| 63 | `aaaeelebsqvwuyaaaeelebsqvwuyaaaeelebsqvwuyaaaeelebsqvwu` | `AAAEELEBSQVWUYAAAEELEBSQVWUYAAAEELEBSQVWUYAAAEELEBSQVWUYWUJE` | 0 QU |
| 64 | `aaaeezeebsqvwuaaaeezeebsqvwuaaaeezeebsqvwuaaaeezeebsqvw` | `AAAEEZEEBSQVWUAAAEEZEEBSQVWUAAAEEZEEBSQVWUAAAEEZEEBSQVWUUDMB` | 0 QU |
| 65 | `aaaesssayaucqqaaaesssayaucqqaaaesssayaucqqaaaesssayaucq` | `AAAESSSAYAUCQQAAAESSSAYAUCQQAAAESSSAYAUCQQAAAESSSAYAUCQQCJJG` | 0 QU |
| 66 | `aaaewamanayeyaaaaaywrlaebhiepesefaeejreqtremjchoffvmjnv` | `AAAEWAMANAYEYAAAAAYWRLAEBHIEPESEFAEEJREQTREMJCHOFFVMJNVFXVVC` | 0 QU |
| 67 | `aaaewampwikgcgaaaewampwikgcgaaaewampwikgcgaaaewampwikgc` | `AAAEWAMPWIKGCGAAAEWAMPWIKGCGAAAEWAMPWIKGCGAAAEWAMPWIKGCGXBZA` | 0 QU |
| 68 | `aaaewmssuaaizfaaaewmssuaaizfaaaewmssuaaizfaaaewmssuaaiz` | `AAAEWMSSUAAIZFAAAEWMSSUAAIZFAAAEWMSSUAAIZFAAAEWMSSUAAIZFRKFI` | 0 QU |
| 69 | `aaaewnsmmfaqwtsmaaaawrybifmuobosaaktavivatglmtvuabdxsxf` | `AAAEWNSMMFAQWTSMAAAAWRYBIFMUOBOSAAKTAVIVATGLMTVUABDXSXFFAWID` | 0 QU |
| 70 | `aaaewnsuaaizfuaaaewnsuaaizfuaaaewnsuaaizfuaaaewnsuaaizf` | `AAAEWNSUAAIZFUAAAEWNSUAAIZFUAAAEWNSUAAIZFUAAAEWNSUAAIZFUSBHB` | 0 QU |
| 71 | `aaagkccaacakqkkkakakgmaaaaakkmkkakamamcaacaqqsqqekgsesi` | `AAAGKCCAACAKQKKKAKAKGMAAAAAKKMKKAKAMAMCAACAQQSQQEKGSESIWLWRB` | 0 QU |
| 72 | `aaagwiwuawaaakaaagwiwuawaaakaaagwiwuawaaakaaagwiwuawaaa` | `AAAGWIWUAWAAAKAAAGWIWUAWAAAKAAAGWIWUAWAAAKAAAGWIWUAWAAAKCSSE` | 0 QU |
| 73 | `aaaiwnwwuawaaaaaaiwnwwuawaaaaaaiwnwwuawaaaaaaiwnwwuawaa` | `AAAIWNWWUAWAAAAAAIWNWWUAWAAAAAAIWNWWUAWAAAAAAIWNWWUAWAAAXVKJ` | 0 QU |
| 74 | `aaajapwtpjebnuwtreebmxcxxxwtxqaqoqcqciwnsqcncswjgaajaaw` | `AAAJAPWTPJEBNUWTREEBMXCXXXWTXQAQOQCQCIWNSQCNCSWJGAAJAAWTCHOK` | 0 QU |
| 75 | `aaajapwuezzodyaaajapwuezzodyaaajapwuezzodyaaajapwuezzod` | `AAAJAPWUEZZODYAAAJAPWUEZZODYAAAJAPWUEZZODYAAAJAPWUEZZODYTFBO` | 0 QU |
| 76 | `aaakaceyzsnaaswpvrxhvpipdjngnpjgugbosowtovimiqcjvrrfhhv` | `AAAKACEYZSNAASWPVRXHVPIPDJNGNPJGUGBOSOWTOVIMIQCJVRRFHHVJBDLC` | 0 QU |
| 77 | `aaakayammmayyyykayacutqkmfaqieeqsqguutiqwpsusjsqeiohevp` | `AAAKAYAMMMAYYYYKAYACUTQKMFAQIEEQSQGUUTIQWPSUSJSQEIOHEVPPRQJI` | 0 QU |
| 78 | `aaakayayaucqquaaakayayaucqquaaakayayaucqquaaakayayaucqq` | `AAAKAYAYAUCQQUAAAKAYAYAUCQQUAAAKAYAYAUCQQUAAAKAYAYAUCQQUHINL` | 0 QU |
| 79 | `aaakaztsisqgebvwwsegizzwmqmnvrvdebxpljxxwabcffjswowijno` | `AAAKAZTSISQGEBVWWSEGIZZWMQMNVRVDEBXPLJXXWABCFFJSWOWIJNOQKLMC` | 0 QU |
| 80 | `aaakcwcqwswwbdaaakcwcqwswwbdaaakcwcqwswwbdaaakcwcqwswwb` | `AAAKCWCQWSWWBDAAAKCWCQWSWWBDAAAKCWCQWSWWBDAAAKCWCQWSWWBDPQSN` | 0 QU |
| 81 | `aaakkmkkakamamcaacaqqsqqekgsesiwecewgawkgmawwqqueccqqmq` | `AAAKKMKKAKAMAMCAACAQQSQQEKGSESIWECEWGAWKGMAWWQQUECCQQMQWHEJE` | 0 QU |
| 82 | `aaakuodsycakmcyweeezbmnwwyextxxxqrmnvxvqmfmkmlkwewadkmk` | `AAAKUODSYCAKMCYWEEEZBMNWWYEXTXXXQRMNVXVQMFMKMLKWEWADKMKWIKZC` | 0 QU |
| 83 | `aaamaaaaaaacacaaamaaaaaaacacaaamaaaaaaacacaaamaaaaaaaca` | `AAAMAAAAAAACACAAAMAAAAAAACACAAAMAAAAAAACACAAAMAAAAAAACACHGUB` | 0 QU |
| 84 | `aaamaaaacgccsyaaamaaaacgccsyaaamaaaacgccsyaaamaaaacgccs` | `AAAMAAAACGCCSYAAAMAAAACGCCSYAAAMAAAACGCCSYAAAMAAAACGCCSYJRWA` | 0 QU |
| 85 | `aaamaaaaggcgaeaaamaaaaggcgaeaaamaaaaggcgaeaaamaaaaggcga` | `AAAMAAAAGGCGAEAAAMAAAAGGCGAEAAAMAAAAGGCGAEAAAMAAAAGGCGAEWCOM` | 0 QU |
| 86 | `aaamaaaaizfusuaaamaaaaizfusuaaamaaaaizfusuaaamaaaaizfus` | `AAAMAAAAIZFUSUAAAMAAAAIZFUSUAAAMAAAAIZFUSUAAAMAAAAIZFUSUHVPJ` | 0 QU |
| 87 | `aaamaaacaccccuaaamaaacaccccuaaamaaacaccccuaaamaaacacccc` | `AAAMAAACACCCCUAAAMAAACACCCCUAAAMAAACACCCCUAAAMAAACACCCCUEWLK` | 0 QU |
| 88 | `aaamaaaccccuacaaamaaaccccuacaaamaaaccccuacaaamaaaccccua` | `AAAMAAACCCCUACAAAMAAACCCCUACAAAMAAACCCCUACAAAMAAACCCCUACGGCJ` | 0 QU |
| 89 | `aaamaaaewnsmmfaqwtsmaaaawrybifmuobosaaktavivatglmtvuabd` | `AAAMAAAEWNSMMFAQWTSMAAAAWRYBIFMUOBOSAAKTAVIVATGLMTVUABDXKOJH` | 0 QU |
| 90 | `aaamaaamaaammhaaanamanacwtnamnfmonkmwnkhanjkanylojfhaxf` | `AAAMAAAMAAAMMHAAANAMANACWTNAMNFMONKMWNKHANJKANYLOJFHAXFZGPJC` | 0 QU |
| 91 | `aaamaaamajammvaakckmkckdobvdwnvcuaqccrqdgdrbgdcaupeqgda` | `AAAMAAAMAJAMMVAAKCKMKCKDOBVDWNVCUAQCCRQDGDRBGDCAUPEQGDAFCZXM` | 0 QU |
| 92 | `aaamaaamamcaacaaamaaamamcaacaaamaaamamcaacaaamaaamamcaa` | `AAAMAAAMAMCAACAAAMAAAMAMCAACAAAMAAAMAMCAACAAAMAAAMAMCAACCWGA` | 0 QU |
| 93 | `aaamaaammhaaanamanacwtnamnfmonkmwnkhanjkanylojfhaxfzfzp` | `AAAMAAAMMHAAANAMANACWTNAMNFMONKMWNKHANJKANYLOJFHAXFZFZPBJJPL` | 0 QU |
| 94 | `aaamaaaqqsqqekaaamaaaqqsqqekaaamaaaqqsqqekaaamaaaqqsqqe` | `AAAMAAAQQSQQEKAAAMAAAQQSQQEKAAAMAAAQQSQQEKAAAMAAAQQSQQEKTRXI` | 0 QU |
| 95 | `aaamajammvaakckmkckdobvdwnvcuaqccrqdgdrbgdcaupeqgdafefv` | `AAAMAJAMMVAAKCKMKCKDOBVDWNVCUAQCCRQDGDRBGDCAUPEQGDAFEFVHDKJI` | 0 QU |
| 96 | `aaamajasssausuaaamajasssausuaaamajasssausuaaamajasssaus` | `AAAMAJASSSAUSUAAAMAJASSSAUSUAAAMAJASSSAUSUAAAMAJASSSAUSUELXB` | 0 QU |
| 97 | `aaameaaacigkuaaaameaaacigkuaaaameaaacigkuaaaameaaacigku` | `AAAMEAAACIGKUAAAAMEAAACIGKUAAAAMEAAACIGKUAAAAMEAAACIGKUAWHRF` | 0 QU |
| 98 | `aaamebawaaakacaaamebawaaakacaaamebawaaakacaaamebawaaaka` | `AAAMEBAWAAAKACAAAMEBAWAAAKACAAAMEBAWAAAKACAAAMEBAWAAAKACDISD` | 0 QU |
| 99 | `aaametapwytwwuaaametapwytwwuaaametapwytwwuaaametapwytww` | `AAAMETAPWYTWWUAAAMETAPWYTWWUAAAMETAPWYTWWUAAAMETAPWYTWWUVQEA` | 0 QU |
| 100 | `aaammhaaanamanacwtnamnfmonkmwnkhanjkanylojfhaxfzfzpbfxb` | `AAAMMHAAANAMANACWTNAMNFMONKMWNKHANJKANYLOJFHAXFZFZPBFXBAPFRN` | 0 QU |

---

## Total

**100 seeds and identities** documented above.

These are a sample from the comprehensive scan. Total on-chain identities found: 22,522+ (scan in progress).

## Source

Extracted from: `outputs/derived/onchain_validation_checkpoint.json`
Date: 2025-11-22
Scan progress: 95.9% (22,801 / 23,765 identities checked)