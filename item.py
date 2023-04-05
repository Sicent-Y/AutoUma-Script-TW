import cv2
import numpy as np
import os
data = "source/data/"

def open(path):
    img = cv2.imread(path)
    if '.jpg' in path:
        img_encode = cv2.imencode('.jpg', img)[1]
    elif '.png' in path:
        img_encode = cv2.imencode('.png', img)[1]
    data_encode = np.array(img_encode)
    str_encode = data_encode.tostring()
    image = np.asarray(bytearray(str_encode), dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    image = np.array(image).astype(np.float32)
    return image

class Item():
    #录入数字:i.Item.Num[i]与i.Item.NumS[i]
    Num = [None, None, None, None, None, None, None, None, None, None]
    NumS = [None, None, None, None, None, None, None, None, None, None]
    for i in range(10):
        Num[i] = cv2.imread(data+str(i)+".png")
    for i in range(10):
        NumS[i] = cv2.imread(data+"s"+str(i)+".jpg")

    SpeedLab = [None, None, None, None, None, None]
    StaminaLab = [None, None, None, None, None, None]
    PowerLab = [None, None, None, None, None, None]
    WillLab = [None, None, None, None, None, None]
    IntellLab = [None, None, None, None, None, None]
    for i in range(6):
        if os.path.exists(data+"Speed_Lv"+str(i+1)+".jpg"):
            SpeedLab[i] = cv2.imread(data+"Speed_Lv"+str(i+1)+".jpg")
    for i in range(6):
        if os.path.exists(data+"Stamina_Lv"+str(i+1)+".jpg"):
            StaminaLab[i] = cv2.imread(data+"Stamina_Lv"+str(i+1)+".jpg")
    for i in range(6):
        if os.path.exists(data+"Power_Lv"+str(i+1)+".jpg"):
            PowerLab[i] = cv2.imread(data+"Power_Lv"+str(i+1)+".jpg")
    for i in range(6):
        if os.path.exists(data+"Will_Lv"+str(i+1)+".jpg"):
            WillLab[i] = cv2.imread(data+"Will_Lv"+str(i+1)+".jpg")
    for i in range(6):
        if os.path.exists(data+"Intell_Lv"+str(i+1)+".jpg"):
            IntellLab[i] = cv2.imread(data+"Intell_Lv"+str(i+1)+".jpg")

    ToRace = {}
    for i in range(72):
        if os.path.exists(data+"ToRace_"+str(i)+".png"):
            ToRace[str(i)] = cv2.imread(data+"ToRace_"+str(i)+".png")

    ActivateOK = cv2.imread(data+"FinalActivate_OK.jpg")
    Skip = cv2.imread(data+"Skip_Button.png")
    ActivateSet = cv2.imread(data+"ActivateSet.jpg")
    EnergyLoc = cv2.imread(data+"EnergyLoc.jpg")
    
    DecideButton2 = cv2.imread(data+"Decide_Button2.png")
    BackButton = cv2.imread(data+"Back_Button.jpg")
    ContinueButton = cv2.imread(data+"Continue_Button.jpg")
    ContinueButton2 = cv2.imread(data+"Continue_Button2.png")
    OKButton = cv2.imread(data+"OK_Button.jpg")
    OKButton2 = cv2.imread(data+"OK_Button2.jpg")
    RaceContinueLab = cv2.imread(data+"RaceContinueLab.jpg")
    CancleButton = cv2.imread(data+"Cancle_Button.jpg")
    GoRaceButton = cv2.imread(data+"GoRace_Button.png")
    ViewResultButton = cv2.imread(data+"SkipRace_Button.png")
    RetryButton = cv2.imread(data+"Retry_Button.jpg")

    EventKey1 = cv2.imread(data+"EventKey_1.jpg")
    EventKey2 = cv2.imread(data+"EventKey_2.jpg")
    Game = cv2.imread(data+"Game_Button.jpg")
    Heritage = cv2.imread(data+"Heritage.jpg")
    FansWarning = cv2.imread(data+"FansWarning.jpg")

    SkillLab = cv2.imread(data+"I_SkillLab.png")
    TrainTitle = cv2.imread(data+"TrainStateMax.jpg")
    MainSleep = cv2.imread(data+"I_Main_SleepButton.jpg")
    illButton = cv2.imread(data+"I_Main_illButton.jpg")
    RMSkill = cv2.imread(data+"I_RM_SkillButton.png")
    SMSleep = cv2.imread(data+"I_Main_SHButton.jpg")
    SelectRaceLab = cv2.imread(data+"SelectRace.png")
    CompleteLab = cv2.imread(data+"End_SkillButton.jpg")

    Motivation5 = cv2.imread(data+"State_M_5.jpg")
    Motivation4 = cv2.imread(data+"State_M_4.jpg")
    Motivation3 = cv2.imread(data+"State_M_3.jpg")

    Be4 = cv2.imread(data+"Be4.jpg")
    Be3 = cv2.imread(data+"TP_B3.png")

    SleepWindow = cv2.imread(data+"I_SleepWindow.jpg")
    IllWindow = cv2.imread(data+"I_illWindow.jpg")
    SummerSleepWindow = cv2.imread(data+"I_SM_SHWindow.jpg")
    HangOutWindow = cv2.imread(data+"I_HangoutWindow.jpg")
    HangOutSelect = cv2.imread(data+"I_HangoutSelect.jpg")
    HangOutTMCH = cv2.imread(data+"Hangout_Chairman.jpg")
    RaceCommendWindow = cv2.imread(data+"RaceCommend_Window.jpg")
    RaceWarningWindow = cv2.imread(data+"RaceERROR_Window.jpg")
    AfterSelectRaceWindow = cv2.imread(data+"I_RaceWindow1.png")
    SkillObtainComfirWindow = cv2.imread(data+"I_SkillWindow1.png")

    SkillDict = {}
    SkillDict['圆弧的艺术家'] = cv2.imread(data+"ExBlue.jpg")
    SkillDict['弯道回复'] = cv2.imread(data+"ExBlue_L.jpg")
    SkillDict['弧线的教授'] = cv2.imread(data+"GBKskill.jpg")
    SkillDict['弯道灵巧'] = cv2.imread(data+"GKBskill_L.jpg")
    SkillDict['出闸'] = cv2.imread(data+"GoldenActivate_L.jpg")
    SkillDict['脱出术'] = cv2.imread(data+"GoldenGofor.jpg")
    SkillDict['疾行'] = cv2.imread(data+"GoldenGofor_L.png")
    SkillDict['直线灵巧'] = cv2.imread(data+"GoStra.jpg")
    SkillDict['直线加速'] = cv2.imread(data+"OnStra.jpg")
    SkillDict['领尊'] = cv2.imread(data+"STo1st_L.jpg")
    SkillDict['先锋'] = cv2.imread(data+"ForAhead.jpg")
    

    Waite = cv2.imread(data+"WAITE.png")

class Skill():
    pass