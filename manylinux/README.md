# manylinux scripts

[manylinux](https://github.com/pypa/manylinux) is a set of old docker containers based on CentOS
with modern compilers and Python installed whose aim is to allow to construction of binary wheels
which would be compatible across the widest range of linux system because they use system library
ABIs which are available for most systems in use.

Because we need to use the Matlab compiler `mcc` in our builds we cannot use the stock 
manylinux container images.
Also, Matlab activations are locked (on Linux) to particular MAC addresses so we need to be able
to set the MAC address of the image.
This cannot be done in a `Dockerfile` so instead we just run the container, install Matlab and
then do the build in one script (which unfortunately takes longer than if there was a 
manylinux container with Matlab pre-installed).

# Usage

To use this you must first have a Matlab installable in the `install_dir` folder (currently empty).
You must first download a Matlab installation executable from your Mathworks account.
Then run it on a system with a GUI, and select "I want to download without installing" from the
"Advance options" menu on the top left.
Set the `install_dir` as the download folder and download the installation files.
Then return to your Mathworks webpage / account and select to "Activate to Retrieve License File"
putting in the Matlab version you had downloaded, and a MAC address. 
This could be randomly generated or you can use a Docker standard address
(often `02:42:AC:11:00:02` is used if you've only run one container).
Put this MAC address in the file `mac_address`.
Put `root` as the user.
Then copy the file installation key to the file `installation_key` and the license file to `license.lic`.

Then run this container with:

```
docker run --mac-address=$(cat mac_address) -v /mnt/hdd/docker/:/mnt quay.io/pypa/manylinux2010_x86_64 /mnt/installscript.sh
```

You can replace `manylinux2010_x86_64` with which other image you like.
