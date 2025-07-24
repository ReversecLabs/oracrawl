import oracledb


class DB:
    def __init__(self, server, port, sid, user, password):
        self.dsn = oracledb.makedsn(server, port, service_name=sid)
        self.user = user
        self.password = password

    def connect(self):
        self.connection = oracledb.connect(user=self.user, password=self.password, dsn=self.dsn)

    def execute_query(self, plsql, start=None, end=None):
        try:
            # print(plsql)
            cursor = self.connection.cursor()
            output_var = cursor.var(oracledb.STRING, size=32000)
            if start != None and end != None:
                cursor.execute(plsql, output=output_var, start=start, end=end)
            else:
                cursor.execute(plsql, output=output_var)

            self.connection.commit()

            v_output_value = output_var.getvalue()
            return v_output_value
        except oracledb.DatabaseError as e:
            (error,) = e.args
            raise Exception(error.message)
        finally:
            cursor.close()
            # connection.close()
