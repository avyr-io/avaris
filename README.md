<h1 align="center" style="border-bottom: none">
    <a href="//github.com/avyr-io/avaris" target="_blank"><img alt="Avaris" src="etc/avaris.png"></a><br>Avaris Task Engine
</h1>

<div align="center">

</div>

Avaris is a modular task execution and data processing engine designed for easy integration and customization for various task executions, with a strong focus on data management tasks.

## Notable Features

- **Flexible Task Configurations:** Manage and customize your tasks with YAML configuration files.
- **Modular Design:** Easily extend or modify components, supporting dynamic loading of plugins under `.avaris/src`.
- **Asynchronous Support:** Built with async capabilities for efficient I/O operations.
- **Task Scheduling:** Supports different backends, currently only APScheduler.
- **Extensible Executors:** Execute tasks based on predefined or custom logic.
- **Data Management:** Introduces `SQLDataManager` for relational database management, in addition to customizable data managers and handlers for diverse data storage and processing needs.

## Installation

```bash
# Clone the repository
git clone https://github.com/avyr-io/avaris.git
cd avaris

# Install requirements
python -m pip install poetry
poetry install
python -m avaris start --config config/conf.yml --compendium-dir ./compendium
```

## Getting Started

To run Avaris, you'll need to specify your engine configuration and compendium directory. Here's a quick guide to get you started.

### Configuration Files

Avaris requires two main types of configuration files:

- **Engine Configuration (`config/conf.yml`):** Defines global settings for the Avaris avaris.engine.
- **Compendium Configurations (`./compendium`):** Each compendium file should have its own configuration file in this directory, detailing tasks, endpoints, and data management settings.

### Running Avaris

```bash
Usage: avaris start [OPTIONS]

  Start the engine with the specified configuration. You must specify either a
  compendium directory or a compendium file. Optionally, you can specify a
  plugins directory.

Options:
  -p, --plugins-dir PATH      Path to the directory containing plugin modules.
                              Defaults to $PWD/.avaris/plugins
  -f, --compendium-file PATH  Path to a single compendium configuration file.
  -d, --compendium-dir PATH   Path to the directory containing compendium
                              configurations.
  -c, --config PATH           Path to the engine configuration YAML file.
  --help                      Show this message and exit.
```

```bash
python -m avaris start --config config/conf.yml --compendium-dir ./compendium
```

Replace `config/conf.yml` and `./compendium` with the paths to your actual engine configuration file and compendium configuration directory, respectively.

## Examples

Here are some examples of how to use Avaris for different tasks.

### Defining a compendium Configuration

```yaml
# compendium_config.yml
compendium:
  - name: PrometheusVersioncompendium
    destination: local
    tasks:
      - name: FetchLatestPrometheusVersion
        schedule: "* * * * *"
        executor:
          task: http_get_github_release
          parameters:
            api_url: "https://api.github.com/repos/prometheus/prometheus/releases/latest"

  - name: FluentBitVersioncompendium
    destination: local
    tasks:
      - name: FetchLatestFluentBitVersion
        schedule: "* * * * *"
        executor:
          task: http_get_github_release
          parameters:
            api_url: "https://api.github.com/repos/fluent/fluent-bit/releases/latest"
```

### Custom Task Executor

Implementing a custom task executor involves creating a Python class that inherits from `TaskExecutor` and defines the `execute` method.

```python
# ./my_avaris.executor.py
from avaris.executor.executor import TaskExecutor
from avaris.api.models import BaseParameter
from avaris.task.task_registry import register_task_executor

class MyExecutorParameters(BaseParameter):
    __NAME__ = 'my_exec_identifier'
    # Define parameters here

@register_task_executor(MyExecutorParameters)
class MyExecutor(TaskExecutor[MyExecutorParameters]):
    async def execute(self) -> dict:
        # Implementation of your task
        try:
            return {}
        except Exception as e:
            self.logger.error(f"An error occurred while executing task: {e}")
            raise
```
## Passing variables from the environment

For a task parameter set that looks like this
```python
class HTTPGetParameters(BaseParameter):
    __NAME__ = 'http_get'
    url: str
    username: Optional[str] = None
    password: Optional[SecretStr] = None
    response_format: Literal['json', 'text',
                             'binary'] = 'text'
```
You can now instruct Avaris to get the secret from the environment directly like so.
```yaml
compendium:
  name: get request
  tasks:
    - name: get example.com
      schedule: "* * * * *"
      executor:
        task: http_get
        parameters:
          username: ${{ env.USERNAME }}
          password: ${{ env.PASSWORD }}
          url: https://example.com
          response_format: text
```

Another way to specify secrets (legacy method) would be like so:
```python
from avaris.executor.executor import TaskExecutor
from avaris.api.models import BaseParameter
from avaris.task.task_registry import register_task_executor

"""Define your parameter model with its identifier"""
class MyParameters(BaseParameter):
    __NAME__ = 'my_task_identifier_in_yaml'
    my_param: str = ""

@register_task_executor(MyParameters)
class MyTask(TaskExecutor[MyParameters]) :

    async def execute(self) -> dict:
        try:
            self.logger.info("Hello World!")
            # Fetch secrets if any were mentioned explicity from the config. (will also load from env)
            secrets = await self.load_secrets()
            access_parameters_this_way = self.parameters.my_param
            my_secret = secrets.get("MY_SECRET", None)
            return {'my_key': self.parameters.my_param}
        except Exception as e:
            self.logger.error(
                f"Error : {e}")
            return {'error': str(e)}
```
And then in YAML you could instruct Avaris this way:
```yaml
compendium:
  name: latest version jobs
  tasks:
    -  # more tasks...
    - name: Example
      schedule: "* * * * *"
      executor:
        task: my_task_identifier_in_yaml # task identifier
        parameters:
          my_param: "123"
        secrets:
          MY_SECRET: # implicity loading from env
```



# Default Configurations Summary

## Directories

- **Home Directory**: `~/.avaris`
- **Working Directory**: `$WORKINGDIR` or fallback to `~/.avaris` or current working directory
- **Data Directory**: `$DATA` or `~/.avaris/data`
- **Plugins Directory**: `~/.avaris` or `$WORKINGDIR/.avaris`
- **Compendium Directory**: `$COMPENDIUM` or `~/.avaris/compendium` or `$WORKINGDIR/compendium`

## Files

- **Configuration File**: `$CONFIG` or `conf.yaml` in several locations
- **SQLite Database**: `~/.avaris/data/local.db`
- **Log File**: `$LOGS` or `avaris.log` in several locations

## Secrets

- **Listener Key**: `$LISTENER_KEY`

## Default Configuration

- **YAML Configuration**:

```
# defined per src/avaris/defaults.py

execution_backend: apscheduler
data_backend:
  backend: sqlite
  database_url: # empty defaults to local.db
services:
  datasource:
    enabled: true
    port: 5000
```

## How To Contribute

Contributions to Avaris are welcome.
Please refer to the CONTRIBUTING.md file for guidelines on how to make contributions.

## License

Avaris is released under the Apache 2.0 License. See the LICENSE file for more details.
