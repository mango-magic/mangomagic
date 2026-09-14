'use strict';

// Run with: node api/mangomagic-repo/tests/test_catalog.js
// Only the pure exports are called. All catalogue and model data are fixtures;
// the macOS run() entry point, live APIs, and user configuration are never used.
const assert = require('node:assert/strict');
const test = require('node:test');
const { repairCatalog, validateCapabilities, validateRouting } = require('../configure-chatgpt.js');

const ALIAS = 'mangomagic/mangomagic-7.1';
const CONTEXT = 1048576;
const REQUIRED_CAPABILITIES = ['vision', 'thinking', 'tools'];

function wrapper(overrides = {}) {
  return {
    remote_model: 'glm-5.3-flash',
    remote_host: 'https://ollama.com',
    capabilities: ['completion'],
    model_info: {},
    parameters: 'temperature 0.7\n',
    ...overrides,
  };
}

function base(overrides = {}) {
  return {
    capabilities: ['completion', 'thinking', 'tools', 'vision'],
    model_info: {
      'general.architecture': 'glm-test',
      'glm-test.context_length': CONTEXT,
    },
    ...overrides,
  };
}

function alias(slug = ALIAS) {
  return {
    slug,
    display_name: 'Old MangoMagic',
    input_modalities: ['text'],
    supported_reasoning_levels: [],
    context_window: 4096,
    base_instructions: 'Keep the existing ManyMangoes sales instructions.\nLiteral $() and `text`.',
    model_messages: {
      instructions_template: '{{ base_instructions }}\n{{ personality }}',
      instructions_variables: { personality: 'Australian English' },
    },
    custom_metadata: { tags: ['sales'], enabled: true },
  };
}

function catalog(models = [alias()]) {
  return {
    version: 3,
    instructions: 'Preserve catalogue-wide instructions verbatim.\nSecond line.',
    metadata: { source: 'fixture', flags: ['keep'] },
    models,
  };
}

function routingModel(slug = ALIAS, thinkingOverrides = {}) {
  return {
    slug,
    thinking: {
      supported: true,
      levels: ['low', 'high', 'max'],
      values: { low: 'low', high: 'high', max: 'max' },
      ...thinkingOverrides,
    },
  };
}

function frozen(value) {
  if (value !== null && typeof value === 'object') {
    Object.values(value).forEach(frozen);
    Object.freeze(value);
  }
  return value;
}

function assertRestored(model, context = CONTEXT) {
  assert.equal(model.display_name, 'MangoMagic 7.1');
  assert.deepEqual(model.input_modalities, ['text', 'image']);
  assert.deepEqual(model.supported_reasoning_levels.map(level => level.effort), ['low', 'high', 'max']);
  for (const level of model.supported_reasoning_levels) {
    assert.equal(typeof level.description, 'string');
    assert.ok(level.description.length > 0);
  }
  assert.equal(model.default_reasoning_level, 'low');
  assert.equal(model.context_window, context);
  assert.equal(model.max_context_window, context);
  assert.deepEqual(model.additional_speed_tiers, []);
  assert.deepEqual(model.service_tiers, []);
  assert.equal(model.default_service_tier, null);
}

for (const slug of [ALIAS, `${ALIAS}:latest`]) {
  test(`restores missing alias metadata from the verified base: ${slug}`, () => {
    const input = frozen(catalog([{ slug, base_instructions: 'Retain these instructions.' }]));
    const actual = repairCatalog(input, frozen(wrapper()), frozen(base()));

    assert.equal(actual.models.length, 1);
    assert.equal(actual.models[0].slug, slug);
    assert.equal(actual.models[0].base_instructions, input.models[0].base_instructions);
    assertRestored(actual.models[0]);
  });
}

