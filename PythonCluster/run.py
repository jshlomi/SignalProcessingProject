import os
from sys import argv
from numpy import mean,std,linspace
import matplotlib.pyplot as plt
from subprocess import PIPE, Popen

farmuser='mattiasb'

if len(argv)<2 or argv[1] not in ['submit','read','submitSTD','readSTD']:
    print "Provide run-mode: 'submit' or 'read'"
    exit()
runmode=argv[1]
if len(argv)==3 and runmode=='read' and argv[2]=='resubmit':
    resubmit=True
else: resubmit=False

if 'run.py' not in os.listdir(os.getcwd()):
    print "Run from own working directory"
    exit()

def cmdline(command):
    process = Popen(
        args=command,
        stdout=PIPE,
        shell=True
    )
    return process.communicate()[0],process.returncode

def mkdir(path):
    tmppath="."
    for d in path.split("/"):
        tmppath+="/"+d
        if not os.path.exists(tmppath):
            os.mkdir(tmppath)
mkdir("results")
mkdir("utils/subfiles")
mkdir("logs/farm")
mkdir("plots")

def submitjob(tag,F,B,decaycst,psfwidth,beta,calcmode):
    if RUNTEST:
        subftemp=open("utils/submittest_template.sh")
    else:
        subftemp=open("utils/submit_template.sh")
    subf=open("utils/subfiles/%s.sh"%tag,'w')
    for l in subftemp.readlines():
        subf.write(
            l.replace("TAG",tag)
            .replace("PATH",os.getcwd())
            .replace("FFF","%s"%F)
            .replace("BBB","%s"%B)
            .replace("DDD","%s"%decaycst)
            .replace("PPP","%s"%psfwidth)
            .replace("EEE","%s"%beta)
            .replace("NNN","%s"%N_tries)
            .replace("GGG","%s"%calcmode)
        )
    subftemp.close()
    subf.close()
    if calcmode=='thr':
        returncode=-1
        while(returncode!=0):
            out,returncode=cmdline("qsub utils/subfiles/%s.sh"%tag)
        print tag,":",out.strip()
        ## Create result file and store job ID
        f=open("results/"+tag+".txt",'w')
        f.write("jobID %s\n"%out.split('.')[0])
    elif calcmode=='comp':
        ## Get jobID of threshold job of this tag then submit with dependency
        tag0=tag.split('__',1)[1]
        f=open("results/"+tag0+".txt")
        for l in f.readlines():
            if l.startswith("jobID"):
                jobID=l.split()[1]
        returncode=-1
        while(returncode!=0):
            ## Check if th job completed, else submit on hold
            rcode=-1
            while(rcode!=0):
                check,rcode=cmdline("qstat -u %s"%farmuser)
            if jobID not in check:
                out,returncode=cmdline("qsub utils/subfiles/%s.sh"%tag)
            elif jobID in check:
                out,returncode=cmdline("qsub -W depend=afterok:%s utils/subfiles/%s.sh"%(jobID,tag))
        print tag,":",out.strip()
    elif calcmode=='thrSTD':
        f=open("results/%s_thrSTD.csv"%tag,'w')
        f.write("Fth, Sth, Sth_G\n")
        ## Submit multiple times the same job
        trynumber=0
        for i in range(N_tries):
            returncode=-1
            while(returncode!=0):
                out,returncode=cmdline("qsub utils/subfiles/%s.sh"%tag)
            print out.strip()

def checkresult(tag):
    if os.path.exists("results/%s"%tag) and os.path.getsize("results/%s"%tag)>0:
        return True
    else: return False
    
