##########################################################################
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
##########################################################################

import struct

with open(r'D:\Jobs\zxm\report\snurr_mofs_separation\New\AdsorptionMap\H2S\UIO-66\H2S_uio_66.poremap.dmap', 'r') as file:
    file_list = file.readlines()
    rank = int(file_list[0].split()[0])
    type = int(file_list[0].split()[1])
    grid_z = int(file_list[1].split()[0])
    grid_y = int(file_list[1].split()[1])
    grid_x = int(file_list[1].split()[2])
    min_z = float(file_list[2].split()[0])
    max_z = float(file_list[2].split()[1])
    min_y = float(file_list[2].split()[2])
    max_y = float(file_list[2].split()[3])
    min_x = float(file_list[2].split()[4])
    max_x = float(file_list[2].split()[5])
    bytes_two = struct.pack('f', float(file_list[3]))
    bytes_one = struct.pack(
        'iiiiiffffff',
        rank,
        int(3),
        grid_z,
        grid_x,
        grid_y,
        min_z,
        max_z,
        min_y,
        max_y,
        min_x,
        max_x)
    for site in file_list[4:]:
        bytes = struct.pack('f', float(site))
        bytes_two += bytes

with open(r'D:\Jobs\zxm\report\snurr_mofs_separation\New\AdsorptionMap\H2S\UIO-66\H2S_uio_66.plt1', 'wb') as file_out:
    file_out.write(bytes_one)
    file_out.write(bytes_two)
