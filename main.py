import cv2
import numpy as np
import time
import os
import random
import sys
import subprocess
import threading
import yaml
import item as i

#设备名称
IP = 'auto'
#培育马娘
Who = 'Defult'
#设置当前回合数
if len(sys.argv) <= 1:
    stage = 0
    print("未设置回合,默认从0开始")
else:
    stage = int(sys.argv[1])    #传入参数
    print("已设置到回合数:", stage)
#模板文件路径
data = ""
#全局页面监控
Page = 'Waite'
#指导屏幕监控的开关,一旦设置为False,则threadingCap终止
CapON = True
#状态参数
Energy, Motivation, Ill = 100, 3, False
#调度列表
Dispatch = []

UR = {}
SSR = {}
SR = {}

#5种训练的Class,包含训练按钮坐标等
class Speed:
    Add = 9
    Value = 0
    Be3 = 0
    Be4 = 0
    tapLoc = (160,2048)
    Aim = (100,100)#在以下回合数应该达到的属性值:初始,24,30,36,40,48,54,60,64,global
    def Weigh():
        if stage in range(1,24+1):
            catg, stepLen, sStage = 1, 24, 1
        elif stage in range(24+1,30+1):
            catg, stepLen, sStage = 2, 6, 24
        elif stage in range(30+1,36+1):
            catg, stepLen, sStage = 3, 6, 30
        elif stage in range(36+1,40+1):
            catg, stepLen, sStage = 4, 4, 36
        elif stage in range(40+1,48+1):
            catg, stepLen, sStage = 5, 8, 40
        elif stage in range(48+1,54+1):
            catg, stepLen, sStage = 6, 6, 48
        elif stage in range(54+1,60+1):
            catg, stepLen, sStage = 7, 6, 54
        elif stage in range(60+1,64+1):
            catg, stepLen, sStage = 8, 4, 60
        else:
            catg, stepLen, sStage = 9, 14, 64
        return (max(((100+(((Speed.Aim[catg]-Speed.Aim[catg-1])/stepLen)*(stage-sStage)))-Speed.Value),0))*Speed.Add*0.0014 + 0.06*(Speed.Add-9) + 0.15*Speed.Be3 + 0.3*Speed.Be4 - int(Speed.Aim[catg+1]<Speed.Value)*0.6 - max((Speed.Value-Speed.Aim[catg]),0)*0.004
class Stamina:
    Add = 9
    Value = 0
    Be3 = 0
    Be4 = 0
    tapLoc = (350,2048)
    Aim = (100,100)#在以下回合数应该达到的属性值:初始,24,30,36,40,48,54,60,64,global
    def Weigh():
        if stage in range(1,24+1):
            catg = 1
        elif stage in range(24+1,30+1):
            catg = 2
        elif stage in range(30+1,36+1):
            catg = 3
        elif stage in range(36+1,40+1):
            catg = 4
        elif stage in range(40+1,48+1):
            catg = 5
        elif stage in range(48+1,54+1):
            catg = 6
        elif stage in range(54+1,60+1):
            catg = 7
        elif stage in range(60+1,64+1):
            catg = 8
        else:
            catg = 9
        weight = 0
        for check in range(1,catg+1):
            weight += int(Stamina.Aim[check]>Stamina.Value)*Stamina.Add*0.025
        return weight + 0.06*(Stamina.Add-9) + 0.15*Stamina.Be3 + 0.3*Stamina.Be4 - int(Stamina.Aim[catg]<Stamina.Value)*0.42 - int(Stamina.Aim[catg+1]<Stamina.Value)*1
class Power:
    Add = 9
    Value = 0
    Be3 = 0
    Be4 = 0
    tapLoc = (540,2048)
    Aim = (100,100)
    def Weigh():
        if stage in range(1,24+1):
            catg, stepLen, sStage = 1, 24, 1
        elif stage in range(24+1,30+1):
            catg, stepLen, sStage = 2, 6, 24
        elif stage in range(30+1,36+1):
            catg, stepLen, sStage = 3, 6, 30
        elif stage in range(36+1,40+1):
            catg, stepLen, sStage = 4, 4, 36
        elif stage in range(40+1,48+1):
            catg, stepLen, sStage = 5, 8, 40
        elif stage in range(48+1,54+1):
            catg, stepLen, sStage = 6, 6, 48
        elif stage in range(54+1,60+1):
            catg, stepLen, sStage = 7, 6, 54
        elif stage in range(60+1,64+1):
            catg, stepLen, sStage = 8, 4, 60
        else:
            catg, stepLen, sStage = 9, 14, 64
        return (max(((100+(((Power.Aim[catg]-Power.Aim[catg-1])/stepLen)*(stage-sStage)))-Power.Value),0))*Power.Add*0.0006 + (max((Stamina.Aim[catg]-Stamina.Value),0))*Power.Add*0.0002 + 0.15*Power.Be3 + 0.3*Power.Be4
class Will:
    Add = 9
    Value = 0
    Be3 = 0
    Be4 = 0
    tapLoc = (730,2048)
    Aim = (200,200)#限制要求
class Intell:
    Add = 9
    Value = 0
    Be3 = 0
    Be4 = 0
    tapLoc = (920,2048)
    Aim = (400,400)#软要求

class Weight():
    Race = 0
    Sleep = 0
    HangOut = 0
    Ill = 0
    Speed = 0
    Stamina = 0
    Power = 0
    Will = 0
    Intell = 0

#监控timeout异常,建立threading,出现异常即中断程序
class TimeOut():
    Latest = time.time()
    Now = time.time()
    
    def Checker():
        global CapON
        while CapON:
            TimeOut.Now = time.time()
            time.sleep(10)
            if TimeOut.Now-TimeOut.Latest > 120:
                print("!!!!!!!!!!!!Timeout ERROR!!!!!!!!!!!!")
                print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[出现未知错误,程序长时间未响应]")
                TimeOut.Latest = time.time()
                CapON = False
                threadingCap.join()
                threadingDispatch.join()

                break
        #raise TimeoutError("Unkown Errors: Interrupt")
    threadingChecker = threading.Thread(target=Checker)

#配置文件
def Config(Who:str):
    global UR, SSR, SR, data, IP
    with open("config.yaml","rb") as data:
        config = yaml.load(data.read(), Loader=yaml.FullLoader)[Who]
    UR = config['ImportantRace']
    SSR = config['ValidRace']
    SR = config['CommonRace']
    Speed.Aim = list(config['Speed'].values())
    Stamina.Aim = list(config['Stamina'].values())
    Power.Aim = list(config['Power'].values())
    Will.Aim = list(config['Will'].values())
    Intell.Aim = list(config['Intell'].values())
    data = config['DataPath']

