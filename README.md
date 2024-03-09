<h1 align="center" style="border-bottom: none">
    <a href="//github.com/avyrion/avaris" target="_blank"><img alt="Avaris" src="etc/avaris.png"></a><br>Avaris Task Engine
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
git clone https://github.com/avyrion/avaris.git
cd avaris

# Install requirements
python -m pip install poetry
poetry install
python -m avaris start --config config/conf.yml --scraper-dir ./scrapers
```

## Getting Started

To run Avaris, you'll need to specify your engine configuration and scraper directory. Here's a quick guide to get you started.

### Configuration Files

Avaris requires two main types of configuration files:

- **Engine Configuration (`config/conf.yml`):** Defines global settings for the Avaris avaris.engine.
- **Scraper Configurations (`./scrapers`):** Each scraper should have its own configuration file in this directory, detailing tasks, endpoints, and data management settings.

### Running Avaris

```bash
python -m avaris start --config config/conf.yml --scraper-dir ./scrapers
```

Replace `config/conf.yml` and `./scrapers` with the paths to your actual engine configuration file and scraper configuration directory, respectively.

## Examples

Here are some examples of how to use Avaris for different tasks.

### Defining a Scraper Configuration

```yaml
# scraper_config.yml
scraper:
  - name: PrometheusVersionScraper
    destination: local
    tasks:
      - name: FetchLatestPrometheusVersion
        schedule: "* * * * *"
        executor:
          task: http_get_github_release
          parameters:
            api_url: "https://api.github.com/repos/prometheus/prometheus/releases/latest"

  - name: FluentBitVersionScraper
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
# my_avaris.executor.py
from avaris.executor.executor import TaskExecutor
from pydantic import BaseModel
from avaris.task.task_registry import register_task_executor
class MyExecutorParameters(BaseModel):
    __NAME__ = 'my_exec_identifier'
    # Define parameters here

@register_task_executor(MyExecutorParameters.__NAME__)
class MyExecutor(TaskExecutor[MyExecutorParameters]):
    PARAMETER_TYPE=MyExecutorParameters
    async def execute(self) -> dict:
        # Implementation of your task
        try:
            return {}
        except Exception as e:
            self.logger.error(f"An error occurred while executing task: {e}")
            return {"error":str(e)}
```

Custom tasks under .src/plugins/executor/your_executor.py are automatically loaded.

## How To Contribute

Contributions to Avaris are welcome.
Please refer to the CONTRIBUTING.md file for guidelines on how to make contributions.

## License

Avaris is released under the Apache 2.0 License. See the LICENSE file for more details.
