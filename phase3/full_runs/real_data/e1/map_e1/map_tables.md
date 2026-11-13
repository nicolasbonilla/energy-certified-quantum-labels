# Map on the real energies: main tables (written by run_map.py)

Declaration SHA-256: `6dfbc5681a7b4708ba790e1dd3139d8efdcccb9ced24e5ab2ce4b5a7a209ffaa`

## J* and counts out of 45 (per label and size)

| n | label | J*_s | cert_s | notcert_s | gray_s | J*_exact | cert exact | J*_exact (ref-free) | cert exact (ref-free) | not certified (explicit) | gray |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 57 | m_s | 3.2 | 29 | 16 | 0 | 3.5 | 26 | 3.5 | 26 | 16 | 3 |
| 57 | Czz_bar | 3.2 | 29 | 16 | 0 | 3.4 | 27 | 3.4 | 27 | 16 | 2 |
| 57 | C2_bar | 4.0 | 21 | 24 | 0 | - | 0 | - | 0 | 24 | 21 |
| 57 | Z_bulk | 6.0 | 1 | 43 | 1 | - | 0 | - | 0 | 42 | 3 |
| 57 | Z_boundary | - | 0 | 45 | 0 | - | 0 | - | 0 | 44 | 1 |
| 57 | Czz_edge | 6.0 | 1 | 43 | 1 | - | 0 | - | 0 | 42 | 3 |
| 57 | Z_loop | - | 0 | 45 | 0 | - | 0 | - | 0 | 45 | 0 |
| 115 | m_s | 3.1 | 30 | 15 | 0 | 4.0 | 21 | 4.0 | 21 | 15 | 9 |
| 115 | Czz_bar | 3.1 | 30 | 15 | 0 | 4.0 | 21 | 4.0 | 21 | 15 | 9 |
| 115 | C2_bar | 3.8 | 23 | 22 | 0 | - | 0 | - | 0 | 22 | 23 |
| 115 | Z_bulk | - | 0 | 1 | 0 | - | 0 | - | 0 | 23 | 22 |
| 115 | Z_boundary | - | 0 | 0 | 0 | - | 0 | - | 0 | 15 | 30 |
| 115 | Czz_edge | - | 0 | 0 | 0 | - | 0 | - | 0 | 22 | 23 |
| 115 | Z_loop | - | 0 | 0 | 0 | - | 0 | - | 0 | 28 | 17 |

## Predicted from the figures versus obtained from the data

Relations over the stored rows: confirmed 152, no_real_data 6, resolved 13. Contradicted rows: 0. Confirmed by the data (rule of Sec. 3): **True**.

| n | label | stored J* | J*_s | within 0.1 |
|---|---|---|---|---|
| 57 | m_s | 3.2 | 3.2 | True |
| 57 | Czz_bar | 3.2 | 3.2 | True |
| 57 | C2_bar | 4.0 | 4.0 | True |
| 57 | Z_bulk | 6.0 | 6.0 | True |
| 57 | Czz_edge | 6.0 | 6.0 | True |
| 115 | m_s | 3.1 | 3.1 | True |
| 115 | Czz_bar | 3.1 | 3.1 | True |
| 115 | C2_bar | 3.8 | 3.8 | True |

