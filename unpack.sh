#!/bin/sh

LFS_SRC_DIR=$1/src
LFS_BUILD_DIR=$2

function do_unpack
{
	local file_name=$1;
	local _fname=$(echo $file_name| rev| cut -f1 -d'/'|rev)
	local comp_dir=$(echo $1 | cut -f1 -d'.')
	local extension=$(echo $1 | rev | cut -f1 -d'.' | rev)
	local unpack_opt=
	case "$extension" in
		xz)
			unpack_opt=J
		;;
		bz2|bz)
			unpack_opt=j
		;;
		gz)
			unpack_opt=z
		;;
	esac
	set -x;
	echo $"Unpacking $1 ..."
	if [ ! -e $LFS_BUILD_DIR/state/${_fname}_done ]
	then
		tar  -${unpack_opt}xvkf  $1 -C $LFS_BUILD_DIR --no-ignore-command-error
		touch $LFS_BUILD_DIR/state/${_fname}_done
	fi;
	if [ ! $? -eq 0 ]
	then
		echo "Directory already exists..."
	fi
	set +x;
}

if [ x$LFS_SRC_DIR = x ] || [ x"$LFS_BUILD_DIR" = x ]
then
	echo "Usage $0 <LFS_SRC_DIR> <LFS_BUILD_DIR>"
	exit 1;
else
	if [ -e $LFS_BUILD_DIR/.lfs_components ]
	then
		rm -fv $LFS_BUILD_DIR/.lfs_components
	fi

	for f in $(ls $LFS_SRC_DIR)
	do
		echo "Looking for files in $LFS_SRC_DIR ..."
		do_unpack $LFS_SRC_DIR/$f

	done

	for dir in $(find $LFS_BUILD_DIR -maxdepth 1 -mindepth 1 -type d)
	do
		if [ ! -d $dir ]
		then
			continue;
		fi;
		_dir=$(echo $dir | rev  | cut -f1 -d'/'| rev)
		echo $_dir >> $LFS_BUILD_DIR/.lfs_components 
	done
fi
