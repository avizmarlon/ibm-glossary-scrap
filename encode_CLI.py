import os
import platform

def encode_CLI():
	usr_os = platform.system()
	if usr_os == "Windows":
		os.system("chcp 65001")
	elif usr_os == "Linux":
		os.system("LANG=en_US.utf8")

if __name__ == "__main__":
	encode_CLI()