| n | Jz | label | predicted | like-for-like at E_real | relation | status of Sec. 2 |
|---|---|---|---|---|---|---|
| 19 | 1.6 | m_s | NOT_CERTIFIED | None | no_real_data | None |
| 19 | 4.0 | m_s | CERTIFIED | None | no_real_data | None |
| 19 | 1.6 | Czz_bar | NOT_CERTIFIED | None | no_real_data | None |
| 19 | 4.0 | Czz_bar | CERTIFIED | None | no_real_data | None |
| 19 | 1.6 | Z_bulk | NOT_CERTIFIED | None | no_real_data | None |
| 19 | 4.0 | Z_bulk | NOT_CERTIFIED | None | no_real_data | None |
| 57 | 1.1 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.2 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.3 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.4 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.6 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.8 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 2.0 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 2.5 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 3.0 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 3.2 | m_s | GRAY | CERTIFIED_s | resolved | GRAY |
| 57 | 3.3 | m_s | GRAY | CERTIFIED_s | resolved | GRAY |
| 57 | 3.4 | m_s | CERTIFIED | CERTIFIED_s | confirmed | GRAY |
| 57 | 3.6 | m_s | CERTIFIED | CERTIFIED_s | confirmed | CERTIFIED_EXACT |
| 57 | 4.0 | m_s | CERTIFIED | CERTIFIED_s | confirmed | CERTIFIED_EXACT |
| 57 | 4.5 | m_s | CERTIFIED | CERTIFIED_s | confirmed | CERTIFIED_EXACT |
| 57 | 5.0 | m_s | CERTIFIED | CERTIFIED_s | confirmed | CERTIFIED_EXACT |
| 57 | 5.5 | m_s | CERTIFIED | CERTIFIED_s | confirmed | CERTIFIED_EXACT |
| 57 | 6.0 | m_s | CERTIFIED | CERTIFIED_s | confirmed | CERTIFIED_EXACT |
| 57 | 1.1 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.2 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.3 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.4 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.6 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.8 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 2.0 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 2.5 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 3.0 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 3.2 | Czz_bar | GRAY | CERTIFIED_s | resolved | GRAY |
| 57 | 3.3 | Czz_bar | GRAY | CERTIFIED_s | resolved | GRAY |
| 57 | 3.4 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | CERTIFIED_EXACT |
| 57 | 3.6 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | CERTIFIED_EXACT |
| 57 | 4.0 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | CERTIFIED_EXACT |
| 57 | 4.5 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | CERTIFIED_EXACT |
| 57 | 5.0 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | CERTIFIED_EXACT |
| 57 | 5.5 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | CERTIFIED_EXACT |
| 57 | 6.0 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | CERTIFIED_EXACT |
| 57 | 1.1 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.2 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.3 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.4 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.6 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.8 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 2.0 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 2.5 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 3.0 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 3.3 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 3.6 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 4.0 | C2_bar | GRAY | CERTIFIED_s | resolved | GRAY |
| 57 | 4.5 | C2_bar | CERTIFIED | CERTIFIED_s | confirmed | GRAY |
| 57 | 5.0 | C2_bar | CERTIFIED | CERTIFIED_s | confirmed | GRAY |
| 57 | 5.5 | C2_bar | CERTIFIED | CERTIFIED_s | confirmed | GRAY |
| 57 | 6.0 | C2_bar | CERTIFIED | CERTIFIED_s | confirmed | GRAY |
| 57 | 1.1 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.2 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.3 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.4 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.6 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.8 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 2.0 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 2.5 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 3.0 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 3.3 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 3.6 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 4.0 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 4.5 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 5.0 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 5.5 | Z_bulk | GRAY | NOT_CERTIFIED_s | resolved | NOT_CERTIFIED |
| 57 | 6.0 | Z_bulk | GRAY | CERTIFIED_s | resolved | GRAY |
| 57 | 1.1 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.2 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.3 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.4 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.6 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.8 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 2.0 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 2.5 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 3.0 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 3.3 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 3.6 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 4.0 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 4.5 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 5.0 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 5.5 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 6.0 | Z_boundary | GRAY | NOT_CERTIFIED_s | resolved | GRAY |
| 57 | 1.1 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.2 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.3 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.4 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.6 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.8 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 2.0 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 2.5 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 3.0 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 3.3 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 3.6 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 4.0 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 4.5 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 5.0 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 5.5 | Czz_edge | GRAY | NOT_CERTIFIED_s | resolved | NOT_CERTIFIED |
| 57 | 6.0 | Czz_edge | GRAY | CERTIFIED_s | resolved | GRAY |
| 57 | 1.1 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.2 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.3 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.4 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.6 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 1.8 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 2.0 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 2.5 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 3.0 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 3.3 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 3.6 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 4.0 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 4.5 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 5.0 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 5.5 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 57 | 6.0 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 1.1 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 1.2 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 1.3 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 1.4 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 1.6 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 1.8 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 2.0 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 2.5 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 3.0 | m_s | GRAY | NOT_CERTIFIED_s | resolved | NOT_CERTIFIED |
| 115 | 3.3 | m_s | CERTIFIED | CERTIFIED_s | confirmed | GRAY |
| 115 | 3.6 | m_s | CERTIFIED | CERTIFIED_s | confirmed | GRAY |
| 115 | 4.0 | m_s | CERTIFIED | CERTIFIED_s | confirmed | CERTIFIED_EXACT |
| 115 | 4.5 | m_s | CERTIFIED | CERTIFIED_s | confirmed | CERTIFIED_EXACT |
| 115 | 5.0 | m_s | CERTIFIED | CERTIFIED_s | confirmed | CERTIFIED_EXACT |
| 115 | 5.5 | m_s | CERTIFIED | CERTIFIED_s | confirmed | CERTIFIED_EXACT |
| 115 | 6.0 | m_s | CERTIFIED | CERTIFIED_s | confirmed | CERTIFIED_EXACT |
| 115 | 1.1 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 1.2 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 1.3 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 1.4 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 1.6 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 1.8 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 2.0 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 2.5 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 3.0 | Czz_bar | GRAY | NOT_CERTIFIED_s | resolved | NOT_CERTIFIED |
| 115 | 3.3 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | GRAY |
| 115 | 3.6 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | GRAY |
| 115 | 4.0 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | CERTIFIED_EXACT |
| 115 | 4.5 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | CERTIFIED_EXACT |
| 115 | 5.0 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | CERTIFIED_EXACT |
| 115 | 5.5 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | CERTIFIED_EXACT |
| 115 | 6.0 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | CERTIFIED_EXACT |
| 115 | 1.1 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 1.2 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 1.3 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 1.4 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 1.6 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 1.8 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 2.0 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 2.5 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 3.0 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 3.3 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |
| 115 | 3.6 | C2_bar | GRAY | NOT_CERTIFIED_s | resolved | NOT_CERTIFIED |
| 115 | 4.0 | C2_bar | CERTIFIED | CERTIFIED_s | confirmed | GRAY |
| 115 | 4.5 | C2_bar | CERTIFIED | CERTIFIED_s | confirmed | GRAY |
| 115 | 5.0 | C2_bar | CERTIFIED | CERTIFIED_s | confirmed | GRAY |
| 115 | 5.5 | C2_bar | CERTIFIED | CERTIFIED_s | confirmed | GRAY |
| 115 | 6.0 | C2_bar | CERTIFIED | CERTIFIED_s | confirmed | GRAY |
| 115 | 4.0 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | NOT_CERTIFIED |

