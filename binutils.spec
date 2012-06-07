
%define lib_major	2
%define lib_name_orig	%{package_prefix}%mklibname binutils
%define lib_name	%{lib_name_orig}%{lib_major}
%define	dev_name	%mklibname binutils -d

# Allow SPU support for native PowerPC arches, not cross env packages
%define spu_arches	ppc ppc64

# Define if building a cross-binutils
%define build_cross	0
%{expand: %{?cross:	%%global build_cross 1}}

%if %{build_cross}
%define target_cpu	%{cross}
%define target_platform	%{target_cpu}-linux
%if "%{target_cpu}" == "spu"
%define target_platform	%{target_cpu}-unknown-elf
%endif
%define program_prefix	%{target_platform}-
%define package_prefix	cross-%{target_cpu}-
%else
%define target_cpu	%{_target_cpu}
%define target_platform	%{_target_platform}
%define program_prefix	%{nil}
%define package_prefix	%{nil}
%endif

%define arch		%(echo %{target_cpu}|sed -e "s/\(i.86\|athlon\)/i386/" -e "s/amd64/x86_64/" -e "s/\(sun4.*\|sparcv[89]\)/sparc/")
%define isarch()	%(case %{arch} in (%1) echo 1;; (*) echo 0;; esac)

# List of targets where gold can be enabled
%define gold_arches %(echo %{ix86} x86_64 ppc ppc64 %{sparc} %{arm}|sed 's/[ ]/\|/g')

%define gold_default	0

Summary:	GNU Binary Utility Development Utilities
Name:		%{package_prefix}binutils
Version:	2.22.52.0.4
Release:	1
License:	GPLv3+
Group:		Development/Other
URL:		http://sources.redhat.com/binutils/
# official beta snapshot from http://git.kernel.org/?p=linux/kernel/git/hjl/binutils.git;a=summary
Source0:	http://ftp.kernel.org/pub/linux/devel/binutils/binutils-%{version}.tar.xz
#Source1:	http://ftp.kernel.org/pub/linux/devel/binutils/binutils-%{version}.tar.bz2.sign
Source2:	build_cross_binutils.sh
Source3:	spu_ovl.o
Source4:	embedspu.sh
Source5:	binutils-2.19.50.0.1-output-format.sed
Source10:	binutils.rpmlintrc
%if "%{name}" == "binutils"
%rename		%{lib_name}
%endif
Conflicts:	gcc-c++ < 3.2.3-1mdk
BuildRequires:	autoconf automake bison flex gcc gettext texinfo
BuildRequires:	dejagnu zlib-devel
# make check'ing requires libdl.a
BuildRequires:	glibc-static-devel >= 6:2.14.90-8
# gold make check'ing requires libstdc++.a & bc
BuildRequires:	libstdc++-static-devel bc

# Fedora patches:
Patch01:	binutils-2.20.51.0.2-libtool-lib64.patch
Patch02:	binutils-2.20.51.0.10-ppc64-pie.patch
Patch03:	binutils-2.20.51.0.2-ia64-lib64.patch
# We don't want this one!
#Patch04:	binutils-2.20.51.0.2-version.patch
Patch05:	binutils-2.20.51.0.2-set-long-long.patch
Patch06:	binutils-2.20.51.0.10-copy-osabi.patch
Patch07:	binutils-2.20.51.0.10-sec-merge-emit.patch
Patch08:	binutils-2.20.51.0.2-build-id.patch

