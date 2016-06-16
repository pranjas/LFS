#!/usr/bin/python
import os
import subprocess
import tempfile
import stat

def get_module_with_code(filename):
	keywords = None;
	result = None;
	result = []
	keywords = {'do_pre_configure':False, 'do_post_configure':False, 'do_pre_compile':False, 'do_post_compile':False,\
			'do_pre_install':False, 'do_post_install':False, 'do_configure' :False, 'do_compile': False,\
			'do_install':False}
	try:
		with open(filename) as f:
			current_function = []
			code="";
			while True:
				line = f.readline()
				if len(line) == 0:
					break;
				line = line.strip(' ')
				line = line.strip('\t')
				for key,value in keywords.items():

					if key in line:
						if value: #True/False
							print "Already parsing/parsed {0}".format(key)
							raise Exception("Invalid file format")
						else:
							keywords[key] = True
				code = code + line
			result.append(code)
			result.append(keywords)
	except (IOError):
		result.append("")
		result.append(keywords)
	return result

def create_tmp_exec_file(data_to_write):
	exec_file = tempfile.NamedTemporaryFile(delete = False)
	with open(exec_file.name, mode = "w") as f:
		f.write("#!/bin/sh\n")
		f.write(data_to_write);
		f.write("\n" + "cmd=$1; shift;\n" + "$cmd $*\n")
	st= os.stat(exec_file.name)
	os.chmod(exec_file.name, st.st_mode | stat.S_IEXEC)
	return exec_file.name

def unlink_tmp_exec_file(filename):
	os.unlink(filename)


if __name__ == "__main__":
	import sys
	if len(sys.argv) >= 2:
		result = get_module_with_code(sys.argv[1])
		print result[0],
		exec_name = create_tmp_exec_file(result[0])
		print "file name is {0}".format(exec_name)
		os.system("cat " + exec_name)
		for key,value in result[1].items():
			if value:
				args = " "
				for _arg in sys.argv[2:]:
					args = args + " " + _arg
				print "Executing {0}".format(key)
				out=subprocess.check_output(exec_name +" " +key +" " + args, shell = True)
				print "Output is {0}".format(out)
		unlink_tmp_exec_file(exec_name)
