// Builds the single-file app and the exercises.csv database export.
//   node exercise-library/scripts/build.mjs          -> output/exercise-library.html (three.js from CDN)
//   node exercise-library/scripts/build.mjs --local  -> output/dev.html (three.js from /three, for testing)
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const app = (f) => readFileSync(join(root, 'app', f), 'utf8');
const local = process.argv.includes('--local');
const THREE = local ? '/three' : 'https://cdn.jsdelivr.net/npm/three@0.170.0';

const importmap = `<script type="importmap">{"imports":{"three":"${THREE}/build/three.module.js","three/addons/":"${THREE}/examples/jsm/"}}</script>`;
// engine.js and ui.js become one module; ui's import of engine is dropped.
const engine = app('engine.js');
const ui = app('ui.js').replace(/^import \{[^}]+\} from '\.\/engine\.js';\n/m, '');
const scripts = [
  `<script>\n${app('motions.js')}\n</script>`,
  `<script>\n${app('exercises.js')}\n</script>`,
  `<script type="module">\n${engine}\n${ui}\n</script>`,
].join('\n');

const html = app('index.html').replace('<!--IMPORTMAP-->', importmap).replace('<!--SCRIPTS-->', scripts);
mkdirSync(join(root, 'output'), { recursive: true });
const out = join(root, 'output', local ? 'dev.html' : 'exercise-library.html');
writeFileSync(out, html);

// CSV export of the database, in the render-pipeline format plus the coaching fields.
const ctx = { window: {} };
vm.runInNewContext(app('exercises.js'), ctx);
const q = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
const rows = [['id', 'exercise', 'motion_file', 'muscles', 'secondary', 'camera', 'equipment', 'fault_demo', 'area', 'where', 'level', 'rehab', 'sets_reps', 'cues', 'mistakes'].join(',')];
for (const e of ctx.window.EXERCISES) {
  rows.push([e.id, e.name, `${e.motion}.fbx`, e.muscles.join(','), e.secondary.join(','), e.camera, e.equipment.join('; '),
    e.fault || '', e.area, e.where, e.level, e.rehab ? 'yes' : '', e.sets, e.cues.join(' | '), e.mistakes.join(' | ')].map(q).join(','));
}
writeFileSync(join(root, 'exercises.csv'), rows.join('\n') + '\n');
console.log(`wrote ${out} (${(html.length / 1024).toFixed(0)} KB) and exercises.csv (${rows.length - 1} exercises)`);
