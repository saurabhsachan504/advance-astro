"use client";

import { useEffect, useState } from "react";

type Language = "en" | "hi";
const STORAGE_KEY = "veda-language";

// Interface strings are translated; calculated chart values and proper nouns stay
// unchanged so the output remains easy to cross-check with source calculations.
const HINDI: Record<string, string> = {
  "Birth chart": "जन्म कुंडली", "Four systems": "चार प्रणालियाँ", "Advanced": "उन्नत", "Privacy": "गोपनीयता", "Engine online": "इंजन ऑनलाइन", "Menu": "मेनू", "Close": "बंद करें", "New": "नया",
  "PRIVATE ASTRO INTELLIGENCE": "निजी ज्योतिष बुद्धिमत्ता", "Your universe,": "आपका ब्रह्मांड,", "rendered precisely.": "सटीक रूप से प्रस्तुत।", "One private observatory for Vedic, KP, numerology and Western chart mathematics.": "वैदिक, KP, अंकशास्त्र और पश्चिमी चार्ट गणित के लिए एक निजी ज्योतिष मंच।", "Exact ephemeris": "सटीक एफेमेरिस", "Local-first data": "लोकल-फर्स्ट डेटा", "A PERSONAL COSMOS": "आपका निजी ब्रह्मांड", "LIVE CHART": "लाइव चार्ट",
  "CREATE CHART": "कुंडली बनाएं", "Find your celestial": "अपनी खगोलीय", "blueprint.": "रूपरेखा जानें।", "Birth date & time": "जन्म तिथि और समय", "Birth time": "जन्म समय", "Latitude": "अक्षांश", "Longitude": "देशांतर", "IANA time zone": "IANA समय क्षेत्र", "Time zone": "समय क्षेत्र", "Reveal four systems": "चार प्रणालियाँ देखें", "Calculating four systems...": "चार प्रणालियों की गणना हो रही है...", "Your birth data stays in your private workspace.": "आपका जन्म डेटा आपके निजी कार्यक्षेत्र में सुरक्षित रहता है।",
  "DUAL INSIGHT": "दोहरी अंतर्दृष्टि", "One chart.": "एक कुंडली।", "Many signals.": "अनेक संकेत।", "Pair chart mathematics with optional palm or face symbolism for a layered spiritual reading.": "गहन आध्यात्मिक अध्ययन के लिए कुंडली गणित के साथ वैकल्पिक हस्तरेखा या चेहरे के संकेत जोड़ें।", "Palm": "हथेली", "Face": "चेहरा", "Browse": "चुनें", "Analyse palm": "हथेली का विश्लेषण", "Analyse face": "चेहरे का विश्लेषण", "Reading image...": "छवि पढ़ी जा रही है...", "Consent required. Raw photos are not stored.": "सहमति आवश्यक है। मूल फोटो संग्रहीत नहीं होतीं।",
  "WHEN YOU ARE READY": "जब आप तैयार हों", "Your chart will unfold here.": "आपकी कुंडली यहाँ दिखाई देगी।", "Enter the moment and place of birth above. Four mathematical perspectives will be calculated locally.": "ऊपर जन्म का समय और स्थान भरें। चार गणितीय दृष्टिकोण स्थानीय रूप से गणना किए जाएंगे।", "PRIVATE BY DESIGN": "डिज़ाइन से निजी", "Your story does not leave your orbit.": "आपकी जानकारी आपके निजी दायरे से बाहर नहीं जाती।", "Privacy architecture": "गोपनीयता संरचना", "Astrology is spiritual guidance, not medical, legal or financial advice.": "ज्योतिष आध्यात्मिक मार्गदर्शन है, चिकित्सा, कानूनी या वित्तीय सलाह नहीं।",
  "ADVANCED TOOLKIT / LOCAL MATH": "उन्नत टूलकिट / लोकल गणना", "Classic view": "क्लासिक दृश्य", "Pro view": "प्रो दृश्य", "Light": "लाइट", "Dark": "डार्क", "YOUR PRIVATE ASTROLOGY LAB": "आपकी निजी ज्योतिष प्रयोगशाला", "Traceable calculations for timing, chart structure and relationship comparisons.": "समय, कुंडली संरचना और संबंध तुलना के लिए पारदर्शी गणनाएँ।", "Go deeper than": "जन्म कुंडली से", "a birth chart.": "आगे जानें।",
  "PRIVATE FAMILY WORKSPACE": "निजी पारिवारिक कार्यक्षेत्र", "Save birth profiles locally.": "जन्म प्रोफाइल स्थानीय रूप से सहेजें।", "Profiles stay only in this browser until you choose to use them.": "जब तक आप चाहें, प्रोफाइल केवल इसी ब्राउज़र में रहते हैं।", "Saved profile": "सहेजा गया प्रोफाइल", "New profile": "नया प्रोफाइल", "Profile name": "प्रोफाइल नाम", "Save profile": "प्रोफाइल सहेजें", "Delete": "हटाएं",
  "Dasha timeline": "दशा समयरेखा", "Maha and Antardasha periods": "महादशा और अंतर्दशा अवधि", "Kundli studio": "कुंडली स्टूडियो", "D1, D9 and D10 chart data": "D1, D9 और D10 कुंडली डेटा", "Panchang calendar": "पंचांग कैलेंडर", "Monthly Panchang, Rahu Kaal and Muhurat windows": "मासिक पंचांग, राहु काल और मुहूर्त समय", "Muhurat planner": "मुहूर्त योजनाकार", "Event time-window baseline": "कार्य के लिए समय-खंड आधार", "Personal Gochar": "व्यक्तिगत गोचर", "Daily transits, retrogrades and sign changes": "दैनिक गोचर, वक्री ग्रह और राशि परिवर्तन", "Ashtakavarga lab": "अष्टकवर्ग प्रयोगशाला", "Bhinna, Sarva and bala components": "भिन्न, सर्व और बल घटक", "Prashna Kundli": "प्रश्न कुंडली", "Question-time chart facts": "प्रश्न समय की कुंडली जानकारी", "Matchmaking": "मिलान", "Ashtakoota, KP and synastry": "अष्टकूट, KP और सिनैस्ट्री", "Jaimini Studio": "जैमिनी स्टूडियो", "Karakas, Arudha, aspects and Chara Dasha": "कारक, अरूढ़, दृष्टि और चर दशा", "KP Astrology Studio": "KP ज्योतिष स्टूडियो", "Cusps, star-sub lords and timing rule cards": "कस्प, नक्षत्र-सब लॉर्ड और समय नियम कार्ड", "Varshaphal Studio": "वर्षफल स्टूडियो", "Tajika return, Muntha and Mudda Dasha": "ताजिक वर्ष प्रवेश, मुंथा और मुद्दा दशा", "Run": "चलाएं",
  "Varshaphal year": "वर्षफल वर्ष", "Prashna question": "प्रश्न कुंडली प्रश्न", "Muhurat event": "मुहूर्त कार्य", "Marriage": "विवाह", "Business": "व्यापार", "Travel": "यात्रा", "Naming": "नामकरण", "Property purchase": "संपत्ति खरीद", "Partner birth time": "साथी का जन्म समय", "Partner latitude": "साथी का अक्षांश", "Partner longitude": "साथी का देशांतर", "Partner time zone": "साथी का समय क्षेत्र", "Download premium PDF": "प्रीमियम PDF डाउनलोड करें", "Download factual PDF": "तथ्यात्मक PDF डाउनलोड करें",
  "OUTPUT / WELCOME": "आउटपुट / स्वागत", "Choose an advanced tool.": "कोई उन्नत टूल चुनें।", "Calculating local chart data...": "स्थानीय कुंडली डेटा की गणना हो रही है...", "No AI inference or guaranteed outcomes.": "कोई AI अनुमान या परिणाम की गारंटी नहीं।", "Select a tool above. Each result keeps its own rules and assumptions visible.": "ऊपर कोई टूल चुनें। हर परिणाम अपने नियम और मान्यताएँ स्पष्ट रखता है।",
  "Advanced observatory": "उन्नत वेधशाला", "LOCAL ASTROLOGY TOOLKIT": "लोकल ज्योतिष टूलकिट", "Time, pattern": "समय, पैटर्न", "& compatibility.": "और अनुकूलता।", "All calculations run through your private Swiss Ephemeris backend. No cloud AI is required.": "सभी गणनाएँ आपके निजी Swiss Ephemeris बैकएंड से होती हैं। किसी क्लाउड AI की आवश्यकता नहीं है।", "YOUR REFERENCE PROFILE": "आपका संदर्भ प्रोफाइल", "Start with birth facts.": "जन्म विवरण से शुरू करें।", "deterministic math": "निश्चित गणित", "Vimshottari Dasha": "विम्शोत्तरी दशा", "Maha + Antardasha timeline": "महादशा + अंतर्दशा समयरेखा", "Interactive Kundli": "इंटरैक्टिव कुंडली", "D1 houses, D9 & D10 divisions": "D1 भाव, D9 और D10 विभाजन", "Astro calendar": "ज्योतिष कैलेंडर", "Panchang, Rahu Kaal, Choghadiya": "पंचांग, राहु काल, चौघड़िया", "Local favourable time windows": "स्थानीय शुभ समय-खंड", "Compare charts": "कुंडलियों की तुलना करें", "CALCULATION OUTPUT": "गणना परिणाम", "Choose a tool.": "कोई टूल चुनें।", "Calculating...": "गणना हो रही है...", "Transparent rules, not guaranteed outcomes.": "पारदर्शी नियम, परिणाम की गारंटी नहीं।", "Select any calculation above to reveal its local, traceable result.": "स्थानीय, पारदर्शी परिणाम देखने के लिए ऊपर कोई गणना चुनें।",
  "Toggle colour theme": "रंग थीम बदलें", "Profile": "प्रोफाइल", "Choose palm photo": "हथेली की फोटो चुनें", "Choose face photo": "चेहरे की फोटो चुनें", "Example: Career momentum may increase over the next month...": "उदाहरण: अगले महीने करियर की गति बढ़ सकती है...", "Interpretive forecast": "व्याख्यात्मक पूर्वानुमान", "Rule label": "नियम नाम", "Review date": "समीक्षा तिथि", "Save for feedback": "फीडबैक के लिए सहेजें", "Location search": "स्थान खोज", "Birth location": "जन्म स्थान", "City fills coordinates & timezone": "शहर से निर्देशांक और समय क्षेत्र भरें", "Close location": "स्थान खोज बंद करें", "Search city, e.g. Delhi, India": "शहर खोजें, जैसे दिल्ली, भारत", "Search": "खोजें", "Searching...": "खोजा जा रहा है...", "Set location": "स्थान सेट करें", "Enter at least 2 characters.": "कम से कम 2 अक्षर लिखें।", "No matching city found. Try city, state or country.": "कोई शहर नहीं मिला। शहर, राज्य या देश के साथ खोजें।", "Location search is unavailable.": "स्थान खोज अभी उपलब्ध नहीं है।", "Your typed city is used only for this lookup. Profiles remain in your browser.": "आपका शहर केवल इस खोज के लिए उपयोग होता है। प्रोफाइल आपके ब्राउज़र में रहते हैं।"
};
// Calculation output is generated after the page has rendered, so these terms
// are kept separately and applied to both the static interface and result cards.
const CALCULATION_HINDI: Record<string, string> = {
  "Yoga & Dosha Analyzer": "योग एवं दोष विश्लेषक",
  "Classical yoga, Manglik and Kaal Sarp screening": "शास्त्रीय योग, मांगलिक और काल सर्प जाँच",
  "Nakshatra & Pada Studio": "नक्षत्र एवं पाद स्टूडियो",
  "Moon Nakshatra, Pada, deity and planet lords": "चंद्र नक्षत्र, पाद, देवता और ग्रह स्वामी",
  "Dasha + Gochar Timeline": "दशा एवं गोचर समयरेखा",
  "Dasha changes, retrogrades and sign ingresses": "दशा परिवर्तन, वक्री ग्रह और राशि प्रवेश",
  "Yoga signals": "योग संकेत",
  "Configured supportive combinations": "निर्धारित सहायक संयोजन",
  "Dosha screening": "दोष जाँच",
  "Flags shown with their exact rule": "सटीक नियम के साथ चिह्न दिखाए गए हैं",
  "No configured yoga was detected in this compact rule set.": "इस संक्षिप्त नियम-समूह में कोई निर्धारित योग नहीं मिला।",
  "Classical screening rules for the selected Lahiri sidereal birth chart": "चुनी हुई लाहिरी निरयण जन्म कुंडली के लिए शास्त्रीय जाँच नियम",
  "Ascendant": "लग्न", "Lahiri sidereal": "लाहिरी निरयण", "Sidereal": "निरयण",
  "Sun": "सूर्य", "Moon": "चंद्र", "Mars": "मंगल", "Mercury": "बुध", "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि", "Rahu": "राहु", "Ketu": "केतु",
  "Aries": "मेष", "Taurus": "वृषभ", "Gemini": "मिथुन", "Cancer": "कर्क", "Leo": "सिंह", "Virgo": "कन्या", "Libra": "तुला", "Scorpio": "वृश्चिक", "Sagittarius": "धनु", "Capricorn": "मकर", "Aquarius": "कुंभ", "Pisces": "मीन",
  "Ashwini": "अश्विनी", "Bharani": "भरणी", "Krittika": "कृत्तिका", "Rohini": "रोहिणी", "Mrigashira": "मृगशिरा", "Ardra": "आर्द्रा", "Punarvasu": "पुनर्वसु", "Pushya": "पुष्य", "Ashlesha": "आश्लेषा", "Magha": "मघा", "Purva Phalguni": "पूर्व फाल्गुनी", "Uttara Phalguni": "उत्तर फाल्गुनी", "Hasta": "हस्त", "Chitra": "चित्रा", "Swati": "स्वाती", "Vishakha": "विशाखा", "Anuradha": "अनुराधा", "Jyeshtha": "ज्येष्ठा", "Mula": "मूल", "Purva Ashadha": "पूर्वाषाढ़ा", "Uttara Ashadha": "उत्तराषाढ़ा", "Shravana": "श्रवण", "Dhanishta": "धनिष्ठा", "Shatabhisha": "शतभिषा", "Purva Bhadrapada": "पूर्व भाद्रपद", "Uttara Bhadrapada": "उत्तर भाद्रपद", "Revati": "रेवती",
  "Pada": "पाद", "Deity": "देवता", "lord": "स्वामी", "House": "भाव", "Present": "उपस्थित", "Flagged": "चिह्नित", "Not flagged": "चिह्नित नहीं", "Review": "समीक्षा आवश्यक",
  "Gajakesari Yoga": "गजकेसरी योग", "Kendra strength": "केंद्र बल", "Manglik Dosha": "मांगलिक दोष", "Kaal Sarp pattern": "काल सर्प पैटर्न", "Kemadruma pattern": "केमद्रुम पैटर्न",
  "Moon and Jupiter are in a configured kendra relationship (same, fourth, seventh, or tenth sign).": "चंद्र और गुरु निर्धारित केंद्र संबंध (एक, चतुर्थ, सप्तम या दशम राशि) में हैं।",
  "occupy Kendra houses from Lagna:": "लग्न से केंद्र भावों में स्थित हैं:",
  "Mars is in H": "मंगल भाव ",
  "from Lagna. This is a screening rule; tradition-specific exceptions and both partner charts must be assessed.": "में है। यह केवल जाँच नियम है; परंपरा-विशिष्ट अपवाद और दोनों साझेदारों की कुंडलियों का आकलन आवश्यक है।",
  "from Lagna, outside the configured 1/4/7/8/12 screening houses.": "में है और निर्धारित 1/4/7/8/12 जाँच भावों से बाहर है।",
  "All seven classical planets fall in one of the two Rahu-Ketu semicircles. Tradition-specific inclusion, conjunction and exception rules still need review.": "सभी सात शास्त्रीय ग्रह राहु-केतु के एक अर्धवृत्त में हैं। परंपरा-विशिष्ट समावेशन, युति और अपवाद नियमों की समीक्षा अभी आवश्यक है।",
  "The seven classical planets do not all occupy a single Rahu-Ketu semicircle in this configured screening rule.": "इस निर्धारित जाँच नियम में सभी सात शास्त्रीय ग्रह राहु-केतु के एक ही अर्धवृत्त में नहीं हैं।",
  "No classical planet other than Moon occupies either neighbouring sign from Moon. Kendra and cancellation rules are not applied in this compact screen.": "चंद्र के अतिरिक्त कोई शास्त्रीय ग्रह चंद्र की दोनों पड़ोसी राशियों में नहीं है। इस संक्षिप्त जाँच में केंद्र और दोष-निरस्तीकरण नियम लागू नहीं किए गए हैं।",
  "Yoga and Dosha Analyzer shows transparent, compact classical screening rules. It is not a complete chart judgement, compatibility conclusion, or guaranteed outcome.": "योग एवं दोष विश्लेषक पारदर्शी, संक्षिप्त शास्त्रीय जाँच नियम दिखाता है। यह पूर्ण कुंडली निर्णय, मिलान निष्कर्ष या किसी परिणाम की गारंटी नहीं है।",
  "Moon:": "चंद्र:", "Next": "अगले", "days": "दिन", "Gold:": "स्वर्ण:", "Mint:": "हरा:", "Blue:": "नीला:", "Coral:": "मूंगा:",
  "Visual Kundli Studio": "दृश्य कुंडली स्टूडियो", "Rashi chart": "राशि कुंडली", "Navamsa harmonic chart": "नवांश विभाजित कुंडली", "Dashamsa harmonic chart": "दशमांश विभाजित कुंडली", "North": "उत्तर", "South": "दक्षिण", "Wheel": "चक्र",
  "Personal Panchang Calendar": "व्यक्तिगत पंचांग कैलेंडर", "Rahu Kaal": "राहु काल", "Muhurat windows": "मुहूर्त समय", "Selected day": "चुना हुआ दिन", "Favourable windows shown in gold": "शुभ समय स्वर्ण रंग में दिखाए गए हैं", "Export .ics": ".ics निर्यात करें",
  "Calculation unavailable": "गणना उपलब्ध नहीं है", "Calculation returned an invalid response. Please try again.": "गणना से अमान्य उत्तर मिला। कृपया फिर प्रयास करें।", "This result could not be rendered. Please run the tool again.": "यह परिणाम दिखाया नहीं जा सका। कृपया टूल फिर चलाएँ।", "Premium PDF report is unavailable.": "प्रीमियम PDF रिपोर्ट उपलब्ध नहीं है।",
  "No AI inference or guaranteed outcomes.": "कोई AI अनुमान या परिणाम की गारंटी नहीं है।"
};
const ALL_HINDI: Record<string, string> = { ...HINDI, ...CALCULATION_HINDI };
const ENGLISH = Object.fromEntries(Object.entries(ALL_HINDI).map(([english, hindi]) => [hindi, english]));

