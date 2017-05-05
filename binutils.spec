%define _disable_lto 1
#define cross aarch64-linux-gnu

%define lib_major 2
%define lib_name_orig %{package_prefix}%mklibname binutils
%define lib_name %{lib_name_orig}%{lib_major}
%define dev_name %mklibname binutils -d

# Allow SPU support for native PowerPC arches, not cross env packages
%define spu_arches ppc ppc64

# Define if building a cross-binutils
%define build_cross 0
%{expand: %{?cross:	%%global build_cross 1}}

%if %{build_cross}
%define target_cpu %{cross}
%global	target_platform	%(rpm --macros %%{_usrlibrpm}/macros:%%{_usrlibrpm}/platform/%{target_cpu}-%{_target_os}/macros --target=%{target_cpu} -E %%{_target_platform})
%if "%{target_cpu}" == "spu"
%define target_platform %{target_cpu}-unknown-elf
%endif
%define program_prefix %{target_platform}-
%define package_prefix cross-%{target_cpu}-
%define	_srcrpmfilename	binutils-%{version}-%{release}.src.rpm
%else
%define target_cpu %{_target_cpu}
%define target_platform %{_target_platform}
%define program_prefix %{nil}
%define package_prefix %{nil}
%endif

%define arch		%(echo %{target_cpu}|sed -e "s/\(i.86\|athlon\)/i386/" -e "s/amd64/x86_64/" -e "s/\(sun4.*\|sparcv[89]\)/sparc/")
%define isarch()	%(case " %* " in (*" %{arch} "*) echo 1;; (*) echo 0;; esac)
# List of targets where gold can be enabled
%define gold_arches %(echo %{ix86} x86_64 ppc ppc64 %{sparc} %{armx}|sed 's/[ ]/\|/g')

%define gold_default 1

%if %mdvver > 3000000
# (tpg) enable LLD linker only on newer than 3.0x
%bcond_without default_lld
%endif

%bcond_without gold

%define ver 2.28
%define linaro %{nil}
%define linaro_spin 0

Summary:	GNU Binary Utility Development Utilities
Name:		%{package_prefix}binutils
%if "%{linaro}" != ""
Version:	%{ver}_%{linaro}
Source0:	http://abe.tcwglab.linaro.org/snapshots/binutils-linaro-%{ver}-%{linaro}%{?linaro_spin:-%{linaro_spin}}.tar.xz
%else
Version:	%{ver}
Source0:	ftp://ftp.gnu.org/gnu/binutils/binutils-%{version}%{?DATE:-%{DATE}}.tar.gz
%endif
Epoch:		1
Release:	2
License:	GPLv3+
Group:		Development/Other
URL:		http://sources.redhat.com/binutils/
#Source1:	http://ftp.kernel.org/pub/linux/devel/binutils/binutils-%{version}.tar.xz.sign
Source2:	build_cross_binutils.sh
Source3:	spu_ovl.o
Source4:	embedspu.sh
Source5:	http://pkgs.fedoraproject.org/cgit/rpms/binutils.git/plain/binutils-2.19.50.0.1-output-format.sed
Source10:	binutils.rpmlintrc
# Wrapper scripts for ar, ranlib and nm that know how to deal with
# LTO bytecode, regardless of whether it's gcc or clang
Source100:	ar
Source101:	ranlib
Source102:	nm
%if "%{name}" == "binutils"
%rename		%{lib_name}
%endif
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	gcc
BuildRequires:	gettext
BuildRequires:	texinfo
BuildRequires:	dejagnu
BuildRequires:	zlib-devel
# make check'ing requires libdl.a
BuildRequires:	glibc-static-devel >= 6:2.14.90-8
# gold make check'ing requires libstdc++.a & bc
BuildRequires:	libstdc++-static-devel
BuildRequires:	bc
BuildRequires:	pkgconfig(isl)
BuildRequires:	pkgconfig(cloog-isl)

