import os
import shutil
from pathlib import Path

from jina.executors import BaseExecutor


def _read_file(filename):
    with open(filename, 'r') as file:
        return file.readlines()


def _extract_executor_files(flows):
    executor_files = []
    for flow_definition in flows.values():
        for line in flow_definition:
            stripped = line.strip()
            if stripped.startswith('uses'):
                executor_file = stripped.split(':', 1)[1].strip()
                executor_files.append(Path(executor_file))
    return executor_files


def _extract_parameters(executor_yml):
    with BaseExecutor.load_config(str(executor_yml)) as executor:
        if hasattr(executor, "DEFAULT_OPTIMIZATION_PARAMETER"):
            default_config = executor.DEFAULT_OPTIMIZATION_PARAMETER
        else:
            default_config = {}
        executor.save_config('bla.yml')
        import sys
        sys.exit()
        return default_config


def print_parameter(discovered_parameters):
    for filename, (
        encoder_name,
        default_parameters,
    ) in discovered_parameters.items():
        print(f'Default .yaml configurations for {filename}:{encoder_name}:')
        print('with:')
        for parameter, value in default_parameters.items():
            print(f'    {parameter}: {value}')


def write_new_flows(flows, executor_renaming, target_directory):
    for flow_file, flow_content in flows.items():
        full_content = ''.join(flow_content)
        for old_executor, new_executor in executor_renaming:
            full_content = full_content.replace(old_executor, new_executor)
            write_to(flow_file, full_content, target_directory)


def replace_parameters(executor_yml, default_parameters):
    for parameter in default_parameters:
        if '\nwith:\n' not in executor_yml:
            executor_yml = executor_yml + '\nwith:\n'
        executor_yml = executor_yml.replace(
            '\nwith:\n', f'\nwith:\n  {parameter.parameter_name}: ${parameter.environment_variable}\n'
        )
    return executor_yml


def use_absolute_python_paths(executor_yml):
    py_modules_usages = executor_yml.split('py_modules: ')[1:]
    print(py_modules_usages)
    current_wrkdir = Path(os.getcwd())
    for py_module in py_modules_usages:
        module = py_module.split('\n')[0]
        print(module)
        module_abspath = str(current_wrkdir / Path(module))
        executor_yml = executor_yml.replace(module, module_abspath)
    return executor_yml


def write_new_executors(executor_configurations, target_directory):
    for executor_file, default_parameters in executor_configurations.items():
        full_content = ''.join(_read_file(executor_file))
        # TODO: link old .py files correcty
        content_with_parameter = replace_parameters(full_content, default_parameters)
        final_content = use_absolute_python_paths(content_with_parameter)
        write_to(executor_file, final_content, target_directory)


def write_optimization_parameter(executor_configurations):
    raise NotImplemented()


def write_to(filepath, content, create_backup=True):
    if create_backup:
        shutil.move(filepath, f'{filepath}.backup')
    with open(filepath, 'w', encoding='utf8') as new_file:
        new_file.write(content)


def run_parameter_discovery(flow_files, target_directory):
    flows = {flow_file: _read_file(flow_file) for flow_file in flow_files}
    executor_files = _extract_executor_files(flows)
    executor_configurations = {
        file: _extract_parameters(file) for file in executor_files
    }

    old_to_new_executors = [
        (str(file), str(target_directory / file)) for file in executor_files
    ]
    write_new_flows(flows, old_to_new_executors, target_directory)
    write_new_executors(executor_configurations, target_directory)
    # write_optimization_parameter(executor_configurations)


def config_global_environment():
    os.environ.setdefault('JINA_DATA_DIRECTORY', 'data')
    os.environ.setdefault('JINA_LOG_CONFIG', 'logging.optimizer.yml')


def main():
    config_global_environment()
    parameters = {
        'JINA_PARALLEL': '1',
        'JINA_SHARDS': '1',
        'JINA_OPTIMIZATION_WORKSPACE': f'workspace_discovery',
        'JINA_WORKSPACE': 'workspace_discovery'
    }
    for environment_variable, value in parameters.items():
        os.environ[environment_variable] = str(value)
    run_parameter_discovery(
        flow_files=[Path('flows/index.yml'), Path('flows/evaluate.yml')],
        target_directory=Path(os.environ['JINA_OPTIMIZATION_WORKSPACE']),
    )


if __name__ == '__main__':
    main()
