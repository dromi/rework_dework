from database.db_dude import DBDude

if __name__ == '__main__':
    sql_create_environmental_table = """ CREATE TABLE IF NOT EXISTS environmental (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        pretty_name text NOT NULL,
                                        base_value DOUBLE PRECISION NOT NULL,
                                        increment DOUBLE PRECISION NOT NULL,
                                        retrieval TIMESTAMP NOT NULL
                                    ); """

    sql_create_political_table = """ CREATE TABLE IF NOT EXISTS political (
                                     id integer PRIMARY KEY,
                                     external_id text NOT NULL UNIQUE,
                                     title text NOT NULL,
                                     summary text NOT NULL,
                                     feed text NOT NULL,
                                     published TIMESTAMP NOT NULL
                                 ); """

    sql_create_financial_table = """ CREATE TABLE IF NOT EXISTS financial (
                                     id integer PRIMARY KEY,
                                     symbol text,
                                     company text NOT NULL UNIQUE,
                                     type TEXT NOT NULL,
                                     industry TEXT NOT NULL,
                                     price BIGINT NOT NULL,
                                     currency text NOT NULL,
                                     change BIGINT NOT NULL,
                                     timestamp TIMESTAMP NOT NULL
                                 ); """

    dude = DBDude()
    dude.create_table(sql_create_environmental_table)
    dude.create_table(sql_create_political_table)
    dude.create_table(sql_create_financial_table)
