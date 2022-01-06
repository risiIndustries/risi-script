import os
import sys
import risiscript
import gi
import time
import threading
from copy import deepcopy

gi.require_version("Gtk", "3.0")
gi.require_version("Vte", "2.91")
from gi.repository import Gtk, GLib, Vte, Gio

saved_data = Gio.Settings.new("io.risi.script")

if len(sys.argv) >= 2:
    if not os.path.isfile(sys.argv[1]):
        print(f"File, {sys.argv[1]} doesn't exist")
        exit()
else:
    print("Please provide risi-script file")
    exit()


class ScriptWindow:
    def __init__(self):
        self.gui = Gtk.Builder()
        self.gui.add_from_file(
            "risiscriptgui.ui"
            # "/usr/share/risi-script-gtk/risiscriptgui.ui"
        )
        self.window = self.gui.get_object("window")
        self.stack = self.gui.get_object("pages")

        # Load Script
        with open(sys.argv[1], "r") as file:
            self.script = risiscript.Script(file.read())

        if self.script.installation_mode:
            self.run = "install"
        else:
            self.run = "run"
        self.gui.get_object("titlebar").set_title("risiScript - " + self.script.metadata.name)

        self.bash_pulse = False
        self.checks_pulse = False

        # Page 1 (Page showing the code)
        self.gui.get_object("textview").get_buffer().set_text(self.script.code)

        # Already installed page
        if self.script.installation_mode and self.script.can_update:
            self.gui.get_object("install_warning_text").set_label(
                self.gui.get_object("install_warning_text").get_label() +
                "\n <b>Update:</b> Updates whatever this script was made for."
            )
            self.gui.get_object("update_button").set_visible(True)
        self.arguments = {}

        self.gui.get_object("cancel_button").connect("clicked", self.installed_installer_buttons)
        self.gui.get_object("install_again_button").connect("clicked", self.installed_installer_buttons)
        self.gui.get_object("remove_button").connect("clicked", self.installed_installer_buttons)
        self.gui.get_object("update_button").connect("clicked", self.installed_installer_buttons)

        # Already run page
        self.gui.get_object("no_button").connect("clicked", self.installed_run_script_buttons)
        self.gui.get_object("yes_button").connect("clicked", self.installed_run_script_buttons)

        # Run Page
        self.terminal = Vte.Terminal()
        self.progressbar = self.gui.get_object("progress_bar")

        self.terminal.connect("child_exited", self.bash_done)
        self.terminal.set_vexpand(True)
        self.terminal.set_valign(Gtk.Align.FILL)
        self.terminal_cancellable = Gio.Cancellable()
        self.terminal_cancellable.connect(lambda: Gtk.main_quit())

        self.gui.get_object("run_page").add(self.terminal)
        self.gui.get_object("run_page").reorder_child(self.terminal, 0)

        # Terminal Cancel Dialog (defined here so it can be destroyed)
        self.run_cancel_dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            text="Are you sure you want to cancel this risiScript?",
        )
        self.run_cancel_dialog.add_buttons(
            "Yes",
            Gtk.ResponseType.YES,
            "No",
            Gtk.ResponseType.NO
        )
        self.run_cancel_dialog.format_secondary_text(
            "This will not reverse the changes this risiScript file has already made and can be destructive."
        )

        # Navigation Buttons
        self.back_btn = self.gui.get_object("back_btn")
        self.back_btn.connect("clicked", self.back_button_pressed)

        self.next_btn = self.gui.get_object("next_btn")
        self.next_btn.connect("clicked", self.next_button_pressed)

        if self.script.arguments is None:
            self.next_btn.set_label("Confirm")

    def generate_argument_widgets(self):
        # Gets (and removes using .pop()) first item of list from yaml arg and gets the class from dictionary
        box = self.gui.get_object("args")
        for child in box.get_children():
            if child != self.gui.get_object("arg_label"):
                child.destroy()
        if self.script.arguments:
            script_args = deepcopy(self.script.arguments)
            if script_args[self.run]:
                for arg in script_args[self.run]:
                    self.arguments[arg] = args_to_class[
                        script_args[self.run][arg].pop(0)
                    ](*script_args[self.run][arg])  # Passes YAML data as args for the class
                    box.add(self.arguments[arg])
                    self.arguments[arg].show_all()

    def generate_arguments(self):
        args = []
        if self.script.arguments[self.run] is not None:
            for arg in self.script.arguments[self.run]:
                args.append(self.arguments[arg].output())
        return args

    def get_arg_outputs(self):
        outputs = {}
        if self.script.arguments[self.run] is not None:
            for arg in self.script.arguments[self.run]:
                outputs[arg] = self.arguments[arg].output()
        return outputs

    def args_page(self):
        if self.script.arguments[self.run] is None:
            self.go_to_run_page()
        else:
            self.generate_argument_widgets()
            self.stack.set_visible_child_name("args")

    def back_button_pressed(self, button):
        if self.stack.get_visible_child_name() == "script_info":
            Gtk.main_quit()
        elif self.stack.get_visible_child_name() == "args":
            if self.script.installed:
                if self.script.installation_mode:
                    self.stack.set_visible_child_name("already_installed")
                    self.next_btn.set_sensitive(False)
                elif self.script.metadata.one_time_use:
                    self.stack.set_visible_child_name("already_ran")
                    self.next_btn.set_sensitive(False)
            else:
                button.set_label("Cancel")
                self.stack.set_visible_child_name("script_info")
        elif self.stack.get_visible_child_name() in ["already_installed", "already_ran"]:
            self.stack.set_visible_child_name("script_info")
            self.next_btn.set_sensitive(True)
            button.set_label("Cancel")
        elif self.stack.get_visible_child_name() == "run_page":
            response = self.run_cancel_dialog.run()

            if response == Gtk.ResponseType.YES:
                self.terminal_cancellable.cancel()
            self.run_cancel_dialog.destroy()

    def next_button_pressed(self, button):
        if self.stack.get_visible_child_name() == "script_info":
            self.back_btn.set_label("Back")
            if self.script.installed:
                if self.script.installation_mode:
                    self.stack.set_visible_child_name("already_installed")
                    button.set_sensitive(False)
                elif self.script.metadata.one_time_use:
                    self.stack.set_visible_child_name("already_ran")
                    button.set_sensitive(False)
            else:
                self.args_page()

        elif self.stack.get_visible_child_name() == "args":
            if not self.check_args():
                dialog = Gtk.MessageDialog(
                    transient_for=self.window,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text="Error: Blank Argument",
                )
                dialog.format_secondary_text(
                    "Make sure that all arguments are filled in"
                )
                dialog.run()
                dialog.destroy()
            else:
                self.go_to_run_page()

    def go_to_run_page(self):
        self.stack.set_visible_child_name("run_page")
        self.script.code_to_script()
        self.next_btn.set_visible(False)

        args = ["/bin/bash", self.script.bash_file_path]
        if self.run != "run":
            args.append(self.run)
        if self.arguments is not None:
            for arg in self.generate_arguments():
                args.append(str(arg))

        self.terminal.spawn_async(
            Vte.PtyFlags.DEFAULT,
            os.environ['HOME'],
            args,
            [],
            GLib.SpawnFlags.DEFAULT,
            None, None,
            -1,
            self.terminal_cancellable,
            None,
            None
        )

        self.back_btn.set_sensitive(True)
        self.back_btn.set_label("Cancel")
        self.next_btn.set_sensitive(False)

        self.bash_pulse = True
        pulse_thread = threading.Thread(target=self.pulse_threading)
        pulse_thread.daemon = True
        pulse_thread.start()

    def check_args(self):
        if self.script.arguments:
            for arg in self.script.arguments[self.run]:
                if self.arguments[arg].output() is None:
                    return False
        return True

    def bash_done(self, terminal, status):
        if status != 0:
            dialog = Gtk.MessageDialog(
                transient_for=self.window,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Error: Exit code not 0",
            )
            dialog.format_secondary_text(
                "The bash script has ran, but not successfully"
            )
            dialog.run()
            Gtk.main_quit()
        self.progressbar.set_text("Running Checks")

        self.bash_pulse = False
        self.checks_pulse = True
        self.run_cancel_dialog.destroy()
        self.back_btn.set_sensitive(False)

        self.progressbar.set_fraction(0)

    def pulse_threading(self):
        while self.bash_pulse is True:
            GLib.idle_add(lambda: self.progressbar.pulse())
            time.sleep(0.1)
        while self.checks_pulse is True:
            try:
                self.script.run_checks(
                    self.run, self.get_arg_outputs(),
                    lambda: self.progressbar.set_fraction(
                        self.progressbar.get_fraction() + 1 / self.script.metadata.number_of_checks[self.run]
                    )
                )
            except risiscript.RisiScriptFailedCheckError as e:
                error = e
                GLib.idle_add(lambda: self.progressbar.set_text("Checks Failed"))
                self.checks_pulse = False
                GLib.idle_add(lambda: self.progressbar.set_fraction(100))
                GLib.idle_add(lambda: self.failed_dialog(error))
            else:
                GLib.idle_add(lambda: self.progressbar.set_text("Done"))
                self.checks_pulse = False
                installed_list = saved_data.get_strv("installed-scripts")

                if self.script.metadata.id not in installed_list and self.script.installation_mode:
                    installed_list.append(self.script.metadata.id)
                    GLib.idle_add(lambda: saved_data.set_strv("installed-scripts", installed_list))

                GLib.idle_add(lambda: self.progressbar.set_fraction(100))
                GLib.idle_add(self.check_dialog)

    def check_dialog(self):
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Script ran successfully",
        )
        dialog.run()
        Gtk.main_quit()

    def failed_dialog(self, e):
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error: Script failed check",
        )
        dialog.format_secondary_text(
            str(e).replace("\n", "\\n")
        )
        dialog.run()
        Gtk.main_quit()

    def installed_run_script_buttons(self, button):
        if button == self.gui.get_object("no_button"):
            Gtk.main_quit()
        if button == self.gui.get_object("yes_button"):
            self.args_page()
            self.next_btn.set_sensitive(True)

    def installed_installer_buttons(self, button):
        if button == self.gui.get_object("cancel_button"):
            Gtk.main_quit()
        else:
            if button == self.gui.get_object("remove_button"):
                self.run = "remove"
            elif button == self.gui.get_object("update_button"):
                self.run = "update"
            print(self.run)
            self.args_page()
            self.next_btn.set_sensitive(True)


