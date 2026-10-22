from .astrology import NAKSHATRAS, VIMSHOTTARI_LORDS, _positions, _utc_and_jd
from .config import Settings
from .schemas import NakshatraRequest
DEITIES=["Ashwini Kumara","Yama","Agni","Brahma","Soma","Rudra","Aditi","Brihaspati","Naga","Pitrs","Bhaga","Aryaman","Savitar","Tvastar","Vayu","Indra-Agni","Vishvakarma","Mitra","Indra","Nirriti","Apah","Vishvedevas","Vishnu","Vasus","Varuna","Aja Ekapada","Ahir Budhnya"]
def nakshatra_studio(request:NakshatraRequest,settings:Settings)->dict:
 _,jd=_utc_and_jd(request,settings); span=360/27; rows=[]
 for p in _positions(jd,True):
  i=min(26,int(p.longitude/span)); rows.append({"planet":p.name,"sign":p.sign,"nakshatra":NAKSHATRAS[i],"pada":min(4,int((p.longitude%span)/(span/4))+1),"lord":VIMSHOTTARI_LORDS[i % len(VIMSHOTTARI_LORDS)],"deity":DEITIES[i]})
 return {"system":"Lahiri sidereal Nakshatra","moon":next(x for x in rows if x["planet"]=="Moon"),"planets":rows,"notice":"Nakshatra and Pada values are calculated from sidereal longitudes; traditional labels are reference data, not guaranteed outcomes."}