class Experiment():
    def __init__(self,tag,runmode):
        self.tag=tag
        self.paramdct=self.getParameters(tag) #{B,decaycst,psfwidth,beta}
        if runmode=='read':
            self.outdct=self.getResults(tag) #{'Fth':, 'Sth':, 'Sth_G':, 'xlist':[], 'ylist':[], 'ylist_G':[]}
        elif runmode=='readSTD':
            self.outdct=self.getResultsSTD(tag)
        self.fillOutTable()

    def getResultsSTD(self,tag):
        yo=1
        
    def fillOutTable(self):
        fill=True
        B=self.paramdct['B']
        decaycst=self.paramdct['decaycst']
        psfwidth=self.paramdct['psfwidth']
        beta=self.paramdct['beta']
        Sth=self.outdct['Sth']
        Sth_G=self.outdct['Sth_G']
        Fth=self.outdct['Fth']
        if not os.path.isfile("plots/out.csv"):
            f=open("plots/out.csv",'w')
            f.write("B, decaycst, psfwidth, beta, F_th, S_th, S_th_G\n")
            f.close()
        else:
            f=open("plots/out.csv",'r')
            for l in f.readlines():
                if l.startswith("%s, %s, %s, %s, %s, %s, %s"%(B,decaycst,psfwidth,beta,Fth,Sth,Sth_G)):
                    fill=False
            f.close()
        if fill:
            f=open("plots/out.csv",'a')
            f.write("%s, %s, %s, %s, %s, %s, %s\n"%(B,decaycst,psfwidth,beta,Fth,Sth,Sth_G))
            f.close()

    def getResults(self,tag):
        dct={'xlist':[],'ylist':[],'ylist_G':[]}
        thlist=['Fth','Sth','Sth_G']
        xlist=[]
        ylist=[]
        ylist_G=[]
        for l in open("results/%s.txt"%tag):
            for r in thlist:
                if l.startswith(r+" "):
                    thlist.pop(thlist.index(r))
                    dct[r]=float(l.split()[1])
            try:
                vals=l.split(',')
                ### PATCH TO CHOOSE XMAX
                xmax=12
                if float(vals[0])>xmax: continue
                ### END
                xlist.append(float(vals[0]))
                ylist.append(float(vals[1]))
                ylist_G.append(float(vals[2]))
            except: continue
        if thlist:
            print "WARNING: Missing parameters %s for %s"%(reslist,tag)
            if resubmit:
                returncode=-1
                while(returncode!=0):
                    out,returncode=cmdline("qsub utils/subfiles/%s.sh"%tag)
                    print tag,":",out.strip()
        for f in fluxes:
            if f not in xlist and f<=xmax:
                print "WARNING: Missing values for F-%s__%s"%(f,tag)
                if resubmit:
                    returncode=-1
                    while(returncode!=0):
                        out,returncode=cmdline("qsub utils/subfiles/F-%s__%s.sh"%(f,tag))
                    print tag,":",out.strip()
            tmplist=[]
            tmplist_G=[]
            for i in range(len(xlist)):
                if xlist[i]==f:
                    tmplist.append(ylist[i])
                    tmplist_G.append(ylist_G[i])
            dct['xlist'].append(f)
            dct['ylist'].append(mean(tmplist))
            dct['ylist_G'].append(mean(tmplist_G))
        # dct['xlist'],dct['ylist'],dct['ylist_G']=zip(*sorted(zip(dct['xlist'],dct['ylist'],dct['ylist_G'])))
        return dct
        
    def getParameters(self,tag):
        dct={}
        for k in tag.split("__"):
            dct[k.split('-')[0]]=float(k.split('-',1)[1])
        return dct

### ----------- Main Loop ----------------------------------------- ###
RUNTEST=True
# RUNTEST=False
if RUNTEST: print "RUNNING TEST"

# fluxes=[0,0.5,1,2]#,3,4,5,6,8,10,12,14,16,18,20,22,24,26,30]
fluxes=linspace(0,30,61)

paramdct_base={
    'B' : 0.005,
    'decaycst' : 0.5,
    'psfwidth' : 2.0,
    'beta' : 0.001
}

bkgmeans=[0.005,0.05,0.1]
decaycsts=[0.2,0.5,0.8,0.]
psfwidths=[2,3,4]
betas=[0.00001,0.001,0.1]

if 'STD' in runmode:
    N_tries=100
else:
    N_tries=100000

if RUNTEST:
    N_tries=10
    fluxes=[0,5,10]

if os.path.isfile("plots/out.csv"): os.remove("plots/out.csv")
Rlist=[]
submitbase=True
modeSTDdone=False
for varparam,vplist in {'B':bkgmeans,'decaycst':decaycsts,'psfwidth':psfwidths,'beta':betas}.iteritems():
    if modeSTDdone: break
    for i in range(len(vplist)):
        B=paramdct_base['B'] if (varparam!='B' or 'STD' in runmode) else vplist[i]
        decaycst=paramdct_base['decaycst'] if (varparam!='decaycst' or 'STD' in runmode) else vplist[i]
        psfwidth=paramdct_base['psfwidth'] if (varparam!='psfwidth' or 'STD' in runmode) else vplist[i]
        beta=paramdct_base['beta'] if (varparam!='beta' or 'STD' in runmode) else vplist[i]
        tag="B-%s"%B+"__decaycst-%s"%decaycst+"__psfwidth-%s"%float(psfwidth)+"__beta-%s"%beta+"__N_tries-%s"%N_tries
        mkdir("plots/%s"%tag)
        if runmode=='submit':
            if vplist[i]==paramdct_base[varparam]: ## Make sure to submit base only once
                if submitbase: submitbase=False
                else: continue
            ## Submit job to calculate thresholds
            submitjob(tag,-1,B,decaycst,psfwidth,beta,'thr')
            for f in fluxes:
                ## Submit jobs to calculate completeness per flux
                tagF="F-%s__"%float(f)+tag
                submitjob(tagF,f,B,decaycst,psfwidth,beta,'comp')
        elif runmode=='read':
            if not checkresult(tag+".txt"):
                print "WARNING: missing or empty file: results/%s.txt"%tag
                continue
            Rlist.append(Experiment(tag,runmode)) ## Save all data for plotting in list of 'Experiments'
        elif runmode=='submitSTD':
            submitjob(tag,-1,B,decaycst,psfwidth,beta,'thrSTD')
            modeSTDdone=True
            break
        elif runmode=='readSTD':
            if not checkresult(tag+"_thrSTD.csv"):
                print "WARNING: missing or empty file: results/%s_thrSTD.csv"%tag
                continue
            modeSTDdone=True
            break