function translate(value: string, language: Language) {
  const dictionary = language === "hi" ? ALL_HINDI : ENGLISH;
  const match = value.match(/^(\s*)([\s\S]*?)(\s*)$/);
  if (!match) return value;
  const content = match[2];
  if (dictionary[content]) return `${match[1]}${dictionary[content]}${match[3]}`;
  const translated = Object.entries(dictionary)
    .filter(([source]) => source.length > 2)
    .sort(([first], [second]) => second.length - first.length)
    .reduce((current, [source, target]) => current.replaceAll(source, target), content);
  return `${match[1]}${translated}${match[3]}`;
}

function translateTree(root: Node, language: Language) {
  const element = root.nodeType === Node.ELEMENT_NODE ? root as Element : root.parentElement;
  if (!element || element.closest("[data-no-translate], script, style, code, pre")) return;
  if (root.nodeType === Node.TEXT_NODE) {
    const next = translate(root.nodeValue || "", language);
    if (next !== root.nodeValue) root.nodeValue = next;
    return;
  }
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const nodes: Text[] = [];
  let node: Node | null;
  while ((node = walker.nextNode())) if (!node.parentElement?.closest("[data-no-translate], script, style, code, pre")) nodes.push(node as Text);
  nodes.forEach((textNode) => { const next = translate(textNode.nodeValue || "", language); if (next !== textNode.nodeValue) textNode.nodeValue = next; });
  if (root.nodeType === Node.ELEMENT_NODE) (root as Element).querySelectorAll<HTMLElement>("[placeholder], [aria-label], [title]").forEach((target) => ["placeholder", "aria-label", "title"].forEach((attribute) => { const current = target.getAttribute(attribute); if (current) target.setAttribute(attribute, translate(current, language)); }));
}

