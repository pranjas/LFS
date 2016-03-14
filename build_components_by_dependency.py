#!/usr/bin/python

import os
from collections import deque

class LFSModule:
	def __init__(self):
		self.depmod = dict()
		self.name = ""


			
def get_module_with_deps(filename):
	d = LFSModule();
	with open(filename) as f:
		d.name = filename.split('.')[0]
		option_continue = False
		option_key = ""
		while True:
			line = f.readline()
			line = line.strip(' ');
			line = line.strip('\t');
			if len(line) == 0:
				break;
			elif len(line) == 1:
				if line[0] != '\n':
					msg = "Invalid format for file " + filename
					print msg
					raise Exception(msg)
				else:
					continue;
			else:
				pass;
			tokens = line.split(":=")
			for index,t in enumerate(tokens):
				tokens[index] = t.strip(' ');
				tokens[index] = tokens[index].strip('\t')
				
			if len(tokens) < 2 and tokens[len(tokens) - 1][-2] != '\\' \
				and not option_continue:
					msg = "Invalid depmod file " + filename;
					print msg
					raise Exception(msg)
			else:
				if(option_continue):
					if (line[-2] != '\\'):
						option_continue = False
					if (line[-1] == '\n') and option_continue:
						d.depmod[option_key] = d.depmod[option_key] + line[:-2]
					elif (line[-1] == '\n'):
						d.depmod[option_key] = d.depmod[option_key] + line[:-1]
					else:
						d.depmod[option_key] = d.depmod[option_key] + line
					
				elif(len(tokens) == 2):
					if (tokens[1][-2] == '\\'):
						option_continue = True;
						option_key = tokens[0]
						d.depmod[tokens[0]] = tokens[1][:-2];
					else:
						d.depmod[tokens[0]] = tokens[1][:-1]

				elif len(tokens) > 2:
					d.depmod[tokens[0]] = tokens[1]
					token_index = 2;
					while token_index < len(tokens):
						if(tokens[token_index][-2] == '\\'):
							option_continue = True;
							option_key = tokens[0]
							d.depmod[tokens[0]] = \
							d.depmod[tokens[0]] + "=" +\
							tokens[token_index][:-2]
						else:
							d.depmod[tokens[0]] = \
							d.depmod[tokens[0]] + "=" +\
							tokens[token_index][:-1]
						token_index += 1
				else:
					msg = "Invalid depmod file " + filename	
					print msg
					raise Exception(msg)

	return d;

def make_dependency_graph(depmod_dir):
	if len(depmod_dir) == 0:
		raise Exception("Dependency directory name can't be empty")
	
	#Queue for all the un-processed packages.
	dependency_list = deque()
	sorted_deps_list = deque()
	saved_pwd = os.getcwd()

	if os.chdir(depmod_dir):
		print("Check if {0} is a directory with proper permissions".format(depmod_dir))
	
	#Need to omit directories
	for f in os.listdir("."):
		dependency_list.append(get_module_with_deps(f))

	processed_list = dict()

	while len(dependency_list) != 0:
		dep = dependency_list.popleft();
		print "processing {0} with depmod {1}".format(dep.name, dep.depmod)
		if 'depends' not in dep.depmod or\
			len(dep.depmod['depends']) == 0 or \
			dep.depmod['depends'].lower() == "none":
				processed_list[dep.name] = dep;
				sorted_deps_list.append(dep);
		else:
			dep_dependencies = dep.depmod['depends'].split(' ')
			for dd in dep_dependencies:
				if dd not in processed_list:
					dependency_list.append(dep);
					break;
				else:
					print "Found {0} to resolve dependency for {1}".format(dd, dep.name)
			else:
				processed_list[dep.name] = dep;
				sorted_deps_list.append(dep);
	os.chdir(saved_pwd)
	return sorted_deps_list;

if __name__ == "__main__":
	import sys;
	if len(sys.argv) != 2:
		print("Usage {0} <depmod_directory>".format(sys.argv[0]))
		exit()
	deps_list = make_dependency_graph(sys.argv[1])

	for item in deps_list:
		print "Module {0} with depmod {1}".format(item.name, item.depmod)
