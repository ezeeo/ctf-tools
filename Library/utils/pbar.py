
import os
import threading
from queue import Queue
import time
#进度条

class Pbar:
    def __init__(self,speed=10,bar_len='Auto',info_len='Auto',bar_fill='#',bar_moving='<=-=>',move_mode='lr'):
        self._fps=speed
        self._bar_len=bar_len
        self._info_len=info_len
        self._bar_fill=bar_fill
        self._bar_moving=bar_moving
        self._move_mode=move_mode

        self._terminal_size=os.get_terminal_size()


        self._log=[]

        if not self._check_init_arg():
            self.show_log()
            raise Exception('[!]error:初始化参数非法')

        self._events=Queue()#事件(tuple类型,第一个是'c','r'(rate),'i'(info),'a'(all(info&rate))，对应控制,渲染请求,r的参数可控(进度条值(0-100),info内容))

        self._bar_position=-len(self._bar_moving)
        self._info_position=0
        self._bar_next_direction=0#表示下一帧移动方向(0不动,1向右,-1向左)
        self._info_next_direction=0
        self._init_direction()

        self._set_show_template()

        self._now_fill_num=10#进度条值
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



    def _cal_next_frame(self,fill_num=None,info=None):
        '''计算下一帧'''

        if fill_num==None:fill_num=self._now_fill_num
        else:self._now_fill_num=fill_num

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


    def _event_loop(self):
        '''事件循环'''
        try:
            while 1:
                s_time=time.time()
                if not self._events.empty():
                    d=self._events.get()

                    #处理控制信号(暂不写)
                    if d[0]=='c':
                        if d[1]=='end':
                            break
                        self._event_handle(d)

                    #处理渲染请求
                    elif d[0]=='a':
                        self._cal_next_frame(d[1],d[2])
                    elif d[0]=='r':
                        self._cal_next_frame(d[1])
                    elif d[0]=='i':
                        self._cal_next_frame(None,d[1])

                else:
                    self._cal_next_frame()

                e_time=time.time()
                self._last_render_cache_time=e_time-s_time

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
            self._events.put(('a',int(rate/100*self._bar_len),info))
        elif rate!=None:
            self._events.put(('r',int(rate/100*self._bar_len)))
        else:
            self._events.put(('i',info))

    def end_bar(self):
        '''结束进度条'''
        self._events.put(('c','end'))
        while self._event_thread.isAlive():
            time.sleep(0.01)
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


if __name__ == "__main__":
    bar=Pbar(speed=30,bar_fill='>',bar_moving='<=-=>',move_mode='lr')
    bar.start_bar()

    rate=0

    import random,string
    r=random.randint(0,100)

    fills='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

    while 1:
        rate+=1
        if rate>100:rate=0
        bar.set_rate(rate,'testing...')

        bar.set_speed((100-rate)//3+10)
        time.sleep(0.1)

        # if rate==r:
        #     bar.set_move_mode(random.choice(('lr','ll','rr')))
        #     bar.set_fill(random.choice(fills))
        #     bar.set_bar_moving(random.choice(('>>>','<>','<<>>','233','>->->','--=>','<=-=>')))
            
        #     r=random.randint(0,100)