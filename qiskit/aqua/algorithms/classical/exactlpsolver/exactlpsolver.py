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
"""The Exact LinearProblem algorithm."""

import logging

import numpy as np
from scipy import sparse as scisparse

from qiskit.aqua.algorithms import QuantumAlgorithm
from qiskit.aqua import AquaError, Pluggable

logger = logging.getLogger(__name__)


class ExactLPsolver(QuantumAlgorithm):
    """The Exact LinearProblem algorithm."""

    CONFIGURATION = {
        'name': 'ExactLPsolver',
        'description': 'ExactLinearProblem Algorithm',
        'classical': True,
        'input_schema': {
            '$schema': 'http://json-schema.org/schema#',
            'id': 'ExactEigensolver_schema',
            'type': 'object',
            'properties': {
            },
            'additionalProperties': False
        },
        'problems': ['energy', 'excited_states', 'ising']
    }

    def __init__(self, matrix=None, vector=None):
        """Constructor.

        Args:
            operator: Operator instance
            k: How many eigenvalues are to be computed
            aux_operators: Auxiliary operators to be evaluated at each eigenvalue
        """
        self.validate(locals())
        super().__init__()
        self._matrix = matrix
        self._vector = vector
        self._ret = {}

    @classmethod
    def init_params(cls, params, algo_input):
        """
        Initialize via parameters dictionary and algorithm input instance
        Args:
            params: parameters dictionary
            algo_input: LinearSystemInput instance
        """
        if algo_input is None:
            raise AquaError("LinearSystemInput instance is required.")

        matrix = algo_input.matrix
        vector = algo_input.vector
        if not isinstance(matrix, np.ndarray):
            matrix = np.asarray(matrix)
        if not isinstance(vector, np.ndarray):
            vector = np.asarray(vector)

        if matrix.shape[0] != len(vector):
            raise ValueError("Input vector dimension does not match input "
                             "matrix dimension!")

        return cls(matrix, vector)

    def _solve(self):
        self._ret["eigenvalues"] = np.linalg.eig(self._matrix)[0]
        self._ret["solution"] = list(np.linalg.solve(self._matrix, self._vector))

    def _run(self):
        """
        Run the algorithm to compute up to the requested k number of eigenvalues.
        Returns:
            Dictionary of results
        """
        self._solve()
        return self._ret