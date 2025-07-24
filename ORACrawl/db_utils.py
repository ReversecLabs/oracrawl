from plsql_queries import (
    inner_script_select,
    outer_script_select,
    inner_script_other,
    inner_script_other_ddl,
    outer_script_other,
)

def is_dml_statement(query):
    #Based on https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Types-of-SQL-Statements.html
    dml_keywords = ["CALL", "DELETE", "EXPLAIN PLAN", "INSERT", "LOCK TABLE", "MERGE", "SELECT", "UPDATE"]
    query = query.strip().upper()
    return any(query.startswith(keyword) for keyword in dml_keywords)

def build_query(db_links, sqlToExecute, typeOfQuery="select", currentQuery=None, first=True, delimiter="''",):
    inner_script = ""
    outer_script = ""

    if typeOfQuery == "select":
        inner_script = inner_script_select
        outer_script = outer_script_select
    elif typeOfQuery == "dml":
        inner_script = inner_script_other
        outer_script = outer_script_other
    else:
        inner_script = inner_script_other_ddl
        outer_script = outer_script_other

    if currentQuery == None:
        currentQuery = outer_script

    if len(db_links) == 0 and first:
        tempQuery = inner_script
        tempQuery = tempQuery.replace("'", delimiter)
        tempQuery = tempQuery.replace(
            "REPLACE_ME", sqlToExecute.replace("'", delimiter * 2)
        )
        currentQuery = currentQuery.replace("REPLACE_ME", tempQuery)
        currentQuery = currentQuery.replace("@replace_link", "")
        
        return currentQuery
    elif len(db_links) == 0:
        tempQuery = inner_script
        tempQuery = tempQuery.replace("'", delimiter)
        tempQuery = tempQuery.replace(
            "REPLACE_ME", sqlToExecute.replace("'", delimiter * 2)
        )
        currentQuery = currentQuery.replace("REPLACE_ME", tempQuery)

        return currentQuery
    else:
        tempQuery = outer_script
        tempQuery = tempQuery.replace("'", delimiter)
        if len(db_links) == 1 and first:
            currentQuery = currentQuery.replace(
                "@replace_link", "@" + db_links[0]["DB_LINK"]
            )
            tempQuery = tempQuery.replace("@replace_link", "")
        elif first:
            currentQuery = currentQuery.replace(
                "@replace_link", "@" + db_links[0]["DB_LINK"]
            )
            db_links.remove(db_links[0])
            tempQuery = tempQuery.replace(
                "@replace_link", "@" + db_links[0]["DB_LINK"]
            )
        else:
            tempQuery = tempQuery.replace(
                "@replace_link", "@" + db_links[0]["DB_LINK"]
            )
        currentQuery = currentQuery.replace("REPLACE_ME", tempQuery)
        db_links.remove(db_links[0])
        
        return build_query(db_links, sqlToExecute, typeOfQuery, currentQuery, False, delimiter * 2)



class DBUtils:
    def __init__(self, db):
        self.db = db


    def extract_info(self, text, fields=None):
        # Split the text into rows
        rows = text.split("ROW:")

        results = []
        for row in rows[1:]:
            # Split the row into lines
            lines = row.strip().split("\n")
            # Initialize a dictionary to store the information of the current row
            info = {}
            for line in lines:
                # Split the line into key and value
                key, value = line.split(" = ")
                # If fields is None or the key is in fields, add the key-value pair to the dictionary
                if fields is None or key in fields:
                    info[key] = value
            # Add the dictionary to the results list
            results.append(info)

        return results

    all_checked_links = []

    def get_all_db_links(self, db_links_initial=[], output=None, chain_array=[]):
        if output == None:
            query = build_query([], "SELECT * FROM ALL_DB_LINKS", "select")
            output = self.db.execute_query(query, 1, 10)

            return self.get_all_db_links(list(db_links_initial), output, chain_array)

        gotChain = False
        db_links = self.extract_info(output)

        for db_link in db_links:
            gotChain = False
            if db_link not in self.all_checked_links:
                self.all_checked_links.append(db_link)
                temp_db_links = list(db_links_initial)
                temp_db_links.append(db_link)
                query = build_query(
                    list(temp_db_links), "SELECT * FROM ALL_DB_LINKS", "select"
                )
                try:
                    output = self.db.execute_query(query, 1, 10)
                    self.get_all_db_links(list(temp_db_links), output, chain_array)
                except Exception as e:
                    if(db_links_initial not in chain_array):
                        chain_array.append(db_links_initial)
                    #print(e)
            else:
                gotChain = True
        if gotChain:
            chain = ""
            for db_link in db_links_initial:
                chain = (
                    chain + db_link["DB_LINK"] + ":" + db_link["USERNAME"] + "  =>  "
                )
            chain_array.append(db_links_initial)
        elif len(chain_array) > 0:
            return chain_array
        else:
            return []

    def build_chain(self, links_array, chosen_db):
        split_chosen_db = chosen_db.replace(" ", "").split(":")
        for links in links_array:
            chain = []
            for link in links:
                chain.append(link)
                if (
                    link["DB_LINK"] in split_chosen_db
                    and link["USERNAME"] in split_chosen_db
                ):
                    return chain

    def run_user_query_select(self, query_text, chain):
        query = build_query(chain, query_text, "select")
        i = 0
        total_rows = []
        run = True
        while run:
            output = self.db.execute_query(query, i * 10 + 1, i * 10 + 10)
            info = self.extract_info(output)
            if len(info) == 0:
                run = False
            total_rows += info
            i = i + 1

        return total_rows

    def run_user_query_other(self, query_text, chain):
        is_dml = is_dml_statement(query_text)

        if(is_dml):
            query = build_query(chain, query_text, "dml")
        else:
            query = build_query(chain, query_text, "other")
        output = self.db.execute_query(query)
        return output
