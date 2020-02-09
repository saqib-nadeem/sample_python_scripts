"""
Usage Example:

cat imesh_sample.txt | python dump_to_json.py -o imesh.json -e imesh_hashes.json
"""

import sys
import json
import argparse
import traceback
from os.path import dirname, abspath

project_folder = dirname(dirname(abspath('.')))
if project_folder not in sys.path:
    sys.path.append(project_folder)

from breaches.lib.data_record import ValidationError


def eprint(*args, **kwargs):  # pylint: disable=w0621
    print(*args, file=sys.stderr, **kwargs)


if '__main__' == __name__:

    parser = argparse.ArgumentParser()

    parser.add_argument("-o", "--output_filename", help="File to write json data info for breaches index")
    parser.add_argument("-e", "--hash_filename",
                        help="File to write json data info for hashes index")

    args = parser.parse_args()

    if args.output_filename is None:
        parser.print_help()
        sys.exit(1)

    package_base = dirname(dirname(dirname(abspath(__file__))))
    if package_base not in sys.path:
        sys.path.insert(0, package_base)

    from breaches.imesh.imesh import ImeshImporter

    importer = ImeshImporter()
    dump_type = 'hashed'

    output_file = open(args.output_filename, "w", encoding='utf8')

    hash_file = None 
    if args.hash_filename:
        hash_file = open(args.hash_filename, "w")

    processed_count = 0
    error_count = 0
    line_num = 1

    for line in sys.stdin:
        try:
            hash_record = {}
            line_num += 1
            record = importer.process_record(line.rstrip(), dump_type, for_import=True)
            if record is None:
                eprint("Skipping: " + line.rstrip())
                continue

            if hash_file and hasattr(record, 'hash') and record.hash is not None: 
                hash_record["hash"] = record.hash
                if hasattr(record, 'password') and record.password is not None:
                    hash_record["password"] = record.password

                if hasattr(record, 'salt') and record.salt is not None:
                    hash_record["salt"] = record.salt
                        
                hash_record["hashtype"] = record.hashtype
                hash_file.write(json.dumps(hash_record) + '\n')

            # Delete any fields that are in the dump's ignore list
            if importer._import_ignore_fields:
                for fname in importer._import_ignore_fields:
                    if hasattr(record, fname):
                        delattr(record, fname)

            processed_count += 1
            output_file.write(record.to_json() + '\n')

            if 0 == processed_count % 100000:
                eprint("Processed %i, Errors: %i" % (processed_count, error_count))

        except ValidationError as vexp:
            error_count += 1
            eprint("ValidationError %r\n while processing line number %i\n %s" %
                   (vexp, line_num, line))

        except Exception as exp:
            error_count += 1
            eprint("Error %r\n while processing line number %i\n %s" %
                   (exp, line_num, line))
            traceback.print_exc(file=sys.stderr)

    print("Processed %i, Errors: %i" % (processed_count, error_count))

    output_file.close()

    if hash_file:
        hash_file.close()
