# Note: requires internet access during build procces because of Rust nightly and git-lfs

# Optimize for build time or performance
%bcond_without release_build

%global debug_package %{nil}

%global commit      4e7c9554907cc5a9a88b6a20d3fd128d7bac9918
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global date        20200109

%global uuid    net.%{name}.%{name}

Name:           veloren
Version:        0.4.0
Release:        1.%{date}git%{shortcommit}%{?dist}
Summary:        Multiplayer voxel RPG written in Rust

License:        GPLv3+
URL:            https://veloren.net/
Source0:        https://gitlab.com/veloren/veloren/-/archive/%{commit}/%{name}-%{version}.%{date}git%{shortcommit}.tar.gz

# Install desktop file, icon and appdata manifest
# * https://gitlab.com/veloren/veloren/merge_requests/654
Source10:       %{uuid}.appdata.xml
Source11:       %{uuid}.desktop
Source12:       %{uuid}.png

#BuildRequires:  cargo >= 1.42
#BuildRequires:  rust >= 1.42
BuildRequires:  gcc
BuildRequires:  git-lfs
%if 0%{?el7}
BuildRequires:  python3
%endif
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
BuildRequires:  pkgconfig(alsa)
BuildRequires:  pkgconfig(atk)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(gdk-3.0)
BuildRequires:  pkgconfig(gdk-pixbuf-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(pango)
Requires:       %{name}-data = %{version}-%{release}
Requires:       hicolor-icon-theme
%if 0%{?fedora} || 0%{?rhel} >= 8
Recommends:     %{name}-chat-cli%{?_isa} = %{version}-%{release}
Recommends:     %{name}-server-cli%{?_isa} = %{version}-%{release}
%endif

%description
Veloren is a multiplayer voxel RPG written in Rust. It is inspired by games such
as Cube World, Legend of Zelda: Breath of the Wild, Dwarf Fortress and
Minecraft.


# Data package
%package        data
Summary:        Data files for %{name}
BuildArch:      noarch

Requires:       %{name} = %{version}-%{release}

%description    data
Data files for %{name}.


# Server CLI package
%package        server-cli
Summary:        Standalone server for %{name}

%if 0%{?fedora} || 0%{?rhel} >= 8
Recommends:     %{name}-chat-cli%{?_isa} = %{version}-%{release}
%endif

%description    server-cli
Standalone server for %{name}.


# Chat CLI package
%package        chat-cli
Summary:        Standalone chat for %{name}

%if 0%{?fedora} || 0%{?rhel} >= 8
Recommends:     %{name}-server-cli%{?_isa} = %{version}-%{release}
%endif

%description    chat-cli
Standalone chat for %{name}.


%prep
%autosetup -n %{name}-%{commit} -p1

# Unoptimize dev/debug builds
sed -i 's/opt-level = 2/opt-level = 0/' Cargo.toml

# Use recommended upstream veloren version of Rust toolchain
rust_toolchain=$(cat rust-toolchain)

git clone https://gitlab.com/veloren/veloren.git
curl https://sh.rustup.rs -sSf | sh -s -- --profile minimal --default-toolchain ${rust_toolchain} -y

# Sync to avoid different builds
pushd %{name}
git reset --hard %{commit}
popd


%build
pushd %{name}/voxygen
#VELOREN_ASSETS=assets
%if %{with release_build}
$HOME/.cargo/bin/cargo build --release
%else
$HOME/.cargo/bin/cargo build
%endif
popd

%if %{with release_build}
# Standalone server
pushd %{name}/server-cli
$HOME/.cargo/bin/cargo build --release
popd

# Standalone chat
pushd %{name}/chat-cli
$HOME/.cargo/bin/cargo build --release
popd
%endif


%install
# Disable cargo install until bug will been fixed in upstream
#$HOME/.cargo/bin/cargo install --root=%{buildroot}%{_prefix} --path=.
pushd %{name}
%if %{with release_build}
install -m 0755 -Dp target/release/%{name}-voxygen  %{buildroot}%{_bindir}/%{name}-voxygen
%else
install -m 0755 -Dp target/debug/%{name}-voxygen    %{buildroot}%{_bindir}/%{name}-voxygen
%endif
mkdir -p        %{buildroot}%{_datadir}/%{name}
cp -ap assets   %{buildroot}%{_datadir}/%{name}/

%if %{with release_build}
# Standalone server
install -m 0755 -Dp target/release/%{name}-server-cli   %{buildroot}%{_bindir}/%{name}-server-cli

# Standalone chat
install -m 0755 -Dp target/release/%{name}-chat-cli     %{buildroot}%{_bindir}/%{name}-chat-cli
%endif
popd

# Install desktop file, icon and appdata manifest
install -m 0644 -Dp %{SOURCE10} %{buildroot}%{_metainfodir}/%{uuid}.appdata.xml
install -m 0644 -Dp %{SOURCE11} %{buildroot}%{_datadir}/applications/%{uuid}.desktop
install -m 0644 -Dp %{SOURCE12} %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/%{uuid}.png


%check
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/*.xml
desktop-file-validate %{buildroot}%{_datadir}/applications/*.desktop


%files
%license LICENSE
%doc README.md CONTRIBUTING.md
%{_bindir}/%{name}-voxygen

%files data
%{_datadir}/%{name}/
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/*/*/*.png
%{_metainfodir}/*.xml

%if %{with release_build}
%files server-cli
%license LICENSE
%doc README.md
%{_bindir}/%{name}-server-cli

%files chat-cli
%license LICENSE
%doc README.md
%{_bindir}/%{name}-chat-cli
%endif


%changelog
* Thu Jan 09 2020 Artem Polishchuk <ego.cordatus@gmail.com> - 0.4.0-1.20200109git4e7c955
- Update to latest git snapshot

* Sun Jan 05 2020 Artem Polishchuk <ego.cordatus@gmail.com> - 0.4.0-1.20200105git4fa0515
- Update to latest git snapshot

* Wed Jan 01 2020 Artem Polishchuk <ego.cordatus@gmail.com> - 0.4.0-1.20200101git7313ec6
- Update to latest git snapshot

* Fri Dec 20 2019 Artem Polishchuk <ego.cordatus@gmail.com> - 0.4.0-1.20191220git6e64924
- Update to latest git snapshot

* Sat Dec 07 2019 Artem Polishchuk <ego.cordatus@gmail.com> - 0.4.0-1.20191207git3e2fe36
- Update to latest git snapshot

* Fri Nov 29 2019 Artem Polishchuk <ego.cordatus@gmail.com> - 0.4.0-1.20191128gitb7a084c
- Update to latest git snapshot
- Add desktop file, icon and appdata manifest
- Split into separate data package

* Sat Nov 23 2019 Artem Polishchuk <ego.cordatus@gmail.com> - 0.4.0-1.20191123git01aa89a
- Update to latest git snapshot

* Thu Nov 21 2019 Artem Polishchuk <ego.cordatus@gmail.com> - 0.4.0-1.20191121git905b3ac
- Update to latest git snapshot

* Wed Nov 13 2019 Artem Polishchuk <ego.cordatus@gmail.com> - 0.4.0-1.20191112giteb7b55d
- Update to latest git snapshot
- Add chat-cli package
- Minor packaging fixes

* Mon Nov 11 2019 Artem Polishchuk <ego.cordatus@gmail.com> - 0.4.0-1.20191109git5fe1eec
- Update to latest git snapshot
- Thanks @ElXreno <elxreno@gmail.com> for help with debugging build

* Sat Sep 07 2019 Artem Polishchuk <ego.cordatus@gmail.com> - 0.3.0-2.20190907git92c0edc
- Update to latest git snapshot

* Fri Mar 29 2019 Artem Polishchuk <ego.cordatus@gmail.com> - 0.3.0-1.20190906gitd41d020
- Initial package