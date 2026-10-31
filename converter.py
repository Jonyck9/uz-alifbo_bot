"""Basic Uzbek script conversion. Context-sensitive cases require review."""
import re

CYR_TO_LAT = {
    'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'yo','ж':'j','з':'z',
    'и':'i','й':'y','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r',
    'с':'s','т':'t','у':'u','ф':'f','х':'x','ц':'ts','ч':'ch','ш':'sh','ъ':'ʼ',
    'ь':'','э':'e','ю':'yu','я':'ya','ў':'oʻ','қ':'q','ғ':'gʻ','ҳ':'h'
}
LAT_TO_CYR = {'a':'а','b':'б','d':'д','e':'е','f':'ф','g':'г','h':'ҳ','i':'и',
              'j':'ж','k':'к','l':'л','m':'м','n':'н','o':'о','p':'п','q':'қ',
              'r':'р','s':'с','t':'т','u':'у','v':'в','x':'х','y':'й','z':'з'}
SPECIAL = [('oʻ','ў'),('gʻ','ғ'),('sh','ш'),('ch','ч'),('yo','ё'),('yu','ю'),('ya','я'),('ts','ц')]
APOSTROPHES = "['‘’ʻʼ`´]"

def apply_case(source, target):
    if source.isupper(): return target.upper()
    if source[0].isupper(): return target[0].upper()+target[1:]
    return target

def cyr_to_latin(text):
    return ''.join(apply_case(ch, CYR_TO_LAT[ch.lower()]) if ch.lower() in CYR_TO_LAT else ch for ch in text)

def latin_to_cyr(text):
    pattern = re.compile(r'o'+APOSTROPHES+r'|g'+APOSTROPHES+r'|sh|ch|yo|yu|ya|ts|[a-z]', re.I)
    def sub(m):
        token=m.group(); norm=re.sub(APOSTROPHES,'ʻ',token.lower())
        result=dict(SPECIAL).get(norm, LAT_TO_CYR.get(norm,token))
        return apply_case(token,result)
    return pattern.sub(sub,text)

def latin_to_new(text):
    for pattern, replacement in [(r'o'+APOSTROPHES,'ö'),(r'g'+APOSTROPHES,'ğ'),('sh','ş'),('ch','ç')]:
        text=re.sub(pattern,lambda m:apply_case(m.group(),replacement),text,flags=re.I)
    return text

def new_to_latin(text):
    return ''.join(apply_case(c,{'ö':'oʻ','ğ':'gʻ','ş':'sh','ç':'ch'}[c.lower()]) if c.lower() in 'öğşç' else c for c in text)

def convert(text, source, target):
    if source == target: return text
    latin = cyr_to_latin(text) if source=='cyr' else new_to_latin(text) if source=='new' else text
    return latin_to_cyr(latin) if target=='cyr' else latin_to_new(latin) if target=='new' else latin
