# rbtempo: plugin to control Rhythmbox playback speed
# Copyright (C) 2015  Bruce Merry <bmerry@users.sourceforge.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import GObject, GLib, Gio, Gtk, RB, Peas, Gst

class RBTempoPlugin(GObject.Object, Peas.Activatable):
    object = GObject.property(type=GObject.GObject)

    def get_shell(self):
        return self.object

    def get_player(self):
        return self.get_shell().props.shell_player.props.player

    def get_toolbar(self):
        """Get the widget for the main toolbar. This is rather fragile, but
        there doesn't seem to be a way to find the toolbar by name now that
        Rhythmbox doesn't use GtkUIManager.
        """
        return self.get_shell().props.shell_player.props.header.get_parent().get_parent()

    def tempo_changed(self, adj, user):
        # Convert delta percent to scale value
        self.pitch_element.props.tempo = adj.get_value() * 0.01 + 1.0

    def create_tempo_scale(self):
        tempo_adj = Gtk.Adjustment(value=0, lower=-50, upper=200, step_increment=5, page_increment=10)
        tempo_adj.connect('value-changed', self.tempo_changed, None)
        tempo_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        tempo_scale.set_adjustment(tempo_adj)
        tempo_scale.set_size_request(100, -1)
        tempo_scale.set_digits(0)
        tempo_scale.set_value_pos(Gtk.PositionType.RIGHT)
        self.tempo_adj = tempo_adj
        return tempo_scale

    def reset(self, button):
        self.tempo_adj.set_value(0)

    def create_reset_button(self):
        reset_button = Gtk.Button.new_from_icon_name('edit-undo', 3)
        reset_button.connect('clicked', self.reset)
        reset_button.show()
        return reset_button

    def create_toolbox(self):
        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 3)
        box.pack_start(self.create_tempo_scale(), True, True, 0)
        box.pack_start(self.create_reset_button(), False, False, 0)
        item = Gtk.ToolItem.new()
        # These margins are based on Rhythmbox's UI description
        item.set_margin_left(6)
        item.set_margin_top(12)
        item.set_margin_bottom(12)
        item.add(box)
        item.show_all()
        return item

    def do_activate(self):
        """Plugin activation callback"""
        self.pitch_element = Gst.ElementFactory.make("pitch", None)
        self.get_player().add_filter(self.pitch_element)
        self.toolbox = self.create_toolbox()
        self.get_toolbar().insert(self.toolbox, 2)

    def do_deactivate(self):
        """Plugin deactivation callback"""
        self.get_toolbar().remove(self.toolbox)
        self.get_player().remove_filter(self.pitch_element)
        del self.toolbox
        del self.pitch_element
