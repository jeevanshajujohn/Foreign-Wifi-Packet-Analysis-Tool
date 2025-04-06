import csv
import os
import subprocess
import time
import argparse
from datetime import datetime

network_file_path = '/home/FPAT/reg_net.csv'
log_file_path = '/home/FPAT/'
net_max = 0
RED = '\033[31m'
GREEN = '\033[32m'
BLUE = '\033[34m'
RESET = '\033[0m'
debug_count = 0

def capture_snapshot():
    result = subprocess.run(["nmcli", "-t", "dev", "wifi"], capture_output=True, text=True)
    networks = result.stdout.split('\n')
    snapshot = []
    for network in networks[0:len(networks) - 1]:
        IPV6 = network[2:4] + network[5:8] + network[9:12] + network[13:16] + network[17:20] + network[21:24]
        parts = network.split(':')
        SSID = parts[7]
        Infra = parts[8]
        Channel = parts[9]
        signal_speed = parts[10]
        signal_strength = parts[11]
        Sec_prot = parts[13]
        net = {'IPV6': IPV6, 'SSID': SSID, 'Infrastructure': Infra, 'Channel': Channel, 'Signal Speed': signal_speed,
               'Signal Strength': signal_strength, 'Security Protocol': Sec_prot}
        snapshot.append(net)

    return snapshot

def add_all_networks():
    current = capture_snapshot()

    print(f"{GREEN}\n\nThe networks to be added will be: \n\n{RESET}")
    for i in range(len(current)):
        print(i, end="\t")
        for j in list(current[i].values()):
            print(j, end="\t")
        print()
    if input("Do you wish to continue with this list? [y/N] ") == "y":
        for j in range(len(current)):
            req = list(current[j].values())
            network_details_processing(req)
    else:
        return

def easy_network_addition():
    curr_networks = capture_snapshot()
    for i in range(len(curr_networks)):
        print(i, end='\t')
        for j in list(curr_networks[i].values()):
            print(j, end="\t")
        print()
    index = int(input("Enter the required network index: "))
    req = list(curr_networks[index].values())
    network_details_processing(req)

def network_details_processing(req):
    SSID, IPV6, Infra, Channel, Rate, Sec_prot = req[1], req[0], req[2], req[3], req[4], req[6]
    manual_network_addition(SSID, IPV6, Infra, Channel, Rate, Sec_prot)


def manual_network_addition(SSID: str, IPV6: str, Infra: str, Channel: str, Rate: str, Sec_prot: str):
    data = {'SSID': SSID, 'IPV6': IPV6, 'Infrastructure': Infra, 'Channel': Channel, 'Rate': Rate, 'Security Protocol': Sec_prot}

    try:
        os.makedirs(os.path.dirname(network_file_path), exist_ok=True)

        if os.path.isfile(network_file_path):
            with open(network_file_path, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                existing_data = [row for row in reader]
                for row in existing_data:
                    if row['IPV6'] == IPV6:
                        print("Duplicate entry found. Network not added.")
                        return

        file_exists = os.path.isfile(network_file_path) and os.path.getsize(network_file_path) > 0
        with open(network_file_path, 'a' if file_exists else 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['SSID', 'IPV6', 'Infrastructure', 'Channel', 'Rate', 'Security Protocol'])
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)

        print("Network added successfully.")

    except PermissionError:
        print("Permission denied. Please run the script with the necessary permissions.")
    except Exception as e:
        print(f"An error occurred: {e}")

def remove_all():
    if not directory():
        return
    os.remove(network_file_path)
    return

def easy_remove(index:int):
    if not directory():
        return
    with open(network_file_path, 'r') as file:
        reader = csv.reader(file)
        rows_keep = [row for row in reader]

    if 0 <= index < len(rows_keep):
        del rows_keep[index]
    else:
        print(f"Index {index} is out of range.")
        return

    with open(network_file_path, "w", newline="") as wrt:
        writer = csv.writer(wrt)
        for row in rows_keep:
            writer.writerow(row)
    return

def remove_manual(IPV6: str):
    if not directory():
        return
    with open(network_file_path, "r") as f:
        reader = csv.reader(f)
        rows_keep = [row for row in reader if row[1] != IPV6]

    with open(network_file_path, "w", newline="") as wrt:
        writer = csv.writer(wrt)
        for row in rows_keep:
            writer.writerow(row)
    return

