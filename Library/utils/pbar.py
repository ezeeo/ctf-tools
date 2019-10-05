
import os,sys
import threading
from queue import Queue
import time
#进度条v1.3 powered by ezeeo|github:https://github.com/ezeeo/ctf-tools qq:1067530461

#初始化时可自定义部分如下(均具有默认值)
#1.可自定义移动部件(非进度部分)。例如  |####            <=-=>                  |   <=-=>为移动部件,####为进度
#2.可自定义进度部分的填充字符。在上面的例子中为'#'(默认)
#3.可自定义进度条刷新速度(会影响到移动部件和进度的刷新速度)刷新速度越快则处理显示事件速度越快
#4.可自定义提示信息部分的刷新速度。例如|####            <=-=>                  | 这里是提示  。其中，当提示部分不足以完整显示"这里是提示"时候，将会左右移动提示
#5.可自定义进度条的长度(单位为字符,不包含'|')
#6.可自定义提示信息部分的长度(单位为字符)
#7.可自定义可移动部件的移动方式ll(从左到右),rr(从右到左),lr(左右来回弹)(默认)
#8.可自定义是否启用平滑进度模式(即目标进度与当前进度差距大于一格进度的时候,平滑模式会逐格进行增减,不启用则进度会跳变)
#9.可自定义是否启用允许跳帧(注意:所有用户请求的帧都不会跳过,跳帧仅仅适用于平滑模式生成的帧)
#10.可自定义是否启用垂直同步(显示事件处理与显示同步)(要使用平滑模式必须启用垂直同步)
#11.可自定义是否展示百分比的数字show_percent_num

#运行时可更改以下配置
#进度条刷新速度,可移动部件(非进度部分),进度部分的填充字符,可移动部件的移动方式

#进度条的控制
#1.start_bar():启动进度条的事件循环,开始显示
#2.end_bar(waiting,newline=True,show_log=False):结束进度条的刷新,waiting表明是否等待所有事件结束,newline代表结束时是否换行,show_log表示结束时是否显示日志
#3.clear(waiting=False):结束并清除进度条的显示。waiting表明是否等待所有事件结束,不建议事先调用end,除非调用endbar时候参数newline=False
#4.hidden(pause=False):隐藏进度条的显示,pause指示是否暂停内部事件循环
#5.reshow():重新显示进度条

#进度的设置
#set_rate(rate,info=None)
#rate表示进度(0-100),如果超过范围将会强制限制在范围内
#info表示提示信息
#注意:rate和info不应该同时是None

#输出字符串
#print(str):用于在进度条上方输出字符串

#日志
#show_log():输出运行日志,建议不要在进度条未结束时输出

#示例
#最简用法
#from pbar import Pbar
#bar=Pbar()
#bar.start_bar()
#bar.set_rate(60)
#即可看到进度从0走到60


path=os.path.abspath('.')
if 'tools' in path.replace('\\','/').split('/'):#这里是为了便于开发调试
    path=path.split('tools',maxsplit=1)[0]+'Library/utils'
else:
    path=path+'/Library/utils'
if not path in (p.replace('\\','/') for p in sys.path):
    sys.path.append(path)
from thread_safe_access_inject import inject_get_set

