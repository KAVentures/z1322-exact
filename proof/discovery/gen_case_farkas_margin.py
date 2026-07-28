import json,itertools,numpy as np,sys,time,os
from scipy.optimize import linprog
from scipy.sparse import lil_matrix,csc_matrix,hstack
from fractions import Fraction

def build(case,W,a,b):
 V=[tuple(x) for x in case['types']];adj=[[0]*12 for _ in range(12)]
 for i,j,w in case['edges']:adj[i][j]=adj[j][i]=w
 cands=[];cat=[]
 for coord,size in enumerate((4,5,6)):
  for B in itertools.combinations(range(12),size):
   if all(V[x][coord]>0 for x in B):cands.append(B);cat.append(coord)
 nr=105; A=lil_matrix((nr,len(cands)),dtype=np.int8); rhs=[];row=0
 for coord in range(3):
  for x in range(12):
   for j,B in enumerate(cands):
    if cat[j]==coord and x in B:A[row,j]=1
   rhs.append(V[x][coord]);row+=1
 for x in range(12):
  for y in range(x+1,12):
   for j,B in enumerate(cands):
    if x in B and y in B:A[row,j]=1
   rhs.append(2-adj[x][y]);row+=1
 for coord,n in enumerate((W,a,b)):
  for j,cg in enumerate(cat):
   if cg==coord:A[row,j]=1
  rhs.append(n);row+=1
 return csc_matrix(A,dtype=float),np.array(rhs,dtype=float),cands

def exact_check(A,rhs,Y):
 erhs=sum(Fraction(int(rhs[i]))*Y[i] for i in range(len(Y)))
 Ac=A.tocsc(); minc=None
 for j in range(Ac.shape[1]):
  z=sum(Y[int(i)]*int(v) for i,v in zip(Ac.indices[Ac.indptr[j]:Ac.indptr[j+1]],Ac.data[Ac.indptr[j]:Ac.indptr[j+1]]))
  minc=z if minc is None or z<minc else minc
  if z<0:return False,erhs,minc
 return erhs<0,erhs,minc

def cert(case,W,a,b):
 A,rhs,cands=build(case,W,a,b); nr=A.shape[0]
 # maximize common coefficient margin t with b^T y=-1 and bounded y.
 Aub=hstack([-A.T,np.ones((A.shape[1],1))],format='csc')
 Aeq=csc_matrix(np.r_[rhs,0].reshape(1,-1));obj=np.r_[np.zeros(nr),-1]
 for BND in (20,100,500):
  res=linprog(obj,A_ub=Aub,b_ub=np.zeros(A.shape[1]),A_eq=Aeq,b_eq=[-1],bounds=[(-BND,BND)]*nr+[(None,None)],method='highs-ds',options={'presolve':False})
  if res.status!=0:continue
  for den in (100,300,1000,3000,10000,100000,1000000):
   Y=[Fraction(float(v)).limit_denominator(den) for v in res.x[:-1]]
   ok,erhs,minc=exact_check(A,rhs,Y)
   if ok:
    sparse=[[i,y.numerator,y.denominator] for i,y in enumerate(Y) if y]
    return {'y':sparse,'rhs':[erhs.numerator,erhs.denominator],'min':[minc.numerator,minc.denominator] if minc is not None else [0,1],'cands':len(cands),'den_limit':den,'bound':BND}
 return {'error':'certificate','status':int(res.status) if 'res' in locals() else None}

if __name__=='__main__':
 fn=sys.argv[1]; outfn=sys.argv[2] if len(sys.argv)>2 else fn.replace('.json','_farkas.json'); limit=int(sys.argv[3]) if len(sys.argv)>3 else None
 d=json.load(open(fn));W=d.get('w',2);a=d['a'];b=d['b'];cases=d['cases'][:limit]
 out=[];t=time.time()
 for i,c in enumerate(cases):
  z=cert(c,W,a,b);out.append(z)
  if 'error' in z: print('ERROR',i,z,flush=True);break
  if i%100==0:print(i,'/',len(cases),'sec',round(time.time()-t,1),'sparse',len(z['y']),'den',z['den_limit'],'bound',z['bound'],flush=True)
 json.dump({'source':os.path.basename(fn),'W':W,'a':a,'b':b,'count':len(out),'certificates':out},open(outfn,'w'),separators=(',',':'))
 print('DONE',len(out),'sec',time.time()-t,'size',os.path.getsize(outfn))
