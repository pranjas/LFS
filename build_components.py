#!/usr/bin/python
import os
import sys
import subprocess;
import build_components_by_dependency

def do_build(root_dir):
	tmp_file = '.lfs_tmp_file'
	components_file="core.depmod"
	cmd = "touch " + root_dir + tmp_file
	print "Testing if I can create files in {0}/{1}".format(root_dir,tmp_file);
	if ( len(root_dir) == 0):
		print "Must provide a non null root dir",
	else:
		if (os.system(cmd) != 0):
			print "Cannot create files in {0}".format(root_dir), 
		else:
			os.system("rm " + root_dir + tmp_file);
			print "Passed file creation test..."
			print "Starting the build..."
			put_env_vars(root_dir)
			os.system("./build.sh " + root_dir)
			deps_graph = build_components_by_dependency.make_dependency_graph("./core-deps")
			for dep in deps_graph:
				print "Starting build for {0}".format(dep.name)
				if 'EXTRA_CONF' in dep.depmod:
					print "Putting EXTRA_CONF as {0}".format(dep.depmod['EXTRA_CONF'])
					extra_conf = subprocess.check_output("echo " + dep.depmod['EXTRA_CONF'].strip()\
									,shell = True)
					os.putenv('EXTRA_CONF',extra_conf)

				if os.system("./build_components.sh " + root_dir + " do_configure_one " \
						+ dep.name +"-"+dep.depmod['version']) != 0:
					print "Halting build"
					exit(-1)
				os.unsetenv('EXTRA_CONF')

def put_env_vars(root_dir):
	if len(root_dir) == 0:
		print "Root directory can't be null"
		raise Exception("Invalid root directory");
	
	build_type = subprocess.check_output("$(uname -m) | grep 64 | wc -l", shell = True)
	print build_type, 
	if build_type == "1":
		os.putenv("libdir",root_dir + "/lib64")
	else:
		os.putenv("libdir", root_dir + "/lib")

	os.putenv("LFS_ROOT_DIR", root_dir)
	os.putenv("sysconfdir", root_dir + "/etc")
	os.putenv("includedir", root_dir + "/usr/include")

	
if __name__ == "__main__":
	if ( len(sys.argv) != 2):
		print "Usage {0} <LFS_ROOT_DIRECTORY>".format(sys.argv[0]);
	else:
		do_build(sys.argv[1]);

#params = dict(sys.argv[1:])
#print "".format(params), 

