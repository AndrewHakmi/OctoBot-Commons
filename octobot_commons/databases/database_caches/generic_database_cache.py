#  Drakkar-Software OctoBot-Commons
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
import octobot_commons.errors as errors
import octobot_commons.dict_util as dict_util



class GenericDatabaseCache:
    MAX_CACHE_SIZE = 512

    def __init__(self):
        # used for select / contains methods
        self.rows_cache = {}
        # used for cached_query() (used in upsert)
        self.query_cache = {}
        # used for cached_uuid() (used in upsert)
        self.uuid_cache = {}

    def register(self, table, row, result=None, uuid=None):
        cached = False
        try:
            if uuid is not None:
                cached = True
                try:
                    self.uuid_cache[table][row] = uuid
                except KeyError:
                    self.uuid_cache[table] = {row: uuid}
            elif result is not None:
                cached = True
                try:
                    self.query_cache[table][row] = result
                except KeyError:
                    self.query_cache[table] = {row: result}
        except TypeError as e:
            # might happen when row can't be hashed: impossible to cache it in this case
            raise errors.UncachableValue(f"Unhashable row: {row}") from e
        if not cached:
            self._add_to_rows_cache(table, row)

    def _add_to_rows_cache(self, table, row):
        try:
            if len(self.rows_cache[table]) >= self.MAX_CACHE_SIZE:
                self.rows_cache[table] = self.rows_cache[table][self.MAX_CACHE_SIZE // 2:]
            self.rows_cache[table].append(row)
        except KeyError:
            self.rows_cache[table] = [row]

    def has(self, table):
        return table in self.rows_cache

    def cached_uuid(self, table, identifier):
        try:
            return self.uuid_cache[table][identifier]
        except KeyError:
            return None

    def cached_query(self, table, identifier):
        try:
            return self.query_cache[table][identifier]
        except KeyError:
            return None

    def contains_row(self, table, val_by_keys):
        # Should check the real database in case this returns false
        try:
            for element in self.rows_cache[table]:
                if dict_util.contains_each_element(element, val_by_keys):
                    return True
        except KeyError:
            pass
        return False

    def clear(self):
        self.rows_cache = {}
        self.query_cache = {}
        self.uuid_cache = {}