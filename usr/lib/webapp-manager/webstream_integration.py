import webstream
import gi
import requests
import textwrap

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, Gio, GdkPixbuf, Gdk

webstream_url = "https://raw.githubusercontent.com/risiOS/risi-webstream-repo/main/repo.yml"
icons_url = "https://raw.githubusercontent.com/risiOS/risi-webstream-repo/main/icons/{}.png"


class ListboxApp(Gtk.Box):
    def __init__(self, app, main_window, store_window):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self.app = app
        self.main_window = main_window
        self.store_window = store_window

        image = Gtk.Image.new_from_icon_name(
            "applications-internet",
            Gtk.IconSize.DIALOG
        )

        pixbuf = pixbuf_from_url(
            icons_url.format(app.appid)
        )

        if not pixbuf:
            image.set_from_pixbuf(
                Gtk.IconTheme().load_icon("applications-internet", 64, Gtk.IconLookupFlags.FORCE_SIZE)
            )
        else:
            pixbuf = pixbuf.scale_simple(64, 64, GdkPixbuf.InterpType.BILINEAR)
            image.set_from_pixbuf(
                pixbuf
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
        installButton.connect("clicked", self.install_button)
        homepageButton.connect("clicked", self.url_button)

        buttonBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        buttonBox.add(installButton)
        buttonBox.add(homepageButton)

        self.add(image)
        self.add(nameAndDescriptionBox)
        self.add(buttonBox)
        self.set_halign(Gtk.Align.FILL)

    def install_button(self, button):
        self.main_window.on_add_button(button)
        self.main_window.name_entry.set_text(self.app.name)
        self.main_window.url_entry.set_text(self.app.url)
        self.main_window.category_combo.set_active(
            list(
                self.store_window.tab_category.values()
            ).index(self.app.main_category)
        )
        self.store_window.window.destroy()

    def url_button(self, button):
        Gtk.show_uri_on_window(self.store_window.window, self.app.homepage, Gdk.CURRENT_TIME)

class StoreWindow:
    def __init__(self, main_window):
        self.main_window = main_window
        self.previous_tab = 0
        # Gtk.ApplicationWindow.__init__(self)

        # Glade file
        self.gui = Gtk.Builder()
        self.gui.add_from_file(
            "/usr/share/webapp-manager/webstream-integration.ui"
        )

        self.window = self.gui.get_object("storeWindow")
        self.window.set_modal(True)
        self.window.set_transient_for(self.main_window.window)

        # Loading data from webstream
        self.app_store = webstream.Storage()
        self.app_store.load_from_url(webstream_url)

        # A dictionary for the category tabs.
        self.tab_category = {
            1: "Audio",
            2: "Utility",
            3: "Development",
            4: "Education",
            5: "Game",
            6: "Graphics",
            7: "Network",
            8: "Office",
            9: "Video"
        }

        self.gui.get_object("tabs").connect("switch-page", self.tab_switched)
        self.load_featured(self.gui.get_object("featured_list"))

    def load_featured(self, page):
        for app in self.app_store.get_apps_by_tag("Featured"):
            app.main_category = app.categories[0]
            page.add(ListboxApp(app, self.main_window, self))

    def tab_switched(self, notebook, page, page_id):
        for child in notebook.get_nth_page(self.previous_tab):
            child.destroy()

        if page_id == 0:
            self.load_featured(page)
        else:
            for app in self.app_store.get_apps_by_category(self.tab_category[page_id]):
                app.main_category = self.tab_category[page_id]
                page.add(ListboxApp(app, self.main_window, self))
        page.show_all()

        self.previous_tab = page_id


def pixbuf_from_url(url):
    try:
        image = requests.get(url)
    except (requests.ConnectionError, requests.HTTPError, requests.RequestException) as error:
        return False

    return GdkPixbuf.Pixbuf.new_from_stream(
        Gio.MemoryInputStream.new_from_data(image.content, None)
    )
