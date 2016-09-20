## DEPECRATED ##

# -*- coding: utf-8 -*-

import shutil
import urllib
import platform
import os
import sys

def salir():
	try:
		raw_input("Presione Enter para continuar")
	except:
		pass
	sys.exit()
	return

def datos_pc():
	print "Nombre del computador: "+ platform.node()
	print "Sistema operativo: "+ platform.system(),platform.release()
	print "Version interna del OS: "+ platform.version()
	print "Procesador: "+ platform.processor()
	print "Tipo de procesador: "+ platform.machine()
	#print "Nombre interno del OS: "+ platform.platform()
	print "Compilacion de Python: "+ str(platform.python_build())
	print "Compilador de Python: "+ platform.python_compiler()
	print "Version de Python: "+ platform.python_version()
	#print platform.uname()
	print
	return

def abrir_config():
	config = dict()
	config_file = open("config.alf")
	for linea in config_file:
		linea = linea.strip().split('=')
		config[linea[0]] = linea[1]
	#ip = config["ip"]
	#version = config["version"]
	config_file.close()
	config['version'] = float(config['version'])
	return config

def crear_config():
	config_file = open("config.alf","w")
	config_file.write("version=0.00\n")
	config_file.write("ip=localhost\n")
	config_file.close()
	return

def check_alf():
	try:
		open("alf.alf").close()
	except:
		file_alf = open("alf.alf","w")
		file_alf.close()
	return

def get_server_version(ip):
	try:
		version_file = urllib.urlopen("http://"+ip+"/update/version.alf")
	except:
		return None
	for i in version_file:
		try:
			server_version = float(i.strip())
		except:
			return None
	version_file.close()
	return server_version

def check_versions(server_version,client_version):
	if server_version > client_version:
		print "Existe una actualizacion"
		return True
	elif server_version < client_version:
		print "Posees una version superior a la del servidor"
		return False
	else:
		print "Tienes la ultima version"
		return False
	return False

def get_updates_errors():
	updates_errors = list()
	try:
		upda_error = open("updates_errors.alf")
		for linea in upda_error:
			updates_errors.append(linea.strip())
		upda_error.close()
	except:
		pass
	return updates_errors

def get_versions_list(ip,client_version,server_version):
	log = urllib.urlopen("http://"+ip+"/update/log.version")
	versions_list = list()
	for linea in log:
		linea = float(linea.strip())
		if linea <= client_version:
			continue
		if linea > server_version:
			continue
		versions_list.append(linea)
	log.close()
	return versions_list

def make_folders(linea):
	alf = linea.split("/")
	try:
		shutil.copy("alf.alf", "/".join(alf[:-1])+"/alf.alf")
	except:
		os.system("mkdir "+"\\".join(alf[:-1]))
	return

def download_update(versions_list,ip):
	lista_error_act = list()
	lista_error_archivos = list()
	upda_error = open("updates_errors.alf","a")
	for version in versions_list:
		try:
			update_file = urllib.urlopen("http://"+ip+"/update/"+str(version)+".version")
			for linea in update_file:
				linea = linea.strip()
				try:
					make_folders(linea)
					print "Descargando "+linea
					directorio,info = urllib.urlretrieve("http://"+ip+"/update/"+linea,linea)
					print "DEBUG: ",directorio,"\nDEBUG: ",info
				except:
					lista_error_archivos.append(linea)
					upda_error.write(linea)
					print "Error descargando "+linea
			update_file.close()
		except:
			lista_error_act.append(str(version))
	upda_error.close()
	return lista_error_act,lista_error_archivos

def download_errors(updates_errors):
	return

def main_updater():
	#datos_pc()

	try:
		config = abrir_config()
		config["version"]
		config["ip"]
	except:
		print "No se ha encontrado el archivo de configuracion o estaba dañado. \nCreando uno nuevo."
		crear_config()
		config = abrir_config()
	check_alf()

	print "Version del cliente: "+str(config["version"])

	print "Conectando con el servidor"
	server_version = get_server_version(config["ip"])
	if server_version == None:
		print "Error conectando al servidor. Reconectando"
		contador_errores = 0
	while server_version == None:
		print "Intento: "+str(contador_errores+1)
		contador_errores += 1
		try:
			server_version += get_server_version(config["ip"])
		except:
			pass
		if type(server_version)==float:
			print "Se ha logrado conectar con el servidor luego de "+str(contador_errores)+" intentos"
			break
		if contador_errores == 10:
			print "Error conectando al servidor despues de 10 intentos"
			salir()

	print "Version del servidor: "+str(server_version)
	new_version = check_versions(server_version,config['version'])

	updates_errors = get_updates_errors()
	if len(updates_errors) != 0:
		print "[WIP]"
		print "Se han encontrado archivos faltantes de actualizaciones anteriores"
		print "Se procedera a descargarlos"
		print "//Por el momento esta funcion no se encuentra disponible"
		print "[WIP]"

	if new_version:
		versions_list = get_versions_list(config["ip"],config['version'],server_version)
		print "Se descargaran las versiones: "+ ",".join(map(str,versions_list))
		print "Descargando actualizaciones"
		lista_error_act,lista_error_archivos = download_update(versions_list,config["ip"])
		if len(lista_error_act) == 0 and len(lista_error_archivos) == 0:
			print "Actualizacion realizada con exito"
		else:
			print str(len(lista_error_act)+len(lista_error_archivos))+" problemas" 
			if len(lista_error_act):
				for version_error in lista_error_act:
					print "No se ha encontrado la actualizacion "+version_error+" en el servidor"
			if len(lista_error_archivos):
				for archivos_error in lista_error_archivos:
					print "No se ha encontrado el archivo "+archivos_error+" en el servidor"
		salir()
	else:
		print "Su version ya esta actualizada"
		salir()
	return

if __name__ == "__main__":
	main_updater()