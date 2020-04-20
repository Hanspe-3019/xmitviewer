''' Extract attributes of load module directory entry
    see IHAPDS macro:

    */********************************************************************/
    */*                                                                  */
    */*  MACRO NAME: IHAPDS                                              */
    */*                                                                  */
    */*  DESCRIPTION: MAPS THE PARTITIONED DATA SET (PDS) AND PARTITIONED*/
    */*      DATA SET EXTENDED (PDSE) DIRECTORY ENTRY.                   */
    */*      BYTES PRIOR TO THE USER DATA (UP TO AND INCLUDING PDS2INDC) */
    */*      CAN BE USED TO MAP ANY TYPE OF PDS OR PDSE DIRECTORY ENTRY. */
    */*      THE USER DATA (BYTES BEYOND PDS2INDC) DESCRIBE THE          */
    */*      DIRECTORY ENTRY FOR EXECUTABLE PROGRAMS.                    */
    */*                                                                  */
    */*  COPYRIGHT:                                                      */
    */*PROPRIETARY V3 STATEMENT                                          */
    */*LICENSED MATERIALS - PROPERTY OF IBM                              */
    */*"RESTRICTED MATERIALS OF IBM"                                     */
    */*5650-ZOS
    */*COPYRIGHT IBM CORP. 1982, 2013                                    */
    */*END PROPRIETARY V3 STATEMENT                                      */
    */*                                                                  */
    */*  USAGE:                                                          */
    */*                                                                  */
    */*      THE PDS(E) DIRECTORY ENTRY MAY HAVE ANY OR ALL OF THE       */
    */*      FOLLOWING SIX SECTIONS IN THIS ORDER --                     */
    */*      1.    BASIC (OPTIONALLY CONTAINS 2 BLDL BYTES)              */
    */*      2.    SCATTER LOAD   - OPTIONAL                             */
    */*      3.    ALIAS          - OPTIONAL                             */
    */*      4.    SSI            - OPTIONAL (NOTE: THIS SECTION IS      */
    */*                                       ALWAYS ON A HALF WORD      */
    */*                                       BOUNDARY)               */
    */*      5.    APF            - OPTIONAL                             */
    */*      6.    LPO            - OPTIONAL
    */*      7.    XATTR          - OPTIONAL
    */*                                                                  */
    */*  METHOD OF ACCESS:                                               */
    */*                                                                  */
    */*      BAL  - DSECT IS PRODUCED UNLESS DSECT=NO IS SPECIFIED.      */
    */*             USING ON PDS2 GIVES ADDRESSABILITY FOR ALL SYMBOLS.  */
    */*             THE MACRO EXPANSION WILL INCLUDE THE TWO BYTES       */
    */*             INSERTED BY BLDL UNLESS PDSBLDL=NO IS SPECIFIED.     */
    */*      PL/S - DCL (PDS2PTR,PDSPTRV) PTR                            */
    */*             THE MACRO EXPANSION WILL INCLUDE THE TWO BYTES       */
    */*             INSERTED BY BLDL UNLESS %PDSBLDL='NO' IS SPECIFIED   */
    */*             BEFORE INCLUDE FOR MACRO.                            */
    */*   m                                                              */
    */*             THE FOLLOWING 5 PL/X STATEMENTS SHOW HOW THE         */
    */*             STARTING ADDRESS OF ANY OF THE SIX OPTIONAL          */
    */*             SECTIONS OF USER DATA MAY BE OBTAINED.               */
    */*                                                                  */
    */*             (1) PDSPTRV=ADDR(PDSBCEND)                           */
    */*             (2) IF PDS2SCTR='1'B THEN PDSPTRV=PDSPTRV +          */
    */*                 LENGTH(PDSS01)                                   */
    */*             (3) IF PDS2ALIS='1'B THEN PDSPTRV=PDSPTRV +          */
    */*                 LENGTH(PDSS02)                                   */
    */*             (4) IF PDS2SSI='1'B THEN PDSPTRV=(PDSPTRV +          */
    */*                 LENGTH(PDSS03) + 1)/2*2                          */
    */*             (5) IF PDSAPFLG='1'B THEN PDSPTRV=PDSPTRV +          */
    */*                 LENGTH(PDSS04)
    */*             (6) IF PDS2BIG='1'B THEN PDSPTRV=PDSPTRV +           */
    */*                 LENGTH(PDSLPO)
    */*                                                                  */
    */*             STATEMENT (1) GETS THE ADDRESS FOR THE START OF THE  */
    */*             OPTIONAL SECTIONS.  TO GET THE STARTING ADDRESS OF   */
    */*             THE SCATTER LOAD SECTION, USE STATEMENT (1).  FOR    */
    */*             THE ALIAS SECTION, USE STATEMENTS (1) AND (2).  FOR  */
    */*             THE SSI SECTION, USE STATEMENTS (1), (2) AND (3)     */
    */*             AND ADD ONE TO ADDRESS IN PDSPTRV IF ADDRESS IS NOT  */
    */*             ON A HALF-WORD BOUNDARY. FOR THE APF SECTION, USE    */
    */*             (1), (2), (3) AND (4). FOR THE LPO SECTION, USE ALL  */
    */*             (1), (2), (3), (4), AND (5). FOR THE XATTR SECTION,  */
    */*             USE ALL 6 STATEMENTS
    */********************************************************************/
             MACRO
             IHAPDS &PDSBLDL=YES,&DSECT=YES
    .*
             IEZBITS ,            SYMBOLIC BIT DEFINITIONS
    PDS2     DSECT ,              PDS2PTR
    PDS2NAME DS    CL8            MEMBER NAME OR ALIAS NAME
    PDS2TTRP DS    CL3            TTR OF FIRST BLOCK OF NAMED MEMBER
    PDS2INDC DS    B              INDICATOR BYTE
    PDS2ALIS EQU   BIT0           NAME IN THE FIELD PDS2NAME IS AN ALIAS
    DEALIAS  EQU   BIT0 --- ALIAS FOR PDS2ALIS
    PDS2NTTR EQU   BIT1+BIT2      NUMBER OF TTR'S IN THE USER DATA FIELD
    PDS2LUSR EQU   BIT3+BIT4+BIT5+BIT6+BIT7 - LENGTH OF USER DATA FIELD
    *                             IN HALF WORDS
    * End of shortest possible entry.  Start of load module attributes
    PDS2USRD DS    0C             START OF VARIABLE LENGTH USER DATA FIELD
    PDS2TTRT DS    CL3            TTR OF FIRST BLOCK OF TEXT
    PDS2ZERO DS    C              ZERO
    PDS2TTRN DS    CL3            TTR OF NOTE LIST OR SCATTER/TRANSLATION
    *                             TABLE.  USED FOR PROGRAM IN SCATTER LOAD
    *                             FORMAT OR OVERLAY STRUCTURE ONLY.
    PDS2NL   DS    FL1            NUMBER OF ENTRIES IN NOTE LIST FOR
    *                             PROGRAM IN OVERLAY STRUCTURE
    PDS2ATR  DS    0BL2           TWO-BYTE PROGRAM ATTRIBUTE FIELD
    PDS2ATR1 DS    B              FIRST BYTE OF PROGRAM ATTRIBUTE FIELD
    PDS2RENT EQU   BIT0           REENTERABLE
    DEREEN   EQU   BIT0 --- ALIAS FOR PDS2RENT
    PDS2REUS EQU   BIT1           REUSABLE
    PDS2OVLY EQU   BIT2           IN OVERLAY STRUCTURE
    DEOVLY   EQU   BIT2 --- ALIAS FOR PDS2OVLY
    PDS2TEST EQU   BIT3           PROGRAM TO BE TESTED - TESTRAN
    PDS2LOAD EQU   BIT4           ONLY LOADABLE
    DELODY   EQU   BIT4 --- ALIAS FOR PDS2LOAD
    PDS2SCTR EQU   BIT5           SCATTER FORMAT
    DESCAT   EQU   BIT5 --- ALIAS FOR PDS2SCTR
    PDS2EXEC EQU   BIT6           EXECUTABLE
    DEXCUT   EQU   BIT6 --- ALIAS FOR PDS2EXEC
    PDS21BLK EQU   BIT7           IF ZERO, PROGRAM CONTAINS MULTIPLE
    *                             RECORDS WITH AT LEAST ONE BLOCK OF TEXT.
    *                             IF ONE, PROGRAM CONTAINS NO RLD ITEMS AND
    *                             ONLY ONE BLOCK OF TEXT.
    PDS2ATR2 DS    B              SECOND BYTE OF PROGRAM ATTRIBUTE FIELD
    PDS2FLVL EQU   BIT0           If one, the program cannot be processed
    *                             by the E level of the linkage editor
    *                             from the early days of OS/360.
    *                             IF OFF, THE PROGRAM CAN BE PROCESSED BY
    *                             ANY LEVEL OF THE LINKAGE EDITOR OR THE
    *                             BINDER.
    PDS2ORG0 EQU   BIT1           ORIGIN OF FIRST BLOCK OF TEXT IS ZERO
    PDS2EP0  EQU   BIT2           ENTRY POINT IS ZERO
    PDS2NRLD EQU   BIT3           PROGRAM CONTAINS NO RLD ITEMS
    PDS2NREP EQU   BIT4           PROGRAM CANNOT BE REPROCESSED BY LINKAGE
    *                             EDITOR OR BINDER.
    PDS2TSTN EQU   BIT5           PROGRAM CONTAINS TESTRAN SYMBOL CARDS
    PDS2LEF  EQU   BIT6           PROGRAM CREATED BY LINKAGE EDITOR F
    PDS2REFR EQU   BIT7           REFRESHABLE PROGRAM
    PDS2STOR DS    FL3            TOTAL CONTIGUOUS MAIN STORAGE REQUIREMENT
    *                             OF PROGRAM
    PDS2FTBL DS    FL2            LENGTH OF FIRST BLOCK OF TEXT
    PDS2EPA  DS    AL3            ENTRY POINT ADDRESS ASSOCIATED WITH
    *                             MEMBER NAME OR WITH ALIAS NAME IF ALIAS
    *                             INDICATOR IS ONE
             DS    0AL3           LINKAGE EDITOR ASSIGNED ORIGIN OF FIRST
    *                             BLOCK OF TEXT (OS/360 USE OF FIELD)
    PDS2FTBO DS    0BL3           FLAG BYTES (MVS USE OF FIELD)
    PDS2FTB1 DS    B              BYTE 1 OF PDS2FTBO
    PDSAOSLE EQU   BIT0           Program has been processed by OS/VS1 or
    *                             OS/VS2 linkage editor or binder
    PDS2BIG  EQU   BIT1           THE LARGE PROGRAM OBJECT EXTENSION
    *                             EXISTS BECAUSE THIS PROGRAM REQUIRES AT
    *                             LEAST 16 MB BYTES OF VIRTUAL STORAGE
    PDS2PAGA EQU   BIT2           PAGE ALIGNMENT REQUIRED FOR PROGRAM
    PDS2SSI  EQU   BIT3           SSI INFORMATION PRESENT
    PDSAPFLG EQU   BIT4           INFORMATION IN PDSAPF IS VALID
    PDS2PGMO EQU   BIT5           PROGRAM OBJECT. THE PDS2FTB3
    *                             FIELD IS VALID AND CONTAINS ADDITIONAL
    *                             FLAGS
    PDS2LFMT EQU   PDS2PGMO       ALTERNATE NAME FOR PDS2PGMO
    PDS2SIGN EQU   BIT6           PROGRAM OBJECT IS SIGNED. VERIFIED ON
    *                             LOAD IF DIRECTED BY SECURITY PRODUCT
    PDS2XATR EQU   BIT7           PDS2XATTR SECTION
    PDS2FTB2 DS    B              BYTE 2 OF PDS2FTBO
    PDS2ALTP EQU   BIT0           ALTERNATE PRIMARY FLAG. IF ON (FOR A
    *                             PRIMARY NAME), INDICATES THE PRIMARY
    *                             NAME WAS GENERATED BY THE BINDER.
    *                             CAN ONLY BE ON FOR PROGRAM OBJECT.
    *                             CANNOT BE ON FOR ALIAS NAME
    PDSLRMOD EQU   BIT3           PROGRAM RESIDENCE MODE
    PDSAAMOD EQU   BIT4+BIT5      ALIAS ENTRY POINT ADDRESSING MODE
    *                             B'00' = AMODE 24
    *                             B'10' = AMODE 31
    *                             B'11' = AMODE ANY
    *                             B'01' = AMODE 64
    PDSMAMOD EQU   BIT6+BIT7      MAIN ENTRY POINT ADDRESSING MODE
    *                             B'00' = AMODE 24
    *                             B'10' = AMODE 31
    *                             B'11' = AMODE ANY
    *                             B'01' = AMODE 64
    PDS2RLDS DS    0XL1           NUMBER OF RLD/CONTROL RECORDS WHICH
    *                             FOLLOW THE FIRST BLOCK OF TEXT
    PDS2FTB3 DS    B              BYTE 3 OF PDS2FTBO
    PDS2NMIG EQU   BIT0           THIS PROGRAM OBJECT CANNOT BE CONVERTED
    *                             TO A LOAD MODULE
    PDS2PRIM EQU   BIT1           FETCHOPT PRIME WAS SPECIFIED
    PDS2PACK EQU   BIT2           FETCHOPT PACK WAS SPECIFIED
    PDSBCEND EQU   *              END OF BASIC SECTION
    PDSBCLN  EQU   PDSBCEND-PDS2 - LENGTH OF BASIC SECTION
             SPACE 2
    *        THE FOLLOWING SECTION IS FOR PROGRAMS WITH SCATTER LOAD
             SPACE 1
    PDSS01   EQU   *              START OF SCATTER LOAD SECTION
    PDS2SLSZ DS    FL2            NUMBER OF BYTES IN SCATTER LIST
    PDS2TTSZ DS    FL2            NUMBER OF BYTES IN TRANSLATION TABLE
    PDS2ESDT DS    CL2            IDENTIFICATION OF ESD ITEM (ESDID) OF
    *                             CONTROL SECTION TO WHICH FIRST BLOCK OF
    *                             TEXT BELONGS
    PDS2ESDC DS    CL2            IDENTIFICATION OF ESD ITEM (ESDID) OF
    *                             CONTROL SECTION CONTAINING ENTRY POINT
    PDSS01ND EQU   *              END OF SCATTER LOAD SECTION
    PDSS01LN EQU   PDSS01ND-PDSS01 - LENGTH OF SCATTER LOAD SECTION
             SPACE 2
    *        THE FOLLOWING SECTION IS FOR PROGRAMS WITH ALIAS NAMES
             SPACE 1
    PDSS02   EQU   *              START OF ALIAS SECTION
    PDS2EPM  DS    AL3            ENTRY POINT FOR MEMBER NAME
    DEENTBK  EQU   PDS2EPM --- ALIAS
    PDS2MNM  DS    CL8            MEMBER NAME OF PROGRAM. WHEN THE
    *                             FIRST FIELD (PDS2NAME) IS AN ALIAS NAME,
    *                             THIS FIELD CONTAINS THE ORIGINAL NAME OF
    *                             THE MEMBER EVEN AFTER THE MEMBER HAS
    *                             BEEN RENAMED.
    PDSS02ND EQU   *              END OF ALIAS SECTION
    PDSS02LN EQU   PDSS02ND-PDSS02 - LENGTH OF ALIAS SECTION
             SPACE 2
    *        THE FOLLOWING SECTION IS FOR SSI INFORMATION AND IS ON
    *        A HALF-WORD BOUNDARY
             SPACE 1
    PDSS03   DS    0H             FORCE HALF-WORD ALIGNMENT FOR SSI
    *                             SECTION
    PDSSSIWD DS    0CL4           SSI INFORMATION WORD
    PDSCHLVL DS    FL1            CHANGE LEVEL OF MEMBER
    PDSSSIFB DS    B              SSI FLAG BYTE
    PDSFORCE EQU   BIT1           A FORCE CONTROL CARD WAS USED WHEN
    *                             EXECUTING THE IHGUAP PROGRAM
    PDSUSRCH EQU   BIT2           A CHANGE WAS MADE TO MEMBER BY THE
    *                             INSTALLATION, AS OPPOSED TO AN
    *                             IBM-DISTRIBUTED CHANGE
    PDSEMFIX EQU   BIT3           SET WHEN AN EMERGENCY IBM-AUTHORIZED
    *                             PROGRAM 'FIX' IS MADE, AS OPPOSED TO
    *                             CHANGES THAT ARE INCLUDED IN AN
    *                             IBM-DISTRIBUTED MAINTENANCE PACKAGE
    PDSDEPCH EQU   BIT4           A CHANGE MADE TO THE MEMBER IS DEPENDENT
    *                             UPON A CHANGE MADE TO SOME OTHER MEMBER
    *                             IN THE SYSTEM
    PDSSYSGN EQU   BIT5+BIT6      FLAGS THAT INDICATE WHETHER A
    *                             CHANGE TO THE MEMBER WILL NECESSITATE A
    *                             PARTIAL OR COMPLETE REGENERATION OF THE
    *                             SYSTEM
    PDSNOSGN EQU   X'00'          NOT CRITICAL FOR SYSTEM GENERATION
    PDSCMSGN EQU   BIT6           MAY REQUIRE COMPLETE REGENERATION
    PDSPTSGN EQU   BIT5           MAY REQUIRE PARTIAL REGENERATION
    PDSIBMMB EQU   BIT7           MEMBER IS SUPPLIED BY IBM
    PDSMBRSN DS    CL2            MEMBER SERIAL NUMBER
    PDSS03ND EQU   *              END OF SSI SECTION
    PDSS03LN EQU   PDSS03ND-PDSS03   LENGTH OF SSI SECTION
             SPACE 2
    *        THE FOLLOWING SECTION IS FOR APF INFORMATION                 *
             SPACE 1
    PDSS04   EQU   *              START OF APF SECTION
    PDSAPF   DS    0CL2           PROGRAM AUTHORIZATION FACILITY (APF)
    *                             FIELD
    PDSAPFCT DS    FL1            LENGTH OF PROGRAM AUTHORIZATION CODE
    *                             (PDSAPFAC) IN BYTES
    PDSAPFAC DS    C              PROGRAM AUTHORIZATION CODE
    PDSS04ND EQU   *              END OF APF SECTION
    PDSS04LN EQU   PDSS04ND-PDSS04   LENGTH OF APF SECTION
             SPACE 2
    *        THE FOLLOWING SECTION IS FOR LARGE (16M OR LARGER) PROGRAM
    *                      OBJECTS
             SPACE 1
    PDSLPO   EQU   *              START OF LARGE PROGRAM OBJECT SECTION
    PDSLLM   EQU   PDSLPO         ALTERNATE NAME FOR PDSLPO
    PDS2LPOL DS    FL1            LARGE PROGRAM OBJECT SECTION LENGTH
             ORG   PDS2LPOL
    PDS2LLML DS    FL1            ALTERNATE NAME FOR PDS2LLML
    PDS2VSTR DS    FL4            VIRTUAL STORAGE REQUIREMENT FOR THIS
    *                             PROGRAM
    PDS2MEPA DS    FL4            MAIN ENTRY POINT OFFSET
    PDS2AEPA DS    FL4            ALIAS ENTRY POINT OFFSET. ONLY VALID
    *                             IF THIS IS A DIRECTORY ENTRY FOR AN
    *                             ALIAS
    PDSLPOND EQU   *              END OF LARGE PROGRAM OBJECT SECTION
    PDSLLMND EQU   PDSLPOND       ALTERNATE NAME FOR PDSLPOND
    PDSLPOLN EQU   PDSLPOND-PDSLPO  LENGTH OF LLM SECTION
    PDSLLMLN EQU   PDSLPOLN       ALTERNATE NAME FOR PDSLPOLN
    *        The following section is for extended attributes.
    *        It is present only when bit PDS2XATR is on.
             SPACE 1
    PDS2XATTR EQU  *              Start of extended attributes
    PDS2XATTRBYTE0 DS FL1         Extended attribute byte 0
    PDS2XATTR_OPTN_MASK EQU X'0F' Bits 4-7 of PDS2XATTRBYTE0 identify the  -
                                  number of bytes (could be 0) starting    -
                                  at PDS2XATTR_OPT
    PDS2XATTRBYTE1 DS FL1         Extended attribute byte 1
    PDS2LONGPARM EQU X'80'        PARM > 100 chars allowed
                  DS FL1          Reserved
    PDS2XATTR_OPT EQU *           Start of optional fields. Number of      -
                                  bytes is in PDS2XATTRBYTE0 masked by     -
                                  PDS2XATTR_OPTN_MASK
             MEND
'''
from collections import namedtuple
import struct

