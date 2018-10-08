import cv2
import numpy as np
import time


class ProcessBackglight:
    def __init__(self):
        self.blank=cv2.imread(__file__+"/../"+'perfmask.jpg',cv2.IMREAD_COLOR)
        self.blank=numpy.require(self.blank,dtype=numpy.float32)
        self.blank-=average(blank)

    def processFrame(self,img):
        corr=average(img*self.blank)
        if corr>0 :
            f=img-corr*self.blank
        else:
            f=img
        return f
        

class Deshaker:
    def __init__(self):
        self.mask=cv2.imread(__file__+"/../"+'perfmask.jpg',cv2.IMREAD_GRAYSCALE)
        self.msize=self.mask.shape
        self.expMask=cv2.copyMakeBorder(self.mask,0,self.msize[0],0,self.msize[1],cv2.BORDER_CONSTANT,value=128) # expand the mask and fill with gray
        self.spMask=np.conj(np.fft.fft2(self.expMask))
        self.offsFilt=np.array([[0.0,0.0] for i in range(16)])
        self.offsFiltCnt=0
        self.offsValidCnt=0

    def calcShift1(self,gimg1,sp2,y1,y2,x1,x2):
        sp1=np.fft.fft2(gimg1)
        sp1[0]=0
        sp=np.multiply(sp1,sp2)
        corr=np.real(np.fft.ifft2(sp))
        corr1=corr # corr[y1:y2,x1:x2]
        imax=np.argmax(corr1)
        sy,sx=corr1.shape
        offsY,offsX=divmod(imax,sx)
#        offsY+=y1
#        offsX+=x1
        return (offsY,offsX,corr)


    def calcShift2(self,img):
        leftIndex=img.shape[1]-self.msize[1]*3/2
        gimg = cv2.cvtColor(img[:,leftIndex:], cv2.COLOR_BGR2GRAY)
        pt=(self.expMask.shape[0]-gimg.shape[0])/2
        pb=self.expMask.shape[0]-gimg.shape[0]-pt
        pl=0
        pr=self.expMask.shape[1]-gimg.shape[1]
        gimg = cv2.copyMakeBorder(gimg,pt,pb,pl,pr,cv2.BORDER_CONSTANT,value=128)
        normY=pt
        normX=self.msize[1]/2
        offsY,offsX,corr=self.calcShift1(gimg, self.spMask,normY-70,normY+70,normX-15,normX+15)
        offsY-=normY
        offsX-=normX
        return (-offsY,-offsX,corr)

    def processFrame(self,img):
        offsY,offsX,corr=self.calcShift2(img)
        
#        offsValid = offsX>=-15 and offsX<=15 and offsY>=-70 and offsY<=70
        offsValid = True

        if not offsValid :
            offsY1,offsX1=self.offsFilt[self.offsFiltCnt]
        else :
            offsY1,offsX1=offsY,offsX
            self.offsFilt[self.offsFiltCnt]=np.array([offsY,offsX])*0.1+self.offsFilt[self.offsFiltCnt]*0.9
            self.offsValidCnt+=1
        print offsY,offsX,offsY1,offsX1,offsValid,self.offsValidCnt,self.offsFiltCnt,self.offsFilt[self.offsFiltCnt][0],self.offsFilt[self.offsFiltCnt][1]
        self.offsFiltCnt=(self.offsFiltCnt+1)&15

#        c0=np.amin(corr)
#        c1=np.amax(corr)
#        corr=(corr-c0)/(c1-c0)*1
#       return corr


        M = np.float32([[1,0,offsX1],[0,1,offsY1]])
        dst = cv2.warpAffine(img,M,(img.shape[1],img.shape[0]))
        return dst

if __name__ == '__main__':
    d = Deshaker()
    b = ProcessBackglight()

    cap = cv2.VideoCapture('test.avi')

    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = None 

    while(cap.isOpened()):

        ret, sf = cap.read()
        if not ret: break

        bf=b.processFrame(sf)
        df=d.processFrame(bf)
#        df=cv2.flip(df[48:-31,33:-20],1)
#        df=cv2.flip(df,1)

        if out is None:
            out=cv2.VideoWriter('test-res.avi', fourcc,16.0, (df.shape[1],df.shape[0]))
            # out=cv2.VideoWriter('test-res.avi', -1,16.0, (df.shape[1],df.shape[0]))
        out.write(df)

        cv2.imshow('sf',sf)
        cv2.imshow('df',df)
        key=cv2.waitKey(1)
        if key & 0xFF == ord('q'): break
        if key & 0xff == ord('p') :
            while True :
                key=cv2.waitKey(1)
                if key & 0xff == ord('c') : break
                time.sleep(1)

    out.release()
    cap.release()
    cv2.destroyAllWindows()

                                                                                                        