def directory():
    if os.path.isfile(network_file_path):
        with open(network_file_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            index = 0
            for lines in reader:
                print(index, end='\t')
                index =  index + 1
                for i in lines:
                    print(i, end = "\t")
                print(end = '\n')
            return True
    else:
        print("No registered networks")
        return False


def debugger():
    print("Debugging Mode")

def scan_header():
    print('Index\tIPV6\t\t\tSSID\tInfrastructure\tChannel\tS. Speed\tS. Strength')

def empty_scan(duration: int):
    prev_snapshot = []
    for _ in range(duration):
        os.system('cls' if os.name == 'nt' else 'clear')
        curr_networks = capture_snapshot()
        if prev_snapshot == []:
            scan_header()
            for i in range(len(curr_networks)):
                print(i, end='\t')
                for j in list(curr_networks[i].values()):
                    print(j, end="\t")
                print()
            time.sleep(10)
            prev_snapshot = curr_networks
        else:
            scan_header()
            for i in range(len(curr_networks)):
                print(i, end='\t')
                num = 0
                flag = False
                for j in list(curr_networks[i].values()):
                    if num != 5:
                        print(j, end="\t")
                    else:
                        for entry in prev_snapshot:
                            if entry['IPV6'] == curr_networks[i]['IPV6']:
                                flag = True
                                if int(entry['Signal Strength']) < int(j):
                                    print(f"{GREEN}{j}{RESET}", end="\t")

                                elif entry['Signal Strength'] > curr_networks[i]['Signal Strength']:
                                    print(f"{RED}{j}{RESET}", end="\t")

                                else:
                                    print(f"{j}", end="\t")
                            else:
                                continue
                        if not flag:
                            print(f"{BLUE}{j}{RESET}", end="\t")
                    num += 1
                print()
            time.sleep(10)
            prev_snapshot = curr_networks

def foreign_log_adder(network, instance):
    new_file_path = log_file_path + 'log' + instance + '.csv'
    data = {'Time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'SSID': network['SSID'], 'IPV6': network['IPV6'], 'Channel': network['Channel'], 'Signal Strength' : network['Signal Strength']}
    try:
        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
        file_exists = os.path.isfile(new_file_path) and os.path.getsize(new_file_path) > 0
        with open(new_file_path, 'a' if file_exists else 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile,fieldnames=['Time', 'SSID', 'IPV6', 'Channel', 'Signal Strength'])
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)

    except PermissionError:
        print("No permission to create the log file")
        return
    except Exception as e:
        print(e)

    pass

def check_if_foreign(duration: int):
    ipv6_list = []
    instance = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    if os.path.isfile(network_file_path):
        with open(network_file_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            reader.__next__()
            for row in reader:
                ipv6_list.append(row[1])

    flag = False
    for _ in range(duration):
        os.system('cls' if os.name == 'nt' else 'clear')
        curr_networks = capture_snapshot()
        scan_header()
        for i in range(len(curr_networks)):
            print(i, end='\t')
            for j in list(curr_networks[i].values()):
                if curr_networks[i]["IPV6"] in ipv6_list:
                    flag = True
                if flag:
                    print(f"{j}", end="\t")
                else:
                    print(f"{RED}{j}{RESET}", end="\t")
            if not flag:
                foreign_log_adder(curr_networks[i], instance)
            print()
            flag = False
        time.sleep(10)

if __name__ == "__main__":
    try:
        os.mkdir("/home/FPAT")
    except FileExistsError:
        print("")
    parser = argparse.ArgumentParser(description="Welcome to Foreign Packet Analysis Tool."
                                                "Done by to Sunayana Debsikdar, Drishya M Nair, Jeevan Shaju John\n")

    parser.add_argument("-a", "--add", action= "store_true" , help="Add networks based on index")
    parser.add_argument("-aa", "--add_all", action="store_true", help="Add all current networks")
    parser.add_argument("-am", "--add_manual", nargs='+',
                        metavar= "ARGUMENTS",
                        help="Manually add a network (SSID IPv6 Infrastructure Channel Rate Security Protocol)")
    parser.add_argument("-r", "--remove", type=int, metavar="index", help="Remove networks")
    parser.add_argument("-ra", "--remove_all", action="store_true", help="Remove all current networks")
    parser.add_argument("-rm", "--remove_manual", metavar="IPV6", help="Remove networks manually (specify IPV6)")
    parser.add_argument("-dir", "--directory", action="store_true", help="Display all registered networks")
    parser.add_argument("-es", "--empty_scan", type=int, metavar="DURATION",
                        help="Perform an empty scan (duration in seconds)")
    parser.add_argument("-fs", "--full_scan", type=int, metavar="DURATION",
                        help="Perform a full scan (duration in seconds)")

    args = parser.parse_args()

    if not any(vars(args).values()):  # Check if no arguments were provided
        parser.print_help()
        exit(1)
    if args.add:
        easy_network_addition()
    elif args.add_all:
        add_all_networks()
    elif args.add_manual:
        if len(args.add_manual) < 2:
            parser.error("Error: SSID and IPv6 are required for manual addition.")
        ssid = args.add_manual[0]
        ipv6 = args.add_manual[1]
        infra = args.add_manual[2] if len(args.add_manual) > 2 else None
        channel = args.add_manual[3] if len(args.add_manual) > 3 else None
        rate = args.add_manual[4] if len(args.add_manual) > 4 else None
        sec_prot = args.add_manual[5] if len(args.add_manual) > 5 else None
        manual_network_addition(ssid, ipv6, infra, channel, rate, sec_prot)

    elif args.remove:
        easy_remove(args.remove)

    elif args.remove_all:
        remove_all()

    elif args.remove_manual:
        remove_manual(args.remove_manual)
    elif args.directory:
        directory()
    elif args.empty_scan is not None:
        empty_scan(args.empty_scan)
    elif args.full_scan is not None:
        check_if_foreign(args.full_scan)

    else:
        print("cooked")