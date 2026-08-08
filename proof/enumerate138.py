from math import comb
p=[comb(d,3)-15*d+70 for d in range(14)]
sol=[]
def rec(d,leftn,lefts,counts,pen):
    if d==13:
        n=leftn
        if 13*n==lefts and pen+p[13]*n<=42:
            c=counts+[n];inc=sum(c[i]*comb(i,3) for i in range(14))
            if inc<=572:sol.append((tuple(c),inc,572-inc,sum(c[i]*p[i] for i in range(14))))
        return
    for n in range(leftn+1):
        if d*n>lefts:break
        np=pen+p[d]*n
        if np<=42:rec(d+1,leftn-n,lefts-d*n,counts+[n],np)
rec(0,22,138,[],0)
sol.sort(key=lambda z:(z[3],z[2],z[0]))
print(len(sol))
for i,(c,inc,s,pen) in enumerate(sol):
 print(i,{d:n for d,n in enumerate(c) if n},inc,s,pen)
