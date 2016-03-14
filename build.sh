#!/bin/sh
#Add more directories here to be in rootfs / directory.
SYSTEM_DIRS="boot root home usr usr/src tmp opt www dev tools src tools/state"

function create_system_dirs
{
	for dir in $SYSTEM_DIRS
	do
		echo "Creating $LFS_ROOTFS/$dir..."
		if [ ! -d $LFS_ROOTFS/$dir ]
		then
			mkdir $LFS_ROOTFS/$dir
		else
			echo "Set REFORMAT_ROOTFS=1 to do a clean install..."
			echo "Ignoring directory $LFS_ROOTFS/$dir. Directory exists..."
		fi;
	done
}

LFS_STATE_DIR=$LFS_ROOTFS/tools/state

if [ x$LFS_ROOTFS = x ]
then
LFS_ROOTFS=$1
fi

if [ x$LFS_ROOTFS = x ]
then
	echo "Must export LFS_ROOT or pass it as first argument"
	echo "Usage $0 [LFS_ROOT]"
	exit 1;
fi

#1 First create system directories
#if [ ! x"$REFORMAT_ROOTFS" = x ]
#then
#	rm -rfv $LFS_ROOTFS/*
#fi

create_system_dirs
echo "Downloading sources for build...."
if [ ! -e ${LFS_ROOTFS}/src/pkg_list ]
then
cp -v $(pwd)/pkg_list $LFS_ROOTFS/src/
fi;

if [ ! -e ${LFS_ROOTFS}/src/md5sums ]
then
cp -v $(pwd)/md5sums $LFS_ROOTFS/src/
fi;
./download_pkgs $LFS_ROOTFS/src
./unpack.sh $LFS_ROOTFS/src $LFS_ROOTFS/tools
#./build_components.sh $LFS_ROOTFS
