import {Romcal} from 'romcal';
import { Brazil_PtBr } from '@romcal/calendar.brazil';
import fs from 'fs';

const romcal = new Romcal({
scope: 'gregorian',
localizedCalendar: Brazil_PtBr,
epiphanyOnSunday: true,
corpusChristiOnSunday: true,
ascensionOnSunday: true,
});

const definitions = await romcal.getAllDefinitions();

let md = '# Definições Romcal\n\n';
md += '| Key | Name |\n';
md += '| --- | --- |\n';
Object.entries(definitions).forEach(([key, def]) => {
  const name = def && def.name ? String(def.name).replace(/\|/g, '\\|') : '(sem nome)';
  md += `| ${key} | ${name} |\n`;
});

fs.writeFileSync('definicoes_romcal.md', md, 'utf8');
console.log('Arquivo definicoes_romcal.md gerado.');