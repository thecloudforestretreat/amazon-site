"""Flag observed local-draft failures; passing never grants editorial approval."""
import json,re
PATTERNS={
 'spanish_voice_mismatch':r'\b(?:confirme|pregunte|solicite|consulte|confirmen|consulten|soliciten|pregúntenle)\b',
 'unsupported_wildlife_timing':r'wildlife can be found at any time|vida silvestre puede encontrarse a cualquier hora',
 'literal_spanish_failure':r'\blas avistamientos\b|\bcamadas guiadas\b|\benforce\b|\blos salidas\b|\bla avistamiento\b',
 'invented_transport':r'flight to Tena|flight from Tena|flight from.*Puyo|vuelo a Tena|vuelo de regreso desde Tena|Sim[oó]n Bol[ií]var',
 'unrealistic_specificity':r'minute-by-minute|minuto a minuto|radio frequency|frecuencia de radio|48 hours|48 horas',
 'unsupported_timing':r'6 to 8 hours|6 y 8 horas',
 'colonial_framing':r'back to civilization|volver a la civilizaci[oó]n',
 'unsafe_river_advice':r'test the water temperature|probar la temperatura del agua',
 'unsupported_group_safety':r'large group for safety|grupo grande por seguridad',
}
def flags(draft):
 text=json.dumps(draft,ensure_ascii=False)
 return [name for name,pattern in PATTERNS.items() if re.search(pattern,text,re.I)]
