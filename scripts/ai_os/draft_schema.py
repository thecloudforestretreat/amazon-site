"""Validate and normalize local worker shapes without generating or approving copy."""
from copy import deepcopy

def normalize_draft(raw):
    result=deepcopy(raw)
    for language in ('en','es'):
        page=result[language]
        for field in ('quick','lede','fit','access','pace'):
            if not isinstance(page.get(field),str) or not page[field].strip():
                raise ValueError(f'{language}: missing {field}')
        if len(page.get('sections',[]))!=10 or len(page.get('faqs',[]))!=6:
            raise ValueError(f'{language}: incomplete sections or FAQs')
        for section in page['sections']:
            if 'paragraphs' not in section:
                section['paragraphs']=[section.get('intro'),section.get('practical_context')]
            if len(section['paragraphs'])!=2 or not all(isinstance(p,str) and p.strip() for p in section['paragraphs']):
                raise ValueError(f'{language}: missing section context')
            display=section.get('display',{})
            if not all(isinstance(display.get(k),str) and display[k].strip() for k in ('heading','intro')):
                raise ValueError(f'{language}: missing display copy')
            if len(display.get('points',[]))!=3 or not all(isinstance(p,str) and p.strip() for p in display['points']):
                raise ValueError(f'{language}: invalid display points')
        page['faqs']=[[faq.get('question'),faq.get('answer')] if isinstance(faq,dict) else faq for faq in page['faqs']]
        if not all(isinstance(f,list) and len(f)==2 and all(isinstance(s,str) and s.strip() for s in f) for f in page['faqs']):
            raise ValueError(f'{language}: invalid FAQ pair')
    return result
