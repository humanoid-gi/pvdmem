# Packet-via-dmem online converter

Simple Docker web app for online converting Juniper MX packet-via-dmem capture into **pcap** file.
For generating pcap it uses text2pcap utility from [wireshark tools](https://github.com/wireshark/wireshark)

## Installation
```
docker build --progress=plain --network=host -t pvdmem_app:v0.1 .
docker run -d --network=host --restart always pvdmem_app:v0.1
```

## How to collect packet-via-dmem dump
1. Login to FPC:
   ```
   start shell pfe network fpc0
   ```
2. Start packet-via-dmem capture and collect dump:
   ```
   test jnh <PFE#> packet-via-dmem enable
   test jnh <PFE#> packet-via-dmem capture 0x3 0a0000ff
   test jnh <PFE#> packet-via-dmem capture 0x0
   test jnh <PFE#> packet-via-dmem decode
   test jnh <PFE#> packet-via-dmem disable
   ```
