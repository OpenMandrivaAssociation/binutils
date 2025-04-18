# (tpg) TODO
# get rid of duplicated files because of triple
# /usr/triple/bin/ld is a copy of /usr/triple/bin/ld.bfd
# /usr/triple/bin/{as,ar,..} should be symlinked to /usr/bin/{as,ar,..} for native arch
# same goes for man and locale files as they are duplicated by triple 
#

%if %{cross_compiling}
# Workaround for libtool being a broken mess
%define prefer_gcc 1
# We don't currently build Canadian Crosses
%global targets %{arch}-linux
%else
# Listed targets are short form and will be expanded by rpm
# gnueabihf variants etc. are inserted by rpm into long_targets
%global targets aarch64-linux aarch64-mingw32 armv7hnl-linux i686-linux x86_64-linux x32-linux riscv32-linux riscv64-linux aarch64-linuxmusl armv7hnl-linuxmusl i686-linuxmusl x86_64-linuxmusl x32-linuxmusl riscv32-linuxmusl riscv64-linuxmusl aarch64-linuxuclibc armv7hnl-linuxuclibc i686-linuxuclibc x86_64-linuxuclibc x32-linuxuclibc riscv32-linuxuclibc riscv64-linuxuclibc aarch64-android armv7l-android armv8l-android x86_64-android i686-mingw32 x86_64-mingw32 ppc64le-linux ppc64le-linuxmusl ppc64le-linuxuclibc ppc64-linux ppc64-linuxmusl ppc64-linuxuclibc loongarch64-linux loongarch64-linuxmusl loongarch64-linuxuclibc
%endif
%global long_targets %(
	for i in %{targets}; do
		CPU=$(echo $i |cut -d- -f1)
		OS=$(echo $i |cut -d- -f2)
		echo -n "$(rpm --target=${CPU}-${OS} -E %%{_target_platform}) "
	done
)

# gprofng uses snprintf and friends as struct members...
%global _fortify_cflags %{nil}

%define lib_major 2
%define lib_name_orig %mklibname binutils
%define lib_name %{lib_name_orig}%{lib_major}
%define dev_name %mklibname binutils -d

%global optflags %{optflags} -Wl,--undefined-version

%ifarch %{riscv}
# Make sure we don't use lld on risc-v yet
%global optflags %{optflags} -fuse-ld=bfd -Wl,--undefined-version
%bcond_with default_lld
%else
%bcond_without default_lld
%endif

# Define if building a cross-binutils
%define build_cross 0
%{expand: %{?cross: %%global build_cross 1}}

# List of targets where gold can be enabled
%define gold_arches %(echo %{ix86} %{x86_64} ppc ppc64 riscv64 %{sparc} %{armx}|sed 's/[ ]/\|/g')

%define gold_default 0

%bcond_with gold
%ifarch %{riscv}
# FIXME Not yet ported -- enable when it is
%bcond_with gprofng
%else
%bcond_without gprofng
%endif

# Make sure we can apply patches from upstream even
# if they contain git binary diffs
#define __scm git

Summary:	GNU Binary Utility Development Utilities
Name:		binutils
Version:	2.44
# To package a snapshot, use
# "./src-release.sh -x binuitls" in binutils-gdb.git
Source0:	https://ftp.gnu.org/gnu/binutils/binutils-with-gold-%{version}%{?DATE:-%{DATE}}.tar.bz2
Release:	2
License:	GPLv3+
Group:		Development/Other
URL:		https://sourceware.org/binutils/
Source5:	https://src.fedoraproject.org/rpms/binutils/raw/master/f/binutils-2.19.50.0.1-output-format.sed
Source10:	binutils.rpmlintrc
# Wrapper scripts for ar, ranlib and nm that know how to deal with
# LTO bytecode, regardless of whether it's gcc or clang
Source100:	ar
Source101:	ranlib
Source102:	nm

