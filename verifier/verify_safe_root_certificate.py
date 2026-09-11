"""Direct checker: no imports from either search implementation."""
from fractions import Fraction

def req(condition,msg):
    if not condition:raise ValueError(msg)

def lint(n):req(type(n) is int and n>=0,'nonnegative integer required')
def word(x):req(type(x)is str and not(set(x)-{'0','1'}),'binary word required')
def keys(obj, expected):
    req(type(obj) is dict and set(obj)==set(expected), 'unexpected certificate fields')
def position_map(w):
    word(w);ps=[i for i,s in enumerate(w) if s=='1'];q=len(ps)
    return 3**q,1<<len(w),sum((1<<p)*3**(q-1-i) for i,p in enumerate(ps))

def run(z,w):
    req(type(z)is int and z>=1,'positive source required')
    word(w);x=z;A=1;M=1;rows=[(x,A,M)]
    for b in w:
        req(x%2==int(b),'not literal')
        if b=='1':x=(3*x+1)//2;A*=3
        else:x//=2
        M*=2;rows.append((x,A,M))
    return rows

def check(cert):
    req(type(cert)is dict,'certificate object')
    req(type(cert.get('schema_version')) is int and cert['schema_version']==1,'schema version')
    req(cert.get('query_scope')=='all_positive_sources_all_lengths_lex','query scope')
    req(cert.get('proves_collatz') is False,'overclaim flag')
    typ=cert.get('status');req(typ in ['IMPROVEMENT','NO_LEX_IMPROVEMENT'],'not proved')
    common={'schema_version','query_scope','proves_collatz','status','source','target_word'}
    keys(cert, common | ({'witness','work'} if typ=='IMPROVEMENT' else
        {'source_bound','depth','leaves','traces','diagnostics'}))
    S=cert['source'];w=cert['target_word'];target=run(S,w);y,A,M=target[-1]
    if typ=='IMPROVEMENT':
        keys(cert['witness'], {'source','word'});lint(cert['work'])
        ws=cert['witness'];z=ws['source'];x,a,m=run(z,ws['word'])[-1]
        req(x==y,'wrong endpoint')
        cmp=a*M-A*m
        req(cmp>0 or(cmp==0 and z<S),'not a lex improvement')
        return True
    req(A>=M,'no-improvement domain requires coefficient >=1')
    Bsrc=(M*y-1)//A;N=Bsrc.bit_length()
    lint(cert['source_bound']);lint(cert['depth'])
    req(cert['source_bound']==Bsrc and cert['depth']==N,'source or depth bound')
    leaves=cert['leaves'];trie={};kraft=0;frontier=set()
    req(type(leaves)is list,'leaves list')
    for leaf in leaves:
        req(type(leaf) is dict,'leaf object')
        keys(leaf, {'word','kind','source'} if leaf.get('kind')=='frontier' else {'word','kind'})
        v=leaf['word'];word(v);req(len(v)<=N,'leaf too deep')
        node=trie
        for b in v:
            req('_leaf' not in node,'prefix overlap')
            node=node.setdefault(b,{})
        req(not node,'duplicate or reverse prefix overlap');node['_leaf']=True
        kraft+=1<<(N-len(v))
        a,m,b=position_map(v);res=(-b*pow(a,-1,m))%m if m>1 else 0
        zmin=res if res else m
        kind=leaf['kind']
        if kind=='empty':req(zmin>Bsrc,'nonempty empty cylinder')
        elif kind=='coefficient_crossing':req(a<m,'no crossing')
        elif kind=='frontier':
            req(len(v)==N and 1<=zmin<=Bsrc,'frontier range')
            lint(leaf['source']);req(leaf['source']==zmin and zmin not in frontier,'frontier source')
            rows=run(zmin,v);req(all(a>=m for x,a,m in rows),'unsafe frontier')
            frontier.add(zmin)
        else:raise ValueError('unknown leaf')
    req(kraft==(1<<N),'incomplete root coverage')
    # Root coverage alone misses competitors ending before the leaf.
    # Inspect every prefix once, using its positional affine equation.
    prefixes={v[:j] for leaf in leaves for v in [leaf['word']] for j in range(len(v)+1)}
    short_hits=0
    for p in prefixes:
        a,m,b=position_map(p);num=m*y-b
        if num%a:continue
        z=num//a
        if 1<=z<=Bsrc:
            cmp=a*M-A*m
            req(not(cmp>0 or(cmp==0 and z<S)),'missed short-prefix improvement')
            if a>=m:short_hits+=1
    traces=cert['traces'];req(type(traces) is list and len(traces)==len(frontier),'trace count');seen=set()
    for tr in traces:
        keys(tr, {'source','word','cut'});lint(tr['source'])
        z=tr['source'];req(z in frontier and z not in seen,'trace root');seen.add(z)
        rows=run(z,tr['word']);req(all(a>=m for x,a,m in rows[:-1]),'trace continues beyond crossing')
        # Any earlier improving hit invalidates a cut.
        for x,a,m in rows:
            cmp=a*M-A*m
            req(not(x==y and(cmp>0 or(cmp==0 and z<S))),'missed improvement')
        x,a,m=rows[-1];cut=tr['cut']
        if cut=='coefficient_crossing':req(a<m,'invalid crossing')
        elif cut=='normalization':
            cmp=m*x*A-M*y*a
            req(cmp>0 or(cmp==0 and z>=S),'wrong normalization inequality')
        elif cut=='first_hit':
            req(x==y and all(xx!=y for xx,aa,mm in rows[:-1]),'not first hit')
            cmp=a*M-A*m
            req(cmp<0 or(cmp==0 and z>=S),'invalid first hit')
        else:raise ValueError('unknown cut')
    diagnostics={'tree_nodes':len(prefixes),'frontier_size':len(frontier),
        'trace_steps':sum(len(t['word']) for t in traces),'short_hits':short_hits}
    keys(cert['diagnostics'], diagnostics)
    for k,v in diagnostics.items():
        lint(cert['diagnostics'][k]);req(cert['diagnostics'][k]==v,'incorrect diagnostic '+k)
    return True