class Pbar:
    '''提供进度条功能，可设置宽度，提示信息，帧率填充等等'''
    def __init__(self,speed=15,info_speed=1,bar_len='Auto',info_len='Auto',bar_fill='#',bar_moving='<=-=>',move_mode='lr',show_percent_num=False,smooth=True,allow_skip_frame=True,vsync=True):
        '''smooth即平滑模式，设定一个进度向另一个进度切换时是否平滑，allow_skip_frame标志是否允许跳过平滑帧'''
        self._fps=speed
        self._info_fps=info_speed#info的fps
        self._bar_len=bar_len
        self._info_len=info_len
        self._bar_fill=bar_fill
        self._bar_moving=bar_moving
        self._move_mode=move_mode
        self._show_percent_num=show_percent_num

        self._smooth=smooth
        self._allow_skip_frame=allow_skip_frame
        self._vsync=vsync

        self._terminal_size=os.get_terminal_size()


        self._log=[]

        if not self._check_init_arg():
            self.show_log()
            raise Exception('[!]error:初始化参数非法')

        self._events=Queue()#事件(tuple类型,第一个是'c','r'(rate),'i'(info),'a'(all(info&rate))，对应控制,渲染请求,r的参数可控(进度条值(0-100),info内容))
        self._user_render_events=Queue()#表示用户设定的帧,不可跳过


        self._bar_position=-len(self._bar_moving)
        self._info_position=0
        self._bar_next_direction=0#表示下一帧移动方向(0不动,1向右,-1向左)
        self._info_next_direction=0
        self._init_direction()

        self._now_move_info_interval=0# 当它等于int(self._fps/self._info_fps)时应该移动info#2fps(多少frame移动一次)

        self._bar_template=None#进度条模板
        self._set_show_template()

        self._now_fill_num=0#进度条值(0-100)
        self._now_str_info=''#显示的信息
        self._tmp_frame=''#缓存帧

        self._last_event_time=0#上次处理event用时
        self._last_render_cache_time=0#上次计算(刷新到缓存)用时
        self._last_to_screen_time=0#上次输出到屏幕用时
        self._frame_sleep=1/self._fps#每帧间隔


        self._event_thread=threading.Thread(target=self._event_loop)
        self._is_start=False


        self._hidden=False#是否隐藏进度条的显示(print以及控制操作依然可用)
        self._pause=False#是否暂停事件循环

        fd=inject_get_set(self)#注入线程安全的属性访问方法
        if fd==False:
            raise Exception('inject method fail')


    def start_bar(self):
        if not self._is_start:
            self._event_thread.start()
            self._is_start=True



    def show_log(self):
        for l in self._log:
            print(l)


    def _init_direction(self):
        '''初始化移动方向'''
        if self._move_mode=='rr':
            self._bar_position=self._bar_len+1
            self._bar_next_direction=-1
        else:
            self._bar_next_direction=1


    def _check_init_arg(self):
        if self._fps<=0:
            self._log.append('[!]error:fps不能小于0')
            return False
        if self._fps>60:
            self._log.append('[-]warn :fps不建议大于60')
        if self._bar_len=='Auto' or self._info_len=='Auto':
            if self._cal_auto_len()==False:return False
        elif isinstance(self._bar_len,int) and isinstance(self._info_len,int):
            if self._bar_len>0 and self._info_len>0:
                if self._bar_len+self._info_len<=self._terminal_size.columns:
                    pass
                else:
                    self._log.append('[!]error:终端宽度{}不足{}+{}'.format(self._terminal_size.columns,self._bar_len,self._info_len))
                    return False
            else:
                self._log.append('[!]error:bar_len和info_len必须>0')
                return False
        else:
            self._log.append('[!]error:bar_len和info_len必须是int')
            return False
        if isinstance(self._bar_fill,str) and len(self._bar_fill)==1:
            pass
        else:
            self._log.append('[!]error:bar_fill必须是长度为1的字符串')
            return False
        if not isinstance(self._bar_moving,str):
            self._log.append('[!]error:bar_moving必须是字符串')
            return False
        if self._move_mode not in ('lr','ll','rr'):
            self._log.append('[!]error:move_mode必须在lr(左->右->左),ll(左->右),rr(右->左)中')
            return False
        if not isinstance(self._smooth,bool):
            self._log.append('[!]error:smooth必须是bool')
            return False
        if not isinstance(self._allow_skip_frame,bool):
            self._log.append('[!]error:allow_skip_frame必须是bool')
            return False
        if not isinstance(self._info_fps,int):
            self._log.append('[!]error:info_speed必须是int')
            return False
        else:
            if self._info_fps<=0 or self._info_fps>self._fps:
                self._log.append('[!]error:0<=info_speed<speed')
                return False
        if not isinstance(self._vsync,bool):
            self._log.append('[!]error:vsync必须是bool')
            return False
        else:
            if self._vsync==False and self._smooth==True:
                self._log.append('[!]error:smooth开启依赖于vsync开启')
                return False
        if not isinstance(self._show_percent_num,bool):
            self._log.append('[!]error:show_percent_num必须是bool')
            return False
        return True



    def _cal_auto_len(self):
        '''计算auto时候的长度'''
        if self._bar_len=='Auto' and self._info_len=='Auto':
            if self._terminal_size.columns>=130:
                self._bar_len=100
                self._info_len=20
            elif self._terminal_size.columns>=80:
                self._bar_len=50
                self._info_len=20
            else:
                self._info_len=10
                self._bar_len=self._terminal_size.columns-self._info_len
        else:
            if isinstance(self._bar_len,int):
                self._info_len=self._terminal_size.columns-self._bar_len-5
            elif isinstance(self._info_len,int):
                self._bar_len=self._terminal_size.columns-self._info_len-5
                if self._bar_len>100:self._bar_len=100
            else:
                self._log.append('[!]error:len参数类型错误,必须是int或是Auto')
                return False
        if self._bar_len<=0 or self._info_len<=0:
                self._log.append('[!]error:len参数值错误,必须是>0')
                return False

        


    def _set_show_template(self):
        '''设置进度条模板'''
        a=[' ' for i in range(self._bar_len+self._info_len+3)]
        a[0]='|'
        a[self._bar_len+1]='|'
        self._bar_template=a


    def _set_blank_bar(self):
        for i in range(1,self._bar_len+1):
            self._bar_template[i]=' '


    def _render_bar_position(self,fill_num,moving_start):
        '''渲染进度条部分'''
        self._set_blank_bar()

        for i,c in enumerate(self._bar_moving):
            if moving_start+i+1>self._bar_len:break
            elif moving_start+i+1<1:
                continue
            self._bar_template[moving_start+i+1]=c

        for i in range(1,fill_num+1):
            self._bar_template[i]=self._bar_fill
        



    def _render_info_position(self,info,info_start_index):
        '''渲染info部分'''
        num=0
        for i in range(self._bar_len+3,self._bar_len+3+self._info_len):
            if info_start_index+num>=len(info):
                self._bar_template[i]=' '
            else:
                self._bar_template[i]=info[info_start_index+num]
                num+=1

    def _render_persent_num(self,fill_num):
        i=self._bar_len//2-1
        s=str(fill_num)+'%'
        for ii,ss in enumerate(s):
            self._bar_template[i+ii]=ss


    def _cal_next_frame(self,frame_mode=None,fill_num=None,info=None):
        '''计算下一帧,frame_mode标志是否是生成的帧，能否跳过'''
        self._now_move_info_interval+=1

        if fill_num==None:fill_num=self._now_fill_num
        #elif frame_mode==False:self._now_fill_num=fill_num

        if info==None:info=self._now_str_info
        else:
            self._now_str_info=info
            self._info_position=0

        #计算下一个position
        self._bar_position=self._bar_position+self._bar_next_direction

        if self._move_mode=='ll' and self._bar_position>self._bar_len:
            self._bar_position=fill_num-len(self._bar_moving)

        elif self._move_mode=='rr' and self._bar_position<fill_num-len(self._bar_moving):
                self._bar_position=self._bar_len+1
        
        elif self._move_mode=='lr':
            if self._bar_position+len(self._bar_moving)>self._bar_len:
                self._bar_position-=1
                self._bar_next_direction=-1
            elif self._bar_position<fill_num:
                self._bar_position+=1
                self._bar_next_direction=1

        if self._now_move_info_interval==int(self._fps/self._info_fps):
            self._now_move_info_interval=0
            #控制info的移动
            if len(info)>self._info_len:#不够用时才需要移动
                self._info_position=self._info_position+self._info_next_direction
                if self._info_position+self._info_len>=len(info):#向右移到头了
                    if self._info_next_direction>=0:self._info_next_direction-=1
                elif self._info_position<=0:
                    self._info_position=0
                    if self._info_next_direction<=0:self._info_next_direction+=1



        self._render_bar_position(fill_num,self._bar_position)
        self._render_info_position(info,self._info_position)

        if self._show_percent_num:
            self._render_persent_num(fill_num)

        self._tmp_frame='\r'+''.join(self._bar_template)


    def _render_to_screen(self):
        '''输出到屏幕'''
        print(self._tmp_frame,end='',flush=True)


    def _event_handle(self,e):
        try:
            eval('self._handle_{}(e)'.format(e[1]))
        except Exception as ex:
            self._log.append('[!]error:handle fail,'+str(ex))
        


    def _handle_speed(self,e):
        '''设定speed的handle'''
        self._fps=e[2]
        self._frame_sleep=1/self._fps
    def _handle_fill(self,e):
        self._bar_fill=e[2]
    def _handle_bar_moving(self,e):
        self._bar_moving=e[2]
    def _handle_move_mode(self,e):
        self._move_mode=e[2]
        if self._move_mode=='rr':
            self._bar_next_direction=-1
        else:
            self._bar_next_direction=1




    def _add_smooth_render(self,target_event):
        '''将用户输入扩充平滑'''
        if target_event[0]in 'ra':target_fill=target_event[2]
        elif target_event[0]=='i':
            self._events.put(target_event)
            return

        if target_event[0]=='a':add_info=True


        if target_fill>self._now_fill_num:skip=1
        elif self._now_fill_num>target_fill:skip=-1
        else:#没有rate的更新
            self._events.put(target_event)#不可跳过帧
            return

        for i in range(self._now_fill_num+skip,target_fill,skip):
            if target_event[0]=='a' and add_info:#需要添加info
                self._events.put(('a',True,i,target_event[3]))
                add_info=False
            elif target_event[0]=='a' and not add_info:
                self._events.put(('r',True,i))
            else:
                self._events.put((target_event[0],True,i))

        self._events.put(target_event)#不可跳过帧

        self._now_fill_num=target_fill#将进度条填充更新到用户最新值(即使还未显示)

    def _event_loop_pause(self):
        '''检查并等待暂停请求结束'''
        if self._pause_get()==False:return
        while 1:
            if self._pause_get()==False:return
            time.sleep(0.001)



    def _event_loop(self):
        '''事件循环'''
        try:
            while 1:
                self._event_loop_pause()

                s_time=time.time()
                d=None#当前应处理的请求
                #处理用户渲染请求
                while not self._user_render_events.empty():
                    dd=self._user_render_events.get()

                    if not self._user_render_events.empty() or self._events.qsize()>100:#还有下一个渲染请求或者未处理事件>100，跳帧
                        #允许跳过
                        while not self._events.empty() and self._allow_skip_frame :

                            d=self._events.get()
                            if d[0] in ('a','r','i') and d[1]==True:pass
                            else:break
                        
                    if self._smooth:
                        self._add_smooth_render(dd)#添加平滑
                    else:
                        if dd[0] in ('r','a'):
                            self._now_fill_num=dd[2]
                        self._events.put(dd)
                    if self._vsync:
                        break
                    else:#超时判断
                        if self._frame_sleep-self._last_render_cache_time-self._last_to_screen_time<=time.time()-s_time:break

                #非垂直同步的跳帧
                if not self._vsync:
                    while not self._events.empty() and (d==None or d[0] in ('a','r','i')):
                        d=self._events.get()
                        if d[0] in ('a','r','i'):pass
                        else:break

                
                c_time=time.time()
                self._last_event_time=c_time-s_time
                #处理事件
                if d!=None or not self._events.empty():
                    if d==None:d=self._events.get()
                    
                    if d[0]=='c':#处理控制信号
                        if d[1]=='end':
                            break
                        self._event_handle(d)
                    elif d[0]=='a':
                        self._cal_next_frame(d[1],d[2],d[3])
                    elif d[0]=='r':
                        self._cal_next_frame(d[1],d[2],None)
                    elif d[0]=='i':
                        self._cal_next_frame(d[1],None,d[2])
                    elif d[0]=='p':
                        print('\r'+d[1]+' '*(self._bar_len+self._info_len+3-len(d[1])-1))
                #无事件
                else:
                    self._cal_next_frame()

                e_time=time.time()
                self._last_render_cache_time=e_time-c_time
                #计算应睡眠事件
                sleep_time=self._frame_sleep-self._last_render_cache_time-self._last_to_screen_time-self._last_event_time
                if sleep_time>0:
                    time.sleep(sleep_time)
                if not self._hidden_get():#没有hidden就渲染到屏幕
                    self._render_to_screen()
                t_time=time.time()
                self._last_to_screen_time=t_time-e_time
        except Exception as ex:
            print('event loop exception ',ex)
            self.show_log()


    def set_rate(self,rate,info=None):
        '''设置进度'''
        if rate!=None and not isinstance(rate,int):
            self._log.append('[-]warn :设置的rate类型错误')
            return False
        
        if info!=None and not isinstance(info,str):
            self._log.append('[-]warn :设置的info类型错误')
            return False

        if rate!=None:
            if rate<0:
                self._log.append('[+]info :进度<0')
                rate=0
            elif rate>100:
                self._log.append('[+]info :进度>100')
                rate=100

        if rate==None and info==None:
            self._log.append('[-]warn :设置的rate和info不能同时为空')
            return False
        elif rate!=None and info!=None:
            self._user_render_events.put(('a',False,int(rate/100*self._bar_len),info))
        elif rate!=None:
            self._user_render_events.put(('r',False,int(rate/100*self._bar_len)))
        else:
            self._user_render_events.put(('i',False,info))

    def end_bar(self,waiting,newline=True,show_log=False):
        '''结束进度条show_log必定newline'''
        if waiting:
            while not self._user_render_events.empty():time.sleep(0.1)

        self._events.put(('c','end'))
        while self._event_thread.isAlive():
            time.sleep(0.01)
        if show_log:
            print()
            self.show_log()
        elif newline:
            print()
        
        self._is_start=False


    def set_speed(self,speed):
        '''设置进度条速度'''
        if not isinstance(speed,int):
            self._log.append('[-]warn :speed必须是int')
            return False
        if speed<=0:
            self._log.append('[-]warn :speed必须>0')
            return False
        self._events.put(('c','speed',speed))


    def set_fill(self,fill):
        '''设置进度条已完成部分填充'''
        if not isinstance(fill,str):
            self._log.append('[-]warn :fill必须是str')
            return False
        if len(fill)!=1:
            self._log.append('[-]warn :fill长度必须是1')
            return False
        self._events.put(('c','fill',fill))

    def set_bar_moving(self,bar_moving):
        '''设置运动部分样式'''
        if not isinstance(bar_moving,str):
            self._log.append('[-]warn :bar_moving必须是str')
            return False
        if len(bar_moving)>=self._bar_len:
            self._log.append('[-]warn :bar_moving长度过长')
            return False
        self._events.put(('c','bar_moving',bar_moving))

    def set_move_mode(self,move_mode):
        if move_mode not in ('lr','ll','rr'):
            self._log.append('[!]error:move_mode必须在lr(左->右->左),ll(左->右),rr(右->左)中')
            return False
        if move_mode==self._move_mode:pass
        else:
            self._events.put(('c','move_mode',move_mode))


    def print(self,s):
        if not isinstance(s,str):
            self._log.append('[!]warn :s必须是str')
            return False
        self._events.put(('p',s))

    def clear(self,waiting=False):
        '''结束并清除进度条。注意不建议事先调用end,除非调用endbar时候参数newline=False'''
        if self._event_thread.isAlive():
            self.end_bar(waiting,False)
        print('\r'+' '*(self._bar_len+self._info_len+3),end='')
        print('\r',end='')

    def hidden(self,pause=False):
        '''隐藏进度条,可选是否需要暂停事件循环'''
        if not isinstance(pause,bool):
            raise Exception('pause必须是bool')
        self._hidden_set(True)
        if pause:
            self._pause_set(True)
        time.sleep(0)
        print('\r'+' '*(self._bar_len+self._info_len+3),end='')
        print('\r',end='')

    def reshow(self,new_line=False):
        '''重新显示进度条'''
        if not isinstance(new_line,bool):
            raise Exception('new_line必须是bool')
        if new_line:
            print()
        else:
            print('\r'+' '*(self._bar_len+self._info_len+3),end='')
            print('\r',end='')
        self._hidden_set(False)
        self._pause_set(False)


