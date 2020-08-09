""" Provides a default template to render the README with """

DEFAULT_TPL = """\
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

## Deployment

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

## Known Issues

> Remove or fill this section in.

## Post-Deployment

> Remove or update with post-deployment steps that may need performing.

"""