### ---------------------------------------------------- ###        

def makeplot(paramdct,ax,xlist,ylist,Sth,Fth,ylist_G=None,Sth_G=None):
    ax.plot(xlist,ylist,label="Poisson\nS_th = %.2g - F_th = %.2g"%(Sth,Fth))
    if ylist_G:
        ax.plot(xlist,ylist_G,label="Gauss - S_th = %.2g"%Sth_G)
    ax.legend(shadow=False,loc='lower right',prop={'size':10})
    title=""
    for k,v in paramdct.iteritems():
        title=title+" %s = %2g "%(k,v)
    ax.set_title(title,size=10,y=-0.25)

def makeThrHist(axarr,paramdct,rows):
    Fths=[]
    Sths=[]
    Sth_Gs=[]
    for r in rows:
        r=r.split(',')
        Fths.append(float(r[0]))
        Sths.append(float(r[1]))
        Sth_Gs.append(float(r[2]))
        if not Sth_Gs[-1]:
            print "BADLINE:",r
            raw_input()
    plotvals=[Fths,Sths,Sth_Gs]
    plotnames=["Poisson - F_th\nmean %.2g, std %.2g"%(mean(Fths),std(Fths)),"Poisson - S_th\nmean %.2g, std %.2g"%(mean(Sths),std(Sths)),"Gauss - S_th\nmean %.2g, std %.2g"%(mean(Sth_Gs),std(Sth_Gs))]
    plotcolors=['green','red','blue']
    for i in range(3):
        vals=plotvals[i]
        ax=axarr[i]
        ax.hist(vals,50,normed=True,facecolor=plotcolors[i],alpha=0.75,label=plotnames[i])
        ax.legend(shadow=False,loc='upper right',prop={'size':10})
        title=""
        for k,v in paramdct.iteritems():
            title=title+" %s = %2g "%(k,v)
        ax.set_title(title,size=10,y=-0.25)
    
def getplot(xvar,paramdct,ax,showGauss=False):
    for e in Rlist:
        select=True
        for k,v in e.paramdct.iteritems():
            if k in [xvar,'N_tries']: continue
            if v!=paramdct[k]:
                select=False
                break
        if select:
            xlist=e.outdct['xlist']
            ylist=e.outdct['ylist']
            Sth=e.outdct['Sth']
            Fth=e.outdct['Fth']
            if showGauss:
                ylist_G=e.outdct['ylist_G']
                Sth_G=e.outdct['Sth_G']
            else:
                ylist_G=None
                Sth_G=None
            break
    makeplot(paramdct,ax,xlist,ylist,Sth,Fth,ylist_G,Sth_G)

### ----- Make Plots ---------------------------------------- ###    
if runmode=='read':
    for varparam,vplist in {'B':bkgmeans,'decaycst':decaycsts,'psfwidth':psfwidths,'beta':betas}.iteritems(): ## Loop on varying parameter
        f,axarr=plt.subplots(1,3,figsize=(15,4))#,sharey=True)
        for i in range(3): ## Loop on varying parameter's values
            paramdct={}
            for k,v in paramdct_base.iteritems():
                if k==varparam:
                    paramdct[k]=vplist[i] 
                else:
                    paramdct[k]=v
            # print paramdct
            getplot('F',paramdct,axarr[i],True)
        plt.suptitle("Completeness VS Flux - Varying \'%s\'"%varparam)
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)
        # plt.show()
        plt.savefig("plots/%s.png"%varparam)
elif runmode=='readSTD':
    B=paramdct_base['B']
    beta=paramdct_base['beta']
    decaycst=paramdct_base['decaycst']
    psfwidth=paramdct_base['psfwidth']
    tag="B-%s"%B+"__decaycst-%s"%decaycst+"__psfwidth-%s"%float(psfwidth)+"__beta-%s"%beta+"__N_tries-%s"%N_tries
    f=open("results/"+tag+"_thrSTD.csv")
    lines=f.readlines()
    f.close()
    f,axarr=plt.subplots(1,3,figsize=(15,4))
    makeThrHist(axarr,paramdct_base,lines[1:])
    plt.suptitle("Threshold distributions")
    plt.tight_layout()
    plt.subplots_adjust(top=0.85)
    # plt.show()
    plt.savefig("plots/%s_thrSTD.png"%tag)
### ---------------------------------------------------- ###        
