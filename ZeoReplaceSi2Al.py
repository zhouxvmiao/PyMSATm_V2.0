#################################################################################
# PyMSATm -- Python Multipurpose Simulation analysis Tools Package for MuSiC    #
# Simulation Software                                                           #
# Copyright (C) 2017  Xumiao Zhou, Li Yang                                      #
#                                                                               #
# 1026715200@qq.com                                                             #
# liyang@wit.edu.cn                                                             #
#                                                                               #
# Contact Address :                                                             #
# Li Yang                                                                       #
# School of Chemical Engineering and Pharmacy                                   #
# Wuhan Institute of Technology                                                 #
# No.206, Guanggu 1st road                                                      #
# Donghu New & High Technology Development Zone                                 #
# Wuhan, Hubei Province, P.R. China                                             #
# Postcode: 430205                                                              #
#################################################################################

import time
from random import choice
import math

def LoadingCellInfo(material_path):
    """
        Read the unit cell parameters of the material file: trilateral length (list),
        silicon atomic coordinates (dictionary), oxygen atom coordinates (dictionary)
    """
    key1=0
    dict_O_sit,dict_Si_sit={},{}
    cell_size=[]

    with open(material_path, 'r') as a:
        for line in a.readlines():
            if line.strip():  # skip blank
                wordlist = line.strip().split()

                if key1==1 and wordlist[0]=='loop_':
                    break

                if wordlist[0]=='_atom_site_occupancy':
                    key1=1
                elif wordlist[0]=='_cell_length_a':
                    cell_size.append(wordlist[1])
                elif wordlist[0]=='_cell_length_b':
                    cell_size.append(wordlist[1])
                elif wordlist[0]=='_cell_length_c':
                    cell_size.append(wordlist[1])

                elif key1==1:
                    if wordlist[1]=='O':
                        dict_O_sit[wordlist[0]]=wordlist[2:5]
                    if wordlist[1]=='Si':
                        dict_Si_sit[wordlist[0]]=wordlist[2:5]

    return (dict_O_sit,dict_Si_sit,cell_size)

def FindConnectionRelationship(dict_O_sit,dict_Si_sit,cell_size):
    """
        Calculate the connection between silicon and oxygen and return it as a dictionary
    """
    dict_O_connect={}
    dict_Si_connect={}
    length_a = float(cell_size[0])
    length_b = float(cell_size[1])
    length_c = float(cell_size[2])

    for O1 in dict_O_sit.keys(): # Find out the silicon which linked with the oxygen

        Si1_list=[]
        compare={}

        a = float(dict_O_sit.get(O1)[0])
        b = float(dict_O_sit.get(O1)[1])
        c = float(dict_O_sit.get(O1)[2])
        for Si1 in dict_Si_sit.keys():
            x = float(dict_Si_sit.get(Si1)[0])
            y = float(dict_Si_sit.get(Si1)[1])
            z = float(dict_Si_sit.get(Si1)[2])
            ax=abs(a-x)
            by=abs(b-y)
            cz=abs(c-z)
            ax = abs(ax - round(ax))   #Minimum image processing
            by = abs(by - round(by))   #Minimum image processing
            cz = abs(cz - round(cz))   #Minimum image processing
            distance = math.sqrt(ax * length_a) + math.sqrt(by * length_b) + math.sqrt(cz * length_c)
            compare[Si1]=distance

        temp=sorted(compare.items(),key=lambda x:x[1])

        Si1_list.append(temp[0][0])
        Si1_list.append(temp[1][0])
        dict_O_connect[O1]=Si1_list

    for Si2 in dict_Si_sit.keys():  # Find out the oxygen which linked with the silicon

        O2_list=[]
        compare1={}

        a = float(dict_Si_sit.get(Si2)[0])
        b = float(dict_Si_sit.get(Si2)[1])
        c = float(dict_Si_sit.get(Si2)[2])
        for O2 in dict_O_sit.keys():
            x = float(dict_O_sit.get(O2)[0])
            y = float(dict_O_sit.get(O2)[1])
            z = float(dict_O_sit.get(O2)[2])
            ax=abs(a-x)
            by=abs(b-y)
            cz=abs(c-z)
            ax = abs(ax - round(ax))   #Minimum image processing
            by = abs(by - round(by))   #Minimum image processing
            cz = abs(cz - round(cz))   #Minimum image processing
            distance=math.sqrt(ax*length_a)+ math.sqrt(by*length_b) + math.sqrt(cz*length_c)
            compare1[O2]=distance

        temp1 = sorted(compare1.items(), key=lambda x: x[1])

        O2_list.append(temp1[0][0])
        O2_list.append(temp1[1][0])
        O2_list.append(temp1[2][0])
        O2_list.append(temp1[3][0])
        dict_Si_connect[Si2] = O2_list

    #print(dict_O_connect,dict_Si_connect)
    return (dict_O_connect,dict_Si_connect)

