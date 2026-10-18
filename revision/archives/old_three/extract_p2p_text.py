from html.parser import HTMLParser
from pathlib import Path

class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'): self.skip+=1
        if tag in ('p','section','div','h1','h2','h3','h4','tr','pre','li'): self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script','style'): self.skip-=1
        if tag in ('p','h1','h2','h3','h4','tr','pre','li'): self.parts.append('\n')
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)

root=Path(__file__).resolve().parent
src=root/'sources/p2p_2603.15799v1.html'
p=Text();p.feed(src.read_text(encoding='utf-8'))
text='\n'.join(line.strip() for line in ''.join(p.parts).splitlines() if line.strip())
(root/'sources/p2p_text.txt').write_text(text+'\n',encoding='utf-8')
print({'chars':len(text)})
