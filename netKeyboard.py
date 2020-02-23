#!/usr/bin/python3

from time import sleep
import socket
import sys
import win32api
import datetime

def special_chars(ordnum):
	# 0 = gotta find out
	# ordnum : [base-keycode, mod]
	# mod = 0 = none
	#	  = 1 = shift
	#	  = 2 = strg + alt = alt gr
	specials = {
		32: [32, 0], # ' '
		33: [49, 1], # '!'
		34: [50, 1], # '"'
		35: [0xBF, 0], # '#'
		36: [52, 1], # '$'
		37: [53, 1], # '%'
		38: [54, 1], # '&'
		39: [0xBF, 1], # '''
		40: [56, 1], # '('
		41: [57, 1], # ')'
		42: [106, 0], # '*'
		43: [107, 0], # '+'
		44: [0xBC, 0], # ','
		45: [109, 0], # '-'
		46: [0xBE, 0], # '.'
		47: [111, 0], # '/'
		#0 - 9
		58: [0xBE, 1], # ':'
		59: [0xBC, 1], # ';'
		60: [0xE2, 0], # '<'
		61: [55, 1], # '='
		62: [0xE2, 1], # '>'
		63: [0xDB, 1], # '?'
		64: [81, 2], # '@'
		#A - Z
		91: [56, 2], # '['
		92: [0xDB, 2], # '\'
		93: [57, 2], # ']'
		94: [0xDC, 0], # '^'
		95: [0xBD, 1], # '_'
		96: [0xDD, 1], # '`'
		#a - z
		123: [55, 2], # '{'
		124: [0xE2, 2], # '|'
		125: [48, 2], # '}'
		126: [0xBB, 2], # '~'
		#language-specific:
		# 196: [0xDE, 1], # 'Ä'	#something not working here - gotta revisit
		# 228: [0xDE, 0], # 'ä'
		# 220: [0xBA, 1], # 'Ü'
		# 252: [0xBA, 0], # 'ü'
		# 214: [0xC0, 1], # 'Ö'
		# 246: [0xC0, 0], # 'ö'
		# 223: [0xDB, 0] # 'ß'
	}

	if(specials[ordnum][0] == 0):
		print(f"\nError for {ordnum}:{chr(ordnum)}\n")
	else:
		base_press = specials[ordnum][0]
		mod_press = specials[ordnum][1]
		if(mod_press == 1):
			win32api.keybd_event(0x10, 0, 0, 0) #shift
		elif(mod_press == 2):
			win32api.keybd_event(0x11, 0, 0, 0) #strg/ctrl
			win32api.keybd_event(0x12, 0, 0, 0) #alt

		win32api.keybd_event(base_press, 0, 0, 0)
		win32api.keybd_event(base_press, 0, 2, 0)

		if(mod_press == 1):
			win32api.keybd_event(0x10, 0, 2, 0)
		elif(mod_press == 2):
			win32api.keybd_event(0x11, 0, 2, 0)
			win32api.keybd_event(0x12, 0, 2, 0)



IP = "0.0.0.0"
PORT = 6969

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((IP, PORT))
server.listen()

outter_running = True

while(outter_running):
	print("\nWaiting for something.")
	client_sock, client_addr = server.accept()
	print(f"Accepted incoming connection from {client_addr[0]} on port {client_addr[1]}")

	with open('log.txt', 'ab') as f:
		f.write(f"{datetime.datetime.now()}:\nclient_sock: {client_sock}\nclient_addr: {client_addr}\n\n".encode('utf-8'))
	f.close()

	client_sock.send(b"Press '[' to end your session!\n")
	
	try:
		incoming = client_sock.recv(1)
	except:
		print("\n!!!Error in client_sock.recv(1)!!!\n")
		continue

	inner_running = True

	while(inner_running):
		if(ord(incoming) >= 32 and ord(incoming) <= 126): #32 or 0x20 = space upto 126 or 0x7E ~ should include most printable chars (except special äöü..)
			print(incoming.decode(), end='')
			vkey = ord(incoming)
			if(vkey >= 97 and vkey <= 122):
				#a - z
				vkey -= 32
				win32api.keybd_event(vkey, 0, 0, 0)
				win32api.keybd_event(vkey, 0, 2, 0)
			elif(vkey >= 65 and vkey <= 90):
				#A - Z
				win32api.keybd_event(0x10, 0, 0, 0)
				win32api.keybd_event(vkey, 0, 0, 0)
				win32api.keybd_event(vkey, 0, 2, 0)
				win32api.keybd_event(0x10, 0, 2, 0)
			elif(vkey >= 48 and vkey <= 57):
				#0 - 9
				win32api.keybd_event(vkey, 0, 0, 0)
				win32api.keybd_event(vkey, 0, 2, 0)
			elif(vkey == 91):
				#[
				inner_running = False
			elif(vkey == 93):
				#]
				inner_running = False
				outter_running = False
			else:
				#any special char within the printable chars (excluding äöü)
				special_chars(vkey)
		elif(ord(incoming) != ord('\r') and ord(incoming) != ord('\n')):
			print(f"\n!!!Weird Char Incoming -> {ord(incoming)}:{incoming}!!!\n")

		try:
			incoming = client_sock.recv(1)
		except:
			print("\n!!!Error in client_sock.recv(1)!!!")
			break