# Mandriva patches
# (from gb, proyvind): defaults to i386 on x86_64 or ppc on ppc64 if 32 bit personality is set
Patch21:	binutils-2.22.52.0.4-linux32.patch
# (proyvind): skip gold tests that fails
Patch27:	binutils-2.21.51.0.8-skip-gold-check.patch
Patch28:	binutils-2.21.51.0.8-ld-default-settings.patch
# enables the following by default:
# --as-needed
# --hash-style=gnu
# --enable-new-dtags
# --no-undefined
# -O1
# --threads
# --warn-common
# --warn-execstack
# --warn-shared-textrel
# --warn-unresolved-symbols
# -z relro
# --build-id=sha1
# --icf=safe
Patch29:	binutils-2.21.52.0.2-ld.gold-default-settings.patch
#from Леонид Юрьев leo@yuriev.ru, posted to binutils list
Patch31:	binutils-2.22.51.0.1-fix-overrides-for-gold-testsuite.patch
Patch33:	binutils-2.21.53.0.1-ld_13048-Invalid-address-for-x32.patch
# from upstream
Patch34:	binutils-2.21.53.0.3-opcodes-missing-ifdef-enable-nls.patch

%description
Binutils is a collection of binary utilities, including:

   * ar: creating modifying and extracting from archives
   * nm: for listing symbols from object files
   * objcopy: for copying and translating object files
   * objdump: for displaying information from object files
   * ranlib: for generating an index for the contents of an archive
   * size: for listing the section sizes of an object or archive file
   * strings: for listing printable strings from files
   * strip: for discarding symbols (a filter for demangling encoded C++ symbols
   * addr2line: for converting addresses to file and line
   * nlmconv: for converting object code into an NLM

Install binutils if you need to perform any of these types of actions on
binary files.  Most programmers will want to install binutils.

%ifarch %{spu_arches}
%package -n	spu-binutils
Summary:	GNU Binary Utility Development Utilities for Cell SPU
Group:		Development/Other

%description -n	spu-binutils
This package contains the binutils with Cell SPU support.
%endif

%package -n	%{dev_name}
Summary:	Main library for %{name}
Group:		Development/Other
Provides:	%{name}-devel = %{version}-%{release}
Provides:	%{lib_name}-devel = %{version}-%{release}
Obsoletes:	%{lib_name}-devel
Requires:	zlib-devel

%description -n	%{dev_name}
This package contains BFD and opcodes static libraries and associated
header files.  Only *.a libraries are included, because BFD doesn't
have a stable ABI.  Developers starting new projects are strongly encouraged
to consider using libelf instead of BFD.

%prep
%setup -q -n binutils-%{version}
%patch01 -p0 -b .libtool-lib64~
%patch02 -p0 -b .ppc64-pie~
%ifarch ia64
%if "%{_lib}" == "lib64"
%patch03 -p0 -b .ia64-lib64~
%endif
%endif
#%%patch04 -p0 -b .version~
%patch05 -p0 -b .set-long-long~
%patch06 -p0 -b .copy-osabi~
%patch07 -p0 -b .sec-merge-emit~
%patch08 -p0 -b .build-id~
 
%patch21 -p1 -b .linux32~
#%%patch27 -p1 -b .skip_gold_check~
# we don't bother modifying the defaults for the bfd linker, we'll switch
# to gold as the default now, so let's just leave the older linker with
# the same behaviour as previous for anyone who needs to use it..
#%%patch28 -p1 -b .defaults~
%if "%{distepoch}" >= "2012"
%patch29 -p1 -b .gold_defaults~
%endif
%patch31 -p1 -b .gold_testsuite~
# later
#%%patch33 -p1 -b .ld_13048~
%patch34 -p1 -b .nls~
# for boostrapping, can be rebuilt afterwards in --enable-maintainer-mode
cp %{SOURCE3} ld/emultempl/

%build
# Additional targets
ADDITIONAL_TARGETS=""
case %{target_cpu} in
ppc | powerpc)
  ADDITIONAL_TARGETS="powerpc64-%{_target_vendor}-%{_target_os}"
  ;;
ppc64)
  ADDITIONAL_TARGETS=""
  ;;
ia64)
  ADDITIONAL_TARGETS="i586-%{_target_vendor}-%{_target_os}"
  ;;
i*86 | athlon*)
  ADDITIONAL_TARGETS="x86_64-%{_target_vendor}-%{_target_os}"
  ;;
sparc*)
  ADDITIONAL_TARGETS="sparc64-%{_target_vendor}-%{_target_os}"
  ;;