%rename %{lib_name}
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	gettext
BuildRequires:	texinfo
BuildRequires:	dejagnu
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(libzstd)
# For git apply
BuildRequires:	git-core
# make check'ing requires libdl.a
BuildRequires:	glibc-static-devel >= 6:2.14.90-8
%if %{with gold}
# gold make check'ing requires libstdc++.a & bc
BuildRequires:	libstdc++-static-devel
BuildRequires:	bc
%endif
BuildRequires:	pkgconfig(isl)
BuildRequires:	pkgconfig(cloog-isl)
BuildRequires:	gmp-devel
BuildRequires:	pkgconfig(mpfr)
BuildRequires:	libmpc-devel
# For llvm-ar
BuildRequires:	llvm
%if %{with default_lld}
Requires:	lld
%endif
%if %{with gprofng}
BuildRequires:	jdk-current
%endif
# wrappers requires
Requires:	which

# Just to allow "lazy dependencies" on a %{_target_platform}
# toolchain (without having to check whether or not it's native).
# Obviously a native toolchain is also a "cross toolchain" to itself.
Provides:	cross-%{_target_platform}-binutils = %{EVRD}

%patchlist
# From upstream git:
0014-gas-fix-rs_fill_nop-listing.patch
0017-score-elf-gas-SEGV.patch
0025-PR-32731-ub-sanitizer-accessing-filenames_reversed.patch
0030-Updated-translations-for-bfd-and-gold.patch
0037-ld-Pass-Wl-z-lazy-to-compiler-for-i386-lazy-binding-.patch
0050-elf-Clear-the-SEC_ALLOC-bit-for-NOLOAD-note-sections.patch
0061-x86-Remove-AVX10.2-256-bit-rounding-support.patch
0076-s390-Add-support-for-z17-as-CPU-name.patch
# From Fedora:
https://src.fedoraproject.org/rpms/binutils/raw/rawhide/f/binutils-libtool-lib64.patch
# We don't want this one! Tends to break compatibility with scripts
# on other distros
#https://src.fedoraproject.org/rpms/binutils/raw/master/f/binutils-2.25-version.patch
# Export demangle.h with the binutils-devel rpm.
https://src.fedoraproject.org/rpms/binutils/raw/rawhide/f/binutils-export-demangle.h.patch
# Disable checks that config.h has been included before system headers.  BZ #845084
https://src.fedoraproject.org/rpms/binutils/raw/rawhide/f/binutils-no-config-h-check.patch
# FIXME this one serves a purpose (fix ltrace, LD_AUDIT) but reduces optimizations.
# This should be an option instead of a hardcode in the longer term!
#https://src.fedoraproject.org/rpms/binutils/raw/master/f/binutils-2.29-revert-PLT-elision.patch
https://src.fedoraproject.org/rpms/binutils/raw/rawhide/f/binutils-2.27-aarch64-ifunc.patch
https://src.fedoraproject.org/rpms/binutils/raw/rawhide/f/binutils-gold-mismatched-section-flags.patch

# From Yocto (note: SOME Yocto patches are important
# and good for OM as well - others are very much Yocto
# specific. Don't blindly add new Yocto
# patches here without double-checking)
0006-Only-generate-an-RPATH-entry-if-LD_RUN_PATH-is-not-e.patch
0011-fix-the-incorrect-assembling-for-ppc-wait-mnemonic.patch
#0013-Use-libtool-2.4.patch
#0014-Fix-rpath-in-libtool-when-sysroot-is-enabled.patch
#0015-sync-with-OE-libtool-changes.patch

# (Open)Mandriva patches
# For some reason, HAVE_READV isn't detected correctly on armv7hnl
# It's safe to just remove the condition because we don't support any
# prehistoric systems.
# https://file-store.openmandriva.org/api/v1/file_stores/e0633c259e3155d913aaa1a1227dda4c5a188992.log?show=true
binutils-2.34.0-arm32-build-workaround.patch
# (from gb, proyvind): defaults to i386 on x86_64 or ppc on ppc64 if 32 bit personality is set
# (tpg) this is needed for 32-bit chroots running on x86_64 host
binutils-2.25.51-linux32.patch
binutils-2.24.51.0.3.ld-default.settings.patch
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
binutils-2.24-2013-10-04.ld.gold-default-setttings.patch

