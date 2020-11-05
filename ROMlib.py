from n64swap import RomType, get_rom_format, convert
import zipfile
import hashlib
import io
import sys

VALID_HASHES = [
    "4ec89bd5cfe2aec976b6db48e9abba9046eaccdd89b1f40893be1a0f6740decf24d95bc06313966a044034233c2d1774c00ef7539d3734297b378dfd34645e47",
    "023daf8ae8aff8b23f37bf686e1ad96f0db2da7069c00a2fbf0f82009f85b46182b5134e09a608fa1e0e8bb972ca651cfbec870f10a26d551626765cc90b2dc6",
    "9627ed0bd2339b5c2270ff103b33842fdc86641982224b8e2c3f6996ece2fd47f3316ec65935af97ce74850930958a9350dfcb5a144d0bd3dc2aae3f39d7b0cb",
    "637d4c47b6f56aefebadd70bb7725419fbc56b481bf06db21f36878deb4b9f79485b347034c81973120998ebe5eb89a968676835bc07d6b1025284d14b492da0",
    "002149ef37ea938d4c813abb904dbd9193b1e68c93c7f4f171fd3dd88c689992664b054154946f032de6cd086577ce593103ea5b2de22450bbf1d7c464470cab",
    "12acfecb0c774c7e06f87c2da1f4fa1215183cfbf173cb92068acaa73671b7ba78a66d0b019d27fa3efce11543da73b09bc52e98ad70769fd26ed46987aa4348",
    "b3fdc449dc0b18bd2beacbc32f5ee84c9c371c624cc369d927d70e9194c4f3af7b0754c6f99b4404b0ceb7e395057824cbd075b36fc8e63d2495f79df3e37f00",
    "3d88a87d384ae6e1610e782c82deda8e67cda4b4433908f0f4ce65ecf141570706f34f9c307234b7528387e7f70031815c075017979a99c37ed160f12b9f55dc",
    "13e32e5282e202e899fd57f0e7152917ae546e5080be1538261b1819304d557927d0cd541c39f89a4892cd15f1c1e75a91473e0b2224f9567fac2e9b59b03c4a",
    "eb05e897c7e1a431e5de26c61bd8bb76c58191a7077e67bf1dd5c4f8da58abc9a1c86125ca3ffd698438feebc58fd53558b3e18a19801640ed36ee90c741583b",
    "c85c207181238bf98b14db54e97a3c09df7e4e1841dc1f9050edcc6525e99e5ffa6fccddfd5911e7ea87ff0625cf9e61cb375a7638bc39820e4e4b55ff45b369",
    "b108cb20e0181b7ea029b19c6070b8108c96417da88c3d2e7e52cf9f1ed2171218ef1417c3b3c70facbb28a1b1a07cc36c4076cf9e845d543085a81993d51adb"]

INFO_TABLE = {
    "4ec89bd5cfe2aec976b6db48e9abba9046eaccdd89b1f40893be1a0f6740decf24d95bc06313966a044034233c2d1774c00ef7539d3734297b378dfd34645e47": (
        "eu", "n64"),
    "023daf8ae8aff8b23f37bf686e1ad96f0db2da7069c00a2fbf0f82009f85b46182b5134e09a608fa1e0e8bb972ca651cfbec870f10a26d551626765cc90b2dc6": (
        "eu", "v64"),
    "9627ed0bd2339b5c2270ff103b33842fdc86641982224b8e2c3f6996ece2fd47f3316ec65935af97ce74850930958a9350dfcb5a144d0bd3dc2aae3f39d7b0cb": (
        "eu", "z64"),
    "637d4c47b6f56aefebadd70bb7725419fbc56b481bf06db21f36878deb4b9f79485b347034c81973120998ebe5eb89a968676835bc07d6b1025284d14b492da0": (
        "jp", "n64"),
    "002149ef37ea938d4c813abb904dbd9193b1e68c93c7f4f171fd3dd88c689992664b054154946f032de6cd086577ce593103ea5b2de22450bbf1d7c464470cab": (
        "jp", "v64"),
    "12acfecb0c774c7e06f87c2da1f4fa1215183cfbf173cb92068acaa73671b7ba78a66d0b019d27fa3efce11543da73b09bc52e98ad70769fd26ed46987aa4348": (
        "jp", "z64"),
    "b3fdc449dc0b18bd2beacbc32f5ee84c9c371c624cc369d927d70e9194c4f3af7b0754c6f99b4404b0ceb7e395057824cbd075b36fc8e63d2495f79df3e37f00": (
        "sh", "n64"),
    "3d88a87d384ae6e1610e782c82deda8e67cda4b4433908f0f4ce65ecf141570706f34f9c307234b7528387e7f70031815c075017979a99c37ed160f12b9f55dc": (
        "sh", "v64"),
    "13e32e5282e202e899fd57f0e7152917ae546e5080be1538261b1819304d557927d0cd541c39f89a4892cd15f1c1e75a91473e0b2224f9567fac2e9b59b03c4a": (
        "sh", "z64"),
    "eb05e897c7e1a431e5de26c61bd8bb76c58191a7077e67bf1dd5c4f8da58abc9a1c86125ca3ffd698438feebc58fd53558b3e18a19801640ed36ee90c741583b": (
        "us", "n64"),
    "c85c207181238bf98b14db54e97a3c09df7e4e1841dc1f9050edcc6525e99e5ffa6fccddfd5911e7ea87ff0625cf9e61cb375a7638bc39820e4e4b55ff45b369": (
        "us", "v64"),
    "b108cb20e0181b7ea029b19c6070b8108c96417da88c3d2e7e52cf9f1ed2171218ef1417c3b3c70facbb28a1b1a07cc36c4076cf9e845d543085a81993d51adb": (
        "us", "z64")}


class ROM:
    def __init__(self, file):
        if zipfile.is_zipfile(file):
            with zipfile.ZipFile(file) as romzip:
                files = list(filter(lambda info: not info.is_dir(), romzip.infolist()))
                romfiles = list(filter(lambda info: info.filename.endswith(('.n64', '.z64', '.v64')), files))
                if len(romfiles) > 1:
                    raise ValueError('Too many ROM files in the zip')
                elif len(romfiles) == 0:
                    raise ValueError('No ROM files in the zip')
                with romzip.open(romfiles[0], 'rb') as romfile:
                    romtype = get_rom_format(romfile.read(4))
                    if romtype == RomType.UNKNOWN:
                        raise ValueError("Invalid ROM file")
                    romfile.seek(0)
                    self.ROM = romfile.read()
        romtype = get_rom_format(file.read(4))
        if romtype == RomType.UNKNOWN:
            raise ValueError("Invalid ROM file")
        file.seek(0)
        self.ROM = file.read()
        romhash = hashlib.sha512(self.ROM).hexdigest()
        if romhash not in VALID_HASHES:
            raise ValueError("ROM file is not genuine")
        self.metadata = INFO_TABLE[romhash]

    def to_z64(self, outfile, log=sys.stdout):
        infile = io.BytesIO(self.ROM)
        convert(infile, outfile, log_file=log)

    def get_correct_filename(self):
        return 'baserom.{0[0]}.{0[1]}'.format(self.metadata)
