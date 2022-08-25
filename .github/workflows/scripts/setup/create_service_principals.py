#!/usr/bin/env python
# This script creates a service principal in the staging and prod workspaces with appropriate permissions,
# writing output to the specified json file
import subprocess
import sys
import json
import pathlib


def run_cmd(cmd, **kwargs):
    current_script_dir = pathlib.Path(__file__).parent.resolve()
    return subprocess.run(
        cmd,
        check=True,
        cwd=current_script_dir,
        **kwargs
    )


def write_formatted_terraform_output(tf_output, destination_file):
    """
    Given a string containing JSON terraform output, i.e. a dict of string -> dict("value" -> string, "type" -> string,
    "sensitive" -> bool), extracts the "value" field from the dictionary and writes terraform JSON output
    to a destination file
    """
    tf_output_dict = json.loads(tf_output)
    secrets_dict = {
        key: tf_output_dict[key]["value"] for key in tf_output_dict
    }
    with open(destination_file, 'w') as output_filename_handle:
        output_filename_handle.write(f"{json.dumps(secrets_dict, indent=2, sort_keys=True)}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise RuntimeError("Usage: 'create_service_principals.py secret-file-path [arg1] [arg2] ...'. Additional "
                               "arguments after secret-file-path will be passed along to the `terraform apply` "
                               "command used to provision service principals.")
    run_cmd(["terraform", "init"])
    run_cmd(["terraform", "apply"] + sys.argv[2:])
    process = run_cmd(["terraform", "output", "-json"], capture_output=True)
    write_formatted_terraform_output(process.stdout, sys.argv[1])
