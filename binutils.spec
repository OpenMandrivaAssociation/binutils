# Listed targets are short form and will be expanded by rpm
# gnueabihf variants etc. are inserted by rpm into long_targets
%if %mdvver <= 3000000
%global targets aarch64-linux armv7hl-linux i586-linux i686-linux x86_64-linux
%else
# (tpg) set cross targets here for cooker
%global targets aarch64-linux armv7hnl-linux i686-linux x86_64-linux x32-linux riscv32-linux riscv64-linux aarch64-linuxmusl armv7hnl-linuxmusl i686-linuxmusl x86_64-linuxmusl x32-linuxmusl riscv32-linuxmusl riscv64-linuxmusl aarch64-android armv7l-android armv8l-android i686-mingw32 x86_64-mingw32
# (tpg) temporary disable build debuginfo for ix86
%ifarch %{ix86}
#error: create archive failed on file /builddir/build/BUILDROOT/mesa-17.3.6-1-omv2015.0.i586-buildroot/usr/lib/debug/usr/lib/gallium-pipe/pipe_radeonsi.so.debug: cpio: Bad magic
%define _enable_debug_packages %{nil}
%define debug_package          %{nil}
%endif
%endif
%global long_targets %(
    for i in %{targets}; do
	CPU=$(echo $i |cut -d- -f1)
	OS=$(echo $i |cut -d- -f2)
	echo -n "$(rpm --target=${CPU}-${OS} -E %%{_target_platform}) "
    done
)


%define _disable_lto 1

%define lib_major 2
%define lib_name_orig %mklibname binutils
%define lib_name %{lib_name_orig}%{lib_major}
%define dev_name %mklibname binutils -d

# (tpg) optimize it a bit
%global optflags %{optflags} -fstack-protector-strong

%ifarch %{arm}
# FIXME remove when binutils links successfully with gold on arm32
%global optflags %{optflags} -fuse-ld=bfd
%endif

# Define if building a cross-binutils
%define build_cross 0
%{expand: %{?cross: %%global build_cross 1}}

# List of targets where gold can be enabled
%define gold_arches %(echo %{ix86} %{x86_64} ppc ppc64 riscv64 %{sparc} %{armx}|sed 's/[ ]/\|/g')

%define gold_default 1

%bcond_with default_lld

%bcond_without gold

Summary:	GNU Binary Utility Development Utilities
Name:		binutils
Version:	2.32
Source0:	ftp://ftp.gnu.org/gnu/binutils/binutils-%{version}%{?DATE:-%{DATE}}.tar.xz
Release:	2
License:	GPLv3+
Group:		Development/Other
URL:		http://sources.redhat.com/binutils/
#Source1:	http://ftp.kernel.org/pub/linux/devel/binutils/binutils-%{version}.tar.xz.sign
Source5:	https://src.fedoraproject.org/rpms/binutils/raw/master/f/binutils-2.19.50.0.1-output-format.sed
Source10:	binutils.rpmlintrc
# Wrapper scripts for ar, ranlib and nm that know how to deal with
# LTO bytecode, regardless of whether it's gcc or clang
Source100:	ar
Source101:	ranlib
Source102:	nm
%rename		%{lib_name}
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	gcc
BuildRequires:	gettext
BuildRequires:	texinfo
BuildRequires:	dejagnu
BuildRequires:	pkgconfig(zlib)
# make check'ing requires libdl.a
BuildRequires:	glibc-static-devel >= 6:2.14.90-8
# gold make check'ing requires libstdc++.a & bc
BuildRequires:	libstdc++-static-devel
BuildRequires:	bc
BuildRequires:	pkgconfig(isl)
BuildRequires:	pkgconfig(cloog-isl)
BuildRequires:	gmp-devel
BuildRequires:	pkgconfig(mpfr)
BuildRequires:	libmpc-devel

# Fedora patches:
Patch01:	https://src.fedoraproject.org/rpms/binutils/raw/master/f/binutils-2.20.51.0.2-libtool-lib64.patch
# We don't want this one! Tends to break compatibility with scripts
# on other distros
#Patch02:	https://src.fedoraproject.org/rpms/binutils/raw/master/f/binutils-2.25-version.patch
# Export demangle.h with the binutils-devel rpm.
Patch03:	https://src.fedoraproject.org/rpms/binutils/raw/master/f/binutils-2.31-export-demangle.h.patch
# Disable checks that config.h has been included before system headers.  BZ #845084
Patch04:	https://src.fedoraproject.org/rpms/binutils/raw/master/f/binutils-2.22.52.0.4-no-config-h-check.patch
Patch05:	https://src.fedoraproject.org/rpms/binutils/raw/master/f/binutils-2.26-lto.patch
Patch06:	https://src.fedoraproject.org/rpms/binutils/raw/master/f/binutils-2.29-filename-in-error-messages.patch
# FIXME this one serves a purpose (fix ltrace, LD_AUDIT) but reduces optimizations.
# This should be an option instead of a hardcode in the longer term!
#Patch07:	https://src.fedoraproject.org/rpms/binutils/raw/master/f/binutils-2.29-revert-PLT-elision.patch
Patch08:	https://src.fedoraproject.org/rpms/binutils/raw/master/f/binutils-readelf-other-sym-info.patch
Patch09:	https://src.fedoraproject.org/rpms/binutils/raw/master/f/binutils-2.27-aarch64-ifunc.patch
Patch16:	https://src.fedoraproject.org/rpms/binutils/raw/master/f/binutils-fix-testsuite-failures.patch
Patch18:	https://src.fedoraproject.org/rpms/binutils/raw/master/f/binutils-gold-ignore-discarded-note-relocs.patch

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
# musl's libintl is good enough, we don't need the internal copy
Patch132:	binutils-2015.01-accept-musl-libintl.patch

