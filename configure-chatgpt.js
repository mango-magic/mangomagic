// MangoMagic 7.1 - repair the supported ChatGPT model catalogue.
// Runs on stock macOS: osascript -l JavaScript configure-chatgpt.js check|repair MODEL
// No UI automation, credentials, app bundle edits or additional runtime required.

var MODEL = 'mangomagic/mangomagic-7.1';
var BASE = 'glm-5.3-flash';
var EFFORTS = [
  {effort: 'low', description: 'Light: lighter reasoning effort for everyday tasks'},
  {effort: 'high', description: 'Mango: high reasoning effort for complex sales decisions'},
  {effort: 'max', description: 'Super Mango: maximum reasoning effort; may take longer'}
];

function validateCapabilities(wrapper, base) {
  if (wrapper.remote_model !== BASE || !/^https:\/\/ollama\.com(?::443)?\/?$/.test(wrapper.remote_host || '')) {
    throw new Error('Unexpected model backend. This release is verified for GLM 5.3 Flash on Ollama.');
  }
  ['vision', 'thinking', 'tools'].forEach(function (capability) {
    if ((base.capabilities || []).indexOf(capability) === -1) {
      throw new Error('The live base model is missing required capability: ' + capability);
    }
  });
  var info = base.model_info || {};
  var context = info[(info['general.architecture'] || '') + '.context_length'];
  if (!Number.isFinite(context) || context <= 0) throw new Error('The live context limit is unavailable.');
  var override = /^num_ctx\s+(\d+)\s*$/m.exec(wrapper.parameters || '');
  if (override) context = Math.min(context, Number(override[1]));
  return {context: context, capabilities: base.capabilities};
}

function repairCatalog(catalogue, wrapper, base) {
  var verified = validateCapabilities(wrapper, base);
  if (!catalogue || !Array.isArray(catalogue.models)) throw new Error('Invalid ChatGPT model catalogue.');
  var next = JSON.parse(JSON.stringify(catalogue));
  var matches = next.models.filter(function (m) { return m.slug === MODEL || m.slug === MODEL + ':latest'; });
  if (!matches.length) throw new Error('MangoMagic is not registered. Run the installer registration step first.');
  matches.forEach(function (m) {
    m.display_name = 'MangoMagic 7.1';
    m.description = 'ManyMangoes B2B sales intelligence. Images and adjustable thinking.';
    m.input_modalities = ['text', 'image'];
    m.supported_reasoning_levels = JSON.parse(JSON.stringify(EFFORTS));
    m.default_reasoning_level = 'low';
    m.context_window = verified.context;
    m.max_context_window = verified.context;
    // Ollama has no verified OpenAI priority service tier. Do not invent one.
    m.additional_speed_tiers = [];
    m.service_tiers = [];
    m.default_service_tier = null;
  });
  return next;
}

function validateRouting(routing) {
  if (!routing || !Array.isArray(routing.models)) throw new Error('Invalid Ollama thinking routing.');
  var model = routing.models.filter(function (m) { return m.slug === MODEL || m.slug === MODEL + ':latest'; })[0];
  var thinking = model && model.thinking;
  if (!thinking || thinking.supported !== true || !Array.isArray(thinking.levels)) {
    throw new Error('Ollama has not enabled thinking for MangoMagic. Pull the current model and register it again.');
  }
  EFFORTS.forEach(function (level) {
    if (thinking.levels.indexOf(level.effort) === -1 || !thinking.values || thinking.values[level.effort] !== level.effort) {
      throw new Error('Ollama is not forwarding the ' + level.effort + ' thinking level. Re-run registration.');
    }
  });
}

