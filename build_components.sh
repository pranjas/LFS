#!/bin/sh
LFS_ROOT_DIR=$1
LFS_SRC_DIR=$LFS_ROOT_DIR/src/src
LFS_BUILD_DIR=$LFS_ROOT_DIR/tools/
LFS_CONFIGURE_PREFIX=$LFS_ROOT_DIR
LFS_COMPONENT_STATE_DIR=$LFS_BUILD_DIR/state

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

function do_clean
{
	set -x;
	if [ x"$SRCDIR" = x ]
	then
		SRCDIR=$LFS_BUILD_DIR/$1
	fi

	if [ x"$WORKDIR" = x ]
	then
		WORKDIR=$SRCDIR
	fi

	cd $WORKDIR
	make distclean
	cd -;
	set +x;
}

function do_configure
{
	do_build_type
	local config_log_file=$LFS_COMPONENT_STATE_DIR/$1/configure.log_$(date +%d_%m_%y)
	if [ ! -d $LFS_COMPONENT_STATE_DIR/$1 ]
	then
		mkdir -p $LFS_COMPONENT_STATE_DIR/$1
	fi
	local force=0
	local retval=0;
	if [ x"$SRCDIR" = x ]
	then
		SRCDIR=$LFS_BUILD_DIR/$1
	fi

	if [ x"$WORKDIR" = x ]
	then
		WORKDIR=$SRCDIR
	fi

	for arg in $(echo $*)
	do
		if [ "$arg" = "-f" ]
		then
			force=1;
			break;
		fi
	done

set -x;
	if [ -e $LFS_COMPONENT_STATE_DIR/$1/.configure ] && [ ! $force -eq 1 ]
	then
		echo "Component $1 is already configured. Use -f to force"
		return $retval
	fi

	if [ ! -d $WORKDIR ]
	then
		mkdir -p $WORKDIR
	fi

	cd $WORKDIR
	if [ ! -e $SRCDIR/configure ]
	then
		if [ ! -e $SRCDIR/configure.ac ]
		then
			echo "Component $component doesn't have configure or configure.ac"
			echo "Continuing without configuring $component ..."
			continue;
		else #configure.ac exists.
			echo "Configure log present in $confile_log_file"
			autoreconf -i --prefix=$LFS_CONFIGURE_PREFIX 2>&1 | tee $config_log_file
			ln -s $config_log_file $LFS_COMPONENT_STATE_DIR/$1/configure.log
		fi
	else #configure  exists.
		#Do nothing.
		echo "" > /dev/null
	fi
set +x;
	set -x;
	$SRCDIR/configure --prefix=$LFS_CONFIGURE_PREFIX --build=$BUILD_TYPE --host=$(uname -m) \
			--with-sysroot=$LFS_ROOT_DIR $EXTRA_CONF 2>&1 | tee -a $config_log_file
	retval=$?
	if [ $? -eq 0 ]
	then
		touch $LFS_COMPONENT_STATE_DIR/$1/.configure
	fi
	set +x;
	cd -;
	return $retval;
}

function do_compile
{
	local force=0;
	if [ x"$SRCDIR" = x ]
	then
		SRCDIR=$LFS_BUILD_DIR/$1
	fi

	if [ x"$WORKDIR" = x ]
	then
		WORKDIR=$SRCDIR
	fi
	
	for arg in $(echo $*)
	do
		if [ "$arg" = "-f" ]
		then
			force=1;
			break;
		fi
	done

	if [ -e $LFS_COMPONENT_STATE_DIR/$1/.compile ] && [ ! $force -eq 1 ]
	then
		echo "Component $1 is already configured. Use -f to force"
		return 0
	fi

	cd $WORKDIR
	set -x;
		make
	if [ $? -eq 0 ]
	then
		touch $LFS_COMPONENT_STATE_DIR/$1/.compile
	fi
	set +x
	cd -
}

function do_install
{
	local force=0;
	if [ x"$SRCDIR" = x ]
	then
		SRCDIR=$LFS_BUILD_DIR/$1
	fi

	if [ x"$WORKDIR" = x ]
	then
		WORKDIR=$SRCDIR
	fi
	for arg in $(echo $*)
	do
		if [ "$arg" = "-f" ]
		then
			force=1;
			break;
		fi
	done
	cd $WORKDIR
	set -x;
		if [ ! -e $LFS_COMPONENT_STATE_DIR/$1/.compile ] || [ $force -eq 1 ]
		then
			make install
		fi
	set +x
	cd -
}
_cmd=$2
shift
shift
$_cmd $*