#连接到adb设备
def adbConnect(ip):
    global IP
    #自动连接adb
    if ip=='auto':
        Command = subprocess.Popen(['adb','devices'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        Command.wait()
        Back = str(Command.stdout.read())
        Devices = []
        for c in range(len(Back)):
            if Back[c:c+8]==r'\tdevice':
                for d in range(c):
                    if Back[c-d-4:c-d]==r'\r\n':
                        Devices.append(Back[c-d:c])
                        break
        if len(Devices)==1:
            IP = Devices[0]
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[已自动连接到adb: {}]".format(IP))
            TimeOut.Latest = time.time()
        elif len(Devices)==0:
            print("!!!!!!!!!!!!没有可用的adb设备,请检查设备连接,确保至少存在一个可用设备!!!!!!!!!!!!")
            raise IndexError('None Devices Accessible.')
        else:
            print("---存在多个设备,请选择你需要的设备---")
            option = []
            for d in range(len(Devices)):
                print(d+1,':',Devices[d])
                option.append(d+1)
            select = input('输入对应数字并回车\n')
            IP = Devices[int(select)-1]
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+'[已选择到:{}]'.format(IP))
            TimeOut.Latest = time.time()
    #指定无线adb连接
    elif ':' in ip:
        print("!!!!!!!!!!!!Devices Illegal!!!!!!!!!!!!")
        print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[该脚本不支持无线adb连接]")
        raise TypeError("Devices Illegal.")

#初始化
Config(Who)
adbConnect(IP) 



#定义屏幕监控函数,设置Cap线程
screen = subprocess.Popen("adb -s "+IP+" shell screencap -p",shell=True,stdout=subprocess.PIPE)
out, error = screen.communicate()
byteImg = out.replace(b'\r\n', b'\n')
array = np.asarray(bytearray(byteImg), dtype=np.uint8)
Cap = cv2.imdecode(array, cv2.IMREAD_COLOR)
def screenCap(sleepTime=250):
    """
    通过threading循环执行,以mat形式刷新Cap变量,可以设置刷新率
    """
    global Cap
    while CapON:
        time.sleep(0.1)
        screen = subprocess.Popen("adb -s "+IP+" shell screencap -p",shell=True,stdout=subprocess.PIPE)
        out, error = screen.communicate()
        byteImg = out.replace(b'\r\n', b'\n')
        array = np.asarray(bytearray(byteImg), dtype=np.uint8)
        Cap = cv2.imdecode(array, cv2.IMREAD_COLOR)
threadingCap = threading.Thread(target=screenCap)


#判断item的存在性
def itemTell(Cap, item, miss = 0.93):
    """
    接受一个item.py中的item变量,判断item是否存在于当前Cap中,返回一个bool型变量
    """
    iH,iW = item.shape[:2]
    #图像匹配
    result = cv2.matchTemplate(Cap, item, cv2.TM_CCOEFF_NORMED)
    #统计所有相似度大于阈值的位置
    location = np.where(result >= miss)
    #定义字典
    item_dict = {}
    #循环向字典中添加item位置
    i = 1
    count = 1
    for pt in zip(*location[::-1]):
        if i > 1:
            #查重判断，判断中心是否在上一个计数区域之内
            if (pt[0]+int(iW/2)) in range((item_dict[str(count-1)][0]-int(iW/2)), (item_dict[str(count-1)][0]+int(iW/2))) and (pt[1]+int(iH/2)) in range((item_dict[str(count-1)][1]-int(iH/2)), (item_dict[str(count-1)][1]+int(iH/2))):
                pass
            else:
                item_dict[str(count)] = (pt[0]+int(iW/2),pt[1]+int(iH/2))
                count = count+1
        else:
            #第一个识别结果无需进行查重判断
            item_dict[str(i)] = (pt[0]+int(iW/2),pt[1]+int(iH/2))
            count = count+1
        i = i+1
    #统计个数，并计入字典中count元素
    item_dict['count'] = count-1
    return item_dict

#执行点击
def click(position):
    """
    在指定位置单击左键并等待0.4秒
    """
    os.system("adb -s "+IP+" shell input tap {} {}".format(position[0],position[1]))
    time.sleep(0.4)
def clickItem(item, miss=0.93):
    """
    接受一个screen路径和item路径,判断item是否存在,若存在则点击并返回True,否则不点击并返回False
    """
    ToClick = itemTell(Cap, item, miss)
    if ToClick['count'] >= 1:
            click(ToClick['1'])
            return True
    return False

#用于识别对应训练的数值
def ocrAddValue(which):
    """
    用于识别训练提升数值,接受一个屏幕路径和一个表示类型的字符串,识别对应的提升数值,并返回该数值
    """
    #截取属性表示上方包含数值的区域
    if which == 'Speed':
        zone = Cap[1500:1800,36:208]
    elif which == 'Stamina':
        zone = Cap[1500:1800,208:378]
    elif which == 'Power':
        zone = Cap[1500:1800,378:546]
    elif which == 'Will':
        zone = Cap[1500:1800,546:714]
    elif which == 'Intell':
        zone = Cap[1500:1800,714:880]
    #循环识别数字0~9
    result = []
    for o in range(10):
        result.append(itemTell(zone, i.Item.Num[o], 0.85))    #将数字o的个数与位置计入result[o]中
    #提取出识别到的数字
    USn = [] #以list形式储存一个数字与其位置
    for o in range(10):
        if result[o]['count'] > 0:
            USn.append([o, result[o]['1']])
            result[o]['count'] -= 1
            break
    for o in range(10):
        if result[o]['count'] > 0:
            if o != USn[0][0]:
                USn.append([o, result[o]['1']])
            else:
                USn.append([o, result[o]['2']])
            break
    if len(USn) == 1:   #只有一个数字
        Avalue = USn[0][0]
    else:   #将提取到的两个数字排序
        if USn[0][1][0] < USn[1][1][0]: #第一个数更靠左
            Avalue = 10*USn[0][0] + USn[1][0]
        else:
            Avalue = 10*USn[1][0] + USn[0][0]
    return Avalue
def ocrNowValue(which):
    """
    用于识别面板数值,接受一个屏幕路径和一个表示类型的字符串,识别对应的面板值,并返回该数值
    """
    #截取属性表示上方包含数值的区域
    if which == 'Speed':
        zone = Cap[1600:1800,36:208]
    elif which == 'Stamina':
        zone = Cap[1600:1800,208:378]
    elif which == 'Power':
        zone = Cap[1600:1800,378:546]
    elif which == 'Will':
        zone = Cap[1600:1800,546:714]
    elif which == 'Intell':
        zone = Cap[1600:1800,714:880]
    #循环识别数字0~9
    result = []
    for o in range(10):
        result.append(itemTell(zone, i.Item.NumS[o], 0.9))    #将数字o的个数与位置计入result[o]中
    #提取出识别到的数字
    USn = [] #以list形式储存一个数字与其位置
    for o in range(10):
        if result[o]['count'] > 0:
            USn.append([o, result[o]['1']])
            result[o]['count'] -= 1
            break
    for o in range(10):
        if result[o]['count'] > 0:
            if o != USn[0][0]:
                USn.append([o, result[o]['1']])
                result[o]['count'] -= 1
            else:
                USn.append([o, result[o]['2']])
                result[o]['count'] -= 1
            break
    for o in range(10):
        if result[o]['count'] > 0:
            if o != USn[0][0] and o != USn[1][0]:
                USn.append([o, result[o]['1']])
            elif (o != USn[0][0] and o == USn[1][0]) or (o == USn[0][0] and o != USn[1][0]):
                USn.append([o, result[o]['2']])
            elif o == USn[0][0] and o == USn[1][0]:
                USn.append([o, result[o]['3']])
            break
    if len(USn) == 1:   #只有一个数字
        Avalue = USn[0][0]
    elif len(USn) == 2: #将提取到的两个数字排序
        if USn[0][1][0] < USn[1][1][0]: #第一个数更靠左
            Avalue = 10*USn[0][0] + USn[1][0]
        else:
            Avalue = 10*USn[1][0] + USn[0][0]
    else:   #三个数字
        if USn[0][1][0] < USn[1][1][0]: #第一个在第二个左边
            if USn[2][1][0] < USn[0][1][0]: #第三个在第一个左边
                Avalue = 100*USn[2][0] + 10*USn[0][0] + USn[1][0]
            elif USn[2][1][0] > USn[1][1][0]:   #第三个在第二个右边
                Avalue = 100*USn[0][0] + 10*USn[1][0] + USn[2][0]
            else:   #第三个在中间
                Avalue = 100*USn[0][0] + 10*USn[2][0] + USn[1][0]
        elif USn[0][1][0] > USn[1][1][0]: #第一个在第二个右边
            if USn[2][1][0] < USn[1][1][0]: #第三个在第二个左边
                Avalue = 100*USn[2][0] + 10*USn[1][0] + USn[0][0]
            elif USn[2][1][0] > USn[0][1][0]:   #第三个在第一个右边
                Avalue = 100*USn[1][0] + 10*USn[0][0] + USn[2][0]
            else:   #第三个在中间
                Avalue = 100*USn[1][0] + 10*USn[2][0] + USn[0][0]
    return Avalue

#定义页面监控class,分别定义各功能下的页面类型监控函数
class pageCap():
    #Activate页面监控及其threading
    def activate():
        global Page
        while not Activate.Complete:
            time.sleep(0.2)
            #print(Page)
            if itemTell(Cap, i.Item.Waite)['count']==1:
                Page = 'Waite'
            elif itemTell(Cap, i.Item.TrainTitle)['count']==5:
                #可能是主界面、夏季合宿主界面、训练界面、档期比赛主界面
                Page = 'Home'
            elif itemTell(Cap, i.Item.ActivateOK)['count']==1:
                Page = 'FinalActivate'
            elif itemTell(Cap, i.Item.Skip)['count']==1:
                Page = 'Skip'
            elif itemTell(Cap, i.Item.ActivateSet)['count']==1:
                Page = 'SkipMode'
            else:
                Page = 'Waite'
            #print('--'+Page)
    threadingActivate = threading.Thread(target=activate)

    #Gap页面监控及其threading
    def gap():
        global Page
        while not Gap.Complete:
            time.sleep(0.2)
            #print(Page)
            if itemTell(Cap, i.Item.Waite)['count']==1:
                Page = 'Connecting'
            elif itemTell(Cap, i.Item.EventKey1)['count']==1 and itemTell(Cap, i.Item.EventKey2)['count']==1:
                Page = 'EventSelect'
            elif itemTell(Cap, i.Item.TrainTitle)['count']==5:
                #可能是主界面、夏季合宿主界面、训练界面、档期比赛主界面
                if itemTell(Cap, i.Item.MainSleep)['count']==1:
                    Page = 'Home'
                elif itemTell(Cap, i.Item.RMSkill)['count']==1:
                    Page = 'RaceHome'
                elif itemTell(Cap, i.Item.SMSleep)['count']==1:
                    Page = 'SummerHome'
                else:
                    Page = 'Train'
            elif itemTell(Cap, i.Item.Game)['count']==1:
                Page = 'Game'
            elif itemTell(Cap, i.Item.Heritage)['count']==1:
                Page = 'Heritage'
            elif itemTell(Cap, i.Item.SkillLab)['count']==1:
                Page = 'Skill'
            elif itemTell(Cap, i.Item.FansWarning)['count']==1:
                Page = 'FansWarning'
            else:
                Page = 'Waite'
            #print('--'+Page)
    
    #Home页面监控及其threading
    def home():
        global Page
        while not Home.Complete:
            time.sleep(0.2)
            if itemTell(Cap, i.Item.Waite)['count']==1:
                Page = 'Connecting'
            elif itemTell(Cap, i.Item.TrainTitle)['count']==5:
                if itemTell(Cap, i.Item.MainSleep)['count']==1:
                    Page = 'Home'
                else:
                    Page = 'Train'
            elif itemTell(Cap, i.Item.SkillLab)['count']==1:
                Page = 'Skill'
            else:
                Page = 'Waite'
            #print('--'+Page)
    
    def train():
        global Page
        while not Train.Complete:
            time.sleep(0.2)
            if itemTell(Cap, i.Item.Waite)['count']==1:
                Page = 'Connecting'
            elif itemTell(Cap, i.Item.TrainTitle)['count']==5:
                if itemTell(Cap, i.Item.MainSleep)['count']==1:
                    Page = 'Home'
                else:
                    Page = 'Train'
            elif itemTell(Cap, i.Item.SkillLab)['count']==1:
                Page = 'Skill'
            else:
                Page = 'Waite'
            #print('--'+Page)
    
    def sleep():
        global Page
        while not Sleep.Complete:
            time.sleep(0.2)
            if itemTell(Cap, i.Item.Waite)['count']==1:
                Page = 'Connecting'
            elif itemTell(Cap, i.Item.TrainTitle)['count']==5:
                #可能是主界面、夏季合宿主界面、训练界面、档期比赛主界面
                if itemTell(Cap, i.Item.MainSleep)['count']==1:
                    Page = 'Home'
                elif itemTell(Cap, i.Item.RMSkill)['count']==1:
                    Page = 'RaceHome'
                elif itemTell(Cap, i.Item.SMSleep)['count']==1:
                    Page = 'SummerHome'
                else:
                    Page = 'Train'
            elif itemTell(Cap, i.Item.SkillLab)['count']==1:
                Page = 'Skill'
            else:
                Page = 'Waite'
            #print('--'+Page)
    
    def hangout():
        global Page
        while not HangOut.Complete:
            time.sleep(0.2)
            if itemTell(Cap, i.Item.Waite)['count']==1:
                Page = 'Connecting'
            elif itemTell(Cap, i.Item.TrainTitle)['count']==5:
                if itemTell(Cap, i.Item.MainSleep)['count']==1:
                    Page = 'Home'
                else:
                    Page = 'Train'
            elif itemTell(Cap, i.Item.SkillLab)['count']==1:
                Page = 'Skill'
            else:
                Page = 'Waite'
            #print('--'+Page)
    
    def race():
        global Page
        while not Race.Complete:
            time.sleep(0.2)
            if itemTell(Cap, i.Item.Waite)['count']==1:
                Page = 'Connecting'
            elif itemTell(Cap, i.Item.TrainTitle)['count']==5:
                #可能是主界面、夏季合宿主界面、训练界面、档期比赛主界面
                if itemTell(Cap, i.Item.MainSleep)['count']==1:
                    Page = 'Home'
                elif itemTell(Cap, i.Item.RMSkill)['count']==1:
                    Page = 'RaceHome'
                elif itemTell(Cap, i.Item.SMSleep)['count']==1:
                    Page = 'SummerHome'
                else:
                    Page = 'Train'
            elif itemTell(Cap, i.Item.SkillLab)['count']==1:
                Page = 'Skill'
            elif itemTell(Cap, i.Item.SelectRaceLab)['count']==1:
                Page = 'SelectRace'
            else:
                Page = 'Waite'
            #print('--'+Page)

    def raceHome():
        global Page
        while not RaceHome.Complete:
            time.sleep(0.2)
            if itemTell(Cap, i.Item.Waite)['count']==1:
                Page = 'Connecting'
            elif itemTell(Cap, i.Item.TrainTitle)['count']==5:
                Page = 'RaceHome'
            elif itemTell(Cap, i.Item.SkillLab)['count']==1:
                Page = 'Skill'
            elif itemTell(Cap, i.Item.SelectRaceLab)['count']==1:
                Page = 'SelectRace'
            else:
                Page = 'Waite'
            #print('--'+Page)

    def summerHome():
        global Page
        while not SummerHome.Complete:
            time.sleep(0.2)
            if itemTell(Cap, i.Item.Waite)['count']==1:
                Page = 'Connecting'
            elif itemTell(Cap, i.Item.TrainTitle)['count']==5:
                #可能是主界面、夏季合宿主界面、训练界面、档期比赛主界面
                if itemTell(Cap, i.Item.MainSleep)['count']==1:
                    Page = 'Home'
                elif itemTell(Cap, i.Item.RMSkill)['count']==1:
                    Page = 'RaceHome'
                elif itemTell(Cap, i.Item.SMSleep)['count']==1:
                    Page = 'SummerHome'
                else:
                    Page = 'Train'
            elif itemTell(Cap, i.Item.SkillLab)['count']==1:
                Page = 'Skill'
            elif itemTell(Cap, i.Item.SelectRaceLab)['count']==1:
                Page = 'SelectRace'
            else:
                Page = 'Waite'
            #print('--'+Page)
##############################################################################################################################

#依次执行当前调度列表中的操作,建立threadingDispatch
def dispatch():
    """
    循环执行调度器(Dispatch)列表中的任务,一旦有任务即执行,任务一经完成即从Dispatch中删除
    """
    global Dispatch
    while CapON:
        time.sleep(0.2)
        #空调度
        if len(Dispatch)==0:
            continue

        #专属调度
        elif '.' in Dispatch[-1]:
            if (Dispatch[-1]).split('.')[0]=='Activate':
                NowDispatch = Dispatch[-1]
                if getattr(Activate, (Dispatch[-1]).split('.')[1])():
                    Dispatch.remove(NowDispatch)
            elif (Dispatch[-1]).split('.')[0]=='Gap':
                NowDispatch = Dispatch[-1]
                if getattr(Gap, (Dispatch[-1]).split('.')[1])():
                    Dispatch.remove(NowDispatch)
            elif (Dispatch[-1]).split('.')[0]=='Home':
                NowDispatch = Dispatch[-1]
                if getattr(Home, (Dispatch[-1]).split('.')[1])():
                    Dispatch.remove(NowDispatch)
            elif (Dispatch[-1]).split('.')[0]=='RaceHome':
                NowDispatch = Dispatch[-1]
                if getattr(RaceHome, (Dispatch[-1]).split('.')[1])():
                    Dispatch.remove(NowDispatch)
            elif (Dispatch[-1]).split('.')[0]=='SummerHome':
                NowDispatch = Dispatch[-1]
                if getattr(SummerHome, (Dispatch[-1]).split('.')[1])():
                    Dispatch.remove(NowDispatch)
            elif (Dispatch[-1]).split('.')[0]=='Train':
                NowDispatch = Dispatch[-1]
                if getattr(Train, (Dispatch[-1]).split('.')[1])():
                    Dispatch.remove(NowDispatch)
            elif (Dispatch[-1]).split('.')[0]=='Sleep':
                NowDispatch = Dispatch[-1]
                if getattr(Sleep, (Dispatch[-1]).split('.')[1])():
                    Dispatch.remove(NowDispatch)
            elif (Dispatch[-1]).split('.')[0]=='HangOut':
                NowDispatch = Dispatch[-1]
                if getattr(HangOut, (Dispatch[-1]).split('.')[1])():
                    Dispatch.remove(NowDispatch)
            elif (Dispatch[-1]).split('.')[0]=='Race':
                NowDispatch = Dispatch[-1]
                if getattr(Race, (Dispatch[-1]).split('.')[1])():
                    Dispatch.remove(NowDispatch)
        
        #通用调度
        elif Dispatch[-1]=='Back':
            click((50,2350))
            Dispatch.remove('Back')
        elif Dispatch[-1]=='Cancle':
            clickItem(i.Item.CancleButton)
            Dispatch.remove('Cancle')
        elif Dispatch[-1]=='GotoTrain':
            if 'Home' in Page:
                print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[前往训练]")
                TimeOut.Latest = time.time()
                click((540,2000))
                Dispatch.remove('GotoTrain')
            elif 'Train' in Page:
                Dispatch.remove('GotoTrain')

        #情况外
        else:
            print("!!!!!!!!!!!!{}:CommenDispatch Not Exists!!!!!!!!!!!!".format(Dispatch[-1]))
            Dispatch.remove(Dispatch[-1])
        
        #debug
        #print(Dispatch)
threadingDispatch = threading.Thread(target=dispatch)
    
##############################################################################################################################





##step类
#启动前
class Activate():
    #监控该step是否完成执行,一旦完成即阻断该step的页面类型监控
    Complete = False

    #该step中可能包含的分布步骤
    def OK():
        global Dispatch
        if Page=='FinalActivate':
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[确认开始育成]")
            TimeOut.Latest = time.time()
            clickItem(i.Item.ActivateOK)
            Dispatch.append('Activate.Skip')
            return True
        elif Page=='Skip':
            Dispatch.append('Activate.Skip')
            return True
        elif Page=='SkipMode':
            Dispatch.append('Activate.SkipMode')
            return True
        elif Page=='Home':
            Dispatch.append('Activate.ComfirIn')
            return True
        elif Page=='Waite':
            return False
    def Skip():
        global Dispatch
        if Page=='Skip':
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[跳过]")
            TimeOut.Latest = time.time()
            clickItem(i.Item.Skip)
            Dispatch.append('Activate.SkipMode')
            return True
        elif Page=='SkipMode':
            Dispatch.append('Activate.SkipMode')
            return True
        elif Page=='Home':
            Dispatch.append('Activate.ComfirIn')
            return True
        elif Page=='Waite':
            return False
    def SkipMode():
        global Dispatch
        if Page=='SkipMode':
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[设置跳过选项]")
            TimeOut.Latest = time.time()
            click((480,2350))
            click((480,2350))
            clickItem(i.Item.DecideButton2)
            Dispatch.append('Activate.ComfirIn')
            return True
        elif Page=='Home':
            Dispatch.append('Activate.ComfirIn')
            return True
        elif Page=='Waite':
            return False
    def ComfirIn():
        global Dispatch
        if Page=='Home':
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"已成功进入育成界面")
            TimeOut.Latest = time.time()
            Activate.Complete = True
            Gap.Gapped = True
            print("==================Activate Completed==================")
            return True
        elif Page=='Waite':
            return False

    #该step的主体函数,向调度器中添加操作,确认该step是否结束
    def main():
        """
        操作进入育成前的内容
        """
        global Dispatch
        Activate.Complete = False
        pageCap.threadingActivate.start()
        Dispatch.append('Activate.OK')
        pageCap.threadingActivate.join()
        Activate.Complete = False


