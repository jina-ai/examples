import inspect
import ruamel.yaml

from jina.helper import yaml


class OptimizationParameter():

    def __init__(self, parameter_name: str, executor_name: str = None, prefix: str = 'JINA', env_var: str = None):
        if env_var is None:
            self.env_var = f'{prefix}_{executor_name}_{parameter_name}'.upper()
        else:
            self.env_var = env_var
        self.parameter_name = parameter_name

    @classmethod
    def to_yaml(cls, representer, data):
        """Required by :mod:`ruamel.yaml.constructor` """
        tmp = data._dump_instance_to_yaml(data)
        representer.sort_base_mapping_type_on_output = False
        return representer.represent_mapping('!' + cls.__name__, tmp)

    @staticmethod
    def _dump_instance_to_yaml(instance):

        attributes = inspect.getmembers(instance, lambda a: not(inspect.isroutine(a)))
        return {a[0]: a[1] for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))}

    @classmethod
    def from_yaml(cls, constructor, node):
        """Required by :mod:`ruamel.yaml.constructor` """
        return cls._get_instance_from_yaml(constructor, node)

    @classmethod
    def _get_instance_from_yaml(cls, constructor, node):
        data = ruamel.yaml.constructor.SafeConstructor.construct_mapping(
            constructor, node, deep=True)
        return cls(**data)


class IntegerParameter(OptimizationParameter):

    def __init__(self, low, high, step_size, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.low = low
        self.high = high
        self.step_size = step_size

    def to_optuna_args(self):
        return {
            'name': self.environment_variable,
            'low': self.low,
            'high': self.high,
            'step': self.step_size
        }


yaml.register_class(IntegerParameter)


class CategoricalParameter(OptimizationParameter):

    def __init__(self, low, high, step_size, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.low = low
        self.high = high
        self.step_size = step_size


def load_optimization_parameters(filename):
    yaml.register_class(IntegerParameter)
    with open(filename, encoding='utf8') as fp:
        return yaml.load(fp)
