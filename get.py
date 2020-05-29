import wmi,winreg,re,getopt
import pymysql,win32com
from win32com import gen_py

import time

from datetime import datetime

import os,sys

c = wmi.WMI()
mainboardId = c.Win32_BaseBoard()[0].SerialNumber
pattern = re.compile(r'\)|\(|\'|\"\.')

"""id,SerialNumber,Name,model,Manufacturer,sizeValue,hardType,descript"""
def deal_str(s):
    if s:
        return re.sub(pattern,'',s)
    else: return s


def get_cpu(c,mainboardId):
    SerialNumber_dict = {}
    Name_list = []
    for cpu in c.Win32_Processor():
        tmpdict = {}
        tmpdict['mainboardId'] = deal_str(mainboardId)
        try:
            tmpdict["Name"] = deal_str(cpu.Name)
        except:
            tmpdict["Name"] = 'Name unknow'
        try:
            tmpdict["model"] = deal_str(cpu.Name)
        except:
            tmpdict["model"] = 'model unknow'
        tmpdict['systemName'] = deal_str(cpu.SystemName)
        try:
            tmpdict["sizeValue"] = deal_str('%score' % cpu.NumberOfCores)
        except:
            tmpdict["sizeValue"] = 'core unknow'
        try:
            tmpdict["Manufacturer"] = deal_str(cpu.Manufacturer)
        except:
            tmpdict["Manufacturer"] = 'Manufacturer unknow'
        tmpdict['hardType'] = 'cpu'
        try:
            tmpdict["SerialNumber"] = deal_str(cpu.ProcessorId.strip())
            SerialNumber_dict[ tmpdict["SerialNumber"] ] = tmpdict
        except:
            tmpdict["SerialNumber"] = None
            Name_list.append(tmpdict)
    return  SerialNumber_dict, Name_list 




def get_mainboard(c):
    SerialNumber_dict = {}
    for board_id in c.Win32_BaseBoard():
        tmpmsg = {}
        tmpmsg['mainboardId'] = board_id.SerialNumber
        tmpmsg['SerialNumber'] = board_id.SerialNumber
        try:
            tmpmsg['Name'] = deal_str(board_id.Name)
        except:
            tmpmsg['Name'] = 'name unknow'
        try:
            tmpmsg['model'] = deal_str(board_id.Product)
        except:
            tmpmsg['model'] = 'model unknow'
        try:
            tmpmsg['Manufacturer'] = deal_str(board_id.Manufacturer)
        except:
            tmpmsg['Manufacturer'] = 'Manufacturer unknow'
        try:
            tmpmsg['sizeValue'] = deal_str('version:%s' % board_id.version)
        except:
            tmpmsg['sizeValue'] = 'version:unknow'
        tmpmsg['hardType'] = 'mainboard'
        SerialNumber_dict[ tmpmsg['SerialNumber'] ] = tmpmsg
    return SerialNumber_dict,[]


def get_bios(c,mainboardId):
    SerialNumber_dict = {}
    Name_list = []
    for bios_id in c.Win32_BIOS():
        tmpmsg = {}
        tmpmsg['mainboardId'] = mainboardId
        try:
            tmpmsg['Name'] = deal_str(bios_id.Name)
        except:
            tmpmsg['Name'] = 'bios name unknow'
        try:
            tmpmsg['model'] = deal_str('version: %s' % bios_id.Version)
        except:
            tmpmsg['model'] = 'bios version unknow'
        try: 
            tmpmsg['Manufacturer'] = deal_str('bios Manufacturer: %s' % bios_id.Manufacturer.strip())
        except:
            tmpmsg['Manufacturer'] = 'bios Manufacturer'
        try:
            tmpmsg['sizeValue'] = deal_str('SMBIOSBIOSVersion: %s' % bios_id.SMBIOSBIOSVersion)
        except:
            tmpmsg['sizeValue'] = 'SMBIOSBIOSVersion unknow'
        tmpmsg['hardType'] = 'bios version'
        try:
            tmpmsg['SerialNumber'] = deal_str(bios_id.SerialNumber)
            SerialNumber_dict[ tmpmsg['SerialNumber'] ] = tmpmsg
        except:
            tmpmsg['SerialNumber'] = None
            Name_list.append(tmpmsg)
    return SerialNumber_dict,Name_list



