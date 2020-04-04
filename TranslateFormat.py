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

# This code used to calculate charge (EQeq) and translate format (auto-make P1)
# Please do not modify or delete comments and key words

import os
import time
import sys
from textwrap import dedent

try:
    import pybel
except ImportError:
    print('Can not import Pybel!\nPlease install openbabel!')


def ReadBasicInfo():
    """Read parameters from info file"""

    ReadFilePath, OutputPath, ImportFormat, ExportFormat, ElementSuffix = '', '', 'cif', 'cif', ''
    CalculateCharge = False

    with open('TranslateInfo', 'r') as File:
        for Line in File.readlines():
            if Line.strip():
                WordList = Line.strip().split()
                if WordList[0] == '#':
                    continue
                elif WordList[0] == 'ReadFilePath:':
                    ReadFilePath = WordList[1]
                elif WordList[0] == 'OutputPath:':
                    OutputPath = WordList[1]
                elif WordList[0] == 'CalculateCharge:' and WordList[1] == 'yes':
                    CalculateCharge = True
                elif WordList[0] == 'ImportFormat:':
                    if WordList[1] == 'cif' or WordList[1] == 'pdb':
                        ImportFormat = WordList[1]
                    else:
                        print(
                            'Failed to run!\nPlease input right import format!\nThis code can only read format of cif or pdb!')
                        sys.exit()
                elif WordList[0] == 'ExportFormat:':
                    if WordList[1] == 'cif' or WordList[1] == 'pdb' or WordList[1] == 'mol':
                        ExportFormat = WordList[1]
                    else:
                        print(
                            'Failed to run!\nPlease input right export format!\nThis code only can translate to format of cif, pdb or mol!')
                        sys.exit()
                elif WordList[0] == 'ElementSuffix:':
                    if len(WordList) > 1:
                        ElementSuffix = WordList[1]

    return ReadFilePath, OutputPath, CalculateCharge, ImportFormat, ExportFormat, ElementSuffix


def ImportMaterialInfo(OriginalFullNamePath, CalculateCharge, ImportFormat):

    if ImportFormat == 'cif':
        CellX = next(pybel.readfile('cif', OriginalFullNamePath))
    elif ImportFormat == 'pdb':
        CellX = next(pybel.readfile('pdb', OriginalFullNamePath))

    CellX.unitcell.FillUnitCell(CellX.OBMol)
    if CalculateCharge:
        CellX.calccharges('eqeq')
    CellY = CellX.unitcell
    CellLengthA, CellLengthB, CellLengthC = CellY.GetA(), CellY.GetB(), CellY.GetC()
    CellAngleAlpha, CellAngleBeta, CellAngleGamma = CellY.GetAlpha(
    ), CellY.GetBeta(), CellY.GetGamma()
    AtomNum = CellX.OBMol.NumAtoms()

    return CellX, CellY, CellLengthA, CellLengthB, CellLengthC, CellAngleAlpha, CellAngleBeta, CellAngleGamma, AtomNum


def TranslateToCif(
        NewName,
        NewNamePath,
        ElementSuffix,
        OriginalFullNamePath,
        ElementTable,
        Time,
        CellX,
        CellY,
        CellLengthA,
        CellLengthB,
        CellLengthC,
        CellAngleAlpha,
        CellAngleBeta,
        CellAngleGamma):
    """Translate to cif format"""

    OutputFile = dedent("""
data_{NewName:<30s}
_audit_creation_method  'PyMSATm cif file'
_audit_creation_date    {Time:10s}
_cell_length_a    {CellLengthA:.4f}
_cell_length_b    {CellLengthB:.4f}
_cell_length_c    {CellLengthC:.4f}
_cell_angle_alpha    {CellAngleAlpha:.4f}
_cell_angle_beta     {CellAngleBeta:.4f}
_cell_angle_gamma    {CellAngleGamma:.4f}
_space_group_name_H-M_alt 'P 1'
_space_group_name_Hall 'P 1'
loop_
_symmetry_equiv_pos_as_xyz
x,y,z
loop_
_atom_site_label
_atom_site_type_symbol
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
_atom_site_charge
""".format(**locals())).strip()
    for Atom in CellX:
        Element = ElementTable.GetSymbol(Atom.atomicnum)
        Label = Element + ElementSuffix
        Charge = Atom.partialcharge
        AtomVecter = CellY.WrapFractionalCoordinate(
            CellY.CartesianToFractional(Atom.vector))
        X, Y, Z = AtomVecter.GetX(), AtomVecter.GetY(), AtomVecter.GetZ()

        OutputFile += dedent(
            "\n{Label:<7s} {Element:<4s}  {X:9.5f}   {Y:9.5f}   {Z:9.5f}   {Charge:9.6f}".format(
                **locals()))

    OutputFile += "\n_end\n"

    with open(NewNamePath, 'w') as File:
        File.write(OutputFile)


