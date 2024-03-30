# NautoPromo
Instructions, script, and service files to have Prometheus server automatically reach out to Nautobot for targets

Created by me for a University project regarding open-source technologies such as Prometheus and Nautobot. 

Essentially what it does is queries Nautobot for interface "Management0" IP addresses and uses them to create a prometheus file_sd_config target file. Code can be easily modified to use another interface or your own query and parsing method. This is a overall a proof of concept of how you can integrate your source of truth with different services.

For clarification: the reason it uses port 8080 is that is the default port ocprometheus, an arista prometheus exporter for its switches, uses and is what I used.
