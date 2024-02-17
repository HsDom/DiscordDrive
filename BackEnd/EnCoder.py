from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import math, datetime, os, json, base64



class EnCoder():
    def __init__(self, File):
        self.File = File
        self.BYTES = self.LoadFile()

    def LoadFile(self):
        with open(self.File, "rb") as text:
            return b''.join(text.readlines())
        
    def MbSize(self):
        return int(len(self.BYTES) / 1000000)
    
    def ByteSplit(self, Bytes, MaxSize_mb, Size_mb):
        SplitBytes = []
        if Size_mb > MaxSize_mb:
            Split = math.ceil(Size_mb / MaxSize_mb)
            SplitSize = math.ceil(len(Bytes) / Split)
            for i in range(Split):
                SplitBytes.append(Bytes[i*SplitSize:(i+1)*SplitSize])
        else:
            SplitBytes.append(Bytes)

        return SplitBytes
    
    def SaveToFile(self, Bytes):
        Files = []
        for bytes in Bytes:
            CurrentTime = datetime.datetime.now().strftime("%Y%m%d %H%M%S%f")
            with open(f"./BackEnd/Data/{CurrentTime}.data", "wb") as image:
                image.write(bytes)
            Files.append(f"./BackEnd/Data/{CurrentTime}.data")
        return Files
    

class Constructor():
    def __init__(self, Chuncks, FileName):
        self.Chuncks = Chuncks
        self.FileName = FileName

    def RebuildFile(self):
        Bytes = b''
        for chunck in self.Chuncks:
            print(chunck[1])
            with open(chunck[1], "rb") as file:
                Bytes += b''.join(file.readlines())
        return Bytes
    
    def SaveFile(self):
        Bytes = self.RebuildFile()
        with open(f"{self.FileName}", "wb") as file:
            file.write(Bytes)
        return f"{self.FileName}"
    