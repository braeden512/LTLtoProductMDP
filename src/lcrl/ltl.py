import re
import subprocess
import os

from lcrl.automata.ldba import LDBA


class _GuardParser:
    def __init__(self, text):
        self.tokens = self._tokenise(text)
        self.index = 0

    @staticmethod
    def _tokenise(text):
        tokens = []
        i = 0
        while i < len(text):
            char = text[i]
            if char.isspace():
                i += 1
                continue
            if char in ('(', ')', '!', '&', '|'):
                tokens.append(char)
                i += 1
                continue
            if char in ('t', 'f'):
                tokens.append(char)
                i += 1
                continue
            if char.isdigit():
                j = i
                while j < len(text) and text[j].isdigit():
                    j += 1
                tokens.append(int(text[i:j]))
                i = j
                continue
            raise ValueError('Unsupported token in HOA guard expression: ' + char)
        return tokens

    def _peek(self):
        if self.index < len(self.tokens):
            return self.tokens[self.index]
        return None

    def _consume(self):
        token = self._peek()
        self.index += 1
        return token

    def parse(self):
        ast = self._parse_or()
        if self._peek() is not None:
            raise ValueError('Unexpected trailing tokens in HOA guard expression.')
        return ast

    def _parse_or(self):
        node = self._parse_and()
        while self._peek() == '|':
            self._consume()
            node = ('or', node, self._parse_and())
        return node

    def _parse_and(self):
        node = self._parse_not()
        while self._peek() == '&':
            self._consume()
            node = ('and', node, self._parse_not())
        return node

    def _parse_not(self):
        if self._peek() == '!':
            self._consume()
            return ('not', self._parse_not())
        return self._parse_atom()

    def _parse_atom(self):
        token = self._peek()
        if token == '(':
            self._consume()
            node = self._parse_or()
            if self._peek() != ')':
                raise ValueError('Expected closing parenthesis in HOA guard expression.')
            self._consume()
            return node
        if token == 't':
            self._consume()
            return ('true',)
        if token == 'f':
            self._consume()
            return ('false',)
        if isinstance(token, int):
            self._consume()
            return ('ap', token)
        raise ValueError('Malformed HOA guard expression.')


def _eval_guard(ast, true_ap_indices):
    node_type = ast[0]
    if node_type == 'true':
        return True
    if node_type == 'false':
        return False
    if node_type == 'ap':
        return ast[1] in true_ap_indices
    if node_type == 'not':
        return not _eval_guard(ast[1], true_ap_indices)
    if node_type == 'and':
        return _eval_guard(ast[1], true_ap_indices) and _eval_guard(ast[2], true_ap_indices)
    if node_type == 'or':
        return _eval_guard(ast[1], true_ap_indices) or _eval_guard(ast[2], true_ap_indices)
    raise ValueError('Unsupported HOA guard AST node: ' + str(node_type))


def hoa_to_ldba(hoa_text):
    ap_names = []
    initial_state = None
    acceptance_count = None
    state_acceptance_sets = {}
    transitions = {}
    current_state = None

    ap_pattern = re.compile(r'^AP:\s+\d+\s+(.*)$')
    start_pattern = re.compile(r'^Start:\s+(-?\d+)$')
    acceptance_pattern = re.compile(r'^Acceptance:\s+(\d+)\s+.*$')
    state_pattern = re.compile(r'^State:\s+(-?\d+)(?:\s+\{([^}]*)\})?$')
    transition_pattern = re.compile(r'^\[(.+)\]\s+(-?\d+)(?:\s+\{([^}]*)\})?$')

    for raw_line in hoa_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith('HOA:') or line.startswith('tool:') or line.startswith('properties:') \
                or line.startswith('acc-name:') or line == '--BODY--' or line == '--END--':
            continue

        start_match = start_pattern.match(line)
        if start_match:
            initial_state = int(start_match.group(1))
            continue

        acceptance_match = acceptance_pattern.match(line)
        if acceptance_match:
            acceptance_count = int(acceptance_match.group(1))
            continue

        ap_match = ap_pattern.match(line)
        if ap_match:
            ap_names = re.findall(r'"([^"]+)"', ap_match.group(1))
            continue

        state_match = state_pattern.match(line)
        if state_match:
            current_state = int(state_match.group(1))
            transitions[current_state] = []
            acceptance_text = state_match.group(2)
            if acceptance_text is not None and acceptance_text.strip() != '':
                set_indices = [int(item.strip()) for item in acceptance_text.split(',') if item.strip() != '']
                state_acceptance_sets[current_state] = set_indices
            continue

        transition_match = transition_pattern.match(line)
        if transition_match:
            if current_state is None:
                raise ValueError('Malformed HOA: transition found before any state declaration.')
            guard_expression = transition_match.group(1)
            destination_state = int(transition_match.group(2))
            transitions[current_state].append({
                'guard_ast': _GuardParser(guard_expression).parse(),
                'to_state': destination_state
            })
            continue

    if initial_state is None:
        raise ValueError('Malformed HOA: missing initial state.')
    if acceptance_count is None:
        raise ValueError('Malformed HOA: missing acceptance condition.')
    if not ap_names and acceptance_count >= 0:
        ap_names = []

    accepting_sets = [[] for _ in range(acceptance_count)]
    for state, set_indices in state_acceptance_sets.items():
        for set_index in set_indices:
            if set_index < 0 or set_index >= acceptance_count:
                raise ValueError('Malformed HOA: acceptance index out of range.')
            accepting_sets[set_index].append(state)

    if acceptance_count > 0 and all(len(accepting_set) == 0 for accepting_set in accepting_sets):
        raise ValueError(
            'Could not derive state-based accepting sets from HOA. '
            'Please export state-based acceptance (for OWL use: --state-acceptance).'
        )

    automaton = LDBA(initial_automaton_state=initial_state, accepting_sets=accepting_sets)
    automaton.atomic_propositions = ap_names

    def step(self, label):
        if self.automaton_state == -1:
            return -1

        if isinstance(label, str):
            label_values = {label}
        else:
            label_values = set(label)

        true_ap_indices = set()
        for i, proposition in enumerate(self.atomic_propositions):
            if proposition in label_values:
                true_ap_indices.add(i)

        for transition in transitions.get(self.automaton_state, []):
            if _eval_guard(transition['guard_ast'], true_ap_indices):
                self.automaton_state = transition['to_state']
                return self.automaton_state

        self.automaton_state = -1
        return self.automaton_state

    automaton.step = step.__get__(automaton, LDBA)
    return automaton


def ltl_to_ldba(ltl_formula, owl_binary='owl'):
    if owl_binary in (None, ''):
        owl_binary = os.environ.get('LCRL_OWL_BINARY') or os.environ.get('OWL_BINARY') or 'owl'

    try:
        process = subprocess.run(
            [owl_binary, 'ltl2ldba', '--state-acceptance', '-f', ltl_formula],
            capture_output=True,
            text=True,
            check=False
        )
    except FileNotFoundError as error:
        raise RuntimeError(
            'Could not find the OWL executable. Install OWL and make sure `owl` is on PATH, '
            'or pass owl_binary="/path/to/owl" (or set LCRL_OWL_BINARY / OWL_BINARY).'
        ) from error

    if process.returncode != 0:
        stderr = process.stderr.strip()
        raise RuntimeError('OWL failed to translate the LTL formula to LDBA: ' + stderr)

    ldba = hoa_to_ldba(process.stdout)
    ldba.source_formula = ltl_formula
    return ldba
