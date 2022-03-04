import subprocess
import re
import socket

def is_valid_ip(ip):
    m = re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", ip)
    return bool(m) and all(map(lambda n: 0 <= int(n) <= 255, m.groups()))

def check_MAC(x):
    return re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", x.lower())
    

def split(paragraph):
    """ ugly, but faster """
    interfaces = paragraph.split(" Link ")
    interface = interfaces[0]
    lines = paragraph.split("\n")
    mac = lines[0].split(' HWaddr ')[-1].strip()
    inet_mask = lines[1].split(':')
    ip, mask = inet_mask[1].split(' ')[0], inet_mask[-1].split(' ')[0]
    return [interface.strip(), ip, mask, mac]

valid_interfaces = {"enp2s0": 1, "wlp1s0": 1, "wlan0": 1}


def test_split():
    p = subprocess.Popen(["ifconfig"], stdout=subprocess.PIPE)

    if_config_output = p.communicate()[0].decode('utf-8')
    c = []
    paragraphs = if_config_output.split('\n\n')[:-1]
    # print(len(paragraphs))
    for paragraph in paragraphs:
        res = split(paragraph)
        if check_MAC(res[-1]) and is_valid_ip(res[1]) and res[0] in valid_interfaces:
            c.append(split(paragraph))
    return c

def cidr(netmask):
    return sum(bin(int(x)).count('1') for x in netmask.split('.'))

def network_cidr_notation(ip, netmask):
    net_ = cidr(netmask)
    net = net_
    ip_cs = ip.split('.')
    network_address = []
    for ip_c in ip_cs:
        if net < 8:
            zeros = net
            op, el = 0, 7
            while zeros > 0:
                op += (1 << el)
                el -= 1
                zeros -= 1
            network_address.append(int(ip_c) & op)
        else:
            network_address.append(int(ip_c))
        net -= 8
    return ".".join(list(map(str, network_address))) + "/" + str(net_)

def run_nmap(network_address):
    mac_to_ip = {}
    p = subprocess.Popen(["sudo", "nmap", "-sP", network_address], stdout=subprocess.PIPE)

    nmap_output = p.communicate()[0].decode('utf-8').split('\n')
    for i in range(2, len(nmap_output) - 1, 3):
        ip = nmap_output[i].split(' ')[-1]
        mac = nmap_output[i + 2].split(' ')[2].strip()
        if check_MAC(mac):
            mac_to_ip[mac] = ip
    # print(nmap_output)
    return mac_to_ip


def scan_wifi():
    interfaces = test_split()
    for interface in interfaces:
        # print(interface[0], interface[1])
        # print(cidr_notation(interface[2]))
        if 'wlp1s' in str(interface[0]) or 'wlan' in str(interface[0]):
            net = network_cidr_notation(interface[1], interface[2])
            return run_nmap(net), interface[1]
    return {}, None




PREDEFINED_PORT = 7890

def broadcastMasterIP():
    print("Scanning WIFI...")
    others, master = scan_wifi()

    # TODO: Remove this line
    others['58:fb:84:9b:a7:3a'] = master

    newDrones = []
    print("WIFI scan complete", len(others.keys()), "found")
    for other in others.keys():
        s = socket.socket()
        s.settimeout(5.0)
        try:
            s.connect((str(others[other]), PREDEFINED_PORT)) 
            # broadcast master ip address to drones 
            s.send(master)
            # TODO: Register drone in database
            newDrones.append({'mac': other, 'ip': others[other]})
            print("Drone found on " + others[other])
        except:
            print("Connection to " + str(others[other]) + " failed")
    return newDrones
# broadcastMasterIP()