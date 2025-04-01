#!/usr/bin/e nv python3

import csv
import os
import subprocess
import time
from mimetypes import knownfiles

network_file_path = '/home/FPAT/reg_net.csv'
log_file_path = '/home/FPAT/log.csv'
net_max = 0
RED = '\033[31m'
GREEN = '\033[32m'
BLUE = '\033[34m'
RESET = '\033[0m'
debug_count = 0

def help_result():
    print("Welcome to Foreign Packet Analysis Tool\n"
          "Credits to Sunayana Debsikdar, Drishya M Nair, Jeevan Shaju John\n"
          "Use fpat [option] [target] to run the program\n"
          "\n"
          "Options\n"
          "-h : Help\n"
          "-dir : View Directory of Registered Networks\n"
          "-scan : Start scanning for all current signals\n"
          "-madd [address]: Manually add new wifi networks with their IPV6 addresses\n"
          "-eadd : Easier addition of IPV6 addresses by creating a capture of all the currently existingn\n"
          "        wifi networks to choose ones to add from the current list\n"
          "-rem : Remove required wifi network from the current list or remove all wifi networks\n"
          "-logs : Display all the captured signal reports available\n"
          "-log [index] : Display detailed logs of the selected captured signal reports\n"
          "-logd [index] : Delete the chosen log report\n"
          "\n")


def capture_snapshot():
    result = subprocess.run(["nmcli", "-t", "dev", "wifi"], capture_output=True, text=True)
    networks = result.stdout.split('\n')
    snapshot = []
    for network in networks[0:len(networks) - 1]:
        IPV6 = network[2:4] + network[5:8] + network[9:12] + network[13:16] + network[17:20] + network[21:24]
        parts = network.split(':')
        SSID = parts[7]
        infra = parts[8]
        channel = parts[9]
        signal_speed = parts[10]
        signal_strength = parts[11]
        sec_prot = parts[13]
        net = {'IPV6': IPV6, 'SSID': SSID, 'Infrastructure': infra, 'Channel': channel, 'Signal Speed': signal_speed,
               'Signal Strength': signal_strength, 'Security Protocol': sec_prot}
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
    SSID, IPV6, infra, channel, rate, sec_prot = req[1], req[0], req[2], req[3], req[4], req[6]
    manual_network_addition(SSID, IPV6, infra, channel, rate, sec_prot)


def manual_network_addition(SSID: str, IPV6: str, infra: str, channel: str, rate: str, sec_prot: str):
    data = {'SSID': SSID, 'IPV6': IPV6, 'Infrastructure': infra, 'Channel': channel, 'Rate': rate, 'Security Protocol': sec_prot}

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


def remove():
    if not directory():
        return
    else:
        if input("Remove all? Enter 'y' to continue: ").lower() == 'y':
            os.remove(network_file_path)
            print("Network removed successfully.")
            return
        else:
            if input("Remove based on Index?: ").lower() == 'y':
                index = int(input("Enter the required network index: "))
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
            else:
                if input("Remove Manually? Enter 'y' to continue: ").lower() == 'y':
                    IPV6 = input("Enter the IPV6 address: ")
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


def addition():
    if input("Would you like to add all the current detected networks to the registration list?: ").lower() == 'y':
        add_all_networks()
    else:
        choice = input("Would you like to add another network with easy mode? (y/n): ")
        if choice.lower() == 'y':
            easy_network_addition()
        else:
            choice = input("Would you like to add another network with manual mode? (y/n): ")
            if choice.lower() == 'y':
                SSID = input("Enter the SSID: ")
                IPV6 = input("Enter the IPV6: ")
                choice = input(
                    "Would you like to add more details? (Channel, Infrastructure, Rate, Security Protocol (y/n): ")
                if choice.lower() == 'y':
                    channel = input("Enter the channel: ")
                    infra = input("Enter the infrastructure: ")
                    rate = input("Enter the rate: ")
                    sec_prot = input("Enter the security protocol: ")
                else:
                    channel = None
                    infra = None
                    rate = None
                    sec_prot = None
                manual_network_addition(SSID, IPV6, infra, channel, rate, sec_prot)
            else:
                return

def debugger():
    print("Debugging Mode")

def scan_header():
    print('Index\tIPV6\t\t\tSSID\tInfrastructure\tChannel\tS. Speed\tS. Strength\tSecurity Protocol')

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

def raw_log_file_network_add(SSID):
    try:
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    except PermissionError:
        print("No permission to create the log file")
        return
    except Exception as e:
        print(e)

    pass

def new_time_instance_adder():
    pass

def check_if_foreign(duration: int):
    ipv6_list = []
    if os.path.isfile(network_file_path):
        with open(network_file_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            reader.__next__()
            for row in reader:
                ipv6_list.append(row[1])

    flag = False
    for _ in range(duration):
        new_time_instance_adder()
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
                    raw_log_file_network_add(curr_networks[i])
                    print(f"{RED}{j}{RESET}", end="\t")
            print()
            flag = False
        time.sleep(10)

if __name__ == "__main__":
    try:
        os.mkdir("/home/FPAT")
    except FileExistsError:
        print("Welcome Back to Foreign Packet Analysis Tool")
    print("Enter 1 to Add Networks, 2 to Remove Networks,3 to Display all Registered Networks 4 for Help and Exit")
    while True:
        switch = int(input("Enter your choice: "))
        if switch == 1:
            addition()

        elif switch == 2:
            remove()

        elif switch == 3:
            directory()

        elif switch == 4:
            empty_scan(20)

        elif switch == 5:
            check_if_foreign(int(input("Enter scan duration: ")))

        else:
            help_result()
            exit()