def get_Disk(c,mainboardId):
    SerialNumber_dict = {}
    Name_list = []
    for disk in c.Win32_DiskDrive():
        tmpmsg = {}
        tmpmsg['mainboardId'] = mainboardId
        try:
            tmpmsg['Name'] = deal_str(disk.model)
        except:
            tmpmsg['Name'] = 'model unknow'
        try:
            tmpmsg['model'] = deal_str(disk.Caption)
        except:
            tmpmsg['model'] =  'caption unknow'
        try:
            tmpmsg['Manufacturer'] = deal_str(disk.Manufacturer)
        except:
            tmpmsg['Manufacturer'] = 'Manufacturer unknow'
        try:
            tmpmsg['sizeValue'] = deal_str('disk:%s' % disk.Size)
        except:
            tmpmsg['sizeValue'] = 'size unknow'
        tmpmsg['hardType'] = 'disk'
        try:
            tmpmsg['SerialNumber'] = deal_str(disk.SerialNumber.strip())
            SerialNumber_dict[ tmpmsg['SerialNumber'] ] = tmpmsg
        except:
            tmpmsg['SerialNumber'] = None
            Name_list.append(tmpmsg)
    return SerialNumber_dict,Name_list



def get_PhysicalMemory(c,mainboardId):
    SerialNumber_dict = {}
    Name_list = []
    for mem in c.Win32_PhysicalMemory():
        tmpmsg = {}
        tmpmsg['mainboardId'] = mainboardId
        try:
            tmpmsg['Name'] = deal_str(mem.Model)
        except:
            tmpmsg['Name'] = 'Name Model'
        try:
            tmpmsg['model'] = deal_str(mem.PartNumber)
        except:
            tmpmsg['model'] = 'PartNumber unknow'
        try:
            tmpmsg['Manufacturer']   = deal_str(mem.Manufacturer)
        except:
            tmpmsg['Manufacturer']   = 'Manufacturer unknow'
        try:
            tmpmsg['sizeValue'] = deal_str('memSize:%s' % mem.Capacity) #size kb)
        except:
            tmpmsg['sizeValue'] = 'size unknow'
        tmpmsg['hardType'] = 'memory'
        try:
            tmpmsg['SerialNumber'] = deal_str(mem.SerialNumber.strip())
            SerialNumber_dict[ tmpmsg['SerialNumber'] ] = tmpmsg
        except:
            tmpmsg['SerialNumber'] = None
            Name_list.append(tmpmsg)
    return SerialNumber_dict,Name_list

      
def get_MacAddress(c,mainboardId):
    SerialNumber_dict = {}
    Name_list = []
    for n in  c.Win32_NetworkAdapter():
        mactmp = n.MACAddress
        if mactmp and len(mactmp.strip()) > 5:
            tmpmsg = {}
            tmpmsg['mainboardId'] = mainboardId
            tmpmsg['SerialNumber'] ='%s' % mactmp.lower().replace(':','')
            tmpmsg['Name']  = deal_str(n.Name)
            tmpmsg['model'] = deal_str('AdapterType:%s' % n.AdapterType)
            tmpmsg['Manufacturer'] = deal_str('%s' % n.Manufacturer)
            tmpmsg['sizeValue'] = deal_str('DeviceID:%s' % n.DeviceID)
            tmpmsg['hardType'] = 'Adapter'
            SerialNumber_dict[ tmpmsg['SerialNumber'] ] = tmpmsg
    return SerialNumber_dict,Name_list



     
def get_video(c,mainboardId):
    SerialNumber_dict = {}
    Name_list = []
    for v in c.Win32_VideoController():  
        tmpmsg = {}
        tmpmsg['mainboardId'] = mainboardId
        tmpmsg['Name'] = deal_str(v.name)
        try:
            tmpmsg['model'] = deal_str(v.Model)
        except:
            tmpmsg['model'] = 'model unknow'
        tmpmsg['Manufacturer'] = None
        tmpmsg['sizeValue'] = deal_str('AdapterRAM:%s' % v.AdapterRAM)
        tmpmsg['hardType']  = 'video'
        tmpmsg['SerialNumber'] = None
        Name_list.append(tmpmsg)
    return SerialNumber_dict,Name_list



