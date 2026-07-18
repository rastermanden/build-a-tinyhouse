const r=JSON.parse(document.getElementById("beregner-data").textContent),m=document.getElementById("vaelg-laengde"),g=document.getElementById("vaelg-bredde"),c=document.getElementById("resultat"),d=document.getElementById("handlinger"),v=document.getElementById("tilgaengelige-hint"),p=r.praedefineredeMaal.map(e=>`${(e.laengde_cm/100).toLocaleString("da-DK")}×${(e.bredde_cm/100).toLocaleString("da-DK")} m`).join(", ");v.textContent=` Færdige lister: ${p}.`;let o=null;function $(e,t){return r.praedefineredeMaal.find(n=>n.laengde_cm===e&&n.bredde_cm===t)}function s(e){const t=document.createElement("div");return t.textContent=e,t.innerHTML}function x(e){return e.toLocaleString("da-DK")}function u(){const e=Number(m.value),t=Number(g.value);if(!e||!t){c.innerHTML="",d.classList.add("hidden"),d.classList.remove("sm:flex"),o=null;return}const n=$(e,t);if(!n){o=null,d.classList.add("hidden"),d.classList.remove("sm:flex"),c.innerHTML=`
          <div class="rounded-2xl border border-dashed border-ler-300 bg-ler-100/60 p-8 text-center">
            <p class="text-3xl">📐</p>
            <p class="mt-3 font-semibold text-ler-900">Ingen færdig materialeliste for ${(e/100).toLocaleString("da-DK")} × ${(t/100).toLocaleString("da-DK")} m endnu.</p>
            <p class="mt-2 text-sm text-ler-700">Vælg et af de tilgængelige mål (${s(p)}),
            eller tilføj målet i <code class="rounded bg-ler-200 px-1">src/data/materialelister.json</code>.</p>
          </div>`;return}o=n,d.classList.remove("hidden"),d.classList.add("sm:flex");const l=r.stepRaekkefolge.map((i,f)=>{const b=r.stepTitler[i]??i,h=(n.materialerPrStep[i]??[]).map(a=>`
              <tr class="border-t border-ler-200 align-top">
                <td class="px-4 py-2.5 font-medium text-ler-900">${s(a.materiale)}</td>
                <td class="whitespace-nowrap px-4 py-2.5 text-right text-ler-800">${x(a.maengde)}</td>
                <td class="px-4 py-2.5 text-ler-700">${s(a.enhed)}</td>
                <td class="px-4 py-2.5 text-sm text-ler-500">${a.note?s(a.note):""}</td>
              </tr>`).join("");return`
            <section class="mt-6">
              <h3 class="mb-2 flex items-center gap-2 text-lg font-bold text-ler-900">
                <span class="flex h-6 w-6 items-center justify-center rounded-full bg-skov-600 text-xs font-bold text-ler-50">${f+1}</span>
                ${s(b)}
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
          <h2 class="text-xl font-bold text-ler-900">${s(n.navn)}</h2>
          <p class="mt-1 text-ler-700">${s(n.beskrivelse)}</p>
          <p class="mt-2 text-sm text-ler-600">Væghøjde brugt i beregningen: ${r.info.vaeghojde_cm} cm.</p>
        </div>
        ${l}`}function y(e){const t=[`Materialeliste – ${e.navn}`,`(${e.laengde_cm} × ${e.bredde_cm} cm, væghøjde ${r.info.vaeghojde_cm} cm)`,""];for(const n of r.stepRaekkefolge){t.push(`## ${r.stepTitler[n]??n}`);for(const l of e.materialerPrStep[n]??[])t.push(`- ${l.materiale}: ${x(l.maengde)} ${l.enhed}${l.note?` (${l.note})`:""}`);t.push("")}return t.push("Vejledende estimater. Metode inspireret af småBYG – smaabyg.nu"),t.join(`
`)}m.addEventListener("change",u);g.addEventListener("change",u);document.getElementById("print-knap").addEventListener("click",()=>window.print());document.getElementById("kopier-knap").addEventListener("click",async e=>{if(!o)return;const t=e.currentTarget;try{await navigator.clipboard.writeText(y(o));const n=t.textContent;t.textContent="✅ Kopieret!",setTimeout(()=>t.textContent=n,2e3)}catch{t.textContent="Kunne ikke kopiere"}});
