import json

from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template

# Summary:
# This Python script reads a Jinja2 template from a file named "workbook.template.json",
# renders it with a context containing key-value pairs,
# and then writes the resulting JSON data to a file named "workbook.json".
# This "workbook.json" can be used as content to deploy an azure workbook.


# Define the template and output file names
template_file_name: str = "workbook.template.json"
output_file_name: str = "workbook.json"

# Set up the Jinja2 environment
loader: FileSystemLoader = FileSystemLoader("..")
env: Environment = Environment(loader=loader, undefined=StrictUndefined)
template: Template = env.get_template(template_file_name)

# Define the context for rendering
context = {
    "title": "Container Apps Jobs",
    "log_analytics_workspace_system_logs": "/subscriptions/a6feefeb-7f6b-425b-8311-b42ebeaee0d1/resourceGroups/johannes-sandbox/providers/Microsoft.OperationalInsights/workspaces/joh-log-analytics-workspace",
    "log_analytics_workspace_console_logs": "/subscriptions/a6feefeb-7f6b-425b-8311-b42ebeaee0d1/resourceGroups/johannes-sandbox/providers/Microsoft.OperationalInsights/workspaces/joh-log-analytics-workspace",
}

# Render the template and load the result as a JSON dictionary
rendered_str: str = template.render(context)
rendered_json: dict = json.loads(rendered_str)

# Write the rendered JSON data to the output file
with open(output_file_name, "w") as outfile:
    json.dump(rendered_json, outfile, indent=4)
