import os
import json
import csv


class FileIO:
    queries = {}
    query_count = 0

    def safe_open_w(self, path):
        """Open "path" for writing, creating any parent directories as needed."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return open(path, "w")

    def export_to_json(self, file_path, data):
        with self.safe_open_w(f"{file_path}.json") as f:
            f.write(json.dumps(data, indent=4))

    def export_to_csv(self, file_path, data):
        with self.safe_open_w(f"{file_path}.csv") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

    def export_results(self, link, export_type, file_path, query, data):
        if export_type == "json":
            if link not in self.queries:
                self.queries[link] = []
            
            row = {"query": query, "result": data}
            self.queries[link].append(row)
            self.export_to_json(file_path, self.queries[link])

        elif export_type == "csv":
            new_data = []

            if type(data) == str:
                data = [{"RESULT": data}]

            for row in data:
                temp_row = {"QUERY": query}
                temp_row.update(row)
                new_data.append(temp_row)

            self.export_to_csv(f"{file_path}_{self.query_count}", new_data)
            self.query_count += 1
