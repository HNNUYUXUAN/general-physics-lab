"""Translate presentation LaTeX to boxes without evaluating mathematical expressions.

The small grammar deliberately fails on unknown commands. It preserves functions,
decimal spellings, and operator order instead of using TeX as executable input.
"""
import re

SYMBOLS = dict(zip(
    'alpha beta gamma delta epsilon varepsilon zeta eta theta vartheta iota kappa lambda mu nu xi pi varpi rho varrho sigma varsigma tau upsilon phi varphi chi psi omega Gamma Delta Theta Lambda Xi Pi Sigma Upsilon Phi Psi Omega'.split(),
    'α β γ δ ε ε ζ η θ ϑ ι κ λ μ ν ξ π ϖ ρ ϱ σ ς τ υ φ ϕ χ ψ ω Γ Δ Θ Λ Ξ Π Σ Υ Φ Ψ Ω'.split()))
SYMBOLS.update({'cdot':'·','times':'×','pm':'±','mp':'∓','approx':'≈','simeq':'≃','sim':'∼','equiv':'≡','neq':'≠','ne':'≠','le':'≤','leq':'≤','ge':'≥','geq':'≥','to':'→','rightarrow':'→','leftarrow':'←','infty':'∞','partial':'∂','nabla':'∇','ell':'ℓ','circ':'°','prime':'′','perp':'⊥','parallel':'∥','propto':'∝','in':'∈','notin':'∉','forall':'∀','angle':'∠','ldots':'…','cdots':'⋯','dots':'…','vert':'|','Vert':'‖','lvert':'|','rvert':'|','langle':'⟨','rangle':'⟩'})
SYMBOLS.update({'ll':'≪','gg':'≫','Longrightarrow':'⟹','Rightarrow':'⇒','Leftrightarrow':'⇔','because':'∵','therefore':'∴','hbar':'ℏ','degree':'°','textdegree':'°','bullet':'•','star':'⋆','ast':'∗'})
SYMBOLS.update({'uparrow':'↑','downarrow':'↓','updownarrow':'↕','leftrightarrow':'↔','rightarrow':'→','leftarrow':'←'})
SYMBOLS.update({'lbrack':'[','rbrack':']','lbrace':'{','rbrace':'}','Re':'ℜ','Im':'ℑ'})

def wl_string(s):
    return '"'+''.join('\\'+c if c in '\\"' else '\\n' if c=='\n' else '\\:'+format(ord(c),'04x') if ord(c)>127 else c for c in s)+'"'

def row(parts):
    return parts[0] if len(parts)==1 else 'RowBox[{'+','.join(parts)+'}]'

