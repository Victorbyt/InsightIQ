{ pkgs }: {
  deps = [
    pkgs.python3
    pkgs.python3Packages.pip
    pkgs.zlib
    pkgs.libffi
    pkgs.openssl
  ];
}