class Argument(Gtk.Box):
    def __init__(self, arg_label):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        label = Gtk.Label(label=arg_label)
        label.set_halign(Gtk.Align.START)
        self.add(label)

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

    def add_widget(self, widget):
        widget.set_hexpand(True)
        widget.set_halign(Gtk.Align.END)
        self.add(widget)

    def output(self):
        return None


class ArgEntry(Argument):
    def __init__(self, arg_label):
        Argument.__init__(self, arg_label)
        self.entry = Gtk.Entry()
        self.add_widget(self.entry)

    def output(self):
        return self.entry.get_text()


class ArgFile(Argument):
    def __init__(self, arg_label, file_pattern):
        Argument.__init__(self, arg_label)
        self.fbtn = Gtk.FileChooserButton(title=arg_label, action=Gtk.FileChooserAction.OPEN)
        pattern = Gtk.FileFilter()
        pattern.add_pattern(file_pattern)
        self.fbtn.set_filter(pattern)
        self.add_widget(self.fbtn)

    def output(self):
        try:
            return self.fbtn.get_file().get_path()
        except AttributeError:
            return None


class ArgDir(Argument):
    def __init__(self, arg_label):
        Argument.__init__(self, arg_label)
        self.fbtn = Gtk.FileChooserButton(title=arg_label, action=Gtk.FileChooserAction.SELECT_FOLDER)
        pattern = Gtk.FileFilter()
        pattern.add_pattern("*")
        self.fbtn.set_filter(pattern)
        self.add_widget(self.fbtn)

    def output(self):
        try:
            return self.fbtn.get_file().get_path()
        except AttributeError:
            return None


class ArgChoice(Argument):
    def __init__(self, arg_label, choices):
        Argument.__init__(self, arg_label)
        self.combo = Gtk.ComboBoxText()
        for choice in choices:
            self.combo.append_text(choice)
        self.add_widget(self.combo)

    def output(self):
        return self.combo.get_active_text()


class ArgBoolean(Argument):
    def __init__(self, arg_label, default):
        Argument.__init__(self, arg_label)
        self.switch = Gtk.Switch()
        self.switch.set_active(default)
        self.add_widget(self.switch)

    def output(self):
        return str(self.switch.get_active())


args_to_class = {
    "ENTRY": ArgEntry,
    "FILE": ArgFile,
    "DIRECTORY": ArgDir,
    "CHOICE": ArgChoice,
    "BOOLEAN": ArgBoolean
}

window = ScriptWindow()
window.window.show_all()
Gtk.main()