def FindReplaceSi(dict_O_connect,dict_Si_connect,Al_num):
#Randomly generate a list of silicon and its associated oxygen and return list or false
    Si_list=list(dict_Si_connect.keys())
    keySi_list=[]
    keyO_list=[]

    while len(keySi_list) != Al_num :

        keySiOSi = []
        keySi = choice(Si_list)
        Si_list.remove(keySi)
        tempO=dict_Si_connect.get(keySi)
        for i in tempO:  #Find out the silicon with oxygen which attached to the replacement silicon
            tempSi=dict_O_connect.get(i)
            keySiOSi.extend(tempSi)
        for j in keySiOSi:  #Remove the silicon with oxygen which attached to the replacement silicon
            if j in Si_list:
                Si_list.remove(j)
        keySi_list.append(keySi)
        if len(Si_list)==0:
            break

    if len(keySi_list)==Al_num:
        for k in keySi_list:
            keyO_list.extend(dict_Si_connect.get(k))
        return keySi_list,keyO_list
    else: return False,False

def OutputResultOfCIF(output_path,material_name,dict_O_sit,dict_Si_sit,cell_size,keySi_list,keyO_list,Al_charge,Si_charge,Si_O_Si_charge,Si_O_Al_charge):

    Si_list=list(dict_Si_sit.keys())
    O_list=list(dict_O_sit.keys())
    num=0

    with open(''.join([output_path,'/',material_name,'.cif']), 'w') as a:
        a.write('''data_%s

_audit_creation_method 'Python'
_audit_creation_date %s
_audit_author_name 'Toad Zhou'

_cell_length_a    %s
_cell_length_b    %s
_cell_length_c    %s
_cell_angle_alpha 90
_cell_angle_beta  90
_cell_angle_gamma 90

_symmetry_cell_setting          triclinic
_symmetry_space_group_name_Hall 'P 1'
_symmetry_space_group_name_H-M  'P 1'
_symmetry_Int_Tables_number     1

_symmetry_equiv_pos_as_xyz 'x,y,z'
  
loop_
_atom_site_label
_atom_site_type_symbol
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
_atom_site_charge\n'''%(material_name,time.strftime('%Y-%m-%d', time.localtime(time.time())),cell_size[0],cell_size[1],cell_size[2]))

        for i in Si_list:
            num+=1
            if i in keySi_list:
                a.write('%-7s  %-7s  %-10.5f  %-10.5f  %-10.5f  %-10.3f  \n'%(''.join(['Al',str(num)]),'Al',float(dict_Si_sit.get(i)[0]),float(dict_Si_sit.get(i)[1]),float(dict_Si_sit.get(i)[2]),Al_charge))
            else:
                a.write('%-7s  %-7s  %-10.5f  %-10.5f  %-10.5f  %-10.3f  \n' % (
            ''.join(['Si', str(num)]),'Si', float(dict_Si_sit.get(i)[0]), float(dict_Si_sit.get(i)[1]),
            float(dict_Si_sit.get(i)[2]), Si_charge))
        for j in O_list:
            num+=1
            if j in keyO_list:
                a.write('%-7s  %-7s  %-10.5f  %-10.5f  %-10.5f  %-10.3f  \n' % (
                ''.join(['O', str(num)]), 'O', float(dict_O_sit.get(j)[0]), float(dict_O_sit.get(j)[1]),
                float(dict_O_sit.get(j)[2]), Si_O_Al_charge))
            else:
                a.write('%-7s  %-7s  %-10.5f  %-10.5f  %-10.5f  %-10.3f  \n' % (
                    ''.join(['O', str(num)]), 'O', float(dict_O_sit.get(j)[0]), float(dict_O_sit.get(j)[1]),
                    float(dict_O_sit.get(j)[2]), Si_O_Si_charge))

