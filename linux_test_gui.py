import  wx
import  wx.grid as gridlib
import time
import datetime


global start_time


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
        table = CustomDataTable(data)
        self.SetTable(table, True)
        self.SetRowLabelSize(0)
        self.SetMargins(0,0)
        self.AutoSizeColumns(False)
        gridlib.EVT_GRID_CELL_LEFT_DCLICK(self, self.OnLeftDClick)
        
        
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
#---------------------------------------------------------------------------
class TestFrame(wx.Frame):
    
    def __init__(self, parent):
        global start_time
        wx.Frame.__init__(self, parent, -1, "Marathon Timer")
        
        
        start_time = datetime.datetime.now()
        current_time = datetime.datetime.now()
               

        
        self.data = [
            [001, "User 1", start_time.strftime("%H:%M:%S"), current_time.strftime("%H:%M:%S"),self.timediff(start_time,current_time)],
            [002, "User 2", start_time.strftime("%H:%M:%S"), current_time.strftime("%H:%M:%S"),self.timediff(start_time,current_time)],
            [003, "User 3", start_time.strftime("%H:%M:%S"), current_time.strftime("%H:%M:%S"),self.timediff(start_time,current_time)],
            ]
        self.initwin()
        self.initmenu()
        
    
    def timediff(self,start_time,current_time):        
        start_delta = datetime.timedelta(hours=start_time.hour,minutes=start_time.minute,seconds=start_time.second)
        current_delta = datetime.timedelta(hours=current_time.hour,minutes=current_time.minute,seconds=current_time.second)
        elapsed_time = current_delta - start_delta
        return elapsed_time
        
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
        grid = CustTableGrid(self.p,self.data)
        b.SetDefault()
        self.Bind(wx.EVT_BUTTON, self.OnButton, b)
        b.Bind(wx.EVT_SET_FOCUS, self.OnButtonFocus)
        bs = wx.BoxSizer(wx.VERTICAL)
        bs.Add(grid, 1, wx.GROW|wx.ALL, 5)
        bs.Add(b)
        self.p.SetSizer(bs)


        
    def initmenu(self):
        menuFile = wx.Menu()
        menuFile.Append(1, "Enter S&tart Time")
        menuFile.AppendSeparator()
        menuFile.Append(2, "&About Marathon Timer")
        menuFile.AppendSeparator()
        menuFile.Append(3, "E&xit")
        menuBar = wx.MenuBar()
        menuBar.Append(menuFile, "&File")
        self.SetMenuBar(menuBar)
        self.CreateStatusBar()
        self.SetStatusText("SITPL Demo Application - RFID based Marathon Timer")
        self.Bind(wx.EVT_MENU, self.OnTime, id=1)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=2)
        self.Bind(wx.EVT_MENU, self.OnQuit, id=3)
        
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
        global start_time
                
        for i in range(3):
            current_time = datetime.datetime.now()
            self.data[i][3] = current_time.strftime("%H:%M:%S")
            self.data[i][4] = self.timediff(start_time,current_time)
            self.data[i][2] = start_time.strftime("%H:%M:%S")
            
            
        

            
        self.SetStatusText("SITPL Demo Application - RFID based Marathon Timer")
        sz= self.p.GetSize()
        self.p.Destroy()
        self.initwin()
        self.p.SetSize(sz)
        print "button selected"
	
    def OnButtonFocus(self,evt):
        self.SetStatusText("Updates the timing information.")
        


	
	
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
