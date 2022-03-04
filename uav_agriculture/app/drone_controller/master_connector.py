import socket
import json
import subprocess
import re


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

def accept_master():
    interfaces = test_split()
    # TODO: Get your ip address here
    # HOST = "127.0.0.1"
    HOST = str(interfaces[0][1])
    PORT = 7890

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    print("Server waiting for connections...")
    s.listen(4)
    conn, addr = s.accept()
    print('Connected by', addr)
    master = conn.recv(2048)
    master = master.decode('utf-8')
    with open('master.json', "w") as f:
        f.write(json.dumps({'ip': master}))
    conn.close()
    s.close()

accept_master()