def OutputResultOfMol(output_path, material_name, dict_O_sit, dict_Si_sit, cell_size, keySi_list, keyO_list, Al_charge,
                      Si_charge, Si_O_Si_charge, Si_O_Al_charge):
    Si_list = list(dict_Si_sit.keys())
    O_list = list(dict_O_sit.keys())
    num = 0

    with open(''.join([output_path,'/',material_name,'.mol']), 'w') as a:
        a.write('''# Basic Unit Cell Information
# Created by Toad Zhou at %s
Molecule_Name: %s CHARGED

Coord_Info: Listed Cartesian None
%s\n''' % (time.strftime('%Y-%m-%d', time.localtime(time.time())),material_name,len(Si_list)+len(O_list)))

        for i in Si_list:
            num += 1
            if i in keySi_list:
                a.write('%-7d  %-10.5f  %-10.5f  %-10.5f  %-7s  %-10.3f    0    0\n' % (
                num, float(dict_Si_sit.get(i)[0])*float(cell_size[0]), float(dict_Si_sit.get(i)[1])*float(cell_size[1]),
                float(dict_Si_sit.get(i)[2])*float(cell_size[2]),'Al_z', Al_charge))
            else:
                a.write('%-7d  %-10.5f  %-10.5f  %-10.5f  %-7s  %-10.3f    0    0\n' % (
                    num, float(dict_Si_sit.get(i)[0])*float(cell_size[0]), float(dict_Si_sit.get(i)[1])*float(cell_size[1]),
                    float(dict_Si_sit.get(i)[2])*float(cell_size[2]),'Si_z', Si_charge))
        for j in O_list:
            num += 1
            if j in keyO_list:
                a.write('%-7d  %-10.5f  %-10.5f  %-10.5f  %-7s  %-10.3f    0    0\n' % (
                    num, float(dict_O_sit.get(j)[0])*float(cell_size[0]), float(dict_O_sit.get(j)[1])*float(cell_size[1]),
                    float(dict_O_sit.get(j)[2])*float(cell_size[2]), 'O_z',Si_O_Al_charge))
            else:
                a.write('%-7d  %-10.5f  %-10.5f  %-10.5f  %-7s  %-10.3f    0    0\n' % (
                    num,  float(dict_O_sit.get(j)[0])*float(cell_size[0]), float(dict_O_sit.get(j)[1])*float(cell_size[1]),
                    float(dict_O_sit.get(j)[2])*float(cell_size[2]),'O_z', Si_O_Si_charge))
        a.write('''\n\n
Fundcell_Info:  Listed
%-10.4f  %-10.4f  %-10.4f
90.0        90.0        90.0
0.0000      0.00000     0.00000
%-10.4f  %-10.4f  %-10.4f'''%(float(cell_size[0]),float(cell_size[1]),float(cell_size[2]),float(cell_size[0]),float(cell_size[1]),float(cell_size[2])))

def main():

    material_path = 'D:/Jobs/Database/zeolite_95_cif/FAU.cif'
    output_path = 'D:/Jobs/Database/test'
    Si_charge = 2.4
    Al_charge = 1.7
    Si_O_Al_charge = -1.2
    Si_O_Si_charge = -1.2
    output_num=1000

    count=0
    count1=0
    count_Si_num_list={}


    material_name=''.join(material_path.split('/')[-1:]).split('.')[0]
    dict_O_sit,dict_Si_sit,cell_size=LoadingCellInfo(material_path)
    dict_O_connect,dict_Si_connect=FindConnectionRelationship(dict_O_sit,dict_Si_sit,cell_size)

    print('The number of silicon atoms in the material is:%s' % (len(dict_Si_sit)))
    Al_num=int(input('Please enter the number of silicon replaced with aluminum(Please do not replace more than half the total number of silicon atoms):\n'))

    start = time.clock()
    count_Si_list = list(dict_Si_connect.keys())
    for count_Si in count_Si_list:
        count_Si_num_list[count_Si]=0

    while count!=output_num:
        count1+=1
        #print('%sth try to replace'%(count))
        keySi_list,keyO_list=FindReplaceSi(dict_O_connect,dict_Si_connect,Al_num)
        if keySi_list == False:
            #print('False!')
            continue
        else:
            count+=1
            for count_Si in count_Si_list:
                if count_Si in keySi_list:
                    count_Si_num_list[count_Si]=count_Si_num_list.get(count_Si)+1

            #print('The %sth replacement was successful, the list of replaced silicon sequences was:\n'%(count),keySi_list)
            OutputResultOfCIF(output_path,material_name+'_%sAl'%(Al_num)+'_%s'%(count)+'_%s'%(count1),dict_O_sit,dict_Si_sit,cell_size,keySi_list,keyO_list,Al_charge,Si_charge,Si_O_Si_charge,Si_O_Al_charge)
            #OutputResultOfMol(output_path, material_name+'_%sAl'%(Al_num)+'_%s'%(count)+'_%s'%(count1), dict_O_sit, dict_Si_sit, cell_size, keySi_list, keyO_list,Al_charge, Si_charge, Si_O_Si_charge, Si_O_Al_charge)

    temp = sorted(count_Si_num_list.items(), key=lambda x: x[1])

    with open('OutputCount.txt', 'w') as OutputCount:
        for count1_Si in temp:
            OutputCount.write('%s     %s\n'%(count1_Si[0],count_Si_num_list.get(count1_Si[0])))

    end = time.clock()
    print('The calculation time: %ss' % (end - start))

if __name__ == '__main__':
    main()

