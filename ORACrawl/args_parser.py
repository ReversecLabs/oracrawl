import argparse
import re

class Validator(object):

    def __init__(self, pattern):
        self._pattern = re.compile(pattern)

    def __call__(self, value):
        if not self._pattern.match(value):
            raise argparse.ArgumentTypeError(
                "Argument has to match '{}'".format(self._pattern.pattern))
        return value

class ArgParser:
    def __init__(self):
        dblink_validator = Validator(r"^[^:]+:[^:]+$")

        parser = argparse.ArgumentParser()

        connection_parser = argparse.ArgumentParser(add_help=False)
        connection_parser._optionals.title = "Connection options"
        connection_parser.add_argument("-s", "--server", dest="server", required=True, help="Hostname or IP address of the Oracle server" )
        connection_parser.add_argument("-p", "--port", dest="port", default=1521,required=False, help="Port used by the Oracle server. Default 1521" )
        connection_parser.add_argument('-U', "--username", dest='user', required=True, help='Username of the Oracle DB user')
        connection_parser.add_argument('-P', "--password", dest='password', required=True, default=None, help='Password of the Oracle DB user')
        connection_parser.add_argument('-d', "--sid", dest='sid', required=True, default=None, help='Service descriptior for the Oracle DB')

        export_parser = argparse.ArgumentParser(add_help=False)
        export_parser._optionals.title = "Exporting options"
        export_parser.add_argument('-e', "--export", dest='export', required=False, default="none", help='Select what will be exported by the tool. Default is none', choices=['all', 'db_links', 'queries', 'none'])
        export_parser.add_argument('-ef', "--export-format", dest='export_format', required=False, default="json", help='Export data format', choices=['json', 'csv'])

        display_parser = argparse.ArgumentParser(add_help=False)
        display_parser._optionals.title = "Display output options"
        display_parser.add_argument('-ot', "--output-type", dest='output_type', required=False, default="pretty", help='Select how results should be displayed by the tool. Default is pretty', choices=['pretty', 'json', 'csv'])

        query_parser = argparse.ArgumentParser(add_help=False)
        query_parser._optionals.title = "Query options"
        query_parser.add_argument('-q', "--query", dest='query', required=True, help='The query to be used')

        sub_parsers = parser.add_subparsers(help="Choose a program mode", dest="sub_parser")

        parser_interactive = sub_parsers.add_parser('interactive', parents=[connection_parser, export_parser, display_parser], help="Runs the program in interactive mode providing a shell for SQL commands")

        parser_query = sub_parsers.add_parser('query', parents=[connection_parser, query_parser, export_parser, display_parser], help='Runs the program in single query mode and returns the output of the query')
        parser_query.add_argument('-l', "--link", dest='link', type=dblink_validator, required=False, help='Link where the query will be run. Format is "DB_LINK:USER"')

        parser_builder = sub_parsers.add_parser('builder', parents=[query_parser], help="Outputs a PL/SQL query based on the program inputs. It can be used to build a daisy-chained query to any linked database")
        parser_builder.add_argument('-ll', "--linkList", dest='link_list', required=True, help='Ordered link list, spearated by pipes, to be used by the builder. Format is "DB1_LINK|DB2_LINK"')


        self.args = parser.parse_args()