import cv2,glob,numpy as np,sys
pre=sys.argv[1]
fs=sorted(glob.glob(f'test/{pre}_*.jpg'), key=lambda f: float(f.rsplit('_',1)[1][:-4]))
ims=[]
for f in fs:
    im=cv2.resize(cv2.imread(f),(960,540)); cv2.putText(im, f.rsplit('_',1)[1][:-4], (10,40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,255), 2); ims.append(im)
for i in range(0,len(ims),6):
    g=ims[i:i+6]
    while len(g)<6: g.append(np.zeros_like(ims[0]))
    cv2.imwrite(f'test/{pre}_sheet{i//6}.png', np.vstack([np.hstack(g[j:j+2]) for j in range(0,6,2)]))
print(len(fs))
