# -*- coding: utf-8 -*-
"""
De huse der bygges.

Hvert hus er et navn og de maal der afviger fra skelet.STANDARD. Alle
input-maal kan overskrives - se STANDARD i skelet.py for listen.

Laengden SKAL gaa op i husets modul. Bredden udledes af gavlrem_l og er
fri - se kontrollér() i skelet.py.
"""

HUSE = [
    {
        "navn": "6000x3600",
        "titel": "Standardhuset",
        "maal": {},
    },
    {
        "navn": "7200x4200",
        "titel": "Stor - 7,2 x 4,2 m",
        # 7,2 m kan ikke daekkes af to 3600-braedder pr. raekke: naermeste
        # stroe til midten giver et stykke paa 4132. Derfor 4200 her.
        "maal": {"laengde": 7200, "gavlrem_l": 4020, "braet_l_max": 4200},
    },
    {
        "navn": "4800x3000",
        "titel": "Lille - 4,8 x 3,0 m",
        "maal": {"laengde": 4800, "gavlrem_l": 2820},
    },
]
