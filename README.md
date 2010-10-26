Idiocy is a warning shot to people browsing the internet insecurely.
====================================================================

For more information: <http://jonty.co.uk/idiocy>

Idiocy quitely watches for people unsecurely visiting twitter on public wifi
networks, then hijacks their session to post a tweet warning them about the
dangers. It was written in response to the release of Firesheep, which will
result in a huge increase in session stealing attacks, with no defence other
than forcing people to use SSL.

Running idiocy
--------------
Idiocy requires libpcap, python-pcap (http://code.google.com/p/pypcap) and python-dpkt. Also python.

On Linux:

* apt-get install libpcap python-pcapy python-dpkt
* iw wlan0 interface add mon0 type monitor && ifconfig mon0 up
* ./idiocy.py -i mon0

On OSX:

* Should be very similar to the above, can someone with a Mac investigate for me?

On Windows:

* God knows. I do know that getting your wifi card into monitor mode on windows can be difficult.

Notes
-----
* The code is crap. I wrote it at 7am in a fit of irritation.
* I'd love to add support for facebook and the like.
