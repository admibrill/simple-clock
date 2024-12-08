from PySide6.QtWidgets import (QApplication,QWidget,QPushButton,QGroupBox,QLabel,
                                QTableWidget,QTableWidgetItem,QProgressBar,QScrollArea,
                                QDialog,QGridLayout,QVBoxLayout,QHBoxLayout,QSpinBox,QLineEdit,QComboBox,QSystemTrayIcon,QCheckBox)
from PySide6.QtGui import QIcon,QFont
from PySide6.QtCore import QObject,QTimer,Qt,QSize
import time
qapp=QApplication([])
icon=QIcon('../media/images/1.png')
widgetslist=[]
musicUrlList=['../media/audio/1.wav']
musicNameList=['音乐1']
class Window(QWidget):
    def __init__(self,width,height,title,icon):
        super().__init__()
        self.setWindowTitle(QObject.tr(title))
        self.resize(width,height)
        self.setWindowIcon(icon)
    def resizeEvent(self,event):
        size=self.size()
        for i in widgetslist:
            i.resize(size.width()-110,size.height()-20)
    def closeEvent(self,event):
        global countDownList,alarmList
        with open('../data/countdown.txt','w',encoding='utf-8') as f:
            for i in countDownList:
                f.write(str(i.timelength)+':/:'+i.titlestr+':/:'+str(i.music)+'\n')
        with open('../data/alarm.txt','w',encoding='utf-8') as f:
            for i in alarmList:
                f.write(str(i.timelength)+':/:'+i.titlestr+':/:'+str(i.music)+':/:'+':/:'.join(map(str,map(int,i.repeat)))+':/:'+i.description+':/:'+str(int(i.running))+'\n')
class MenuButton(QPushButton):
    def __init__(self,parent,num):
        super().__init__(parent)
        self.num=num
        self.clicked.connect(self.toggleMode)
    def toggleMode(self):
        global mode
        widgetslist[mode].hide()
        widgetslist[self.num].show()
        mode=self.num
mainWindow=Window(1000,600,'时钟',icon)
mainWindow.show()
menubuttonnamelist=['时钟','秒表','倒计时','闹钟']
menubuttonlist=[]
mode=0
for i in range(len(menubuttonnamelist)):
    button=MenuButton(mainWindow,i)
    button.setText(menubuttonnamelist[i])
    button.move(10,10+i*30)
    button.show()
    menubuttonlist.append(button)
    group=QGroupBox(parent=mainWindow,title=menubuttonnamelist[i])
    group.resize(890,580)
    group.move(100,10)
    widgetslist.append(group)

nowtime=time.strftime('%H:%M:%S')
labelTime=QLabel(widgetslist[0])
font=QFont('Arian',100,10)
labelTime.setFont(font)
labelTime.setText(nowtime)

recorder=QLabel(widgetslist[1])
recorder.setText('00:00:00.000')
recorder.setFont(font)
startStopButton=QPushButton('开始',widgetslist[1])
recordButton=QPushButton('记录',widgetslist[1])
recordButton.setDisabled(True)
clearButton=QPushButton('清零',widgetslist[1])
clearButton.setDisabled(True)
recordTable=QTableWidget(0,3,widgetslist[1])
recordTable.setHorizontalHeaderLabels(['序次','间隔','总计'])
recordTable.verticalHeader().setVisible(False)
recordTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
recordTable.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
startTimeStamp=0
lastEndStamp=0
lastRecordStamp=0
running=False
timeDelta=0        
def getTime():
    global startTimeStamp,timeDelta
    return time.time()-startTimeStamp-timeDelta 
