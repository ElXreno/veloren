## WIP, expect some crap in packaging
## Note: requires internet access during build procces because of Rust nightly and git-lfs

## Optimize for build time or performance
%bcond_without release_build

%global debug_package %{nil}

%global commit        b7a084cbb8db211400d0260261cafef57002755c
%global shortcommit   %(c=%{commit}; echo ${c:0:7})
%global date          20191128

Name:           veloren
Version:        0.4.0
Release:        7.%{date}git%{shortcommit}%{?dist}
Summary:        Multiplayer voxel RPG written in Rust

License:        GPLv3+
URL:            https://gitlab.com/veloren/veloren
Source0:        %{url}/-/archive/%{commit}/%{name}-%{version}.%{date}git%{shortcommit}.tar.gz
Source1:        %{name}-voxygen.desktop
Source2:        %{name}-voxygen-16.png
Source3:        %{name}-voxygen-32.png
Source4:        %{name}-voxygen-48.png
Source5:        %{name}-voxygen-64.png
Source6:        %{name}-voxygen-128.png
Source7:        %{name}-voxygen-256.png

# BuildRequires:  cargo >= 1.40
BuildRequires:  desktop-file-utils
BuildRequires:  gcc
BuildRequires:  git
BuildRequires:  git-lfs
BuildRequires:  pkgconfig(alsa)
BuildRequires:  pkgconfig(atk)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(gdk-3.0)
BuildRequires:  pkgconfig(gdk-pixbuf-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(pango)
%if 0%{?rhel} >= 7
BuildRequires:  python3-devel
%endif

Requires:       hicolor-icon-theme

%if 0%{?fedora} || 0%{?rhel} >= 8
Recommends:     %{name}-server-cli%{?_isa}
Recommends:     %{name}-chat-cli%{?_isa}
%endif

%description
Veloren is a multiplayer voxel RPG written in Rust. It is inspired by games
such as Cube World, Legend of Zelda: Breath of the Wild, Dwarf Fortress
and Minecraft.


%package        server-cli
Summary:        Standalone server for %{name}

%if 0%{?fedora} || 0%{?rhel} >= 8
Recommends:     %{name}%{?_isa} = %{version}-%{release}
%endif

%description    server-cli
Standalone server for %{name}.


%package        chat-cli
Summary:        Console chat for %{name}

%if 0%{?fedora} || 0%{?rhel} >= 8
Recommends:     %{name}%{?_isa} = %{version}-%{release}
%endif

%description    chat-cli
Console chat for %{name}.


%prep
%autosetup -p1 -n %{name}-%{commit}

%if %{with release_build}
echo "Building release package..."
%else
echo "Building debug package..."
%endif

## Use recommended upstream veloren version of Rust toolchain
rust_toolchain=$(cat rust-toolchain)
curl https://sh.rustup.rs -sSf | sh -s -- --default-toolchain ${rust_toolchain} --profile minimal -y

git init
git remote add origin https://gitlab.com/%{name}/%{name}.git
git fetch origin %{commit}
git reset --hard %{commit}

%if %{without release_build}
## Unoptimize dev/debug builds
sed -i 's/opt-level = 2/opt-level = 0/' Cargo.toml
%endif


%build
BUILD_FLAGS=

%if %{with release_build}
BUILD_FLAGS=--release
%endif

$HOME/.cargo/bin/cargo build ${BUILD_FLAGS}


%install
TARGET_PATH=target/debug

%if %{with release_build}
TARGET_PATH=target/release
%endif

## Game
install -m 0755 -Dp ${TARGET_PATH}/%{name}-voxygen      %{buildroot}%{_bindir}/%{name}-voxygen
mkdir -p                                                %{buildroot}%{_datadir}/%{name}
cp -a assets                                            %{buildroot}%{_datadir}/%{name}

## Standalone server
install -m 0755 -Dp ${TARGET_PATH}/%{name}-server-cli   %{buildroot}%{_bindir}/%{name}-server-cli

## Console chat
install -m 0755 -Dp ${TARGET_PATH}/%{name}-chat-cli     %{buildroot}%{_bindir}/%{name}-chat-cli

## Install desktop file
desktop-file-install \
    --dir %{buildroot}%{_datadir}/applications \
    %{SOURCE1}

## Install icons
for size in 16 32 48 64 128 256; do
    dir=%{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps
    install -d $dir
    install -m 0644 -p %{_sourcedir}/%{name}-voxygen-${size}.png $dir/%{name}-voxygen.png
done


%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}-voxygen
%{_datadir}/%{name}
%{_datadir}/applications/%{name}-voxygen.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}-voxygen.png

%files server-cli
%license LICENSE
%doc README.md
%{_bindir}/%{name}-server-cli

%files chat-cli
%license LICENSE
%doc README.md
%{_bindir}/%{name}-chat-cli


%changelog
* Thu Nov 28 2019 ElXreno <elxreno@gmail.com> - 0.4.0-7.20191128gitb7a084c
- Updated to commit b7a084cbb8db211400d0260261cafef57002755c

* Sat Nov 23 2019 ElXreno <elxreno@gmail.com> - 0.4.0-6.20191123git9de1075
- Updated to commit 9de10759d16229f877bedf92dbcb9f50d5ec8a14

* Wed Nov 20 2019 ElXreno <elxreno@gmail.com> - 0.4.0-5.20191120gitf380af9
- Updated to commit eb7b55d3ad78856593bbae365857ec5b3b79540e

* Sat Nov 16 2019 ElXreno <elxreno@gmail.com> - 0.4.0-4.20191109giteb7b55d
- Added more icons resolution and fixed it's installation

* Wed Nov 13 2019 ElXreno <elxreno@gmail.com> - 0.4.0-3.20191109giteb7b55d
- Updated to eb7b55d3ad78856593bbae365857ec5b3b79540e commit
- Added desktop file and icon
- Minor fixes (thanks @atim)

* Mon Nov 11 2019 ElXreno <elxreno@gmail.com> - 0.4.0-2.20191107git5fe1eec
- Fixed building and added chat-cli package

* Sat Sep 07 2019 Artem Polishchuk <ego.cordatus@gmail.com> - 0.3.0-2.20190907git92c0edc
- Update to latest git snapshot

* Fri Mar 29 2019 Artem Polishchuk <ego.cordatus@gmail.com> - 0.3.0-1.20190906gitd41d020
- Initial package
