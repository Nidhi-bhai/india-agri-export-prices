# Product catalogue: what Nidhi Farms trades, mapped to public data series.
# hs: UN Comtrade HS6 codes (India exports). pooled=True means the HS code covers many products,
# so its unit value is NOT a product-specific price.
# agm: Agmarknet commodity ids (all-India average, Rs/quintal).
PRODUCTS = [
 dict(slug="moringa-leaf-powder", name="Moringa leaf powder", hs=["121190"], pooled=True, agm=[], desk="moringa"),
 dict(slug="ashwagandha-root-powder", name="Ashwagandha root powder", hs=["121190"], pooled=True, agm=[(372,"Ashwagandha (raw root)")], desk="ashwagandha"),
 dict(slug="neem-leaf-powder", name="Neem leaf powder", hs=["121190"], pooled=True, agm=[(109,"Neem seed (related raw material, not leaf)")], desk=None),
 dict(slug="curry-leaf-powder", name="Curry leaf powder", hs=["121190"], pooled=True, agm=[(415,"Curry leaf (fresh)")], desk="curry"),
 dict(slug="indigo-leaf-powder", name="Indigo leaf powder", hs=["320300"], pooled=True, agm=[], desk=None),
 dict(slug="wheatgrass-powder", name="Wheatgrass powder", hs=[], pooled=False, agm=[], desk=None),
 dict(slug="turmeric", name="Turmeric (finger and powder)", hs=["091030"], pooled=False, agm=[(35,"Turmeric"),(610,"Turmeric powder")], desk=None),
 dict(slug="jaggery-powder", name="Jaggery powder", hs=["170113"], pooled=True, agm=[(61,"Gur (jaggery)")], desk="jaggery_powder"),
 dict(slug="ragi-finger-millet", name="Ragi (finger millet)", hs=["100829"], pooled=True, agm=[(30,"Ragi (finger millet)")], desk="ragi"),
 dict(slug="bajra-pearl-millet", name="Bajra (pearl millet)", hs=["100829"], pooled=True, agm=[(28,"Bajra (pearl millet)")], desk="bajra"),
 dict(slug="foxtail-millet", name="Foxtail millet", hs=["100829"], pooled=True, agm=[(104,"Foxtail millet (navane)")], desk="small_millets"),
 dict(slug="small-millets", name="Kodo, little, proso, barnyard and browntop millets", hs=["100829"], pooled=True,
      agm=[(101,"Kodo millet (varagu)"),(498,"Little millet"),(511,"Proso millet"),(461,"Barnyard millet"),(465,"Browntop millet")], desk="small_millets"),
 dict(slug="khapli-wheat", name="Khapli (emmer) wheat and atta", hs=["100199"], pooled=True, agm=[(1,"Wheat, common (reference only, not khapli)")], desk="khapli"),
 dict(slug="groundnut-oil", name="Cold-pressed groundnut oil", hs=["150810","150890"], pooled=True, agm=[(221,"Groundnut oil"),(10,"Groundnut (seed)")], desk=None),
 dict(slug="coconut-oil", name="Cold-pressed coconut oil", hs=["151311","151319"], pooled=True, agm=[(220,"Coconut oil"),(111,"Copra")], desk="coconut_oil"),
 dict(slug="karanja-oil", name="Karanja (pongamia) oil", hs=["151590"], pooled=True, agm=[(368,"Karanja seeds")], desk=None),
 dict(slug="moringa-seed-oil", name="Moringa seed oil", hs=["151590"], pooled=True, agm=[], desk=None),
 dict(slug="vetiver-root", name="Vetiver (khus) root, dried", hs=["121190"], pooled=True, agm=[], desk="vetiver"),
]
HS_DESC = {
 "121190":"Plants and parts of plants used in pharmacy/perfumery, n.e.s. (pooled: moringa, ashwagandha, neem, curry leaf, vetiver and hundreds of other herbs)",
 "320300":"Colouring matter of vegetable origin (pooled: natural indigo and other plant dyes)",
 "091030":"Turmeric (curcuma)",
 "170113":"Cane sugar, non-centrifugal, solid, without flavouring (jaggery/gur; blocks and powder pooled)",
 "100829":"Millet, other than seed for sowing (pooled: bajra, ragi, foxtail and other millets)",
 "100199":"Wheat and meslin, other than durum and seed (pooled: khapli/emmer with common wheat)",
 "150810":"Groundnut oil, crude",
 "150890":"Groundnut oil, other than crude (refined, filtered, cold-pressed pooled)",
 "151311":"Coconut (copra) oil, crude",
 "151319":"Coconut (copra) oil, other than crude",
 "151590":"Other fixed vegetable fats and oils (pooled: karanja, moringa seed and many others)",
}
