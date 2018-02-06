import csv
import hashlib
import json


class CsvToDisk:

    def __init__(self, path):
        self._path = path

    def export(self, dest):
        o = open(dest, 'w')
        with open(self._path) as f:
            r = csv.DictReader(f)

            for l in r:
                doc = json.dumps(l, indent=' ')
                checksum = hashlib.md5(doc).hexdigest()[:10]
                o.write(f"BEGIN ******************** {checksum}\n")
                o.write(doc)
                o.write("\n")
                o.write(f"END ******************** {checksum}\n")
        o.close()


if __name__ == '__main__':

    c = CsvToDisk('./test.csv')
    c.export('export')

