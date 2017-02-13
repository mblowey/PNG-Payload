import os
import struct
import binascii

#In certain places a read is called, but not assigned and bytesRead has a value added to it. 
#This is to skip forward in the file towards the next relevant piece of information. 
#BytesRead is tracked so that one 'IEND' is found, I can back track to the point before it.

def hide():
	hostPath = 'C:/Users/Mitchell/Pictures/nice-flowers.png' #raw_input("Input host PNG: ")
	host = open(hostPath, "rb+")
	payloadPath = 'C:/Users/Mitchell/Pictures/Purple_Yoshi.png' #raw_input("Input payload PNG: ")
	payload = open(payloadPath, "rb+")
	payloadSize = os.path.getsize(payloadPath)
	payloadData = payload.read()
	
	readInt(host)
	readInt(host)
	bytesRead = 8 #starts at 8 to skip header of png format
	
	chunk_length = readInt(host)
	bytesRead += 4
	
	chunk_type = readASCII(host)
	bytesRead += 4
	
	
	while(chunk_type != 'IEND'):
		host.read(chunk_length)
		bytesRead += chunk_length 
		readInt(host)
		bytesRead += 4 #the 4 skips the CNC tag at the end of each chunk. 
		
		chunk_length = readInt(host)
		bytesRead += 4
		
		chunk_type = readASCII(host)
		bytesRead += 4
		
	#found the last chunk. Need to go back 8 bytes
	bytesRead -= 8
	host.seek(bytesRead)
	
	#prep CRC
	tmp_bytes = bytearray()
	tmp_bytes.extend(bytearray("caVe"))
	tmp_bytes.extend(payload)
	
	#write chunk header: <chunk size> <chunk type>
	host.write(bytearray(struct.pack("!i", payloadSize)))
	host.write(bytearray("caVe"))
	host.write(payloadData)
	
	
	crc = binascii.crc32(tmp_bytes)
	host.write(bytearray(struct.pack("!i", crc)))
	
	#write EOF
	host.write(bytearray(struct.pack("!i", 0)))
	host.write(bytearray("IEND"))
	
def reveal():
	host = open("C:/Users/Mitchell/Pictures/nice-flowers.png", "rb+")
	
	readInt(host)
	readInt(host)
	bytesRead = 8 #starts at 8 to skip header of png format
	
	chunk_length = readInt(host)
	bytesRead += 4
	
	chunk_type = readASCII(host)
	bytesRead += 4
	
	
	while(chunk_type != 'caVe'):
		print chunk_type + ": " + str(chunk_length)
		host.read(chunk_length)
		bytesRead += chunk_length 
		readInt(host)
		bytesRead += 4 #the 4 skips the CNC tag at the end of each chunk. 
		
		chunk_length = readInt(host)
		bytesRead += 4
		
		chunk_type = readASCII(host)
		bytesRead += 4

	#Payload has been found!
	output = open("C:/Users/Mitchell/Pictures/payload.png", "ab+")
	output.write(host.read(chunk_length))
	
	
def readInt(file):
	return int(file.read(4).encode("hex"), 16)

def readASCII(file):
	return file.read(4).encode("ascii")
	
