import numpy as np
from scipy import signal,sparse
import argparse as ap
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

opt=ap.ArgumentParser(description="Simulation of signal flare detection in a weak background.\nList of parameters to be used:")
opt.add_argument('--Nxy'      ,default = 100        ,type = int   ,help = "Dimension of large image - xyplane / default = 100")
opt.add_argument('--Nt'       ,default = 300        ,type = int   ,help = "Dimension of large image - tplane / default = 300")
opt.add_argument('--Mxy'      ,default = 20         ,type = int   ,help = "Dimension of template - xyplane / default = 20")
opt.add_argument('--Mt'       ,default = 16         ,type = int   ,help = "Dimension of template - tplane / default = 16")
opt.add_argument('--B'        ,default = 0.05       ,type = float ,help = "Noise expectation value / default = 0.05")
opt.add_argument('--decaycst' ,default = 0.5        ,type = float ,help = "Decay constant of template signal / default = 0.5")
opt.add_argument('--F'        ,default = 5          ,type = float ,help = "Norm of template signal / default = 5")
opt.add_argument('--psfwidth' ,default = 2          ,type = float ,help = "PSF width / default = 2")
opt.add_argument('--sigloc'   ,default = [20,40,60] ,type = int   ,help = "To specify default simulated signal location in large image use:\n --sigloc X --sigloc Y --sigloc Z / default = [20,40,60]" ,action = 'append' )
opt.add_argument('--beta'     ,default = 0.001      ,type = float ,help = "False positive alarm value / default = 0.001")
opt.add_argument('--N_tries'  ,default = 10         ,type = int   ,help = "Number of tries for completeness / default = 10")
opt.add_argument('--getTH'    ,default = 1          ,type = int   ,help = "If 1 job will calculate threshold, if 0 job will calculate completeness" ,choices=[0,1])

args=opt.parse_args()
print "Parameters used:"
print args

Nxy=args.__dict__["Nxy"]
Nt=args.__dict__["Nt"]
Mxy=args.__dict__["Mxy"]
Mt=args.__dict__["Mt"]
B=args.__dict__["B"]
decaycst=args.__dict__["decaycst"]
F=args.__dict__["F"]
psfwidth=args.__dict__["psfwidth"]
if len(args.__dict__["sigloc"])>3: #stupid patch because 'append' action doesn't override default
    [x_tsig,y_tsig,z_tsig]=args.__dict__["sigloc"][3:]
else:
    [x_tsig,y_tsig,z_tsig]=args.__dict__["sigloc"]
beta=args.__dict__["beta"]
N_tries=args.__dict__["N_tries"]
getTH=args.__dict__["getTH"]

