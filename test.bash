sudo rm /usr/lib64/python3.10/site-packages/risiscript.py
sudo rm /bin/risiscript-run
sudo rm /usr/share/risi-script-gtk/risi-script-gtk.ui

sudo mkdir /usr/lib64/python3.10/site-packages/risi-script
sudo mkdir /usr/share/risi-script-gtk

sudo cp __main__.py /usr/lib64/python3.10/site-packages/risiscript.py
sudo cp risiscript-run.py /bin/risiscript-run
sudo cp risi-script-gtk/risi-script-gtk.ui /usr/share/risi-script-gtk/risi-script-gtk.ui

sudo chmod +x /bin/risiscript-run

python3 risi-script-gtk/__main__.py test.risisc