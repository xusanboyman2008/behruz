"""
Async Server
"""
import asyncio
import mmap

class AS:
    def __init__(self,host,port,sMsize=256,sFsize=65536,rMsize=256,rFsize=65536):
        self.host=host
        self.port=port
        self.sMs=sMsize
        self.sFs=sFsize
        self.rMs=rMsize
        self.rFs=rFsize
        self.clis=[0]*65535 # max cli ports how possible
        self.interuptcode=b'/\x00\x07/'
        self.icl=len(self.interuptcode)
        async def ced(_):pass #Client Exited Default function
        async def osd(_):pass #On Start Default function
        self.cli_ex_func=ced
        self.pro_func=osd

    def run(self):asyncio.run(self.st())
    
    def message_reception(self,func):self.message_func=func
    
    def file_reception(self,func):self.file_func=func
    
    def client_exited(self,func):self.cli_ex_func=func
    
    def start(self,func):self.pro_func=func
    
    async def st(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        self.server = server
        self.serv_addr = server.sockets[0].getsockname()
        await self.pro_func(self.serv_addr)
        async with server:
            await server.serve_forever()
            
        
    async def handle_client(self,reader, writer):
        addr = writer.get_extra_info('peername')
        self.clis[addr[1]]=writer #Ident with port number
        
        calls_m,calls_f=0,0
        try:
            while True:
                rMs=self.rMs
                rFs=self.rFs
                datatyp=await reader.read(7)
                if datatyp==b'/\x00MeSs/':
                    received_data = b""
                    try:
                        while True:
                            data = await reader.read(rMs)
                            if not data:print("Bu umuman ishlamasligi kutilmoqda\n(Agar bu senga ko'rinsa dasturda e'tiborga olinmagan hodisa yuz berdi va [bu BUG]) ...");exit(1)
                            received_data += data
                            if received_data[-self.icl:]==self.interuptcode:
                                received_data=received_data[:-self.icl]
                                break
                        await self.message_func(received_data,addr,calls_m)
                        calls_m+=1
                    except asyncio.CancelledError:pass
                elif datatyp==b'/\x00FiLe/':
                    try:
                        fs = int((await reader.read(16)).decode().lstrip('0'))
                        rc = fs/rFs
                        if not rc.is_integer():rc=int(rc)+1
                        async def receiver():
                            for _ in range(int(rc)):
                                # print(_,'/',rc-1)
                                yield await reader.read(rFs)
                        await self.file_func(receiver,fs,addr,calls_f)
                        calls_f+=1
                    except asyncio.CancelledError:pass
                elif not datatyp:
                    writer.close()
                    await writer.wait_closed()
                    self.clis[addr[1]]=0
                    await self.cli_ex_func(addr)
                    return None
                else:
                    print("Qiyshiq so'rov")
        except:
            writer.close()
            await writer.wait_closed()
            self.clis[addr[1]]=0
            await self.cli_ex_func(addr)
            return None
        
    async def sMessage(self,cli,message:bytes,buffer_s:int=0):
        message=memoryview(message)
        writer=self.clis[cli]
        if not buffer_s:buffer_s = self.sMs
        for i in range(0, len(message), buffer_s):
            writer.write(message[i:i+buffer_s])
            await writer.drain()
        writer.write(self.interuptcode)
        
    async def sFile(self,cli,file,size,buffer_s:int=0):
        writer=self.clis[cli]
        if not buffer_s:buffer_s = self.sFs
        mmf = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)
        writer.write(str(size).rjust(16,'0').encode()) #16 baytda fayl hajmi (1024^5) b ~> 1 PiB :)
        for i in range(0, size, buffer_s):
            writer.write(mmf[i:i+buffer_s])
            await writer.drain()
        # writer.write(self.interuptcode)