import json,itertools,numpy as np,sys,time,os
from scipy.optimize import linprog
from scipy.sparse import lil_matrix,csc_matrix,hstack
from fractions import Fraction

def build(case,sizes,counts):
 k=len(sizes);V=[tuple(x) for x in case['types']];adj=[[0]*12 for _ in range(12)]
 for i,j,w in case['edges']:adj[i][j]=adj[j][i]=w
 cands=[];cat=[]
 for coord,size in enumerate(sizes):
  for B in itertools.combinations(range(12),size):
   if all(V[x][coord]>0 for x in B):cands.append(B);cat.append(coord)
 nr=12*k+66+k;A=lil_matrix((nr,len(cands)),dtype=np.int8);rhs=[];row=0
 for coord in range(k):
  for x in range(12):
   for j,B in enumerate(cands):
    if cat[j]==coord and x in B:A[row,j]=1
   rhs.append(V[x][coord]);row+=1
 for x in range(12):
  for y in range(x+1,12):
   for j,B in enumerate(cands):
    if x in B and y in B:A[row,j]=1
   rhs.append(2-adj[x][y]);row+=1
 for coord,n in enumerate(counts):
  for j,cg in enumerate(cat):
   if cg==coord:A[row,j]=1
  rhs.append(n);row+=1
 return csc_matrix(A,dtype=float),np.array(rhs,dtype=float),cands

def cert(case,sizes,counts):
 A,rhs,cands=build(case,sizes,counts);nr=A.shape[0]
 Aub=hstack([-A.T,np.ones((A.shape[1],1))],format='csc');Aeq=csc_matrix(np.r_[rhs,0].reshape(1,-1));obj=np.r_[np.zeros(nr),-1]
 for BND in (20,100,500):
  res=linprog(obj,A_ub=Aub,b_ub=np.zeros(A.shape[1]),A_eq=Aeq,b_eq=[-1],bounds=[(-BND,BND)]*nr+[(None,None)],method='highs-ds',options={'presolve':False})
  if res.status!=0:continue
  for den in (100,300,1000,3000,10000,100000,1000000):
   Y=[Fraction(float(v)).limit_denominator(den) for v in res.x[:-1]]
   erhs=sum(Fraction(int(rhs[i]))*Y[i] for i in range(nr));minc=None;ok=erhs<0;Ac=A.tocsc()
   for j in range(Ac.shape[1]):
    z=sum(Y[int(i)]*int(v) for i,v in zip(Ac.indices[Ac.indptr[j]:Ac.indptr[j+1]],Ac.data[Ac.indptr[j]:Ac.indptr[j+1]]))
    minc=z if minc is None or z<minc else minc
    if z<0:ok=False;break
   if ok:return {'y':[[i,z.numerator,z.denominator] for i,z in enumerate(Y) if z],'rhs':[erhs.numerator,erhs.denominator],'min':[minc.numerator,minc.denominator],'cands':len(cands),'den_limit':den,'bound':BND}
 return {'error':'certificate'}
if __name__=='__main__':
 fn,outfn=sys.argv[1],sys.argv[2];d=json.load(open(fn));sizes=d['sizes'];counts=d['counts'];t=time.time();out=[]
 for i,c in enumerate(d['cases']):
  z=cert(c,sizes,counts);out.append(z);print(i,z.get('error','OK'),z.get('den_limit'),flush=True)
 json.dump({'source':os.path.basename(fn),'sizes':sizes,'counts':counts,'certificates':out},open(outfn,'w'),separators=(',',':'))
 print('DONE',len(out),time.time()-t)
