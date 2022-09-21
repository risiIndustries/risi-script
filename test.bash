sudo rm -rf /usr/lib64/python3.10/site-packages/risi_script/
sudo rm /bin/risi-script-gtk
sudo rm -rf /usr/share/risi-script-gtk
sudo rm /usr/share/glib-2.0/schemas/io.risi.script.gschema.xml
sudo rm /usr/share/risi-script-gtk/risi-script-gtk.ui

sudo mkdir /usr/lib64/python3.10/site-packages/risi_script
sudo mkdir /usr/share/risi-script-gtk

sudo cp -a risi_script /usr/lib64/python3.10/site-packages
sudo cp risi_script_gtk/__main__.py /bin/risi-script-gtk
sudo cp risi-script-run.py /bin/risi-script-run
sudo cp risi_script_gtk/risi-script-gtk.ui /usr/share/risi-script-gtk/risi-script-gtk.ui

# sudo glib-compile-schemas /usr/share/glib-2.0/schemas/

#sudo chmod +x /bin/risi_script-run
#sudo chmod +x /bin/risi_script-gtk

# python3 risi_script-gtk/__main__.py --file test.risisc
# risi_script-gtk --file test.risisc
# risi_script-gtk --file /home/cameron/Documents/risi-welcome/usr/share/risiWelcome/scripts/quicksetup/graphicdesign.risisc
