import argparse
import numpy as np
from scapy.all import *

from utils import get_bytes_from_raw,get_bytes_from_raw_new
from config import *

PKT_COUNT = 0
p_header_list = []
p_payload_list = []
payload_length = []
pkt_length = []
src_ip = []
dst_ip = []
src_port = []
dst_port = []
time = []
protocol = []
flag = []
mss = []

def process(pkt):
    global PKT_COUNT, p_header_list, p_payload_list, payload_length, pkt_length, src_ip, dst_ip, src_port, dst_port, time, protocol, flag, mss
    PKT_COUNT += 1
    p_header = get_bytes_from_raw_new(pkt)
    p_payload = []
    if pkt.haslayer("Raw"):
        _, p_payload = get_bytes_from_raw(hexdump(pkt["Raw"].load, dump=True))
    
    p_header_list.append(p_header)
    p_payload_list.append(p_payload)

def pcap2npy4ISCX(dir_path_dict, save_path_dict):
    global PKT_COUNT, p_header_list, p_payload_list, payload_length, pkt_length, src_ip, dst_ip, src_port, dst_port, time, protocol, flag, mss
    for category in dir_path_dict:
        dir_path = dir_path_dict[category]
        file_list = os.listdir(dir_path)
        for file in file_list:
            if not file.endswith('.pcap'):
                continue
            p_header_list.clear()
            p_payload_list.clear()
            payload_length.clear()
            pkt_length.clear()
            src_ip.clear()
            dst_ip.clear()
            src_port.clear()
            dst_port.clear()
            time.clear()
            protocol.clear()
            flag.clear()
            mss.clear()
            PKT_COUNT = 0
            file_path = dir_path + '/' + file
            print(' {} Process Starting'.format(file_path))
            sniff(offline=file_path, prn=process, store=0)
            if not (len(p_header_list) == PKT_COUNT and len(p_payload_list) == PKT_COUNT):
                print("Error")
                raise Exception('Error')
            save_file = file[:-4] + 'npz'
            print('{} Process Saving'.format(save_path_dict[category] + '/' + save_file))
            np.savez_compressed(save_path_dict[category] + '/' + save_file,
                                header=np.array(p_header_list, dtype=object),
                                payload=np.array(p_payload_list, dtype=object),
                                payload_length=np.array(payload_length, dtype=object),
                                pkt_length=np.array(pkt_length, dtype=object),
                                src_ip=np.array(src_ip, dtype=object),
                                dst_ip=np.array(dst_ip, dtype=object),
                                src_port=np.array(src_port, dtype=object),
                                dst_port=np.array(dst_port, dtype=object),
                                time=np.array(time, dtype=object),
                                protocol=np.array(protocol, dtype=object),
                                flag=np.array(flag, dtype=object),
                                mss=np.array(mss, dtype=object))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, help="dataset", required=True)
    opt = parser.parse_args()

    if opt.dataset == 'iscx-vpn':
        config = ISCXVPNConfig()
    elif opt.dataset == 'iscx-nonvpn':
        config = ISCXNonVPNConfig()
    elif opt.dataset == 'iscx-tor':
        config = ISCXTorConfig()
    elif opt.dataset == 'iscx-nontor':
        config = ISCXNonTorConfig()
    elif opt.dataset == 'ciciot':
        config = CICIoTConfig()
    else:
        raise Exception('Dataset Error')

    pcap2npy4ISCX(dir_path_dict=config.DIR_PATH_DICT, save_path_dict=config.DIR_SAVE_DICT)