def get_hard_info(c):
    SerialNumber_dict = {}
    Name_list = []
    SerialNumber,Name = get_mainboard(c)
    for key,value in SerialNumber.items():
        SerialNumber_dict[key] = value
    mainboardId=key
    SerialNumber,Name = get_cpu(c,mainboardId)
    if SerialNumber:
        for key,value in SerialNumber.items():
            SerialNumber_dict[key] = value
    if Name:
        Name_list = Name_list + Name
    SerialNumber,Name = get_bios(c,mainboardId)
    if SerialNumber:
        for key,value in SerialNumber.items():
            SerialNumber_dict[key] = value
    if Name:
        Name_list = Name_list + Name
    SerialNumber,Name = get_Disk(c,mainboardId)
    if SerialNumber:
        for key,value in SerialNumber.items():
            SerialNumber_dict[key] = value
    if Name:
        Name_list = Name_list + Name
    SerialNumber,Name = get_PhysicalMemory(c,mainboardId)
    if SerialNumber:
        for key,value in SerialNumber.items():
            SerialNumber_dict[key] = value
    if Name:
        Name_list = Name_list + Name
    SerialNumber,Name = get_MacAddress(c,mainboardId)
    if SerialNumber:
        for key,value in SerialNumber.items():
            SerialNumber_dict[key] = value
    if Name:
        Name_list = Name_list + Name
    SerialNumber,Name = get_video(c,mainboardId)
    if SerialNumber:
        for key,value in SerialNumber.items():
            SerialNumber_dict[key] = value
    if Name:
        Name_list = Name_list + Name
    return SerialNumber_dict,Name_list


########################### deal computersystem ######################

def get_ComputerOperationSystem(c,mainboardId):
    """wmic path Win32_OperatingSystem"""
    retV = {}
    retV['mainboardId'] = mainboardId
    os = c.Win32_OperatingSystem()[0]
    retV['OS']        = deal_str('%s' % os.Caption)               #Microsoft Windows 7 Professional'
    retV['CSDVersion']     = deal_str('%s' % os.CSDVersion)            #Service Pack 1
    retV['OSLanguage']     = deal_str('%s' % os.OSLanguage)            #1033,int
    retV['SerialNumber']=    deal_str('%s' % os.SerialNumber)             #00371-OEM-8992671-00524
    retV['InstallDate'] =    deal_str('%s' % os.InstallDate)              #20170720095230.000000+480
    retV['OSArchitecture'] = deal_str('%s' % os.OSArchitecture)        #64-bit
    computer = c.win32_computersystem()[0]
    retV['computerName'] = deal_str('%s' % computer.Name)
    try:
        retV['Manufacturer'] = deal_str('%s' % computer.Manufacturer.strip())      #'OptiPlex 380
    except:
        retV['Manufacturer'] = 'unknow Manufacturer'
    try:
        retV['Model']        = deal_str('%s' % computer.Model.strip()) 
    except:
        retV['Model']        = 'unknow Model'
    try:
        retV['NumberOfProcessors'] = deal_str('%s' % computer.NumberOfProcessors)   # 0
    except:
        retV['NumberOfProcessors'] = 'unknow NumberOfProcessors'
    try:
        retV['PowerState']         = deal_str('%s' % computer.PowerState)           # 0
    except:
        retV['PowerState']         = 'unknow PowerState'
    retV['TotalPhysicalMemory']= deal_str('%s' % computer.TotalPhysicalMemory)  # 0
    return retV



################  start  computersystem ##################################
def sq_lComputerSystem(mainboardId,conn,cursor):
    sqlStr  = "select id,InstallDate,computerName from switch_computersystem where mainboardId='%s'"
    number = cursor.execute(sqlStr  % mainboardId )
    if number == 0:
        return None
    else:
        retV = {}
        retV['id'],retV['InstallDate'],retV['computerName'] = cursor.fetchone()
        return retV


