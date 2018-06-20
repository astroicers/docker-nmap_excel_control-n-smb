import Queue
import threading
import time
import nmap
import requests
from openpyxl import Workbook
from pymongo import MongoClient
from argparse import ArgumentParser
import sys


def py_nse(target, nse_name):
    target = target
    port = nse[nse_name]['port']
    argument = nse[nse_name]['argument']
    nse_name = nse_name
    jp = nse[nse_name]['jp']
    hack = '0'
    nm = nmap.PortScanner()
    data = nm.scan(hosts=target, ports=str(port),
                   arguments=argument)

    try:
        mon.toybox.nse_list.insert_one({'_id': target})
    except:
        pass

    if jp in str(data):
        hack = '1'
        print '%s have %s !!' % (target, nse_name,)

    mon.toybox.nse_list.update(
        {'_id': target, },
        {'$set': {
            ('vuln.%s' % nse_name): {
                'hack': hack,
                'time_pc': str(time.time()),
                'time_man': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            }
        }
        })
    print '%s data updated' % target


def cut_net_mask_range(input_ip):
    t_list = []
    ip = a.split('.')[0] + '.' + a.split('.')[1] + '.'+a.split('.')[2] + '.'
    head_num = int(a.split('.')[3].split('-')[0])
    feet_num = int(a.split('.')[3].split('-')[1])
    for x in range(head_num, feet_num + 1):
        t_list.append(ip + str(x))
    return t_list


def cut_net_mask(input_ip):
    target = input_ip.split('/')[0]
    mask = input_ip.split('/')[1]
    print target, mask
    answer = []
    target = target.split('.')
    #print target
    temp = str()
    for x in target:
        x = int(x)
        x = bin(x)
        x = str(x).lstrip('0b')
        while len(x) < 8:
            x = '0' + x
        temp = temp + x
    #print temp
    #print temp[0:int(mask)] + 'x'*(32 - int(mask))
    #print int('1'*(32 - int(mask)), 2)
    #print 2 ** (32 - int(mask)) - 1
    top = 0b0
    all = str()

    while top < int('1'*(32 - int(mask)), 2):
        y = bin(top)
        y = str(y).lstrip('0b')
        while len(y) < (32 - int(mask)):
            y = '0' + y
            #print y
        all = temp[0:int(mask)] + y
        #print temp[0:int(mask)] + y
        top += 0b1

        ip1 = all[0:8]
        ip2 = all[8:16]
        ip3 = all[16:24]
        ip4 = all[24:32]
        answer.append(str(int(ip1, 2)) + '.' + str(int(ip2, 2)) +
                      '.' + str(int(ip3, 2)) + '.' + str(int(ip4, 2)))
    return answer


def post_to_mongo(ip, port, data):
    data['ip'] = ip
    data['port'] = str(port)
    _id = ip + "_" + str(port)
    data['_id'] = _id
    #print data
    mon.toybox.ip_list.insert_one(data)
    print '%s data posted' % ip
    return data


def update_to_mongo(ip, port, data):
    data['ip'] = ip
    data['port'] = str(port)
    _id = ip + "_" + str(port)
    #print data
    mon.toybox.ip_list.update({'_id': _id}, data)
    print '%s data updated' % ip
    return data


def py_scan(target):
    global scanned
    print 'open hosts: %s' % scanned
    num2 = 0
    print 'scanning %s' % target
    try:
        nm = nmap.PortScanner()
        nm.scan(hosts=target, ports='1-1000,1433,3306,3389,4786,8080-8100',
                arguments=Narg, sudo=False)
        print nm.command_line()
        for port in nm[target]['tcp'].keys():
            #print nm[target]['tcp'][port]
            if nm[target]['tcp'][port]['state'] != 'closed':
                data_temp = {}
                try:
                    data_temp = post_to_mongo(
                        target, port, nm[target]['tcp'][port])
                except:
                    data_temp = update_to_mongo(
                        target, port, nm[target]['tcp'][port])
                print data_temp
                num2 += 1
    except:
        print 'scanning %s error!' % target


def process_data(threadName, q):
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            target = q.get()
            queueLock.release()
            print "%s processing %s" % (threadName, target) + '\n'
            ##---------------------##
            py_scan(target)
            py_nse(target, 'ms17-010')
            py_nse(target, 'ms08-067')
            py_nse(target, 'ms12-020')
            ##---------------------##
        else:
            queueLock.release()
        # time.sleep(1)


class myThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q

    def run(self):
        #print "Starting " + self.name + '\n'
        process_data(self.name, self.q)
        #print "Exiting " + self.name + '\n'


