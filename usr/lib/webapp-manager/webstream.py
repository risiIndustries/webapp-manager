import yaml
import requests

class Storage:
    def __init__(self):
        self.apps = []

    def load_from_yaml(ymlfile):
        with open(ymlfile, "r") as file:
            data = yaml.safe_load(file)
        self.apps = self.yaml_data_to_list(data)

    def load_from_url(self, url):
        try:
            r = requests.get(url)
            yaml.safe_load(r.content)
            self.apps = self.yaml_data_to_list(yaml.safe_load(r.content))
            return True
        except (requests.ConnectionError, requests.HTTPError, requests.RequestException) as error:
            return error

    def yaml_data_to_list(self, data):
        output = []
        for item in data.keys():
            output.append(WebApp(
                item,
                data[item]["name"],
                data[item]["url"],
                data[item]["description"],
                data[item]["category"],
                data[item]["price"],
                data[item]["tags"]
            ))
        return output

    def get_app_by_id(self, id):
        for app in self.apps:
            if app.id == id:
                return app
        return False

    def get_apps_by_category(self, category):
        apps = []
        for app in self.apps:
            if app.category == category:
                apps.append(app)
        return apps

    def get_apps_by_search(self, search_term):
        terms = search_term.split()
        apps = []
        matched_name = []
        matched_description = []
        matched_url = []

        for term in terms:
            for app in self.apps:
                if term in app.name:
                    matched_name.append(app)
                if term in app.comment:
                    matched_comment.append(app)
                if term in app.description:
                    matched_description.append(app)

        apps = matched_name
        for app in matched_description:
            if app not in apps:
                apps.append(app)
        for app in matched_url:
            if app not in apps:
                apps.append(app)

        return apps

    def add_app(self,  app):
        if not app_id_exists(app.id):
            self.apps.append(app)

    def app_id_exists(self, id):
        for app in self.apps:
            if app.id == id:
                return True
        return False

class WebApp:
    def __init__(self, appid, name, url, description, category, price, tags):
        self.appid = appid
        self.name = name
        self.url = url
        self.description = description
        self.category = category
        self.price = price
        self.tags = tags
