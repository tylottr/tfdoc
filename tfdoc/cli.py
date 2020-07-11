""" Generate a templated Terraform README """

import os
import click

from .parse import generate_template
from .templates import DEFAULT_TPL


@click.command()
@click.option("-t",
              "--title",
              default="Terraform",
              help="The title in the generated document")
@click.option("-o",
              "--out-file",
              default=f"{os.getcwd()}/tfdoc_README.md",
              help="The output file name")
@click.argument("tf_dir", default=os.getcwd())
def cli(tf_dir, title, out_file):
    """ Generate a templated Terraform README """

    print(f"Reading Terraform configuration from: {tf_dir}")

    with open(out_file, 'w') as f:
        data = generate_template(tf_dir, DEFAULT_TPL, title)
        f.write(data)

    print(f"Written data to: {out_file}")
