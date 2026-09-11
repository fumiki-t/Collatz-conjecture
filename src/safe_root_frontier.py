from __future__ import annotations
from fractions import Fraction
from src.safe_ancestor_window import literal,affine,ceil_div,positive_int

def _search(S:int,L:int,limit:int=1000000):
    positive_int(S,'S');positive_int(limit,'limit')
    y,w,_=literal(S,L);A,M,B,Q=affine(w);gamma=Fraction(A,M)
    if gamma<1:return {'status':'IMPROVEMENT','source':S,'target_word':w,'witness':{'source':y,'word':''},'work':0}
    H=Fraction(M*y,A);Bsrc=ceil_div(M*y,A)-1;N=Bsrc.bit_length()
    leaves=[];candidates=[];nodes=0;short_hits=0
    stack=[('',1,0,0)]
    while stack:
        if nodes>=limit:return {'status':'UNKNOWN','source':S,'target_word':w,'work':nodes}
        v,a,bb,r=stack.pop();nodes+=1;k=len(v);m=1<<k
        zmin=r if r else m
        if zmin>Bsrc:
            leaves.append({'word':v,'kind':'empty'});continue
        if a<m:
            leaves.append({'word':v,'kind':'coefficient_crossing'});continue
        if (m*y-bb)%a==0:
            z=(m*y-bb)//a
            if 1<=z<=Bsrc and (z-r)%m==0:
                short_hits+=1;cmp=a*gamma.denominator-m*gamma.numerator
                if cmp>0 or (cmp==0 and z<S):
                    return {'status':'IMPROVEMENT','source':S,'target_word':w,'witness':{'source':z,'word':v},'work':nodes}
        if k==N:
            leaves.append({'word':v,'kind':'frontier','source':zmin});candidates.append(zmin);continue
        yrep=(a*r+bb)//m
        for bit in [1,0]:
            lift=(bit-yrep)%2
            stack.append((v+str(bit),a*(3 if bit else 1),3*bb+m if bit else bb,r+m*lift))
    traces=[];steps=0
    for z in sorted(candidates):
        x=z;a=1;m=1;v=[]
        while True:
            c=Fraction(a,m);Y=Fraction(m*x,a)
            if c<1:reason='coefficient_crossing';break
            if x==y:
                if c>gamma or(c==gamma and z<S):
                    return {'status':'IMPROVEMENT','source':S,'target_word':w,'witness':{'source':z,'word':''.join(v)},'work':nodes+steps}
                reason='first_hit';break
            if Y>H or(Y==H and z>=S):reason='normalization';break
            if nodes+steps>=limit:return {'status':'UNKNOWN','source':S,'target_word':w,'work':nodes+steps}
            bit=x%2;v.append(str(bit));m*=2
            if bit:a*=3;x=(3*x+1)//2
            else:x//=2
            steps+=1
        traces.append({'source':z,'word':''.join(v),'cut':reason})
    return {'status':'NO_LEX_IMPROVEMENT','source':S,'target_word':w,'source_bound':Bsrc,'depth':N,'leaves':leaves,'traces':traces,'diagnostics':{'tree_nodes':nodes,'frontier_size':len(candidates),'trace_steps':steps,'short_hits':short_hits}}


def search(S:int,L:int,limit:int=1000000):
    result=_search(S,L,limit)
    result['schema_version']=1
    result['query_scope']='all_positive_sources_all_lengths_lex'
    result['proves_collatz']=False
    return result