#回合间隙
class Gap():
    #监控该step是否完成执行,一旦完成即阻断该step的页面类型监控
    Complete = False
    #检查进入新回合前是否出现过论外界面
    Gapped = False
    #该step执行完成后应该执行的step
    Next = 'Home'

    #该step中可能包含的分布步骤
    def ComfirIn():
        global Dispatch, stage
        if Page=='Waite':
            Gap.Gapped = True
            if clickItem(i.Item.ContinueButton):
                print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[继续]")
                TimeOut.Latest = time.time()
            elif clickItem(i.Item.ContinueButton2):
                print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[继续]")
                TimeOut.Latest = time.time()
            elif clickItem(i.Item.OKButton):
                print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[继续]")
                TimeOut.Latest = time.time()
            elif clickItem(i.Item.OKButton2):
                print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[继续]")
                TimeOut.Latest = time.time()
            elif itemTell(Cap, i.Item.RaceContinueLab)['count']==1:
                click((640,2250))
                print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[继续]")
                TimeOut.Latest = time.time()
            elif clickItem(i.Item.RetryButton):
                print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[目标未达成,再次挑战]")
                TimeOut.Latest = time.time()
                Gap.Next = 'Retry'
                Gap.Complete = True
                return True
            else:
                click((540,1800))
            return False
        elif Page=='Connecting':
            return False
        elif Page=='EventSelect':
            Gap.Gapped = True
            Dispatch.append('Gap.EventSelect')
            return False
        elif Page=='Game':
            Gap.Gapped = True
            Dispatch.append('Gap.Game')
            return False
        elif Page=='Heritage':
            Gap.Gapped = True
            Dispatch.append('Gap.Heritage')
            return False
        elif Page=='Train' or Page=='Skill':
            Gap.Gapped = True
            Dispatch.append('Back')
            time.sleep(1)
            return False
        elif Page=='FansWarning':
            Dispatch.append('Cancle')
            time.sleep(1)
            return False
        elif 'Home' in Page:
            if Gap.Gapped:
                Gap.Gapped = False
                print("================== Round "+str(stage)+" ==================")
                time.sleep(2)
                Gap.Next = Page
                while Gap.Next not in 'Home,SummerHome,RaceHome':
                    time.sleep(0.1)
                    Gap.Next = Page
                Gap.Complete = True
                return True
            elif not Gap.Gapped:
                print("!!!!!!!!!!!! NOT GAPPED !!!!!!!!!!!!")
                return False
    def EventSelect():
        print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[发生事件:默认选择选项1]")
        TimeOut.Latest = time.time()
        clickItem(i.Item.EventKey1)
        time.sleep(1)
        return True
    def Game():
        times = 0
        print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[发生抓娃娃事件,该脚本不能识别目标,将进行随机抓取]")
        TimeOut.Latest = time.time()
        while times<3:
            time.sleep(0.1)
            if Page=='Game':
                Game = (540,2250)
                print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[第"+str(times+1)+"次抓取]")
                TimeOut.Latest = time.time()
                os.system("adb -s "+IP+" shell input swipe "+str(Game[0])+' '+str(Game[1])+' '+str(Game[0]+1)+' '+str(Game[1])+' '+str(random.randint(1000,3000)))
                times += 1
                time.sleep(0.3)
            else:
                time.sleep(0.3)
        return True
    def Heritage():
        print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[因子继承]")
        TimeOut.Latest = time.time()
        clickItem(i.Item.Heritage)
        return True

    #该step的主体函数,向调度器中添加操作,确认该step是否结束
    def main():
        global Dispatch
        threadingGap = threading.Thread(target=pageCap.gap)
        Gap.Complete = False
        threadingGap.start()
        Dispatch.insert(0,'Gap.ComfirIn')
        if not CapON:
            Gap.Complete = True
            return False
        threadingGap.join()
        Gap.Complete = False


