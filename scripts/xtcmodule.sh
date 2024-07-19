chmod 777 /data/adb/magisk/busybox
DATABIN="/data/adb/magisk"
BBPATH="/data/adb/magisk/busybox"
UTIL_FUNCTIONS_SH="$DATABIN/util_functions.sh"
export OUTFD=1
export ZIPFILE="/sdcard/xtcme.zip"
export ASH_STANDALONE=1
"$BBPATH" sh -c ". \"$UTIL_FUNCTIONS_SH\"; install_module"