#from Леонид Юрьев leo@yuriev.ru, posted to binutils list
Patch131:	binutils-2.25.51-fix-overrides-for-gold-testsuite.patch
# from upstream
Patch134:	binutils-2.21.53.0.3-opcodes-missing-ifdef-enable-nls.patch
Patch135:	binutils-2.25.51-lto.patch

Patch136:	binutils-2.27.90-fix-warnings.patch
Patch138:	binutils-2.31-clang7.patch

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
%setup -q -n binutils-%{version}%{?DATE:-%{DATE}}
%autopatch -p1
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

%ifarch %{arm}
# This should be fixed with patches 138 and 139, but leaving it here for now
# so we can restore the temporary fix if more problems occur.
# --icf=safe is unstable on 32-bit ARM
# https://sourceware.org/bugzilla/show_bug.cgi?id=23046
#ed -i -e '/^[^/-]*icf/ s/"safe"/"none"/' gold/options.h
%endif

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
    else
# Cross build -- need to set program_prefix and friends...
	EXTRA_CONFIG="--target=$i --program-prefix=$i- --disable-shared --enable-static --with-sysroot=%{_prefix}/${i} --with-native-system-header-dir=/include"
    fi

    case $i in
	i*86|athlon|znver1_32)
	    EXTRA_CONFIG="$EXTRA_CONFIG --enable-targets=x86_64-$(echo $i |cut -d- -f2-)"
	    ;;
	aarch64)
	    EXTRA_CONFIG="$EXTRA_CONFIG --enable-targets=armv7hnl-$(echo $i |cut -d- -f2-)eabihf"
	    ;;
	armv7*)
	    EXTRA_CONFIG="$EXTRA_CONFIG --with-cpu=cortex-a8 --with-tune=cortex-a8 --with-arch=armv7-a --with-mode=thumb --with-float=hard --with-fpu=neon --with-abi=aapcs-linux"
	    ;;
	x86_64|znver1)
	    EXTRA_CONFIG="$EXTRA_CONFIG --enable-targets=i586-$(echo $i |cut -d- -f2-),i686-$(echo $i |cut -d- -f2-)"
	    ;;
    esac

    CONFIGURE_TOP=.. %configure \
		--enable-64-bit-bfd \
		--with-bugurl=%{bugurl} \
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
%if "%{_lib}" == "lib64"
		--with-lib-path=/%{_lib}:%{_libdir}:%{_prefix}/local/%{_lib}:/lib:%{_prefix}/lib:%{_prefix}/local/lib:%{_prefix}/$i/lib \
%else
		--with-lib-path=/lib:%{_prefix}/lib:%{_prefix}/local/lib:%{_prefix}/$i/lib \
%endif
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
		--with-mpc=%{_libdir} \
		--with-mpfr=%{_libdir} \
		--with-gmp=%{_libdir} \
		--with-isl=%{_libdir} \
		--with-system-zlib
    cd -
done

%build
for i in %{long_targets}; do
    cd BUILD-$i
    %make_build
    cd -
done

%make_build -C BUILD-%{_target_platform}/bfd/doc html
mkdir -p html
cp -f BUILD-%{_target_platform}/bfd/doc/bfd.html/* html

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

%install
for i in %{long_targets}; do
    [ "$i" = "%{_target_platform}" ] && continue
    cd BUILD-$i
    %make_install
    cd -
    mkdir -p %{buildroot}%{_prefix}/"$i"/include
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
    ln -s $i ${i/-openmandriva-/-mandriva-}
done
# And for armv7hl (as opposed to armv7hnl) -- it's the same binutils-wise
for i in armv7hnl-*; do
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

%files -f binutils.lang
%{_bindir}/addr2line
%{_bindir}/ar
%{_bindir}/binutils-ar
%{_bindir}/as
%{_bindir}/c++filt
%optional %{_bindir}/dwp
%{_bindir}/elfedit
%{_bindir}/gprof
%{_bindir}/ld
%{_bindir}/ld.bfd
%optional %{_bindir}/ld.gold
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
%optional %{_bindir}/%{_target_platform}-ld.gold
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
%{_mandir}/man1/*
%{_infodir}/*info*
%{_libdir}/libbfd-*.so
%{_libdir}/libopcodes-*.so
%{_prefix}/%{_target_platform}
%(
if [ -n "$(echo %{_target_platform} |cut -d- -f4-)" ]; then
    echo "%{_bindir}/$(echo %{_target_platform} |cut -d- -f1)-$(echo %{_target_platform} |cut -d- -f3-)-*"
    if echo %{_target_platform} |grep -q armv7hnl-; then
        echo "%{_bindir}/$(echo %{_target_platform} |sed -e 's,armv7hnl-,armv7hl-,g' |cut -d- -f1)-$(echo %{_target_platform} |cut -d- -f3-)-*"
    fi
fi
)

%files -n %{dev_name}
%doc html
%{_includedir}/*.h
%{_libdir}/libbfd.a
%{_libdir}/libbfd.so
%{_libdir}/libopcodes.a
%{_libdir}/libopcodes.so
%{_libdir}/libiberty.a

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
