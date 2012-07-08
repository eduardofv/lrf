
import time
import BaseHTTPServer

from lrf import * 

PORT=80
SERVER=''

class WebLRFHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_GET(s):
		res = ""

                if s.path == '/photo':
			f = open('img2.jpg')
			img = f.read()
			f.close()
			s.send_response(200)
			s.send_header('Content-Type','image/jpeg')
			s.end_headers()
			s.wfile.write(img)
			
		elif s.path == '/' or s.path=='/measure':
			data = single_measure()
			res = "<table><tr><td><h2>Distance:</h2></td><td><h2>%0.2f [cm]</h2></td></tr>"
			res += "<tr><td>posX</td><td>%d [pixel]</td></tr>"
			res += "<tr><td>posY</td><td>%d [pixel]</td></tr>"
			res += "<tr><td>area</td><td>%d</td></tr></table>"
			res += "<a href='/photo'><img src='/photo' style='width:400px'/></a>"
			res = res%data

			s.send_response(200)
			s.send_header("Content-Type","text/html")
			s.end_headers()
			s.wfile.write("<html><body><h1>Laser Range Finder</h1>")
			s.wfile.write("<h3><a href='/measure'>Measure</a></h3>")
			s.wfile.write("<div>"+res+"</div>")
			s.wfile.write(s.path)
			s.wfile.write("</body></html>")
		else:
			s.send_response(404)

#main
server_class = BaseHTTPServer.HTTPServer
httpd = server_class((SERVER,PORT), WebLRFHandler)
print "starting"
try:
	httpd.serve_forever()
except:
	pass
httpd.server_close()
print "ended"
