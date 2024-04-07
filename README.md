# keepsecret.py 

keepsecret.py is a CLI tool or script designed for encrypting and decrypting files.

## Overview

I sometimes need to manage sensitive information with the applications I develop, such as database passwords, API keys, and encryption private keys.

Of course, there are several great tools or services to manage this secret data, such as GCP Secret Manager and HashiCorp Vault. However, these tools don't match my personal project's needs. I want a simpler tool to just encrypt files and commit them to a Git repository.

keepsecret.py was created with this motivation. It simply encrypts and decrypts files without complexity.

```sh
# Encrypt file1.txt and file2.txt
keepsecret.py encrypt -r age1hxn.... -- file1.txt file2.txt

# Decrypt file1.txt and file2.txt
keepsecret.py decrypt -k path/to/private_key_file -- file1.txt.decrypted file2.txt.decrypted
```

It uses [age](https://github.com/FiloSottile/age) for core encryption functionality. `keepsecret.py` is also designed as a wrapper script to make using `age` more convenient.

## Requirements

- Python 3.11 or later
- [age](https://github.com/FiloSottile/age)

## Installation

Simply download the [`keepsecret.py`](https://github.com/kohkimakimoto/keepsecret/raw/main/keepsecret.py) file from the repository and set the file to have executable permissions.

## Usage 

Before using `keepsecret.py`, you need to have both the public and private `age` keys. If you do not already have these keys, you can generate them by running the following command:

```sh
age-keygen 
```

This command will generate a key pair as shown below.

```
# created: 2024-04-07T14:41:45+09:00
# public key: age1d9huzvucvm7hueyz0ck90gkyxuqyzvqepx594nfhzzfv2tk60yysdf2l09
AGE-SECRET-KEY-1VGYZM79EQPV80CRMKTQHFN4GD6X7UMY7KJ8LYTG3S5EVGUXW7T5S9JRS6Z
```

For more details, please see the age's [documentation](https://github.com/FiloSottile/age).

### Encrypt files

You can encrypt files (for example: `file1.txt`, `file2.txt`) with the following command:

```sh
keepsecret.py encrypt -r age1hxn.... -- file1.txt file2.txt
```

This command will generate encrypted files `file1.txt.encrypted`, `file2.txt.encrypted`.
`keepsecret.py` adds a `.encrypted` extension to generate encrypted versions of the files.

#### `-r`, `--recipient` option

You can also use multiple public keys as follows:

```sh
keepsecret.py encrypt -r age1hxn.... -r age1hxn....  -- file1.txt file2.txt
```

#### `-f`, `--force` option

By default, `keepsecret.py` does not overwrite existing files when generating encrypted files. If you want to override this behavior and force file generation, use the `-f` or `--force` option.

```sh
keepsecret.py encrypt -r age1hxn.... -f -- file1.txt file2.txt
```

### Decrypt files

You can decrypt files (for example: `file1.txt.encrypted`, `file2.txt.encrypted`) with the following command:

```sh
keepsecret.py decrypt -- file1.txt.encrypted file2.txt.encrypted
```

This command prompts you to input your private key like the following:

```sh
Input private key content:
```

After inputting the correct private key, `keepsecret.py` will generate decrypted files `file1.txt`, `file2.txt`.
`keepsecret.py` removes a `.encrypted` extension to restore the files to their original form.

#### Use STDIN

You can input the private key via STDIN like the following:

```sh
echo "AGE-SECRET-KEY-1VGYZM79E..." | keepsecret.py decrypt -- file1.txt.encrypted file2.txt.encrypted
```

#### `-k`, `--key` option

You can specify a private key as a file path like the following:

```sh
keepsecret.py decrypt -k /path/to/private_key -- file1.txt.encrypted file2.txt.encrypted
```


#### `-f`, `--force` option

By default, `keepsecret.py` does not overwrite existing files when restoring them to their original form. If you want to override this behavior and force file generation, use the `-f` or `--force` option.

```sh
keepsecret.py decrypt -f -- file1.txt.encrypted file2.txt.encrypted
```

### Use Configuration File

`keepsecret.py` supports defining secret files in a dedicated configuration file. Here is an example:

```toml
# Equivalent to the `-f` or `--force` command line option.
force = true
# Equivalent to the `-r` or `--recipient` command line option.
recipients = [
    "age1hxn....",
]
# Specify files here instead of using command line arguments.
files = [
    "file1.txt",
    "file2.txt",
]
```

If you put the avobe configuration as a file `keepsecret.toml`, you can run the following command to encrypt files:

```sh
keepsecret.py encrypt
```

And you can also decrypt files like the following:

```sh
keepsecret.py decrypt
```


`keepsecret.py` loads the configuration from `keepsecret.toml` file located in the current working directory. You can also specify a different file path by using the `-c` or `--config` option.

### Use Configuration File with Sections

In the configuration file, you can use sections to define multiple settings within a single file. See the following example:

```toml
[development]
force = true
recipients = [
    "age1hxn....",
    "age1hxn....",
]
files = [
    "file1.txt",
    "file2.txt",
]

[production]
force = true
recipients = [
    "age1hxn....",
]
files = [
    "file3.txt",
    "file4.txt",
]
```

As you can see, the sections are useful for storing secrets for various environments. You can encrypt and decrypt the files by specifying the section with the `-s`, `--section` option:

```sh
# Encrypt the files in development environment.
keepsecret.py encrypt -s development

# Decript the files in development environment.
keepsecret.py decrypt -s development
```

## Author

Kohki Makimoto <kohki.makimoto@gmail.com>

## License

The MIT License (MIT)