function run(argv) {
  ObjC.import('Foundation');
  if (argv.length !== 2 || ['check', 'repair'].indexOf(argv[0]) === -1 || argv[1] !== MODEL) {
    throw new Error('Usage: configure-chatgpt.js check|repair ' + MODEL);
  }
  var env = $.NSProcessInfo.processInfo.environment;
  function environment(name) { var value = env.objectForKey($(name)); return value.isNil() ? '' : ObjC.unwrap(value); }
  function read(path) {
    var error = Ref();
    var value = $.NSString.stringWithContentsOfFileEncodingError($(path), $.NSUTF8StringEncoding, error);
    if (value.isNil()) throw new Error('Cannot read ' + path);
    return ObjC.unwrap(value);
  }
  function write(path, text) {
    var error = Ref();
    if (!$(text).writeToFileAtomicallyEncodingError($(path), true, $.NSUTF8StringEncoding, error)) {
      throw new Error('Cannot write ' + path);
    }
  }
  var host = environment('OLLAMA_HOST') || 'http://127.0.0.1:11434';
  if (host.indexOf('://') === -1) host = 'http://' + host;
  host = host.replace(/\/$/, '');
  if (!/^http:\/\/(?:localhost|127\.0\.0\.1|\[::1\])(?::\d+)?$/.test(host)) {
    throw new Error('This installer requires a local Ollama server (localhost).');
  }
  function show(model) {
    var task = $.NSTask.alloc.init;
    var output = $.NSPipe.pipe;
    var errors = $.NSPipe.pipe;
    task.launchPath = '/usr/bin/curl';
    task.arguments = ['--fail', '--silent', '--show-error', '--connect-timeout', '5', '--max-time', '30',
      '--header', 'Content-Type: application/json', '--data', JSON.stringify({model: model}), host + '/api/show'];
    task.standardOutput = output;
    task.standardError = errors;
    task.launch;
    var bytes = output.fileHandleForReading.readDataToEndOfFile;
    task.waitUntilExit;
    if (task.terminationStatus !== 0) throw new Error('Ollama could not verify ' + model + '. Check that Ollama is running and connected.');
    var value = JSON.parse(ObjC.unwrap($.NSString.alloc.initWithDataEncoding(bytes, $.NSUTF8StringEncoding)));
    if (value.error) throw new Error('Ollama could not verify ' + model + '.');
    return value;
  }
  var wrapper = show(MODEL);
  // The cloud FROM implementation omits discovery metadata on custom aliases.
  // Resolve the actual backend before granting image or thinking UI controls.
  var base = show(BASE + ':cloud');
  var verified = validateCapabilities(wrapper, base);
  if (argv[0] === 'check') return 'Verified: images, tools, Low / High / Max thinking.';

  var configHome = environment('CODEX_HOME') || ObjC.unwrap($.NSHomeDirectory()) + '/.codex';
  validateRouting(JSON.parse(read(configHome + '/ollama-launch-codex-routing.json')));
  var config = read(configHome + '/config.toml');
  var topLevel = config.split(/^\s*\[/m)[0];
  var match = /^\s*model_catalog_json\s*=\s*("(?:[^"\\]|\\.)*"|'[^']*')\s*(?:#.*)?$/m.exec(topLevel);
  if (!match) throw new Error('ChatGPT model_catalog_json is missing from config.toml.');
  var path = match[1].charAt(0) === '"' ? JSON.parse(match[1]) : match[1].slice(1, -1);
  if (path.indexOf('~/') === 0) path = ObjC.unwrap($.NSHomeDirectory()) + path.slice(1);
  if (path.charAt(0) !== '/') throw new Error('ChatGPT catalogue must use an absolute path.');
  var original = read(path);
  var next = repairCatalog(JSON.parse(original), wrapper, base);
  var rendered = JSON.stringify(next, null, 2) + '\n';
  if (rendered !== original) {
    var stamp = new Date().toISOString().replace(/[:.]/g, '-');
    write(path + '.mangomagic-backup-' + stamp, original);
    // Avoid overwriting an unrelated update made during validation.
    if (read(path) !== original) throw new Error('ChatGPT catalogue changed during setup. Re-run the installer.');
    write(path, rendered);
  }
  var saved = JSON.parse(read(path));
  if (JSON.stringify(repairCatalog(saved, wrapper, base)) !== JSON.stringify(saved)) {
    throw new Error('ChatGPT catalogue verification failed.');
  }
  return 'MangoMagic 7.1 configured: images, Low / High / Max, ' + verified.context + ' token context. Restart ChatGPT to load it.';
}

if (typeof module !== 'undefined') module.exports = {validateCapabilities: validateCapabilities, repairCatalog: repairCatalog, validateRouting: validateRouting};
