import requests
from bs4 import BeautifulSoup
import nmap
import time


def parser():
    show_html = requests.get('http://127.0.0.1/show.php')
    soup = BeautifulSoup(show_html.text, 'html.parser')

    x_port = []
    x_ip = []
    for a in soup.find_all(id="port"):
        x_port.append(a.text)
    for a in soup.find_all(id="ip_address"):
        x_ip.append(a.text)
    #print x_port
    #print x_ip
    target = []
    for a, b in enumerate(x_port):
        #print a,b
        if b == "Scanning":
            target.append(a)

    for a, b in enumerate(x_ip):
        if a in target:
            target.remove(a)
            if not b in target:
                target.append(b)
    return target
    #print target


def post(ip_address, port, product, version, name, cpe, extrainfo):
    post_payload = {
        'ip_address': ip_address,
        'port': port,
        'product': product,
        'version': version,
        'name': name,
        'cpe': cpe,
        'extrainfo': extrainfo,
    }
    requests.post('http://127.0.0.1/scan.php', data=post_payload)


def post_del(target):
    post_payload = {
        'ip_address': target,
    }
    requests.post(
        'http://127.0.0.1/del_new.php', data=post_payload)


num = 0


def py_scan(target):
    global num
    print 'num = %s' % num
    num2 = 0
    print 'scanning %s' % target
    try:
        nm = nmap.PortScanner()
        nm.scan(target, '1-1000,1433,3306,3389,8080-8090', '-sS -Av')
        print nm.command_line()
        for port in range(1, 10000):
            try:
                s1 = nm[target]['tcp'][port]['product']
                s2 = nm[target]['tcp'][port]['version']
                s3 = nm[target]['tcp'][port]['name']
                s4 = nm[target]['tcp'][port]['cpe']
                s5 = nm[target]['tcp'][port]['extrainfo']
                print target, port, s1, s2, s3, s4, s5
                post_del(target)
                post(target, port, s1, s2, s3, s4, s5)
                num2 += 1
            except:
                pass
        if num2 != 0:
            num += 1
        else:
            requests.post('http://127.0.0.1/del_new.php', data={'ip_address': target})
    except:
        print 'scanning %s error!' % target


while 1:
    time.sleep(1)
    target_list = parser()
    print target_list
    for target in target_list:
        py_scan(target)
