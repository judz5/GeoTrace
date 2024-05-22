import socket
import requests
import curses

port = 33434

logo = """
  ______ _______  _____  _______  ______ _______ _______ _______
 |  ____ |______ |     |    |    |_____/ |_____| |       |______
 |_____| |______ |_____|    |    |    \_ |     | |_____  |______
                                                                
"""


def print_logo(stdscr):
    global logo_line

    height, width = stdscr.getmaxyx()

    logo_line = logo.splitlines()
    for i, line in enumerate(logo_line):
        stdscr.addstr(2 + i, (width // 2) - (len(line) // 2), line)

    prompt = "Enter URL: "
    stdscr.addstr(4 + len(logo_line), (width // 2) -
                  (len(prompt) // 2), prompt)


def get_user_url(stdscr):
    curses.curs_set(1)
    stdscr.clear()

    height, width = stdscr.getmaxyx()

    print_logo(stdscr)

    prompt = "Enter URL: "
    stdscr.addstr(4 + len(logo_line), (width // 2) -
                  (len(prompt) // 2), prompt)

    curses.echo()
    stdscr.refresh()

    url = stdscr.getstr(5 + len(logo_line), (width // 2) - 10).decode('utf-8')
    curses.noecho()
    return url


def main(stdscr):

    curses.curs_set(1)

    site = get_user_url(stdscr)

    stdscr.clear()

    print_logo(stdscr)

    # Get target IP addr
    dest_ip = socket.gethostbyname(site)
    stdscr.addstr(2 + len(logo_line), 0, f'Tracing path to : {dest_ip}')
    stdscr.refresh()

    # Creates a UDP Socket for sending out packets
    sent_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sent_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Create UDP socket for listening to returned ICMP responses
    receiver = socket.socket(
        socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_ICMP)
    receiver.setsockopt(socket.SOL_IP, socket.IP_HDRINCL, 1)

    hopped_ip = None
    num_hop = 1
    while hopped_ip != dest_ip:

        # A TTL (time to live) value is set for each hop based of num_hops
        sent_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, num_hop)

        # Sends UDP packet with random message
        sent_socket.sendto(bytes("foo", 'utf-8'), (dest_ip, port))

        _, addr = receiver.recvfrom(1500)
        hopped_ip = addr[0]

        # Uses ip geolocation api for location data
        loc_response = requests.get(
            f'http://ip-api.com/json/{hopped_ip}').json()
        loc_data = {
            "city": loc_response.get("city"),
            "region": loc_response.get("regionName"),
            "country": loc_response.get("country")
        }

        # print(loc_response)

        info = ('Hop #' + str(num_hop) + ": " + hopped_ip + ", " + str(loc_data.get("city")) +
                ", " + str(loc_data.get("region")) + ", " + str(loc_data.get("country")))
        stdscr.addstr((2 + len(logo_line)) + num_hop, 0, info)
        stdscr.refresh()

        num_hop += 1


curses.wrapper(main)