mipsel)
  ADDITIONAL_TARGETS="mips64el-%{_target_vendor}-%{_target_os}"
  ;;
mips)
  ADDITIONAL_TARGETS="mips64-%{_target_vendor}-%{_target_os}"
  ;;
esac
%ifarch %{spu_arches}
if [[ -n "$ADDITIONAL_TARGETS" ]]; then
  ADDITIONAL_TARGETS="$ADDITIONAL_TARGETS,spu-unknown-elf"
else
  ADDITIONAL_TARGETS="spu-unknown-elf"
fi
%endif
if [[ -n "$ADDITIONAL_TARGETS" ]]; then
  TARGET_CONFIG="$TARGET_CONFIG --enable-targets=$ADDITIONAL_TARGETS"
fi

case %{target_cpu} in
ppc | powerpc | i*86 | athlon* | sparc* | mips* | s390* | sh* | arm*)
  TARGET_CONFIG="$TARGET_CONFIG --enable-64-bit-bfd"
  ;;
esac

%if "%{name}" != "binutils"
%define _program_prefix %{program_prefix}
TARGET_CONFIG="$TARGET_CONFIG --target=%{target_platform}"
%endif

# Don't build shared libraries in cross binutils
%if "%{name}" == "binutils"
TARGET_CONFIG="$TARGET_CONFIG --enable-shared --with-pic"
%endif

# Binutils comes with its own custom libtool
# [gb] FIXME: but system libtool also works and has relink fix
%define __libtoolize /bin/true

# Build main binaries
rm -rf objs
mkdir objs
pushd objs
CONFIGURE_TOP=.. %configure2_5x $TARGET_CONFIG	--with-bugurl=http://qa.mandriva.com/ \
%if %{gold_default}
						--enable-ld=yes \
						--enable-gold=default \
%else
						--enable-ld=default \
						--enable-gold=yes \
%endif
						--enable-plugins \
						--enable-threads \
%if "%{_lib}" == "lib64"
						--with-lib-path=/%{_lib}:%{_libdir}:%{_prefix}/local/%{_lib}:/lib:%{_prefix}/lib:%{_prefix}/local/lib \
%else
						--with-lib-path=/lib:%{_prefix}/lib:%{_prefix}/local/lib \
%endif
%ifarch armv7l armv7hl
						--with-cpu=cortex-a8 \
						--with-tune=cortex-a8 \
						--with-arch=armv7-a \
						--with-mode=thumb \
%ifarch armv7l
						--with-float=softfp \
%else
						--with-float=hard \
%endif
						--with-fpu=vfpv3-d16 \
						--with-abi=aapcs-linux \
%endif
						--disable-werror \
						--with-separate-debug-dir=%{_prefix}/lib/debug
# There seems to be some problems with builds of gold randomly failing whenever
# going through the build system, so let's try workaround this by trying to do
# make once again when it happens...
%make tooldir=%{_prefix} || make tooldir=%{_prefix}
make -C bfd/doc html
mkdir -p ../html
cp -f bfd/doc/bfd.html/* ../html
popd

# Build alternate binaries (spu-gas in particular)
case "$ADDITIONAL_TARGETS," in
%ifarch %{spu_arches}
*spu-*-elf,*)
  ALTERNATE_TARGETS="spu-unknown-elf"
  ;;
%endif
*)
  ;;
esac
if [[ -n "$ALTERNATE_TARGETS" ]]; then
  for target in $ALTERNATE_TARGETS; do
    cpu=`echo "$target" | sed -e "s/-.*//"`
    rm -rf objs-$cpu
    mkdir objs-$cpu
    pushd objs-$cpu
    CONFIGURE_TOP=.. %configure	--enable-shared \
				--target=$target \
				--program-prefix=$cpu- \
%if "%{distepoch}" < "2012"
				--enable-ld=default \
				--enable-gold=yes \
%else
				--enable-ld=yes \
				--enable-gold=default \
