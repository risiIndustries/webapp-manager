import threading
import time

import webstream
import gi
import requests
import tempfile

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, Gio, GdkPixbuf, Gdk, GLib

webstream_url = "https://raw.githubusercontent.com/risiOS/risi-webstream-repo/main/repo.yml"
icons_url = "https://raw.githubusercontent.com/risiOS/risi-webstream-repo/main/icons/{}.png"

# A dictionary for the category tabs.
tab_category = {
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

class ListboxApp(Gtk.Box):
    def __init__(self, app, main_window):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self.app = app
        self.main_window = main_window

        image = Gtk.Image.new_from_icon_name(
            "webapp-default", 64
        )

        self.pixbuf = pixbuf_from_url(
            icons_url.format(app.appid)
        )

        if not self.pixbuf:
            self.pixbuf = None
        else:
            self.pixbuf = self.pixbuf.scale_simple(64, 64, GdkPixbuf.InterpType.BILINEAR)
        if self.pixbuf:
            image.set_from_pixbuf(
                self.pixbuf
            )

        nameAndTagBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        mainLabel = Gtk.Label()
        mainLabel.set_markup("<b>%s</b>" % app.name)
        nameAndTagBox.add(mainLabel)

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
        # Generate icon
        icon_path = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        self.pixbuf.savev(
            icon_path.name,
            "png"
        )

        self.main_window.on_add_button(button)
        self.main_window.name_entry.set_text(self.app.name)
        self.main_window.url_entry.set_text(f"https://redirect.risi.io/?url={self.app.url}")
        self.main_window.category_combo.set_active(
            list(
                tab_category.values()
            ).index(self.app.main_category)
        )
        self.main_window.icon_chooser.set_icon(icon_path.name)
        self.get_toplevel().destroy()

    def url_button(self, button):
        Gtk.show_uri_on_window(self.store_window.window, self.app.homepage, Gdk.CURRENT_TIME)


class StoreWindow:
    def __init__(self, main_window):
        self.main_window = main_window
        self.previous_tab = 0
        self.stop_event = threading.Event()
        self.thread = threading.Thread()

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

        self.gui.get_object("tabs").connect("switch-page", self.tab_switched)
        self.load_featured(self.gui.get_object("featured_list"))

        search_page = Search(self.app_store, self.main_window)
        self.gui.get_object("searchpage").add(search_page)
        self.gui.get_object("searchbox").connect("changed", lambda query: search_page.search(query.get_text()))

    def load_featured(self, page):
        for app in self.app_store.get_apps_by_tag("Featured"):
            app.main_category = app.categories[0]
            page.add(ListboxApp(app, self.main_window))

    def tab_switched(self, notebook, page, page_id):
        for child in notebook.get_nth_page(self.previous_tab).get_children()[0].get_children()[0]:
            child.destroy()
        for thr in threading.enumerate():
            self.thread.join()
        self.stop_event.clear()

        self.previous_tab = page_id
        if page_id == 0:
            self.load_featured(self.gui.get_object("featured_list"))
        else:
            self.thread = threading.Thread(target=self.add_apps_thread, args=[page_id, page])
            self.thread.daemon = True
            self.thread.start()
        #     for app in self.app_store.get_apps_by_category(tab_category[page_id]):
        #         app.main_category = tab_category[page_id]
        #         page.get_children()[0].get_children()[0].add(ListboxApp(app, self.main_window))
        # page.show_all()

    def add_apps_thread(self, page_id, page):
        for app in self.app_store.get_apps_by_category(tab_category[page_id]):
            if self.stop_event.is_set():
                self.stop_event.clear()
                break

            app.main_category = tab_category[page_id]
            time.sleep(0.001)
            GLib.idle_add(
                self.add_app, page.get_children()[0].get_children()[0], app
            )

    def add_app(self, page, app):
        if not self.stop_event.is_set():
            app_widget = ListboxApp(app, self.main_window)
            if not self.stop_event.is_set():
                page.add(app_widget)
                app_widget.show_all()


def pixbuf_from_url(url):
    try:
        image = requests.get(url)
    except (requests.ConnectionError, requests.HTTPError, requests.RequestException) as error:
        return False

    try:
        return GdkPixbuf.Pixbuf.new_from_stream(
            Gio.MemoryInputStream.new_from_data(image.content, None)
        )
    except GLib.GError:
        return False


class Search(Gtk.ListBox):
    def __init__(self, app_store, main_window):
        Gtk.ListBox.__init__(self)
        self.app_store = app_store
        self.main_window = main_window
        self.set_valign(Gtk.Align.FILL)
        self.set_vexpand(True)

    def search(self, query):
        self.reset()
        if len(query) > 2:
            for app in self.app_store.get_apps_by_search(query):
                app.main_category = app.categories[0]
                self.add(ListboxApp(app, self.main_window))
        else:
            search_label = Gtk.Label()
            search_label.set_margin_top(10)
            search_label.set_markup("<b>Please enter search query</b>")
            search_label.set_margin_bottom(10)
            self.add(search_label)

        self.show_all()

    def reset(self):
        for child in self.get_children():
            child.destroy()