#from Леонид Юрьев leo@yuriev.ru, posted to binutils list
binutils-2.25.51-fix-overrides-for-gold-testsuite.patch
#binutils-2.25.51-lto.patch
binutils-2.27.90-fix-warnings.patch
binutils-2.31-clang7.patch
binutils-2.44-workaround-linkage-failure.patch

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

%package -n %{dev_name}
Summary:	Main library for %{name}
Group:		Development/Other
Provides:	%{name}-devel = %{version}-%{release}
Provides:	%{lib_name}-devel = %{version}-%{release}
Obsoletes:	%{lib_name}-devel <= %{version}-%{release}
Requires:	pkgconfig(zlib)

%description -n %{dev_name}
This package contains BFD and opcodes static libraries and associated
header files.  Only *.a libraries are included, because BFD doesn't
have a stable ABI.  Developers starting new projects are strongly encouraged
to consider using libelf instead of BFD.

%prep
%autosetup -p1 -n binutils-with-gold-%{version}%{?DATE:-%{DATE}}

%if %{with gprofng}
. %{_sysconfdir}/profile.d/90java.sh
%endif

cp -f %{_datadir}/libtool/config/config.{guess,sub} .

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

#ifarch %{arm}
# This should be fixed with patches 138 and 139, but leaving it here for now
# so we can restore the temporary fix if more problems occur.
# --icf=safe is unstable on 32-bit ARM
# https://sourceware.org/bugzilla/show_bug.cgi?id=23046
# sed -i -e '/^[^/-]*icf/ s/"safe"/"none"/' gold/options.h
#endif

find -name \*.h -o -name \*.c -o -name \*.cc | xargs chmod 644

%if "%{_lib}" != "lib"
# Fix bogus lib hardcodes...
sed -i -e 's,/lib/,/%{_lib}/,g' bfd/plugin.c
sed -i -e 's,tooldir)/lib,tooldir)/%{_lib},g' gold/Makefile.*
%endif

export CC="%{__cc} -D_GNU_SOURCE=1 -DHAVE_DECL_ASPRINTF=1"
export CXX="%{__cxx} -D_GNU_SOURCE=1 -std=gnu++14"

for i in %{long_targets}; do
	mkdir -p BUILD-$i
	cd BUILD-$i
	if [ "%{_target_platform}" = "$i" ]; then
# Native build -- we want shared libs here...
		EXTRA_CONFIG="--enable-shared --with-pic"
		if echo $i |grep -q x32; then
			EXTRA_CONFIG="$EXTRA_CONFIG --with-lib-path=/libx32:%{_prefix}/libx32:%{_prefix}/local/libx32:%{_prefix}/$i/libx32:/lib64:%{_prefix}/lib64:%{_prefix}/local/lib64:%{_prefix}/$i/lib64:/lib:%{_prefix}/lib:%{_prefix}/local/lib:%{_prefix}/$i/lib"
		else
%if "%{_lib}" == "lib64"
			EXTRA_CONFIG="$EXTRA_CONFIG --with-lib-path=/%{_lib}:%{_libdir}:%{_prefix}/local/%{_lib}:/lib:%{_prefix}/lib:%{_prefix}/local/lib:%{_prefix}/$i/lib"
%else
			EXTRA_CONFIG="$EXTRA_CONFIG --with-lib-path=/lib:%{_prefix}/lib:%{_prefix}/local/lib:%{_prefix}/$i/lib"
%endif
		fi
		EXTRA_CONFIG="$EXTRA_CONFIG --enable-targets=all"
	else