## Accuracy factors at the test couplings (Sec. 4)

| n | label | Jz | de_real | de*_in | de*_out | F_A | F_B |
|---|---|---|---|---|---|---|---|
| 57 | m_s | 1.1 | 0.021400 | 0.00005401 | 0.00004918 | 396.22 | 210.22 |
| 57 | m_s | 1.2 | 0.019759 | 0.00007350 | 0.00007074 | 268.83 | 154.48 |
| 57 | m_s | 1.3 | 0.018017 | 0.00009971 | 0.00009778 | 180.69 | 113.88 |
| 57 | m_s | 1.4 | 0.015424 | 0.00013244 | 0.00013142 | 116.47 | 85.74 |
| 57 | m_s | 1.5 | 0.012613 | 0.00020646 | 0.00017088 | 61.09 | 55.00 |
| 57 | m_s | headline | | | | more than 110 | more than 85 |
| 57 | Czz_bar | 1.1 | 0.021400 | 0.00015927 | 0.00015426 | 134.37 | 71.29 |
| 57 | Czz_bar | 1.2 | 0.019759 | 0.00018933 | 0.00018626 | 104.36 | 59.97 |
| 57 | Czz_bar | 1.3 | 0.018017 | 0.00022549 | 0.00022382 | 79.90 | 50.35 |
| 57 | Czz_bar | 1.4 | 0.015424 | 0.00026903 | 0.00026754 | 57.33 | 42.21 |
| 57 | Czz_bar | 1.5 | 0.012613 | 0.00032040 | 0.00031726 | 39.36 | 35.44 |
| 57 | Czz_bar | headline | | | | more than 57 | more than 42 |
| 115 | m_s | 1.1 | 0.022729 | 0.00015886 | 0.00000000 | 143.07 | 73.52 |
| 115 | m_s | 1.2 | 0.019683 | 0.00015799 | 0.00001710 | 124.58 | 73.93 |
| 115 | m_s | 1.3 | 0.017174 | 0.00017079 | 0.00007051 | 100.56 | 68.39 |
| 115 | m_s | 1.4 | 0.015418 | 0.00019410 | 0.00012679 | 79.43 | 60.18 |
| 115 | m_s | 1.5 | 0.015706 | 0.00026236 | 0.00017881 | 59.86 | 44.52 |
| 115 | m_s | headline | | | | more than 79 | more than 60 |
| 115 | Czz_bar | 1.1 | 0.022729 | 0.00026351 | 0.00005694 | 86.25 | 44.32 |
| 115 | Czz_bar | 1.2 | 0.019683 | 0.00026419 | 0.00012203 | 74.50 | 44.21 |
| 115 | Czz_bar | 1.3 | 0.017174 | 0.00028127 | 0.00018530 | 61.06 | 41.53 |
| 115 | Czz_bar | 1.4 | 0.015418 | 0.00031337 | 0.00024626 | 49.20 | 37.27 |
| 115 | Czz_bar | 1.5 | 0.015706 | 0.00033999 | 0.00030608 | 46.20 | 34.35 |
| 115 | Czz_bar | headline | | | | more than 49 | more than 37 |

