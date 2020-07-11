# tfdoc

Generate a templated Terraform README by reading a Terraform configuration directory and injecting outputs and variables into a file

## Installation

Install using `pip`:

```
$ pip install tfdoc
```

## Usage

`tfdoc` without any arguments scans the current directory for any `.tf` files and creates a markdown file named "tfdoc_README.md".

This file is populated with a few TODO notes and all variables and outputs formatted into a neat table layout with the description, type and default pulled from your configuration.

## Development

This project uses Python 3.7 and [`pipenv`][1]. To set up your development environment:

```
$ pipenv install --dev
```

And to activate the virtualenv:

```
$ pipenv shell
```

[1]: https://docs.pipenv.org/en/latest/