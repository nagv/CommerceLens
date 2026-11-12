"""Application response structure; no golden answers or evaluator criteria are used."""
import json
import re

PLAN_SECTIONS = {
    'strategy': 'Overall strategy',
    'service_changes': 'Service changes',
    'implementation_order': 'Implementation order',
    'requirement_coverage': 'How this meets the request',
    'alternatives': 'Alternatives',
    'recommendation': 'Why this approach',
    'validation': 'Validation',
}
PLAN_INSTRUCTION = (
    'For an implementation plan, return a plan object alongside behavior and factual_claims. '
    'plan must have exactly these fields, each a nonempty string containing useful paragraphs or Markdown bullets: '
    + ', '.join(PLAN_SECTIONS) + '. '
    'strategy explains the selected approach and boundaries. service_changes describes each necessary service separately '
    'with its responsibility, proposed changes and interactions; distinguish required from conditional changes. '
    'implementation_order gives numbered stages, prerequisites and safe parallel work. '
    'requirement_coverage breaks down each requested outcome and explains how it is met, including user-visible behavior, '
    'unchanged constraints, repeat requests and relevant failures. alternatives gives meaningful variations and trade-offs '
    '(for Replan keep the selected option and exclusions; discuss only compatible variations). recommendation explains '
    'why the selected approach fits better. validation covers behavior, failures, rollout and unanswered capability checks. '
    'Each section must be substantive, not a heading or placeholder. Cite current facts using supplied source IDs, '
    'label future capabilities as proposals, and do not invent existing interfaces or production provider support. '
    'Do not put a plan object on clarification, unknown, redirect or uncertain/debugging responses. '
    'A debugging request needs ordered investigation leads and focused evidence requests, not an implementation plan. '
    'If a plan object is supplied, the host renders its sections; answer may be a short introduction.'
)
REVIEW_INSTRUCTION = (
    'Perform a final quality review of the draft against the original request and supplied evidence only. '
    'Return the complete revised JSON response; do not describe this review. '
    'First decide whether this is an implementation request, an incident/debugging request, an ambiguous request, '
    'or a request for unavailable information. Do not force an implementation plan on the other types. '
    'For debugging give ordered discriminating checks, conditional causes, relevant services and focused missing evidence; '
    'never assert an unverified root cause, recommend new business actions or propose service changes. '
    'For high-level Ask remove table/queue/endpoint/header identifiers and locking internals unless explicitly requested; '
    'use human-readable service names and business language. The word how alone is not a request for implementation details. Preserve counts, costs, deadlines, outcomes, cross-service/provider responsibilities and limits. '
    'Explain who initiates an operation, who enforces it and the customer outcome; do not omit safety-relevant steps '
    'that the evidence identifies. Explain unavailable live information directly. '
    'For ambiguity ask which operation, provide relevant choices and invite a more detailed question; do not guess. '
    'For a feasible Plan request use the plan object defined in the system instructions, including all seven sections. '
    'For Replan honor the selection and exclusions throughout. Do not require changes to every retrieved service. '
    'All current-state claims must still cite supplied evidence; do not add claims from your own knowledge. '
    'If evidence conflicts, preserve uncertainty without presenting a speculative fix as current behavior.'
)

def decode_response(raw):
    candidate = re.sub(r'^```(?:json)?\s*|\s*```$', '', raw.strip())
    if not candidate.startswith('{'):
        return None  # Backwards-compatible plain text; engine still checks citations.
    payload = json.loads(candidate)
    if (not isinstance(payload, dict) or payload.get('behavior') not in
            ('answer', 'partial_answer', 'uncertain', 'unknown', 'clarify', 'redirect')
            or not isinstance(payload.get('factual_claims'), bool)):
        raise ValueError('Invalid response envelope')
    if payload.get('plan') is not None:
        plan = payload['plan']
        if (payload['behavior'] not in ('answer', 'partial_answer') or not isinstance(plan, dict)
                or set(plan) != set(PLAN_SECTIONS)
                or any(not isinstance(v, str) or not v.strip() for v in plan.values())):
            raise ValueError('Invalid implementation plan sections')
        payload['answer'] = '\n\n'.join('## '+title+'\n\n'+plan[key].strip()
                                        for key, title in PLAN_SECTIONS.items())
    if not isinstance(payload.get('answer'), str) or not payload['answer'].strip():
        raise ValueError('Invalid response answer')
    return payload


def response_schema(mode):
    properties={'behavior':{'type':'string','enum':['answer','partial_answer','uncertain','unknown','clarify','redirect']},
                'factual_claims':{'type':'boolean'},'answer':{'type':'string'}}
    if mode=='plan':
        properties['plan']={'anyOf':[{'type':'null'},{'type':'object',
            'properties':{key:{'type':'string','minLength':1} for key in PLAN_SECTIONS},
            'required':list(PLAN_SECTIONS),'additionalProperties':False}]}
    return {'type':'object','properties':properties,'required':list(properties),'additionalProperties':False}


def normalize_citations(answer, aliases):
    def expand_range(match):
        first,last=int(match[1]),int(match[2])
        if 1 <= first <= last <= len(aliases):
            return ''.join(f'[S{i}]' for i in range(first,last+1))
        return match[0]  # Invalid/reversed ranges still fail validation.
    answer = re.sub(r'\[S(\d+)\s*[-\u2013\u2014]\s*S(\d+)\]',expand_range,answer)
    answer = re.sub(r'\[(S\d+(?:\s*,\s*S\d+)+)\]',
                    lambda m: ''.join('['+x.strip()+']' for x in m[1].split(',')), answer)
    # The input-field label is not a documentary source citation.
    answer = answer.replace('[replan_context]', '`replan_context`')
    # Keep canonical IDs in persisted output/evaluation; only the
    # model-facing prompt uses compact aliases to prevent truncation.
    answer = re.sub(r'\[([^\[\]\n]+)\]',
                    lambda match: '[' + aliases.get(match[1], match[1]) + ']', answer)
    return answer
