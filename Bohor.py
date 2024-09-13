import pandas as pd
import numpy as np

##### حالات العلل والزحاف في العروض والضراب
ad_cases=pd.read_csv('corpus/arod_drb_cases.csv',sep='\t',encoding='utf-16')
seas_tafilat_code=pd.read_csv('corpus/Seas_cases.csv',sep='\t',encoding='utf-16')
ailla_zihaf=pd.read_csv('corpus/ailla_zihaf.csv',sep='\t',encoding='utf-16')
##########
si = pd.read_csv('corpus/Seas_info.csv', sep='\t', encoding='utf-16')
sea_dict = dict(zip(si['Snum'], si['Sname']))
########### مثال لحالات الضرب والعروض
ad_cases.head()
#############
### استدعاء قواعد انماط التفعيلات التي تم اعداها اعتمادا على ستة مراجع ذهبية لعلم العروض  بالاضافة الى مراجعة خبراء في العروض
ard_drb=pd.read_csv('corpus/rule1_ard_drb.csv',sep='\t',encoding='utf-16')
hsho_info=pd.read_csv('corpus/rule2_hsho_info.csv',sep='\t',encoding='utf-16')
hsho_tfilah=pd.read_csv('corpus/rule3_hsho_tfilah.csv',sep='\t',encoding='utf-16')
ver_info=pd.read_csv('corpus/rule4_byt_info.csv',sep='\t',encoding='utf-16')
# استدعاء معلومات البحور
si=pd.read_csv('corpus/Seas_info.csv',sep='\t',encoding='utf-16')
sc=seas_tafilat_code.copy()
#####################
cse=[]
def get_arroth_seting(sid,arod_drb_case,hshw_info):
    aid=[];adc=[]
    for i in arod_drb_case:
        for d in arod_drb_case[i]:
            aid.append(i)
            adc.append(d)
    adf=pd.DataFrame({'sids':[sid for i in range(len(aid))],'aid':aid,'adc':adc})

    hc=[i for i in hshw_info["case"]]
    hcs=pd.DataFrame({'sids':[sid for i in range(len(hc))],'hc':hc})

    pt=[i for i in hshw_info["pt"]]
    ft=[i for i in hshw_info["ft"]]
    ptft=pd.DataFrame({'sids':[sid for i in range(len(pt))],'pt':pt,'ft':ft})
    cse.append([sid,hshw_info["count"],hshw_info["start"],hshw_info["end"]])
    return adf,hcs,ptft,cse
# هذه الدالة تجلب التفعيلات التي يجب استبعادها عند اجتماع زحافين يفترض الا يجتمعا
# مثال رقم1: اذ وقع القبض امتنع الكف والعكس في بحر الطويل
def get_zihaf_conflict(tf,p,shtr_position,zhaf1,zhaf2):
    tid =[i for i in range(len(p)) if (len([j for j in p[i][:shtr_position] if j ==zhaf1])!=0)\
          and (len([j for j in p[i][shtr_position:] if j ==zhaf2])!=0)]
    tid1 =[i for i in range(len(p)) if (len([j for j in p[i][:shtr_position] if j ==zhaf2])!=0)\
          and (len([j for j in p[i][shtr_position:] if j ==zhaf1])!=0)]
    tid.extend(tid1)
    tf=tf[~tf.Tid.isin(tid)]
    return(tf)

