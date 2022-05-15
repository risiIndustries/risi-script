#sudo rm /usr/lib64/python3.10/site-packages/risiscript.py
sudo rm /bin/risi-script-run
sudo rm /bin/risi-script-gtk
sudo rm -rf /usr/share/risi-script-gtk
sudo rm /usr/share/glib-2.0/schemas/io.risi.script.gschema.xml
sudo rm /usr/share/risi-script-gtk/risi-script-gtk.ui

# sudo mkdir /usr/lib64/python3.10/site-packages/risi-script
sudo mkdir /usr/share/risi-script-gtk

sudo cp __main__.py /usr/lib64/python3.10/site-packages/risiscript.py
sudo cp risi-script-gtk/__main__.py /bin/risi-script-gtk
sudo cp risi-script-run.py /bin/risi-script-run
sudo cp risi-script-gtk/risi-script-gtk.ui /usr/share/risi-script-gtk/risi-script-gtk.ui
sudo cp io.risi.script.gschema.xml /usr/share/glib-2.0/schemas/io.risi.script.gschema.xml

# sudo glib-compile-schemas /usr/share/glib-2.0/schemas/

sudo chmod +x /bin/risi-script-run
sudo chmod +x /bin/risi-script-gtk

# python3 risi-script-gtk/__main__.py --file test.risisc
risi-script-gtk --file test.risisc
# risi-script-gtk --file /home/cameron/Documents/risi-welcome/usr/share/risiWelcome/scripts/quicksetup/graphicdesign.risisc