#回合权重判断
class Home():
    Complete = False
    Next = 'Intell'

    def JudgeRace():
        global Dispatch
        print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[常规训练]")
        TimeOut.Latest = time.time()
        if stage in UR.values():
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[该回合存在极端重要比赛,跳过权重判断,并前往获取技能,以保证胜率]")
            TimeOut.Latest = time.time()
            Home.Next = 'Race'
            Home.Complete = True
        elif stage in SSR.values():
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[该回合存在重要比赛,可以在其余操作收益不高时参加比赛]")
            TimeOut.Latest = time.time()
            Weight.Race = 3.1
            Dispatch.append('Home.JudgeState')
        elif stage in SR.values():
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[该回合存在优质比赛,可以在其余操作收益差时参加比赛]")
            TimeOut.Latest = time.time()
            Weight.Race = 1.6
            Dispatch.append('Home.JudgeState')
        else:
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[本回合无优质比赛]")
            TimeOut.Latest = time.time()
            Dispatch.append('Home.JudgeState')
        return True
    def JudgeState():
        global Dispatch
        if Page=='Home':
            Home.IllComfir()
            Home.EnergyComfir()
            Home.MotivationComfir()
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[体力:{}    干劲:{}    医务室:{}]".format(Energy,Motivation,Ill))
            TimeOut.Latest = time.time()
            Dispatch.append('Home.JudgeTrain')
            return True
        elif Page=='Skill' or Page=='Train':
            Dispatch.append('Back')
            return False
        else:
            return False
    def JudgeTrain():
        global Dispatch
        print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[开始读取训练]")
        TimeOut.Latest = time.time()
        Dispatch.append('GotoTrain')
        Dispatch.insert(0,'Home.ToSpeed')
        Dispatch.insert(0,'Home.SpeedComfir')
        Dispatch.insert(0,'Home.ToStamina')
        Dispatch.insert(0,'Home.StaminaComfir')
        Dispatch.insert(0,'Home.ToPower')
        Dispatch.insert(0,'Home.PowerComfir')
        Dispatch.insert(0,'Home.ToWill')
        Dispatch.insert(0,'Home.WillComfir')
        Dispatch.insert(0,'Home.ToIntell')
        Dispatch.insert(0,'Home.IntellComfir')
        Dispatch.insert(0,'Home.WeightCalculate')
        return True


    #JudgeState的内容,读取数值,但不计算权重
    def IllComfir():
        global Ill, Dispatch
        ill = itemTell(Cap, i.Item.illButton)
        if ill['count'] == 1:
            dot = Cap[ill['1'][1]-25, ill['1'][0]-100]
            if (int(dot[0])+int(dot[1])+int(dot[2])) > 600:
                Ill = True
            else:
                Ill = False
    def EnergyComfir():
        #读取数值
        global Energy, Dispatch
        w, UnF = 750, 0
        while w >= 350:
            Cp = Cap[EnergyLoc, w]
            if int(Cp[0]) in range(110, 130) and int(Cp[1]) in range(110, 130) and int(Cp[2]) in range(110, 130):
                UnF += 1
            w -= 8
        Energy = 100 - 2*UnF
        #计算权重
    def MotivationComfir():
        global Motivation, Dispatch
        if itemTell(Cap, i.Item.Motivation5)['count'] == 1:
            #绝好调
            Motivation = 5
        elif itemTell(Cap, i.Item.Motivation4)['count'] == 1:
            #干劲较好
            Motivation = 4
        elif itemTell(Cap, i.Item.Motivation3)['count'] == 1:
            #干劲普通
            Motivation = 3
        else:
            #干劲普通以下
            Motivation = 2

    #JudgeTrain的内容,训练读取数据,但不计算权重
    def ToSpeed():
        if Page!='Train':
            return False
        elif Page=='Train':
            time.sleep(2)
            IsSpeed = 0
            for j in range(6):
                IsSpeed += itemTell(Cap, i.Item.SpeedLab[j])['count']
            if IsSpeed:
                return True
            
            else:
                click(Speed.tapLoc)
                return True
    def SpeedComfir():
        if Page!='Train':
            return False
        elif Page=='Train':
            IsSpeed = 0
            for j in range(6):
                IsSpeed += itemTell(Cap, i.Item.SpeedLab[j])['count']
            if IsSpeed:
                Speed.Value = ocrNowValue('Speed')
                print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[速度:{}]".format(Speed.Value))
                TimeOut.Latest = time.time()
                Speed.Add = ocrAddValue('Speed')
                Speed.Be3 = itemTell(Cap, i.Item.Be3)['count']
                Speed.Be4 = itemTell(Cap, i.Item.Be4)['count']
                print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[训练主属性提升值:{}  低羁绊修正:{:.2f}  近满羁绊修正{:.2f}]".format(Speed.Add, 0.15*Speed.Be3, 0.3*Speed.Be4))
                TimeOut.Latest = time.time()
                return True
            else:
                return False
    def ToStamina():
        if Page!='Train':
            return False
        elif Page=='Train':
            time.sleep(0.5)
            IsStamina = 0
            for j in range(6):
                IsStamina += itemTell(Cap, i.Item.StaminaLab[j])['count']
            if IsStamina:
                return True
            else:
                click(Stamina.tapLoc)
                return True
    def StaminaComfir():
        if Page!='Train':
            return False
        elif Page=='Train':
            IsStamina = 0
            for j in range(6):
                IsStamina += itemTell(Cap, i.Item.StaminaLab[j])['count']
            if IsStamina:
                Stamina.Value = ocrNowValue('Stamina')
                print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[耐力:{}]".format(Stamina.Value))
                TimeOut.Latest = time.time()
                Stamina.Add = ocrAddValue('Stamina')
                Stamina.Be3 = itemTell(Cap, i.Item.Be3)['count']
                Stamina.Be4 = itemTell(Cap, i.Item.Be4)['count']
                print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[训练主属性提升值:{}  低羁绊修正:{:.2f}  近满羁绊修正{:.2f}]".format(Stamina.Add, 0.15*Stamina.Be3, 0.3*Stamina.Be4))
                TimeOut.Latest = time.time()
                return True
            else:
                return False
    def ToPower():
        if Page!='Train':
            return False
        elif Page=='Train':
            time.sleep(0.5)
            IsPower = 0
            for j in range(6):
                IsPower += itemTell(Cap, i.Item.PowerLab[j])['count']
            if IsPower:
                return True
            else:
                click(Power.tapLoc)
                return True
    def PowerComfir():
        if Page!='Train':
            return False
        elif Page=='Train':
            IsPower = 0
            for j in range(6):
                IsPower += itemTell(Cap, i.Item.PowerLab[j])['count']
            if IsPower:
                Power.Value = ocrNowValue('Power')
                print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[力量:{}]".format(Power.Value))
                TimeOut.Latest = time.time()
                Power.Add = ocrAddValue('Power')
                Power.Be3 = itemTell(Cap, i.Item.Be3)['count']
                Power.Be4 = itemTell(Cap, i.Item.Be4)['count']
                print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[训练主属性提升值:{}  低羁绊修正:{:.2f}  近满羁绊修正{:.2f}]".format(Power.Add, 0.15*Power.Be3, 0.3*Power.Be4))
                TimeOut.Latest = time.time()
                return True
            else:
                return False
    def ToWill():
        if Page!='Train':
            return False
        elif Page=='Train':
            time.sleep(0.5)
            IsWill = 0
            for j in range(6):
                IsWill += itemTell(Cap, i.Item.WillLab[j])['count']
            if IsWill:
                return True
            else:
                click(Will.tapLoc)
                return True
    def WillComfir():
        if Page!='Train':
            return False
        elif Page=='Train':
            IsWill = 0
            for j in range(6):
                IsWill += itemTell(Cap, i.Item.WillLab[j])['count']
            if IsWill:
                Will.Value = ocrNowValue('Will')
                print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[根性:{}]".format(Will.Value))
                TimeOut.Latest = time.time()
                Will.Add = ocrAddValue('Will')
                Will.Be3 = itemTell(Cap, i.Item.Be3)['count']
                Will.Be4 = itemTell(Cap, i.Item.Be4)['count']
                print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[训练主属性提升值:{}  低羁绊修正:{:.2f}  近满羁绊修正{:.2f}]".format(Will.Add, 0.15*Will.Be3, 0.3*Will.Be4))
                TimeOut.Latest = time.time()
                return True
            else:
                return False
    def ToIntell():
        if Page!='Train':
            return False
        elif Page=='Train':
            time.sleep(0.5)
            IsIntell = 0
            for j in range(6):
                IsIntell += itemTell(Cap, i.Item.IntellLab[j])['count']
            if IsIntell:
                return True
            else:
                click(Intell.tapLoc)
                return True
    def IntellComfir():
        if Page!='Train':
            return False
        elif Page=='Train':
            IsIntell = 0
            for j in range(6):
                IsIntell += itemTell(Cap, i.Item.IntellLab[j])['count']
            if IsIntell:
                Intell.Value = ocrNowValue('Intell')
                print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[智力:{}]".format(Intell.Value))
                TimeOut.Latest = time.time()
                Intell.Add = ocrAddValue('Intell')
                Intell.Be3 = itemTell(Cap, i.Item.Be3)['count']
                Intell.Be4 = itemTell(Cap, i.Item.Be4)['count']
                print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[训练主属性提升值:{}  低羁绊修正:{:.2f}  近满羁绊修正{:.2f}]".format(Intell.Add, 0.15*Intell.Be3, 0.3*Intell.Be4))
                TimeOut.Latest = time.time()
                return True
            else:
                return False

    #计算并比较权重
    def WeightCalculate():
        global Dispatch
        #Ill
        Weight.Ill = 5.8*(int(Ill)-0.5)
        #HangOut
        if Motivation==5:
            Weight.HangOut -= 0.3
        elif Motivation==4:
            Weight.HangOut += 1.5
        elif Motivation==3:
            Weight.HangOut += 2.6
        elif Motivation<3:
            Weight.HangOut += 3
        #Sleep
        if Energy in range(70,100):
            Weight.Sleep -= 0.3
        elif Energy in range(60,70):
            Weight.HangOut += 0.3
            if stage==36 or stage==59:
                Weight.Sleep += 1
        elif Energy in range(50,60):
            Weight.Sleep += 0.9
            if stage==36 or stage==59:
                Weight.Sleep += 1
        elif Energy in range(45,50):
            Weight.Sleep += 1.9
            if stage==36 or stage==59:
                Weight.Sleep += 1
        elif Energy in range(30,45):
            Weight.Sleep += 2.9
            if stage==36 or stage==59:
                Weight.Sleep += 1
        elif Energy in range(0,30):
            Weight.Sleep += 4
        #Sleep&Out&Ill
        if stage>57:
            Weight.Ill -= 0.4
            Weight.Sleep -= 0.4
            Weight.HangOut -= 0.4
        #Train
        Weight.Speed += Speed.Weigh() - int(Ill)*0.7 - int(stage>57)*0.3
        Weight.Stamina += Stamina.Weigh() - int(Ill)*0.7 - int(stage>57)*0.6
        Weight.Power += Power.Weigh() - int(Ill)*0.7 - int(stage>57)*0.3
        Weight.Will += 0.06*(Will.Add-9) + 0.15*Will.Be3 + 0.3*Will.Be4 + min((Will.Aim[0]-Will.Value),0)*0.01 - int(Ill)*0.7 - int(stage>57)*0.3
        Weight.Intell += 0.06*(Intell.Add-9) + 0.15*Intell.Be3 + 0.3*Intell.Be4 + int(Intell.Add>21)*int(Energy>40)*max((95-Energy),0)*0.015*(min((Energy-39),25))*0.04 - int(Ill)*0.7 - int(stage>57)*0.3
        Dispatch.append('Home.WeightCompare')
        return True
    def WeightCompare():
        global Dispatch
        sW = {'Sleep':Weight.Sleep, 'HangOut':Weight.HangOut, 'Race':Weight.Race, 'Speed':Weight.Speed, 'Stamina':Weight.Stamina, 'Power':Weight.Power, 'Will':Weight.Will, 'Intell':Weight.Intell, 'Ill':Weight.Ill}
        print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[Sleep:{:.2f}  Hangout:{:.2f}  Race:{:.2f}  Speed:{:.2f}  Stamina:{:.2f}  Power:{:.2f}  Will:{:.2f}  Intell:{:.2f}  ill:{:.2f}]".format(sW['Sleep'],sW['HangOut'],sW['Race'],sW['Speed'],sW['Stamina'],sW['Power'],sW['Will'],sW['Intell'],sW['Ill']))
        TimeOut.Latest = time.time()
        Home.Next = max(sW, key=sW.get)
        print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[执行:{}]".format(Home.Next))
        TimeOut.Latest = time.time()
        Dispatch.append('Home.WeightClear')
        Home.Complete = True
        return True
    def WeightClear():
        Weight.Race, Weight.Ill, Weight.Sleep, Weight.HangOut, Weight.Speed, Weight.Stamina, Weight.Power, Weight.Will, Weight.Intell = 0,0,0,0,0,0,0,0,0
        return True

    def main():
        global Dispatch
        threadingHome = threading.Thread(target=pageCap.home)
        Home.Complete = False
        threadingHome.start()
        Dispatch.insert(0,'Home.JudgeRace')
        if not CapON:
            Home.Complete = True
            return False
        threadingHome.join()
        Home.Complete = False

