import json,sys,re
m,area=sys.argv[1],sys.argv[2]
C=json.load(open(f'cand_{m}.json'))
T={'Regular notification':'R','Emergency notifications (SPS)':'E','Addendum to Emergency Notification (SPS)':'AddE','Corrigendum to Emergency Notification (SPS)':'CorE','Addendum to Regular Notification':'Add','Corrigendum to Regular Notification':'Cor','Revision to Regular Notification':'Rev'}
ks=sorted([k for k,x in C.items() if x['area']==area], key=lambda k:(C[k]['notifyingMember'],k))
for i,k in enumerate(ks):
    x=C[k]; t=re.sub(r'\s+',' ',x['titlePlain'] or '')[:150]
    typ=T.get(x['notificationType'],x['notificationType'][:6])
    d=re.sub(r'\s+',' ',x.get('descriptionPlain') or '')
    d=d[:140] if (typ!='R' or len(t)<60) else ''
    print(f"{i}|{k.split('/N/')[1]}|{x['notifyingMember'][:14]}|{typ}|{''.join(s[0] for s in x.get('_sig',[]))}|{t}"+(f"|D:{d}" if d else ''))