def deal_ComputerSystem(c,mainboardId,conn,cursor):
    v = get_ComputerOperationSystem(c,mainboardId)
    retV = sq_lComputerSystem(mainboardId,conn,cursor)
    install_strSql = "insert into switch_computersystem"\
                 " (mainboardId,OS,CSDVersion,OSLanguage,SerialNumber"\
                 " ,InstallDate,OSArchitecture,computerName,Manufacturer"\
                 "  ,Model,NumberOfProcessors,PowerState,TotalPhysicalMemory,created)"\
                 "  values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') " % \
                   (v['mainboardId'],v['OS'],v['CSDVersion'],v['OSLanguage'],v['SerialNumber'],\
                    v['InstallDate'],v['OSArchitecture'],v['computerName'],v['Manufacturer'],\
                    v['Model'],v['NumberOfProcessors'],v['PowerState'],v['TotalPhysicalMemory'],datetime.now())
    if retV:
        update_strSql = "update switch_computersystem set mainboardId='%s',OS='%s',CSDVersion='%s',OSLanguage='%s',SerialNumber='%s'"\
                    ",InstallDate='%s',OSArchitecture='%s',computerName='%s',Manufacturer='%s'"\
                    ",Model='%s',NumberOfProcessors='%s',PowerState='%s',TotalPhysicalMemory='%s',created='%s' where id='%d'" %\
                    (v['mainboardId'],v['OS'],v['CSDVersion'],v['OSLanguage'],v['SerialNumber'],\
                    v['InstallDate'],v['OSArchitecture'],v['computerName'],v['Manufacturer'],\
                    v['Model'],v['NumberOfProcessors'],v['PowerState'],v['TotalPhysicalMemory'],datetime.now(),retV['id'])
        if retV['InstallDate'] != v['InstallDate']:
            logStr = "mainboardId:%s os reinstall os: %s" % (mainboardId,v['OS'])
            install_log_strSql = "insert into switch_computerlog (mainboardId,mothed,logStr,created) values ('%s','%s','%s','%s')" % \
                                                                 (mainboardId,'reinstall os',logStr,datetime.now())
            cursor.execute(update_strSql)
            cursor.execute(install_log_strSql)
            conn.commit()
        elif retV['computerName'] != v['computerName']:
            logStr = "mainboardId:%s change computer name: %s" % (mainboardId,v['computerName'])
            install_log_strSql = "insert into switch_computerlog (mainboardId,mothed,logStr,created) values ('%s','%s','%s','%s')" % \
                                                                 (mainboardId,'change computer name',logStr,datetime.now())
            cursor.execute(update_strSql)
            cursor.execute(install_log_strSql)
            conn.commit()
    else:
        cursor.execute(install_strSql)
        conn.commit()
################end computersystem##################################


################start install##################################
def _get_install(key,sub_key,mainboardId):
    openkey = winreg.OpenKey(key,sub_key)
    key_number = winreg.QueryInfoKey(openkey)[0]
    Uninstall = {}
    for i in range(key_number):
        D = {}
        tmp = winreg.EnumKey(openkey,i)
        tmp_sub_key = '%s\\%s'% (sub_key,tmp)
        tmp_openkey = winreg.OpenKey(key,tmp_sub_key)
        try:
            D['mainboardId'] = mainboardId
            Name = deal_str('%s' % winreg.QueryValueEx(tmp_openkey,'DisplayName')[0])
            D['DisplayName'] = Name
            try:
                D['DisplayVersion'] = deal_str('%s' % winreg.QueryValueEx(tmp_openkey,'DisplayVersion')[0])
            except:
                D['DisplayVersion']= ''
            try:
                D['InstallDate'] = deal_str('%s' % winreg.QueryValueEx(tmp_openkey,'InstallDate')[0])
            except:
                D['InstallDate'] = ''
            Uninstall[Name] = D
        except:
            pass
    return Uninstall



def get_install_from_regedit(c):
    install = {}
    regkey=winreg.HKEY_LOCAL_MACHINE
    sub_key1 = r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall'
    sub_key2 = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'
    sub_key3 = r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths'
    ret_install = _get_install(regkey,sub_key1,mainboardId)
    for key in ret_install.keys():
        try:
            tmp = install[key]
        except:
            install[key]=ret_install[key]
    ret_install = _get_install(regkey,sub_key2,mainboardId)
    for key in ret_install.keys():
        try:
            tmp = install[key]
        except:
            install[key]=ret_install[key]
    ret_install = _get_install(regkey,sub_key3,mainboardId)
    for key in ret_install.keys():
        try:
            tmp = install[key]
        except:
            install[key]=ret_install[key]
    return install
         


