"""Optional SymPy generator adapted from the supplied 2026-09-12 proposal."""
from __future__ import annotations
import sympy as s
import time
Y=s.Symbol('y')

def fixed_prefix(u:str,v:str,seed:str,n:int)->str:
    w=seed
    while len(w)<n:
        w=''.join(u if b=='0' else v for b in w)
    return w[:n]

def auxiliary(u,v,seed,n=10):
    start=time.monotonic()
    w=fixed_prefix(u,v,seed,200)
    h=0; coeff=[]
    for b in w:
        coeff.append(Y**h if b=='1' else s.S.Zero)
        h+=b=='1'
    # order constraints n+1..2n; Q(x) has degree n
    M=s.Matrix([[coeff[k-i] for i in range(n+1)] for k in range(n+1,2*n+1)])
    from sympy.polys.matrices import DomainMatrix
    ns=DomainMatrix.from_Matrix(M).nullspace().to_Matrix()
    q=list(ns.row(0))
    den=s.lcm([s.denom(s.cancel(z)) for z in q])
    qs=[s.Poly(s.cancel(z*den),Y) for z in q]
    common=qs[0]
    for z in qs[1:]: common=s.gcd(common,z)
    qs=[s.exquo(z,common).as_expr() for z in qs]
    ps=[-s.expand(sum(qs[i]*coeff[k-i] for i in range(k+1))) for k in range(n+1)]
    allp=[s.Poly(z,Y) for z in qs+ps]
    common=allp[0]
    for z in allp[1:]: common=s.gcd(common,z)
    qs=[s.exquo(s.Poly(z,Y),common).as_expr() for z in qs]
    ps=[s.exquo(s.Poly(z,Y),common).as_expr() for z in ps]
    leading=None
    for k in range(2*n+1,150):
        c=s.expand(sum(qs[i]*coeff[k-i] for i in range(n+1)))
        if c!=0:
            leading=(k,c); break
    # sparse coefficient serialization
    def enc(poly):
        return {str(k[0]):str(c) for k,c in s.Poly(poly,Y).terms() if c}
    out={'u':u,'v':v,'seed':seed,'degree_x_bound':n,
         'p':[enc(z) for z in ps], 'q':[enc(z) for z in qs],
         'leading':{'order':leading[0],'poly':enc(leading[1])},
         'degree_y_max':max(s.Poly(z,Y).degree() for z in qs+ps if z!=0)}
    print(u,v,'nullity',ns.rows,'leading',leading,'degY',out['degree_y_max'],'elapsed',time.monotonic()-start,flush=True)
    return out
