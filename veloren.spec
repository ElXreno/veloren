## WIP, expect some crap in packaging
## Note: requires internet access during build procces because of Rust nightly and git-lfs

%global debug_package %{nil}

%global commit        5fe1eecf1f1f1394c92d410cc324e6e3f4aee718
%global shortcommit   %(c=%{commit}; echo ${c:0:7})
%global date          20191109

Name:           veloren
Version:        0.4.0
Release:        2.%{date}git%{shortcommit}%{?dist}
Summary:        Multiplayer voxel RPG written in Rust

License:        GPLv3+
URL:            https://gitlab.com/veloren/veloren
Source0:        %{url}/-/archive/%{commit}/%{name}-%{version}.%{date}git%{shortcommit}.tar.gz

# BuildRequires:  cargo >= 1.40
# BuildRequires:  desktop-file-utils
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
# Requires:       hicolor-icon-theme
Recommends:     %{name}-server-cli%{?_isa}

%description
Veloren is a multiplayer voxel RPG written in Rust. It is inspired by games
such as Cube World, Legend of Zelda: Breath of the Wild, Dwarf Fortress
and Minecraft.


%package        server-cli
Summary:        Standalone server for %{name}

Recommends:     %{name}%{?_isa} = %{version}-%{release}

%description    server-cli
Standalone server for %{name}.


%package        chat-cli
Summary:        Console chat for %{name}

Recommends:     %{name}%{?_isa} = %{version}-%{release}

%description    chat-cli
Console chat for %{name}.


%prep
%autosetup -p1 -n %{name}-%{commit}

## Use recommended upstream veloren version of Rust toolchain
rust_toolchain=$(cat rust-toolchain)
curl https://sh.rustup.rs -sSf | sh -s -- --default-toolchain ${rust_toolchain} --profile minimal -y

git clone https://gitlab.com/veloren/veloren.git

pushd veloren
git reset --hard %{commit}
# sed -i 's/codegen-units = 1/opt-level = 0/; /lto = true/d' Cargo.toml
popd
# sed -i '/default-run = "veloren-voxygen"/d' voxygen/Cargo.toml


%build
pushd veloren
$HOME/.cargo/bin/cargo build --release
popd

%install
pushd veloren

## Game
install -m 0755 -Dp target/release/%{name}-voxygen      %{buildroot}%{_bindir}/%{name}-voxygen
mkdir -p                                                %{buildroot}%{_datadir}/%{name}
cp -a assets                                            %{buildroot}%{_datadir}/%{name}

## Standalone server
install -m 0755 -Dp target/release/%{name}-server-cli   %{buildroot}%{_bindir}/%{name}-server-cli

## Console chat
install -m 0755 -Dp target/release/%{name}-chat-cli     %{buildroot}%{_bindir}/%{name}-chat-cli

popd


%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}-voxygen
%{_datadir}/%{name}

%files server-cli
%license LICENSE
%doc README.md
%{_bindir}/%{name}-server-cli

%files chat-cli
%license LICENSE
%doc README.md
%{_bindir}/%{name}-chat-cli


%changelog
* Mon Nov 11 2019 ElXreno <elxreno@gmail.com> - 0.4.0-2.20191107git5fe1eec
- Fixed building and added chat-cli package

* Sat Sep 07 2019 Artem Polishchuk <ego.cordatus@gmail.com> - 0.3.0-2.20190907git92c0edc
- Update to latest git snapshot

* Fri Mar 29 2019 Artem Polishchuk <ego.cordatus@gmail.com> - 0.3.0-1.20190906gitd41d020
- Initial package