## Filter (Sec. 6), over the 45 training labels

| n | label | rule | kept | largest miss kept | mean miss kept | largest miss dropped | dropped within tau/2 | dropped within tau | kept above tau/2 |
|---|---|---|---|---|---|---|---|---|---|
| 57 | m_s | exact | 26 | 0.1745 | 0.0815 | 1.6684 | 10 | 15 | 0 |
| 57 | m_s | exact_reference_free | 26 | 0.1745 | 0.0815 | 1.6684 | 10 | 15 | 0 |
| 57 | m_s | like_for_like | 29 | 0.2070 | 0.0931 | 1.6684 | 7 | 12 | 0 |
| 57 | m_s | exact_with_E1 | 26 | 0.1745 | 0.0815 | 1.6684 | 10 | 15 | 0 |
| 57 | Czz_bar | exact | 27 | 0.1608 | 0.0806 | 1.1699 | 10 | 16 | 0 |
| 57 | Czz_bar | exact_reference_free | 27 | 0.1608 | 0.0806 | 1.1699 | 10 | 16 | 0 |
| 57 | Czz_bar | like_for_like | 29 | 0.1868 | 0.0876 | 1.1699 | 8 | 14 | 0 |
| 57 | Czz_bar | exact_with_E1 | 27 | 0.1608 | 0.0806 | 1.1699 | 10 | 16 | 0 |
| 115 | m_s | exact | 21 | 0.0639 | 0.0358 | 1.5426 | 17 | 21 | 0 |
| 115 | m_s | exact_reference_free | 21 | 0.0639 | 0.0358 | 1.5426 | 17 | 21 | 0 |
| 115 | m_s | like_for_like | 30 | 0.1626 | 0.0600 | 1.5426 | 8 | 12 | 0 |
| 115 | m_s | exact_with_E1 | 27 | 0.1173 | 0.0491 | 1.5426 | 11 | 15 | 0 |
| 115 | Czz_bar | exact | 21 | 0.0589 | 0.0312 | 1.1113 | 18 | 23 | 0 |
| 115 | Czz_bar | exact_reference_free | 21 | 0.0589 | 0.0312 | 1.1113 | 18 | 23 | 0 |
| 115 | Czz_bar | like_for_like | 30 | 0.1398 | 0.0512 | 1.1113 | 9 | 14 | 0 |
| 115 | Czz_bar | exact_with_E1 | 25 | 0.0803 | 0.0378 | 1.1113 | 14 | 19 | 0 |

## Nested sets (Sec. 7), m_s, stored certificates only

- n = 57: |S| = 26, |S_3/4| = 23, |S_1/2| = 18, S_p = S_1_2 (18 couplings)
- n = 115: |S| = 21, |S_3/4| = 21, |S_1/2| = 10, S_p = S_3_4 (21 couplings)

S_sets.json SHA-256: `e82b32a79abdc43c4cce0480e7d0e542cc0fc40e5fe5757c959acb10e433f97c`

## Gates

- G1: pass on what could be checked; not complete
- G2_57: True
- G3_57: True
- G4_57: True
- G2_115: True
- G3_115: True
- G4_115: True
- G5a: True
- G5b: True
- G6a: pass on what could be checked; not complete
- G6b: True
- G7: True
