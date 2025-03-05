from abc import ABC, abstractmethod


class DBHandler(ABC):
    @abstractmethod
    def get_ids(self, portal: str = None):
        pass

    @abstractmethod
    def add_ids(self, ids: list[str], portal: str):
        pass


class FileHandler(DBHandler):
    ARGENPROP_FILE = "argenprop.txt"
    CABAPROP_FILE = "cabaprop.txt"
    ZONAPROP_FILE = "zonaprop.txt"

    def get_ids(self, portal: str = None):
        ids = list()
        if portal is None:
            for file in [self.ARGENPROP_FILE, self.CABAPROP_FILE, self.ZONAPROP_FILE]:
                with open(file, "r") as f:
                    ids.extend([l.rstrip() for l in f.readlines()])

        else:
            if portal.lower() == "argenprop":
                file_name = self.ARGENPROP_FILE
            elif portal.lower() == "cabaprop":
                file_name = self.CABAPROP_FILE
            elif portal.lower() == "zonaprop":
                file_name = self.ZONAPROP_FILE
            else:
                raise ValueError("Unknown portal")
            with open(file_name, "r") as f:
                ids.extend([l.rstrip() for l in f.readlines()])

        return set(ids)

    def add_ids(self, ids: list[str], portal: str):
        if portal.lower() == "argenprop":
            file_name = self.ARGENPROP_FILE
        elif portal.lower() == "cabaprop":
            file_name = self.CABAPROP_FILE
        elif portal.lower() == "zonaprop":
            file_name = self.ZONAPROP_FILE
        else:
            raise ValueError("Unknown portal")
        id_lines = ["{}\n".format(ad_id) for ad_id in ids]
        with open(file_name, "a+") as f:
            f.writelines(id_lines)
