#!/usr/bin/python
'''
* LICENSE PLACEHOLDER
*
* @file client.py
* @package OpenPST Extras - QFPROM Kernel Module
* @brief This client can be used with the qfprom kernel module when started with start_tcp=PORT
* @usage
*   read addresses:
*       python client.py [HOST] [PORT] -r 0x00000000 0x00000001 0x00000002
*   read corrected addresses:
*       python client.py [HOST] [PORT] -rc 0x00000000 0x00000001 0x00000002
* @author Gassan Idriss <ghassani@gmail.com>
'''
import sys
import argparse
import socket
import ctypes
import pprint
import time
import binascii
import re
import struct
import csv

def read_row(sock, addr, corrected=False):    
    request = struct.pack('<BLL', 0x01, addr, 0x00000001 if corrected else 0x00000000)
    #print 'Request   :', binascii.hexlify(request)
    written = sock.send(request)
    #print "Sent %d bytes\n" % written 
    response = sock.recv(1024); 
    #print 'Response   :', binascii.hexlify(response)
    command, address, read_type, lsb, msb, error = struct.unpack('<BLLLLL', response)
    
    return {'address': address, 'lsb': lsb, 'msb' : msb, 'error' : error}

def read_row_direct(sock, addr):    
    request = struct.pack('<BLL', 0x03, addr, 0x00000000)
    #print 'Request   :', binascii.hexlify(request)
    written = sock.send(request)
    #print "Sent %d bytes\n" % written 
    response = sock.recv(1024); 
    #print 'Response   :', binascii.hexlify(response)
    command, address, read_type, lsb, msb, error = struct.unpack('<BLLLLL', response)
    
    return {'address': address, 'lsb': lsb, 'msb' : msb, 'error' : error}

def read_many(sock, addresses, corrected=False):
    try:

        for addr in addresses:
            address = int(addr, 16)
            result = read_row(sock, address, False)
            if result['error'] > 0:
                print "Error reading 0x%08X - %d" % (result['address'], result['error'] )
            else:
                print "Row data for 0x%08X - LSB: 0x%08X MSB: 0x%08X" % ( result['address'], result['lsb'], result['msb'] )
    except TypeError, e:
        pass
    except NameError, e:
        pass
    except Exception, e:
        print e

def read_many_direct(sock, addresses, corrected=False):
    try:

        for addr in addresses:
            address = int(addr, 16)
            result = read_row_direct(sock, address)
            if result['error'] > 0:
                print "Error reading 0x%08X - %d" % (result['address'], result['error'] )
            else:
                print "Row data for 0x%08X - LSB: 0x%08X MSB: 0x%08X" % ( result['address'], result['lsb'], result['msb'] )
    except TypeError, e:
        pass
    except NameError, e:
        pass
    except Exception, e:
        print e

def write_row(sock, addr, lsb, msb, bus_clk_khz):    
    request = struct.pack('<BLLLL', 0x01, addr, bus_clk_khz, lsb, msb)
    #print 'Request   :', binascii.hexlify(request)
    written = sock.send(request)
    #print "Sent %d bytes\n" % written 
    response = sock.recv(1024);
    #print 'Response   :', binascii.hexlify(response)
    command, address, read_type, lsb, msb, error = struct.unpack('<BLLLLL', response)
    
    return {'address': address, 'lsb': lsb, 'msb' : msb, 'error' : error}

