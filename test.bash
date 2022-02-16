#sudo rm /usr/lib64/python3.10/site-packages/risiscript.py
sudo rm /bin/risiscript-run
sudo rm -rf /usr/share/risi-script-gtk
sudo rm /usr/share/glib-2.0/schemas/io.risi.script.gschema.xml

# sudo mkdir /usr/lib64/python3.10/site-packages/risi-script
sudo mkdir /usr/share/risi-script-gtk

sudo cp __main__.py /usr/lib64/python3.10/site-packages/risiscript.py
sudo cp risiscript-run.py /bin/risi-script-run
sudo cp risi-script-gtk/risi-script-gtk.ui /usr/share/risi-script-gtk/risi-script-gtk.ui
sudo cp io.risi.script.gschema.xml /usr/share/glib-2.0/schemas/io.risi.script.gschema.xml

# sudo glib-compile-schemas /usr/share/glib-2.0/schemas/

sudo chmod +x /bin/risiscript-run

python3 risi-script-gtk/__main__.py test.risisc
