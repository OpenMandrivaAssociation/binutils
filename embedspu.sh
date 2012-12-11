#!/bin/sh 

# (C)Copyright                                                    
# Sony Computer Entertainment, Inc.,                              
# 2005,2005.  All rights reserved.                                

#
# Embed SPE ELF executable into PPE object file, and define a
# global pointer variable refering to the embedded file.
#
# Usage: embedspu [flags] symbol_name input_filename output_filename
#
#        input_filename:  SPE ELF executable to be embedded
#        output_filename: Resulting PPE object file
#        symbol_name:     Name of global pointer variable to be defined
#        flags:           GCC flags defining PPE object file format
#                         (e.g. -m32 or -m64)
#

# Determine location of dependent utilities
file=`basename "$0"`
dir=`dirname "$0"`
[ "${file#ppu-}" != "$file" ] && PREFIX=ppu-

PPU_GCC=${PREFIX}gcc
SPU_READELF=spu-readelf

which $PPU_GCC > /dev/null 2>&1
if [ $? -eq 0 ]
then
	:
elif [ -a ${dir}/$PPU_GCC ]
then
	PPU_GCC=${dir}/$PPU_GCC
elif [ -a /opt/cell/ppu/bin/$PPU_GCC ]
then
	PPU_GCC=/opt/cell/ppu/bin/$PPU_GCC
else
	echo Cannot find $PPU_GCC.
	exit 1
fi

which $SPU_READELF > /dev/null 2>&1
if [ $? -eq 0 ]
then
	:
elif [ -a ${dir}/$SPU_READELF ]
then
	SPU_READELF=${dir}/$SPU_READELF
elif [ -a /opt/cell/spu/bin/$SPU_READELF ]
then
	SPU_READELF=/opt/cell/spu/bin/$SPU_READELF
else
	echo Cannot find $SPU_READELF.
	exit 1
fi

# Argument parsing
SYMBOL=
INFILE=
OUTFILE=
FLAGS=

while [ -n "$1" ]; do
  case $1 in
    -*) FLAGS="${FLAGS} $1"
	shift ;;
    *)  if [ -z $SYMBOL ]; then
	  SYMBOL=$1
	elif [ -z $INFILE ]; then
	  INFILE=$1
	elif [ -z $OUTFILE ]; then
	  OUTFILE=$1
	fi
	shift ;;
  esac
done

if [ -z "$SYMBOL" -o -z "$INFILE" -o -z "$OUTFILE" ]; then
  echo "Usage: $0 [symbol_name] [input_filename] [output_filename]"
  exit 1
fi

if [ ! -e "$INFILE" ]; then
  echo "${INFILE}: File not found"
  exit 1
fi

${PPU_GCC} ${FLAGS} -x assembler-with-cpp -nostartfiles -nostdlib \
	-Wl,-r -Wl,-x -o ${OUTFILE} - <<EOF
.section .rodata.speelf,"a",@progbits
.p2align 7
__speelf__:
.incbin "${INFILE}"

.section .data.spetoe,"aw",@progbits
.p2align 7
__spetoe__:
`${SPU_READELF} -s ${INFILE} | egrep ' _EAR_' | sort -k 2 | awk \
'$8 == "_EAR_" { \
	print "#ifdef _LP64"; \
	print ".quad __speelf__"; \
	print ".quad 0"; \
	print "#else"; \
	print ".int 0"; \
	print ".int __speelf__"; \
	print ".int 0"; \
	print ".int 0"; \
	print "#endif"; \
} \
$8 != "_EAR_" { \
	print "#ifdef _LP64"; \
	print ".quad " substr($8, 6); \
	print ".quad 0"; \
	print "#else"; \
	print ".int 0"; \
	print ".int " substr($8, 6); \
	print ".int 0"; \
	print ".int 0"; \
	print "#endif"; \
}'`

.section .data,"aw",@progbits
.globl ${SYMBOL}
${SYMBOL}:
# fill in a struct spe_program_handle
#ifdef _LP64
.int 24
.int 0
.quad __speelf__
.quad __spetoe__
#else
.int 12
.int __speelf__
.int __spetoe__
#endif
EOF