# هذه الدالة تعالج الحالات الاستثناية التي تخرج عن قواعد تنميط العروض
def exception_handling(sid,tf,p):
    if sid==1:
        # استثناءات البحر الطويل
        # حالة رقم1: اذ وقع القبض امتنع الكف والعكس
        tf=get_zihaf_conflict(tf,p,4,"2","5")
    elif sid==2:
        # استثناءات البحر المديد
        # اذ وقع الكف امتنع الخبن والعكس
        tf=get_zihaf_conflict(tf,p,3,"6","7")
    elif sid==3:
        # استثناءات البحر البحر البسيط
        # اذ وقع القبض امتنع الكف والعكس
        tf=get_zihaf_conflict(tf,p,4,"2","5")
    elif sid==8:
        # استثناءات البحر الكامل
        # استبعاد التفعيلات اذ كانت كلها خالية من الصحة لانه يتحول الى بحر الرجز
        tid=[i for i in range(len(p)) if len([j for j in p[i] if j !="1"])!=6]
        tf=tf[tf.Tid.isin(tid)]
    elif sid==9:
        # استثناءات بحر مجزوء الكامل
        # استبعاد التفعيلات اذ كانت كلها خالية من الصحة لانه يتحول الى بحر الرجز
        tid=[i for i in range(len(p)) if len([j for j in p[i] if j !="1"])!=4]
        tf=tf[tf.Tid.isin(tid)]
    elif sid==11:
        # استثناءات بحر الهزج 
        # اذ وقع الكف امتنع القبض والعكس
        tf=get_zihaf_conflict(tf,p,2,"4","5")
    elif sid==14:
        # استثناءات بحر الرمل 
        # اذا كان الخبن في جزء امتنع الكف في الجزء الاخر
        tf=get_zihaf_conflict(tf,p,3,"4","5")
    elif sid==15:
        # استثناءات بحر مجزوء الرمل 
        # اذا كان الخبن في جزء امتنع الكف في الجزء الاخر
        tf=get_zihaf_conflict(tf,p,2,"4","5")
    elif sid==18:        
        # استثناءات بحر الخفيف 
        # اذ وقع الكف امتنع الخبن والعكس
        tf=get_zihaf_conflict(tf,p,3,"3","4")
    elif sid==19:        
        # استثناءات بحر مجزوء الخفيف 
        # اذ وقع الكف امتنع الخبن والعكس
        tf=get_zihaf_conflict(tf,p,2,"3","4")
    elif sid==20:        
        # استثناءات بحر المضارع 
        # اذ وقع الكف امتنع الخبن والعكس
        tf=get_zihaf_conflict(tf,p,2,"3","4")
    elif sid==23:        
        # استثناءات بحر المجتث 
        # اذ وقع الكف امتنع الخبن والعكس
        tf=get_zihaf_conflict(tf,p,2,"3","4")    
    elif sid==24:        
        # استثناءات بحر المتقارب 
        # زحاف القبض يمتنع اذا كان قبل العروض الابتر
        tid=[i for i in range(len(p)) if (p[i][2]=='5' and p[i][3]=='4')]
        tf=tf[~tf.Tid.isin(tid)]
    return tf