def main():
    ## This script has two tasks:
    ## First run with getTH=1 to calculate the threshold values for given parameters
    ## Then run with getTH=0 to calculate the completeness for a given flux value
    tag="B-%s"%B+"__decaycst-%s"%decaycst+"__psfwidth-%s"%psfwidth+"__beta-%s"%beta+"__N_tries-%s"%N_tries
    if getTH==0:
        tag="F-%s__"%F+tag
    print "\nTAGNAME:",tag
    ## Get signal template (normalized)
    tsig=makeTemplate()
    ## Get thresholds
    if getTH==1:
        make2Dsliceplot(tsig,'x',Mxy/2,"Template signal",tag)
        make2Dsliceplot(tsig,'z',Mt/2,"Template signal",tag)
        ## Get image filled with bkg and mean subtracted + noise_avg value
        image,noise_avg=makeImage('large')
        make2Dsliceplot(image,'x',Nxy/2,"Image filled with noise and mean subtracted",tag)
        ## Find threshold values for F and S
        Fth,Sth=getFluxThreshold(image,tsig,tag,True)
        ## Find threshold value for S in Gaussian approx
        Sth_G=getFluxThresholdGauss(image,tsig,tag,True)
        ## Fill result file with parameters in name
        f=open("results/"+tag+".txt",'a')
        f.write("noise_avg %s\n"%noise_avg)
        f.write("Fth %s\n"%Fth)
        f.write("Sth %s\n"%Sth)
        f.write("Sth_G %s\n"%Sth_G)
        f.write("\nFlux, Completeness, Completeness_Gauss\n")
        f.close()
    ## Get completeness
    elif getTH==0:
        ## Retreive noise_avg and threshold values
        tag0=tag.split('__',1)[1]
        f=open("results/"+tag0+".txt")
        for l in f.readlines():
            if l.startswith("noise_avg "): noise_avg=float(l.split()[1])
            if l.startswith("Fth "): Fth=float(l.split()[1])
            if l.startswith("Sth "): Sth=float(l.split()[1])
            if l.startswith("Sth_G "): Sth_G=float(l.split()[1])
        f.close()
        ## Get filter (for Poisson case only, since in Gaussian case the filter is the template signal)
        filt=makeFilter(tsig,Fth)
        ## Calculate completeness and compare to Gaussian case
        successrate=[]
        successrate_G=[]
        N_tried=0
        countsuccess=0
        countsuccess_G=0
        print "\nRunning completeness check"
        while(N_tried!=N_tries):
            N_tried+=1
            ## Get simulated signal with relevant flux
            ssig=makeSimSignal(tsig,F)
            ## Get 'small' image of "bkg + sim. signal - mean(bkg)" of the size of the template
            image=makeImage('small',ssig,noise_avg=noise_avg)
            ## Get sum of element by element multiplication of this image with filter (= S)
            S=getFiltNorm(image,filt)
            ## Get sum of element by element multiplication of this image with template signal (= S_G)
            S_G=getFiltNorm(image,tsig)
            ## Count number of succeses
            if S>Sth:
                countsuccess+=1
            if S_G>Sth_G:
                countsuccess_G+=1
        print "Done"
        ## Write to result file
        f=open("results/"+tag0+".txt",'a')
        f.write("%s, %s, %s\n"%(F,countsuccess/float(N_tries),countsuccess_G/float(N_tries)))
        f.close()

################################-ListOfFunctions-###############################################################
################################################################################################################

## Get threshold for S in case of Gaussian matched filter, same input and options as above
def getFluxThresholdGauss(image,tsig,tag,showPDF=False):
    print "Getting Sth in Gaussian approx:"
    mf=crossCorrelate(image,tsig)
    Sth=np.percentile(mf.flatten(),(1-beta)*100.0)
    print "Sth =","%.2g"%Sth,"\n"
    if showPDF:
        fig=plt.figure()
        ax=fig.add_subplot(111)
        hist,bin_edges=np.histogram(mf.flatten(),200,density=True)
        plt.plot(bin_edges[:-1],hist)
        plt.yscale('log')
        title="PDF of S - Gaussian case"
        plt.title(title)
        # plt.show()
        plt.savefig("plots/%s/%s.png"%(tag,title))
        plt.close(fig)
    return Sth

## Implement iteration to find optimal threshold values of F and S
## Input should be a 'large' image filled with bkg noise and a template signal
## Option to plot the PDF of S
def getFluxThreshold(image,tsig,tag,showPDF=False):
    print "Getting Fth and Sth:"
    Fth=100
    converged=False
    while(not converged):
        print "Fth =",Fth
        filt=makeFilter(tsig,Fth)
        SF=getFiltNorm(tsig,filt)
        print "SF =",SF
        mf=crossCorrelate(image,filt)
        Sth=np.percentile(mf.flatten(),(1-beta)*100.0) ## Get current Sth as a function of the chosen false positive alarm
        print "Sth =",Sth
        Fth_new=Sth/SF+B
        print "Fth_new =",Fth_new,"\n"
        if (abs(Fth-Fth_new)<0.01*Fth): converged=True
        Fth=Fth_new
    print "Fth =","%.2f"%Fth,"Sth =","%.2f"%Sth,"\n"
    if showPDF:
        fig=plt.figure()
        ax=fig.add_subplot(111)
        hist,bin_edges=np.histogram(mf.flatten(),200,density=True)
        plt.plot(bin_edges[:-1],hist)
        plt.yscale('log')
        title="PDF of S"
        plt.title(title)
        # plt.show()
        plt.savefig("plots/%s/%s.png"%(tag,title))
        plt.close(fig)
    return Fth,Sth

## Return filter for Poisson matched filtering based on formula described above
def makeFilter(tsig,flux=None):
    if flux is None: flux=F
    filt=np.zeros((Mxy,Mxy,Mt))
    for i in range(Mxy):
        for j in range(Mxy):
            for t in range(Mt):
                filt[i][j][t]=np.log(1+flux*tsig[i][j][t]/B)
    return filt
