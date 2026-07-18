const r=JSON.parse(document.getElementById("beregner-data").textContent),d=JSON.parse(document.getElementById("faktisk-info").textContent);function v(e,t){return e!==d.laengde_cm||t!==d.bredde_cm?"":`
        <a href="${d.url}" class="mt-4 flex items-start gap-3 rounded-2xl border border-skov-600/30 bg-skov-600/10 p-4 no-underline transition-colors hover:bg-skov-600/20">
          <span class="text-2xl" aria-hidden="true">🧾</span>
          <span>
            <span class="block font-semibold text-ler-900">Se den faktiske indkøbsliste for dette mål</span>
            <span class="mt-0.5 block text-sm text-ler-700">Jeg har bygget et hus på præcis ${(e/100).toLocaleString("da-DK")} × ${(t/100).toLocaleString("da-DK")} m – se de konkrete varer og mængder fra fakturaen.</span>
          </span>
        </a>`}const g=document.getElementById("vaelg-laengde"),p=document.getElementById("vaelg-bredde"),c=document.getElementById("resultat"),l=document.getElementById("handlinger"),$=document.getElementById("tilgaengelige-hint"),u=r.praedefineredeMaal.map(e=>`${(e.laengde_cm/100).toLocaleString("da-DK")}×${(e.bredde_cm/100).toLocaleString("da-DK")} m`).join(", ");$.textContent=` Færdige lister: ${u}.`;let i=null;function y(e,t){return r.praedefineredeMaal.find(n=>n.laengde_cm===e&&n.bredde_cm===t)}function a(e){const t=document.createElement("div");return t.textContent=e,t.innerHTML}function f(e){return e.toLocaleString("da-DK")}function x(){const e=Number(g.value),t=Number(p.value);if(!e||!t){c.innerHTML="",l.classList.add("hidden"),l.classList.remove("sm:flex"),i=null;return}const n=y(e,t);if(!n){if(i=null,l.classList.add("hidden"),l.classList.remove("sm:flex"),e===d.laengde_cm&&t===d.bredde_cm){c.innerHTML=`
            <a href="${d.url}" class="flex items-start gap-4 rounded-2xl border border-skov-600/30 bg-skov-600/5 p-6 no-underline transition-colors hover:bg-skov-600/10">
              <span class="text-3xl" aria-hidden="true">🧾</span>
              <span>
                <span class="block text-lg font-bold text-ler-900">Faktisk indkøbsliste for ${(e/100).toLocaleString("da-DK")} × ${(t/100).toLocaleString("da-DK")} m</span>
                <span class="mt-1 block text-ler-700">Jeg har bygget et hus i præcis dette mål. I stedet for et estimat kan du se de konkrete varer og mængder fra fakturaen – med billeder af skrueæskerne.</span>
                <span class="mt-3 inline-block font-semibold text-skov-700">Se den faktiske liste →</span>
              </span>
            </a>`;return}c.innerHTML=`
          <div class="rounded-2xl border border-dashed border-ler-300 bg-ler-100/60 p-8 text-center">
            <p class="text-3xl">📐</p>
            <p class="mt-3 font-semibold text-ler-900">Ingen færdig materialeliste for ${(e/100).toLocaleString("da-DK")} × ${(t/100).toLocaleString("da-DK")} m endnu.</p>
            <p class="mt-2 text-sm text-ler-700">Vælg et af de tilgængelige mål (${a(u)}),
            eller tilføj målet i <code class="rounded bg-ler-200 px-1">src/data/materialelister.json</code>.</p>
          </div>`;return}i=n,l.classList.remove("hidden"),l.classList.add("sm:flex");const s=r.stepRaekkefolge.map((m,b)=>{const k=r.stepTitler[m]??m,h=(n.materialerPrStep[m]??[]).map(o=>`
              <tr class="border-t border-ler-200 align-top">
                <td class="px-4 py-2.5 font-medium text-ler-900">${a(o.materiale)}</td>
                <td class="whitespace-nowrap px-4 py-2.5 text-right text-ler-800">${f(o.maengde)}</td>
                <td class="px-4 py-2.5 text-ler-700">${a(o.enhed)}</td>
                <td class="px-4 py-2.5 text-sm text-ler-500">${o.note?a(o.note):""}</td>
              </tr>`).join("");return`
            <section class="mt-6">
              <h3 class="mb-2 flex items-center gap-2 text-lg font-bold text-ler-900">
                <span class="flex h-6 w-6 items-center justify-center rounded-full bg-skov-600 text-xs font-bold text-ler-50">${b+1}</span>
                ${a(k)}
              </h3>
              <div class="overflow-x-auto rounded-xl border border-ler-200">
                <table class="w-full border-collapse text-left text-sm">
                  <thead class="bg-ler-100 text-ler-800">
                    <tr>
                      <th class="px-4 py-2.5 font-semibold">Materiale</th>
                      <th class="px-4 py-2.5 text-right font-semibold">Mængde</th>
                      <th class="px-4 py-2.5 font-semibold">Enhed</th>
                      <th class="px-4 py-2.5 font-semibold">Note</th>
                    </tr>
                  </thead>
                  <tbody>${h}</tbody>
                </table>
              </div>
            </section>`}).join("");c.innerHTML=`
        <div class="rounded-2xl border border-skov-600/20 bg-skov-600/5 p-5">
          <h2 class="text-xl font-bold text-ler-900">${a(n.navn)}</h2>
          <p class="mt-1 text-ler-700">${a(n.beskrivelse)}</p>
          <p class="mt-2 text-sm text-ler-600">Væghøjde brugt i beregningen: ${r.info.vaeghojde_cm} cm.</p>
        </div>
        ${v(e,t)}
        ${s}`}function L(e){const t=[`Materialeliste – ${e.navn}`,`(${e.laengde_cm} × ${e.bredde_cm} cm, væghøjde ${r.info.vaeghojde_cm} cm)`,""];for(const n of r.stepRaekkefolge){t.push(`## ${r.stepTitler[n]??n}`);for(const s of e.materialerPrStep[n]??[])t.push(`- ${s.materiale}: ${f(s.maengde)} ${s.enhed}${s.note?` (${s.note})`:""}`);t.push("")}return t.push("Vejledende estimater. Metode inspireret af småBYG – smaabyg.nu"),t.join(`
`)}g.addEventListener("change",x);p.addEventListener("change",x);document.getElementById("print-knap").addEventListener("click",()=>window.print());document.getElementById("kopier-knap").addEventListener("click",async e=>{if(!i)return;const t=e.currentTarget;try{await navigator.clipboard.writeText(L(i));const n=t.textContent;t.textContent="✅ Kopieret!",setTimeout(()=>t.textContent=n,2e3)}catch{t.textContent="Kunne ikke kopiere"}});
