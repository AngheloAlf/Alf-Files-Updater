# -*- coding: utf-8 -*-

import shutil
import urllib
import platform
import os
import sys


CLIENT_VERSION = "0.1" #updater.py version

DEFAULT_DATA_VERSION = "0.0" #the default version of the files
DEFAULT_IP = "http://127.0.0.1/" #localhost, for testing porpuses
DEFAULT_UPDATE_PATH = "update/"
DEFAULT_VERSIONS_FILE = "version.alf"
DEFAULT_LOG = "update/log.alf"
DEFAULT_UPDATE_VERSIONS_FILES_PATH = "versions_files/"
DEFAULT_FILES_PATH = "data/"


def abrir_config():
	config = dict()
	config_file = open("config.alf")
	for line in config_file:
		line = line.strip().split('=')
		config[line[0]] = line[1]
	config_file.close()
	config['version'] = float(config['version'])
	return config

def crear_config(ip, version):
	config_file = open("config.alf","w")
	config_file.write("ip="+ip+"\n")
	config_file.write("version="+str(version)+"\n")
	config_file.close()
	return

def get_config(ip, version):
	try:
		config = abrir_config()
		config["version"]
		config["ip"]
	except:
		print "Config file doesn't found.\nCreating config file"
		crear_config(ip, version)
		config = abrir_config()
	return config


def check_alf():
	try:
		open("alf.alf").close()
	except:
		file_alf = open("alf.alf","w")
		file_alf.close()
	return


def escribir_archivo(nombre, lista, modo = "r"):
	file = open(nombre, modo)
	for i in lista:
		if type(lista) == dict:
			file.write(i + "=" + str(lista[i]) + "\n")
		else:
			file.write(i + "\n")
	file.close()

# The version.alf file in the server must have only the actual version
def get_server_version(ip, update_path, version_file):
	try:
		route = ip + update_path + version_file
		version_file = urllib.urlopen(route)
		for i in version_file:
			try:
				server_version = i.strip()
			except:
				return None
		version_file.close()
		return float(server_version)
	except:
		return None

def get_server_version_retries(ip, update_path, version_file):
	print "Connecting with the server..."
	contador_errores = 0
	errors_limit = 10
	server_version = get_server_version(ip, update_path, version_file)
	if server_version == None:
		print "Error connecting the server. Reconnecting..."
	while server_version == None:
		print "Try: "+str(contador_errores+1)
		contador_errores += 1
		try:
			server_version = get_server_version(config["ip"])
		except:
			pass
		if type(server_version) == float:
			print "Connected with the server after "+str(contador_errores)+" tries"
			break
		if contador_errores == errors_limit:
			print "Error connecting to the server after " + str(errors_limit) + " tries"
			return None
	return server_version


def check_versions(data_version, server_version):
	if server_version > data_version:
		print "There's an update"
		return True
	elif server_version < data_version:
		print "You have a version superior to the server's version"
		return False
	else:
		print "It's updated"
		return False
	return False

# Return a list with all the versions to download
def get_versions_list(ip, log, data_version, server_version):
	versions_file = urllib.urlopen(ip + log)
	versions_list = list()
	for version in versions_file:
		version = float(version.strip())
		if version <= data_version: 
			continue
		if version > server_version:
			continue
		versions_list.append(version)
	versions_file.close()
	return versions_list

# TODO: review if works in all os
def make_folders(download_file):
	alf = download_file.split("/")
	if(len(alf) > 1):
		try:
			shutil.copy("alf.alf", "/".join(alf[:-1])+"/alf.alf")
		except:
			os.system("mkdir "+"\\".join(alf[:-1]))
	return

def download_update(ip, update_path, update_versions_files_path, files_path, versions_list, more_files_to_download = set()):
	files_to_download = set() | more_files_to_download

	lista_error_act = list()
	lista_error_archivos = list()
	
	notAdd = False

	for version in versions_list:
		version = str(version)
		if notAdd:
			lista_error_act.append(version)
		else:
			update_file = urllib.urlopen(ip + update_path + update_versions_files_path + version + ".version")
			
			for download_file in update_file:
				if download_file.strip() == "Archivo no encontrado":
					lista_error_act.append(version)
					notAdd = True
					break

				download_file = download_file.strip()
				files_to_download.add(download_file)
					
			update_file.close()

	for files in files_to_download:
		make_folders(files)
		print "\tDownloading " + files
		badFile = False
		link = ip + update_path + files_path + files
		
		fileTest = urllib.urlopen(link)
		for i in fileTest:
			if i.strip() == "Archivo no encontrado":
				badFile = True
			break
		fileTest.close()

		if not badFile:
			print link
			directorio, info = urllib.urlretrieve(link, files)
			#print "DEBUG: ", directorio, "\nDEBUG: ", info, "\n"
		else:
			lista_error_archivos.append(files)
			print "\t\tError downloading "+files

	escribir_archivo("updates_errors_files.alf", lista_error_archivos, "w")
	escribir_archivo("updates_errors_versions.alf", lista_error_act, "w")

	return lista_error_act, lista_error_archivos


def download_error_files(ip, update_path, update_versions_files_path, files_path):

	files_to_redownload = set()
	versions_to_redownload = list()

	try:
		files_errors = open("updates_errors_files.alf")
		for i in files_errors:
			files_to_redownload.add(i.strip())
		files_errors.close()
	except:
		pass

	try:
		files_errors = open("updates_errors_versions.alf")
		for i in files_errors:
			versions_to_redownload.append(i.strip())
		files_errors.close()
	except:
		pass

	if(len(files_to_redownload) + len(versions_to_redownload) != 0):
		print "Missing files has been found."
		download_update(ip, update_path, update_versions_files_path, files_path, versions_to_redownload, files_to_redownload)
		print ""

	return


def use_updater(ip, update_path, version_file, log, update_versions_files_path, files_path):
	print ""
	print "Client version:", CLIENT_VERSION

	check_alf()

	config = get_config(ip, DEFAULT_DATA_VERSION)
	print "Data version: " + str(config['version']) + "\n"
	
	server_version = get_server_version_retries(ip, update_path, version_file)
	if server_version == None:
		print "Download failed"
		return
	print "Server version: " + str(server_version)
	print ""
	
	download_error_files(config["ip"], update_path, update_versions_files_path, files_path)

	new_version = check_versions(config['version'], server_version)

	if new_version:
		versions_list = get_versions_list(config["ip"], log, config['version'], server_version)
		print "The following versions will be downloaded: " + ", ".join(map(str,versions_list))
		print "Downloading updates"
		lista_error_act,lista_error_archivos = download_update(config["ip"], update_path, update_versions_files_path, files_path, versions_list)
		print ""
		if len(lista_error_act) == 0 and len(lista_error_archivos) == 0:
			config['version'] = server_version
			print "Updated successfully"
		else:
			print str(len(lista_error_act)+len(lista_error_archivos))+" problem(s) found" 
			if len(lista_error_act):
				for version_error in lista_error_act:
					print "\tCan't find update "+version_error+" in the server"
			if len(lista_error_archivos):
				for archivos_error in lista_error_archivos:
					print "\tCan't find "+archivos_error+" in the server"
	else:
		print "This version is updated."

	escribir_archivo("config.alf", config, "w")
	return

if __name__ == "__main__":
	use_updater(DEFAULT_IP, DEFAULT_UPDATE_PATH, DEFAULT_VERSIONS_FILE, DEFAULT_LOG, DEFAULT_UPDATE_VERSIONS_FILES_PATH, DEFAULT_FILES_PATH)