# Fedora patches:
Patch01:	http://pkgs.fedoraproject.org/cgit/rpms/binutils.git/plain/binutils-2.20.51.0.2-libtool-lib64.patch
Patch02:	http://pkgs.fedoraproject.org/cgit/rpms/binutils.git/plain/binutils-2.20.51.0.10-ppc64-pie.patch
Patch03:	http://pkgs.fedoraproject.org/cgit/rpms/binutils.git/plain/binutils-2.20.51.0.2-ia64-lib64.patch
# We don't want this one!
#Patch04:	binutils-2.20.51.0.2-version.patch
Patch05:	http://pkgs.fedoraproject.org/cgit/rpms/binutils.git/plain/binutils-2.25-set-long-long.patch
Patch07:	http://pkgs.fedoraproject.org/cgit/rpms/binutils.git/plain/binutils-2.20.51.0.10-sec-merge-emit.patch
# we already set our own set of defaults...
# Enable -zrelro by default: BZ #621983
#Patch08:	binutils-2.22.52.0.1-relro-on-by-default.patch
Patch08:	http://pkgs.fedoraproject.org/cgit/rpms/binutils.git/plain/binutils-2.25.1-cleansweep.patch
# Local patch - export demangle.h with the binutils-devel rpm.
Patch09:	http://pkgs.fedoraproject.org/cgit/rpms/binutils.git/plain/binutils-2.22.52.0.1-export-demangle.h.patch
# Disable checks that config.h has been included before system headers.  BZ #845084
Patch10:	http://pkgs.fedoraproject.org/cgit/rpms/binutils.git/plain/binutils-2.22.52.0.4-no-config-h-check.patch
# Fix detections little endian PPC shared libraries
Patch19:	http://pkgs.fedoraproject.org/cgit/rpms/binutils.git/plain/binutils-2.24-ldforcele.patch
# already in our more recent version
#Patch21:	binutils-2.24-fat-lto-objects.patch
Patch24:	http://pkgs.fedoraproject.org/cgit/rpms/binutils.git/plain/binutils-2.26-fix-compile-warnings.patch
Patch26:	http://pkgs.fedoraproject.org/cgit/rpms/binutils.git/plain/binutils-2.26-lto.patch
# already in our more recent version
#Patch28:	http://pkgs.fedoraproject.org/cgit/rpms/binutils.git/plain/binutils-2.27-local-dynsym-count.patch
#Patch29:	http://pkgs.fedoraproject.org/cgit/rpms/binutils.git/plain/binutils-2.27-monotonic-section-offsets.patch

# Mandriva patches
# (from gb, proyvind): defaults to i386 on x86_64 or ppc on ppc64 if 32 bit personality is set
Patch121:	binutils-2.25.51-linux32.patch
# (proyvind): skip gold tests that fails
Patch127:	binutils-2.21.51.0.8-skip-gold-check.patch
Patch128:	binutils-2.24.51.0.3.ld-default.settings.patch
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
# --build-id=sha1
# --icf=safe
Patch129:	binutils-2.24-2013-10-04.ld.gold-default-setttings.patch
# https://bugs.linaro.org/show_bug.cgi?id=1652
Patch130:	binutils-2015.01-linaro-bug1652.patch
# musl's libintl is good enough, we don't need the internal copy
Patch132:	binutils-2015.01-accept-musl-libintl.patch

#from Леонид Юрьев leo@yuriev.ru, posted to binutils list
Patch131:	binutils-2.25.51-fix-overrides-for-gold-testsuite.patch
Patch133:	binutils-2.21.53.0.1-ld_13048-Invalid-address-for-x32.patch
# from upstream
Patch134:	binutils-2.21.53.0.3-opcodes-missing-ifdef-enable-nls.patch
Patch135:	binutils-2.25.51-lto.patch

Patch136:	binutils-2.27.90-fix-warnings.patch

%if %{with default_lld}
Requires:	lld
%endif

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
Obsoletes:	%{lib_name}-devel <= %{version}-%{release}
Requires:	zlib-devel

%description -n	%{dev_name}
This package contains BFD and opcodes static libraries and associated
header files.  Only *.a libraries are included, because BFD doesn't
have a stable ABI.  Developers starting new projects are strongly encouraged
to consider using libelf instead of BFD.

%prep
%if "%{linaro}" != ""
%setup -q -n binutils-linaro-%{ver}-%{linaro}%{?linaro_spin:-%{linaro_spin}}
%else
%setup -q -n binutils-%{version}%{?DATE:-%{DATE}}
%endif
%patch01 -p1 -b .libtool-lib64~
# Needs porting, and we don't care about the target for now
#patch02 -p1 -b .ppc64-pie~
%if %isarch ia64
%if "%{_lib}" == "lib64"
%patch03 -p0 -b .ia64-lib64~
%endif
%endif
%patch05 -p1 -b .set-long-long~
%patch07 -p1 -b .sec-merge-emit~
%patch08 -p0 -b .cleansweep~
%patch09 -p1 -b .export-demangle-h~
%patch10 -p1 -b .no-config-h-check~
%if %isarch ppc64le
%patch19 -p0 -b .ldforcele~
%endif
#patch21 -p1 -b .fatlto~
%patch24 -p1 -b .warn~
%patch26 -p1 -b .lto~