# Cross build -- need to set program_prefix and friends...
		EXTRA_CONFIG="--target=$i --program-prefix=$i- --disable-shared --enable-static --with-sysroot=%{_prefix}/${i} --with-native-system-header-dir=/include"
		if echo $i |grep -q x32; then
			EXTRA_CONFIG="$EXTRA_CONFIG --with-lib-path=%{_prefix}/$i/libx32:%{_prefix}/$i/lib64:%{_prefix}/$i/lib"
		elif echo $i |grep -q 64; then
			EXTRA_CONFIG="$EXTRA_CONFIG --with-lib-path=%{_prefix}/$i/lib64:%{_prefix}/$i/lib"
		else
			EXTRA_CONFIG="$EXTRA_CONFIG --with-lib-path=%{_prefix}/$i/lib"
		fi
		case $i in
		*x32)
			EXTRA_CONFIG="$EXTRA_CONFIG --enable-targets=$i,x86_64-$(echo $i |cut -d- -f2- |sed -e 's,x32,,'),i686-$(echo $i |cut -d- -f2- |sed -e 's,x32,,')"
			;;
		i*86*|athlon*|znver1_32*)
			EXTRA_CONFIG="$EXTRA_CONFIG --enable-targets=$i,x86_64-$(echo $i |cut -d- -f2-)"
			;;
		aarch64*mingw*)
			# There's no such thing as armv7hnl-mingw
			;;
		aarch64*)
			EXTRA_CONFIG="$EXTRA_CONFIG --enable-targets=$i,armv7hnl-$(echo $i |cut -d- -f2-)eabihf"
			;;
		esac
	fi

	case $i in
	*x32)
		EXTRA_CONFIG="$EXTRA_CONFIG --with-abi=x32"
		;;
	i*86*|athlon*|znver1_32*)
		EXTRA_CONFIG="$EXTRA_CONFIG --with-abi=32"
		;;
	armv7*)
		EXTRA_CONFIG="$EXTRA_CONFIG --with-cpu=cortex-a8 --with-tune=cortex-a8 --with-arch=armv7-a --with-mode=thumb --with-float=hard --with-fpu=neon --with-abi=aapcs-linux"
		;;
	x86_64*|znver1*)
		EXTRA_CONFIG="$EXTRA_CONFIG --with-abi=64"
		;;
	esac

	CONFIGURE_TOP=.. %configure \
		--without-static-standard-libraries \
		--enable-64-bit-bfd \
		--with-bugurl=%{bugurl} \
%if ! %{with gprofng}
		--disable-gprofng \
%endif
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
		$EXTRA_CONFIG \
		--enable-plugins \
		--enable-threads \
%ifarch %{mips}
		--enable-default-hash-style=sysv \
%else
		--enable-default-hash-style=gnu \
%endif
		--enable-lto \
		--disable-werror \
		--enable-static \
		--enable-relro=yes \
		--with-separate-debug-dir=%{_prefix}/lib/debug \
		--enable-initfini-array \
		--disable-isl-version-check \
		--enable-generate-build-notes=no \
		--enable-compressed-debug-sections=none \
		--enable-separate-code=yes \
		--with-mpc=%{_libdir} \
		--with-mpfr=%{_libdir} \
		--with-gmp=%{_libdir} \
		--with-isl=%{_libdir} \
		--with-system-zlib \
		--enable-default-compressed-debug-sections-algorithm=zstd \
		--with-zstd
	cd -
done

%build
for i in %{long_targets}; do
	cd BUILD-$i
	%make_build
	cd -
done