def get_all_patterns(sid,patt, p, tt, ttt,pt,ft):
    length=len(p[0])
    tid=[i for i in range(len(p))]
    
    if length==2:
        t=[[patt[i[0]], patt[i[1]]] for i in p]
        t = numpy.array(t)
        rawy, qafih=get_rway_qafiah([t[:,0][:,ft[0]][i]+t[:,1][:,ft[1]][i] for i in range(len(t))])
        tf=pd.DataFrame({'Sid':sid,'Tid':tid,'tcode':p,'type':tt , 'ttt':ttt ,'t1':t[:,0][:,2], 't2':t[:,1][:,0], 't3':'_',\
                         't4':'_', 't5':'_', 't6':'_','t7':'_','t8':'_','t11':t[:,0][:,pt[0]],'t12':t[:,1][:,pt[1]],'t13':'_',\
                         't14':'_', 't15':'_', 't16':'_','t17':'_','t18':'_','t21':t[:,0][:,ft[0]],'t22':t[:,1][:,ft[1]],\
                         't23':'0', 't24':'0', 't25':'0', 't26':'0','t27':'0','t28':'0','rawy':rawy, 'qafih':qafih})

        
    elif length==3:
        t=[[patt[i[0]], patt[i[1]],patt[i[2]]] for i in p]
        t = numpy.array(t)
        rawy, qafih=get_rway_qafiah([t[:,1][:,ft[1]][i]+t[:,2][:,ft[2]][i] for i in range(len(t))])
        tf=pd.DataFrame({'Sid':sid,'Tid':tid,'tcode':p,'type':tt ,'ttt':ttt,'t1':t[:,0][:,2],'t2':t[:,1][:,2],'t3':t[:,2][:,0],\
                         't4':'_', 't5':'_', 't6':'_','t7':'_','t8':'_','t11':t[:,0][:,pt[0]],'t12':t[:,1][:,pt[1]],\
                         't13':t[:,2][:,pt[2]],'t14':'_', 't15':'_', 't16':'_','t17':'_','t18':'_','t21':t[:,0][:,ft[0]],\
                         't22':t[:,1][:,ft[1]],'t23':t[:,2][:,ft[2]],'t24':'0', 't25':'0', 't26':'0','t27':'0','t28':'0',\
                         'rawy':rawy, 'qafih':qafih})
                         
    elif length==4:
        t=[[patt[i[0]], patt[i[1]],patt[i[2]],patt[i[3]]] for i in p]
        t = np.array(t)
        rawy, qafih=get_rway_qafiah([t[:,2][:,ft[2]][i]+t[:,3][:,ft[3]][i] for i in range(len(t))])
        tf=pd.DataFrame({'Sid':sid,'Tid':tid,'tcode':p,'type':tt , 'ttt':ttt ,'t1':t[:,0][:,2],'t2':t[:,1][:,0],\
                         't3':t[:,2][:,2],'t4':t[:,3][:,1], 't5':'_', 't6':'_','t7':'_','t8':'_','t11':t[:,0][:,pt[0]],\
                         't12':t[:,1][:,pt[1]],'t13':t[:,2][:,pt[2]],'t14':t[:,3][:,pt[3]],'t15':'_', 't16':'_','t17':'_',\
                         't18':'_','t21':t[:,0][:,ft[0]],'t22':t[:,1][:,ft[1]],'t23':t[:,2][:,ft[2]],'t24':t[:,3][:,ft[3]],\
                         't25':'0', 't26':'0','t27':'0','t28':'0','rawy':rawy, 'qafih':qafih})

    elif length==6:
        #print(p)
        t=[[patt[i[0]], patt[i[1]],patt[i[2]],patt[i[3]],patt[i[4]],patt[i[5]]] for i in p]
        t = np.array(t)
        rawy, qafih=get_rway_qafiah([t[:,4][:,ft[4]][i]+t[:,5][:,ft[5]][i] for i in range(len(t))])
        tf=pd.DataFrame({'Sid':sid,'Tid':tid,'tcode':p,'type':tt , 'ttt':ttt ,'t1':t[:,0][:,2],'t2':t[:,1][:,2],\
                         't3':t[:,2][:,0],'t4':t[:,3][:,2],'t5':t[:,4][:,2],'t6':t[:,5][:,1],'t7':'_','t8':'_',\
                         't11':t[:,0][:,pt[0]],'t12':t[:,1][:,pt[1]],'t13':t[:,2][:,pt[2]],'t14':t[:,3][:,pt[3]],\
                         't15':t[:,4][:,pt[4]],'t16':t[:,5][:,pt[5]],'t17':'_', 't18':'_',\
                         't21':t[:,0][:,ft[0]],'t22':t[:,1][:,ft[1]],'t23':t[:,2][:,ft[2]],'t24':t[:,3][:,ft[3]],\
                         't25':t[:,4][:,ft[4]],'t26':t[:,5][:,ft[5]],'t27':'0','t28':'0','rawy':rawy, 'qafih':qafih})
    elif length==8:
        t=[[patt[i[0]], patt[i[1]],patt[i[2]],patt[i[3]],patt[i[4]],patt[i[5]],patt[i[6]],patt[i[7]]] for i in p]
        #print(t)
        t = np.array(t)
        rawy, qafih=get_rway_qafiah([t[:,6][:,ft[6]][i]+t[:,7][:,ft[7]][i] for i in range(len(t))])
        tf=pd.DataFrame({'Sid':sid,'Tid':tid,'tcode':p,'type':tt , 'ttt':ttt ,'t1':t[:,0][:,2],'t2':t[:,1][:,2],\
                         't3':t[:,2][:,2],'t4':t[:,3][:,0],'t5':t[:,4][:,2],'t6':t[:,5][:,2],'t7':t[:,6][:,2],'t8':t[:,7][:,1],\
                         't11':t[:,0][:,pt[0]],'t12':t[:,1][:,pt[1]],'t13':t[:,2][:,pt[2]],'t14':t[:,3][:,pt[3]],\
                         't15':t[:,4][:,pt[4]],'t16':t[:,5][:,pt[5]],'t17':t[:,6][:,pt[6]],'t18':t[:,7][:,pt[7]],\
                         't21':t[:,0][:,ft[0]],'t22':t[:,1][:,ft[1]],'t23':t[:,2][:,ft[2]],'t24':t[:,3][:,ft[3]],\
                         't25':t[:,4][:,ft[4]],'t26':t[:,5][:,ft[5]],'t27':t[:,6][:,ft[6]],'t28':t[:,7][:,ft[7]],\
                         'rawy':rawy, 'qafih':qafih})
    return tf