def custom(sock):
    raw_rows = {
        'HWIO_QFPROM_RAW_ACC_PRIVATEn_ADDR(0)' : 0xFC4B8000,
        'HWIO_QFPROM_RAW_ACC_PRIVATEn_ADDR(1)' : 0xFC4B8004,
        'HWIO_QFPROM_RAW_ACC_PRIVATEn_ADDR(2)' : 0xFC4B8008,
        'HWIO_QFPROM_RAW_JTAG_ID_LSB_ADDR' : 0xFC4B80A0,
#        'HWIO_QFPROM_RAW_JTAG_ID_MSB_ADDR' : 0xFC4B80A4,
        'HWIO_QFPROM_RAW_RD_WR_PERM_LSB_ADDR' : 0xFC4B80A8,
#        'HWIO_QFPROM_RAW_RD_WR_PERM_MSB_ADDR' : 0xFC4B80AC,
        'HWIO_QFPROM_RAW_PTE_LSB_ADDR' : 0xFC4B80B0,
#        'HWIO_QFPROM_RAW_PTE_MSB_ADDR' : 0xFC4B80B4,
        'HWIO_QFPROM_RAW_AP_ANTI_ROLLBACK_ROW0_LSB_ADDR' : 0xFC4B80B8,
#        'HWIO_QFPROM_RAW_AP_ANTI_ROLLBACK_ROW0_MSB_ADDR' : 0xFC4B80BC,
        'HWIO_QFPROM_RAW_AP_ANTI_ROLLBACK_ROW1_LSB_ADDR' : 0xFC4B80C0,
#        'HWIO_QFPROM_RAW_AP_ANTI_ROLLBACK_ROW1_MSB_ADDR' : 0xFC4B80C4,
        'HWIO_QFPROM_RAW_MSA_ANTI_ROLLBACK_LSB_ADDR' : 0xFC4B80C8,
#        'HWIO_QFPROM_RAW_MSA_ANTI_ROLLBACK_MSB_ADDR' : 0xFC4B80CC,
        'HWIO_QFPROM_RAW_IMEI_ESN0_LSB_ADDR' : 0xFC4B80D0,
#        'HWIO_QFPROM_RAW_IMEI_ESN0_MSB_ADDR' : 0xFC4B80D4,
        'HWIO_QFPROM_RAW_IMEI_ESN1_LSB_ADDR' : 0xFC4B80D8,
#        'HWIO_QFPROM_RAW_IMEI_ESN1_MSB_ADDR' : 0xFC4B80DC,
        'HWIO_QFPROM_RAW_IMEI_ESN2_LSB_ADDR' : 0xFC4B80E0,
#        'HWIO_QFPROM_RAW_IMEI_ESN2_MSB_ADDR' : 0xFC4B80E4,
        'HWIO_QFPROM_RAW_OEM_CONFIG_ROW0_LSB_ADDR' : 0xFC4B80E8,
#        'HWIO_QFPROM_RAW_OEM_CONFIG_ROW0_MSB_ADDR' : 0xFC4B80EC,
        'HWIO_QFPROM_RAW_OEM_CONFIG_ROW1_LSB_ADDR' : 0xFC4B80F0,
#        'HWIO_QFPROM_RAW_OEM_CONFIG_ROW1_MSB_ADDR' : 0xFC4B80F4,
        'HWIO_QFPROM_RAW_FEAT_CONFIG_ROW0_LSB_ADDR' : 0xFC4B80F8,
#        'HWIO_QFPROM_RAW_FEAT_CONFIG_ROW0_MSB_ADDR' : 0xFC4B80FC,
        'HWIO_QFPROM_RAW_FEAT_CONFIG_ROW1_LSB_ADDR' : 0xFC4B8100,
#        'HWIO_QFPROM_RAW_FEAT_CONFIG_ROW1_MSB_ADDR' : 0xFC4B8104,
        'HWIO_QFPROM_RAW_FEAT_CONFIG_ROW2_LSB_ADDR' : 0xFC4B8108,
#        'HWIO_QFPROM_RAW_FEAT_CONFIG_ROW2_MSB_ADDR' : 0xFC4B810C,
        'HWIO_QFPROM_RAW_FEAT_CONFIG_ROW3_LSB_ADDR' : 0xFC4B8110,
#        'HWIO_QFPROM_RAW_FEAT_CONFIG_ROW3_MSB_ADDR' : 0xFC4B8114,
        'HWIO_QFPROM_RAW_MEM_REDUNn_ADDR(0)' : 0xFC4B8118,
        'HWIO_QFPROM_RAW_DEBUG_KEY_LSB_ADDR' : 0xFC4B81A8,
#        'HWIO_QFPROM_RAW_DEBUG_KEY_MSB_ADDR' : 0xFC4B81AC,
        'HWIO_QFPROM_RAW_MEM_ACCEL_ROW0_LSB_ADDR' : 0xFC4B81B0,
#        'HWIO_QFPROM_RAW_MEM_ACCEL_ROW0_MSB_ADDR' : 0xFC4B81B4,
        'HWIO_QFPROM_RAW_MEM_ACCEL_ROW1_LSB_ADDR' : 0xFC4B81B8,
#        'HWIO_QFPROM_RAW_MEM_ACCEL_ROW1_MSB_ADDR' : 0xFC4B81BC,
        'HWIO_QFPROM_RAW_CALIB_ROW0_LSB_ADDR' : 0xFC4B81C0,
#        'HWIO_QFPROM_RAW_CALIB_ROW0_MSB_ADDR' : 0xFC4B81C4,
        'HWIO_QFPROM_RAW_CALIB_ROW1_LSB_ADDR' : 0xFC4B81C8,
#        'HWIO_QFPROM_RAW_CALIB_ROW1_MSB_ADDR' : 0xFC4B81CC,
        'HWIO_QFPROM_RAW_FEC_EN_LSB_ADDR' : 0xFC4B81D0,
#        'HWIO_QFPROM_RAW_FEC_EN_MSB_ADDR' : 0xFC4B81D4,
        #'HWIO_QFPROM_RAW_INTAGLIO_GLUEBIT_LSB_ADDR' : 0xFC4B81D8,
#        #'HWIO_QFPROM_RAW_INTAGLIO_GLUEBIT_MSB_ADDR' : 0xFC4B81DC,
        'HWIO_QFPROM_RAW_CUST_KEY_ROWn_LSB_ADDR(0)' : 0xFC4B81E0,
        'HWIO_QFPROM_RAW_CUST_KEY_ROWn_LSB_ADDR(1)' : 0xFC4B81E8,
        'HWIO_QFPROM_RAW_CUST_KEY_ROWn_LSB_ADDR(2)' : 0xFC4B81F0,
#        'HWIO_QFPROM_RAW_CUST_KEY_ROWn_MSB_ADDR(0)' : 0xFC4B81E4,
#        'HWIO_QFPROM_RAW_CUST_KEY_ROWn_MSB_ADDR(1)' : 0xFC4B81EC,
#        'HWIO_QFPROM_RAW_CUST_KEY_ROWn_MSB_ADDR(2)' : 0xFC4B81F4,
        'HWIO_QFPROM_RAW_SERIAL_NUM_LSB_ADDR' : 0xFC4B81F0,
#        'HWIO_QFPROM_RAW_SERIAL_NUM_MSB_ADDR' : 0xFC4B81F4,
        'HWIO_QFPROM_RAW_SPARE_REG19_LSB_ADDR' : 0xFC4B81F8,
#        'HWIO_QFPROM_RAW_SPARE_REG19_MSB_ADDR' : 0xFC4B81FC,
        'HWIO_QFPROM_RAW_ROM_PATCH_ROWn_LSB_ADDR(0)' : 0xFC4B8200,
        'HWIO_QFPROM_RAW_ROM_PATCH_ROWn_LSB_ADDR(1)' : 0xFC4B8208,
        'HWIO_QFPROM_RAW_ROM_PATCH_ROWn_LSB_ADDR(2)' : 0xFC4B8210,
#        'HWIO_QFPROM_RAW_ROM_PATCH_ROWn_MSB_ADDR(0)' : 0xFC4B8204,
#        'HWIO_QFPROM_RAW_ROM_PATCH_ROWn_MSB_ADDR(1)' : 0xFC4B820C,
#        'HWIO_QFPROM_RAW_ROM_PATCH_ROWn_MSB_ADDR(2)' : 0xFC4B8214,
        'HWIO_QFPROM_RAW_PRI_KEY_DERIVATION_KEY_ROWn_LSB_ADDR(0)' : 0xFC4B8380,
        'HWIO_QFPROM_RAW_PRI_KEY_DERIVATION_KEY_ROWn_LSB_ADDR(1)' : 0xFC4B8388,
        'HWIO_QFPROM_RAW_PRI_KEY_DERIVATION_KEY_ROWn_LSB_ADDR(2)' : 0xFC4B8390,
#        'HWIO_QFPROM_RAW_PRI_KEY_DERIVATION_KEY_ROWn_MSB_ADDR(0)' : 0xFC4B8384,
#        'HWIO_QFPROM_RAW_PRI_KEY_DERIVATION_KEY_ROWn_MSB_ADDR(1)' : 0xFC4B838C,
#        'HWIO_QFPROM_RAW_PRI_KEY_DERIVATION_KEY_ROWn_MSB_ADDR(2)' : 0xFC4B8394,
#        'HWIO_QFPROM_RAW_PRI_KEY_DERIVATION_KEY_ROW4_MSB_ADDR' : 0xFC4B83A4,
        'HWIO_QFPROM_RAW_SEC_KEY_DERIVATION_KEY_ROWn_LSB_ADDR(0)' : 0xFC4B83A8,
        'HWIO_QFPROM_RAW_SEC_KEY_DERIVATION_KEY_ROWn_LSB_ADDR(1)' : 0xFC4B83B0,
        'HWIO_QFPROM_RAW_SEC_KEY_DERIVATION_KEY_ROWn_LSB_ADDR(2)' : 0xFC4B83B8,
#        'HWIO_QFPROM_RAW_SEC_KEY_DERIVATION_KEY_ROWn_MSB_ADDR(0)' : 0xFC4B83AC,
#        'HWIO_QFPROM_RAW_SEC_KEY_DERIVATION_KEY_ROWn_MSB_ADDR(1)' : 0xFC4B83B4,
#        'HWIO_QFPROM_RAW_SEC_KEY_DERIVATION_KEY_ROWn_MSB_ADDR(2)' : 0xFC4B83BC,
        'HWIO_QFPROM_RAW_SEC_KEY_DERIVATION_KEY_ROW4_LSB_ADDR' : 0xFC4B83C8,
#        'HWIO_QFPROM_RAW_SEC_KEY_DERIVATION_KEY_ROW4_MSB_ADDR' : 0xFC4B83CC,
        'HWIO_QFPROM_RAW_OEM_PK_HASH_ROWn_LSB_ADDR(0)' : 0xFC4B83D0,
        'HWIO_QFPROM_RAW_OEM_PK_HASH_ROWn_LSB_ADDR(1)' : 0xFC4B83D8,
        'HWIO_QFPROM_RAW_OEM_PK_HASH_ROWn_LSB_ADDR(2)' : 0xFC4B83E0,
#        'HWIO_QFPROM_RAW_OEM_PK_HASH_ROWn_MSB_ADDR(0)' : 0xFC4B83D4,
#        'HWIO_QFPROM_RAW_OEM_PK_HASH_ROWn_MSB_ADDR(1)' : 0xFC4B83DC,
#        'HWIO_QFPROM_RAW_OEM_PK_HASH_ROWn_MSB_ADDR(2)' : 0xFC4B83E4,
        'HWIO_QFPROM_RAW_OEM_PK_HASH_ROW4_LSB_ADDR' : 0xFC4B83F0,
#        'HWIO_QFPROM_RAW_OEM_PK_HASH_ROW4_MSB_ADDR' : 0xFC4B83F4,
        'HWIO_QFPROM_RAW_OEM_SEC_BOOT_ROWn_LSB_ADDR(0)' : 0xFC4B83F8,
        'HWIO_QFPROM_RAW_OEM_SEC_BOOT_ROWn_LSB_ADDR(1)' : 0xFC4B8400,
        'HWIO_QFPROM_RAW_OEM_SEC_BOOT_ROWn_LSB_ADDR(2)' : 0xFC4B8408,
#        'HWIO_QFPROM_RAW_OEM_SEC_BOOT_ROWn_MSB_ADDR(0)' : 0xFC4B83FC,
#        'HWIO_QFPROM_RAW_OEM_SEC_BOOT_ROWn_MSB_ADDR(1)' : 0xFC4B8404,
#        'HWIO_QFPROM_RAW_OEM_SEC_BOOT_ROWn_MSB_ADDR(2)' : 0xFC4B840C,
        'HWIO_QFPROM_RAW_QC_SEC_BOOT_ROWn_LSB_ADDR(0)' : 0xFC4B8418,
        'HWIO_QFPROM_RAW_QC_SEC_BOOT_ROWn_LSB_ADDR(1)' : 0xFC4B8420,
        'HWIO_QFPROM_RAW_QC_SEC_BOOT_ROWn_LSB_ADDR(2)' : 0xFC4B8428,
#        'HWIO_QFPROM_RAW_QC_SEC_BOOT_ROWn_MSB_ADDR(0)' : 0xFC4B841C,
#        'HWIO_QFPROM_RAW_QC_SEC_BOOT_ROWn_MSB_ADDR(1)' : 0xFC4B8424,
#        'HWIO_QFPROM_RAW_QC_SEC_BOOT_ROWn_MSB_ADDR(2)' : 0xFC4B842C,
        'HWIO_QFPROM_RAW_USB_VID_PID_LSB_ADDR' : 0xFC4B8438,
#        'HWIO_QFPROM_RAW_USB_VID_PID_MSB_ADDR' : 0xFC4B843C,
        'HWIO_QFPROM_RAW_SW_CALIB_ROW0_LSB_ADDR' : 0xFC4B8440,
#        'HWIO_QFPROM_RAW_SW_CALIB_ROW0_MSB_ADDR' : 0xFC4B8444,
        'HWIO_QFPROM_RAW_SW_CALIB_ROW1_LSB_ADDR' : 0xFC4B8448,
#        'HWIO_QFPROM_RAW_SW_CALIB_ROW1_MSB_ADDR' : 0xFC4B844C,
        'HWIO_QFPROM_RAW_SPARE_REG28_ROW0_LSB_ADDR' : 0xFC4B8450,
#        'HWIO_QFPROM_RAW_SPARE_REG28_ROW0_MSB_ADDR' : 0xFC4B8454,
        'HWIO_QFPROM_RAW_SPARE_REG28_ROW1_LSB_ADDR' : 0xFC4B8458,
#        'HWIO_QFPROM_RAW_SPARE_REG28_ROW1_MSB_ADDR' : 0xFC4B845C,
        'HWIO_QFPROM_RAW_SPARE_REG28_ROW2_LSB_ADDR' : 0xFC4B8460,
#        'HWIO_QFPROM_RAW_SPARE_REG28_ROW2_MSB_ADDR' : 0xFC4B8464,
        'HWIO_QFPROM_RAW_SPARE_REG29_ROWn_LSB_ADDR(0)' : 0xFC4B8468,
        'HWIO_QFPROM_RAW_SPARE_REG29_ROWn_LSB_ADDR(1)' : 0xFC4B8470,
        'HWIO_QFPROM_RAW_SPARE_REG29_ROWn_LSB_ADDR(2)' : 0xFC4B8478,
#        'HWIO_QFPROM_RAW_SPARE_REG29_ROWn_MSB_ADDR(0)' : 0xFC4B846C,
#        'HWIO_QFPROM_RAW_SPARE_REG29_ROWn_MSB_ADDR(1)' : 0xFC4B8474,
#        'HWIO_QFPROM_RAW_SPARE_REG29_ROWn_MSB_ADDR(2)' : 0xFC4B847C,
        'HWIO_QFPROM_RAW_SPARE_REG30_ROWn_LSB_ADDR(0)' : 0xFC4B84F8,
        'HWIO_QFPROM_RAW_SPARE_REG30_ROWn_LSB_ADDR(1)' : 0xFC4B8500,
        'HWIO_QFPROM_RAW_SPARE_REG30_ROWn_LSB_ADDR(2)' : 0xFC4B8508,
#        'HWIO_QFPROM_RAW_SPARE_REG30_ROWn_MSB_ADDR(0)' : 0xFC4B84FC,
#        'HWIO_QFPROM_RAW_SPARE_REG30_ROWn_MSB_ADDR(1)' : 0xFC4B8504,
#        'HWIO_QFPROM_RAW_SPARE_REG30_ROWn_MSB_ADDR(2)' : 0xFC4B850C,
        'HWIO_QFPROM_RAW_SPARE_REG31_ROWn_LSB_ADDR(0)' : 0xFC4B8580,
        'HWIO_QFPROM_RAW_SPARE_REG31_ROWn_LSB_ADDR(1)' : 0xFC4B8588,
        'HWIO_QFPROM_RAW_SPARE_REG31_ROWn_LSB_ADDR(2)' : 0xFC4B8590,
#        'HWIO_QFPROM_RAW_SPARE_REG31_ROWn_MSB_ADDR(0)' : 0xFC4B8584,
#        'HWIO_QFPROM_RAW_SPARE_REG31_ROWn_MSB_ADDR(1)' : 0xFC4B858C,
#        'HWIO_QFPROM_RAW_SPARE_REG31_ROWn_MSB_ADDR(2)' : 0xFC4B8594,
        'HWIO_QFPROM_BLOW_TIMER_ADDR' : 0xFC4BA038,
        'HWIO_QFPROM_TEST_CTRL_ADDR' : 0xFC4BA03C,
        'HWIO_QFPROM_ACCEL_ADDR' : 0xFC4BA040,
        'HWIO_QFPROM_BLOW_STATUS_ADDR' : 0xFC4BA048,
        'HWIO_QFPROM_BIST_CTRL_ADDR' : 0xFC4BA050,
        'HWIO_QFPROM_BIST_ERROR_ADDR' : 0xFC4BA054,
        'HWIO_QFPROM_HASH_SIGNATUREn_ADDR(0)' : 0xFC4BA060,
        'HWIO_QFPROM_ROM_ERROR_ADDR' : 0xFC4BA090,
        'HWIO_QFPROM_CLK_CTL_ADDR' : 0xFC4BE0D4,
    }

    corrected_rows = {
        'HWIO_QFPROM_CORR_ACC_PRIVATEn_ADDR(0)' : 0xFC4BC000,
        'HWIO_QFPROM_CORR_ACC_PRIVATEn_ADDR(1)' : 0xFC4BC004,
        'HWIO_QFPROM_CORR_ACC_PRIVATEn_ADDR(2)' : 0xFC4BC008,
        'HWIO_QFPROM_CORR_JTAG_ID_LSB_ADDR' : 0xFC4BC0A0,
#        'HWIO_QFPROM_CORR_JTAG_ID_MSB_ADDR' : 0xFC4BC0A4,
        'HWIO_QFPROM_CORR_RD_WR_PERM_LSB_ADDR' : 0xFC4BC0A8,
#        'HWIO_QFPROM_CORR_RD_WR_PERM_MSB_ADDR' : 0xFC4BC0AC,
        'HWIO_QFPROM_CORR_PTE_LSB_ADDR' : 0xFC4BC0B0,
#        'HWIO_QFPROM_CORR_PTE_MSB_ADDR' : 0xFC4BC0B4,
        'HWIO_QFPROM_CORR_AP_ANTI_ROLLBACK_ROW0_LSB_ADDR' : 0xFC4BC0B8,
#        'HWIO_QFPROM_CORR_AP_ANTI_ROLLBACK_ROW0_MSB_ADDR' : 0xFC4BC0BC,
        'HWIO_QFPROM_CORR_AP_ANTI_ROLLBACK_ROW1_LSB_ADDR' : 0xFC4BC0C0,
#        'HWIO_QFPROM_CORR_AP_ANTI_ROLLBACK_ROW1_MSB_ADDR' : 0xFC4BC0C4,
        'HWIO_QFPROM_CORR_MSA_ANTI_ROLLBACK_LSB_ADDR' : 0xFC4BC0C8,
#        'HWIO_QFPROM_CORR_MSA_ANTI_ROLLBACK_MSB_ADDR' : 0xFC4BC0CC,
        'HWIO_QFPROM_CORR_IMEI_ESN0_LSB_ADDR' : 0xFC4BC0D0,
#        'HWIO_QFPROM_CORR_IMEI_ESN0_MSB_ADDR' : 0xFC4BC0D4,
        'HWIO_QFPROM_CORR_IMEI_ESN1_LSB_ADDR' : 0xFC4BC0D8,
#        'HWIO_QFPROM_CORR_IMEI_ESN1_MSB_ADDR' : 0xFC4BC0DC,
        'HWIO_QFPROM_CORR_IMEI_ESN2_LSB_ADDR' : 0xFC4BC0E0,
#        'HWIO_QFPROM_CORR_IMEI_ESN2_MSB_ADDR' : 0xFC4BC0E4,
        'HWIO_QFPROM_CORR_OEM_CONFIG_ROW0_LSB_ADDR' : 0xFC4BC0E8,
#        'HWIO_QFPROM_CORR_OEM_CONFIG_ROW0_MSB_ADDR' : 0xFC4BC0EC,
        'HWIO_QFPROM_CORR_OEM_CONFIG_ROW1_LSB_ADDR' : 0xFC4BC0F0,
#        'HWIO_QFPROM_CORR_OEM_CONFIG_ROW1_MSB_ADDR' : 0xFC4BC0F4,
        'HWIO_QFPROM_CORR_FEAT_CONFIG_ROW0_LSB_ADDR' : 0xFC4BC0F8,
#        'HWIO_QFPROM_CORR_FEAT_CONFIG_ROW0_MSB_ADDR' : 0xFC4BC0FC,
        'HWIO_QFPROM_CORR_FEAT_CONFIG_ROW1_LSB_ADDR' : 0xFC4BC100,
#        'HWIO_QFPROM_CORR_FEAT_CONFIG_ROW1_MSB_ADDR' : 0xFC4BC104,
        'HWIO_QFPROM_CORR_FEAT_CONFIG_ROW2_LSB_ADDR' : 0xFC4BC108,
#        'HWIO_QFPROM_CORR_FEAT_CONFIG_ROW2_MSB_ADDR' : 0xFC4BC10C,
        'HWIO_QFPROM_CORR_FEAT_CONFIG_ROW3_LSB_ADDR' : 0xFC4BC110,
#        'HWIO_QFPROM_CORR_FEAT_CONFIG_ROW3_MSB_ADDR' : 0xFC4BC114,
        'HWIO_QFPROM_CORR_MEM_REDUNn_ADDR(0)' : 0xFC4BC118,
        'HWIO_QFPROM_CORR_MEM_REDUNn_ADDR(1)' : 0xFC4BC11C,
        'HWIO_QFPROM_CORR_MEM_REDUNn_ADDR(2)' : 0xFC4BC120,
        'HWIO_QFPROM_CORR_DEBUG_KEY_LSB_ADDR' : 0xFC4BC1A8,
#        'HWIO_QFPROM_CORR_DEBUG_KEY_MSB_ADDR' : 0xFC4BC1AC,
        'HWIO_QFPROM_CORR_MEM_ACCEL_ROW0_LSB_ADDR' : 0xFC4BC1B0,
#        'HWIO_QFPROM_CORR_MEM_ACCEL_ROW0_MSB_ADDR' : 0xFC4BC1B4,
        'HWIO_QFPROM_CORR_MEM_ACCEL_ROW1_LSB_ADDR' : 0xFC4BC1B8,
#        'HWIO_QFPROM_CORR_MEM_ACCEL_ROW1_MSB_ADDR' : 0xFC4BC1BC,
        'HWIO_QFPROM_CORR_CALIB_ROW0_LSB_ADDR' : 0xFC4BC1C0,
#        'HWIO_QFPROM_CORR_CALIB_ROW0_MSB_ADDR' : 0xFC4BC1C4,
        'HWIO_QFPROM_CORR_CALIB_ROW1_LSB_ADDR' : 0xFC4BC1C8,
#        'HWIO_QFPROM_CORR_CALIB_ROW1_MSB_ADDR' : 0xFC4BC1CC,
        'HWIO_QFPROM_CORR_FEC_EN_LSB_ADDR' : 0xFC4BC1D0,
#        'HWIO_QFPROM_CORR_FEC_EN_MSB_ADDR' : 0xFC4BC1D4,
        #'HWIO_QFPROM_CORR_INTAGLIO_GLUEBIT_LSB_ADDR' : 0xFC4BC1D8,
#        #'HWIO_QFPROM_CORR_INTAGLIO_GLUEBIT_MSB_ADDR' : 0xFC4BC1DC,
        'HWIO_QFPROM_CORR_CUST_KEY_ROWn_LSB_ADDR(0)' : 0xFC4BC1E0,
        'HWIO_QFPROM_CORR_CUST_KEY_ROWn_LSB_ADDR(1)' : 0xFC4BC1E8,
        'HWIO_QFPROM_CORR_CUST_KEY_ROWn_LSB_ADDR(2)' : 0xFC4BC1F0,
#        'HWIO_QFPROM_CORR_CUST_KEY_ROWn_MSB_ADDR(0)' : 0xFC4BC1E4,
#        'HWIO_QFPROM_CORR_CUST_KEY_ROWn_MSB_ADDR(1)' : 0xFC4BC1EC,
#        'HWIO_QFPROM_CORR_CUST_KEY_ROWn_MSB_ADDR(2)' : 0xFC4BC1F4,
        'HWIO_QFPROM_CORR_SERIAL_NUM_LSB_ADDR' : 0xFC4BC1F0,
#        'HWIO_QFPROM_CORR_SERIAL_NUM_MSB_ADDR' : 0xFC4BC1F4,
        'HWIO_QFPROM_CORR_SPARE_REG19_LSB_ADDR' : 0xFC4BC1F8,
#        'HWIO_QFPROM_CORR_SPARE_REG19_MSB_ADDR' : 0xFC4BC1FC,
        'HWIO_QFPROM_CORR_ROM_PATCH_ROWn_LSB_ADDR(0)' : 0xFC4BC200,
        'HWIO_QFPROM_CORR_ROM_PATCH_ROWn_LSB_ADDR(1)' : 0xFC4BC208,
        'HWIO_QFPROM_CORR_ROM_PATCH_ROWn_LSB_ADDR(2)' : 0xFC4BC210,
#        'HWIO_QFPROM_CORR_ROM_PATCH_ROWn_MSB_ADDR(0)' : 0xFC4BC204,
#        'HWIO_QFPROM_CORR_ROM_PATCH_ROWn_MSB_ADDR(1)' : 0xFC4BC20C,
#        'HWIO_QFPROM_CORR_ROM_PATCH_ROWn_MSB_ADDR(2)' : 0xFC4BC214,
        'HWIO_QFPROM_CORR_PRI_KEY_DERIVATION_KEY_ROWn_LSB_ADDR(0)' : 0xFC4BC380,
        'HWIO_QFPROM_CORR_PRI_KEY_DERIVATION_KEY_ROWn_LSB_ADDR(1)' : 0xFC4BC388,
        'HWIO_QFPROM_CORR_PRI_KEY_DERIVATION_KEY_ROWn_LSB_ADDR(2)' : 0xFC4BC390,
#        'HWIO_QFPROM_CORR_PRI_KEY_DERIVATION_KEY_ROWn_MSB_ADDR(0)' : 0xFC4BC384,
#        'HWIO_QFPROM_CORR_PRI_KEY_DERIVATION_KEY_ROWn_MSB_ADDR(1)' : 0xFC4BC38C,
#        'HWIO_QFPROM_CORR_PRI_KEY_DERIVATION_KEY_ROWn_MSB_ADDR(2)' : 0xFC4BC394,
        'HWIO_QFPROM_CORR_PRI_KEY_DERIVATION_KEY_ROW4_LSB_ADDR' : 0xFC4BC3A0,
#        'HWIO_QFPROM_CORR_PRI_KEY_DERIVATION_KEY_ROW4_MSB_ADDR' : 0xFC4BC3A4,
        'HWIO_QFPROM_CORR_SEC_KEY_DERIVATION_KEY_ROWn_LSB_ADDR(0)' : 0xFC4BC3A8,
        'HWIO_QFPROM_CORR_SEC_KEY_DERIVATION_KEY_ROWn_LSB_ADDR(1)' : 0xFC4BC3B0,
        'HWIO_QFPROM_CORR_SEC_KEY_DERIVATION_KEY_ROWn_LSB_ADDR(2)' : 0xFC4BC3B8,
#        'HWIO_QFPROM_CORR_SEC_KEY_DERIVATION_KEY_ROWn_MSB_ADDR(0)' : 0xFC4BC3AC,
#        'HWIO_QFPROM_CORR_SEC_KEY_DERIVATION_KEY_ROWn_MSB_ADDR(1)' : 0xFC4BC3B4,
#        'HWIO_QFPROM_CORR_SEC_KEY_DERIVATION_KEY_ROWn_MSB_ADDR(2)' : 0xFC4BC3BC,
        'HWIO_QFPROM_CORR_SEC_KEY_DERIVATION_KEY_ROW4_LSB_ADDR' : 0xFC4BC3C8,
#        'HWIO_QFPROM_CORR_SEC_KEY_DERIVATION_KEY_ROW4_MSB_ADDR' : 0xFC4BC3CC,
        'HWIO_QFPROM_CORR_OEM_PK_HASH_ROWn_LSB_ADDR(0)' : 0xFC4BC3D0,
        'HWIO_QFPROM_CORR_OEM_PK_HASH_ROWn_LSB_ADDR(1)' : 0xFC4BC3D8,
        'HWIO_QFPROM_CORR_OEM_PK_HASH_ROWn_LSB_ADDR(2)' : 0xFC4BC3E0,
#        'HWIO_QFPROM_CORR_OEM_PK_HASH_ROWn_MSB_ADDR(0)' : 0xFC4BC3D4,
#        'HWIO_QFPROM_CORR_OEM_PK_HASH_ROWn_MSB_ADDR(1)' : 0xFC4BC3DC,
#        'HWIO_QFPROM_CORR_OEM_PK_HASH_ROWn_MSB_ADDR(2)' : 0xFC4BC3E4,
        'HWIO_QFPROM_CORR_OEM_PK_HASH_ROW4_LSB_ADDR' : 0xFC4BC3F0,
#        'HWIO_QFPROM_CORR_OEM_PK_HASH_ROW4_MSB_ADDR' : 0xFC4BC3F4,
        'HWIO_QFPROM_CORR_OEM_SEC_BOOT_ROWn_LSB_ADDR(0)' : 0xFC4BC3F8,
        'HWIO_QFPROM_CORR_OEM_SEC_BOOT_ROWn_LSB_ADDR(1)' : 0xFC4BC400,
        'HWIO_QFPROM_CORR_OEM_SEC_BOOT_ROWn_LSB_ADDR(2)' : 0xFC4BC408,
#        'HWIO_QFPROM_CORR_OEM_SEC_BOOT_ROWn_MSB_ADDR(0)' : 0xFC4BC3FC,
        'HWIO_QFPROM_CORR_QC_SEC_BOOT_ROWn_LSB_ADDR(1)' : 0xFC4BC420,
#        'HWIO_QFPROM_CORR_QC_SEC_BOOT_ROWn_MSB_ADDR(2)' : 0xFC4BC42C,
        'HWIO_QFPROM_CORR_USB_VID_PID_LSB_ADDR' : 0xFC4BC438,
#        'HWIO_QFPROM_CORR_USB_VID_PID_MSB_ADDR' : 0xFC4BC43C,
        'HWIO_QFPROM_CORR_SW_CALIB_ROW0_LSB_ADDR' : 0xFC4BC440,
#        'HWIO_QFPROM_CORR_SW_CALIB_ROW0_MSB_ADDR' : 0xFC4BC444,
        'HWIO_QFPROM_CORR_SW_CALIB_ROW1_LSB_ADDR' : 0xFC4BC448,
#        'HWIO_QFPROM_CORR_SW_CALIB_ROW1_MSB_ADDR' : 0xFC4BC44C,
        'HWIO_QFPROM_CORR_SPARE_REG28_ROW0_LSB_ADDR' : 0xFC4BC450,
#        'HWIO_QFPROM_CORR_SPARE_REG28_ROW0_MSB_ADDR' : 0xFC4BC454,
        'HWIO_QFPROM_CORR_SPARE_REG28_ROW1_LSB_ADDR' : 0xFC4BC458,
#        'HWIO_QFPROM_CORR_SPARE_REG28_ROW1_MSB_ADDR' : 0xFC4BC45C,
        'HWIO_QFPROM_CORR_SPARE_REG28_ROW2_LSB_ADDR' : 0xFC4BC460,
#        'HWIO_QFPROM_CORR_SPARE_REG28_ROW2_MSB_ADDR' : 0xFC4BC464,
        'HWIO_QFPROM_CORR_SPARE_REG29_ROWn_LSB_ADDR(0)' : 0xFC4BC468,
        'HWIO_QFPROM_CORR_SPARE_REG29_ROWn_LSB_ADDR(0)' : 0xFC4BC470,
        'HWIO_QFPROM_CORR_SPARE_REG29_ROWn_LSB_ADDR(0)' : 0xFC4BC478,
#        'HWIO_QFPROM_CORR_SPARE_REG29_ROWn_MSB_ADDR(0)' : 0xFC4BC46C,
#        'HWIO_QFPROM_CORR_SPARE_REG29_ROWn_MSB_ADDR(0)' : 0xFC4BC474,
#        'HWIO_QFPROM_CORR_SPARE_REG29_ROWn_MSB_ADDR(0)' : 0xFC4BC47C,
        'HWIO_QFPROM_CORR_SPARE_REG30_ROWn_LSB_ADDR(0)' : 0xFC4BC4F8,
        'HWIO_QFPROM_CORR_SPARE_REG30_ROWn_LSB_ADDR(0)' : 0xFC4BC500,
        'HWIO_QFPROM_CORR_SPARE_REG30_ROWn_LSB_ADDR(0)' : 0xFC4BC508,
#        'HWIO_QFPROM_CORR_SPARE_REG30_ROWn_MSB_ADDR(0)' : 0xFC4BC4FC,
#        'HWIO_QFPROM_CORR_SPARE_REG30_ROWn_MSB_ADDR(0)' : 0xFC4BC504,
#        'HWIO_QFPROM_CORR_SPARE_REG30_ROWn_MSB_ADDR(0)' : 0xFC4BC50C,
        'HWIO_QFPROM_CORR_SPARE_REG31_ROWn_LSB_ADDR(0)' : 0xFC4BC580,
        'HWIO_QFPROM_CORR_SPARE_REG31_ROWn_LSB_ADDR(0)' : 0xFC4BC588,
        'HWIO_QFPROM_CORR_SPARE_REG31_ROWn_LSB_ADDR(0)' : 0xFC4BC590,
#        'HWIO_QFPROM_CORR_SPARE_REG31_ROWn_MSB_ADDR(0)' : 0xFC4BC584,
#        'HWIO_QFPROM_CORR_SPARE_REG31_ROWn_MSB_ADDR(0)' : 0xFC4BC58C,
#        'HWIO_QFPROM_CORR_SPARE_REG31_ROWn_MSB_ADDR(0)' : 0xFC4BC594,
    }


    export = open('read_out.csv', 'a+')
    exportWriter = csv.writer(export, delimiter=',', quotechar='"')
    exportWriter.writerow([ 'Name', 'Address', 'LSB', 'MSB', 'Type', 'Error', 'Direct LSB On Error', 'Direct MSB On Error'])

    for name, address in raw_rows.iteritems():
        print "%s - 0x%08X" % (name, address)
        result = read_row(sock, address, False)

        _address = "0x%08X" % address
        if result['error'] > 0:
            print "Error reading 0x%08X - %d" % (result['address'], result['error'] )
            if address == 0xFC4B81E0 or address == 0xFC4B81E8 or address == 0xFC4B81F0:
                exportWriter.writerow([ name, _address, '', '', 'RAW', result['error'], 'SKIP', 'SKIP'])
            else:
                direct_result = read_row_direct(sock, address)            
                lsb = "0x%08X" % result['lsb']
                msb = "0x%08X" % result['msb']
                print "Direct Read Row data for 0x%08X - LSB: 0x%08X MSB: 0x%08X" % ( direct_result['address'], direct_result['lsb'], direct_result['msb'] )
                exportWriter.writerow([ name, _address, '', '', 'RAW', result['error'], lsb, msb])
        else:
            lsb = "0x%08X" % result['lsb']
            msb = "0x%08X" % result['msb']
            exportWriter.writerow([ name, _address, lsb, msb, 'RAW', ''])
            print "Row data for 0x%08X - LSB: 0x%08X MSB: 0x%08X" % ( result['address'], result['lsb'], result['msb'] )


    '''for name, address in corrected_rows.iteritems():
        print "%s - 0x%08X" % (name, address)
        result = read_row(sock, address, True)
        _address = "0x%08X" % address
        if result['error'] > 0:
            exportWriter.writerow([ name, _address, '', '', 'CORRECTED', result['error']])
            print "Error reading 0x%08X - %d" % (result['address'], result['error'] )
        else:
            lsb = "0x%08X" % result['lsb']
            msb = "0x%08X" % result['msb']
            exportWriter.writerow([ name, _address, lsb, msb, 'CORRECTED', ''])
            print "Row data for 0x%08X - LSB: 0x%08X MSB: 0x%08X" % ( result['address'], result['lsb'], result['msb'] )
    '''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('host', metavar='host', help='the host to connect to')
    parser.add_argument('port', metavar='port', type=int, help='the port to connect on')
    parser.add_argument('-r',   metavar='--read',   nargs='*',   help='Read specified address(es)')
    parser.add_argument('-rc',  metavar='--read-corrected',   nargs='*',   help='Read specified corrected address(es)')
    parser.add_argument('-rd',  metavar='--read-direct',   nargs='*',   help='Read specified addresses directly with readl')
    #parser.add_argument('-rcr',  metavar='--read-corrected-range',   nargs='*',   help='Read specified range of corrected addresses')
    args = parser.parse_args()
    
    print "Trying to connect to %s on port %d" % (args.host, args.port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.connect((args.host, args.port))
    except Exception, e:
        print "Error connecting to %s on port %d" % (args.host, args.port)
        return

    print "Connected"

    try:
        read_many(sock, args.r, False)
    except Exception, e:
        pass

    try:
        read_many(sock, args.rc, True)
    except Exception, e:
        pass

    try:
        read_many_direct(sock, args.rd)
    except Exception, e:
        pass

    
    #custom(sock)

    print "Disconnecting"

    sock.send(struct.pack('B', 0x00))


if __name__ == '__main__':    
    main()

