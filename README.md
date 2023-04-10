# AutoUma-Script-TW

赛马娘凹种马根本不是人干的事，由于没有找到免费的、手机版、繁中服的自动化脚本，遂自己动手编写了一个超级简陋的。

# 功能

- 该脚本**单次运行**只能进行一次**单轮育成**。
- 进入育成后，脚本将自动读取训练、状态，自动选择训练、休息、外出或前往比赛，循环执行78个回合完成一轮育成
- 脚本使用**adb**进行操作，需要用电脑连接手机，控制手机自动游玩赛马娘游戏；adb连接的该设备**不应**被操作、打断(包括弹出通知、切换屏幕),**否则将会卡死** *详细内容见后*
- 代码识别范围狭窄，**不能够**自动选择剧本、培育马娘、种马与支援卡。请手动操作，将页面导航至**开始育成前的最后一步**再运行代码(也就是确认支援卡后，弹出的确认开始育成弹窗，确保体力足够进行一次育成；此时再运行代码，**否则将会卡死** *详细内容见后*)
- 代码运行将在育成完成获取技能的界面处**结束**，之后需要手动查收；代码执行完成后会自动让手机熄屏
- 具体使用方法，会在后面的使用方法里介绍

# 原理

- 通过adb连接手机，截取手机屏幕进行判断，随后模拟点击
- 通过`opencv`库的`matchtemplate`函数进行模板匹配，通过访问`source\data\`文件夹内存储的模板图像，匹配手机截屏，以此判断页面、训练信息、按钮位置等
  - 注意：模板匹配对分辨率敏感，该脚本在1080x2400分辨率下开发，请确保你的设备分辨率一致，否则将会卡死 *详细内容见后*
- 每一回合会根据获取的信息，按照一定的算法，计算各项操作的权重，最后选取权重最高者执行(休息、外出、保健室、五种训练、比赛)
  
# 配置环境

开始环境配置前，请确保如下条件
> 安装Python>=3.8
> 
> 安装Git
> 
> 闲置的、支持adb的Android手机
>
> Android端繁中服赛马娘
> 
> 正确的网络连接

### 安装脚本运行环境

#### 克隆GitHub仓库

在你的目录下打开cmd，输入如下内容克隆仓库 *注:是在指定目录下打开cmd，操作方法请自己搜索*
```
git clone https://github.com/Sicent-Y/AutoUma-Script-TW
```

运行完成后，会在你的目录下创建一个AutoUma-Script-TW文件夹，该文件夹即项目文件夹

#### 创建python虚拟环境

进入AutoUma-Script-TW文件夹，在该目录下重新打开cmd；或者你也可以不关闭刚才打开的cmd窗口，输入`cd AutoUma-Script-TW`进入AutoUma-Script-TW目录

输入如下代码创建虚拟环境
```
python -m venv AutoUma
```

进入虚拟环境
```
.\AutoUma\Scripts\activate.bat
```

安装依赖
```
pip install -r requiremnets.txt
```

这可能需要一些时间，你可以使用国内镜像源，这样会快一些`pip install -r requiremnets.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

### 配置adb

#### 安装adb

*该仓库自带有adb工具包，无需额外手动下载。当然你也可以根据网络教程手动安装adb并设置系统变量*

你可以在AutoUma-Script-TW文件夹根目录下找到platform-tools文件夹，这就是adb工具；接下来需要将其添加到系统变量，从而使得我们能够使用adb
- 右键点击win菜单键(屏幕左下角的那个)
- 选择`系统`
- 点击`高级系统设置`
- 点击`环境变量`
- 在`系统变量`框中找到`Path`，选择到`Path`点击下方的`编辑`
- 点击`新建`
- 输入platform-tools文件夹的路径，如`D:\Github\AutoUma-Scripts-TW\platform-tools`

#### 连接你的设备

使用数据线连接你的手机与电脑，确保你的数据线与接口能够传输数据；过于低级的数据线可能只能充电而无法起到连接手机电脑的作用；另外，为了防止意料外的问题，请将手机自动熄屏时间调至10分钟或者永不熄屏

#### 手机adb设置

找到你的手机，打开开发者选项

进入`设置->开发者选项`，找到`USB调试`或`ADB设置`，该部分不同手机并不完全相同，请自行完成操作，允许你的电脑使用adb操作你的手机；或者自行搜索网络教程

  - 注:由于未知bug，脚本**不支持**无线adb连接，请不要尝试使用无线adb连接
 
在项目文件夹下打开cmd，可以通过`adb devices`确认是否连接成功

#### 设置分辨率
该脚本只能在指定的分辨率下运行，需要将分辨率设置为1080x2400，density为420，在项目文件夹下打开cmd
```
adb shell wm size 1080x2400
adb shell wm density 420
```

设置完成后，你的手机屏幕可能会变得有点抽象，不必担心，你可以在脚本使用完成后，通过如下命令重置屏幕
```
adb shell wm size reset
adb shell wm density reset
```

同样，你可能会出现屏幕无法点击的问题，如下命令可能可以帮助你
```
adb shell input tap X Y   点击屏幕(X,Y)像素处 
adb shell input swipe X1 Y1 X2 Y2 T   在T秒内滑动屏幕,从(X1,Y1)到(X2,Y2)
adb shell input keyevent 82   唤起菜单/切后台
```

# 使用方法
在AutoUma-Script-TW文件夹根目录下打开cmd，进入你创建的虚拟环境
```
.\AutoUma\Scripts\activate.bat
```

确认adb连接正常、且手机界面位于指定位置后，输入以下命令，即可执行脚本
```
python main.py
```
### 脚本适用范围与指定页面
请在输入上述命令开始执行脚本前，确保你的手机已经打开了赛马娘，并使你的屏幕处在如下界面

![ActivatePos](https://i.postimg.cc/76gBrcLC/Activate-Pos.jpg)

脚本运行后，会自动点击“开始培育！”，随后进入育成页面。

接下来脚本将会持续运行，直到育成结束，抵达如下界面，抵达此界面后脚本将自动关闭，运行结束，并使手机熄屏

![CompletePos]()

**注：**启动脚本时，请确保你的体力充足，防止出现如下界面；如果你希望使用双倍体力，请自己勾上双倍选项后再启动脚本，并确保体力足够

![NOTActivatePos](https://i.postimg.cc/NFdkgwv0/NOTActivate-Pos.jpg)

**注：**脚本目前仅支持URA剧本的育成，并且单次执行只能进行一次育成，不能够连续多次执行(因为需要人工选择种马与支援卡)；脚本将会停在结束确认的界面，请手动前往获取技能
