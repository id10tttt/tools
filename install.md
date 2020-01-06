# XPS 9570 install macOS under Linux(Debian)

1. format the driver
    
    fdisk /dev/sda
        n
            partition number: keep blank for default
            first sector: keep blank for default
            last sector: +200M to create a 200MB partition that will be named later on CLOVER
        t
            1
                1(EFI)
        n
            partition number: keep blank for default
            first sector: keep blank for default
            last sector: keep black for default
        t
            2
                38(HPS)
        w

1. use qemu macos to make bootable flash driver(https://github.com/foxlet/macOS-Simple-KVM)
    lsusb
        Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
        Bus 001 Device 004: ID 27c6:5395 HTMicroelectronics Goodix Fingerprint Device 
        Bus 001 Device 003: ID 8087:0029 Intel Corp. 
        Bus 001 Device 005: ID 0c45:671d Microdia Integrated_Webcam_HD
        Bus 001 Device 002: ID 046d:c52f Logitech, Inc. Unifying Receiver
        Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub

    find out the ID and replace blow and add to basic.sh
        -device usb-ehci,id=ehci \
        -device usb-host,bus=ehci.0,vendorid=0x0930,productid=0x1408 \
2. after install and make bootable driver
3. You should execute : mkfs.vfat -F 32 -n "CLOVER" /dev/sda1
4. then: 
    sudo mount /dev/sda1 /mnt
    cd /mnt
    cp -R ~/Dell-XPS-15-9570-macOS-Mojave/EFI .
    cp -R ~/xps-9570-mojave/EFI/APPLE .
    cd EFI/CLOVER
    cp config.plist config.plist.bk
    cp config_1080.plist config.plist
5. reboot

You must confirm the driver format is right.
if not:
1. format the driver
    
    fdisk /dev/sda
        n
            partition number: keep blank for default
            first sector: keep blank for default
            last sector: +200M to create a 200MB partition that will be named later on CLOVER
        t
            1
                1(EFI)
        n
            partition number: keep blank for default
            first sector: keep blank for default
            last sector: keep black for default
        t
            2
                38(HPS)
        w