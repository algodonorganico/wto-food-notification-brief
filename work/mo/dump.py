import json,sys,re
m,area,a,b=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4])
C=json.load(open(f'cand_{m}.json'))
T={'Regular notification':'R','Emergency notifications (SPS)':'E','Addendum to Regular Notification':'Add','Addendum to Emergency Notification (SPS)':'AddE','Corrigendum to Emergency Notification (SPS)':'CorE','Corrigendum to Regular Notification':'Cor','Revision to Regular Notification':'Rev'}
ks=sorted([k for k,x in C.items() if x['area']==area], key=lambda k:(C[k]['notifyingMember'],k))
OB={'Food safety':'FS','Animal health':'AH','Plant protection':'PP','Protect humans from animal/plant pest or disease':'HUM','Protect territory from other damage from pests':'TER'}
for i,k in enumerate(ks[a:b],a):
    x=C[k]
    ob=','.join(OB.get(o['name'],o['name'][:12]) for o in x.get('objectives') or [])
    t=re.sub(r'\s+',' ',x['titlePlain'] or '')[:230]
    p=re.sub(r'\s+',' ',x.get('productsFreeTextPlain') or '')[:100]
    d=re.sub(r'\s+',' ',x.get('descriptionPlain') or '')[:220] if (T.get(x['notificationType'],'?').startswith(('Add','Cor')) or len(t)<70) else ''
    print(f"{i}|{k.replace('G/SPS/N/','').replace('G/TBT/N/','')}|{x['notifyingMember']}|{T.get(x['notificationType'],x['notificationType'][:10])}|{ob}|{x.get('_sig','')}|{t}|P:{p}" + (f"|D:{d}" if d else ''))
print(len(ks))
