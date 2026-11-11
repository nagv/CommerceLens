const form = document.querySelector('#chat-form');
const question = document.querySelector('#question');
const submit = document.querySelector('#submit');
const status = document.querySelector('#status');
const conversation = document.querySelector('#conversation');
function node(tag, text, className) {
  const element = document.createElement(tag);
  element.textContent = text;
  if (className) element.className = className;
  return element;
}
// Parse a deliberately small Markdown subset into text nodes, never HTML.
function renderInline(parent, text, citations, sourcePrefix) {
  const tokens = /(\*\*([^*]+)\*\*|`([^`]+)`|\[([^\]\n]+)\])/g;
  let cursor = 0;
  for (const match of text.matchAll(tokens)) {
    parent.append(node('span', text.slice(cursor, match.index)));
    if (match[2]) parent.append(node('strong', match[2]));
    else if (match[3]) parent.append(node('code', match[3]));
    else {
      const index = citations.findIndex(citation => citation.id === match[4]);
      if (index < 0) parent.append(node('span', match[0]));
      else {
        const reference = node('button', `[${index + 1}]`, 'citation-ref');
        reference.type = 'button';
        reference.setAttribute('aria-label', `Show evidence source ${index + 1}`);
        reference.addEventListener('click', () => {
          const card = document.getElementById(`${sourcePrefix}-${index + 1}`);
          if (card) {
            card.closest('details').open = true;
            card.scrollIntoView({behavior: 'smooth', block: 'nearest'});
            card.focus({preventScroll: true});
          }
        });
        parent.append(reference);
      }
    }
    cursor = match.index + match[0].length;
  }
  parent.append(node('span', text.slice(cursor)));
}
function renderAnswer(text, citations, sourcePrefix) {
  const container = node('div', '', 'answer');
  let paragraph = null;
  let list = null;
  for (const line of text.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed) { paragraph = null; list = null; continue; }
    const heading = trimmed.match(/^#{1,6}\s+(.+?)\s*#*$/) || trimmed.match(/^\*\*(.+?)\*\*:?$/);
    const bullet = trimmed.match(/^[-*]\s+(.+)$/);
    const numbered = trimmed.match(/^\d+[.)]\s+(.+)$/);
    if (heading) {
      const title = node('h4', '');
      renderInline(title, heading[1], citations, sourcePrefix);
      container.append(title); paragraph = null; list = null;
    } else if (bullet || numbered) {
      const kind = bullet ? 'UL' : 'OL';
      if (!list || list.tagName !== kind) { list = node(kind.toLowerCase(), ''); container.append(list); }
      const item = node('li', '');
      renderInline(item, (bullet || numbered)[1], citations, sourcePrefix);
      list.append(item); paragraph = null;
    } else {
      if (!paragraph) { paragraph = node('p', ''); container.append(paragraph); }
      else paragraph.append(node('span', ' '));
      renderInline(paragraph, trimmed, citations, sourcePrefix); list = null;
    }
  }
  return container;
}
let turnNumber = 0;
form.addEventListener('change', () => {
  submit.textContent = new FormData(form).get('mode') === 'plan' ? 'Build a plan' : 'Send question';
});
async function sendRequest(value, mode, context = null) {
  submit.disabled = true;
  status.textContent = 'Retrieving evidence and preparing a response…';
  const turn = node('article', '', 'turn');
  const sourcePrefix = `source-${++turnNumber}`;
  turn.append(node('h3', value));
  conversation.append(turn);
  try {
    const response = await fetch(context ? '/api/replan' : '/api/chat', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(context || {question: value, mode})});
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Request failed.');
    turn.append(renderAnswer(result.answer, result.citations || [], sourcePrefix));
    if (result.citations?.length) {
      const sources = node('details', '');
      sources.append(node('summary', `Evidence · ${result.citations.length} sources`));
      for (const [index, citation] of result.citations.entries()) {
        const card = node('div', '', 'source');
        card.id = `${sourcePrefix}-${index + 1}`;
        card.tabIndex = -1;
        const serviceName = (citation.service_id || 'Documentation').replace(/^commercelens-/, '').replace(/[-_]/g, ' ');
        const label = `[${index + 1}] ${serviceName}`;
        let url;
        try { url = new URL(citation.source_url); } catch (_) { /* No usable URL. */ }
        if (url && ['http:', 'https:'].includes(url.protocol)) {
          const link = node('a', label);
          link.href = url.href; link.target = '_blank'; link.rel = 'noopener noreferrer';
          card.append(link);
        } else card.append(node('strong', label));
        card.append(node('p', citation.excerpt || citation.text || ''));
        sources.append(card);
      }
      turn.append(sources);
    }
    const trace = node('details', '');
    trace.append(node('summary', 'Retrieval trace'), node('pre', JSON.stringify({services: result.selected_services, steps: result.trace}, null, 2)));
    turn.append(trace);
    status.textContent = `${result.status} · ${result.latency_seconds}s · ${result.tool_calls} retrieval/relationship calls · ${result.model_calls || 0} model calls`;
    if (result.status === 'ok' && !context) question.value = '';
    if (result.status === 'ok' && mode === 'plan' && (result.behavior || 'answer') === 'answer') {
      const controls = node('form', '', 'replan-form');
      const choiceLabel = node('label', 'Selected alternative');
      const choice = node('textarea', ''); choice.rows = 2; choice.required = true; choice.maxLength = 2000;
      choice.placeholder = 'Enter or paste the alternative you want to explore'; choiceLabel.append(choice);
      const constraintsLabel = node('label', 'Additional constraints (optional)');
      const constraints = node('textarea', ''); constraints.rows = 2; constraints.maxLength = 4000;
      constraints.placeholder = 'For example: no Customer Portal changes'; constraintsLabel.append(constraints);
      const button = node('button', 'Replan with this alternative'); button.type = 'submit';
      const note = node('p', 'The original request and this plan will be included. Fresh documentation will be retrieved.');
      controls.append(choiceLabel, constraintsLabel, note, button); turn.append(controls);
      controls.addEventListener('submit', async event => {
        event.preventDefault();
        if (submit.disabled || !choice.value.trim()) return;
        button.disabled = true;
        try {
          await sendRequest('Replan: ' + choice.value.trim(), 'plan', {
            original_request: context ? context.original_request : value,
            previous_plan: result.answer,
            selected_alternative: choice.value.trim(),
            instruction: constraints.value.trim()
          });
        } finally { button.disabled = false; }
      });
    }
  } catch (error) {
    turn.append(node('p', error.message, 'error'));
    status.textContent = 'Request failed. Your question is preserved for retry.';
  } finally { submit.disabled = false; question.focus(); }
}
form.addEventListener('submit', async event => {
  event.preventDefault();
  const value = question.value.trim();
  if (value && !submit.disabled) await sendRequest(value, new FormData(form).get('mode'));
});