def TranslateToPdb(
        NewName,
        NewNamePath,
        ElementSuffix,
        OriginalFullNamePath,
        ElementTable,
        Time,
        CellX,
        CellY,
        CellLengthA,
        CellLengthB,
        CellLengthC,
        CellAngleAlpha,
        CellAngleBeta,
        CellAngleGamma):
    """Translate to pdb format which can read by PyMSATm"""

    Range = 0
    OutputFile = dedent("""
REMARK   PyMSATm PDB file
REMARK   Created:  {Time:10s}
CRYST1{CellLengthA:>9.3f}{CellLengthB:>9.3f}{CellLengthC:>9.3f}{CellAngleAlpha:>7.2f}{CellAngleBeta:>7.2f}{CellAngleGamma:>7.2f} P1
""".format(**locals())).strip()

    for Atom in CellX:
        Range += 1
        Element = ElementTable.GetSymbol(Atom.atomicnum)
        Label = Element + ElementSuffix
        Charge = Atom.partialcharge
        AtomVecter = CellY.WrapCartesianCoordinate(Atom.vector)
        X, Y, Z = AtomVecter.GetX(), AtomVecter.GetY(), AtomVecter.GetZ()

        OutputFile += dedent(
            """\nATOM  {Range:>5d} {Label:<4s} MOL     2    {X:>8.3f}{Y:>8.3f}{Z:>8.3f}{Charge:>6.2f}                {Element:>2s}""".format(
                **locals())).strip('')

    OutputFile += dedent("""\nTER\nEND\n""")

    with open(NewNamePath, 'w') as File:
        File.write(OutputFile)


def TranslateToMol(
        NewName,
        NewNamePath,
        ElementSuffix,
        OriginalFullNamePath,
        ElementTable,
        Time,
        CellX,
        CellY,
        CellLengthA,
        CellLengthB,
        CellLengthC,
        CellAngleAlpha,
        CellAngleBeta,
        CellAngleGamma,
        AtomNum):
    """Translate to mol format which can read by PyMASTm"""

    Range = 0

    OutputFile = dedent("""# Basic Molecule Information
# Created by PyMSATm at {Time:10s}
Molecule_name: {NewName:<30s}

Coord_Info: Listed Cartesian None
{AtomNum:10d}\n""".format(**locals()))

    for Atom in CellX:
        Range += 1
        Element = ElementTable.GetSymbol(Atom.atomicnum)
        Label = Element + ElementSuffix
        Charge = Atom.partialcharge
        AtomVecter = CellY.WrapCartesianCoordinate(Atom.vector)
        X, Y, Z = AtomVecter.GetX(), AtomVecter.GetY(), AtomVecter.GetZ()

        OutputFile += dedent(
            """{Range:<6d}  {X:>8.4f}  {Y:>8.4f}  {Z:>8.4f} {Label:>8s}  {Charge:>10.6f}   0   0\n""".format(
                **locals()))

    OutputFile += dedent("""
Fundcell_Info:  Listed
{CellLengthA:<.4f} {CellLengthB:<.4f} {CellLengthC:<.4f}
{CellAngleAlpha:<.4f} {CellAngleBeta:<.4f} {CellAngleGamma:<.4f}
0.0000  0.00000  0.00000
{CellLengthA:<.4f} {CellLengthB:<.4f} {CellLengthC:<.4f}""".format(**locals()))

    with open(NewNamePath, 'w') as File:
        File.write(OutputFile)


def main():
    """main function"""

    ReadFilePath, OutputPath, CalculateCharge, ImportFormat, ExportFormat, ElementSuffix = ReadBasicInfo()

    OriginalFullNameList = os.listdir(ReadFilePath)
    ElementTable = pybel.ob.OBElementTable()
    Time = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    if ExportFormat == 'pdb':
        CalculateCharge = False

    print('The code is running:')
    for OriginalFullName in OriginalFullNameList:
        OriginalName, OriginalNameType = os.path.splitext(OriginalFullName)
        OriginalFullNamePath = os.path.join(ReadFilePath, OriginalFullName)

        NewName = OriginalName

        NewFullName = ''.join([NewName, '.', ExportFormat])
        NewNamePath = os.path.join(OutputPath, NewFullName)

        if OriginalNameType == '.' + ImportFormat:
            print(OriginalName)
            CellX, CellY, CellLengthA, CellLengthB, CellLengthC, CellAngleAlpha, CellAngleBeta, CellAngleGamma, AtomNum = ImportMaterialInfo(
                OriginalFullNamePath, CalculateCharge, ImportFormat)
            if ExportFormat == 'cif':
                TranslateToCif(
                    NewName,
                    NewNamePath,
                    ElementSuffix,
                    OriginalFullNamePath,
                    ElementTable,
                    Time,
                    CellX,
                    CellY,
                    CellLengthA,
                    CellLengthB,
                    CellLengthC,
                    CellAngleAlpha,
                    CellAngleBeta,
                    CellAngleGamma)
            elif ExportFormat == 'pdb':
                TranslateToPdb(
                    NewName,
                    NewNamePath,
                    ElementSuffix,
                    OriginalFullNamePath,
                    ElementTable,
                    Time,
                    CellX,
                    CellY,
                    CellLengthA,
                    CellLengthB,
                    CellLengthC,
                    CellAngleAlpha,
                    CellAngleBeta,
                    CellAngleGamma)
            elif ExportFormat == 'mol':
                TranslateToMol(
                    NewName,
                    NewNamePath,
                    ElementSuffix,
                    OriginalFullNamePath,
                    ElementTable,
                    Time,
                    CellX,
                    CellY,
                    CellLengthA,
                    CellLengthB,
                    CellLengthC,
                    CellAngleAlpha,
                    CellAngleBeta,
                    CellAngleGamma,
                    AtomNum)

    print('The transformation is finished')


if __name__ == '__main__':
    main()