class SummerHome():
    Complete = False
    Next = 'Intell'

    def JudgeState():
        global Dispatch
        if 'Home' in Page:
            Home.IllComfir()
            Home.EnergyComfir()
            Home.MotivationComfir()
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[体力:{}    干劲:{}    医务室:{}]".format(Energy,Motivation,Ill))
            TimeOut.Latest = time.time()
            Dispatch.append('SummerHome.JudgeTrain')
            return True
        elif Page=='Skill' or 'Train' in Page:
            Dispatch.append('Back')
            return False
        else:
            return False
    def JudgeTrain():
        global Dispatch
        print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[开始读取训练]")
        TimeOut.Latest = time.time()
        Dispatch.append('GotoTrain')
        Dispatch.insert(0,'Home.ToSpeed')
        Dispatch.insert(0,'Home.SpeedComfir')
        Dispatch.insert(0,'Home.ToStamina')
        Dispatch.insert(0,'Home.StaminaComfir')
        Dispatch.insert(0,'Home.ToPower')
        Dispatch.insert(0,'Home.PowerComfir')
        Dispatch.insert(0,'Home.ToWill')
        Dispatch.insert(0,'Home.WillComfir')
        Dispatch.insert(0,'Home.ToIntell')
        Dispatch.insert(0,'Home.IntellComfir')
        Dispatch.insert(0,'SummerHome.WeightCalculate')
        return True

    #JudgeState的内容,读取数值,但不计算权重
    def IllComfir():
        global Ill, Dispatch
        ill = itemTell(Cap, i.Item.illButton)
        if ill['count'] == 1:
            dot = Cap[ill['1'][1]-25, ill['1'][0]-100]
            if (int(dot[0])+int(dot[1])+int(dot[2])) > 600:
                Ill = True
            else:
                Ill = False
    def EnergyComfir():
        #读取数值
        global Energy, Dispatch
        w, UnF = 750, 0
        while w >= 350:
            Cp = Cap[EnergyLoc, w]
            if int(Cp[0]) in range(110, 130) and int(Cp[1]) in range(110, 130) and int(Cp[2]) in range(110, 130):
                UnF += 1
            w -= 8
        Energy = 100 - 2*UnF
        #计算权重
    def MotivationComfir():
        global Motivation, Dispatch
        if itemTell(Cap, i.Item.Motivation5)['count'] == 1:
            #绝好调
            Motivation = 5
        elif itemTell(Cap, i.Item.Motivation4)['count'] == 1:
            #干劲较好
            Motivation = 4
        elif itemTell(Cap, i.Item.Motivation3)['count'] == 1:
            #干劲普通
            Motivation = 3
        else:
            #干劲普通以下
            Motivation = 2

    #计算并比较权重
    def WeightCalculate():
        global Dispatch
        #不执行的权重
        Weight.Race, Weight.Ill, Weight.HangOut = -10, -10, -10
        #HangOut
        if Motivation==5:
            Weight.Sleep -= 0.5
        elif Motivation==4:
            Weight.Sleep += 1.2
        elif Motivation==3:
            Weight.Sleep += 2.6
        elif Motivation<3:
            Weight.Sleep += 3
        #Sleep
        if Energy in range(70,100):
            Weight.Sleep -= 0.5
        elif Energy in range(60,70):
            Weight.HangOut += 0.3
        elif Energy in range(50,60):
            Weight.Sleep += 0.9
        elif Energy in range(45,50):
            Weight.Sleep += 1.9
        elif Energy in range(30,45):
            Weight.Sleep += 2.9
        elif Energy in range(0,30):
            Weight.Sleep += 6
        Weight.Sleep *= 0.7
        #Train
        Weight.Speed += Speed.Weigh() - int(Ill)*0.7 + 0.5
        Weight.Stamina += Stamina.Weigh() - int(Ill)*0.7 + 0.5
        Weight.Power += Power.Weigh() - int(Ill)*0.7 + 0.5
        Weight.Will += 0.06*(Will.Add-9) + 0.15*Will.Be3 + 0.3*Will.Be4 + min((Will.Aim[0]-Will.Value),0)*0.01 - int(Ill)*0.7 + 0.5
        Weight.Intell += 0.06*(Intell.Add-9) + 0.15*Intell.Be3 + 0.3*Intell.Be4 + int(Intell.Add>21)*int(Energy>40)*max((95-Energy),0)*0.017*(min((Energy-39),25))*0.05 - int(Ill)*0.7 + 0.5
        Dispatch.append('SummerHome.WeightCompare')
        return True
    def WeightCompare():
        global Dispatch
        sW = {'Sleep':Weight.Sleep, 'Speed':Weight.Speed, 'Stamina':Weight.Stamina, 'Power':Weight.Power, 'Will':Weight.Will, 'Intell':Weight.Intell}
        print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[Sleep:{:.2f}  Speed:{:.2f}  Stamina:{:.2f}  Power:{:.2f}  Will:{:.2f}  Intell:{:.2f}]".format(sW['Sleep'],sW['Speed'],sW['Stamina'],sW['Power'],sW['Will'],sW['Intell']))
        TimeOut.Latest = time.time()
        SummerHome.Next = max(sW, key=sW.get)
        print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[执行:{}]".format(SummerHome.Next))
        TimeOut.Latest = time.time()
        Dispatch.append('Home.WeightClear')
        SummerHome.Complete = True
        return True

    def main():
        global Dispatch
        threadingSummerHome = threading.Thread(target=pageCap.summerHome)
        SummerHome.Complete = False
        threadingSummerHome.start()
        print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[夏季合宿]")
        TimeOut.Latest = time.time()
        Dispatch.append('SummerHome.JudgeState')
        if not CapON:
            SummerHome.Complete = True
            return False
        threadingSummerHome.join()
        SummerHome.Complete = False

