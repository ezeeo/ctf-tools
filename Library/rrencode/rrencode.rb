#!/usr/bin/env ruby
#
# rrencode "Fun with Symbols"
#
# Copyright(C) 2005 YOSHIDA, Yuichi. All rights reserved.
#

# generate variable name
def make_variable_name
  variable_name = ""
  case rand(3)
  when 0
    variable_name += "@"
  when 1
    variable_name += "@@"
  when 2
  end
  variable_name += "_"
  return variable_name
end

# generate global variable name
def make_global_variable_name
  case rand(18)
  when 0
    return "$_"
  when 1
    return "$&"
  when 2
    return "$~"
  when 3
    return "$'"
  when 4
    return "$`"
  when 5
    return "$+"
  when 6
    return "$?"
  when 7
    return "$!"
  when 8
    return "$@"
  when 9
    return "$/"
  when 10
    return "$\\"
  when 11
    return "$;"
  when 12
    return "$."
  when 13
    return "$<"
  when 14
    return "$>"
  when 15
    return "$*"
  when 16
    return "$$"
  when 17
    return "$\""
  end
end

# generate nonsense statement
def make_nonsense_statement
  v = make_variable_name
  g = make_global_variable_name
  return decorate(v + "=" + g)
end

# generate something
def make_something
  return make_nil
end

# generate nil
def make_nil
  return "$,"
end

# generate false
def make_false
  return make_nil+"&"+make_something
end

# genrate what is true if it's evaluated
def make_something_true
  return "$$"
end

# generate true (instance of TrueClass)
def make_true
  case rand(2)
  when 0
    return make_nil+"|"+make_something_true
  when 1
    return make_nil+"^"+make_something_true
  end
end

# decorate with nonsense expression
def decorate(program)
  case rand(2)
  when 0
    return "(" + make_false + "||" + program + ")"
  when 1
    return "(" + make_true + "&&" + program + ")"
  end
end


def make_3
  return "("+make_less_than_15(1)+"+"+make_less_than_15(2)+")"
end

def make_4
  s = 33 + rand(11)
  e = s + 4
  return "?#{e.chr}-?#{s.chr}"
end

def make_8
  s = 33 + rand(7)
  e = s + 8
  return "?#{e.chr}-?#{s.chr}"
end

def make_less_than_15(num)
  s = 33 + rand(15-num)
  e = s + num
  return "?#{e.chr}-?#{s.chr}"
end

def make_16
  s = 42 + rand(6)
  e = s + 16
  return "?#{e.chr}-?#{s.chr}"
end

def make_32
  s = 0
  e = 0
  case rand(2)
  when 0
    s = 59 + rand(5)
    e = s + 32
  when 1
    s = 91 + rand(4)
    e = s + 32
  end
  s = s.chr
  e = e.chr
  s *= 2 if s == "\\"  
  e *= 2 if e == "\\"  
  return "?#{e}-?#{s}"
end

def make_64
  s = 59 + rand(4)
  e = s + 64
  return "?#{e.chr}-?#{s.chr}"
end

def make_num(num)
  if num >= 64
    return "(" + make_64 + "+" + make_num(num - 64) + ")"
  elsif num >= 32
    return "(" + make_32 + "+" + make_num(num - 32) + ")"
  elsif num >= 16
    return "(" + make_16 + "+" + make_num(num - 16) + ")"
  elsif num == 15
    return "(" + make_8 + "+" + make_num(num - 8) + ")"
  else
    return make_less_than_15(num)
  end
end

# generate 99
def make_ascii_c
  case rand(2)
  when 0
    return "?!+?!+?!"
  when 1
    return "?!*"+make_3
  end
end

# generate "%c"
def make_mod_c
  return "("+"%!\%!<<("+make_ascii_c+")"+")"
end

# generate char
def make_char(char)
  return decorate(make_mod_c+"%"+make_num(char))
end

# generate str
def make_str(str)
  program = []
  str.each_byte do |char|
    program << make_char(char)
  end
  return program.join("+")
end

# print "\n"
def make_print_lf
  return "$><<$/"
end


# print str
def make_print_str(str)
  return "$><<" + make_str(str)
end

input = ARGV[0]
input = "" unless input
input_array = []
while input and input.size > 0
  length = rand(3)+1
  input_array << input[0...length]
  input = input[length..-1]
end

output_array = []
input_array.each do |segment|
  output_array << make_nonsense_statement
  output_array << make_print_str(segment)
end
output_array << make_nonsense_statement
output_array << make_print_lf

output = output_array.join(";")
puts "#!/usr/bin/env ruby"
puts ""
puts output