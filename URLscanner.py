import socket
import argparse
from tqdm import tqdm
import concurrent.futures
import art
import ipaddress
import sys


#清理掉http和https
def clean_url(url):
    if url.startswith("http://"):
        url = url[7:]
    elif url.startswith("https://"):
        url = url[8:]
    return url

def get_ip_address(url):
    try:
        ip = ipaddress.ip_address(url)
        return str(ip)
    except ValueError:
        try:
            ip_address = socket.gethostbyname(url)
            return ip_address
        except socket.gaierror:
            print(f"无法解析主机名：{url}")
            sys.exit(1)


# 扫描单个端口的函数
def scan_port(ip_address,port):
    try:
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((ip_address,port))
            if result == 0:
                return  port
    except socket.error:
        pass
    return None
def scan_ports(ip_address, num_threads, min_port, max_port):
    open_ports = []
    ports_to_scan = range(min_port, max_port + 1)
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(scan_port, ip_address, port) for port in ports_to_scan]
        with tqdm(total=len(ports_to_scan), desc="扫描端口") as bar:
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                result = future.result()
                if result is not None:
                    open_ports.append(result)
                bar.update(1)
    return open_ports

# 获得端口对应的服务器名称的函数

def get_service_name(port):
    try:
        service_name = socket.getservbyport(port)
        return service_name
    except OSError:
        return "UNKnown"

def print_ascii_art():
    ascii_art = art.text2art("Zero  URLscanner")
    print(ascii_art)

if __name__ == "__main__":

    print_ascii_art()

    print("欢迎来到Zero老师写的第一个URlscanner工具")
    print("-----------------------------------------------------------")
    print("请你享用")
    print("-----------------------------------------------------------")
    print('输入-h获得提示')
    parser = argparse.ArgumentParser(description="Zero URLscanner - 作者:zzm")
    parser.add_argument("-u","--url",required=True,help="要扫描单个ip或者URl")
    parser.add_argument("-t","--threads",type=int,default=4,help="线程数(不超过700)")
    parser.add_argument("-min",type=int,default=1,help="开始扫描端口")
    parser.add_argument("-max",type=int,default=65537,help='截止的端口号')
    args = parser.parse_args()


#     限制线程不超过700
    num_threads = min(args.threads,700)
    url = args.url
    url = clean_url(url)
    host_name = url.split('/')[0]
    ip_address = get_ip_address(host_name)
    print(f"{host_name}的ip地址:{ip_address}")

    open_ports = scan_ports(ip_address, num_threads, args.min, args.max)
    print(f"\n{host_name} ({ip_address}) 的开放端口:")
    if open_ports:
        for port in open_ports:
            service_name = get_service_name(port)
            print(f"端口 {port} ({service_name}) 是开放的")
    else:
        print('没有找到开放的端口')



