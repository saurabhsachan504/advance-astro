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
  "Toggle colour theme": "रंग थीम बदलें", "Profile": "प्रोफाइल", "Choose palm photo": "हथेली की फोटो चुनें", "Choose face photo": "चेहरे की फोटो चुनें", "Example: Career momentum may increase over the next month...": "उदाहरण: अगले महीने करियर की गति बढ़ सकती है...", "Interpretive forecast": "व्याख्यात्मक पूर्वानुमान", "Rule label": "नियम नाम", "Review date": "समीक्षा तिथि", "Save for feedback": "फीडबैक के लिए सहेजें"
};
const ENGLISH = Object.fromEntries(Object.entries(HINDI).map(([english, hindi]) => [hindi, english]));

function translate(value: string, language: Language) {
  const dictionary = language === "hi" ? HINDI : ENGLISH;
  const match = value.match(/^(\s*)([\s\S]*?)(\s*)$/);
  return match ? `${match[1]}${dictionary[match[2]] || match[2]}${match[3]}` : value;
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
