import oracledb

un = 'APIUSER'  # Your Oracle Database username
pw = 'AlexisSanchez1998'  # Your Oracle Database password
cs = '(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.eu-madrid-1.oraclecloud.com))(connect_data=(service_name=gd51c296542b64f_projectdb22023_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))'

with oracledb.connect(user=un, password=pw, dsn=cs) as connection:
    with connection.cursor() as cursor:
        sql = """select sysdate from dual"""
        for r in cursor.execute(sql):
            print(r)
