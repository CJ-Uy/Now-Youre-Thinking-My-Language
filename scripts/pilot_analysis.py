"""CPU analyses for the pre-registered Opus pilot; no model or test-set access."""
from collections import defaultdict
from itertools import combinations
from statistics import mean

from research import core


def key(row):
    return row['id'], row['pool'], row['candidate']


def unique(rows, with_attempt=False):
    result = {}
    for row in rows:
        identity = key(row) + ((row['attempt'],) if with_attempt else ())
        if identity in result:
            raise ValueError(f'Duplicate record: {identity}')
        result[identity] = row
    return result


def validate_scores(problems, candidates, attempts, count, per_pool):
    """Require every eligible attempt and retain all failed/unparseable outputs."""
    lookup = {p['id']: p for p in problems}
    scores, records = unique(candidates), unique(attempts, True)
    expected = set()
    for identity, row in scores.items():
        if row['id'] not in lookup:
            raise ValueError(f'Question outside split: {identity}')
        errors = core.validate_candidate(row, lookup[row['id']])
        if errors != row['validation_errors']:
            raise ValueError(f'Validation changed: {identity}')
        prefix_error = None
        if not errors:
            if type(row['tokens']) is not int or row['tokens'] <= 0:
                raise ValueError(f'Missing tokenizer measurement: {identity}')
            try:
                core.feedback_prefix(row)
            except ValueError as error:
                prefix_error = str(error)
        if row.get('feedback_error') != prefix_error:
            raise ValueError(f'Prefix eligibility changed: {identity}')
        if errors or prefix_error:
            continue
        correct = []
        for attempt in range(count):
            attempt_key = identity + (attempt,)
            expected.add(attempt_key)
            if attempt_key not in records:
                raise ValueError(f'Missing attempt: {attempt_key}')
            prediction = records[attempt_key]
            truth = prediction['predicted_answer'] == lookup[row['id']]['answer']
            if prediction['correct'] != truth:
                raise ValueError(f'Incorrect success label: {attempt_key}')
            if prediction['error'] is None and (type(prediction['output_tokens']) is not int or prediction['output_tokens'] <= 0):
                raise ValueError(f'Missing generation measurement: {attempt_key}')
            correct.append(prediction['correct'])
        if row['feedback_accuracy'] != mean(correct):
            raise ValueError(f'Feedback mean differs from attempts: {identity}')
    if set(records) != expected:
        raise ValueError('Unexpected attempt IDs or attempt numbers')
    # Reuse the production validation of complete pools, token counts and scores.
    core.select_conditions(problems, candidates, per_pool, 0)
    return {'candidates': len(candidates), 'attempts': len(attempts),
            'errors': sum(r['error'] is not None for r in attempts),
            'truncated': sum(r['truncated'] for r in attempts),
            'unparseable': sum(r['predicted_answer'] is None for r in attempts),
            'generation_seconds': sum(r['seconds'] for r in attempts)}


def stability(problems, scores2, scores8, attempts2, attempts8, per_pool, penalty):
    ids = {p['id'] for p in problems}
    scores2 = [r for r in scores2 if r['id'] in ids]
    attempts2 = [r for r in attempts2 if r['id'] in ids]
    validate_scores(problems, scores2, attempts2, 2, per_pool)
    validate_scores(problems, scores8, attempts8, 8, per_pool)
    old, new = unique(scores2), unique(scores8)
    if set(old) != set(new):
        raise ValueError('Repeated scoring changed the candidate set')
    for identity in old:
        if {k: v for k, v in old[identity].items() if k != 'feedback_accuracy'} != {
                k: v for k, v in new[identity].items() if k != 'feedback_accuracy'}:
            raise ValueError(f'Repeated candidate changed: {identity}')
    a2, a8 = unique(attempts2, True), unique(attempts8, True)
    for identity, row in a2.items():
        # Wall-clock durations cannot reproduce; every other recorded field must.
        if {k: v for k, v in row.items() if k != 'seconds'} != {
                k: v for k, v in a8[identity].items() if k != 'seconds'}:
            raise ValueError(f'Attempts 0-1 do not reproduce Step 1: {identity}')
    pools = defaultdict(list)
    for row in scores8:
        pools[row['id'], row['pool']].append(row)
    picks = []
    for (question_id, pool), rows in sorted(pools.items()):
        eligible = [r for r in rows if not r['validation_errors'] and not r.get('feedback_error')
                    and r.get('human_rejected') is not True]
        if len(rows) != per_pool or not eligible:
            continue
        longest = max(r['tokens'] for r in eligible)

        def choose(attempt_numbers):
            return min(eligible, key=lambda r: (
                -(mean(a8[key(r) + (a,)]['correct'] for a in attempt_numbers)
                  - penalty * r['tokens'] / longest), r['tokens'], r['candidate']))['candidate']

        picks.append({'id': question_id, 'pool': pool,
                      'pairs': [choose(range(start, start + 2)) for start in (0, 2, 4, 6)],
                      'eight': choose(range(8)),
                      'shortest': min(eligible, key=lambda r: (r['tokens'], r['candidate']))['candidate']})
    if not picks:
        raise ValueError('No eligible pools in the stability check')
    agreement = mean(r['pairs'][0] == r['eight'] for r in picks)
    return {'eligible_pools': len(picks), 'penalty_for_stability': penalty,
            'reproduction': 'All recorded attempt fields match except elapsed seconds',
            'pairwise_agreement': mean(a == b for r in picks for a, b in combinations(r['pairs'], 2)),
            'all_four_pairs_agree': mean(len(set(r['pairs'])) == 1 for r in picks),
            'two_equals_eight': agreement,
            'two_equals_shortest': mean(r['pairs'][0] == r['shortest'] for r in picks),
            'eight_equals_shortest': mean(r['eight'] == r['shortest'] for r in picks),
            'each_pair_equals_shortest': [mean(r['pairs'][i] == r['shortest'] for r in picks) for i in range(4)],
            'training_attempts': 4 if agreement < 0.60 else 2, 'picks': picks}


def calibrate(problems, scores, per_pool):
    table = []
    for penalty in (0, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0):
        groups, excluded = core.select_conditions(problems, scores, per_pool, penalty)
        if not groups['original']:
            raise ValueError('No matched calibration questions remain')
        table.append({'penalty': penalty, 'ids': [r['id'] for r in groups['original']],
                      'excluded': excluded, 'pools': {
                          pool: {'mean_accuracy': mean(r['feedback_accuracy'] for r in groups[pool + '-feedback']),
                                 'mean_tokens': mean(r['tokens'] for r in groups[pool + '-feedback'])}
                          for pool in core.POOLS}})
    baseline = table[0]
    for row in table:
        if row['ids'] != baseline['ids']:
            raise ValueError('Penalty comparison changed the matched IDs')
        row['passes'] = all(
            row['pools'][p]['mean_accuracy'] >= baseline['pools'][p]['mean_accuracy'] - 0.05 for p in core.POOLS)
        for pool in core.POOLS:
            row['pools'][pool]['token_reduction_fraction'] = 1 - row['pools'][pool]['mean_tokens'] / baseline['pools'][pool]['mean_tokens']
    chosen = max(r['penalty'] for r in table if r['passes'])
    return {'chosen_penalty': chosen, 'table': table}
