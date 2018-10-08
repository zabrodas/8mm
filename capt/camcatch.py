import wx
import cv2
import numpy
import serial
import sys
import glob
import time

steps=[
128,128,128,128,
128,128,128,128,
128,128,128,128,
128,128,128,128
]
stepindex=0

def getCamList():
    l=[]
    id=0
    print "getCamList"
    while True:
        try:
            vc=cv2.VideoCapture(id)
            if vc is None: break;
        except:
            break
        w=vc.get(cv2.CAP_PROP_FRAME_WIDTH)
        h=vc.get(cv2.CAP_PROP_FRAME_HEIGHT)
        vc.release()
        if w<=0 or h<=0: break
        descr="%s: %sx%s"%(id,w,h)
        l+=[{"id":id,"descr":descr}]
        id+=1
        if id>5: break
    return l

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

class MainFrame(wx.Frame):

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(MainFrame, self).__init__(None,title="Cam")
        
        self.camera=None
        self.videoOutput=None
        self.serial=None
        
        self.panel=wx.Panel(self)
        self.preview=wx.StaticBitmap(self.panel)

        tl=self.panel # wx.ToolBar(self.panel)
        selcam=wx.Choice(tl,name="Select camera")
        cl=getCamList()
        for i in range(len(cl)):
            selcam.Append(cl[i]["descr"])
        selcam.SetSelection(wx.NOT_FOUND)
        self.Bind(wx.EVT_CHOICE,self.OnCamSelected,selcam)
        
        self.capFrameBtn=wx.Button(tl, label="Frame")
        self.Bind(wx.EVT_BUTTON,self.OnFrameCaptureClicked,self.capFrameBtn)
        
        self.filenameToSave=None
        self.selectFileBtn=wx.Button(tl, label="<Select file>")
        self.Bind(wx.EVT_BUTTON,self.OnFileToSave,self.selectFileBtn)

        self.startCaptureBtn=wx.Button(tl, label="Start")
        self.Bind(wx.EVT_BUTTON,self.startCapturing,self.startCaptureBtn)
        self.stopCaptureBtn=wx.Button(tl, label="Stop")
        self.Bind(wx.EVT_BUTTON,self.stopCapturing,self.stopCaptureBtn)

        selSerial=wx.Choice(tl,name="Select port")
        for p in serial_ports(): selSerial.Append(p)
        selSerial.SetSelection(wx.NOT_FOUND)
        self.Bind(wx.EVT_CHOICE,self.serialConnect,selSerial)
        self.serialDisconnectBtn=wx.Button(tl, label="Serial disconnect")
        self.Bind(wx.EVT_BUTTON,self.serialDisconnect,self.serialDisconnectBtn)
        self.frameBackBtn=wx.Button(tl, label="[<")
        self.Bind(wx.EVT_BUTTON,self.frameBack,self.frameBackBtn)
        self.stepBackBtn=wx.Button(tl, label="<")
        self.Bind(wx.EVT_BUTTON,self.stepBack,self.stepBackBtn)
        self.stepForwardBtn=wx.Button(tl, label=">")
        self.Bind(wx.EVT_BUTTON,self.stepForward,self.stepForwardBtn)
        self.frameForwardBtn=wx.Button(tl, label=">]")
        self.Bind(wx.EVT_BUTTON,self.frameForward,self.frameForwardBtn)

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("Hello!")
        
        self.topSizer=wx.BoxSizer(wx.VERTICAL)
        toolSizer=wx.BoxSizer(wx.HORIZONTAL)
        toolSizer.Add(selcam,wx.ALL)
        toolSizer.Add(self.capFrameBtn,wx.ALL)
        toolSizer.Add(self.selectFileBtn,wx.ALL)
        toolSizer.Add(self.startCaptureBtn,wx.ALL)
        toolSizer.Add(self.stopCaptureBtn,wx.ALL)
        
        toolSizer.Add(selSerial,wx.ALL)
        toolSizer.Add(self.serialDisconnectBtn,wx.ALL)
        toolSizer.Add(self.frameBackBtn,wx.ALL)
        toolSizer.Add(self.stepBackBtn,wx.ALL)
        toolSizer.Add(self.stepForwardBtn,wx.ALL)
        toolSizer.Add(self.frameForwardBtn,wx.ALL)

        self.topSizer.Add(toolSizer,wx.ALL)
        self.topSizer.Add(self.preview,wx.ALL)
        self.panel.SetSizer(self.topSizer)
        self.topSizer.Fit(self)
       
        
    def OnCamSelected(self,event):
        self.SetStatusText("!!!!")

        if self.camera is not None:
            self.camera.release()
            self.camera=None
            self.SetStatusText("Stop camera")

        id=event.GetEventObject().GetSelection()
        if id<0 : return
            
        self.camera=cv2.VideoCapture(id)
        if not self.camera.isOpened():
            self.SetStatusText("Can't open camera %s"%id)
            self.camera.release()
            self.camera=None
            return
        
        self.SetStatusText("Start camera %s"%id)
        
    def OnFrameCaptureClicked(self,event):
        self.captureFrame()
        
    def captureFrame(self):
        if self.camera is None: return None
        ret,frame=self.camera.read()
        if not ret: return None
        h,w,c=frame.shape
        dt=frame.dtype
        data=frame.data # tobytes('C')
        bmp=wx.Bitmap.FromBuffer(w,h,data)
        ws=self.preview.GetSize()
        if w!=ws.x or h!=ws.y:
            self.preview.SetSize(0,0, w,h)
            self.topSizer.Fit(self)
            
        #dc=wx.ClientDC(self.preview)
        #dc.DrawBitmap(bmp,0,0)
        self.preview.SetBitmap(bmp)
        self.SetStatusText("w=%s h=%s c=%s, dt=%s"%(w,h,c,dt))
        return frame
        
    def OnFileToSave(self,event):
        dlg=wx.FileDialog(self,message="File to save video")
        if self.filenameToSave is not None:
            dlg.SetPath(self.filenameToSave)
        if dlg.ShowModal()==wx.ID_OK:
            self.filenameToSave=dlg.GetPath()
            self.selectFileBtn.SetLabel(self.filenameToSave)

    def startCapturing(self,event):
        if self.videoOutput is not None: return
        if self.filenameToSave is None: self.OnFileToSave(None)
        if self.filenameToSave is None: return
        if self.camera is None: return
        frame=self.captureFrame()
        if frame is None: return
        h,w,c=frame.shape
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.videoOutput=cv2.VideoWriter(self.filenameToSave, fourcc,16.0, (w,h))
        self.videoOutput.set(cv2.VIDEOWRITER_PROP_QUALITY,100)
