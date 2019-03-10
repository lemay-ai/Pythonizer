#!/usr/bin/python
import subprocess
import sys

def in_string(codeline, posn):
    cut_line = codeline[:posn]
    if cut_line.count('"') % 2 == 1:
        return True
    else:
        return False  

def separate_comments(code_lines):
    commented = []
    in_block = False
    
    for line in code_lines:
        if in_block == False and '//' in line:
            split_line = line.split('//')
            if not in_string(line, len(split_line[0])):
                commented.append("## " + '//'.join(split_line[1:]).rstrip())
                if len(split_line[0]) > 0 and not split_line[0].isspace():
                    commented.append(split_line[0].rstrip())
                
        elif in_block == False and '/*' in line:
            split_line = line.split('/*')
            split_line = [split_line[0], '/*'.join(split_line[1:])]
            if not in_string(line, len(split_line[0])):
                if '*/' not in line:
                    if len(split_line[0]) > 0 and not split_line[0].isspace():
                        commented.append(split_line[0].rstrip())
                    commented.append("## "+ split_line[1].rstrip())
                    in_block = True
                else:
                    second_split = split_line[1].split('*/')
                    second_split = [second_split[0], '*/'.join(second_split[1:])]
                    in_block = True
                    if not in_string(line, len(second_split[0])):
                        in_block = False
                        commented.append("## " + second_split[0].rstrip())
                        if len(second_split[1]) > 0 and not second_split[1].isspace():
                            commented.append(second_split[1].rstrip())
                    else:
                        commented.append("## " + split_line[1])
                        if len(split_line[0]) > 0 and not split_line[0].isspace():
                            commented.append(split_line[0].rstrip())
                        in_block = True
            else:
                commented.append(line)
        
        elif in_block == True:
            if "*/" not in line:
                commented.append("## " + line.rstrip())
            else:
                split_line = line.split("*/")
                split_line = [split_line[0], "*/".join(split_line[1:])]
                if not in_string(line, len(split_line[0])):
                    in_block = False
                    commented.append("## "+ split_line[0].rstrip())
                    if len(split_line[1]) > 0 and not split_line[1].isspace():
                        commented.append(split_line[1].rstrip())
                else:
                    commented.append("## " + line.rstrip())
        else:
            commented.append(line.rstrip())
    return commented

def semicolons(commented_lines):
    remove_semicolons = []
    for line in commented_lines:
        if line[:2] == "##":
            line_list = [line, '']
        elif len(line) > 0 and line[-1]== ';':
            line_list = [line[:-1], ';']
        else:
            line_list = [line, '']
        remove_semicolons.append(line_list)
    return remove_semicolons


def open_braces(semicoloned_lines):
    remove_open_braces = []
    for line in semicoloned_lines:
        if len(line[0]) > 0 and line[0][:2] != "##" and line[0][-1] == '{':
            remove_open_braces.append([line[0][:-1], '{' + line[1]])
        else:
            remove_open_braces.append(line)
    return remove_open_braces
               
def close_braces(open_braced_lines):
    remove_close_braces = []
    for i in range(len(open_braced_lines)):
        line = open_braced_lines[i]
        if len(line[0]) > 0         and line[0][:2] != "##"         and line[0][-1] == '}'         and (len(line[0][:-1]) == 0 or line[0][:-1].isspace()):
            if open_braced_lines[i - 1][0][:2] != "##":
                remove_close_braces[-1][1] += '}'
        else:
            remove_close_braces.append(line)
    return(remove_close_braces)

def fix_comments(close_braced_lines):
    fixed_comments = []
    for i in range(len(close_braced_lines)):
        line = close_braced_lines[i]
        if len(line[0]) > 0:
            if i == 0 and line[0][:2] == "##":
                fixed_comments.append(['', '/*'])
                fixed_comments.append(line)
            elif line[0][:2] == "##":
                if fixed_comments[-1][0][:2] != "##":
                    fixed_comments[-1][1] += '/*'
                    fixed_comments.append(line)
                else:
                    fixed_comments.append(line)

                if  i < (len(close_braced_lines) - 1) and close_braced_lines[i+1][0][:2] != "##":
                    fixed_comments[-1][1] += "*/"
                elif i == len(close_braced_lines) - 1:
                    fixed_comments.append(['', "*/"])
            else:
                fixed_comments.append(line)
        else:
            fixed_comments.append(line)
    return fixed_comments

def print_script(split_code):
    maxlen = 0
    for line in split_code:
        if len(line[0]) > maxlen:
            maxlen = len(line[0])
    padding = "{:<" + str(maxlen + 20) + "}"
    for line in split_code:
        spaced = ""
        for char in line[0]:
            if char == " ":
                spaced += "  "
            else:
                break
        print(padding.format(spaced + line[0]) + line[1])


def pythonizer(java_file_name):
    code_lines, stderr = subprocess.Popen(["java", "-jar", "google-java-format-1.7-all-deps.jar", java_file_name],
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.STDOUT).communicate()
    code_lines = code_lines.split("\n")
    print_script(fix_comments(close_braces(open_braces(semicolons(separate_comments(code_lines))))))


pythonizer(str(sys.argv[1]))

