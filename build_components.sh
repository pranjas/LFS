#!/bin/sh
LFS_ROOT_DIR=$1
LFS_SRC_DIR=$LFS_ROOT_DIR/src/src
LFS_BUILD_DIR=$LFS_ROOT_DIR/tools/
LFS_CONFIGURE_PREFIX=$LFS_ROOT_DIR

COMPONENTS=$(find $LFS_BUILD_DIR -maxdepth 1 -mindepth 1 -type d)

BUILD_TYPE=
DEFAULT_BUILD_TYPE=i686

function do_build_type
{
if [ x"$BUILD_TYPE" = x ]
then
	if [ $(uname -m | grep 64 | wc -l) -eq 0 ]
	then
		BUILD_TYPE=i686
	else
		BUILD_TYPE=$(uname -m)
	fi
fi
}

function do_configure_all
{
do_build_type
for comp in $COMPONENTS
do
	if [ ! -d $comp ]
	then
		continue;
	fi;
	do_configure_one $comp
done
}


function do_configure_one
{
	do_build_type
	cd $LFS_BUILD_DIR/$1
	if [ ! -e configure ]
	then
		if [ ! -e configure.ac ]
		then
			echo "Component $component doesn't have configure or configure.ac"
			echo "Continuing without configuring $component ..."
			continue;
		else #configure.ac exists.
			autoreconf -i --prefix=$LFS_CONFIGURE_PREFIX;
		fi
	else #configure  exists.
		#Do nothing.
		echo "" > /dev/null
	fi
	set -x;
	./configure --prefix=$LFS_CONFIGURE_PREFIX --build=$BUILD_TYPE --host=$(uname -m) \
			--with-sysroot=$LFS_ROOT_DIR $EXTRA_CONF
	if [ $? -eq 0 ]
	then
		make && make install 2>&1 > $LFS_BUILD_DIR/$1.log
	fi;
	set +x


	cd -

}
_cmd=$2
shift
shift
$_cmd $*