def formatTime(data,round=False):
    return '{:0>2d}'.format(int(data//3600))+':'+'{:0>2d}'.format((int(data)%3600)//60)+':'+'{:0>2d}'.format(int(data)%60)+('.'+'{:0>3d}'.format(int((data%1)*1000)) if not round else '')
def startStop():
    global running,startTimeStamp,lastEndStamp,timeDelta,lastRecordStamp
    if running:
        lastEndStamp=time.time()
        startStopButton.setText('开始')
    else:
        if startTimeStamp==0:
            startTimeStamp=lastEndStamp=time.time()
        timeDelta+=time.time()-lastEndStamp
        startStopButton.setText('停止')
    recordButton.setDisabled(running)
    running=not running
    clearButton.setDisabled(running)
def writeRecord():
    global lastRecordStamp
    recordTable.insertRow(0)
    recordTable.setItem(0,0,QTableWidgetItem(str(recordTable.rowCount())))
    if recordTable.rowCount()>1:
        recordTable.setItem(0,1,QTableWidgetItem(formatTime(getTime()-lastRecordStamp)))
    recordTable.setItem(0,2,QTableWidgetItem(formatTime(getTime())))
    lastRecordStamp=getTime()
def clearRecord():
    global startTimeStamp,lastEndStamp,timeDelta,recorder
    startTimeStamp=lastEndStamp=timeDelta=0
    recorder.setText('00:00:00.000')
    clearButton.setDisabled(True)
    while(recordTable.rowCount()>0):
        recordTable.removeRow(0)
startStopButton.clicked.connect(startStop)  
recordButton.clicked.connect(writeRecord)     
clearButton.clicked.connect(clearRecord)

newCountDown=QPushButton('新建',widgetslist[2])
deleteCountDown=QPushButton('编辑',widgetslist[2])
countDownScrollArea=QScrollArea(widgetslist[2])
countDownScrollArea.move(10,30)
countDownScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
countDownScrollAreaWidget=QWidget()
countDownScrollArea.setWidget(countDownScrollAreaWidget)
countDownList=[]
class CountDown(QGroupBox):
    def __init__(self,parent,timelength,title,music):
        super().__init__(parent)
        self.timelength=timelength
        self.titlestr=title
        self.music=music
        self.restTime=0
        self.startTimeStamp=0
        self.lastEndStamp=0
        self.timeDelta=0
        self.running=False
    def launch(self):
        self.resize(400,300)
        self.restTime=self.timelength
        self.timelabel=QLabel(formatTime(self.restTime),self)
        font=QFont('Arian',40,10)
        self.timelabel.setFont(font)
        self.progressbar=QProgressBar(self)
        self.progressbar.setTextVisible(False)
        self.progressbar.setRange(0,10000)
        self.startStopButton=QPushButton('开始',self)
        self.startStopButton.clicked.connect(self.startStop)
        self.clearButton=QPushButton('还原',self)
        self.clearButton.clicked.connect(self.reset)
        self.clearButton.setDisabled(True)
        self.editButton=None
        self.deleteButton=None
        self.mode=True
    def toggleMode(self):
        if self.mode:
            self.startStopButton.hide()
            self.clearButton.hide()
            self.editButton=QPushButton('编辑',self)
            self.editButton.clicked.connect(self.edit)
            self.editButton.show()
            self.deleteButton=QPushButton('删除',self)
            self.deleteButton.clicked.connect(self.deleteSelf)
            self.deleteButton.show()
        else:
            self.startStopButton.show()
            self.clearButton.show()
            self.editButton.hide()
            self.editButton=None
            self.deleteButton.hide()
            self.deleteButton=None
        self.mode=not self.mode
    def updating(self):
        self.setTitle(self.titlestr)
        selfsize=self.size()
        buttonsize=self.startStopButton.size()
        progressbarsize=self.progressbar.size()
        if abs(self.timelength-max(0,time.time()-self.startTimeStamp-self.timeDelta))<0.0005:
            self.showMessage()
            self.startStop()
            self.timelabel.setText('00:00:00:000')
        self.restTime=max(0,self.timelength-max(0,time.time()-self.startTimeStamp-self.timeDelta))
        if self.running:
            self.timelabel.setText(formatTime(self.restTime))
            self.progressbar.setValue(self.restTime/self.timelength*10000)
            self.progressbar.update()
        labelsize=self.timelabel.size()
        self.timelabel.move(selfsize.width()/2-labelsize.width()/2,selfsize.height()/2-labelsize.height()/2)
        self.progressbar.resize(selfsize.width()-20,20)
        self.progressbar.move(10,selfsize.height()-10-buttonsize.height()-10-progressbarsize.height())
        if self.mode:
            self.startStopButton.move(selfsize.width()/2-5-buttonsize.width(),selfsize.height()-10-buttonsize.height())
            self.clearButton.move(selfsize.width()/2+5,selfsize.height()-10-buttonsize.height())
        else:
            self.editButton.move(selfsize.width()/2-5-buttonsize.width(),selfsize.height()-10-buttonsize.height())
            self.deleteButton.move(selfsize.width()/2+5,selfsize.height()-10-buttonsize.height())
    def startStop(self):
        if self.running:
            self.lastEndStamp=time.time()
            self.startStopButton.setText('开始')
        else:
            if self.startTimeStamp==0:
                self.startTimeStamp=self.lastEndStamp=time.time()
            self.timeDelta+=time.time()-self.lastEndStamp
            self.startStopButton.setText('停止')
        self.running=not self.running
        self.clearButton.setDisabled(self.running)
    def reset(self):
        self.startTimeStamp=self.lastEndStamp=self.timeDelta=0
        self.timelabel.setText(formatTime(self.timelength))
        self.clearButton.setDisabled(True)
    def edit(self):
        editor=CountDownEdit(self.timelength,self.titlestr,self.music)
        editor.editData()
        self.timelength=editor.length
        self.restTime=self.timelength
        self.titlestr=editor.titlestr
        self.music=editor.music
    def showMessage(self):
        self.trayicon=QSystemTrayIcon()
        self.trayicon.setIcon(icon)
        self.trayicon.show()
        self.trayicon.showMessage('计时器到了','倒计时'+self.titlestr+'计时已完成。',icon)
    def deleteSelf(self):
        countDownList.remove(self)
        self.deleteLater()
        del self
class CountDownEdit(QDialog):
    def __init__(self,length,title,music):
        super().__init__()
        self.confirmed=False
        self.length=length
        self.titlestr=title
        self.music=music
    def editData(self):
        self.setWindowTitle('倒计时编辑')
        self.vlayout=QVBoxLayout()
        self.gridlayout=QGridLayout()
        self.hlayout=QHBoxLayout()
        self.gridlayout.setSpacing(10)
        self.label1=QLabel('时长')
        self.label2=QLabel('标题')
        self.label3=QLabel('音乐')
        self.content1=QHBoxLayout()
        self.content1_1=QSpinBox()
        self.content1_1.setMinimum(0)
        self.content1_1.setMaximum(99)
        self.content1_1.setValue(self.length//3600)
        self.content1_2=QLabel(':')
        self.content1_3=QSpinBox()
        self.content1_3.setMinimum(0)
        self.content1_3.setMaximum(59)
        self.content1_3.setValue((self.length%3600)//60)
        self.content1_4=QLabel(':')
        self.content1_5=QSpinBox()
        self.content1_5.setMinimum(0)
        self.content1_5.setMaximum(59)
        self.content1_5.setValue(self.length%60)
        self.content1.addWidget(self.content1_1)
        self.content1.addWidget(self.content1_2)
        self.content1.addWidget(self.content1_3)
        self.content1.addWidget(self.content1_4)
        self.content1.addWidget(self.content1_5)
        self.content2=QLineEdit()
        self.content2.setText(self.titlestr)
        self.content3=QComboBox()
        self.content3.addItems(musicNameList)
        self.content3.setCurrentIndex(self.music)
        self.gridlayout.addWidget(self.label1,0,0)
        self.gridlayout.addWidget(self.label2,1,0)
        self.gridlayout.addWidget(self.label3,2,0)
        self.gridlayout.addLayout(self.content1,0,1)
        self.gridlayout.addWidget(self.content2,1,1)
        self.gridlayout.addWidget(self.content3,2,1)
        self.confirm=QPushButton('确定')
        self.cancel=QPushButton('取消')
        self.confirm.clicked.connect(self.confirming)
        self.cancel.clicked.connect(self.close)
        self.hlayout.addWidget(self.confirm)
        self.hlayout.addWidget(self.cancel)
        self.vlayout.addLayout(self.gridlayout)
        self.vlayout.addLayout(self.hlayout)
        self.setLayout(self.vlayout)
        self.show()
        self.exec()
    def confirming(self):
        self.confirmed=True
        self.length=self.content1_1.value()*3600+self.content1_3.value()*60+self.content1_5.value()
        self.titlestr=self.content2.text()
        self.music=self.content3.currentIndex()
        self.close()
def onNewCountDown():
    global countDownList
    countDownEdit=CountDownEdit(0,'未命名',0)
    countDownEdit.editData()
    if countDownEdit.confirmed:
        countDown=CountDown(countDownScrollAreaWidget,countDownEdit.length,countDownEdit.titlestr,countDownEdit.music)
        countDown.launch()
        countDown.show()
        countDownList.append(countDown)
def onDeleteCountDown():
    global countDownList
    for i in countDownList:
        i.toggleMode()
newCountDown.clicked.connect(onNewCountDown)
deleteCountDown.clicked.connect(onDeleteCountDown)
with open('../data/countdown.txt','r',encoding='utf-8') as f:
    for i in f.readlines():
        timelength,title,music=i.split(':/:')
        countDown=CountDown(countDownScrollAreaWidget,int(timelength),title,int(music))
        countDown.launch()
        countDown.show()
        countDownList.append(countDown)

newAlarm=QPushButton('新建',widgetslist[3])
deleteAlarm=QPushButton('编辑',widgetslist[3])
alarmScrollArea=QScrollArea(widgetslist[3])
alarmScrollArea.move(10,30)
alarmScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
alarmScrollAreaWidget=QWidget()
alarmScrollArea.setWidget(alarmScrollAreaWidget)
alarmList=[]
class Alarm(QGroupBox):
    def __init__(self,parent,timelength,title,music,repeat,description,running):
        super().__init__(parent)
        self.timelength=timelength
        self.titlestr=title
        self.music=music
        self.running=running
        self.repeat=repeat
        self.description=description
    def launch(self):
        self.resize(400,300)
        self.restTime=self.timelength
        self.timelabel=QLabel(formatTime(self.restTime,round=True),self)
        font=QFont('Arian',40,10)
        self.timelabel.setFont(font)
        self.descriptionLabel=QLabel(self)
        self.descriptionLabel.setWordWrap(True)
        self.descriptionLabel.setAlignment(Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft)
        self.repetitionLabel=QLabel(self)
        self.startStopButton=QPushButton('关闭' if self.running else '开启',self)
        self.startStopButton.clicked.connect(self.startStop)
        self.editButton=None
        self.deleteButton=None
        self.mode=True
    def toggleMode(self):
        if self.mode:
            self.startStopButton.hide()
            self.editButton=QPushButton('编辑',self)
            self.editButton.clicked.connect(self.edit)
            self.editButton.show()
            self.deleteButton=QPushButton('删除',self)
            self.deleteButton.clicked.connect(self.deleteSelf)
            self.deleteButton.show()
        else:
            self.startStopButton.show()
            self.editButton.hide()
            self.editButton=None
            self.deleteButton.hide()
            self.deleteButton=None
        self.mode=not self.mode
    def updating(self):
        hours,minutes,seconds=list(map(int,time.strftime('%H %M %S').split()))
        if abs(self.timelength-(hours*3600+minutes*60+seconds))<0.0005 and self.running:
            self.showMessage()
            self.startStop()
        self.setTitle(self.titlestr)
        selfsize=self.size()
        buttonsize=self.startStopButton.size()
        self.timelabel.setText(formatTime(self.timelength,round=True))
        labelsize=self.timelabel.size()
        self.timelabel.move(selfsize.width()/2-labelsize.width()/2,30)

        self.descriptionLabel.setText(self.description)
        self.descriptionLabel.setFixedSize(selfsize.width()-10,200)
        labelsize=self.descriptionLabel.size()
        self.descriptionLabel.move(selfsize.width()/2-labelsize.width()/2,150)
        text=['星期一','星期二','星期三','星期四','星期五','星期六','星期日']
        list1=[]
        for i in range(7):
            if self.repeat[i]:
                list1.append(text[i])
        self.repetitionLabel.setText('，'.join(list1))
        self.repetitionLabel.setFixedSize(selfsize.width()-10,20)
        labelsize=self.repetitionLabel.size()
        self.repetitionLabel.move(selfsize.width()/2-labelsize.width()/2,100)
        if self.mode:
            self.startStopButton.move(selfsize.width()/2-buttonsize.width()/2,selfsize.height()-10-buttonsize.height())
        else:
            self.editButton.move(selfsize.width()/2-5-buttonsize.width(),selfsize.height()-10-buttonsize.height())
            self.deleteButton.move(selfsize.width()/2+5,selfsize.height()-10-buttonsize.height())
    def startStop(self):
        if self.running:
            self.startStopButton.setText('开启')
        else:
            self.startStopButton.setText('关闭')
        self.running=not self.running
    def edit(self):
        editor=AlarmEdit(self.timelength,self.titlestr,self.music,self.repeat,self.description,self.running)
        editor.editData()
        self.timelength=editor.length
        self.restTime=self.timelength
        self.titlestr=editor.titlestr
        self.music=editor.music
        self.repeat=editor.repeat
        self.description=editor.description
        self.running=editor.running
    def showMessage(self):
        self.trayicon=QSystemTrayIcon()
        self.trayicon.setIcon(icon)
        self.trayicon.show()
        self.trayicon.showMessage('闹钟'+formatTime(self.timelength,round=True),self.description,icon)
    def deleteSelf(self):
        alarmList.remove(self)
        self.deleteLater()
        del self
class AlarmEdit(QDialog):
    def __init__(self,length,title,music,repeat,description,running):
        super().__init__()
        self.confirmed=False
        self.length=length
        self.titlestr=title
        self.music=music
        self.repeat=repeat
        self.description=description
        self.running=running
    def editData(self):
        self.setWindowTitle('闹钟编辑')
        self.vlayout=QVBoxLayout()
        self.gridlayout=QGridLayout()
        self.hlayout=QHBoxLayout()
        self.gridlayout.setSpacing(10)
        self.label1=QLabel('时间')
        self.label2=QLabel('标题')
        self.label3=QLabel('音乐')
        self.label4=QLabel('描述')
        self.label5=QLabel('重复')
        self.content1=QHBoxLayout()
        self.content1_1=QSpinBox()
        self.content1_1.setMinimum(0)
        self.content1_1.setMaximum(23)
        self.content1_1.setValue(self.length//3600)
        self.content1_2=QLabel(':')
        self.content1_3=QSpinBox()
        self.content1_3.setMinimum(0)
        self.content1_3.setMaximum(59)
        self.content1_3.setValue((self.length%3600)//60)
        self.content1_4=QLabel(':')
        self.content1_5=QSpinBox()
        self.content1_5.setMinimum(0)
        self.content1_5.setMaximum(59)
        self.content1_5.setValue(self.length%60)
        self.content1.addWidget(self.content1_1)
        self.content1.addWidget(self.content1_2)
        self.content1.addWidget(self.content1_3)
        self.content1.addWidget(self.content1_4)
        self.content1.addWidget(self.content1_5)
        self.content2=QLineEdit()
        self.content2.setText(self.titlestr)
        self.content3=QComboBox()
        self.content3.addItems(musicNameList)
        self.content3.setCurrentIndex(self.music)
        self.content4=QLineEdit()
        self.content4.setText(self.description)
        self.content5=QVBoxLayout()
        text=['星期一','星期二','星期三','星期四','星期五','星期六','星期日']
        self.content5s=[QCheckBox(text=i) for i in text]
        for i in self.content5s:
            self.content5.addWidget(i)
            p=self.content5s.index(i)
            i.setChecked(self.repeat[p])
        self.gridlayout.addWidget(self.label1,0,0)
        self.gridlayout.addWidget(self.label2,1,0)
        self.gridlayout.addWidget(self.label3,2,0)
        self.gridlayout.addWidget(self.label4,3,0)
        self.gridlayout.addWidget(self.label5,4,0)
        self.gridlayout.addLayout(self.content1,0,1)
        self.gridlayout.addWidget(self.content2,1,1)
        self.gridlayout.addWidget(self.content3,2,1)
        self.gridlayout.addWidget(self.content4,3,1)
        self.gridlayout.addLayout(self.content5,4,1)
        self.confirm=QPushButton('确定')
        self.cancel=QPushButton('取消')
        self.confirm.clicked.connect(self.confirming)
        self.cancel.clicked.connect(self.close)
        self.hlayout.addWidget(self.confirm)
        self.hlayout.addWidget(self.cancel)
        self.vlayout.addLayout(self.gridlayout)
        self.vlayout.addLayout(self.hlayout)
        self.setLayout(self.vlayout)
        self.show()
        self.exec()
    def setRepeat(self,p):
        self.repeat[p]=not self.repeat[p]
    def confirming(self):
        self.confirmed=True
        self.length=self.content1_1.value()*3600+self.content1_3.value()*60+self.content1_5.value()
        self.titlestr=self.content2.text()
        self.music=self.content3.currentIndex()
        self.description=self.content4.text()
        self.repeat=[i.isChecked() for i in self.content5s]
        self.close()
def onNewAlarm():
    global alarmList
    alarmEdit=AlarmEdit(0,'未命名',0,[False,False,False,False,False,False,False],'',True)
    alarmEdit.editData()
    if alarmEdit.confirmed:
        alarm=Alarm(alarmScrollAreaWidget,alarmEdit.length,alarmEdit.titlestr,alarmEdit.music,alarmEdit.repeat,alarmEdit.description,alarmEdit.running)
        alarm.launch()
        alarm.show()
        alarmList.append(alarm)
def onDeleteAlarm():
    global alarmList
    for i in alarmList:
        i.toggleMode()
newAlarm.clicked.connect(onNewAlarm)
deleteAlarm.clicked.connect(onDeleteAlarm)
with open('../data/alarm.txt','r',encoding='utf-8') as f:
    for i in f.readlines():
        timelength,title,music,repeat1,repeat2,repeat3,repeat4,repeat5,repeat6,repeat7,description,running1=i.split(':/:')
        alarm=Alarm(alarmScrollAreaWidget,int(timelength),title,int(music),list(map(bool,map(int,[repeat1,repeat2,repeat3,repeat4,repeat5,repeat6,repeat7]))),description,bool(int(running1)))
        alarm.launch()
        alarm.show()
        alarmList.append(alarm)

def update():
    global startTimeStamp,timeDelta
    size1_1=widgetslist[0].size()
    nowtime=time.strftime('%H:%M:%S')
    labelTime.setText(nowtime)
    size2=labelTime.size()
    labelTime.move(size1_1.width()/2-size2.width()/2,size1_1.height()/2-size2.height()/2)

    size1_2=widgetslist[1].size()
    size3=recorder.size()
    size4=startStopButton.size()
    size5=recordButton.size()
    size6=clearButton.size()
    recorder.move(size1_2.width()/2-size3.width()/2,10)
    startStopButton.move(size1_2.width()/2-size5.width()/2-10-size4.width(),size1_2.height()-10-size4.height())
    recordButton.move(size1_2.width()/2-size5.width()/2,size1_2.height()-10-size5.height())
    clearButton.move(size1_2.width()/2+size5.width()/2+10,size1_2.height()-10-size6.height())
    recordTable.resize(size1_2.width()-200,size1_2.height()-320)
    size7=recordTable.size()
    recordTable.move(size1_2.width()/2-size7.width()/2,220)
    recordTable.setColumnWidth(0,40)
    recordTable.setColumnWidth(1,size7.width()/2-20)
    recordTable.setColumnWidth(2,size7.width()/2-20)
    if running:
        stampDelta=getTime()
        rec=formatTime(stampDelta)
        recorder.setText(rec)

    size1_3=widgetslist[2].size()
    size8=newCountDown.size()
    size9=deleteCountDown.size()
    newCountDown.move(size1_3.width()/2-5-size8.width(),size1_3.height()-10-size8.height())
    deleteCountDown.move(size1_3.width()/2+5,size1_3.height()-10-size9.height())
    countDownScrollArea.resize(size1_3.width()-20,size1_3.height()-50-size8.height())
    size10=countDownScrollArea.size()
    size11=QSize(400,300)
    numPerRow=(size10.width()-size11.width())//(size11.width()+10)+1
    widthPerRow=numPerRow*size11.width()+(numPerRow-1)*10
    countDownScrollAreaWidget.resize(size10.width(),10+((len(countDownList))//numPerRow+1)*(10+size11.height()))
    for i in range(len(countDownList)):
        countDownList[i].move(size10.width()/2-widthPerRow/2+(i%numPerRow)*(10+size11.width()),10+(i//numPerRow)*(10+size11.height()))
        countDownList[i].updating()
    
    size8=newAlarm.size()
    size9=deleteAlarm.size()
    newAlarm.move(size1_3.width()/2-5-size8.width(),size1_3.height()-10-size8.height())
    deleteAlarm.move(size1_3.width()/2+5,size1_3.height()-10-size9.height())
    alarmScrollArea.resize(size1_3.width()-20,size1_3.height()-50-size8.height())
    size10=alarmScrollArea.size()
    size11=QSize(400,300)
    numPerRow=(size10.width()-size11.width())//(size11.width()+10)+1
    widthPerRow=numPerRow*size11.width()+(numPerRow-1)*10
    alarmScrollAreaWidget.resize(size10.width(),10+((len(alarmList))//numPerRow+1)*(10+size11.height()))
    for i in range(len(alarmList)):
        alarmList[i].move(size10.width()/2-widthPerRow/2+(i%numPerRow)*(10+size11.width()),10+(i//numPerRow)*(10+size11.height()))
        alarmList[i].updating()
    

timer=QTimer()
timer.start(0.05)
timer.timeout.connect(update)

widgetslist[mode].show()
qapp.exec()