test('preserves other models, alias instructions, unknown fields, ordering, and all inputs', () => {
  const other = {
    slug: 'other-provider/model',
    display_name: 'Other model',
    input_modalities: ['text', 'image', 'audio'],
    supported_reasoning_levels: [{ effort: 'medium', description: 'Keep me' }],
    context_window: 128000,
    base_instructions: 'Other model instructions.\nKeep their exact whitespace.  ',
    custom_metadata: { nested: [{ value: 42 }] },
  };
  const similar = { slug: `${ALIAS}-preview`, base_instructions: 'Do not match by prefix.' };
  const input = frozen(catalog([other, alias(), similar, alias(`${ALIAS}:latest`)]));
  const liveWrapper = frozen(wrapper());
  const liveBase = frozen(base());
  const before = JSON.stringify([input, liveWrapper, liveBase]);
  const actual = repairCatalog(input, liveWrapper, liveBase);

  assert.notStrictEqual(actual, input);
  assert.deepEqual(actual.models.map(model => model.slug), input.models.map(model => model.slug));
  assert.equal(JSON.stringify(actual.models[0]), JSON.stringify(other));
  assert.equal(JSON.stringify(actual.models[2]), JSON.stringify(similar));
  const { models: originalModels, ...originalTopLevel } = input;
  const { models: repairedModels, ...repairedTopLevel } = actual;
  assert.deepEqual(repairedTopLevel, originalTopLevel);
  const repairedFields = new Set([
    'display_name', 'description', 'input_modalities', 'supported_reasoning_levels',
    'default_reasoning_level', 'context_window', 'max_context_window',
    'additional_speed_tiers', 'service_tiers', 'default_service_tier',
  ]);
  for (const index of [1, 3]) {
    assertRestored(repairedModels[index]);
    for (const [key, value] of Object.entries(originalModels[index])) {
      if (!repairedFields.has(key)) assert.deepEqual(repairedModels[index][key], value);
    }
  }
  assert.equal(JSON.stringify([input, liveWrapper, liveBase]), before);
});

test('repair is idempotent and does not share mutable output with earlier results', () => {
  const once = frozen(repairCatalog(catalog([alias(), alias(`${ALIAS}:latest`)]), wrapper(), base()));
  const twice = repairCatalog(once, wrapper(), base());

  assert.equal(JSON.stringify(twice), JSON.stringify(once));
  assert.notStrictEqual(twice, once);
  twice.models[0].supported_reasoning_levels[0].description = 'Changed only in this result';
  twice.models[0].custom_metadata.tags.push('changed');
  assert.notEqual(twice.models[0].supported_reasoning_levels[0].description,
    once.models[0].supported_reasoning_levels[0].description);
  assert.deepEqual(once.models[0].custom_metadata.tags, ['sales']);
  assert.deepEqual(twice.models[1].supported_reasoning_levels, once.models[1].supported_reasoning_levels);
  const fresh = repairCatalog(catalog(), wrapper(), base());
  assert.deepEqual(fresh.models[0].supported_reasoning_levels, once.models[0].supported_reasoning_levels);
});

test('validates base capabilities even when wrapper discovery metadata is absent', () => {
  const liveWrapper = wrapper();
  delete liveWrapper.capabilities;
  delete liveWrapper.model_info;
  const liveBase = frozen(base());
  const actual = validateCapabilities(frozen(liveWrapper), liveBase);

  assert.equal(actual.context, CONTEXT);
  for (const capability of REQUIRED_CAPABILITIES) assert.ok(actual.capabilities.includes(capability));
});

for (const missing of REQUIRED_CAPABILITIES) {
  test(`rejects a base missing ${missing}, even if the wrapper claims support`, () => {
    const liveBase = frozen(base({ capabilities: base().capabilities.filter(value => value !== missing) }));
    const liveWrapper = frozen(wrapper({ capabilities: base().capabilities }));
    const input = frozen(catalog());
    const before = JSON.stringify(input);
    const expected = new RegExp(`missing required capability: ${missing}`);

    assert.throws(() => validateCapabilities(liveWrapper, liveBase), expected);
    assert.throws(() => repairCatalog(input, liveWrapper, liveBase), expected);
    assert.equal(JSON.stringify(input), before);
  });
}

test('rejects unavailable base capabilities', () => {
  for (const capabilities of [undefined, null, []]) {
    assert.throws(() => validateCapabilities(wrapper(), base({ capabilities })), /missing required capability/);
    assert.throws(() => repairCatalog(catalog(), wrapper(), base({ capabilities })), /missing required capability/);
  }
});

test('rejects mismatched or missing remote backends', () => {
  for (const remote_model of ['kimi-k3', 'glm-5.3', 'glm-5.3-flash:cloud', '', null, undefined]) {
    const liveWrapper = frozen(wrapper({ remote_model }));
    assert.throws(() => validateCapabilities(liveWrapper, base()), /Unexpected model backend/);
    assert.throws(() => repairCatalog(frozen(catalog()), liveWrapper, base()), /Unexpected model backend/);
  }
});