## Parameters:
## tsig : template signal
## flux : desired overall signal flux, defaults as F

## Return simulated signal from template
## This simulates the detector response to the template signal scaled to a given flux
def makeSimSignal(tsig,f=None,t=None):
    if f is None: f=F
    if t is None: t=1
    ssig=np.zeros((Mxy,Mxy,Mt))
    for i in range(Mxy):
        for j in range(Mxy):
            for t in range(Mt):
                ssig[i][j][t]=np.random.poisson(f*t*tsig[i][j][t])
    return ssig
## Parameters:
## tsig is the template signal from above
## f is the desired overall signal flux, default is F
## t is the exposition time between two images, default is 1

## Return normalized template signal of size Mxy*Mxy*Mt
## The template signal is a PSF in the xy plane and exponentially decaying in the z-direction
def makeTemplate():
    tsig=np.zeros((Mxy,Mxy,Mt))
    for t in range(2,Mt):
        tnorm=np.exp(-decaycst*t)
        for i in range(Mxy):
            for j in range(Mxy):
                tsig[i][j][t]=(tnorm/np.sqrt(2*np.pi*psfwidth**2))*np.exp(-((i-Mxy/2.)**2+(j-Mxy/2.)**2)/(2*psfwidth**2))
    tsig/=float(np.sum(tsig))
    return tsig

## Return 3D image filled with noise, subtract average, add signal
def makeImage(size,ssig=None,noise_avg=None,x=x_tsig,y=y_tsig,z=z_tsig):
    if size=='large': nx=Nxy; ny=Nxy; nt=Nt;
    elif size=='small': nx=Mxy; ny=Mxy; nt=Mt;
    else: print "size:",size
    image=np.random.poisson(B,(nx,ny,nt))
    if size=='large' and noise_avg is None:
        noise_avg=np.mean(image)
        returnAVG=True
    else:
        returnAVG=False
    image=image-noise_avg
    if not ssig is None:
        for i in range(Mxy):
            for j in range(Mxy):
                for t in range(Mt):
                    if size=='large':
                        image[i+x-Mxy/2][j+y-Mxy/2][t+z-Mt/2]+=ssig[i][j][t]
                    else:
                        image[i][j][t]+=ssig[i][j][t] ## image and ssig have the same size
    if returnAVG:
        return image,noise_avg
    else:
        return image
## Parameters:
## size : size of returned image. If size=='large' -> Nxy*Nxy*Nt ; If size == 'small' -> Mxy*Mxy*Mt
## noise_avg : average of the bkg to be subtracted ; when left to None it is calculated from current generated image
## ssig : simulated signal to add to the bkg filled image, must be of dimension Mxy*Mxy*Mt. Default is None
## x,y,z: index location of where to add the signal - relevant only if size == 'large' and ssig is not None
## Note:
## The first time we run this function is to generate a 'large' image with bkg only, and we calculate the noise_avg 
## value that will be subtracted everytime this function is called again

## Sum of element by element multiplication of 2 matrices of same size
## Used for template signal * filter
## Used for image*filter when image is 'small' instead of cross-correlation
def getFiltNorm(im,filt):
    return np.sum(np.multiply(im,filt))

## Return built-in cross-correlation between two arrays
def crossCorrelate(image,filt):
    ## cross-correlate image and filter
    mf=signal.correlate(image,filt,'same')
    return mf

## Plot 2D colormap plot of 3D array sliced at desired axis and axis value
def make2Dsliceplot(ar3D,slax,val,title,tag):
    if slax=='x': ar2D=ar3D[val,:,:]
    if slax=='y': ar2D=ar3D[:,val,:]
    if slax=='z': ar2D=ar3D[:,:,val]
    fig=plt.figure()
    ax=fig.add_subplot(111)
    plt.imshow(ar2D,interpolation='nearest')
    plt.colorbar(orientation='vertical')
    title="%s for %s=%s"%(title,slax,val)
    plt.title(title)
    # plt.show()
    plt.savefig("plots/%s/%s.png"%(tag,title))
    plt.close(fig)
##Parameters
## ar3D : the 3D array
## slax : axis to slice on, either 'x','y' or 'z'
## val : axis value to slice on
## title : plot description

if __name__=="__main__":
    main()
