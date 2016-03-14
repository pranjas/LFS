#!/bin/sh

# Update this comment
# -f to force
# -c for which command to run

commands=("fetch" "configure" "compile" "install" "package")

force_cmd=false;
options_supported=":fc:"
cmd=

function check_options
{
	local OPTIND
	while getopts $options_supported opt
	do
		case $opt in
			f) 
				force_cmd=true;
			;;
			c)
				cmd=$OPTARG
			;;
			\?)
				echo "Invalid option -$OPTARG"
				return $(false);
			;;
			:)
				echo "Option -$OPTARG needs an argument"
				return $(false);
			;;
		esac
	done
	shift $(($OPTIND - 1))
	return $(true)
}

function run_command
{
	check_options "$*"
	chk_opt=$?
	if [ $chk_opt -eq  0 ] #0 means command was success
	then
		$cmd
		return $?
	else
		return $(false);
	fi
}
set -x
shift
run_command $*
set +x;