test('rejects remote hosts outside the verified HTTPS Ollama origin', () => {
  const invalidHosts = [
    'http://ollama.com', 'https://example.com', 'https://ollama.com.example.com',
    'https://ollama.com@evil.example', 'https://user@ollama.com',
    'https://ollama.com:8443', 'https://ollama.com/api',
    'https://ollama.com?host=example.com', 'https://ollama.com#fragment',
    '', null, undefined,
  ];
  for (const remote_host of invalidHosts) {
    const liveWrapper = frozen(wrapper({ remote_host }));
    assert.throws(() => validateCapabilities(liveWrapper, base()), /Unexpected model backend/);
    assert.throws(() => repairCatalog(frozen(catalog()), liveWrapper, base()), /Unexpected model backend/);
  }
});

test('accepts equivalent HTTPS Ollama hosts with a trailing slash or explicit port 443', () => {
  for (const remote_host of ['https://ollama.com', 'https://ollama.com/', 'https://ollama.com:443', 'https://ollama.com:443/']) {
    const liveWrapper = frozen(wrapper({ remote_host }));
    assert.equal(validateCapabilities(liveWrapper, frozen(base())).context, CONTEXT);
    assertRestored(repairCatalog(frozen(catalog()), liveWrapper, frozen(base())).models[0]);
  }
});

test('uses the live architecture context limit when there is no num_ctx override', () => {
  const liveBase = frozen(base({ model_info: {
    'general.architecture': 'another-architecture',
    'another-architecture.context_length': 262144,
    'glm-test.context_length': CONTEXT,
  } }));
  for (const parameters of ['', undefined, 'temperature 0.5\nnum_predict 2048\n']) {
    const liveWrapper = frozen(wrapper({ parameters }));
    assert.equal(validateCapabilities(liveWrapper, liveBase).context, 262144);
    assertRestored(repairCatalog(frozen(catalog()), liveWrapper, liveBase).models[0], 262144);
  }
});

test('a smaller num_ctx conservatively limits both catalogue context fields', () => {
  for (const parameters of ['num_ctx 64000', 'temperature 0.7\nnum_ctx\t64000\nnum_predict 2048\n']) {
    const liveWrapper = frozen(wrapper({ parameters }));
    const liveBase = frozen(base());
    assert.equal(validateCapabilities(liveWrapper, liveBase).context, 64000);
    assertRestored(repairCatalog(frozen(catalog()), liveWrapper, liveBase).models[0], 64000);
  }
});

test('num_ctx never increases the verified base model context limit', () => {
  for (const context of [CONTEXT, CONTEXT * 2]) {
    const liveWrapper = frozen(wrapper({ parameters: `num_ctx ${context}\n` }));
    assert.equal(validateCapabilities(liveWrapper, frozen(base())).context, CONTEXT);
    assertRestored(repairCatalog(frozen(catalog()), liveWrapper, frozen(base())).models[0]);
  }
});

test('rejects unavailable or invalid live base context limits', () => {
  const invalidInfo = [undefined, null, {}, { 'general.architecture': 'glm-test' }];
  for (const value of [0, -1, '1048576', null, NaN, Infinity]) {
    invalidInfo.push({ 'general.architecture': 'glm-test', 'glm-test.context_length': value });
  }
  for (const model_info of invalidInfo) {
    const liveBase = frozen(base({ model_info }));
    assert.throws(() => validateCapabilities(wrapper(), liveBase), /context limit is unavailable/);
    assert.throws(() => repairCatalog(frozen(catalog()), wrapper(), liveBase), /context limit is unavailable/);
  }
});

test('refuses invalid catalogue structures', () => {
  const invalidCatalogs = [undefined, null, false, 'catalogue', [], {}, { models: null }, { models: {} }, { models: 'alias' }];
  for (const input of invalidCatalogs) {
    assert.throws(() => repairCatalog(frozen(input), frozen(wrapper()), frozen(base())), /Invalid ChatGPT model catalogue/);
  }
  for (const models of [[null], [undefined]]) {
    assert.throws(() => repairCatalog(frozen(catalog(models)), frozen(wrapper()), frozen(base())));
  }
});

test('refuses catalogues with no exact registered alias and does not add a model', () => {
  const cases = [
    [],
    [{ slug: 'glm-5.3-flash:cloud' }],
    [{ slug: 'mangomagic/mangomagic-7.0' }],
    [{ slug: `${ALIAS}-preview` }, { slug: `${ALIAS}:other` }],
  ];
  for (const models of cases) {
    const input = frozen(catalog(models));
    const before = JSON.stringify(input);
    assert.throws(() => repairCatalog(input, frozen(wrapper()), frozen(base())), /not registered/);
    assert.equal(JSON.stringify(input), before);
  }
});

