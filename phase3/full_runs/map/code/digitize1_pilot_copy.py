import sys, numpy as np
from PIL import Image
im=np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(int)
# calibration passed: x(J1),J1,x(J2),J2, y(d1),log10 d1,y(d2),log10 d2, xa,xb,ya,yb
xa1,J1,xa2,J2,ya1,L1,ya2,L2,fx0,fx1,fy0,fy1=[float(v) for v in sys.argv[2:14]]
R,G,B=im[:,:,0],im[:,:,1],im[:,:,2]
purple=(R>110)&(R<190)&(G>80)&(G<150)&(B>160)&(B<215)&(B-G>45)
green=(G>130)&(G<190)&(R>50)&(R<140)&(B<140)&(G-R>40)&(G-B>40)
def x2J(x): return J1+(x-xa1)*(J2-J1)/(xa2-xa1)
def J2x(J): return xa1+(J-J1)*(xa2-xa1)/(J2-J1)
def y2v(y): return 10**(L1+(y-ya1)*(L2-L1)/(ya2-ya1))
out={}
for name,mask in (('purple',purple),('green',green)):
    res=[]
    for k in range(int(sys.argv[14]),int(sys.argv[15])+1):
        J=k/10; x=J2x(J)
        lo=int(max(fx0+3,x-4)); hi=int(min(fx1-3,x+4))
        ys=np.nonzero(mask[int(fy0)+3:int(fy1)-3,lo:hi+1])[0]+int(fy0)+3
        if len(ys)<15: res.append((J,None)); continue
        # marker: take densest window of 25 rows
        best=None
        for y in range(ys.min(),ys.max()+1):
            c=((ys>=y)&(ys<y+25)).sum()
            if best is None or c>best[0]: best=(c,y)
        sel=ys[(ys>=best[1])&(ys<best[1]+25)]
        res.append((J,round(y2v(np.median(sel)),4)))
    out[name]=res
    print(name, res)
