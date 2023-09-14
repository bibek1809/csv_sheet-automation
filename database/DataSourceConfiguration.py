import glob

from database.JdbcDataSource import JdbcDataSource, JdbcDatabase
from utils.Env import Env

env = Env.instance()


def get_all_jdbc_jars():
    return glob.glob(f"{env.get_or_default('datalayer.libs.path', 'libs')}/*.jar")


def get_jdbc_connection_props(source):
    return {
        "url": env.get_or_default(f"{source}.datasource.url", ""),
        "jclassname": env.get_or_default(f"{source}.datasource.driver.classname", ""),
        "driver_args": {
            "user": env.get_or_default(f"{source}.datasource.user", ""),
            "password": env.get_or_default(f"{source}.datasource.password", ""),
            "ssl": env.get_or_default(f"{source}.datasource.ssl", "true"),
            "useEncryption": env.get_or_default(f"{source}.datasource.userEncryption", "true"),
            "disableCertificateVerification": env.get_or_default(
                f"{source}.datasource.disableCertificateVerification",
                "true")
        },
        "jars": get_all_jdbc_jars(),
        "libs": get_all_jdbc_jars()
    }

jdbc_database = JdbcDatabase(get_jdbc_connection_props('mysql'))
mysql_datasource = JdbcDataSource(jdbc_database)

def check_connection():
    try:
        jdbc_database.get_connection()
        return True
    except:
        return False
        

