import cv2
import numpy as np
import time
import math
import sys

class ProcessBackglight:
    def __init__(self):
        self.blank=cv2.imread(__file__+"/../"+'blank.jpg',cv2.IMREAD_COLOR)
        self.blank=np.require(self.blank,dtype=np.float32)
        avg=np.average(self.blank)
        self.blank=avg/self.blank

    def startAnl(self):
        self.blank=None

    def analyseFrame(self,img):
        if self.blank is None :
            self.blank=np.require(img,dtype=np.float32)
            self.cnt=1
        else :
            self.blank+=img
            self.cnt+=1
        return np.require(np.clip(self.blank/self.cnt,0,255),dtype=np.uint8)

    def stopAnl(self):
        self.blank/=self.cnt
        avg=np.average(self.blank)
        self.blank=avg/self.blank

    def processFrame(self,img):
        f=img*self.blank
        f=np.require(np.clip(f,0,255),dtype=np.uint8)
        return f
        
if __name__ == '__main__':
    print sys.argv
    if len(sys.argv)!=3: raise Exception("Usage: %s src dst"%(sys.argv[0]))

    b = ProcessBackglight()

    if False :
        cap = cv2.VideoCapture(sys.argv[1])
        b.startAnl()
    
        while(cap.isOpened()):
    
            ret, sf = cap.read()
            if not ret: break
    
            df=b.analyseFrame(sf)
    
            cv2.imshow('sf',sf)
            cv2.imshow('df',df)
            key=cv2.waitKey(1)
            if key & 0xFF == ord('q'): break
            if key & 0xff == ord('p') :
                while True :
                    key=cv2.waitKey(1)
                    if key & 0xff == ord('c') : break
                    time.sleep(1)
    
        b.stopAnl()

    cap = cv2.VideoCapture(sys.argv[1])

    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = None 

    while(cap.isOpened()):

        ret, sf = cap.read()
        if not ret: break

        df=b.processFrame(sf)

        if out is None:
            out=cv2.VideoWriter(sys.argv[2], fourcc,16.0, (df.shape[1],df.shape[0]))
            out.set(cv2.VIDEOWRITER_PROP_QUALITY,100)
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

                                                                                                        