for (const slug of [ALIAS, `${ALIAS}:latest`]) {
  test(`accepts actual low/high/max forwarding for the registered alias: ${slug}`, () => {
    const input = frozen({
      models: [
        routingModel('other-provider/model', { supported: false, values: {} }),
        routingModel(slug),
      ],
      metadata: { source: 'fixture' },
    });
    const before = JSON.stringify(input);

    assert.doesNotThrow(() => validateRouting(input));
    assert.equal(JSON.stringify(input), before);
  });
}

test('refuses malformed routing documents', () => {
  const inputs = [undefined, null, false, 'routing', [], {}, { models: null }, { models: {} }];
  for (const input of inputs) {
    assert.throws(() => validateRouting(frozen(input)), /Invalid Ollama thinking routing/);
  }
});

test('refuses absent thinking configuration even when another model supports thinking', () => {
  for (const thinking of [undefined, null, false, {}]) {
    const input = frozen({ models: [routingModel('other-provider/model'), { slug: ALIAS, thinking }] });
    assert.throws(() => validateRouting(input), /has not enabled thinking for MangoMagic/);
  }
});

test('requires supported to be boolean true, refusing false, missing, and truthy substitutes', () => {
  for (const supported of [false, undefined, null, 'true', 'false', 1, 0]) {
    const model = routingModel(ALIAS, { supported });
    if (supported === undefined) delete model.thinking.supported;
    const input = frozen({ models: [model] });
    assert.throws(() => validateRouting(input), /has not enabled thinking for MangoMagic/);
  }
});

test('requires an explicit levels array even when the value mapping is complete', () => {
  for (const levels of [undefined, null, false, 'low,high,max', { low: true, high: true, max: true }]) {
    const model = routingModel(ALIAS, { levels });
    if (levels === undefined) delete model.thinking.levels;
    assert.throws(() => validateRouting(frozen({ models: [model] })), /has not enabled thinking for MangoMagic/);
  }
  assert.throws(() => validateRouting(frozen({ models: [routingModel(ALIAS, { levels: [] })] })), /not forwarding the low thinking level/);
});

test('refuses absent value mappings despite supported=true and advertised levels', () => {
  for (const values of [undefined, null, {}, false, 'low,high,max']) {
    const model = routingModel(ALIAS, { values });
    if (values === undefined) delete model.thinking.values;
    assert.throws(() => validateRouting(frozen({ models: [model] })), /not forwarding the low thinking level/);
  }
});

for (const level of ['low', 'high', 'max']) {
  test(`requires the advertised ${level} level even when its mapping is present`, () => {
    const model = routingModel();
    model.thinking.levels = model.thinking.levels.filter(value => value !== level);
    assert.throws(() => validateRouting(frozen({ models: [model] })), new RegExp(`not forwarding the ${level} thinking level`));
  });

  test(`requires the ${level} value mapping even when the level is advertised`, () => {
    const model = routingModel();
    delete model.thinking.values[level];
    assert.throws(() => validateRouting(frozen({ models: [model] })), new RegExp(`not forwarding the ${level} thinking level`));
  });

  test(`rejects boolean, wrong-string, and non-string forwarding values for ${level}`, () => {
    const incorrectValues = [true, false, 'true', 'false', 'medium', 'none', '', level.toUpperCase(), 1, null,
      ...['low', 'high', 'max'].filter(value => value !== level)];
    for (const value of incorrectValues) {
      const model = routingModel();
      model.thinking.values[level] = value;
      const input = frozen({ models: [model] });
      const before = JSON.stringify(input);

      assert.throws(() => validateRouting(input), new RegExp(`not forwarding the ${level} thinking level`),
        `Must reject ${level} mapped to ${JSON.stringify(value)}`);
      assert.equal(JSON.stringify(input), before);
    }
  });
}

test('refuses routing without an exact registered alias even when other models have valid mappings', () => {
  const cases = [
    [],
    [routingModel('glm-5.3-flash:cloud')],
    [routingModel('other-provider/model')],
    [routingModel('mangomagic/mangomagic-7.0')],
    [routingModel(`${ALIAS}-preview`), routingModel(`${ALIAS}:other`)],
  ];
  for (const models of cases) {
    const input = frozen({ models });
    const before = JSON.stringify(input);
    assert.throws(() => validateRouting(input), /has not enabled thinking for MangoMagic/);
    assert.equal(JSON.stringify(input), before);
  }
});
