import  wx
import  wx.grid as gridlib
import time
import datetime
import threading
import serial
import sys
import random

global start_time

COM_PORT=4
ROWS    =30
tag_data={}
tag_time={}

#---------------------------------------------------------------------------
class CustomStatusBar(wx.StatusBar):
    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent, -1)

        # This status bar has three fields
        self.SetFieldsCount(2)
        # Sets the three fields to be relative widths to each other.
        self.SetStatusWidths([-1,-1])
        
                
        # Field 0 ... just text
        self.SetStatusText("SITPL Demo Application", 0)


        # We're going to use a timer to drive a 'clock' in the last
        # field.
        #self.timer = wx.PyTimer(self.Notify)
        #self.timer.Start(1000)
        #self.Notify()


    # Handles events from the timer we started in __init__().
    # We're using it to drive a 'clock' in field 2 (the third field).
    def Notify(self):
        t = time.localtime(time.time())
        st = time.strftime("%d-%b-%Y   %H:%M:%S", t)
        self.SetStatusText(st, 1)
        

#---------------------------------------------------------------------------
class CustomDataTable(gridlib.PyGridTableBase):
    def __init__(self,data):
        self.data= data
        gridlib.PyGridTableBase.__init__(self)
        self.colLabels = ['Tag ID', 'User Name', 'Start Time', 'Crossed Time', 'Elapsed Time']
        self.dataTypes = [gridlib.GRID_VALUE_NUMBER,
                          gridlib.GRID_VALUE_STRING,
                          gridlib.GRID_VALUE_STRING,
                          gridlib.GRID_VALUE_STRING,
                          gridlib.GRID_VALUE_STRING,
                          ]


    def GetNumberRows(self):
        return len(self.data)
    def GetNumberCols(self):
        return len(self.data[0])
    def IsEmptyCell(self, row, col):
        try:
            return not self.data[row][col]
        except IndexError:
            return true
    def GetValue(self, row, col):
        try:
            return self.data[row][col]
        except IndexError:
            return ''

    def Update(self):
        self.GetView().BeginBatch() 
        msg = gridlib.GridTableMessage(self, gridlib.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.GetView().ProcessTableMessage(msg)
        
        
        self.GetView().EndBatch()      



    def SetValue(self, row, col, value):
        def innerSetValue(row, col, value):
            try:
                self.data[row][col] = value
            except IndexError:
                # add a new row
                self.data.append([''] * self.GetNumberCols())
                innerSetValue(row, col, value)

                # tell the grid we've added a row
                msg = gridlib.GridTableMessage(self,            # The table
                        gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED, # what we did to it
                        1                                       # how many
                        )

                self.GetView().ProcessTableMessage(msg)
        innerSetValue(row, col, value)

#--------------------------------------------------
    # Some optional methods

    # Called when the grid needs to display labels
    def GetColLabelValue(self, col):
        return self.colLabels[col]

    # Called to determine the kind of editor/renderer to use by
    # default, doesn't necessarily have to be the same type used
    # natively by the editor/renderer if they know how to convert.
    def GetTypeName(self, row, col):
        return self.dataTypes[col]

    # Called to determine how the data can be fetched and stored by the
    # editor and renderer.  This allows you to enforce some type-safety
    # in the grid.
    def CanGetValueAs(self, row, col, typeName):
        colType = self.dataTypes[col].split(':')[0]
        if typeName == colType:
            return True
        else:
            return False

    def CanSetValueAs(self, row, col, typeName):
        return self.CanGetValueAs(row, col, typeName)





#---------------------------------------------------------------------------
class CustTableGrid(gridlib.Grid):
    def __init__(self, parent, data):
        gridlib.Grid.__init__(self, parent, -1)
        self.table = CustomDataTable(data)
        self.SetTable(self.table, True)
        self.SetRowLabelSize(0)
        self.SetMargins(0,0)
        self.AutoSizeColumns(False)
        gridlib.EVT_GRID_CELL_LEFT_DCLICK(self, self.OnLeftDClick)

        self.red_attr=gridlib.GridCellAttr()
        self.red_attr.SetBackgroundColour("red")

        self.white_attr=gridlib.GridCellAttr()
        self.white_attr.SetBackgroundColour("white")


##        self.table.SetCellTextColour(1, 1, "red")
##        grid.SetCellFont(1,1, wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
##        grid.SetCellBackgroundColour(2, 2, "light blue")
##        attr = wx.grid.GridCellAttr()
##        attr.SetTextColour("navyblue")
##        attr.SetBackgroundColour("pink")
##        attr.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
##        grid.SetAttr(4, 0, attr)
##        grid.SetAttr(5, 1, attr)
##        grid.SetRowAttr(8, attr)

    def OnLeftDClick(self, evt):
        if self.CanEnableCellControl():
            self.EnableCellEditControl()

    def Update(self):
        print "In Update"
        print tag_time
        self.table.Update()
        for i in range(1,ROWS+1):
            if(tag_time[i]==0):
                self.SetAttr((i-1),4,self.red_attr)
                self.red_attr.IncRef()
            else:
                self.SetAttr((i-1),4,self.white_attr)
                self.white_attr.IncRef()
                


#---------------------------------------------------------------------------
class Tag(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._read_port=True
        self.setDaemon(1)
        self.master_port=serial.Serial(COM_PORT)
        self.master_port.open()

        for i in range(1,31):
            tag_data[i]=0
        self.start()

    def run(self):
        while self._read_port:
            packet=self.master_port.read(8)
            now=datetime.datetime.now()
            if (packet[0]=='*') and (packet[1]=='T') and (packet[5]=='#'):

                if (packet[2]=='A') and (packet[3]=='G'):
                    pass
                else:
                   tag_id=int(packet[2:5])
                   tag_data[tag_id]=now
                   print tag_id, now.strftime("%H:%M:%S")
                   sys.stdout.flush()

    def abort(self):
        print "In tag abort"
        self.master_port.close()
        self._read_port=False



##Dummy Class which mimics the hardware! Used for testing.
#class Tag(threading.Thread):
#    def __init__(self):
#        threading.Thread.__init__(self)
#        self._read_port=True
#        self.setDaemon(1)
#
#        for i in range(1,ROWS+1):
#            tag_data[i]=0
#        self.start()
#
#    def run(self):
#	while self._read_port:
#            now=datetime.datetime.now()
#	    tag_id = random.randint(1,ROWS)
#	    time.sleep(random.randint(1,10))
#            tag_data[tag_id]=now
#	    print tag_id, now.strftime("%H:%M:%S")
#            sys.stdout.flush()
#
#    def abort(self):
#        print "In tag abort"
#        self._read_port=False
#

#---------------------------------------------------------------------------
class TestFrame(wx.Frame):

    def __init__(self, parent):
        global start_time
        wx.Frame.__init__(self, parent, -1, "Marathon Timer",size=(400,700))


        start_time = datetime.datetime.now()
        current_time = datetime.datetime.now()



        self.data=self.createdata()
        self.initwin()
        self.initmenu()
        self.tag=Tag()

    def createdata(self):
        table=[]
        now=datetime.datetime.now().strftime("%H:%M:%S")
        for i in range(1,ROWS+1):
            row=[i,"User "+str(i),now,now,0]
            table.append(row)
        return table


    def timediff(self,start_time,current_time):
        try:
            start_delta = datetime.timedelta(hours=start_time.hour,minutes=start_time.minute,seconds=start_time.second)
            current_delta = datetime.timedelta(hours=current_time.hour,minutes=current_time.minute,seconds=current_time.second)
            elapsed_time = current_delta - start_delta
            return elapsed_time
        except:
            print current_time
            print start_time

    def validateTime(self,entered_time):
        if len(entered_time) is not 8:#len of 00:00:00
            print "Invalid length of the time string"
            return False
        # Enter check for individual characters

        #Figure out if the entered time is greater than the current time.
        new_start=datetime.datetime.strptime(entered_time,"%H:%M:%S")
        cur_time=datetime.datetime.now()
        sd=datetime.timedelta(hours=new_start.hour,minutes=new_start.minute,seconds=new_start.second)
        cd=datetime.timedelta(hours=cur_time.hour,minutes=cur_time.minute,seconds=cur_time.second)
        if(sd>cd):
            print "Invalid time diff between start time and current time"
            return False

        return True

    def initwin(self):
        self.ref= None
        self.p = wx.Panel(self, -1, style=0)
        b = wx.Button(self.p, -1, "Update")
        self.grid = CustTableGrid(self.p,self.data)
        b.SetDefault()
        self.Bind(wx.EVT_BUTTON, self.OnButton, b)
        b.Bind(wx.EVT_SET_FOCUS, self.OnButtonFocus)
        bs = wx.BoxSizer(wx.VERTICAL)
        bs.Add(self.grid, 1, wx.GROW|wx.ALL, 5)
        bs.Add(b)
        self.p.SetSizer(bs)
        self.Bind(wx.EVT_CLOSE,self.OnCloseWindow)



    def initmenu(self):
        menuFile = wx.Menu()
        menuFile.Append(1, "Enter S&tart Time")
        menuFile.AppendSeparator()
        menuFile.Append(2, "&About Marathon Timer")
        menuFile.AppendSeparator()
        menuFile.Append(3, "&Save")
        menuFile.AppendSeparator()
        menuFile.Append(4, "E&xit")
        menuBar = wx.MenuBar()
        menuBar.Append(menuFile, "&File")
        self.SetMenuBar(menuBar)
        self.sb = CustomStatusBar(self)
        self.SetStatusBar(self.sb)
        self.Bind(wx.EVT_MENU, self.OnTime, id=1)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=2)
        self.Bind(wx.EVT_MENU, self.OnSave, id=3)
        self.Bind(wx.EVT_MENU, self.OnQuit, id=4)

    def OnQuit(self, event):
        self.Close()

    def OnAbout(self, event):
        wx.MessageBox("This is a demo application to demonstrate SITPL's RFID technology when used as a marathon timer.",
        "About Marathon Timer", wx.OK | wx.ICON_INFORMATION, self)

    def OnTime(self,event):
        global start_time
        global start_time
        print "In Time Entry"
        dlg = wx.TextEntryDialog(
                self, 'Enter the Marathon Start Time in the HH:MM:SS format',
                'Start Time', '12:12:12')

        dlg.SetValue("00:00:00")

        if dlg.ShowModal() == wx.ID_OK:
            print('You entered: %s\n' % dlg.GetValue())

            entered_time = dlg.GetValue()
            if not self.validateTime(entered_time):
                dlg.SetValue("00:00:00")
                print "Invalid time entered."
            else:
                start_time = datetime.datetime.strptime(entered_time,"%H:%M:%S")


        dlg.Destroy()


    def OnButton(self, evt):
        self.updateData()
        self.grid.Update()
        self.sb.SetStatusText("SITPL Demo Application",0)
        
    
    def OnSave(self,event):
        now=datetime.datetime.now().strftime("%H:%M:%S")
        name="MLog_"+now+".csv"
        
        
        try:
            log=open(name,"wb")
           
            for i in range(ROWS):
                data = str(self.data[i][0])+","+str(self.data[i][1])+","+str(self.data[i][4])+"\n"
                log.write(data)
                 
        except:
            print "Failed to save the log file: ", name
            raise
            
        finally:
            log.close()


    def updateData(self):
        global start_time     

        for i in range(ROWS):
            current_time = datetime.datetime.now()
            #self.data[i][3] = current_time.strftime("%H:%M:%S")
            id = self.data[i][0]
            crossed = tag_data[id]
            if (crossed==0):
                crossed=start_time

            self.data[i][3] = crossed.strftime("%H:%M:%S")
            self.data[i][4] = self.timediff(start_time,crossed)
            self.data[i][2] = start_time.strftime("%H:%M:%S")

            if(self.data[i][4]==datetime.timedelta(0)):
                tag_time[i+1]=1
            else:
                tag_time[i+1]=0

    def OnButtonFocus(self,evt):
        self.sb.SetStatusText("Updates the timing information.",0)

    def OnCloseWindow(self,event):
        self.tag.abort()
        #self.Close()
        self.Destroy()





#-------------------------------------------------------------------------------
class mApp(wx.App):
    def OnInit(self):
        frame= TestFrame(None)
        frame.Show(True)
        return True
#-------------------------------------------------------------------------------
app = mApp(0)
app.MainLoop()
#-------------------------------------------------------------------------------