%endif
				--disable-werror \
				--with-bugurl=http://qa.mandriva.com/
    # make sure we use the fully built libbfd & libopcodes libs
    # XXX could have been simpler to just pass $ADDITIONAL_TARGETS
    # again to configure and rebuild all of those though...
    for dso in bfd opcodes; do
    %make all-$dso
    rm -f $dso/.libs/lib$dso-%{version}.so
    ln -s ../../../objs/$dso/.libs/lib$dso-%{version}.so $dso/.libs/
    done
    %make all-binutils all-gas all-ld
    popd
  done
fi

%check
# All Tests must pass on x86 and x86_64
echo ====================TESTING=========================
# workaround for not using colorgcc when building due to colorgcc
# messes up output redirection..
PATH=${PATH#%{_datadir}/colorgcc:}
%if %isarch i386|x86_64|ppc|ppc64|spu
%make -k -C objs check CFLAGS="" CXXFLAGS="" LDFLAGS="" || :
[[ -d objs-spu ]] && \
%make -C objs-spu check-gas CFLAGS="" CXXFLAGS="" LDFLAGS=""
%else
%make -C objs -k check CFLAGS="" CXXFLAGS="" LDFLAGS="" || echo make check failed
%endif
echo ====================TESTING END=====================

logfile="%{name}-%{version}-%{release}.log"
rm -f $logfile; find . -name "*.sum" | xargs cat >> $logfile

%install
mkdir -p %{buildroot}%{_prefix}
%makeinstall_std -C objs

rm -f %{buildroot}%{_mandir}/man1/{dlltool,nlmconv,windres}*
rm -f %{buildroot}%{_infodir}/dir
rm -f %{buildroot}%{_libdir}/*.la
rm -f %{buildroot}%{_libdir}/lib{bfd,opcodes}.so

%if "%{name}" == "binutils"
make -C objs prefix=%{buildroot}%{_prefix} infodir=%{buildroot}%{_infodir} install-info
install -m 644 include/libiberty.h %{buildroot}%{_includedir}/
if [ -e objs/libiberty/pic/libiberty.a ]; then
	# Ship with the PIC libiberty
	install -m 644 objs/libiberty/pic/libiberty.a %{buildroot}%{_libdir}/
else
	install -m 644 objs/libiberty/libiberty.a %{buildroot}%{_libdir}/
fi
rm -rf %{buildroot}%{_prefix}/%{_target_platform}/

# Sanity check --enable-64-bit-bfd really works.
grep '^#define BFD_ARCH_SIZE 64$' %{buildroot}%{_prefix}/include/bfd.h
# Fix multilib conflicts of generated values by __WORDSIZE-based expressions.
%ifarch %{ix86} x86_64 ppc ppc64 s390 s390x sh3 sh4 sparc sparc64 %arm
sed -i -e '/^#include "ansidecl.h"/{p;s~^.*$~#include <bits/wordsize.h>~;}' \
    -e 's/^#define BFD_DEFAULT_TARGET_SIZE \(32\|64\) *$/#define BFD_DEFAULT_TARGET_SIZE __WORDSIZE/' \
    -e 's/^#define BFD_HOST_64BIT_LONG [01] *$/#define BFD_HOST_64BIT_LONG (__WORDSIZE == 64)/' \
    -e 's/^#define BFD_HOST_64_BIT \(long \)\?long *$/#if __WORDSIZE == 32\
#define BFD_HOST_64_BIT long long\
#else\
#define BFD_HOST_64_BIT long\
#endif/' \
    -e 's/^#define BFD_HOST_U_64_BIT unsigned \(long \)\?long *$/#define BFD_HOST_U_64_BIT unsigned BFD_HOST_64_BIT/' \
    %{buildroot}%{_prefix}/include/bfd.h
%endif
touch -r bfd/bfd-in2.h %{buildroot}%{_prefix}/include/bfd.h

# Generate .so linker scripts for dependencies; imported from glibc/Makerules:

# This fragment of linker script gives the OUTPUT_FORMAT statement
# for the configuration we are building.
OUTPUT_FORMAT="\
/* Ensure this .so library will not be used by a link for a different format
   on a multi-architecture system.  */
$(gcc $CFLAGS $LDFLAGS -shared -x c /dev/null -o /dev/null -Wl,--verbose -v 2>&1 | sed -n -f "%{SOURCE5}")"

tee %{buildroot}%{_libdir}/libbfd.so <<EOH
/* GNU ld script */

$OUTPUT_FORMAT

/* The libz dependency is unexpected by legacy build scripts.  */
INPUT ( %{_libdir}/libbfd.a -liberty -lz )
EOH

tee %{buildroot}%{_libdir}/libopcodes.so <<EOH
/* GNU ld script */

$OUTPUT_FORMAT

INPUT ( %{_libdir}/libopcodes.a -lbfd -lz )
EOH

%else
rm -f  %{buildroot}%{_libdir}/libiberty.a
rm -rf %{buildroot}%{_infodir}
rm -rf %{buildroot}%{_datadir}/locale/
rm -f  %{buildroot}%{_prefix}/%{_target_platform}/%{target_cpu}-linux/lib/*.la
%endif

%if "%{name}" == "binutils"
%find_lang binutils --all-name
%endif

# Alternate binaries
[[ -d objs-spu ]] && {
destdir=`mktemp -d`
make -C objs-spu DESTDIR=$destdir install-binutils install-gas install-ld
mv $destdir%{_bindir}/spu-* %{buildroot}%{_bindir}/
mkdir -p %{buildroot}%{_prefix}/spu/bin
mv $destdir%{_prefix}/spu-unknown-elf/bin/* %{buildroot}%{_prefix}/spu/bin/
rm -rf $destdir
cat > %{buildroot}%{_bindir}/ppu-as << EOF
#!/bin/sh
exec %{_bindir}/as -mcell -maltivec \${1+"\$@"}
EOF
chmod +x %{buildroot}%{_bindir}/ppu-as
install -m 755 %{SOURCE4} %{buildroot}%{_bindir}/embedspu
}

%if "%{name}" == "binutils"
%files -f binutils.lang
%else
%files
%endif
%{_bindir}/%{program_prefix}addr2line
%{_bindir}/%{program_prefix}ar
%{_bindir}/%{program_prefix}as
%{_bindir}/%{program_prefix}c++filt
%{_bindir}/%{program_prefix}elfedit
%{_bindir}/%{program_prefix}gprof
%{_bindir}/%{program_prefix}ld
%{_bindir}/%{program_prefix}ld.bfd
%if %isarch %{gold_arches}
%{_bindir}/%{program_prefix}ld.gold
%endif
%{_bindir}/%{program_prefix}nm
%{_bindir}/%{program_prefix}objcopy
%{_bindir}/%{program_prefix}objdump
%{_bindir}/%{program_prefix}ranlib
%{_bindir}/%{program_prefix}readelf
%{_bindir}/%{program_prefix}size
%{_bindir}/%{program_prefix}strings
%{_bindir}/%{program_prefix}strip
%ifarch %{spu_arches}
%{_bindir}/ppu-as
%endif
%{_mandir}/man1/*
%if "%{name}" == "binutils"
%{_infodir}/*info*
%{_libdir}/libbfd-%{version}*.so
%{_libdir}/libopcodes-%{version}*.so
%else
%{_prefix}/%{target_platform}/bin/*
%{_prefix}/%{target_platform}/lib/ldscripts
%endif

%ifarch %{spu_arches}
%files -n spu-binutils
%{_bindir}/spu-*
%{_bindir}/embedspu
%dir %{_prefix}/spu/bin
%{_prefix}/spu/bin
%endif

%if "%{name}" == "binutils"
%files -n %{dev_name}
%doc html
%{_includedir}/*.h
%{_libdir}/libbfd.a
%{_libdir}/libbfd.so
%{_libdir}/libopcodes.a
%{_libdir}/libopcodes.so
%{_libdir}/libiberty.a
%endif
