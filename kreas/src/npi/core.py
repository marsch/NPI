# coding: utf-8
import json
from copy import copy
import numpy as np

# 程序参数的参数: 最大三个，每个为10位的one-hot
MAX_ARG_NUM = 3
ARG_DEPTH = 10   # 0~9 digit. one-hot.


# program continure, program return?
PG_CONTINUE = 0
PG_RETURN = 1


# 参数a: 三个数，每个数都是10位的one-hot
class IntegerArguments:
    depth = ARG_DEPTH
    max_arg_num = MAX_ARG_NUM
    size_of_arguments = depth * max_arg_num

    def __init__(self, args: list=None, values: np.ndarray=None):
        if values is not None:
            self.values = values.reshape((self.max_arg_num, self.depth))
        else:
            self.values = np.zeros((self.max_arg_num, self.depth), dtype=np.float32)

        if args:
            for i, v in enumerate(args):
                self.update_to(i, v)

    def copy(self):
        obj = IntegerArguments()
        obj.values = np.copy(self.values)
        return obj

    def decode_all(self):
        return [self.decode_at(i) for i in range(len(self.values))]

    def decode_at(self, index: int) -> int:
        return self.values[index].argmax()

    # 第index位参数设置成integer大小(one-hot)
    def update_to(self, index: int, integer: int):
        self.values[index] = 0
        self.values[index, int(np.clip(integer, 0, self.depth-1))] = 1

    def __str__(self):
        return "<IA: %s>" % self.decode_all()



# 程序: 名称、参数、id
class Program:
    output_to_env = False

    def __init__(self, name, *args):
        self.name = name
        self.args = args
        self.program_id = None

    def description_with_args(self, args: IntegerArguments) -> str:
        int_args = args.decode_all()
        return "%s(%s)" % (self.name, ", ".join([str(x) for x in int_args]))

    def to_one_hot(self, size, dtype=np.float):
        ret = np.zeros((size,), dtype=dtype)
        ret[self.program_id] = 1
        return ret

    def do(self, env, args: IntegerArguments):
        raise NotImplementedError()

    def __str__(self):
        return "<Program: name=%s>" % self.name



# 输入: 环境、程序、参数
class StepInput:
    def __init__(self, env: np.ndarray, program: Program, arguments: IntegerArguments):
        self.env = env
        self.program = program
        self.arguments = arguments



# 输出: 结束概率、程序、参数
class StepOutput:
    def __init__(self, r: float, program: Program=None, arguments: IntegerArguments=None):
        self.r = r
        self.program = program
        self.arguments = arguments

    def __str__(self):
        return "<StepOutput: r=%s pg=%s arg=%s>" % (self.r, self.program, self.arguments)



# 结合输入输出
class StepInOut:
    def __init__(self, input: StepInput, output: StepOutput):
        self.input = input
        self.output = output



# 结果日志
class ResultLogger:
    def __init__(self, filename):
        self.filename = filename

    def write(self, obj):
        with open(self.filename, "a") as f:
            json.dump(obj, f)
            f.write("\n")



# NPI步
class NPIStep:
    def reset(self):
        pass

    def enter_function(self):
        pass

    def exit_function(self):
        pass

    def step(self, env_observation: np.ndarray, pg: Program, arguments: IntegerArguments) -> StepOutput:
        raise NotImplementedError()


# 运行时系统
class RuntimeSystem:
    def __init__(self, terminal=None):
        self.terminal = terminal

    def logging(self, message):
        if self.terminal:
            self.terminal.add_log(message)
        else:
            print(message)


def to_one_hot_array(idx, size, dtype=np.int8):
    ret = np.zeros((size, ), dtype=dtype)
    ret[idx] = 1
    return ret