import xmitviewer.iebcopy.userdata as userdata
import xmitviewer.utils.dumper as dumper

BASICSECTION = struct.Struct('>8x B B 3s 2x 3s B B B')
Basicsection = namedtuple(
    'Basicsection',
    'atr1 atr2 stor epa ftb1 ftb2 ftb3'
)
PDSS01LN = 8    # Length of scatter load section
PDSS02LN = 11   # Length of alias section
PDSS03LN = 4    # Length of SSI section (halfword aligned!)
ATR1RENT = 0b10000000
ATR1REUS = 0b01000000
ATR1LOAD = 0b00001000
ATR1SCTR = 0b00000100
ATR1EXEC = 0b00000010
FTB1SSI = 0b00010000
FTB1APFLG = 0b00001000
FTB1LFMT = 0b00000100
FTB1XATR = 0b00000001   # XATTR Section
FTB2RMOD = 0b00010000
FTB2AMOD = 0b00001100
FTB2AMOD31 = 0b00001000
FTB2AMOD64 = 0b00000100
FTB2MAMOD = 0b00000011
FTB2MAMOD31 = 0b00000010
FTB2MAMOD64 = 0b00000001

def extract_lmod(dirdata, is_alias=False):
    '''Userdata in directory entry of load module or program object
    Basic Section with 12 half words:
    '''
    if len(dirdata) < BASICSECTION.size:
        return userdata.UserdataUnknown(dirdata)

    bdata = Basicsection(*BASICSECTION.unpack(dirdata[:BASICSECTION.size]))
    stor_int = int.from_bytes(bdata.stor, byteorder='big')
    stor = '{:08X}'.format(stor_int)
    rent = 'RN' if bdata.atr1 & ATR1RENT else '--'
    reus = 'RU' if bdata.atr1 & ATR1REUS else '--'
    nonx = '--' if bdata.atr1 & ATR1EXEC else 'NX'