def deal_install_from_regedit(c,mainboardId,conn,cursor):
    now = datetime.now()
    D = get_install_from_regedit(c)    
    sqlSql = "select id,mainboardId,DisplayName,DisplayVersion,InstallDate from switch_install where mainboardId='%s'" % mainboardId
    number = cursor.execute(sqlSql)
    if number == 0:
        for key,value in D.items():
            install_strSql = "insert into switch_install ( mainboardId,DisplayName,DisplayVersion,InstallDate,created ) values ('%s','%s','%s','%s','%s') " %\
                ( value['mainboardId'],value['DisplayName'],value['DisplayVersion'],value['InstallDate'],now)
            cursor.execute(install_strSql)
    else:
        sqlD = {};new_list = []; delete_list = [] 
        datas = cursor.fetchall()
        for data in datas:
            tmp = {}
            tmp['id'] = data[0]
            tmp['mainboardId'] = data[1]
            tmp['DisplayName'] = data[2]
            tmp['DisplayVersion'] = data[3]
            tmp['InstallDate'] = data[4]
            sqlD[ tmp['DisplayName'] ] = tmp
        D_keys =[key for key in D.keys() ]
        sqlD_keys = [ key for key in sqlD.keys() ]
        for key in D_keys:
            if key not in sqlD_keys:
                new_list.append( D[key] )
            else:
                D_DisplayVersion = D[key]['DisplayVersion']
                sqlD_DisplayVersion = sqlD[key]['DisplayVersion']
                if D_DisplayVersion != sqlD_DisplayVersion:
                    new_list.append( D[key] )
                    delete_list.append( sqlD[key] )   
        for key  in sqlD_keys:
            if key not in D_keys:
                delete_list.append( sqlD[key] )
        #first exec delete,then exec insta into
        for delete in delete_list:
            strSql = "delete from switch_install where id='%d'" %  delete['id']
            cursor.execute(strSql)
            logStr = "mainboardId:***%s*** delete product name***%s*** version***%s***" % \
                     (mainboardId,delete['DisplayName'],delete['DisplayVersion'])
            install_log_strSql = "insert into switch_computerlog (mainboardId,mothed,logStr,created) values ('%s','%s','%s','%s')" % \
                                                                 (mainboardId,'Delete or Update product',logStr,now)
            cursor.execute(install_log_strSql)
        for i in new_list:
            install_strSql = "insert into switch_install ( mainboardId,DisplayName,DisplayVersion,InstallDate,created) values ('%s','%s','%s','%s','%s')" %\
                ( i['mainboardId'],i['DisplayName'],i['DisplayVersion'],i['InstallDate'],now)
            cursor.execute(install_strSql)
            logStr = "mainboardId***%s*** install product name: ***%s*** version***%s***" % \
                     (mainboardId,i['DisplayName'],i['DisplayVersion'])
            install_log_strSql = "insert into switch_computerlog (mainboardId,mothed,logStr,created) values ('%s','%s','%s','%s')" % \
                                                                 (mainboardId,'new install or Update product',logStr,now)
            cursor.execute(install_log_strSql)
    conn.commit()

################end install################################## 
def deal_sql_data(data):
    SerialNumber_dict = {}
    Name_list         = []
    for row in data:
        if row:
            tmp= {}
            tmp['id']           = row[0]
            tmp['SerialNumber'] = row[2]
            tmp['Name']         = row[3]
            if row[2] == 'None':
                Name_list.append(tmp)
            else:   
                SerialNumber_dict[row[2]] = tmp
    return SerialNumber_dict, Name_list
   

            
def search_hardware(mainboardid,conn,cursor):
    strSql = "select id,mainboardId,SerialNumber,Name,model,Manufacturer,sizeValue,hardType,created from switch_hardware where mainboardId = '%s'" % mainboardid
    row_count = cursor.execute(strSql)
    SerialNumber_dict = {}
    Name_list         = []
    if row_count > 0:
        data = cursor.fetchall()
        SerialNumber_dict,Name_list = deal_sql_data(data)
    return SerialNumber_dict,Name_list

    

def connect(host,user,password,db):
    try:
        conn = pymysql.connect(host,user,password,db)
        cursor = conn.cursor()
        return conn,cursor
    except:
        sys.exit(1)  



