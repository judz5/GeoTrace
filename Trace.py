import socket
import requests
import folium
from folium.plugins import AntPath

port = 33434

logo = r"""
 ▄▄ • ▄▄▄ .      ▄▄▄▄▄▄▄▄   ▄▄▄·  ▄▄· ▄▄▄ .
▐█ ▀ ▪▀▄.▀·▪     •██  ▀▄ █·▐█ ▀█ ▐█ ▌▪▀▄.▀·
▄█ ▀█▄▐▀▀▪▄ ▄█▀▄  ▐█.▪▐▀▀▄ ▄█▀▀█ ██ ▄▄▐▀▀▪▄
▐█▄▪▐█▐█▄▄▌▐█▌.▐▌ ▐█▌·▐█•█▌▐█ ▪▐▌▐███▌▐█▄▄▌
·▀▀▀▀  ▀▀▀  ▀█▄▀▪ ▀▀▀ .▀  ▀ ▀  ▀ ·▀▀▀  ▀▀▀ 
"""


def print_logo():
    print(logo)

def get_user_url():
    print_logo()

    url = input("Enter URL/IP: ")
    return url

def main():

    site = get_user_url()


    #print_logo()

    # Get target IP addr
    dest_ip = socket.gethostbyname(site)
    print(f'Tracing path to : {dest_ip}')

    # Creates a UDP Socket for sending out packets
    sent_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sent_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Create UDP socket for listening to returned ICMP responses
    receiver = socket.socket(
        socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_ICMP)
    receiver.setsockopt(socket.SOL_IP, socket.IP_HDRINCL, 1)
    receiver.settimeout(10)

    hopped_ip = None
    global num_hop
    num_hop = 1

    global cords
    cords = []
    while True:

        # print("starting")

        # A TTL (time to live) value is set for each hop based of num_hops
        sent_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, num_hop)

        # Sends UDP packet with random message
        sent_socket.sendto(bytes("foo", 'utf-8'), (dest_ip, port))

        try:
            _, addr = receiver.recvfrom(1500)
            hopped_ip = addr[0]

            # print("Getting")

            # Uses ip geolocation api for location data
            loc_response = requests.get(
                f'http://ip-api.com/json/{hopped_ip}').json()

            # if loc_response.get("status") == "fail":
            #     continue

            # print("going")

            loc_data = {
                "city": loc_response.get("city"),
                "region": loc_response.get("regionName"),
                "country": loc_response.get("country"),
                "lat": loc_response.get("lat"),
                "lon": loc_response.get("lon")
            }

            # print(loc_response)
            # print((loc_data.get("lat"), loc_data.get("lon")))
            cords.append((loc_data.get("lat"), loc_data.get("lon"), num_hop))
            info = ('Hop #' + str(num_hop) + ": " + hopped_ip + ", " + str(loc_data.get("city")) +
                    ", " + str(loc_data.get("region")) + ", " + str(loc_data.get("country")))
            print(info)

        except socket.timeout:
            print(f'Hop #{num_hop}: Request timed out')

        if hopped_ip == dest_ip:
            break

        num_hop += 1

    pingMap = folium.Map(zoom_start=5)
    for lat, lon, hop in cords:
        if lat is not None and lon is not None:
            folium.Marker(location=(lat, lon), popup=f'Hop #{hop}').add_to(pingMap)

    # ant path for showing order
    lat_lon_list = [(lat, lon) for lat, lon,
                    _ in cords if lat is not None and lon is not None]
    if lat_lon_list:
        AntPath(lat_lon_list).add_to(pingMap)

    pingMap.save("traceMap.html")

    print(f'dest found in {num_hop} hops, at location {cords[-1]}')

main()