%patch121 -p1 -b .linux32~
# Modify the defaults of the BFD linker as well, since many
# things fall back to it...
%patch128 -p1 -b .defaults~
%patch129 -p1 -b .gold_defaults~
%if "%{linaro}" != ""
%patch130 -p1 -b .1652~
%endif
%patch131 -p1 -b .gold_testsuite~
%patch132 -p1 -b .musl~
# later
#%%patch33 -p1 -b .ld_13048~
%patch134 -p1 -b .nls~
%patch135 -p1 -b .lto~
%patch136 -p1 -b .warnings~

# Need to regenerate lex files
rm -f binutils/syslex.c binutils/arlex.c binutils/deflex.c gas/config/bfin-lex.c gas/itbl-lex.c ld/ldlex.c

# Some distributions (e.g. Fedora 23 for Opteron A1100) use 64 kB pages on aarch64.
# Adjust the page size so binaries built with our toolchain can run there.
sed -i -e '/#define.*ELF_COMMONPAGESIZE/s/0x1000$/0x10000/' bfd/elf*ppc.c
sed -i -e '/#define.*ELF_COMMONPAGESIZE/s/0x1000$/0x10000/' bfd/elf*aarch64.c
sed -i -e '/common_pagesize/s/4 /64 /' gold/powerpc.cc
sed -i -e '/pagesize/s/0x1000,/0x10000,/' gold/aarch64.cc
# Build libbfd.so and libopcodes.so with -Bsymbolic-functions if possible.
sed -i -e 's/^libbfd_la_LDFLAGS = /&-Wl,-Bsymbolic-functions /' bfd/Makefile.{am,in}
sed -i -e 's/^libopcodes_la_LDFLAGS = /&-Wl,-Bsymbolic-functions /' opcodes/Makefile.{am,in}

# for boostrapping, can be rebuilt afterwards in --enable-maintainer-mode
cp %{SOURCE3} ld/emultempl/

# glibc and musl have gettext built in -- no need to bundle
# another copy...
#rm -rf intl/*.h
#for i in intl/*.c; do
#	rm -f $i
#	touch $i
#done

find -name \*.h -o -name \*.c -o -name \*.cc | xargs chmod 644

# (proyvind): for weird reasons, gold testsuite failes building on arm with
# 'execvp: /bin/sh: Argument list too long' when invoking make...
%ifarch %{arm}
sed -e 's#2\.64#2.69#g' -i config/override.m4 gold/configure.ac configure.ac
sed -e 's#testsuite##g' -i gold/Makefile.am
find gold -name Makefile.in|xargs rm -f
cd gold
autoreconf -fiv
%endif

%if "%{_lib}" != "lib"
# Fix bogus lib hardcodes...
sed -i -e 's,/lib/,/%{_lib}/,g' bfd/plugin.c
sed -i -e 's,tooldir)/lib,tooldir)/%{_lib},g' gold/Makefile.*
%endif

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
arm*)
  #ADDITIONAL_TARGETS="aarch64-linux-gnu"
  ;;
aarch64*)
  #ADDITIONAL_TARGETS="armv7hl-linux-gnueabihf"
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
ppc | powerpc | i*86 | athlon* | sparc* | mips* | s390* | sh* | arm* | aarch64)
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
export CC="%{__cc} -D_GNU_SOURCE=1 -DHAVE_DECL_ASPRINTF=1"
export CXX="%{__cxx} -D_GNU_SOURCE=1"
CONFIGURE_TOP=.. %configure $TARGET_CONFIG	--with-bugurl=%{bugurl} \
%if %{with gold}
%if %{gold_default}
						--enable-ld=yes \
						--enable-gold=default \
%else
						--enable-ld=default \
						--enable-gold=yes \
%endif
%else
						--enable-ld=default \
						--disable-gold \
%endif
						--enable-plugins \
						--enable-threads \
%if "%{_lib}" == "lib64"
						--with-lib-path=/%{_lib}:%{_libdir}:%{_prefix}/local/%{_lib}:/lib:%{_prefix}/lib:%{_prefix}/local/lib \
%else
						--with-lib-path=/lib:%{_prefix}/lib:%{_prefix}/local/lib \
%endif
%if %isarch armv7l armv7hl
						--with-cpu=cortex-a8 \
						--with-tune=cortex-a8 \
						--with-arch=armv7-a \
						--with-mode=thumb \
%if %isarch armv7l
						--with-float=softfp \
%else
						--with-float=hard \
%endif
						--with-fpu=vfpv3-d16 \
						--with-abi=aapcs-linux \
%endif
%if "%{distepoch}" < "2015"
%ifnarch %{ix86}
						--enable-lto \
