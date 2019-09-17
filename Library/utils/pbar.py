
import os
import threading
from queue import Queue
import time
#进度条

class Pbar:
    '''提供进度条功能，可设置宽度，提示信息，帧率填充等等'''
    def __init__(self,speed=10,bar_len='Auto',info_len='Auto',bar_fill='#',bar_moving='<=-=>',move_mode='lr',smooth=True,allow_skip_frame=True):
        '''smooth即平滑模式，设定一个进度向另一个进度切换时是否平滑，allow_skip_frame标志是否允许跳过平滑帧'''
        self._fps=speed
        self._bar_len=bar_len
        self._info_len=info_len
        self._bar_fill=bar_fill
        self._bar_moving=bar_moving
        self._move_mode=move_mode

        self._smooth=smooth
        self._allow_skip_frame=allow_skip_frame

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

        self._set_show_template()

        self._now_fill_num=0#进度条值
        self._now_str_info=''#显示的信息
        self._tmp_frame=''#缓存帧

        self._last_render_cache_time=0#上次计算用时
        self._last_to_screen_time=0#上次输出到屏幕用时
        self._frame_sleep=1/self._fps#每帧间隔


        self._event_thread=threading.Thread(target=self._event_loop)
        self._is_start=False

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
                self._info_len=self._terminal_size.columns-self._bar_len
            elif isinstance(self._info_len,int):
                self._bar_len=self._terminal_size.columns-self._info_len
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



    def _cal_next_frame(self,frame_mode=None,fill_num=None,info=None):
        '''计算下一帧'''

        if fill_num==None:fill_num=self._now_fill_num
        elif frame_mode==False:self._now_fill_num=fill_num

        if info==None:info=self._now_str_info
        else:self._now_str_info=info

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



        self._info_position=self._info_position+self._info_next_direction




        self._render_bar_position(fill_num,self._bar_position)
        self._render_info_position(info,self._info_position)

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
        if target_event[0]in 'ra':target_rate=target_event[2]
        elif target_event[0]=='i':
            self._events.put(target_event)
            return

        if target_event[0]=='a':add_info=False


        now_rate=int(self._now_fill_num/self._bar_len*100)
        if target_rate>now_rate:skip=1
        elif now_rate>target_rate:skip=-1
        else:#没有rate的更新
            self._events.put(target_event)#不可跳过帧
            return
        last_fill_num=self._now_fill_num#上次的值
        for i in range(now_rate+skip,target_rate,skip):
            if int(i/100*self._bar_len)==last_fill_num:
                continue
                #pass
            else:
                if target_event[0]=='a' and not add_info:
                    self._events.put(('a',True,int(i/100*self._bar_len),target_event[3]))
                    add_info=True
                elif target_event[0]=='a' and add_info:
                    self._events.put(('r',True,int(i/100*self._bar_len)))
                else:
                    self._events.put((target_event[0],True,int(i/100*self._bar_len)))
                last_fill_num=int(i/100*self._bar_len)
        self._events.put(target_event)#不可跳过帧

        self._now_fill_num=int(target_event[2]/100*self._bar_len)#将进度条填充更新到用户最新值(即使还未显示)



    def _event_loop(self):
        '''事件循环'''
        try:
            while 1:
                s_time=time.time()
                d=None#当前应处理的请求
                #处理用户渲染请求
                if not self._user_render_events.empty():
                    dd=self._user_render_events.get()

                    if not self._user_render_events.empty():#还有下一个渲染请求，跳帧
                        #允许跳过
                        while not self._events.empty() and self._allow_skip_frame:

                            d=self._events.get()
                            if d[0] in ('a','r','i') and d[1]==True:pass
                            else:break
                        
                    if self._smooth:
                        self._add_smooth_render(dd)#添加平滑
                    else:self._events.put(dd)


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
                        print('\r'+d[1]+' '*(self._bar_len+self._info_len+3-len(d[1])))
                #无事件
                else:
                    self._cal_next_frame()

                e_time=time.time()
                self._last_render_cache_time=e_time-s_time
                #计算应睡眠事件
                sleep_time=self._frame_sleep-self._last_render_cache_time-self._last_to_screen_time
                if sleep_time>0:
                    time.sleep(sleep_time)

                self._render_to_screen()
                t_time=time.time()
                self._last_to_screen_time=t_time-e_time
        except Exception as ex:
            print('event loop exception ',ex)
            self.show_log()


    def set_rate(self,rate,info):
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

    def end_bar(self,waiting,newline=True):
        '''结束进度条'''
        if waiting:
            while not self._user_render_events.empty():time.sleep(0.1)

        self._events.put(('c','end'))
        while self._event_thread.isAlive():
            time.sleep(0.01)
        if newline:
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
        if self._move_mode not in ('lr','ll','rr'):
            self._log.append('[!]error:move_mode必须在lr(左->右->左),ll(左->右),rr(右->左)中')
            return False
        self._events.put(('c','move_mode',move_mode))


    def print(self,s):
        if not isinstance(s,str):
            self._log.append('[!]warn :s必须是str')
            return False
        self._events.put(('p',s))

    def clear(self,waiting=False):
        '''注意不建议事先调用end,除非调用endbar时候参数newline=False'''
        if self._event_thread.isAlive():
            self.end_bar(waiting,False)
        print('\r'+' '*(self._bar_len+self._info_len+3),end='')
        print('\r',end='')


if __name__ == "__main__":
    bar=Pbar(speed=30,bar_fill='#',bar_moving='<=-=>',move_mode='lr',smooth=True,allow_skip_frame=False)
    bar.start_bar()

    rate=0

    import random,string
    r=random.randint(0,100)

    fills='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'


    bar.set_rate(100,'123')
    bar.print('1231231312')
    bar.set_rate(0,'234')
    #bar.end_bar(True)
    bar.clear(True)
    print('end')

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
