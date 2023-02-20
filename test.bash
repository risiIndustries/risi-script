sudo rm -rf /usr/lib64/python3.11/site-packages/risi_script
sudo rm /bin/risi-script-gtk
sudo rm -rf /usr/share/risi-script-gtk
# sudo rm /usr/share/risi-script-gtk/risi-script-gtk.ui

sudo mkdir /usr/lib64/python3.11/site-packages/risi_script
sudo mkdir /usr/share/risi-script-gtk

sudo cp -a risi_script /usr/lib64/python3.11/site-packages
sudo cp risi_script_gtk/__main__.py /bin/risi-script-gtk
sudo cp risi_script_gtk/risi-script-gtk.ui /usr/share/risi-script-gtk/risi-script-gtk.ui

sudo chmod +x /bin/risi_script-gtk

python3 risi_script/__main__.py run standards.risisc action hello

# python3 risi_script-gtk/__main__.py --file test.risisc
# risi_script-gtk --file test.risisc
# risi_script-gtk --file /home/cameron/Documents/risi-welcome/usr/share/risiWelcome/scripts/quicksetup/graphicdesign.risisc
