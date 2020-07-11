""" Parse a HCL2 file """

import sys
import os
import logging
import re
import hcl2
import jinja2

logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO').upper(),
                    format="[%(asctime)s] %(message)s")

INPUT_TEMPLATE = """\
# {{ title }}

> Update this document to describe what is being deployed.

## Prerequisites

In terms of software you require the below:

> Populate the list below with all required software dependencies.

- [terraform](https://www.terraform.io/)

> Detail any additional dependencies below, such as permissions, access etc.

## Variables

|Variable Name|Description|Type|Default|
|-|-|-|-|
{%- for k, v in variable.items() %}
|{{ k }}|{{ v['description'] }}|{{ v['type'] }}|{% if v['default'] %}`{{ v['default'] }}`{% endif %}|
{%- endfor %}

{%- if output | length > 0 %}

## Outputs

|Output Name|Description|
|-|-|
{%- for k, v in output.items() %}
|{{ k }}|{{ v['description'] }}|
{%- endfor %}

{%- endif %}

# Deployment

1. Set variables for the deployment
    - Terraform has a number of ways to set variables. See [here](https://www.terraform.io/docs/configuration/variables.html#assigning-values-to-root-module-variables) for more information.
2. Log into Azure with `az login` and set your subscription with `az account set --subscription='REPLACE_WITH_SUBSCRIPTION_ID_OR_NAME'`
    - Terraform has a number of ways to authenticate. See [here](https://www.terraform.io/docs/providers/azurerm/guides/azure_cli.html) for more information.
3. Initialise Terraform with `terraform init`
    - By default, state is stored locally. State can be stored in different backends. See [here](https://www.terraform.io/docs/backends/types/index.html) for more information.
4. Set the workspace with `terraform workspace select REPLACE_WITH_WORKSPACE_NAME`
    - If the workspace does not exist, use `terraform workspace new REPLACE_WITH_WORKSPACE_NAME`
5. Generate a plan with `terraform plan -out tf.plan`
6. If the plan passes, apply it with `terraform apply tf.plan`

In the event the deployment needs to be destroyed, you can run `terraform destroy` in place of steps 5 and 6.

# Known Issues

> Remove or fill this section in.

# Post-Deployment

> Remove or update with post-deployment steps that may need performing.

"""

def parse_tf_variable(tf_variable):
    """
    Parses Terraform and transforms a single terraform variable

    >>> var1 = {
    ...   "myVar1": {
    ...     "description": ["this is one variable"],
    ...     "type": ["${string}"],
    ...     "default": ["foo"]
    ...   }
    ... }
    >>> parse_tf_variable(var1)
    {'myVar1': {'description': 'this is one variable', 'type': 'string', 'default': 'foo'}}
    >>> var2 = {
    ...   "myVar2": {
    ...     "description": ["this is another variable"],
    ...     "type": ["${list(string)}"]
    ...   }
    ... }
    >>> parse_tf_variable(var2)
    {'myVar2': {'description': 'this is another variable', 'type': 'list(string)'}}
    >>> var3 = {
    ...   "myVar3": {
    ...     "description": ["this is yet another variable"],
    ...   }
    ... }
    >>> parse_tf_variable(var3)
    {'myVar3': {'description': 'this is yet another variable', 'type': 'any'}}
    """

    out_variable = {}

    variable_name = list(tf_variable.keys()).pop()
    out_variable.setdefault(variable_name, {})

    variable_description = tf_variable[variable_name].get("description", [""]).pop()
    out_variable[variable_name].setdefault("description", variable_description)

    variable_type = tf_variable[variable_name].get("type", [""]).pop()
    variable_type = re.sub("[${}]", "", variable_type)
    if variable_type == "":
        variable_type = "any"
    out_variable[variable_name].setdefault("type", variable_type)

    variable_default = tf_variable[variable_name].get("default")
    if variable_default is not None:
        variable_default = variable_default.pop()
        if isinstance(variable_default, str):
            variable_default = f'"{variable_default}"'
        elif str(variable_default) == "None":
            variable_default = "null"
        elif str(variable_default) in ["True", "False"]:
            variable_default = str(variable_default).lower()
        elif str(variable_default) == "{}":
            variable_default = "{}"
        elif str(variable_default) == "[]":
            variable_default = "[]"

        out_variable[variable_name].setdefault("default", variable_default)

    return out_variable


def parse_tf_output(tf_output):
    """
    Parses Terraform and transforms a single terraform output

    >>> op1 = {
    ...   "myOut1": {}
    ... }
    >>> parse_tf_output(op1)
    {'myOut1': {'description': ''}}
    >>> op2 = {
    ...   "myOut2": {
    ...     "description": ["this outputs something"]
    ...   }
    ... }
    >>> parse_tf_output(op2)
    {'myOut2': {'description': 'this outputs something'}}
    """
    output_name = list(tf_output.keys()).pop()
    output_description = tf_output[output_name].get('description', ['']).pop()

    output_parsed = {
        output_name: {
            'description': output_description
        }
    }

    return output_parsed

def parse_tf_config(tf_dir):
    """
    Parses Terraform configuration files into a more usable format
    """
    out_data = {
        "variable": {},
        "output": {}
    }
    tf_files = [x for x in os.listdir(tf_dir) if os.path.splitext(x)[1] == ".tf"]
    logging.debug("Found files: %r", tf_files)

    if len(tf_files) < 1:
        print("No Terraform configuration files found. Quitting.")
        sys.exit()

    for tf_file in tf_files:
        try:
            f = open(f"{tf_dir}{os.sep}{tf_file}")
            tf_data = hcl2.load(f)

            if tf_data.get('variable'):
                for tf_variable in tf_data['variable']:
                    tf_variable_parsed = parse_tf_variable(tf_variable)
                    out_data['variable'].update(tf_variable_parsed)

            if tf_data.get('output'):
                for tf_output in tf_data['output']:
                    tf_output_parsed = parse_tf_output(tf_output)
                    out_data['output'].update(tf_output_parsed)

            f.close()
        except ValueError as err:
            logging.error("Error in parsing file: '%s': %r", tf_file, err)

    logging.debug("Returning object: %r", out_data)
    return out_data

def generate_template(tf_dir, title):
    """ Generate a template string """

    tf_data = parse_tf_config(tf_dir)
    tpl = jinja2.Template(INPUT_TEMPLATE)
    tpl_rendered = tpl.render(title=title,
                              variable=tf_data.get('variable'),
                              output=tf_data.get('output'))
    return tpl_rendered
