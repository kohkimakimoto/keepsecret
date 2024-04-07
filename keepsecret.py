#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import getpass
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import textwrap
import tomllib

version = "0.1.0"


no_color = False


def _color(code):
    def inner(text):
        if no_color:
            return text
        return "\033[%sm%s\033[0m" % (code, text)

    return inner


bold = _color("1")
dim = _color("2")
italic = _color("3")
underline = _color("4")
blinking = _color("5")
red = _color("31")
green = _color("32")
yellow = _color("33")
blue = _color("34")
magenta = _color("35")
cyan = _color("36")
white = _color("37")


def print_error(s):
    print(s, file=sys.stderr)


def abort(s: str = None):
    if s is not None:
        print_error(s)
    sys.exit(1)


def check_requirements():
    # check age command
    if shutil.which("age") is None:
        print_error("keepsecret.py needs 'age' command but it does not exist in your system.")
        if platform.system() == "Darwin":
            print_error("You can install age by using homebrew like the following:")
            print_error("$ brew install age")
        print_error("see also: https://github.com/FiloSottile/age#installation")
        abort()


def resolve_config_path(config_path):
    if config_path is None:
        config_path = os.path.join(os.getcwd(), 'keepsecret.toml')
    return config_path


def load_config(config_path, section=None):
    result = {}
    with open(config_path, 'rb') as f:
        config = tomllib.load(f)
        if section and section in config:
            # if the section is specified, pick up the section
            config = config[section]

        result["recipients"] = config.get("recipients", [])
        result["files"]  = config.get("files", [])
        result["force"]  = config.get("force", False)
    return result

def encrypt_command(args):
    check_requirements()

    recipients = []
    files = []
    force = False

    if len(args.file) == 0:
        # use config file
        config_path = resolve_config_path(args.config)
        if not os.path.exists(config_path):
            abort("Config file not found: " + config_path)
        config = load_config(config_path, args.section)
        recipients = config["recipients"]
        files = config["files"]
        force = config["force"]
        # move to the directory where the config file exists
        os.chdir(os.path.dirname(config_path))
    else:
        # use command line arguments
        recipients = args.recipient
        files = args.file

    if args.force:
        # the force can be always enabled by the command line option
        force = True

    if len(recipients) == 0:
        abort("No recipients specified")
    if len(files) == 0:
        abort("No files specified")

    try:
        for file in files:
            if not os.path.exists(file):
                abort("File not found: " + file)

            if not os.path.isfile(file):
                abort("Not a file: " + file)

            encrypted_file = file + ".encrypted"
            if os.path.exists(encrypted_file):
                if not force:
                    abort("File already exists: " + encrypted_file)

            age_flags = ["--encrypt", "--armor"]
            for recipient in recipients:
                age_flags.append("-r")
                age_flags.append(recipient)
            age_flags.append("-o")
            age_flags.append(encrypted_file)
            age_command = "age %s %s" % (" ".join(age_flags), file)
            # print(age_command)
            subprocess.run(age_command, shell=True, check=True)
            print(green("Encrypted: ") + file + " -> " + encrypted_file)
    except subprocess.CalledProcessError as e:
        print_error(e)


