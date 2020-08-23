import sqlite3
import datetime


class Database:
    def __init__(self):
        self.conn = None

        try:
            self.conn = sqlite3.connect("conf/database.sqlite3")
        except sqlite3.Error as e:
            print(e)
        finally:
            if self.conn:
                self.conn.close

    def __del__(self):
        self.conn.close()

    def __create_datasets(self):
        c = self.conn.cursor()
        c.execute(
            """
        CREATE TABLE IF NOT EXISTS datasets (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dataset_last_modified TEXT NOT NULL,
            timestamp_created_at TEXT NOT NULL,
            timestamp_updated_at TEXT NOT NULL
        );
        """
        )
        self.conn.commit()

    def __create_distributions(self):
        c = self.conn.cursor()
        c.execute(
            """
        CREATE TABLE IF NOT EXISTS distributions (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            dataset_id NOT NULL,
            title TEXT NOT NULL,
            byteSize INTEGER NOT NULL,
            accessURL TEXT NOT NULL,
            timestamp_created_at TEXT NOT NULL,
            timestamp_updated_at TEXT NOT NULL,
            FOREIGN KEY(dataset_id) REFERENCES datasets(id)
        );
        """
        )

        self.conn.commit()

    def __create_stations(self):
        c = self.conn.cursor()
        c.execute(
            """
        CREATE TABLE IF NOT EXISTS stations (
            id INTEGER NOT NULL PRIMARY KEY,
            name TEXT NOT NULL,
            element_type TEXT NOT NULL,
            x_utm REAL NOT NULL,
            y_utm REAL NOT NULL,
            timestamp_created_at TEXT NOT NULL,
            timestamp_updated_at TEXT NOT NULL
        );
        """
        )

        self.conn.commit()

    def __create_counts(self):
        c = self.conn.cursor()
        c.execute(
            """
        CREATE TABLE IF NOT EXISTS counts (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            type INTEGER NOT NULL,
            station_id INTEGER NOT NULL,
            datetime TEXT NOT NULL,
            intensity TEXT NOT NULL,
            timestamp_created_at TEXT NOT NULL,
            timestamp_updated_at TEXT NOT NULL,
            FOREIGN KEY(station_id) REFERENCES stations(id)
        );
        """
        )

        self.conn.commit()

    def __create_daily_counts(self):
        c = self.conn.cursor()
        c.execute(
            """
        CREATE TABLE IF NOT EXISTS counts (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            type INTEGER NOT NULL,
            station_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            intensity TEXT NOT NULL,
            timestamp_created_at TEXT NOT NULL,
            timestamp_updated_at TEXT NOT NULL,
            FOREIGN KEY(station_id) REFERENCES stations(id)
        );
        """
        )

        self.conn.commit()

    def initialize(self):
        self.__create_datasets()
        self.__create_distributions()
        self.__create_stations()
        self.__create_counts()
        self.__create_daily_counts()

    def get_dataset_by_name(self, name):
        """Given a name, returns a dataset

        Parameters
        ----------
        name : str
         The name oof the dataset to retrieve.

        Returns
        -------
        `list` of `dict`
            ``"id"``
                ID of the dataset
            ``"name"``
                name of the dataset
            ``"last_modified"``
                Last time the dataset was modified by Madrid
            ``"created_at"``
                When the dataset was added to the database
            ``"updated_at"``
                When the dataset was last updated in the database
        """
        c = self.conn.cursor()
        query = "SELECT * FROM datasets where name LIKE ?;"
        c.execute(query, [name])

        results = []

        for idx, result in enumerate(c.fetchall()):
            results.append({})
            results[idx]["id"] = result[0]
            results[idx]["name"] = result[1]
            results[idx]["last_modified"] = result[2]
            results[idx]["created_at"] = result[3]
            results[idx]["updated_at"] = result[4]

        c.close()

        return results

    def add_dataset(self, dataset_name, last_modified):
        """Add a dataset to the dataset tables.

        Parameters
        ----------
        dataset_name : `str`
        last_modified : `DateTime`

        Returns
        -------
        `dict`
            ``"id"``
                ID of the dataset
            ``"name"``
                name of the dataset
            ``"last_modified"``
                Last time the dataset was modified by Madrid
            ``"created_at"``
                When the dataset was added to the database
            ``"updated_at"``
                When the dataset was last updated in the database
        """

        if not dataset_name:
            raise Exception("The name of dataset can't be empty")
        if not isinstance(dataset_name, str):
            raise Exception("The name of Dataset must be a string, but a {} was provided ".format(
                type(dataset_name)))

            if not last_modified:
                raise Exception("last_modified can't be empty")
        if not isinstance(last_modified, datetime.datetime):
            raise Exception(
                "last_modified must be a datetime.datetime, but a {} was provided".format(
                    type(datetime.datetime)
                )
            )

            timestamp = datetime.datetime.now()

        dataset = (dataset_name, last_modified, str(timestamp), str(timestamp))

        c = self.conn.cursor()
        query = """
        INSERT INTO datasets(name, dataset_last_modified,timestamp_created_at,timestamp_updated_at) VALUES(?,?,?,?);
        """
        c.execute(query, dataset)
        self.conn.commit()
        c.close()

        return self.get_dataset_by_name(dataset_name)

    def add_distributions(self, distributions_list, dataset_id):
        """Add a distribution to the distribution tables.

        Parameters
        ----------
        distributions_list : `list` with `dict`
            ``"title"``
                title of the distribution
            ``"byteSize"``
                Size of the file to download of the distribution in bytes
            ``"accessURL"``
                URL where the distribution can be downloaded
        dataset_id : int
            id of the dataset where this distribution belongs

        Returns
        -------
        `list` with `dict`
            ``"id"``
                ID of the distribution
            ``"dataset_id"``
                id of the dataset where this distribution belongs
            ``"title"``
                title of the distribution
            ``"byteSize"``
                Size of the file to download of the distribution in bytes
            ``"accessURL"``
                URL where the distribution can be downloaded
           ``"created_at"``
                When the distribution was added to the database
            ``"updated_at"``
                When the distribution was last updated in the database

        """

        if type(distributions_list) == dict:
            distributions_list = [distributions_list]

        distributions_tuple_list = []
        timestamp = datetime.datetime.now()

        for idx, distribution in enumerate(distributions_list):
            if not dataset_id:
                raise Exception(
                    'dataset_id is empty'
                )
            if not distribution["title"]:
                raise Exception(
                    'title in distribution item {} is empty'.format(idx)
                )

            if not distribution["byteSize"]:
                raise Exception(
                    'byteSize in distribution item {} is empty'.format(idx)
                )

            if not distribution["accessURL"]:
                raise Exception(
                    'accessURL in distribution item {} is empty'.format(idx)
                )

            distribution["byteSize"] = int(distribution["byteSize"])
            distribution["created_at"] = timestamp
            distribution["updated_at"] = timestamp

            distributions_tuple_list.append(
                tuple((
                    int(dataset_id),
                    distribution["title"],
                    distribution["byteSize"],
                    distribution["accessURL"],
                    str(distribution["created_at"]),
                    str(distribution["updated_at"])
                ))
            )

        c = self.conn.cursor()
        query = """
        INSERT INTO distributions(dataset_id, title, byteSize, accessURL, timestamp_created_at, timestamp_updated_at) VALUES(?,?,?,?,?,?);
        """
        c.executemany(query, distributions_tuple_list)
        self.conn.commit()
        c.close()

        return distributions_list

    def get_distributions_by_dataset_name(self, dataset_name):
        """Given a dataset_name, returns all its distributions

        Parameters
        ----------
        dataset_name : str

        Returns
        -------
        `list` with `dict`
            ``"id"``
                ID of the distribution
            ``"dataset_id"``
                id of the dataset where this distribution belongs
            ``"title"``
                title of the distribution
            ``"byteSize"``
                Size of the file to download of the distribution in bytes
            ``"accessURL"``
                URL where the distribution can be downloaded
           ``"created_at"``
                When the distribution was added to the database
            ``"updated_at"``
                When the distribution was last updated in the database
        """
        c = self.conn.cursor()
        query = """
            SELECT dis.*
            FROM distributions as dis
            INNER JOIN datasets as dat
            ON dis.dataset_id = dat.id
            WHERE dat.name LIKE ?;"""
        c.execute(query, [dataset_name])

        distributions = c.fetchall()

        result = []

        if not isinstance(distributions, type(None)):
            for idx, distribution in enumerate(distributions):
                result.append({})
                result[idx]["id"] = distribution[0]
                result[idx]["dataset_id"] = distribution[1]
                result[idx]["title"] = distribution[2]
                result[idx]["byteSize"] = distribution[3]
                result[idx]["accessURL"] = distribution[4]
                result[idx]["created_at"] = distribution[5]
                result[idx]["updated_at"] = distribution[6]
        c.close()

        return result

    def add_stations(self, stations_list):
        """Given a list with stations data, adds them to the database

        Parameters
        ----------
        stations : `list` with `dict` or a `dict`
            ``"id"``
                Station ID
            ``"name"``
                Name of the station
            ``"element_type"``
                Type of station
            ``"x_utm"``
                X UTM coordinate
            ``"y_utm"``
                Y UTM coordinate

        Returns
        -------
        stations : `list` with `dict`
            ``"id"``
                Station ID
            ``"name"``
                Name of the station
            ``"element_type"`
                Type of station
            ``"x_utm"``
                X UTM coordinate
            ``"y_utm"``
                Y UTM coordinate
            ``"created_at"``
                When the station was added to the database
            ``"updated_at"``
                When the station was last updated in the database

        """

        if type(stations_list) == dict:
            stations_list = [stations_list]

        stations_tuple_list = []
        timestamp = datetime.datetime.now()

        for idx, station in enumerate(stations_list):
            if not station["id"]:
                raise Exception(
                    'id in station_list item {} is empty'.format(idx))

            if not station["name"]:
                raise Exception(
                    'name in station_list item {} is empty'.format(idx))
            if not station["element_type"]:
                raise Exception(
                    'element_type in station_list item {} is empty'.format(idx)
                )

            if not station["x_utm"]:
                raise Exception(
                    'x_utm in station_list item {} is empty'.format(idx))
            if not station["y_utm"]:
                raise Exception(
                    'y_utm in station_list item {} is empty'.format(idx))

            station["id"] = int(station["id"])
            station["x_utm"] = float(station["x_utm"])
            station["y_utm"] = float(station["y_utm"])
            station["timestamp_created_at"] = timestamp
            station["timestamp_updated_at"] = timestamp

            stations_tuple_list.append(
                tuple((
                    station["id"],
                    station["name"],
                    station["element_type"],
                    station["x_utm"],
                    station["y_utm"],
                    station["created_at"],
                    station["updated_at"]
                ))
            )

        c = self.conn.cursor()
        query = """
        INSERT INTO stations(id, name, element_type, x_utm, y_utm, timestamp_created_at, timestamp_updated_at) VALUES(?,?,?,?,?,?,?);
        """
        c.executemany(query, stations_tuple_list)
        self.conn.commit()
        c.close()

        return stations_list

    def get_station_by_id(self, id):
        """Given a name, returns a dataset

        Parameters
        ----------
        name : int
            id of the station to retrieve

        Returns
        -------
        `dict`
            ``"id"``
                ID of the station
            ``"name"``
                name of the id
            ``"element_type"``
                Wether the stations ir a urban one or an M-30 one
            ``"x_utm"``
                Coordinate x in UTM system
            ``"y-utm"``
                Coordinate y in UTM system
            ``"created_at"``
                When the station was added to the database
            ``"updated_at"``
                When the station was last updated in the database
        """
        c = self.conn.cursor()
        query = "SELECT * FROM stations where id = ?;"
        c.execute(query, [id])

        station = c.fetchone()

        result = {}
        if type(station) is not type(None):
            result["id"] = station[0]
            result["name"] = station[1]
            result["element_type"] = station[2]
            result["x_utm"] = station[3]
            result["y_utm"] = station[4]
            result["created_at"] = station[5]
            result["updated_at"] = station[6]
        c.close()

        return result

    def add_car_counts(self, car_counts_list):
        """Given a list with car count data, adds them to the database

        Parameters
        ----------
        stations : `list` with `dict` or a `dict`
            ``"station_id"``
                id of the station which has counted the car
            ``"datetime"``
                datetime.datetime with info about the time and date of when
                measure was done
            ``"intensity"``
                Number of cars measured

        Returns
        -------
        stations : `list` with `dict`
            ``"id"``
                id of the count
            ``"type"``
                type of the count (car, bicycle or pedestrian)
            ``"station_id"`
                id of the station which has counted the car
            ``"datetime"``
                datetime.datetime with info about the time and date of when
                measure was done
            ``"intensity"``
                Number of cars measured
            ``"created_at"``
                When the station was added to the database
            ``"updated_at"``
                When the station was last updated in the database

        """

        if type(car_counts_list) == dict:
            car_counts_list = [car_counts_list]

        car_counts_tuple_list = []
        timestamp = datetime.datetime.now()

        for idx, car_count in enumerate(car_counts_list):
            if not car_count["station_id"]:
                raise Exception(
                    'station_id in car_count item {} is empty'.format(idx)
                )

            if not car_count["datetime"]:
                raise Exception(
                    'datetime in car_count item {} is empty'.format(idx)
                )
            if not isinstance(car_count["datetime"], datetime.datetime):
                raise Exception(
                    'datetime in car_count item {} is not an instance of datetime.datetime'.format(
                        idx)
                )

            if not car_count["intensity"]:
                car_count["intensity"] = 0

            car_count["type"] = 1
            car_count["station_id"] = int(car_count["station_id"])
            car_count["datetime"] = str(car_count["datetime"])
            car_count["created_at"] = timestamp
            car_count["updated_at"] = timestamp

            car_counts_tuple_list.append(
                tuple((
                    car_count["type"],
                    car_count["station_id"],
                    car_count["datetime"],
                    car_count["intensity"],
                    car_count["created_at"],
                    car_count["updated_at"]
                ))
            )

        c = self.conn.cursor()
        query = """
        INSERT INTO counts(type, station_id, datetime, intensity, timestamp_created_at, timestamp_updated_at) VALUES(?,?,?,?,?,?);
        """
        c.executemany(query, car_counts_tuple_list)
        self.conn.commit()
        c.close()

        return car_counts_list
