import math
import random
import string
from collections import defaultdict

import numpy.random

from graph_diff.nirvana_object_model.block import Block
from graph_diff.nirvana_object_model.operation import Operation
from graph_diff.nirvana_object_model.workflow import Workflow
from graph_diff.nirvana_object_model.workflow_generator import WorkflowGenerator


class StandardWorkflowGenerator(WorkflowGenerator):
    LENGTH_OF_STRINGS = 10

    def set_blocks(self, blocks):
        if self.types_of_block is not None:
            raise Exception("Setting blocks twice.")
        self.types_of_block = tuple(blocks)

        return self

    def generate_blocks(self,
                        min_block_num=8,
                        max_block_num=12,
                        min_input_output_number=0,
                        max_input_output_number=3,
                        min_key_value_number=0,
                        max_key_value_number=10):
        if self.types_of_block is not None:
            raise Exception("Setting blocks twice.")

        # Expectation is equal to self.node_number_expectation
        block_number = random.randint(min_block_num, max_block_num)

        a_type_number = 1
        # Mode for number of types is 20% of numbers of the nodes.
        mode_type_number = math.ceil((block_number - 1) / 5)
        b_type_number = block_number

        types_of_block_number = int(math.ceil(numpy.random.triangular(
            left=a_type_number,
            mode=mode_type_number,
            right=b_type_number
        )))

        generate_new_string = lambda : \
            ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for _ in range(StandardWorkflowGenerator.LENGTH_OF_STRINGS))

        self.types_of_block = []
        for _ in range(0, types_of_block_number):
            operation_id = generate_new_string()
            input_number = numpy.random.randint(
                max_input_output_number - min_input_output_number) + min_input_output_number
            output_number = numpy.random.randint(
                max_input_output_number - min_input_output_number) + min_input_output_number
            inputs = sorted([generate_new_string() for _
                             in range(0, input_number)])
            outputs = sorted([generate_new_string() for _
                              in range(0, output_number)])

            key_value = numpy.random.randint(
                max_key_value_number - min_key_value_number) + min_key_value_number
            key_values = {generate_new_string():
                          generate_new_string()
                          for _ in range(0, key_value)}
            self.types_of_block.append(Block(
                operation=Operation(
                    operation_id=operation_id,
                    inputs=inputs,
                    outputs=outputs),
                options=key_values
            ))

        return self


    def __init__(self):
        self.types_of_block = None

    def generate_workflow(self):
        if self.types_of_block is None:
            raise Exception("Blocks not set yet! Set them explicitly or generate them by generate_blocks method.")

        workflow = Workflow()

        block_types = numpy.random.multinomial(n=int(len(self.types_of_block) * 0.7),
                                               pvals=[1 / len(self.types_of_block)] * len(self.types_of_block))

        block_types = sum([
            [i] * value for i, value in enumerate(block_types)
        ], [])
        random.shuffle(block_types)

        for i in block_types:
            block_number = workflow.add_block(self.types_of_block[i])
            previous_block_numbers = defaultdict(int)
            for prev_block in workflow:
                previous_block_numbers[prev_block] += 1
                if 1 == numpy.random.randint(2) and self.types_of_block[i] is not prev_block:
                    workflow.add_connection_by_execution(
                        from_block=prev_block,
                        from_number=previous_block_numbers[prev_block],
                        to_block=self.types_of_block[i],
                        to_number=block_number
                    )
                if 1 == numpy.random.randint(2) \
                        and self.types_of_block[i] is not prev_block \
                        and len(self.types_of_block[i].operation.inputs) > 0 \
                        and len(prev_block.operation.outputs) > 0:
                    input_nest = random.choice(self.types_of_block[i].operation.inputs)
                    output_nest = random.choice(prev_block.operation.outputs)
                    workflow.add_connection_by_data(
                        from_block=prev_block,
                        from_number=previous_block_numbers[prev_block],
                        output_nest=output_nest,
                        to_block=self.types_of_block[i],
                        to_number=block_number,
                        input_nest=input_nest
                    )

        return workflow