class RaceHome():
    Complete = False
    Swipe = 0

    def Skill():##完成技能获取,不兼容RaceHome,进行完整的技能获取流程,返回主界面
        global Dispatch
        Dispatch.append('RaceHome.TapSkill')
    def Race():##从主界面前往比赛,选择比赛进入回合间隙,不兼容RaceHome
        global Dispatch
        Dispatch.insert(0,'RaceHome.TapRace')

    def TapSkill():
        if Page=='RaceHome':
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[前往技能]")
            TimeOut.Latest = time.time()
            click((450,2200))
            Dispatch.append('RaceHome.SkillObtain')
            return True
        elif Page=='Skill':
            Dispatch.append('RaceHome.SkillObtain')
            return True
        else:
            Dispatch.append('Back')##确保回到主界面
            return False
    def SkillObtain():##仅负责滑动屏幕、点击技能右侧的加号,不履行点击下方获取技能的职责
        SkillList = []##此处可以加入#条件#获取技能
        SkillList.append(i.Item.SkillDict['脱出术'])
        SkillList.append(i.Item.SkillDict['弯道灵巧'])
        SkillList.append(i.Item.SkillDict['弧线的教授'])
        SkillList.append(i.Item.SkillDict['直线加速'])
        SkillList.append(i.Item.SkillDict['直线灵巧'])
        SkillList.append(i.Item.SkillDict['出闸'])
        SkillList.append(i.Item.SkillDict['圆弧的艺术家'])
        SkillList.append(i.Item.SkillDict['弯道回复'])
        if Page=='Skill':
            time.sleep(1)
            for c in range(len(SkillList)):##
                Skill = itemTell(Cap, SkillList[c])#添加第c+1个技能的信息
                if Skill['count'] == 1:
                    click((976,Skill['1'][1]))#点击与第c+1个技能高度相同的屏幕右侧
            os.system("adb -s "+IP+" shell input swipe 540 1800 540 1300 1000")#向上滑动屏幕
            RaceHome.Swipe += 1
            time.sleep(2)
            if RaceHome.Swipe>5:
                Dispatch.append('RaceHome.SkillComfir')
                RaceHome.Swipe = 0
                return True
            return False
        else:
            return False
    def SkillComfir():
        print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[尝试获取技能]")
        TimeOut.Latest = time.time()
        click((600,2050))
        if itemTell(Cap, i.Item.SkillObtainComfirWindow)['count']==1:
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[确认获取技能]")
            TimeOut.Latest = time.time()
            click((620,2100))
            return True
        else:
            if Race.Swipe>3:
                print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[没有能够获取的技能]")
                TimeOut.Latest = time.time()
                Race.Swipe = 0
                return True
            Race.Swipe += 1
            time.sleep(0.5)
            return False

    def TapRace():##仅Home,无需报告进入SelectRace,执行isSelectRace
        if Page=='RaceHome':
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[前往比赛]")
            TimeOut.Latest = time.time()
            click((700,2200))
            Dispatch.append('RaceHome.isSelectRace')
            return True
        elif Page=='SelectRace':
            Dispatch.append('RaceHome.SelectRace')
            return True
        else:
            Dispatch.append('Back')##确保回到主界面
            return False
    def isSelectRace():##应对第一次出现的CommendWindow以及RaceWarning,报告进入SelectRace
        if Page=='SelectRace':
            Dispatch.append('RaceHome.SelectRace')
            Race.First = True
            return True
        elif itemTell(Cap, i.Item.RaceWarningWindow)['count']==1 and Race.First:
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[无视连战警告]")
            TimeOut.Latest = time.time()
            clickItem(i.Item.OKButton)
            time.sleep(1)
            click((700,2200))
            Race.First = False
            return False
        else:
            return False
    def SelectRace():##选择比赛并点击参赛,对接SelectRaceComfirWindow函数,导向确认窗口
        if Page=='SelectRace':
            clickItem(i.Item.GoRaceButton)
            Dispatch.append('RaceHome.AfterSelectRaceWindow')
            return True
        else:
            return False
    def AfterSelectRaceWindow():
        if itemTell(Cap, i.Item.AfterSelectRaceWindow)['count']==1:
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[确认参赛]")
            TimeOut.Latest = time.time()
            clickItem(i.Item.GoRaceButton)
            Dispatch.append('RaceHome.ViewResult')
            return True
        else:
            return False
    def ViewResult():
        if clickItem(i.Item.ViewResultButton):
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[观看结果]")
            TimeOut.Latest = time.time()
            RaceHome.Complete = True
            return True
        else:
            return False

    def main():
        global Dispatch
        threadingRaceHome = threading.Thread(target=pageCap.raceHome)
        RaceHome.Complete = False
        threadingRaceHome.start()
        print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[档期比赛]")
        TimeOut.Latest = time.time()
        if stage in range(0,60):
            RaceHome.Skill()
        RaceHome.Race()
        if not CapON:
            RaceHome.Complete = True
            return False
        threadingRaceHome.join()
        RaceHome.Complete = False


