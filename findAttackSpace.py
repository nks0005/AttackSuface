import os

file_paths = []

def search_files(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    # print("[*] 검사중,,,", file_path)
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        if 'static' in line and 'struct' in line and 'file_operation' in line:
                            variable_index = line.index('file_operation')
                            variable_name = ''
                            if(len(line[variable_index:].split()) == 1):
                                variable_name = (lines[i+1].split())[0].replace('*', '').replace('&', '')
                            else:
                                variable_name = line[variable_index:].split()[1].replace('*', '').replace('&', '')

                            
                            if variable_name!='':
                                if has_register_nearby(lines, i, variable_name):
                                    
                                    
                                    ret = has_copyto(lines, i)
                                    if ret[0]:    
                                        
                                        

                                        file_paths.append(file_path)
                                        

                                        # .write의 함수에 copy_to가 있는지 확인
                                        checkInWriteCF = has_copy_from_user(lines, ret[1], 'copy_from_user')
                                        checkInReadCF = has_copy_from_user(lines, ret[2], 'copy_from_user')
                                        checkInOpenCF = has_copy_from_user(lines, ret[4], 'copy_from_user')


                                        checkInWriteCT = has_copy_from_user(lines, ret[1], 'copy_to_user')
                                        checkInReadCT = has_copy_from_user(lines, ret[2], 'copy_to_user')
                                        checkInOpenCT = has_copy_from_user(lines, ret[4], 'copy_to_user')

                                        if checkInWriteCF[0] or checkInReadCF[0] or checkInOpenCF[0] or checkInWriteCT[0] or checkInReadCT[0] or checkInOpenCT[0]:


                                            print("[+] file_oprations : ", variable_name)
                                            print("[+] 파일 경로:", file_path)

                                            print("[+] .write : ", ret[1])
                                            print("[+] .read : ", ret[2])
                                            print("[+] .open : ", ret[4])

                                            if checkInWriteCF[0] == True:
                                                print('\033[95m','write',checkInWriteCF[1],'\033[0m')

                                            if checkInReadCF[0] == True:
                                                print('\033[95m','read',checkInReadCF[1],'\033[0m')


                                            if checkInOpenCF[0] == True:
                                                print('\033[95m','open',checkInOpenCF[1],'\033[0m')

                                            if checkInWriteCT[0] == True:
                                                print('\033[95m','write',checkInWriteCT[1],'\033[0m')

                                            if checkInReadCT[0] == True:
                                                print('\033[95m','read',checkInReadCT[1],'\033[0m')


                                            if checkInOpenCT[0] == True:
                                                print('\033[95m','open',checkInOpenCT[1],'\033[0m')
                                                           
            except IOError:
                print("파일을 읽을 수 없습니다:", file_path)

def is_variable_used(lines, start_index, variable_name):
    find_index = start_index
    for line in lines[start_index + 1:]:
        if variable_name in line:
            return [find_index, True]
        
        find_index += 1
    return [start_index, False]


def check_open(_line, _check):
    line = _line
    check = _check
    if '(' in line:
        check += 1
        check += check_open(line.split('(', 1)[1], check)

    return check

def check_end(_line, _check):
    line = _line
    check = _check
    if ')' in line:
        check += 1
        check += check_end(line.split(')', 1)[1], check)

    return check

def has_register_nearby(lines, start_index, file_operation_name):

    findRegister = 0
    for i in range(0, len(lines)):
        if 'register_chrdev' in lines[i]:
            if 'unregister_chrdev' in lines[i]:
                pass
            else:
                findRegister = i
    
    if findRegister == 0:
        return False

    for i in range(findRegister, findRegister+1):
        start_open = 0
        end_open = 0

        fullMethod = ''
        count = 0
        # ( 와 )를 검사


    for i in range(findRegister, len(lines)):
        if(start_open > 0 and start_open == end_open):
            
            count = i
            break

        start_open = check_open(lines[i], start_open)
        end_open = check_end(lines[i], end_open)
        

    for i in range(findRegister, count):
        fullMethod += lines[i]
    
    if file_operation_name in fullMethod:
        return True
    else:
        return False


def check_find(_line, _check, _find):
    line = _line
    check = _check
    if _find in line:
        check += 1
        check += check_find(line.split(_find, 1)[1], check, _find)

    return check

def has_copyto(lines, index):

    # { .write 여부 확인 }
    start_open = 0
    start_end = 0
    
    for i in range(index, len(lines)):
        if(start_open > 0 and start_open == start_end):
            count = i
            break

        start_open = check_find(lines[i], start_open, '{')
        start_end = check_find(lines[i], start_end, '}')

    msg = ''
    value = ''
    value2 = ''
    value3 = ''
    value4 = ''





    for i in range(index, count):
        msg += lines[i]
        if '.write ' in lines[i]:
            value = lines[i].split('.write', 1)[1].split('=',1)[1].split(',', 1)[0].strip().replace('*', '').replace('&', '')
            if 'NULL' in value:
                value = ''  

        if '.read ' in lines[i]:
            value2 = lines[i].split('.read', 1)[1].split('=',1)[1].split(',', 1)[0].strip().replace('*', '').replace('&', '')
            if 'NULL' in value2:
                value2 = '' 

        target = '.mmap '
        target2 = '.mmap'
        if target in lines[i]:
            value3 = lines[i].split(target2, 1)[1].split('=',1)[1].split(',', 1)[0].strip().replace('*', '').replace('&', '')
            if 'NULL' in value3:
                value3 = '' 

        target = '.open '
        target2 = '.open'
        if target in lines[i]:
            value4 = lines[i].split(target2, 1)[1].split('=',1)[1].split(',', 1)[0].strip().replace('*', '').replace('&', '')
            if 'NULL' in value4:
                value4 = '' 

    return [True, value, value2, value3, value4]

    


def has_copy_from_user(lines, funcName, whatcopy):
    '''
    funcName 선언문 확인 

    { } 확인

    안에 copy_from_user 확인
    '''
    check_attack_space = False
    msg = ''

    # static struct에는 static 함수가 선언되어야한다.
    funcIndex = 0
    for i in range(0, len(lines)):
        if ('static' in lines[i]) and (funcName in lines[i]) and (not (';' in lines[i]) ):
            funcIndex = i
            break

    if funcIndex == 0:
        return [check_attack_space, msg]
    
    
    # { } 확인
    funcStart = funcIndex
    funcEnd = 0

    start_open = 0
    start_end = 0
    for i in range(funcStart, len(lines)):
        if start_open > 0 and start_open == start_end:
            funcEnd = i
            break
        
        start_open = check_find(lines[i], start_open, '{')
        start_end = check_find(lines[i], start_end, '}')
    
    if funcEnd == 0:
        return [check_attack_space, msg]

    # print('[?] funcStart : ', funcStart, ' funcEnd : ', funcEnd)

    # copy_from_user 확인
    check_attack_space = False
    msg = ''
    for i in range(funcStart, funcEnd):
        if whatcopy in lines[i]:
            msg ='[*] find! ', whatcopy , lines[i].strip()
            check_attack_space = True

    return [check_attack_space, msg]

# 검색할 폴더 경로를 지정합니다.
folder_path = './linux-6.4'

# 코드 실행
search_files(folder_path)