#   lfmt = 'LPO' if bdata.ftb1 & FTB1LFMT else ' - '
#   xatr = 'XAT' if bdata.ftb1 & FTB1XATR else ' - '
    rmod = 'ANY' if bdata.ftb2 & FTB2RMOD else '24 '
    amod = 'ANY' if (bdata.ftb2 & FTB2MAMOD) > FTB2MAMOD31 else\
            '31 ' if bdata.ftb2 & FTB2MAMOD31 else\
            '64 ' if bdata.ftb2 & FTB2MAMOD64 else '24 '

    pos = BASICSECTION.size
    if bdata.atr1 & ATR1SCTR:
        pos = pos + PDSS01LN
    if is_alias:
        basisname = extract_alias(dirdata[pos:])
    else:
        basisname = 8*' '

    if bdata.ftb1 & FTB1APFLG:
        if is_alias:
            pos = pos + PDSS02LN
        if bdata.ftb1 & FTB1SSI:
            pos = ((pos + PDSS03LN + 1)//2)*2
        authcode = extract_apf(dirdata[pos:])
    else:
        authcode = '--'

    attributes = ' '.join(
        (basisname, stor, authcode, amod, rmod, rent, reus, nonx))
    return UserdataLmod(bdata, attributes)

class UserdataLmod(object):
    '''Wrapper around load module userdata in directory,
        only to provide __repr__ of it.
    '''
    def __init__(self, bdata, attributes):
        self.dirdata = bdata
        self.attributes = attributes
    def __repr__(self):
        return self.attributes
def extract_alias(alias_section):
    '''Fetch base name of alias
    '''
    return dumper.check_cp037(alias_section[3:11])
def extract_apf(apf_section):
    '''Fetch AC from apf section
    '''
    return '{:02d}'.format(apf_section[1])
