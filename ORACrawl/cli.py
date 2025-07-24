import sys
import json
import csv
import questionary
import io
from rich.console import Console
from rich.table import Table


class CLI:
    def __init__(self, output_type):
        self.console = Console()
        self.output_type = output_type

    def start_status(self, text):
        status = self.console.status(text)
        status.start()

        return status

    def stop_status(self, status):
        if status != None:
            status.stop()

    def good_message(self, message):
        self.console.print(message, style="green")

    def bad_message(self, message):
        self.console.print(message, style="red")

    def message(self, message, color):
        self.console.print(message, style=color)

    def try_print_other_format(self, rows):
        choices = ["json", "csv", "Don't display in a different format"]

        format = questionary.select(
            "Would you link to display the results in a different format?",
            choices=choices,
        ).ask()

        if format == "json":
            self.message(json.dumps(rows, indent=4), "white")
        elif format == "csv":
            with io.StringIO() as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)
                    self.message(csvfile.getvalue(), "white")

    def print_available_db_links(self, available_links):
        if(len(available_links) > 0):
            if(self.output_type == "pretty"):
                table = Table(
                    title="These were the identified chains of DB Links:",
                    show_header=False,
                    header_style="#d10606",
                    show_lines=True,
                )
                table.add_column("Chain", overflow="fold")
                for index, link in enumerate(available_links):
                    style = "#f5f0f0" if index % 2 == 0 else "#c98383"
                    chain = ""
                    for db_link in link:
                        chain = (
                            chain
                            + db_link["DB_LINK"]
                            + "[bold magenta]:[/bold magenta]"
                            + db_link["USERNAME"]
                            + " :right_arrow:  "
                        )
                    table.add_row(chain[:-16], style=style)
                self.console.print(table)
            elif(self.output_type == "json"):
                self.message(json.dumps(available_links, indent=4), "white")
            elif(self.output_type == "csv"):
                for index, chain in enumerate(available_links):
                    self.message(f"\nChain {index}:\n\n", "medium_spring_green")
                    with io.StringIO() as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=chain[0].keys())
                        writer.writeheader()
                        writer.writerows(chain)
                        self.message(csvfile.getvalue(), "white")
        else:
            self.message("No DB Links were identified", "gold1")
                


    def choose_db(self, links_array):
        db_links = []
        for links in links_array:
            for link in links:
                if (link["DB_LINK"] + " : " + link["USERNAME"]) not in db_links:
                    db_links.append(link["DB_LINK"] + " : " + link["USERNAME"])

        response = questionary.select(
            "What link do you want to execute SQL operations on?",
            choices=db_links,
        ).ask()

        return response

    def get_query_text(self):
        return questionary.text("SQL >").ask()

    def print_table_results(self, results):
        if(self.output_type == "pretty"):
            if len(results) > 0:
                table = Table(
                    title=None, show_header=True, header_style="#d10606", show_lines=True
                )

            for collumn in results[0].keys():
                if collumn != "RNUM":
                    table.add_column(collumn, overflow="fold")

            for index, row in enumerate(results):
                # Exclude 'RNUM' from the row data
                row_values = [value for key, value in row.items() if key != "RNUM"]
                # Set the style to 'blue' for odd rows and 'light_blue' for even rows
                style = "#f5f0f0" if index % 2 == 0 else "#c98383"
                table.add_row(*row_values, style=style)

            if self.console.size.width / len(table.columns) < 7.5:
                self.bad_message(
                    "Table size was too big. Please increase the size of the console or reduce the number of selected elements on the query."
                )
                self.try_print_other_format(results)
            else:
                self.console.print(table)
        elif(self.output_type == "json"):
            self.message(json.dumps(results, indent=4), "white")
        elif(self.output_type == "csv"):
            with io.StringIO() as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
                self.message(csvfile.getvalue(), "white")
        
