#!/usr/bin/env python3

import csv
import os
import subprocess
import time
from re import split

network_file_path = '/home/FPAT/reg_net.csv'
net_max = 0


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
            net = {'IPV6': IPV6, 'SSID': SSID, 'Infrastructure': infra, 'Channel': channel, 'Signal Speed': signal_speed,'Signal Strength': signal_strength, 'Security Protocol': sec_prot}
            snapshot.append(net)

    return snapshot

def display():


def easy_addition():
    curr_networks = capture_snapshot()
    for i in range(len(curr_networks)):
        print(i, curr_networks[i].values())
    index = int(input("Enter the required network index: "))
    req = list(curr_networks[index].values())
    IPV6, SSID , infra, channel, rate, sec_prot = req[1], req[0], req[2], req[3], req[4], req[7]
    manual_addition(SSID, IPV6, infra, channel, rate, sec_prot)


def manual_addition(SSID: str, IPV6: str, infra: str, channel: str, rate: str, sec_prot: str):
    data = {'SSID': SSID, 'IPV6': IPV6, 'Infra': infra, 'Channel': channel, 'Rate': rate, 'Security Protocol': sec_prot}

    try:
        os.makedirs(os.path.dirname(network_file_path), exist_ok=True)

        if os.path.isfile(network_file_path):
            with open(network_file_path, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                existing_data = [row for row in reader]
                for row in existing_data:
                    if row['SSID'] == SSID or row['IPV6'] == IPV6:
                        print("Duplicate entry found. Network not added.")
                        return

        file_exists = os.path.isfile(network_file_path) and os.path.getsize(network_file_path) > 0
        with open(network_file_path, 'a' if file_exists else 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['SSID', 'IPV6'])
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
            if input("Remove Single? Enter 'y' to continue: ").lower() == 'y':
                IPV6 = input("Enter the IPV6 address: ")
                with open(network_file_path, "r") as f:
                    reader = csv.reader(f)
                    rows_keep = [row for row in reader if row[1] != IPV6]

                with open(network_file_path, "w", newline="") as wrt:
                    writer = csv.writer(wrt)
                    for row in rows_keep:
                        writer.writerow(row)
                return
            else:
                return


def directory():
    if os.path.isfile(network_file_path):
        with open(network_file_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            for lines in reader:
                print(lines)
            return True
    else:
        print("No registered networks")
        return False


if __name__ == "__main__":
    easy_addition()
    # try:
    #       os.mkdir("/home/FPAT")
    # except FileExistsError:
    #       print("Welcome Back to Foreign Packet Analysis Tool")
    # print("Enter 1 to add, 2 to remove")
    # while True:
    #       switch = int(input("Enter your choice: "))
    #       if switch == 1:
    #             easy_addition()
    #       elif switch == 2:
    #             remove()
    #       else:
    #             help_result()
    #             exit()