#
def get_tafilah_pattern(sid,arod_drb_case,hshw_info,pattern):
    p1=[]; ad=int(hshw_info["count"]/2); n=0 ;arod_drb_cases=[];arod_drb_code=[]
    ### اختيار حالات تفعيلات الحشو كاملة
    p=[str(i) for i in range(hshw_info["start"],hshw_info["end"]+1)\
       if len([j for j in str(i) if j in hshw_info["case"]])==hshw_info["count"]]
    ### اضافة حالات تفعيلات العروض والضرب كاملة
    for i in arod_drb_case:
        n=0
        for d in arod_drb_case[i]:
            n=n+1            
            for j in p:
                p1.append(j[:ad]+d[0]+j[ad:]+d[1])
                arod_drb_cases.append(i)
                arod_drb_code.append(n)
    tf = get_all_patterns(sid,pattern,p1, arod_drb_cases, arod_drb_code,hshw_info["pt"],hshw_info["ft"])
    return tf,p1


def get_sea_pattern(sid):
    st=pd.read_csv('corpus/Seas_cases.csv',sep='\t',encoding='utf-16')
    s=st[(st.Sid==sid)]
    pattern={}
    # (العلل والزحافات) حصر جميع التفعيلات الجائزة للبحر
    for i in range(len(s)):
        pattern[str(s.iloc[i,2])]=[s.iloc[i,3],s.iloc[i,4],s.iloc[i,5],s.iloc[i,6],str(s.iloc[i,7]),str(s.iloc[i,8]),\
                                        str(s.iloc[i,9])]
    return pattern

def get_arrwth_info(sid):
    # اخذ حالات الضرب والعروض
    ad=ard_drb[(ard_drb.sids==sid)]
    arod_drb_case={}
    set(list(ad.aid))
    for i in set(list(ad.aid)):
        arod_drb_case[i]= [str(i) for i in list(ad[ad.aid==i].adc)]

    # اخذ تفاصيل الحشو
    hshw_info={}
    hshw_info["case"]= [str(i) for i in list(hsho_info[(hsho_info.sids==sid)].hc)]
    hshw_info["count"]= int(int(ver_info[(ver_info.sids==sid)]["count"]))
    hshw_info["start"]= int(ver_info[(ver_info.sids==sid)]["start"])
    hshw_info["end"]= int(ver_info[(ver_info.sids==sid)]["end"])
    hshw_info["pt"]= list(hsho_tfilah[(hsho_tfilah.sids==sid)].pt)
    hshw_info["ft"]= list(hsho_tfilah[(hsho_tfilah.sids==sid)].ft)
    return arod_drb_case,hshw_info

def get_pattern(sid):
    pattern=get_sea_pattern(sid)
    arod_drb_case,hshw_info=get_arrwth_info(sid)
    #print(arod_drb_case)
    #print(hshw_info)
    tf,p=get_tafilah_pattern(sid,arod_drb_case,hshw_info,pattern)
    return tf,p

def get_rway_qafiah(end_agz): #
    rawy=[]
    for i in end_agz:
        if i != "0":
           # print(i[-1])
            if i[-1]   == "0":    rawy.append(2)
            elif i[-2] == "0":    rawy.append(3)
            elif i[-3] == "0":    rawy.append(4)
            elif i[-3] == "0":    rawy.append(5)
            elif i[-4] == "0":    rawy.append(6)
        else:
            rawy.append("0")
    qafih = [i for i in rawy]

    for i in range(len(end_agz)): #
        if end_agz[i] != "0" :
            if end_agz[i][-qafih[i]]     == "0":     qafih[i]=qafih[i]+1 
            elif end_agz[i][-(qafih[i]+1)] == "0":    qafih[i]=qafih[i]+2
            elif end_agz[i][-(qafih[i]+2)] == "0":    qafih[i]=qafih[i]+3
            elif end_agz[i][-(qafih[i]+3)] == "0":    qafih[i]=qafih[i]+4
            elif end_agz[i][-(qafih[i]+4)] == "0":    qafih[i]=qafih[i]+5
            elif end_agz[i][-(qafih[i]+5)] == "0":    qafih[i]=qafih[i]+6
    return rawy, qafih
