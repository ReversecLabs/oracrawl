from args_parser import ArgParser
from db_utils import DBUtils, build_query
from file_io import FileIO
from datetime import datetime

MISSING_REQUIREMENTS = False

try:
    from db import DB
    from cli import CLI
except:
    MISSING_REQUIREMENTS = True

MISSING_REQUIREMENTS_MESSAGE = """
The tool will only run in builder mode since there are missing requirements. To install them run the following command:

pip install -r requirements.txt
"""


def main():
    args = ArgParser().args
    
    if args.sub_parser == "builder":
        chain = []
        
        if args.link_list:
            chain_split = args.link_list.split("|")
            for split in chain_split:
                chain.append({'DB_LINK': split})
                
        if "select" in args.query.lower():
            print(build_query(chain, args.query, "select"))
        else:
            print(build_query(chain, args.query, "other"))
    elif(MISSING_REQUIREMENTS == False):
        cli = CLI(args.output_type)
        db = DB(args.server, args.port, args.sid, args.user, args.password)
        dbutils = DBUtils(db)
        file = FileIO()
        run_id = datetime.timestamp(datetime.now())

        try:
            db.connect()
            status = cli.start_status("Getting all the DB links...")

            # Get all necessary DB_LINKS
            available_links = dbutils.get_all_db_links()
            cli.stop_status(status)
            cli.print_available_db_links(available_links)

            if args.export == "all" or args.export == "db_links":
                if args.export_format == "json":
                    # Export to JSON
                    file.export_to_json(
                        f"./output/{args.server}/{args.sid}_{args.user}_db-links_{run_id}",
                        available_links,
                    )
                elif args.export_format == "csv":
                    # Export to CSV
                    for index, links in enumerate(available_links):
                        file.export_to_csv(
                            f"./output/{args.server}/{args.sid}_{args.user}_db-chain_{run_id}_{index}",
                            links,
                        )

            if args.sub_parser == "interactive":
                chosen_db = ""
                while chosen_db != None and len(available_links) > 0:
                    # Ask the user to choose a link to execute SQL commands on
                    chosen_db = cli.choose_db(available_links)
                    if chosen_db != None:
                        chain = dbutils.build_chain(available_links, chosen_db)

                        query = ""
                        while query != None and chosen_db != None:
                            query = cli.get_query_text()
                            if query != None:
                                status = cli.start_status("Running SQL command")
                                try:
                                    if "select" in query.lower():
                                        result = dbutils.run_user_query_select(
                                            query, list(chain)
                                        )
                                        cli.print_table_results(result)
                                    else:
                                        result = dbutils.run_user_query_other(
                                            query, list(chain)
                                        )
                                        cli.good_message(result)
                                        # run_user_query_other("COMMIT", list(chain))
                                    if (
                                        (args.export == "all" or args.export == "queries")
                                        and args.export_format != None
                                        and result != None
                                    ):
                                        file.export_results(
                                            chosen_db,
                                            args.export_format,
                                            f"./output/{args.server}/{chosen_db.split(':')[0]}_{chosen_db.split(':')[1]}_queries_{run_id}",
                                            query,
                                            result,
                                        )
                                except Exception as e:
                                    cli.bad_message(e)
                                
                                cli.stop_status(status)
            elif (args.sub_parser == "query"):
                if args.query:
                    status = cli.start_status(f"Running SQL query")
                    chain = []
                    target = args.link if args.link != None else args.sid
                    
                    if args.link:
                        chain = dbutils.build_chain(available_links, args.link)
                    try:
                        if "select" in args.query.lower():
                            cli.message(
                                f"Results for [cyan]{args.query}[/cyan] @ [cyan]{target}[/cyan]:",
                                "bold white",
                            )
                            result = dbutils.run_user_query_select(args.query, list(chain))
                            cli.print_table_results(result)
                        else:
                            cli.message(
                                f"Command execution status for [cyan]{args.query}[/cyan] @ [cyan]{target}[/cyan]:",
                                "bold white",
                            )
                            result = dbutils.run_user_query_other(args.query, list(chain))
                            cli.good_message(result)

                        if (
                            (args.export == "all" or args.export == "queries")
                            and args.export_format != None
                            and result != None
                        ):
                            file.export_results(
                                args.link,
                                args.export_format,
                                f"./output/{args.server}/{args.link.split(':')[0]}_{args.link.split(':')[1]}_queries_{run_id}",
                                args.query,
                                result,
                            )
                    except Exception as e:
                        cli.bad_message(e)
                    finally:
                        cli.stop_status(status)
        except Exception as e:
            cli.bad_message(e)
        finally:
            cli.good_message("Gracefully shutting down")
            if(hasattr(db, 'connection') and db.connection.ping()):
                db.connection.close()
    else:
        print(MISSING_REQUIREMENTS_MESSAGE)
        


if __name__ == "__main__":
    main()
        

# if args.interactive:
#        import questionary
#        from rich.prompt import Prompt
