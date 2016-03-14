#!/usr/bin/python
import os
import sys
import subprocess;
import build_components_by_dependency
import get_module_code


__COMMAND = ['configure', 'compile', 'install']


def put_env_vars(root_dir):
	if len(root_dir) == 0:
		print "Root directory can't be null"
		raise Exception("Invalid root directory");
	
	build_type = subprocess.check_output("echo $(uname -m) | grep 64 | wc -l", shell = True)
	bin_path_exports = subprocess.check_output("echo $PATH", shell = True)
	print build_type, 
	if int(build_type) == 1:
		os.putenv("libdir",root_dir + "/lib64")
	else:
		os.putenv("libdir", root_dir + "/lib")

	os.putenv("LFS_ROOT_DIR", root_dir)
	os.putenv("sysconfdir", root_dir + "/etc")
	os.putenv("includedir", root_dir + "/usr/include")
	os.putenv("PATH", root_dir+"/bin;" + bin_path_exports)


def check_and_put_env(dict_env,keyname):
	if keyname in dict_env:
		print "Putting {0} as {1}".format(keyname, dict_env[keyname])
		evaled_env= subprocess.check_output("echo " + dict_env[keyname].strip()\
				,shell = True)
		os.putenv(keyname, evaled_env)

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
				check_and_put_env(dep.depmod, 'EXTRA_CONF')
				mod_result = get_module_code.get_module_with_code("./core-exec/" + dep.name + ".exec")
				exec_name = get_module_code.create_tmp_exec_file(mod_result[0])
				custom_cmd_dict = mod_result[1]

				for cmd in __COMMAND:
					check_and_put_env(dep.depmod, 'WORKDIR')
					check_and_put_env(dep.depmod, 'SRCDIR')
					if custom_cmd_dict["do_pre_" + cmd ]:
						subprocess.check_output(exec_name + " " + "do_pre_" + cmd\
							+" " + dep.name +"-"+dep.depmod['version'], shell = True)
					if not custom_cmd_dict["do_" + cmd ]:
						if os.system("./build_components.sh " + root_dir + " do_" + cmd \
								+ " " + dep.name +"-"+dep.depmod['version']) != 0:
							print "Halting build"
							exit(-1)
					else:
						subprocess.check_output(exec_name +" "+ "do_" + cmd + " " \
								+ dep.name +"-"+dep.depmod['version'], shell = True)
					if custom_cmd_dict["do_post_" + cmd ]:
						subprocess.check_output(exec_name + " " + "do_post_" + cmd\
							+" " + dep.name +"-"+dep.depmod['version'], shell = True)
					os.unsetenv('WORKDIR')
					os.unsetenv('SRCDIR')
				get_module_code.unlink_tmp_exec_file(exec_name)
				os.unsetenv('EXTRA_CONF')

if __name__ == "__main__":
	if ( len(sys.argv) != 2):
		print "Usage {0} <LFS_ROOT_DIRECTORY>".format(sys.argv[0]);
	else:
		do_build(sys.argv[1]);

#params = dict(sys.argv[1:])
#print "".format(params), 