#回合操作执行
class Train():
    Complete = False

    def ConductSpeed():
        if Page!='Train':
            return False
        elif Page=='Train':
            time.sleep(0.5)
            click(Speed.tapLoc)
            click(Speed.tapLoc)
            Train.Complete = True
            return True
    def ConductStamina():
        if Page!='Train':
            return False
        elif Page=='Train':
            time.sleep(0.5)
            click(Stamina.tapLoc)
            click(Stamina.tapLoc)
            Train.Complete = True
            return True
    def ConductPower():
        if Page!='Train':
            return False
        elif Page=='Train':
            time.sleep(0.5)
            click(Power.tapLoc)
            click(Power.tapLoc)
            Train.Complete = True
            return True
    def ConductWill():
        if Page!='Train':
            return False
        elif Page=='Train':
            time.sleep(0.5)
            click(Will.tapLoc)
            click(Will.tapLoc)
            Train.Complete = True
            return True
    def ConductIntell():
        if Page!='Train':
            return False
        elif Page=='Train':
            time.sleep(0.5)
            click(Intell.tapLoc)
            click(Intell.tapLoc)
            Train.Complete = True
            return True

    def main(which:str):
        global Dispatch
        threadingTrain = threading.Thread(target=pageCap.train)
        Train.Complete = False
        threadingTrain.start()
        Dispatch.append('Train.Conduct'+which)
        if not CapON:
            Train.Complete = True
            return False
        threadingTrain.join()
        Train.Complete = False

class Sleep():##需要兼容夏季合宿的休息按钮,兼具Ill执行权限
    Complete = False

    def TapSleep():
        global Dispatch
        if 'Home' in Page:
            click((200,2000))
            Dispatch.append('Sleep.ComfirSleep')
            return True
        elif itemTell(Cap, i.Item.SleepWindow)['count']==1:
            Dispatch.append('Sleep.ComfirSleep')
            return True
        else:
            return False
    def ComfirSleep():
        if itemTell(Cap, i.Item.SleepWindow)['count']==1 or itemTell(Cap, i.Item.SummerSleepWindow)['count']==1:
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[确认休息]")
            TimeOut.Latest = time.time()
            clickItem(i.Item.OKButton)
            Sleep.Complete = True
            return True
        else:
            return False

    def TapIll():
        global Dispatch
        if Page=='Home':
            click((250,2200))
            Dispatch.append('Sleep.ComfirIll')
            return True
        elif itemTell(Cap, i.Item.IllWindow)['count']==1:
            Dispatch.append('Sleep.ComfirIll')
            return True
        else:
            return False
    def ComfirIll():
        if itemTell(Cap, i.Item.IllWindow)['count']==1:
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[确认治疗]")
            TimeOut.Latest = time.time()
            clickItem(i.Item.OKButton)
            Sleep.Complete = True
            return True
        else:
            return False

    def main(which:str):
        global Dispatch
        threadingSleep = threading.Thread(target=pageCap.sleep)
        Sleep.Complete = False
        threadingSleep.start()
        if which=='Sleep':
            Dispatch.append('Back')
            Dispatch.insert(0,'Sleep.TapSleep')
        else:
            Dispatch.append('Back')
            Dispatch.insert(0,'Sleep.TapIll')
        if not CapON:
            Sleep.Complete = True
            return False
        threadingSleep.join()
        Sleep.Complete = False

class HangOut():##夏季合宿不执行HangOut操作,合并到Sleep中
    Complete = False
    timesTMCH = 0

    def TapHangOut():
        global Dispatch
        if Page=='Home':
            click((540,2200))
            Dispatch.append('HangOut.SelectHangOut')
            return True
        elif itemTell(Cap, i.Item.HangOutSelect)['count']==1:
            Dispatch.append('HangOut.SelectHangOut')
            return True
        elif itemTell(Cap, i.Item.HangOutWindow)['count']==1:
            Dispatch.append('HangOut.ComfirHangOut')
            return True
        else:
            return False
    def SelectHangOut():
        global Dispatch
        if itemTell(Cap, i.Item.HangOutSelect)['count']==1:
            if HangOut.timesTMCH<5:
                print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[选择到代理理事长]")
                TimeOut.Latest = time.time()
                clickItem(i.Item.HangOutTMCH)
                HangOut.timesTMCH += 1
            else:
                print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[选择到培育马娘]")
                TimeOut.Latest = time.time()
                click((540,itemTell(Cap,i.Item.HangOutTMCH,0.8)['1'][1]+100))
            Dispatch.append('HangOut.ComfirHangOut')
            return True
        elif itemTell(Cap, i.Item.HangOutWindow)['count']==1:
            Dispatch.append('HangOut.ComfirHangOut')
            return True
        else:
            return False
    def ComfirHangOut():
        if itemTell(Cap, i.Item.HangOutWindow)['count']==1:
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[确认外出]")
            TimeOut.Latest = time.time()
            clickItem(i.Item.OKButton)
            HangOut.Complete = True
            return True
        else:
            return False

    def main():
        global Dispatch
        threadingHangOut = threading.Thread(target=pageCap.hangout)
        HangOut.Complete = False
        threadingHangOut.start()
        Dispatch.append('Back')
        Dispatch.insert(0,'HangOut.TapHangOut')
        if not CapON:
            HangOut.Complete = True
            return False
        threadingHangOut.join()
        HangOut.Complete = False