if __name__ == "__main__":
    print '#######################[Initialization Data]#######################'
    scanned = 0
    exitFlag = 0
    threads = 1
    mongo_admin = 'root'
    mongo_pass = 'example'
    database = 'toybox'
    collection = ['ip_list', 'nse_list']
    Narg = '-A -v '
    file_path = ''
    ip_arg = ''
    target_list = []
    nse = {
        'ms17-010': {
            'port': '445',
            'argument': '--script smb-vuln-ms17-010',
            'jp': 'Risk factor: HIGH',
        },
        'ms08-067': {
            'port': '445',
            'argument': '--script smb-vuln-ms08-067',
            'jp': '(MS08-067)',
        },
        'ms12-020': {
            'port': '3389',
            'argument': '-sV --script=rdp-vuln-ms12-020',
            'jp': 'Risk factor: Medium',
        }
    }
    parser = ArgumentParser()
    parser = ArgumentParser(prog=sys.argv[0])
    parser = ArgumentParser(usage="usage")
    parser = ArgumentParser(description='''
        Ke : https://github.com/playerKe0402........................................
        Toy : https://github.com/box02200059........................................
        Sean : https://github.com/astroicers........................................
    ''')
    parser.add_argument('-t,', metavar='--threads', help='number of threads')
    parser.add_argument('-l,', metavar='--list', help='ip list file path')
    parser.add_argument('-i,', metavar='--ip', help='one ip')
    #parser.add_argument('-N,', metavar='--Narg', help='nmap argument')

    if len(sys.argv) > 6:
        parser.print_help()
        sys.exit()

    print '#######################[Get Argument]#######################'
    for a, b in enumerate(sys.argv):
        try:
            if b == '-t' or b == '--threads':
                if sys.argv[a+1] >= 1 and sys.argv[a+1] <= 64:
                    threads = sys.argv[a+1]
        except:
            parser.print_help()
            sys.exit()
    print 'Threads : %s' % threads
    # for a, b in enumerate(sys.argv):
    #    try:
    #        if b == '-n' or b == '--Narg':
    #            Narg = sys.argv[a+1]
    #        else:
    #            Narg = '-A -v '
    #    except:
    #        parser.print_help()

    for a, b in enumerate(sys.argv):
        try:
            if b == '-l' or b == '--list':
                file_path = sys.argv[a+1]
                print 'File_path : %s' % file_path
            elif b == '-i' or b == '--ip':
                ip_arg = sys.argv[a+1]
                print 'ip : %s' % ip_arg
        except:
            parser.print_help()
            sys.exit()

    print '#######################[Confirm target]#######################'
    if '-l' in sys.argv or '--list' in sys.argv:
        try:
            f = open(file_path, 'r')
            lines = f.readlines()
            for line in lines:
                line = line.rstrip('\r\n')
                if '/' in line:
                    for x in cut_net_mask(line):
                        target_list.append(x)
                elif '-' in line:
                    for x in cut_net_mask_range(line):
                        target_list.append(x)
                else:
                    target_list.append(line)
            f.close()
        except:
            print 'Error:Check your file path.'
            sys.exit()
    elif '-i' in sys.argv or '--ip' in sys.argv:
        try:
            line = ip_arg
            if '/' in line:
                for x in cut_net_mask(line):
                    target_list.append(x)
            elif '-' in line:
                for x in cut_net_mask_range(line):
                    target_list.append(x)
            else:
                target_list.append(line)
        except:
            print 'Error:Check your ip format.'
            sys.exit()
    else:
        parser.print_help()
        sys.exit()

    print '#######################[Connect MongoDB]#######################'
    try:
        mon = MongoClient('mongodb://'+mongo_admin +
                          ':' + mongo_pass + '@127.0.0.1')
    except:
        print 'Error: Connect mongodb fail.'
        sys.exit()
    try:

        mon[database][collection[0]].insert_one({"_id": 'Ke_Sean_Toy'})
        mon[database][collection[0]].remove({"_id": 'Ke_Sean_Toy'})
        print 'Create database : %s' % database
        print 'Create collection : %s' % collection[0]
    except:
        pass
    try:

        mon[database][collection[1]].insert_one({"_id": 'Ke_Sean_Toy'})
        mon[database][collection[1]].remove({"_id": 'Ke_Sean_Toy'})
        print 'Create database : %s' % database
        print 'Create collection : %s' % collection[1]
    except:
        pass
    print '#######################[Scanning...]#######################'
    threadList = []
    for i in range(0, threads):
        threadList.append("Thread-%s" % (i+1))
    queueLock = threading.Lock()
    workQueue = Queue.Queue()
    threads = []
    threadID = 1

    # Create new Tread
    for tName in threadList:
        thread = myThread(threadID, tName, workQueue)
        thread.start()
        threads.append(thread)
        threadID += 1

    # Fill Queue
    queueLock.acquire()
    for word in target_list:
        workQueue.put(word)
    queueLock.release()

    # Wait Queue empty
    while not workQueue.empty():
        pass

    exitFlag = 1

    # Wait all thread finished
    for t in threads:
        t.join()
    print '#######################[Finish]#######################'