def decrypt_command(args):
    check_requirements()

    private_keys = []
    files = []
    force = False

    if len(args.file) == 0:
        # use config file
        config_path = resolve_config_path(args.config)
        if not os.path.exists(config_path):
            abort("Config file not found: " + config_path)
        config = load_config(config_path, args.section)
        raw_files = config["files"]
        for raw_file in raw_files:
            files.append(raw_file + ".encrypted")
        force = config["force"]
        # move to the directory where the config file exists
        os.chdir(os.path.dirname(config_path))
    else:
        files = args.file

    if args.force:
        # the force can be always enabled by the command line option
        force = True

    if len(files) == 0:
        abort("No files specified")

    tmp_dir = None
    try:
        if args.key is None or len(args.key) == 0:
            if sys.stdin.isatty():
                # try to get private key from interactive input
                key = getpass.getpass(prompt="Input private key content: ")
            else:
                # read private key from stdin
                key = sys.stdin.read()
            
            # the key is written into a temporary file.
            tmp_dir = tempfile.TemporaryDirectory(prefix="keepsecret_")
            tmp_key_file = os.path.join(tmp_dir.name, 'key.txt')
            with open(tmp_key_file, 'w') as f:
                f.write(key)
            private_keys.append(tmp_key_file)
        else:
            # read private key from files that are specified by -k option
            private_keys.extend(args.key)

        for file in files:
            if not os.path.exists(file):
                abort("File not found: " + file)

            if not os.path.isfile(file):
                abort("Not a file: " + file)

            if not file.endswith(".encrypted"):
                abort("Not an encrypted file: " + file)

            # remove .encrypted extension
            raw_file = file[:-len(".encrypted")]
            if os.path.exists(raw_file):
                if not force:
                    abort("File already exists: " + raw_file)

            age_flags = ["--decrypt"]
            for private_key in private_keys:
                age_flags.append("-i")
                age_flags.append(private_key)
            age_flags.append("-o")
            age_flags.append(raw_file)

            age_command = "age %s %s" % (" ".join(age_flags), file)
            # debug print
            # print(age_command)
            subprocess.run(age_command, shell=True, check=True)
            print(green("Decrypted: ") + file + " -> " + raw_file)

    except subprocess.CalledProcessError as e:
        print_error(e)
    finally:
        if tmp_dir is not None:
            tmp_dir.cleanup()


def main():
    parser = argparse.ArgumentParser(
        description="keepsecret.py is a CLI tool or script designed for encrypting and decrypting files.\nversion: " + version,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''\
            dependencies:
              %(prog)s requires age encryption tool. see https://github.com/FiloSottile/age

            examples:
              # The following command encrypts files and adds a ".encrypted" extension to create encrypted versions of the files.
              $ %(prog)s encrypt -r age1hxn........ -- /path/to/file1 /path/to/file2 /path/to/file3

              # The following command decrypts files and removes the ".encrypted" extension, restoring the files to their original names.
              $ %(prog)s decrypt -- /path/to/file1.decrypted /path/to/file2.decrypted /path/to/file3.decrypted


            Copyright (c) Kohki Makimoto <kohki.makimoto@gmail.com>
            The MIT License (MIT)
            https://github.com/kohkimakimoto/keepsecret
        '''))
    parser.add_argument("--no-color", dest="no_color", action="store_true", help="Disable color output")

    subparsers = parser.add_subparsers(title="subcommands")

    # encrypt
    parser_encrypt = subparsers.add_parser("encrypt", help="Encrypt files", description="Encrypt files")
    parser_encrypt.add_argument("-c", "--config", help="Path to the config file.")
    parser_encrypt.add_argument("-s", "--section", help="Specify the config section to use. This option is used with -c option.")
    parser_encrypt.add_argument("-r", "--recipient", dest="recipient", metavar="RECIPIENT", nargs='*',
                                help="Encrypt to the specified RECIPIENT (age publick key). Can be repeated.",
                                default=[])
    parser_encrypt.add_argument("-f", "--force", dest="force", action="store_true",
                                help="Encrypt files even if they exist")
    parser_encrypt.add_argument("file", nargs="*", help="File path that you want to encrypt")
    parser_encrypt.set_defaults(func=encrypt_command)

    # decrypt
    parser_decrypt = subparsers.add_parser("decrypt", help="Decrypt files", description="Decrypt files")
    parser_decrypt.add_argument("-c", "--config", help="Path to the config file.")
    parser_decrypt.add_argument("-s", "--section", help="Specify the config section to use. This option is used with -c option.")
    parser_decrypt.add_argument("-k", "--key", dest="key", metavar="PATH", nargs="*",
                                help="Private key file path for decrypting the secret files (age private key). If not specified, it will be read from stdin or interactive input.")
    parser_decrypt.add_argument("-f", "--force", dest="force", action="store_true",
                                help="Decrypt files even if they exist")
    parser_decrypt.add_argument("file", nargs="*", help="File path that you want to decrypt")
    parser_decrypt.set_defaults(func=decrypt_command)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    global no_color
    no_color = args.no_color
    args.func(args)


if __name__ == "__main__":
    main()
