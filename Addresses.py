# Python 3.6.5

from sys import exit
import win32api, ctypes
from ctypes import wintypes as w
from win32com.client import GetObject
from re import findall

class GameAddresses:
    a = {}

    def __init__(self):
        try:
            f = open("game_addresses.txt", "r")
            try:
                for line in f:
                    line = line.strip()
                    if len(line) == 0 or line[0] == "#":
                        continue
                    name, addr, _ = findall('([a-z0-9\_\-]+) += +((0x)?[a-fA-F0-9]+)', line)[0]
                    GameAddresses.a[name] = int(addr, 16)
            except Exception as e:
                print("Invalid game_addresses.txt format")
                print(e)
        except:
            print("Could not open file game_addresses.txt")

class GameClass:
    def __init__(self, processName):
        self.PID = 0
        self.PROCESS = None
        
        wmi = GetObject('winmgmts:')
        for p in wmi.InstancesOf('win32_process'):
            if p.Name == processName:  
                self.PID = int(p.Properties_('ProcessId'))
            
        if self.PID == 0:
            print("Couldn't find process \"%s\"" % (processName))
            exit(1)
    
        self.PROCESS = win32api.OpenProcess(0x1F0FFF, 0, self.PID)
        self.handle = self.PROCESS.handle

    def readBytes(self, addr, bytes_length):
        buff = ctypes.create_string_buffer(bytes_length)
        bufferSize = ctypes.sizeof(buff)
        bytesRead = ctypes.c_ulonglong(0)
        
        if ReadProcessMemory(self.handle, addr, buff, bufferSize, ctypes.byref(bytesRead)) != 1:
            raise Exception('Could not read memory addr "%x" (%d bytes): invalid address or process closed?' % (addr, bytes_length))

        return bytes(buff)
    
    def writeBytes(self, addr, value):
        return WriteProcessMemory(self.handle, addr, bytes(value), len(value), None)

    def readInt(self, addr, bytes_length=4, endian='little'):
        return int.from_bytes(self.readBytes(addr, bytes_length), endian)
        
    def writeInt(self, addr, value, bytes_length=0):
        if bytes_length <= 0:
            bytes_length = value.bit_length() + 7 // 8
        return self.writeBytes(addr, value.to_bytes(bytes_length, 'little'))
 
ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
ReadProcessMemory.argtypes = [w.HANDLE, w.LPCVOID, w.LPVOID, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
ReadProcessMemory.restype = w.BOOL
        
WriteProcessMemory = ctypes.windll.kernel32.WriteProcessMemory
WriteProcessMemory.restype = w.BOOL
WriteProcessMemory.argtypes = [w.HANDLE, w.LPVOID, w.LPCVOID, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t) ]

VirtualAllocEx = ctypes.windll.kernel32.VirtualAllocEx
VirtualAllocEx.restype = w.LPVOID
VirtualAllocEx.argtypes = (w.HANDLE, w.LPVOID, w.DWORD, w.DWORD, w.DWORD)

VirtualFreeEx  = ctypes.windll.kernel32.VirtualFreeEx 
VirtualFreeEx.restype = w.LPVOID
VirtualFreeEx.argtypes = (w.HANDLE, w.LPVOID, w.DWORD, w.DWORD)

MEM_RESERVE = 0x00002000
MEM_COMMIT = 0x00001000
MEM_DECOMMIT = 0x4000
MEM_RELEASE = 0x8000
PAGE_EXECUTE_READWRITE = 0x40

GetLastError = ctypes.windll.kernel32.GetLastError
GetLastError.restype = ctypes.wintypes.DWORD
GetLastError.argtypes = ()

GameAddresses()