%if ! %{cross_compiling}
%check
# All Tests must pass
echo ====================TESTING=========================
# workaround for not using colorgcc when building due to colorgcc
# messing up output redirection..
PATH=${PATH#%{_datadir}/colorgcc:}
%make_build -k -C BUILD-%{_target_platform} check CFLAGS="" CXXFLAGS="" LDFLAGS="" || :
echo ====================TESTING END=====================

logfile="%{name}-%{version}-%{release}.log"
rm -f $logfile; find . -name "*.sum" | xargs cat >> $logfile
%endif

%install
for i in %{long_targets}; do
	[ "$i" = "%{_target_platform}" ] && continue
	cd BUILD-$i
	%make_install
	cd -
	mkdir -p %{buildroot}%{_prefix}/"$i"/include
	ln -s . %{buildroot}%{_prefix}/"$i"/usr
	ln -s . %{buildroot}%{_prefix}/"$i"/"$i"
done
# We install the native version last to make sure we get all
# the man pages etc. for the native version rather than a random
# cross compiler that happens to go last
cd BUILD-%{_target_platform}
%make_install
cp libiberty/pic/libiberty.a %{buildroot}%{_libdir}/
cd -

rm -f %{buildroot}%{_mandir}/man1/*{dlltool,nlmconv,windres}*
rm -f %{buildroot}%{_infodir}/dir

# [ -d BUILD-%{_target_platform} ] && %make -C BUILD-%{_target_platform} prefix=%{buildroot}%{_prefix} infodir=%{buildroot}%{_infodir} install-info

# Sanity check --enable-64-bit-bfd really works.
grep '^#define BFD_ARCH_SIZE 64$' %{buildroot}%{_prefix}/include/bfd.h
# Fix multilib conflicts of generated values by __WORDSIZE-based expressions.
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
touch -r bfd/bfd-in2.h %{buildroot}%{_prefix}/include/bfd.h

# Generate .so linker scripts for dependencies; imported from glibc/Makerules:
rm -f %{buildroot}%{_libdir}/libbfd.so %{buildroot}%{_libdir}/libopcodes.so
# This fragment of linker script gives the OUTPUT_FORMAT statement
# for the configuration we are building.
OUTPUT_FORMAT="\
/* Ensure this .so library will not be used by a link for a different format
   on a multi-architecture system.  */
$(%{_cc} $CFLAGS $LDFLAGS -shared -x c /dev/null -o /dev/null -Wl,--verbose -v 2>&1 | sed -n -f "%{SOURCE5}")"

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

cd %{buildroot}%{_bindir}
# Symlinks for native tools compatibility with crosscompilers
for i in *; do
	echo $i |grep -q -- - && continue
	[ -e %{_target_platform}-$i ] || ln -s $i %{_target_platform}-$i
done

# Default ld, if one is missing...
for i in *-ld.bfd; do
	[ -e ${i/.bfd/} ] || ln -s $i ${i/.bfd}
done
cd -

rm -f  %{buildroot}%{_prefix}/*/*/lib/*.la

%find_lang binutils --all-name

# Replace ar, ranlib and nm with LTO friendly wrappers
cd %{buildroot}%{_bindir}
mv ar binutils-ar
mv ranlib binutils-ranlib
mv nm binutils-nm
install -c -m 755 %{SOURCE100} ar
install -c -m 755 %{SOURCE101} ranlib
install -c -m 755 %{SOURCE102} nm
cd -

mkdir -p %{buildroot}%{_libdir}/bfd-plugins

for i in %{long_targets}; do
	# aarch64-mandriva-linux-gnu and aarch64-linux-gnu are similar enough...
	longplatform=$(grep ^target_alias= BUILD-$i/Makefile |cut -d= -f2-)
	if [ -n "$(echo $i |cut -d- -f4-)" ]; then
		shortplatform="$(echo $i |cut -d- -f1)-$(echo $i |cut -d- -f3-)"
		cd %{buildroot}%{_bindir}
		for j in $longplatform-*; do
			[ -e $(echo $j |sed -e "s,$longplatform,$shortplatform,") ] || ln -s $j $(echo $j |sed -e "s,$longplatform,$shortplatform,")
		done
		cd -
		fi
		if [ "$longplatform" != "$i" ]; then
		cd %{buildroot}%{_bindir}
		for j in $longplatform-*; do
			[ -e $(echo $j |sed -e "s,$longplatform,$i,") ] || ln -s $j $(echo $j |sed -e "s,$longplatform,$i,")
		done
		cd -
	fi
done

cd %{buildroot}%{_bindir}
# Set compat symlinks for scripts expecting *-mandriva-linux-gnu toolchains
for i in *-openmandriva-*; do
	[ -e "$i" ] || continue
	ln -s $i ${i/-openmandriva-/-mandriva-}
done
# And for armv7hl (as opposed to armv7hnl) -- it's the same binutils-wise
for i in armv7hnl-*; do
	[ -e "$i" ] || continue
	ln -s $i ${i/armv7hnl-/armv7hl-}
done
cd -

%if %{with default_lld}
# For now, let's keep %{_bindir}/ld in here even if it points
# to lld...
# Least surprise for now, but ultimately %{_bindir}/ld should
# move to lld
rm -f %{buildroot}%{_bindir}/ld
ln -s ld.lld %{buildroot}%{_bindir}/ld
%endif

# We get those from gdb-doc (the files are identical too, coming out of
# the binutils-gdb shared repository)
rm %{buildroot}%{_infodir}/ctf-spec.info* %{buildroot}%{_infodir}/sframe-spec.info*

%files -f binutils.lang
%{_bindir}/addr2line
%{_bindir}/ar
%{_bindir}/binutils-ar
%{_bindir}/as
%{_bindir}/c++filt
%optional %{_bindir}/dwp
%{_bindir}/elfedit
%{_bindir}/gprof
%if %{with gprofng}
%ifarch %{x86_64} %{aarch64}
%config(noreplace) %{_sysconfdir}/gprofng.rc
%{_bindir}/gprofng
%{_bindir}/%{_target_platform}-gprofng
%{_bindir}/gp-archive
%{_bindir}/gp-collect-app
%{_bindir}/gp-display-html
%{_bindir}/gp-display-src
%{_bindir}/gp-display-text
%{_bindir}/gprofng-archive
%{_bindir}/gprofng-collect-app
%{_bindir}/gprofng-display-html
%{_bindir}/gprofng-display-src
%{_bindir}/gprofng-display-text
%{_libdir}/gprofng
%doc %{_docdir}/gprofng
%endif
%endif
%{_bindir}/ld
%{_bindir}/ld.bfd
%if %{with gold}
%{_bindir}/ld.gold
%{_bindir}/%{_target_platform}-ld.gold
%endif
%{_bindir}/nm
%{_bindir}/binutils-nm
%{_bindir}/objcopy
%{_bindir}/objdump
%{_bindir}/ranlib
%{_bindir}/binutils-ranlib
%{_bindir}/readelf
%{_bindir}/size
%{_bindir}/strings
%{_bindir}/strip
%{_bindir}/%{_target_platform}-addr2line
%{_bindir}/%{_target_platform}-ar
%{_bindir}/%{_target_platform}-as
%{_bindir}/%{_target_platform}-c++filt
%optional %{_bindir}/%{_target_platform}-dwp
%{_bindir}/%{_target_platform}-elfedit
%{_bindir}/%{_target_platform}-gprof
%{_bindir}/%{_target_platform}-ld
%{_bindir}/%{_target_platform}-ld.bfd
%{_bindir}/%{_target_platform}-nm
%{_bindir}/%{_target_platform}-objcopy
%{_bindir}/%{_target_platform}-objdump
%{_bindir}/%{_target_platform}-ranlib
%{_bindir}/%{_target_platform}-readelf
%{_bindir}/%{_target_platform}-size
%{_bindir}/%{_target_platform}-strings
%{_bindir}/%{_target_platform}-strip
%(if echo %{_target_platform} |grep -q -- -openmandriva-; then echo "%{_bindir}/%(echo %{_target_platform} |sed -e 's,-openmandriva-,-mandriva-,')-*"; fi)
%(if echo %{_target_platform} |grep -q -- armv7hnl-; then echo "%{_bindir}/%(echo %{_target_platform} |sed -e 's,armv7hnl-,armv7hl-,')-*"; fi)
%(if echo %{_target_platform} |grep -q -- armv7hnl- && echo %{_target_platform} |grep -q -- -openmandriva-; then echo "%{_bindir}/%(echo %{_target_platform} |sed -e 's,armv7hnl-,armv7hl-,;s,-openmandriva-,-mandriva-,g')-*"; fi)
%{_libdir}/bfd-plugins
%doc %{_mandir}/man1/*
%doc %{_infodir}/*info*
%{_libdir}/libbfd-*.so
%{_libdir}/libctf.so.*
%{_libdir}/libctf-nobfd.so.*
%{_libdir}/libopcodes-*.so
%{_libdir}/libsframe.so.*
%if %{with gprofng}
%{_libdir}/libgprofng.so.*
%endif
%{_prefix}/%{_target_platform}
%(
if [ -n "$(echo %{_target_platform} |cut -d- -f4-)" ]; then
	echo "%{_bindir}/$(echo %{_target_platform} |cut -d- -f1)-$(echo %{_target_platform} |cut -d- -f3-)-*"
	if echo %{_target_platform} |grep -q armv7hnl-; then
		echo "%{_bindir}/$(echo %{_target_platform} |sed -e 's,armv7hnl-,armv7hl-,g' |cut -d- -f1)-$(echo %{_target_platform} |cut -d- -f3-)-*"
	fi
fi
)
# All of the following are optional because they're
# built only if we support a COFF/PE target
%{_bindir}/coffdump
%{_bindir}/dlltool
%{_bindir}/dllwrap
%{_bindir}/srconv
%{_bindir}/sysdump
%{_bindir}/windmc
%{_bindir}/windres
%{_bindir}/%{_target_platform}-coffdump
%{_bindir}/%{_target_platform}-dlltool
%{_bindir}/%{_target_platform}-dllwrap
%{_bindir}/%{_target_platform}-srconv
%{_bindir}/%{_target_platform}-sysdump
%{_bindir}/%{_target_platform}-windmc
%{_bindir}/%{_target_platform}-windres

%files -n %{dev_name}
%{_includedir}/*.h
%{_libdir}/libbfd.a
%{_libdir}/libbfd.so
%{_libdir}/libctf.a
%{_libdir}/libctf.so
%{_libdir}/libctf-nobfd.a
%{_libdir}/libctf-nobfd.so
%{_libdir}/libopcodes.a
%{_libdir}/libopcodes.so
%{_libdir}/libiberty.a
%{_libdir}/libsframe.a
%{_libdir}/libsframe.so
%if %{with gprofng}
%{_libdir}/libgprofng.so
%{_libdir}/libgprofng.a
%endif

%(
for i in %{long_targets}; do
	[ "$i" = "%{_target_platform}" ] && continue
	cat <<EOF
%package -n cross-${i}-binutils
Summary:	Binutils for crosscompiling to ${i}
Group:	Development/Other
EOF

	if echo $i |grep -q -- -openmandriva-; then
		echo "Obsoletes: cross-${i/-openmandriva-/-mandriva-}-binutils < %{EVRD}"
		echo "Provides: cross-${i/-openmandriva-/-mandriva-}-binutils = %{EVRD}"
	fi

	cat <<EOF
%description -n cross-${i}-binutils
Binutils for crosscompiling to ${i}.

%files -n cross-${i}-binutils
%{_prefix}/${i}
%{_bindir}/${i}-*
EOF

	if [ -n "$(echo $i |cut -d- -f4-)" ]; then
	shortplatform="$(echo $i |cut -d- -f1)-$(echo $i |cut -d- -f3-)"
	echo "%{_bindir}/${shortplatform}-*"
		if echo $shortplatform |grep -q armv7hnl-; then
		echo "%{_bindir}/${shortplatform/armv7hnl-/armv7hl-}-*"
		fi
	fi
	if echo $i |grep -q -- -openmandriva-; then
		f=${i/-openmandriva-/-mandriva-}
		echo "%{_bindir}/${f}-*"
		if echo $i |grep -q armv7hnl-; then
			echo "%{_bindir}/${f/armv7hnl-/armv7hl-}-*"
		fi
	fi
	if echo $i |grep -q armv7hnl-; then
		echo "%{_bindir}/${i/armv7hnl-/armv7hl-}-*"
	fi
	echo
done
)