%endif
%endif
						--disable-werror \
						--enable-static \
						--enable-relro \
						--with-separate-debug-dir=%{_prefix}/lib/debug \
						--enable-initfini-array \
						--with-system-zlib
# There seems to be some problems with builds of gold randomly failing whenever
# going through the build system, so let's try workaround this by trying to do
# make once again when it happens...
%make tooldir=%{_prefix}

%if "%{name}" == "binutils"
%make -C bfd/doc html
mkdir -p ../html
cp -f bfd/doc/bfd.html/* ../html
popd
%endif

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
%if "%{distepoch}" < "2015"
%ifnarch %{ix86}
				--enable-lto \
%endif
%endif
				--disable-werror \
				--with-bugurl=%{bugurl} \
				--enable-initfini-array \
				--with-system-zlib
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

%if !%{build_cross}
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
%endif

%install
mkdir -p %{buildroot}%{_prefix}
%makeinstall_std -C objs

rm -f %{buildroot}%{_mandir}/man1/{dlltool,nlmconv,windres}*
rm -f %{buildroot}%{_infodir}/dir
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
%if %isarch %{ix86} x86_64 ppc ppc64 s390 s390x sh3 sh4 sparc sparc64 %{arm}
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

# Symlinks for compatibility with crosscompilers
cd %buildroot%_bindir
for i in *; do
	ln -s $i %_target_platform-$i
done
cd -

%else
if [ -f "%{buildroot}%{_bindir}/%{target_platform}-ld.bfd" -a ! -e "%{buildroot}%{_bindir}/%{target_platform}-ld" ]; then
	ln -s %{target_platform}-ld.bfd "%{buildroot}%{_bindir}/%{target_platform}-ld"
fi
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
# Replace ar, ranlib and nm with LTO friendly wrappers
cd %{buildroot}%{_bindir}
mv ar binutils-ar
mv ranlib binutils-ranlib
mv nm binutils-nm
install -c -m 755 %{SOURCE100} ar
install -c -m 755 %{SOURCE101} ranlib
install -c -m 755 %{SOURCE102} nm
cd -
%endif

mkdir -p %{buildroot}%{_libdir}/bfd-plugins

if [ "%{cross}" != "%%{cross}" ]; then
	# aarch64-mandriva-linux-gnu and aarch64-linux-gnu are similar enough...
	longplatform=$(grep ^target_alias= objs/Makefile |cut -d= -f2-)
	shortplatform="%{cross}"
	#shortplatform=$(echo $longplatform |cut -d- -f1)-$(echo $longplatform |cut -d- -f3)-$(echo $longplatform |cut -d- -f4)
	if [ "$longplatform" != "$shortplatform" ]; then
		cd %{buildroot}%{_bindir}
		for i in $longplatform-*; do
			ln -s $i $(echo $i |sed -e "s,$longplatform,$shortplatform,")
		done
	fi
fi

%if !%{build_cross}
%if %{with default_lld}
# For now, let's keep %{_bindir}/ld in here even if it points
# to lld...
# Least surprise for now, but ultimately %{_bindir}/ld should
# move to lld
rm -f %{buildroot}%{_bindir}/ld
ln -s ld.lld %{buildroot}%{_bindir}/ld
%endif
%endif

%if "%{name}" == "binutils"
%files -f binutils.lang
%else
%files
%endif
%{_bindir}/*addr2line
%{_bindir}/*ar
%{_bindir}/*as
%{_bindir}/*c++filt
%optional %{_bindir}/*dwp
%{_bindir}/*elfedit
%{_bindir}/*gprof
%{_bindir}/*ld
%{_bindir}/*ld.bfd
%{_bindir}/*nm
%{_bindir}/*objcopy
%{_bindir}/*objdump
%{_bindir}/*ranlib
%{_bindir}/*readelf
%{_bindir}/*size
%{_bindir}/*strings
%{_bindir}/*strip
%ifarch %{spu_arches}
%{_bindir}/ppu-as
%endif
%{_libdir}/bfd-plugins
%{_mandir}/man1/*
%if "%{name}" == "binutils"
%{_infodir}/*info*
%{_libdir}/libbfd-*.so
%{_libdir}/libopcodes-*.so
%else
%dir %{_prefix}/%{target_platform}/
%dir %{_prefix}/%{target_platform}/bin/
%{_prefix}/%{target_platform}/bin/*
%dir %{_prefix}/%{target_platform}/lib
%dir %{_prefix}/%{target_platform}/lib/ldscripts
%{_prefix}/%{target_platform}/lib/ldscripts/*
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
