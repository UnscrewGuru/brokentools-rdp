# Maintainer: Unscrew Guru
pkgname=brokentools-rdp
pkgver=1.0.0
pkgrel=1
pkgdesc="Simple, familiar RDP client window for Linux (PyQt6 front-end for FreeRDP)"
arch=('any')
url="https://github.com/UnscrewGuru/brokentools-rdp"
license=('GPL-3.0-or-later')
depends=('python' 'python-pyqt6' 'freerdp')
source=("$pkgname-$pkgver.tar.gz::$url/archive/refs/tags/v$pkgver.tar.gz")
# Replace with the real checksum by running `updpkgsums` (package pacman-contrib)
# after the v1.0.0 tag exists on GitHub.
sha256sums=('SKIP')

package() {
    cd "$pkgname-$pkgver"
    install -Dm755 brokentools_rdp.py "$pkgdir/usr/share/$pkgname/brokentools_rdp.py"
    printf '#!/bin/sh\nexec python3 /usr/share/%s/brokentools_rdp.py "$@"\n' "$pkgname" \
        | install -Dm755 /dev/stdin "$pkgdir/usr/bin/$pkgname"
    install -Dm644 brokentools-rdp.desktop "$pkgdir/usr/share/applications/brokentools-rdp.desktop"
    install -Dm644 brokentools-rdp.svg "$pkgdir/usr/share/icons/hicolor/scalable/apps/brokentools-rdp.svg"
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