if __name__ == "__main__":


    bar=Pbar(speed=15,bar_len=100,info_len=30,bar_fill='#',bar_moving='<=-=>',move_mode='lr',show_percent_num=True,smooth=True,allow_skip_frame=False,vsync=True)
    bar.start_bar()
    fills='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    bar.set_rate(0,fills)
    # while 1:
    #     for i in range(101):
    #         bar.set_rate(i)
    #         time.sleep(0.0005)
    #     time.sleep(0.05)

    # import random,string
    # r=random.randint(0,100)
    # while 1:
    #     time.sleep(2)
    #     bar.set_rate(100)
    #     time.sleep(2)
    #     bar.set_rate(0)
    


    bar.set_rate(10,'1231235skjdfbksdgkuasgfkjasgfk')
    bar.print('1231231312')
    time.sleep(1)
    bar.set_rate(20,'234agsvkjgavskjgas')
    #time.sleep(1)
    bar.set_rate(60,'234askjbcaskjva')
    #time.sleep(5)
    #bar.print('endbar...')
    bar.set_rate(100,'1234567890abcdefghijklmnopqrstuvwxyz')
    bar.set_rate(100,fills)
    bar.hidden()
    bar.set_rate(0)
    input('press any key to reshow')
    bar.reshow()
    #bar.set_rate(0)
    #bar.end_bar(True,False)
    #bar.clear()
    # bar.end_bar(True,show_log=True)
    #bar.clear(True)
    #print('end')

    #while 1:
        # rate+=1
        # if rate>100:rate=0
        # bar.set_rate(rate,'testing...')

        # bar.set_speed((100-rate)//3+10)
        # time.sleep(0.1)

        # if rate==r:
        #     bar.set_move_mode(random.choice(('lr','ll','rr')))
        #     bar.set_fill(random.choice(fills))
        #     bar.set_bar_moving(random.choice(('>>>','<>','<<>>','233','>->->','--=>','<=-=>')))
            
        #     r=random.randint(0,100)
        # bar.set_rate(10,'testing...')
        # #time.sleep(5)
        # bar.set_rate(20,None)
        # #time.sleep(4)
        # bar.set_rate(30,None)
        # #time.sleep(3)
        # bar.set_rate(40,None)
        # #time.sleep(3)
        # bar.set_rate(50,None)
        # #time.sleep(1)
        # bar.set_rate(60,None)
        # #time.sleep(1)
        # bar.set_rate(70,None)
        # #time.sleep(2)
        # bar.set_rate(80,None)
        # #time.sleep(3)
        # bar.set_rate(90,None)
        # #time.sleep(4)
        # bar.set_rate(100,None)
        # time.sleep(500)
