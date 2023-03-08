sudo rm -rf /usr/lib64/python3.11/site-packages/risi_script
sudo rm -rf /usr/lib64/python3.11/site-packages/risi_script_gtk

sudo mkdir /usr/lib64/python3.11/site-packages/risi_script
sudo mkdir /usr/lib64/python3.11/site-packages/risi_script_gtk

sudo cp -a risi_script /usr/lib64/python3.11/site-packages
sudo cp -a risi_script_gtk /usr/lib64/python3.11/site-packages
sudo cp risi_script_gtk/__main__.py /bin/risi-script_gtk

sudo chmod +x /bin/risi_script_gtk

python3 risi_script_gtk/__main__.py --file standards.risisc

# python3 risi_script-gtk/__main__.py --file test.risisc
# risi_script-gtk --file test.risisc
# risi_script-gtk --file /home/cameron/Documents/risi-welcome/usr/share/risiWelcome/scripts/quicksetup/graphicdesign.risisc
