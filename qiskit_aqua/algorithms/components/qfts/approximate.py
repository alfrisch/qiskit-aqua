# -*- coding: utf-8 -*-

# Copyright 2018 IBM.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

from scipy import linalg
import numpy as np

from qiskit import QuantumRegister, QuantumCircuit
from qiskit.qasm import pi

from qiskit_aqua.algorithms.components.qfts import QFT


class Approximate(QFT):
    """An approximate QFT."""

    APPROXIMATE_CONFIGURATION = {
        'name': 'APPROXIMATE',
        'description': 'Approximate inverse QFT',
        'input_schema': {
            '$schema': 'http://json-schema.org/schema#',
            'id': 'aqft_schema',
            'type': 'object',
            'properties': {
                'degree': {
                    'type': 'integer',
                    'default': 0,
                    'minimum':  0
                },
            },
            'additionalProperties': False
        }
    }

    def __init__(self, configuration=None):
        super().__init__(configuration or self.APPROXIMATE_CONFIGURATION.copy())
        self._num_qubits = 0
        self._degree = 0

    def init_args(self, num_qubits, degree=1):
        self._num_qubits = num_qubits
        self._degree = degree

    def construct_circuit(self, mode, register=None, circuit=None):
        if mode == 'vector':
            return linalg.dft(2 ** self._num_qubits, scale='sqrtn')
        elif mode == 'circuit':
            if register is None:
                register = QuantumRegister(self._num_qubits, name='q')
            if circuit is None:
                circuit = QuantumCircuit(register)

            for j in range(self._num_qubits):
                # neighbor_range = range(np.max([0, j - self._degree + 1]), j)
                neighbor_range = range(np.max([0, j - self._num_qubits + self._degree + 1]), j)
                for k in neighbor_range:
                    lam = 1.0 * pi / float(2 ** (j - k))
                    circuit.u1(lam / 2, register[j])
                    circuit.cx(register[j], register[k])
                    circuit.u1(-lam / 2, register[k])
                    circuit.cx(register[j], register[k])
                    circuit.u1(lam / 2, register[k])
                circuit.u2(0, np.pi, register[j])
            return circuit
        else:
            raise ValueError('Mode should be either "vector" or "circuit"')