class Race():##需要根据stage判断是否获取技能,并主动前往获取技能,参加比赛,直到进入Gap(不考虑SummerHome,不兼容RaceHome)
    Complete = False
    Swipe = 0
    First = True

    #主体分为两部分,获取技能函数模块、参加比赛函数模块
    def Skill():##完成技能获取,不兼容RaceHome,进行完整的技能获取流程,返回主界面
        global Dispatch
        Dispatch.append('Race.TapSkill')
    def Race():##从主界面前往比赛,选择比赛进入回合间隙,不兼容RaceHome
        global Dispatch
        Dispatch.insert(0,'Race.TapRace')

    #Skill操作功能函数
    def TapSkill():
        if Page=='Home':
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[前往技能]")
            TimeOut.Latest = time.time()
            click((850,2000))
            Dispatch.append('Race.SkillObtain')
            return True
        elif Page=='Skill':
            Dispatch.append('Race.SkillObtain')
            return True
        else:
            Dispatch.append('Back')##确保回到主界面
            return False
    def SkillObtain():##仅负责滑动屏幕、点击技能右侧的加号,不履行点击下方获取技能的职责
        SkillList = []##此处可以加入#条件#获取技能
        SkillList.append(i.Item.SkillDict['脱出术'])
        SkillList.append(i.Item.SkillDict['弯道灵巧'])
        SkillList.append(i.Item.SkillDict['弧线的教授'])
        SkillList.append(i.Item.SkillDict['直线加速'])
        SkillList.append(i.Item.SkillDict['直线灵巧'])
        SkillList.append(i.Item.SkillDict['出闸'])
        SkillList.append(i.Item.SkillDict['圆弧的艺术家'])
        SkillList.append(i.Item.SkillDict['弯道回复'])
        if Page=='Skill':
            time.sleep(1)
            for c in range(len(SkillList)):##
                Skill = itemTell(Cap, SkillList[c])#添加第c+1个技能的信息
                if Skill['count'] == 1:
                    click((976,Skill['1'][1]))#点击与第c+1个技能高度相同的屏幕右侧
            os.system("adb -s "+IP+" shell input swipe 540 1800 540 1200 1000")#向上滑动屏幕
            Race.Swipe += 1
            time.sleep(2)
            if Race.Swipe>5:
                Dispatch.append('Race.SkillComfir')
                Race.Swipe = 0
                return True
            return False
        else:
            return False
    def SkillComfir():
        print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[尝试获取技能]")
        TimeOut.Latest = time.time()
        click((600,2050))
        time.sleep(0.5)
        if itemTell(Cap, i.Item.SkillObtainComfirWindow)['count']==1:
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[确认获取技能]")
            TimeOut.Latest = time.time()
            click((620,2100))
            return True
        else:
            if Race.Swipe>3:
                print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[没有能够获取的技能]")
                TimeOut.Latest = time.time()
                Race.Swipe = 0
                return True
            Race.Swipe += 1
            return False

    #Race操作功能函数
    def TapRace():##仅Home,无需报告进入SelectRace,执行isSelectRace
        if Page=='Home':
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[前往比赛]")
            TimeOut.Latest = time.time()
            click((800,2200))
            Dispatch.append('Race.isSelectRace')
            return True
        elif Page=='SelectRace':
            Dispatch.append('Race.SelectRace')
            return True
        else:
            Dispatch.append('Back')##确保回到主界面
            return False
    def isSelectRace():##应对第一次出现的CommendWindow以及RaceWarning,报告进入SelectRace
        if Page=='SelectRace':
            Dispatch.append('Race.SelectRace')
            Race.First = True
            return True
        elif itemTell(Cap, i.Item.RaceWarningWindow)['count']==1 and Race.First:
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[无视连战警告]")
            TimeOut.Latest = time.time()
            clickItem(i.Item.OKButton)
            time.sleep(1)
            click((800,2200))
            Race.First = False
            return False
        elif itemTell(Cap, i.Item.RaceCommendWindow)['count']==1 and Race.First:
            clickItem(i.Item.DecideButton2)
            Race.First = False
            return False
        else:
            return False
    def SelectRace():##选择比赛并点击参赛,对接SelectRaceComfirWindow函数,导向确认窗口
        if clickItem(i.Item.ToRace[str(stage)]):
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[选择到对应比赛]")
            TimeOut.Latest = time.time()
            clickItem(i.Item.GoRaceButton)
            Race.Swipe = 0
            Dispatch.append('Race.AfterSelectRaceWindow')
            return True
        elif Race.Swipe<3:
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[没有找到目标,上划屏幕]")
            TimeOut.Latest = time.time()
            os.system("adb -s "+IP+" shell input swipe 540 1800 540 1400 1000")    #向上滑动屏幕
            Race.Swipe += 1
            time.sleep(2)
            return False
        else:
            print("!!!!!!!!!!!!Warning:Item Cannot Be Found!!!!!!!!!!!!")
            clickItem(i.Item.GoRaceButton)
            Race.Swipe = 0
            Dispatch.append('Race.AfterSelectRaceWindow')
            return True
    def AfterSelectRaceWindow():
        if itemTell(Cap, i.Item.AfterSelectRaceWindow)['count']==1:
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[确认参赛]")
            TimeOut.Latest = time.time()
            clickItem(i.Item.GoRaceButton)
            Dispatch.append('Race.ViewResult')
            return True
        else:
            return False
    def ViewResult():
        if clickItem(i.Item.ViewResultButton):
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[观看结果]")
            TimeOut.Latest = time.time()
            Race.Complete = True
            return True
        else:
            return False

    def main():
        global Dispatch
        threadingRace = threading.Thread(target=pageCap.race)
        Race.Complete = False
        threadingRace.start()
        if stage in UR.values() and stage in range(0,60):
            Race.Skill()
        Race.Race()
        if not CapON:
            Race.Complete = True
            return False
        threadingRace.join()
        Race.Complete = False


class Finish():
    def ConfirmOut():
        if clickItem(i.Item.ContinueButton):
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[继续]")
            TimeOut.Latest = time.time()
            return False
        elif clickItem(i.Item.ContinueButton2):
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[继续]")
            TimeOut.Latest = time.time()
            return False
        elif clickItem(i.Item.OKButton):
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[继续]")
            TimeOut.Latest = time.time()
            return False
        elif clickItem(i.Item.OKButton2):
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[继续]")
            TimeOut.Latest = time.time()
            return False
        elif itemTell(Cap, i.Item.RaceContinueLab)['count']==1:
            click((640,2250))
            print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[继续]")
            TimeOut.Latest = time.time()
            return False
        elif itemTell(Cap, i.Item.CompleteLab)['count']==1:
            return True
        else:
            click((540,1800))
            return False

    def main():
        Comp = False
        while not Comp:
            Comp = Finish.ConfirmOut()
            time.sleep(0.2)



#主函数
if __name__ == '__main__':    
    #全局启用屏幕监控threading及调度器threading
    threadingCap.start()
    threadingDispatch.start()
    TimeOut.threadingChecker.start()
    
    #启动部分
    if stage==0:
        Activate.main()
        stage += 1

    ##养成回合,循环
    while stage<=78:
        time.sleep(0.1)

        #回合间隙
        Gap.main()

        #标定体力条位置
        EnergyLoc = itemTell(Cap, i.Item.EnergyLoc)['1'][1]

        #判断Gap后的步骤
        if Gap.Next=='Home':
            Last = 'Home'
            Home.main()
        elif Gap.Next=='RaceHome':##RaceHome同时履行回合主体与回合操作步骤
            Last = 'RaceHome'
            RaceHome.main()
        elif Gap.Next=='SummerHome':
            Last = 'SummerHome'
            SummerHome.main()
        elif Gap.Next=='Retry':
            Last = 'Gap'
            Dispatch.append('Race.ViewResult')
            while not Race.Complete:
                time.sleep(0.1)
            Race.Complete = False
            continue
        
        #判断Home后的步骤
        if Last=='Home':
            if Home.Next in ('Speed','Stamina','Power','Will','Intell'):
                Train.main(Home.Next)
            elif Home.Next=='Sleep' or Home.Next=='Ill':
                Sleep.main(Home.Next)
            elif Home.Next=='HangOut':
                HangOut.main()
            elif Home.Next=='Race':
                Race.main()
        
        #判断SummerHome
        elif Last=='SummerHome':
            if SummerHome.Next in ('Speed','Stamina','Power','Will','Intell'):
                Train.main(SummerHome.Next)
            elif SummerHome.Next=='Sleep' or Home.Next=='Ill':
                Sleep.main(SummerHome.Next)

        stage += 1
        if not CapON:
            raise TimeoutError('Unknown Errors')
        
        
    Finish.main()
    ##养成结束
    print(time.strftime("%m-%d %H:%M:%S",time.localtime())+"[育成结束,请人工查收]")

    #终止全局线程
    CapON = False
    threadingCap.join()
    threadingDispatch.join()
    TimeOut.threadingChecker.join()
    os.system("adb shell input keyevent 26")