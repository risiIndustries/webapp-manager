import webstream
import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Pango

webstream_url = "https://raw.githubusercontent.com/risiOS/risi-webstream-repo/main/repo.yml"

class ListboxApp(Gtk.Box):
    def __init__(self, app):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self.app = app

        image = Gtk.Image.new_from_icon_name(
            "applications-internet",
            Gtk.IconSize.DIALOG
        )

        nameAndTagBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        mainLabel = Gtk.Label()
        mainLabel.set_markup("<b>%s</b>" % app.name)
        nameAndTagBox.add(mainLabel)

        # for tag in app.tags:
        #     print(tag) # Placeholder

        descriptionLabel = Gtk.Label(label=app.description, xalign=0)
        descriptionLabel.set_ellipsize(Pango.EllipsizeMode.END)

        nameAndDescriptionBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        nameAndDescriptionBox.add(nameAndTagBox)
        nameAndDescriptionBox.add(descriptionLabel)
        nameAndDescriptionBox.set_hexpand(True)
        nameAndDescriptionBox.set_margin_start(5)
        nameAndDescriptionBox.set_margin_top(5)

        installButton = Gtk.Button.new_from_icon_name(
            "document-save-symbolic", Gtk.IconSize.BUTTON
        )
        homepageButton = Gtk.Button.new_from_icon_name(
            "insert-link-symbolic", Gtk.IconSize.BUTTON
        )

        installButton.set_relief(Gtk.ReliefStyle.NONE)
        homepageButton.set_relief(Gtk.ReliefStyle.NONE)
        installButton.get_style_context().add_class("circular")
        homepageButton.get_style_context().add_class("circular")
        buttonBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        buttonBox.add(installButton)
        buttonBox.add(homepageButton)

        self.add(image)
        self.add(nameAndDescriptionBox)
        self.add(buttonBox)
        self.set_halign(Gtk.Align.FILL)

class storeWindow:
    def __init__(self, mainWindow):
        self.previous_tab = 0
        # Gtk.ApplicationWindow.__init__(self)

        # Glade file
        self.gui = Gtk.Builder()
        self.gui.add_from_file(
            "/usr/share/webapp-manager/webstream-integration.ui"
        )

        self.window = self.gui.get_object("storeWindow")
        self.window.set_modal(True)
        self.window.set_transient_for(mainWindow.window)

        # Loading data from webstream
        self.app_store = webstream.Storage()
        self.app_store.load_from_url(webstream_url)

        # A dictionary for the category tabs.
        self.tab_category = {}
        self.tab_category[1] = "audio"
        self.tab_category[2] = "utility"
        self.tab_category[3] = "development"
        self.tab_category[4] = "education"
        self.tab_category[5] = "games"
        self.tab_category[6] = "graphics"
        self.tab_category[7] = "internet"
        self.tab_category[8] = "productivity"
        self.tab_category[9] = "video"

        self.gui.get_object("tabs").connect("switch-page", self.tab_switched)

    def tab_switched(self, notebook, page, page_id):
        for child in notebook.get_nth_page(self.previous_tab):
            child.destroy()

        if page_id == 0:
            for app in self.app_store.get_apps_by_tag("featured"):
                page.add(ListboxApp(app))
        else:
            for app in self.app_store.get_apps_by_category(self.tab_category[page_id]):
                page.add(ListboxApp(app))
        page.show_all()

        self.previous_tab = page_id

    def install_button(self, button, app):
        self.name_entry.set_text(app.name)
        self.url_entry.set_text(app.url)
        self.icon_chooser.set_icon("webapp-manager")
        self.category_combo.set_active(0)
        self.browser_combo.set_active(0)
        self.isolated_switch.set_active(True)
        self.navbar_switch.set_active(False)
        self.privatewindow_switch.set_active(False)
        for widget in self.add_specific_widgets:
            widget.show()
        self.show_hide_browser_widgets()
        self.stack.set_visible_child_name("add_page")
        self.headerbar.set_subtitle(_("Add a New Web App"))
        self.edit_mode = False
        self.toggle_ok_sensitivity()
        self.name_entry.grab_focus()
        self.stack.set_visible_child_name("add_page")