class Parser:
    def __init__(self,text): self.text=text;self.i=0;self.roman=False
    def group(self):
        while self.i<len(self.text) and self.text[self.i].isspace():self.i+=1
        if self.i>=len(self.text): raise ValueError('Missing TeX argument: '+self.text)
        if self.text[self.i]=='{':
            self.i+=1;result=self.sequence('}');self.i+=1;return result
        # An unbraced argument consumes a single token, not a whole number.
        if self.text[self.i].isdigit():
            c=self.text[self.i];self.i+=1;return wl_string(c)
        return self.atom()
    def literal_group(self):
        if self.i>=len(self.text) or self.text[self.i]!='{':raise ValueError('Expected text group: '+self.text)
        self.i+=1;start=self.i;depth=1
        while self.i<len(self.text) and depth:
            if self.text[self.i]=='{':depth+=1
            if self.text[self.i]=='}':depth-=1
            self.i+=1
        if depth:raise ValueError('Unclosed text group: '+self.text)
        return self.text[start:self.i-1]
    def atom(self):
        c=self.text[self.i];self.i+=1
        if c=='{':result=self.sequence('}');self.i+=1;return result
        if c in '([':
            result=self.sequence((')',']'));close=self.text[self.i];self.i+=1
            return row([wl_string(c),result,wl_string(close)])
        if c!='\\':
            if c.isalpha() and self.roman:
                m=re.match(r'[A-Za-z]*',self.text[self.i:]);c+=m[0];self.i+=len(m[0])
            if c.isdigit():
                m=re.match(r'[0-9]*(?:\.[0-9]+)?',self.text[self.i:]);c+=m[0];self.i+=len(m[0])
            return wl_string(c)
        m=re.match(r'[A-Za-z]+|.',self.text[self.i:])
        if not m:raise ValueError('Trailing TeX escape')
        command=m[0];self.i+=len(command)
        if command in SYMBOLS:return wl_string(SYMBOLS[command])
        if command in ('frac','dfrac','tfrac'):return 'FractionBox['+self.group()+','+self.group()+']'
        if command=='sqrt':
            if self.i<len(self.text) and self.text[self.i]=='[':
                self.i+=1;index=self.sequence(']');self.i+=1;return 'RadicalBox['+self.group()+','+index+']'
            return 'SqrtBox['+self.group()+']'
        if command in ('bar','overline','hat','widehat','dot','ddot','tilde','widetilde','vec'):
            mark={'bar':'_','overline':'_','hat':'^','widehat':'^','dot':'.','ddot':'¨','tilde':'~','widetilde':'~','vec':'→'}[command]
            return 'OverscriptBox['+self.group()+','+wl_string(mark)+']'
        if command in ('mathrm','textrm'):
            previous=self.roman;self.roman=True;value=self.group();self.roman=previous
            return 'StyleBox['+value+',FontSlant->"Plain",FontFamily->"Times New Roman"]'
        if command in ('text','operatorname','mbox'):
            text=re.sub(r'\\[,;:! ]',' ',self.literal_group())
            return 'StyleBox['+wl_string(text)+',FontSlant->"Plain"]'
        if command in ('mathbf','boldsymbol'):return 'StyleBox['+self.group()+',FontWeight->"Bold"]'
        if command in ('mathit','mathcal','mathsf'):return self.group()
        if command in ('sin','cos','tan','cot','arcsin','arccos','arctan','sinh','cosh','exp','ln','log','max','min','det','lim'):
            return 'StyleBox['+wl_string(command)+',FontSlant->"Plain"]'
        if command in ('sum','prod','int','iint','oint'):return wl_string({'sum':'∑','prod':'∏','int':'∫','iint':'∬','oint':'∮'}[command])
        if command in ('left','right','big','Big','bigg','Bigg','displaystyle','textstyle','limits','nolimits'):return wl_string('')
        if command in (',',';',':',' ','quad','qquad','enspace','thinspace'):return wl_string('  ' if command=='qquad' else ' ')
        if command=='!':return wl_string('')
        if command in ('%','_','{','}','#','&','$','|'):return wl_string(command)
        if command=='begin':
            env=self.literal_group()
            if env=='array':self.literal_group()
            end='\\end{'+env+'}';position=self.text.find(end,self.i)
            if position<0:raise ValueError('Unclosed math environment '+env)
            content=self.text[self.i:position];self.i=position+len(end)
            rows=['{'+','.join(Parser(c).sequence() for c in r.split('&'))+'}' for r in content.split('\\\\') if r.strip()]
            grid='GridBox[{'+','.join(rows)+'},GridBoxAlignment->{"Columns"->{{Left}}}]'
            borders={'cases':('{',''),'pmatrix':('(',')'),'bmatrix':('[',']'),'vmatrix':('|','|')}
            if env in borders:return row([wl_string(borders[env][0]),grid,wl_string(borders[env][1])])
            if env in ('array','matrix','aligned','align','align*','gathered'):return grid
            raise ValueError('Unknown math environment '+env)
        if command=='\\':return wl_string('  ')
        raise ValueError('Unsupported TeX command \\'+command+' in '+self.text)
    def sequence(self,stop=None):
        parts=[]
        while self.i<len(self.text) and not (self.text[self.i] in stop if isinstance(stop,tuple) else self.text[self.i]==stop):
            if self.text[self.i].isspace():self.i+=1;continue
            base=wl_string('') if self.text[self.i] in '_^' else self.atom();sub=None;sup=None
            while self.i<len(self.text) and self.text[self.i].isspace():self.i+=1
            while self.i<len(self.text) and self.text[self.i] in '_^':
                op=self.text[self.i];self.i+=1;value=self.group()
                if op=='_':sub=value
                else:sup=value
                while self.i<len(self.text) and self.text[self.i].isspace():self.i+=1
            if sub is not None and sup is not None:base='SubsuperscriptBox['+base+','+sub+','+sup+']'
            elif sub is not None:base='SubscriptBox['+base+','+sub+']'
            elif sup is not None:base='SuperscriptBox['+base+','+sup+']'
            parts.append(base)
        if stop and self.i>=len(self.text):raise ValueError('Unclosed TeX group: '+self.text)
        return row(parts)

def tex_boxes(text):
    return Parser(text.strip()).sequence()