def deal_hardware(c,conn,cursor):
    install_list = [];delete_dict = {};log_list=[]
    get_SerialNumber_dict, get_Name_list = get_hard_info(c)
    #SerialNumber,Name = get_mainboard(c)
    search_SerialNumber_dict, search_Name_list = search_hardware(mainboardId,conn,cursor)
    tmpList = [ name for name in search_Name_list ]
    # require install hardware,make install list
    get_hard_keys = get_SerialNumber_dict.keys()
    search_hard_keys = search_SerialNumber_dict.keys()
    for key in get_hard_keys :
        if key not in search_hard_keys:
            logStr = "Name:%s SerialNumber:%s" % (get_SerialNumber_dict[key]['Name'],get_SerialNumber_dict[key]['SerialNumber'])
            log = [mainboardId,'install',logStr]
            log_list.append(log)
            install_list.append( get_SerialNumber_dict[key])
    for key in search_hard_keys:
        if not key in get_hard_keys:
            id = search_SerialNumber_dict[key]['id']
            delete_dict[id] = search_SerialNumber_dict[key]
            logStr = "Name:%s SerialNumber:%s" % (delete_dict[id]['Name'],delete_dict[id]['SerialNumber'])
            log = [mainboardId,'delete',logStr]
            log_list.append(log)
    for hardware in get_Name_list:
        name = hardware['Name']
        flag = None
        for t in tmpList:
            if ( not flag ) and t['Name'] == name :
                flag = True
                tmpList.pop()
        if not flag:
            install_list.append(hardware)
            logStr = "Name:%s SerialNumber:%s" % (hardware['Name'],hardware['SerialNumber'])
            log = [mainboardId,'install',logStr]
            log_list.append(log)
    if len(tmpList) > 0 :
        for t in tmpList:
            id = t['id']
            delete_dict[id] = t
            if t['Name']:         t['Name'] = re.sub(pattern,'',t['Name'])
            if t['SerialNumber']: t['SerialNumber'] = re.sub(t['SerialNumber'],'',t['SerialNumber'])
            logStr = "Name:%s SerialNumber:%s" % (t['Name'],t['SerialNumber'])
            log = [mainboardId,'delete',logStr]
            log_list.append(log)  
    return  install_list ,delete_dict ,log_list       
                 
           
    
def write_hardware(install_list, delete_dict,log_list,conn,cursor):
    now = datetime.now()
    for install in install_list:
        if install['mainboardId']:  install['mainboardId'] = re.sub(pattern,'',install['mainboardId'])
        if install['SerialNumber']: install['SerialNumber'] = re.sub(pattern,'',install['SerialNumber'])
        if install['Name']:         install['Name'] = re.sub(pattern,'',install['Name']) 
        if install['model']:        install['model'] = re.sub(pattern,'',install['model'])
        if install['Manufacturer']: install['Manufacturer'] = re.sub(pattern,'',install['Manufacturer'])
        if install['sizeValue']:    install['sizeValue'] = re.sub(pattern,'',install['sizeValue'])
        strSql = "insert into switch_hardware ( mainboardId, SerialNumber, Name, Model ,Manufacturer, sizeValue, hardType, created) values ('%s','%s','%s','%s','%s','%s','%s','%s')" % 
			(install['mainboardId'],install['SerialNumber'],install['Name'],install['model'], install['Manufacturer'],install['sizeValue'],install['hardType'],now)
        cursor.execute(strSql)
    for id in delete_dict.keys():
        strSql = "DELETE FROM switch_hardware WHERE id = %d" 
        cursor.execute(strSql % id)
    for log in log_list:
        strSql = "insert into switch_computerlog (mainboardId,mothed,logStr,created) values ('%s','%s','%s','%s')" % (log[0],log[1],log[2],now)
        cursor.execute(strSql)
    conn.commit()
    
def main(c):
    kwargs={}
    opts,args = getopt.getopt(sys.argv[1:],'h:u:p:d:',['host','user','password','db'])
    host=None;user=None;password=None;db=None
    for name,value in opts:
        if name in ('-h','host'):
            host = value

        if name in ('-u','user'):
            user = value

        if name in ('-p','password'):
            password = value

        if name in ('-d','db'):
            db     = value
 
 
    if not host:     print('pls input argv: -h ');sys.exit(1)
    if not user:     print('pls input argv: -u ');sys.exit(1)
    if not password: print('pls input argv: -p ');sys.exit(1)
    if not db:       print('pls input argv: -d ');sys.exit(1)



    conn,cursor = connect(host,user,password,db)
    install_list, delete_dict,log_list = deal_hardware(c,conn,cursor)
    write_hardware(install_list, delete_dict,log_list,conn,cursor)

    deal_ComputerSystem(c,mainboardId,conn,cursor)
    
    deal_install_from_regedit(c,mainboardId,conn,cursor)
    print("adsfadfasddfadf")
    conn.close()
    sys.exit(1)

if __name__ == '__main__':
    main(c)
