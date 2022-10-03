#  Drakkar-Software OctoBot-Trading
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
import octobot_commons.singleton as singleton
import octobot_commons.databases.implementations.meta_database as meta_database
import octobot_commons.errors as errors
import octobot_commons.logging as logging


class RunDatabasesProvider(singleton.Singleton):
    def __init__(self):
        self.logger = logging.get_logger(self.__class__.__name__)
        self.run_databases = {}

    async def add_bot_id(
        self, bot_id, run_database_identifier, with_lock=False, cache_size=None
    ):
        """
        Initialize the given run_database_identifier and create a new MetaDatabase associated to the given bot_id
        """
        await run_database_identifier.initialize()
        self.run_databases[bot_id] = meta_database.MetaDatabase(
            run_database_identifier, with_lock=with_lock, cache_size=cache_size
        )

    def has_bot_id(self, bot_id):
        """
        :return: True if the given bot_id has been added via add_bot_id
        """
        return bot_id in self.run_databases

    def get_run_databases_identifier(self, bot_id):
        """
        :return: the bot_id associated run_dbs_identifier
        """
        return self.run_databases[bot_id].run_dbs_identifier

    def get_run_db(self, bot_id):
        """
        :return: the bot_id associated run database
        """
        return self.run_databases[bot_id].get_run_db()

    def get_orders_db(self, bot_id, exchange=None):
        """
        :return: the bot_id and exchange associated orders database.
        Use local run_database_identifier.context for exchange if not provided.
        """
        return self.run_databases[bot_id].get_orders_db(exchange=exchange)

    def get_trades_db(self, bot_id, exchange=None):
        """
        :return: the bot_id and exchange associated trades database.
        Use local run_database_identifier.context for exchange if not provided.
        """
        return self.run_databases[bot_id].get_trades_db(exchange=exchange)

    def get_transactions_db(self, bot_id, exchange=None):
        """
        :return: the bot_id and exchange associated transactions database.
        Use local run_database_identifier.context for exchange if not provided.
        """
        return self.run_databases[bot_id].get_transactions_db(exchange=exchange)

    def get_backtesting_metadata_db(self, bot_id):
        """
        :return: the bot_id and exchange associated backtesting metadata database.
        """
        return self.run_databases[bot_id].get_backtesting_metadata_db()

    def get_symbol_db(self, bot_id, exchange, symbol):
        """
        :return: the bot_id and exchange associated transactions database.
        Use local run_database_identifier.context for exchange if exchange is None.
        """
        if not symbol:
            raise errors.DatabaseNotFoundError("symbol parameter has to be provided")
        return self.run_databases[bot_id].get_symbol_db(exchange, symbol)

    def get_historical_portfolio_value_db(self, bot_id, exchange, portfolio_suffix):
        """
        :return: the bot_id, exchange and portfolio_suffix associated transactions database.
        """
        return self.run_databases[bot_id].get_historical_portfolio_value_db(exchange, portfolio_suffix)

    async def close(self, bot_id):
        """
        Close the bot_id associated databases. Does not pop bot_id from self.run_databases to allow post-close calls.
        """
        self.logger.debug(f"Closing bot storage for bot_id: {bot_id} ...")
        await self.run_databases[bot_id].close()
        # do not pop bot_id to keep run data access
        self.logger.debug(f"Closed bot storage for bot_id: {bot_id}")
