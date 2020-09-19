import os
import sys
import nmap

def get_website(ip_address, profile):
    # Initiate wget download recursive
    try:
        os.system("wget -P ./" + profile + " --tries=3 " + ip_address + " -r")
    except OSError:
        print("Website unreachable\n")
        return False
    else:
        print("Website found\n")
        return True

def get_nmap_fingerprint(ip_address, profile):

    # instantiate nmap.PortScanner object
    nm = nmap.PortScanner()

    # scan PLC target, ports from 22 to 20000
    print("Nmap Scan started")
    nm.scan(ip_address, '1-2000', '-v5 -O -oN ./' + profile + '/fingerprint > out')
    print("Nmap Scan completed")


def create_honeyd_template(ip_address, profile):

    #Honeyd template using subsystem virtualization
    template = "create base\n"
    #Subsystem to start the s7comm server, server must be installed in the directory below
    template += "add base subsystem \"/usr/share/honeyd/s7commServer\" shared restart\n\n"
    template += "clone honeyplchost1 base\n"
    #Assign a personality to fool nmap scans, the personality must be added to /usr/share/nmap/nmap-os-db file.
    template += "set honeyplchost1 personality \"Siemens Simatic 300 programmable logic controller\"\n"
    #Bind a PLC vendor MAC address, the included one belongs to the Siemens S7-1200 but a different one might be used.
    template += "set honeyplchost1 ethernet 00:1C:06:0B:2E:C5\n\n"
    #IP address of the HoneyPLC host, can be any IP depending on environment.
    template += "bind 192.168.0.100 honeyplchost1\n"

    #Write template to file
    file1 = open("./" + profile + "/honeyd-template","w") 
    file1.write(template)
    file1.close
    print("Honeyd template created\n")


def create_profile_dir(profile_name):
    try:
        os.mkdir(profile_name)
    except OSError:
        print("Creation of new directory failed\n")
        return False
    else:
        print("New profile directory created\n")
        return True


def plc_reachable(ip_address):

    if os.system("ping -c 1 " + ip_address) is 0:
        return True
    return False


def command_sage():
    msg = "usage: profiler.py <address> <profile>\n\n"
    msg += "Run profiler.py to create a new HoneyPLC profile.\n"
    msg += "Write the IP address of the PLC host.\n"
    msg += "Write the name of the profile to be created.\n"
    msg += "A new directory with the profile data will be created.\n"

    return msg


def get_snmp_mib(ip_address, profile):
    #PLCs normally implement SNMP v1, if using a different version modify the -v argument
    try:
        os.system("snmpwalk -v 1 -ObentU -c public " + ip_address +
                " > ./" + profile + "/public.snmpwalk")
    except OSError:
        print("SNMP MIB Download failed\n")
        return False
    else:
        print("SNMP MIB Download completed\n")
        return True


def main():
    # Check for invalid argument input
    if len(sys.argv) != 3:
        print(command_sage())
        return

    # Get command line arguments
    plc_ip = sys.argv[1]
    profile_name = sys.argv[2]

    # Check if PLC is reachable
    if not plc_reachable(plc_ip):
        print("Unreachable host\n")
        exit(1)
    else:
        print("Host is reachable\n")

    # Create new profile dir
    if not create_profile_dir(profile_name + "-Profile"):
        exit(1)

    get_snmp_mib(plc_ip, profile_name + "-Profile")
    get_website(plc_ip, profile_name + "-Profile")
    get_nmap_fingerprint(plc_ip, profile_name + "-Profile")
    create_honeyd_template(plc_ip, profile_name + "-Profile")

    print("PLC Profile successfully created from host " + plc_ip + "\n")


if __name__ == '__main__':

    main()