#        self.videoOutput=cv2.VideoWriter(self.filenameToSave, -1,16.0, (w,h))
        self.capFrameCnt=0
        self.capTimer=wx.Timer(self)
        self.Bind(wx.EVT_TIMER,self.captureNextFrame,self.capTimer)
        self.capTimer.Start(0)
    
    def stopCapturing(self,event):
        if self.videoOutput is None: return
        self.capTimer.Stop()
        self.capTimer=None
        self.videoOutput.release()
        self.videoOutput=None
        cv2.destroyAllWindows()

    def captureNextFrame(self,event):
        if self.videoOutput is None: return
        ff=None
        for i in range(10):
            ret,frame=self.camera.read()
            if not ret:
                self.SetStatusText("Capture error")
                return
#            frame=cv2.flip(frame,0)
#            frame=cv2.flip(frame,1)
            if ff is None:
                h,w,c=frame.shape
                ff=numpy.require(frame,dtype=numpy.float32)
            else:
                ff+=frame
                #ff=numpy.minimum(ff,frame)
        ff/=10
        frame=numpy.require(ff,dtype=numpy.uint8)
        frame=cv2.flip(frame,1)

        self.frameForward(None)
        
        cv2.imshow('frame',frame)
        self.videoOutput.write(frame)
        self.capFrameCnt+=1
        self.SetStatusText("Frame %s"%self.capFrameCnt)

    def serialConnect(self,event):
        port=event.GetEventObject().GetString(event.GetEventObject().GetSelection())
        self.serialDisconnect(event)
        try:
            self.serial=serial.Serial(port,115200,timeout=10)
            print("Serial connected '%s'"%port)
        except:
            print("Can't connect serial '%s'"%port)
        
        
    def serialDisconnect(self,event):
        if self.serial is not None:
            self.serial.close()
            self.serial=None
            print("Serial disconnected")
    
    def frameBack(self,event):
        self.serialCommand("128-")
    def stepBack(self,event):
        self.serialCommand("4-")
    def stepForward(self,event):
        self.serialCommand("4+")
    def frameForward(self,event):
        global stepindex,steps
        ns=steps[stepindex]
        self.serialCommand("%s>"%ns)
        stepindex+=1
        stepindex&=15

    def serialCommand(self,cmd):
        if self.serial is None:
            print("Serial disconnected")
            return
        print "Send serial cmd=%s"%cmd
        self.serial.write(cmd)
        t0=time.time()
        while True:
            reply=self.serial.read()
            if reply==".": break
            if time.time()-t0>5:
                print "Serial cmd timeout"
                break
    
if __name__ == '__main__':
    app = wx.App()
    frm = MainFrame()
    frm.Show()
    app.MainLoop()