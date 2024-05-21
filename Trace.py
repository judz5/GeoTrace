import socket
import requests

site = "youtube.com"
port = 33434


def main():

    # Get target IP addr
    dest_ip = socket.gethostbyname(site)
    print("Tracing to " + dest_ip)

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

        print('Hop #' + str(num_hop) + ": " + hopped_ip + ", " + str(loc_data.get("city")) +
              ", " + str(loc_data.get("region")) + ", " + str(loc_data.get("country")))
        num_hop += 1


main()