export default function LanguageToggle() {
  const [language, setLanguage] = useState<Language>("en");
  const [ready, setReady] = useState(false);
  useEffect(() => { setLanguage(window.localStorage.getItem(STORAGE_KEY) === "hi" ? "hi" : "en"); setReady(true); }, []);
  useEffect(() => {
    if (!ready) return;
    document.documentElement.lang = language === "hi" ? "hi" : "en";
    document.documentElement.dataset.language = language;
    window.localStorage.setItem(STORAGE_KEY, language);
    const apply = (root: Node = document.body) => translateTree(root, language);
    apply();
    const observer = new MutationObserver((changes) => { observer.disconnect(); changes.forEach((change) => { if (change.type === "characterData") apply(change.target); change.addedNodes.forEach((node) => apply(node)); }); observer.observe(document.body, { childList: true, subtree: true, characterData: true }); });
    observer.observe(document.body, { childList: true, subtree: true, characterData: true });
    return () => observer.disconnect();
  }, [language, ready]);
  return <button className="language-toggle" type="button" data-no-translate onClick={() => setLanguage((current) => current === "en" ? "hi" : "en")} aria-label={language === "en" ? "हिंदी में बदलें" : "Switch to English"}><span aria-hidden="true">{language === "en" ? "अ" : "A"}</span>{language === "en" ? "हिंदी" : "English"}</button>;
}
