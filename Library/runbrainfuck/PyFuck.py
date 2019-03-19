#coding=utf-8
#BrainFuck_Interpreter.py
#Created by Maiko.Our
#This code is distributed under the GPLv3 License
#The code should be self explanatory
#As long as you know how BrainFuck works
#EOF is No-Change

from sys import stdout

class PyFuck(object):
    def __init__(self, asize = 1000, program = "", input_text = ""):
        self.asize = asize
        self.array = [0] * self.asize#This prepares the memory array
        self.ptr = 0
        self.commands = {">": self.inc_ptr, "<": self.dec_ptr, "+": self.inc_cell, "-": self.dec_cell, ".": self.print_chr, ",": self.get_chr, "[": self.add_loop_location, "]": self.jump_back}#This is a sort of a switch statement
        self.input_text = input_text
        self.input_pos = 0
        self.program = self.prepare_program(program)#This prepares the input and return a valid program
        self.program_ptr = 0#This points to the command to be executed
        self.loop_locations = []#This list holds pairs of brackets
    
    def inc_ptr(self):
        if self.ptr is self.asize - 1:
            self.ptr = 0
        else:
            self.ptr += 1      
        return 1          
    
    def dec_ptr(self):
        if self.ptr is 0:
            self.ptr = self.asize - 1
        else:
            self.ptr -= 1
        return 1
    
    def inc_cell(self):
        if self.array[self.ptr] is 255:
            print("[*] 8-bit Cell Overflow ! Program Quiting !")
            return 0
        else:
            self.array[self.ptr] += 1
            return 1
           
    def dec_cell(self):
        if self.array[self.ptr] is 0:
            print("[*] 8-bit Cell May Not Take Negative Values ! Program Quiting !")
            return 0
        else:
            self.array[self.ptr] -= 1
            return 1
    
    def print_chr(self):
        stdout.write(chr(self.array[self.ptr]))
        return 1
        
    def get_chr(self):
        if self.input_pos < len(self.input_text):
            self.array[self.ptr] = ord(self.input_text[self.input_pos])
            self.input_pos += 1
        return 1
    
    def add_loop_location(self):
        opb = 0
        clb = 0
        closingbrackloc = 0
        for i in range(self.program_ptr, len(self.program)):
            if self.program[i] == "[": opb += 1
            elif self.program[i] == "]": clb += 1
            if opb is clb:
                closingbrackloc = i
                break
        if self.array[self.ptr]:
            if not self.loop_locations.__contains__([self.program_ptr, closingbrackloc]):
                self.loop_locations.append([self.program_ptr, closingbrackloc])
        else:
            self.program_ptr = closingbrackloc
        return 1
    
    def jump_back(self):
        for i in range(len(self.loop_locations)):
            if self.loop_locations[i][1] is self.program_ptr:
                self.program_ptr = self.loop_locations[i][0] - 1
        return 1

    def execute(self):
        while self.program_ptr < len(self.program):
            if not self.commands[self.program[self.program_ptr]]():
                break
            else:
                self.program_ptr += 1
                
    def prepare_program(self, program):
        result = ""
        opb = 0
        clb = 0
        for c in program:
            if c in "<>+-,.[]":
                result += c
                if result == "[":opb += 1
                elif result == "]":clb +=1
        if opb != clb:
            if opb > clb:print ("[*] Missing Closing Bracket ! Program Quiting !")
            if opb < clb:print ("[*] Missing Opening Bracket ! Program Quiting !")
            return ""
        else:
            return result
