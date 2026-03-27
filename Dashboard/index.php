<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CYBER-PATH | Security Operations Center</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .severity-CRITICAL { border-left: 4px solid #ef4444; background-color: rgba(239, 68, 68, 0.1); }
        .severity-HIGH { border-left: 4px solid #f97316; }
        .severity-MEDIUM { border-left: 4px solid #eab308; }
        .severity-LOW { border-left: 4px solid #22c55e; }
        #side-panel { transition: transform 0.3s ease-in-out; }
        .panel-hidden { transform: translateX(100%); }
    </style>
</head>
<body class="bg-gray-900 text-gray-100 font-sans h-screen flex flex-col overflow-hidden">

    <nav class="bg-gray-800 border-b border-gray-700 px-6 py-3 flex justify-between items-center shrink-0">
        <div class="flex items-center space-x-6">
            <span class="text-xl font-bold tracking-widest text-cyan-500"><i class="fa-solid fa-satellite-dish mr-2"></i>CYBER-PATH</span>
            <div class="space-x-1">
                <a href="#" class="px-3 py-2 bg-gray-900 text-white rounded-md text-sm font-medium border border-gray-700">Triage des Alertes</a>
                <a href="#" class="px-3 py-2 text-gray-400 hover:text-white rounded-md text-sm font-medium transition">Référentiel MITRE</a>
                <a href="#" class="px-3 py-2 text-gray-400 hover:text-white rounded-md text-sm font-medium transition">Logs Bruts</a>
            </div>
        </div>
        <div class="flex items-center space-x-4">
            <span class="text-xs text-gray-400 uppercase tracking-widest"><i class="fa-solid fa-circle text-green-500 text-[8px] animate-pulse mr-1"></i> Data Stream Active</span>
        </div>
    </nav>

    <div class="flex flex-1 overflow-hidden relative">
        <main class="flex-1 overflow-y-auto p-6">
            <div class="mb-4 flex justify-between items-end border-b border-gray-700 pb-2">
                <h2 class="text-lg font-semibold uppercase tracking-wider text-gray-300">File d'Éviction (LRU Analytics)</h2>
                <span class="text-xs text-gray-500 font-mono" id="last-update">En attente de synchronisation...</span>
            </div>
            
            <div class="bg-gray-800 rounded shadow-xl border border-gray-700 overflow-hidden">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-gray-900 text-gray-400 uppercase text-[10px] tracking-widest border-b border-gray-700">
                            <th class="p-3">Sévérité</th>
                            <th class="p-3">Horodatage</th>
                            <th class="p-3">Identifiant Entité (Hash)</th>
                            <th class="p-3">Profil Analytique</th>
                            <th class="p-3 text-right">Indice de Risque</th>
                        </tr>
                    </thead>
                    <tbody id="logs-body" class="divide-y divide-gray-700 cursor-pointer">
                        </tbody>
                </table>
            </div>
        </main>

        <aside id="side-panel" class="w-[400px] bg-gray-800 border-l border-gray-700 p-6 flex flex-col absolute right-0 top-0 bottom-0 panel-hidden shadow-2xl z-10">
            <div class="flex justify-between items-center mb-6 border-b border-gray-700 pb-4">
                <h3 class="text-sm font-bold uppercase tracking-widest text-cyan-400"><i class="fa-solid fa-microscope mr-2"></i>Inspection Vectorielle</h3>
                <button onclick="closePanel()" class="text-gray-400 hover:text-white"><i class="fa-solid fa-xmark text-lg"></i></button>
            </div>
            
            <div id="panel-content" class="flex-1 overflow-y-auto space-y-6">
                </div>
        </aside>
    </div>

    <script>
        // Définitions techniques de niveau SOC
        const dimDefinitions = [
            { name: "Criticité de la Cible (d1)", info: "Évaluation de la sensibilité de la ressource ciblée. Une valeur élevée indique une interaction avec des composants critiques (ex: SAM, /etc/shadow, processus système)." },
            { name: "Entropie du Payload (d2)", info: "Mesure de la variance des données. Une entropie élevée caractérise généralement l'utilisation de techniques d'obfuscation, d'encodage (Base64) ou de chiffrement." },
            { name: "Fréquence Temporelle (d3)", info: "Analyse de la récurrence et de la vélocité de l'action. Un score élevé est symptomatique de processus automatisés (force brute, balisage C2)." },
            { name: "Intensité de l'Action (d4)", info: "Niveau de privilège de la commande exécutée. Les valeurs maximales correspondent à des actions de modification d'état ou d'exécution de code arbitraire." },
            { name: "Score de Rareté (d5)", info: "Indice statistique basé sur l'historique comportemental. Quantifie l'écart par rapport à la ligne de base (baseline) d'utilisation légitime (concept LoTL)." }
        ];

        let currentData = [];

        async function fetchLogs() {
            try {
                const response = await fetch('api.php');
                currentData = await response.json();
                if (currentData.error) throw new Error(currentData.error);
                
                const now = new Date();
                document.getElementById('last-update').innerText = "Dernière synchro : " + now.toLocaleTimeString();
                
                renderTable();
            } catch (error) {
                console.error("Erreur API:", error);
            }
        }

        // Fonction d'analyse pour générer un résumé lisible dans le tableau
        function analyzeBehavior(dims) {
            let maxVal = Math.max(...dims);
            if (maxVal < 0.4) return "<span class='text-gray-500'>Bruit de fond (Anodin)</span>";
            
            let traits = [];
            if (dims[0] >= 0.7) traits.push("Ciblage Critique");
            if (dims[1] >= 0.7) traits.push("Forte Obfuscation");
            if (dims[2] >= 0.7) traits.push("Automatisation/Flood");
            if (dims[3] >= 0.7) traits.push("Exécution Système");
            if (dims[4] >= 0.7) traits.push("Anomalie Majeure");

            if (traits.length > 0) return `<span class="text-cyan-400">${traits.join(" + ")}</span>`;
            return "<span class='text-gray-400'>Comportement Suspect</span>";
        }

        function renderTable() {
            const tbody = document.getElementById('logs-body');
            tbody.innerHTML = '';
            
            const severityLabels = { 
                'CRITICAL': '<span class="bg-red-500 text-white px-2 py-0.5 rounded-sm text-[10px] font-bold">CRIT</span>', 
                'HIGH': '<span class="bg-orange-500 text-white px-2 py-0.5 rounded-sm text-[10px] font-bold">HIGH</span>', 
                'MEDIUM': '<span class="bg-yellow-500 text-gray-900 px-2 py-0.5 rounded-sm text-[10px] font-bold">MED</span>', 
                'LOW': '<span class="bg-green-600 text-white px-2 py-0.5 rounded-sm text-[10px] font-bold">LOW</span>' 
            };

            currentData.forEach(log => {
                const tr = document.createElement('tr');
                tr.className = `severity-${log.severity} hover:bg-gray-750 transition-colors`;
                tr.onclick = () => openPanel(log.id);
                
                tr.innerHTML = `
                    <td class="p-3">${severityLabels[log.severity]}</td>
                    <td class="p-3 text-xs font-mono text-gray-400">${log.timestamp}</td>
                    <td class="p-3 text-xs font-mono text-gray-300 truncate max-w-[150px]">${log.id_hex}</td>
                    <td class="p-3 text-xs font-semibold">${analyzeBehavior(log.dimensions)}</td>
                    <td class="p-3 text-xs font-mono text-right ${log.risk_score >= 0.7 ? 'text-red-400 font-bold' : 'text-gray-400'}">${log.risk_score}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        function openPanel(id) {
            const log = currentData.find(l => l.id === id);
            if (!log) return;
            const content = document.getElementById('panel-content');
            
            const dimsHtml = log.dimensions.map((val, i) => `
                <div class="relative group mb-4">
                    <div class="flex items-center justify-between text-xs mb-1.5">
                        <div class="flex items-center space-x-1.5 cursor-help">
                            <span class="text-gray-300 border-b border-dashed border-gray-600 pb-0.5">${dimDefinitions[i].name}</span>
                        </div>
                        <span class="font-mono ${val >= 0.7 ? 'text-red-400 font-bold' : 'text-gray-400'}">${val.toFixed(2)}</span>
                    </div>
                    <div class="w-full bg-gray-900 rounded-sm h-1 border border-gray-700">
                        <div class="${val >= 0.7 ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]' : (val >= 0.4 ? 'bg-orange-500' : 'bg-cyan-600')} h-1 rounded-sm" style="width: ${val * 100}%"></div>
                    </div>
                    <div class="absolute bottom-full left-0 mb-2 w-full p-3 bg-gray-900 rounded border border-gray-600 shadow-2xl text-[11px] text-gray-300 hidden group-hover:block z-20">
                        <p class="font-bold text-gray-100 mb-1 border-b border-gray-700 pb-1 uppercase tracking-wider">Définition Opérationnelle</p>
                        ${dimDefinitions[i].info}
                    </div>
                </div>
            `).join('');

            let mitreHtml = `<div class="p-3 bg-gray-900 rounded border border-gray-700 text-xs text-gray-500 font-mono">Status: UNMATCHED_SIGNATURE</div>`;
            if (log.mitre) {
                mitreHtml = `
                    <div class="p-4 bg-red-900/20 border border-red-800 rounded">
                        <div class="flex items-center text-red-500 mb-2 border-b border-red-900/50 pb-2">
                            <span class="font-mono text-xs font-bold tracking-widest">${log.mitre.tid} MATCH</span>
                        </div>
                        <h4 class="text-gray-100 font-semibold text-sm mb-1">${log.mitre.name}</h4>
                        <p class="text-xs text-gray-400 mb-4 leading-relaxed">${log.mitre.desc}</p>
                        <a href="https://attack.mitre.org/techniques/${log.mitre.tid}/" target="_blank" class="text-[10px] uppercase tracking-widest bg-gray-800 hover:bg-gray-700 border border-gray-600 text-gray-300 px-3 py-1.5 rounded transition">
                            Ouvrir le Framework MITRE <i class="fa-solid fa-arrow-up-right-from-square ml-1"></i>
                        </a>
                    </div>
                `;
            }

            content.innerHTML = `
                <div class="space-y-1 mb-6">
                    <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">UUID Entité Cible</p>
                    <div class="font-mono text-cyan-500 text-xs bg-gray-900 p-2.5 rounded border border-gray-700 select-all">${log.id_hex}</div>
                </div>
                <div class="mb-6">
                    <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-4">Analyse Dimensionnelle</p>
                    ${dimsHtml}
                </div>
                <div>
                    <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-3">Threat Intelligence (MITRE)</p>
                    ${mitreHtml}
                </div>
            `;
            document.getElementById('side-panel').classList.remove('panel-hidden');
        }

        function closePanel() {
            document.getElementById('side-panel').classList.add('panel-hidden');
        }

        fetchLogs();
        setInterval(fetchLogs, 3000); // Polling toutes les 3 secondes
    </script>
</body>
</html>