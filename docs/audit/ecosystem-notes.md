# NotFair — mapa de sobreposição pública e recorte recomendado

Leitura em 2026-10-17 UTC. Somente oito repositórios confirmados públicos foram
usados nesta nota. Nenhum nome ou conteúdo privado está incluído. Leitura
estática de README, branch main e árvore recursiva; não é reauditoria de execução
dos projetos existentes nem prova de homologação das integrações descritas.

## Conclusão

**F — ADAPT**, condicionado a um recorte pequeno para o novo
`camaleao-marketing-copilot` explicitamente solicitado: instruções PT-BR para
ChatGPT e análises locais de snapshots HTML e exports de Search Console e mídia
paga. Não recriar suíte SEO, portal de agência, CRM, biblioteca de evidências ou
gateway de ferramentas. O ganho proposto é transformar entradas fornecidas pelo
operador em análise reproduzível, limitações e propostas ainda pendentes.

Sem a exigência de um novo repositório, **C — EXTRACT** em consumidores existentes
seria o caminho mais econômico. O nome novo não justifica copiar 48 skills nem
construir um segundo produto de automação de marketing nesta entrega.

## Upstream fixado

NotFair: `nowork-studio/notfair-plugin`, main
`c839f30bfea788b822d1ab1b6f1a8cc4c0d3020d`.
[README](https://github.com/nowork-studio/notfair-plugin/blob/c839f30bfea788b822d1ab1b6f1a8cc4c0d3020d/README.md)
declara 48 skills e MIT; o MCP hospedado é dependência externa, não um backend
livre contido no plugin.

Trechos lidos em fonte primária:

- [Paid Ads Review](https://github.com/nowork-studio/notfair-plugin/blob/c839f30bfea788b822d1ab1b6f1a8cc4c0d3020d/paid-ads/paid-ads-review/WORKFLOW.md): exige períodos completos equivalentes, moeda, conversão, atribuição e atraso de reporte; bloqueia mistura não qualificada de CPA/ROAS; revisão somente leitura.
- [Paid Ads Integrations](https://github.com/nowork-studio/notfair-plugin/blob/c839f30bfea788b822d1ab1b6f1a8cc4c0d3020d/paid-ads/paid-ads-integrations/WORKFLOW.md): ferramentas acessíveis na sessão determinam capacidades; não inferir autorização nem inventar conector. Amazon e ChatGPT Ads dependem de conector verificado ou export.
- [Google Analytics](https://github.com/nowork-studio/notfair-plugin/blob/c839f30bfea788b822d1ab1b6f1a8cc4c0d3020d/analytics/google-analytics/WORKFLOW.md): separa atribuição GA4 da atribuição de anúncios; pede janela, timezone e definição de métrica; correlação não prova causalidade.

## Mapa baseado em evidência pública

| Projeto e revisão main lida | Capacidade já existente | Relação com NotFair / evitar duplicação | Papel recomendado |
|---|---|---|---|
| [open-seo](https://github.com/ofelipepeixoto/open-seo/tree/d7ea7852480601af9bc8870942af8311a410e567) | Fork público. README e árvore mostram SEO, pesquisa de palavras, backlinks, auditoria, visibilidade IA, plugin e MCP. DataForSEO é dependência de serviço. | Sobreposição muito alta em SEO/GEO e relatórios. `plugins/openseo/skills/` já contém keyword-research, seo-audit, ai-visibility-audit, seo-report e outros. | Manter como referência/ferramenta especialista futura. Copilot só analisa arquivos fornecidos; não duplicar rastreador, índices, trackers e dashboards. |
| [no-ai-slop](https://github.com/ofelipepeixoto/no-ai-slop/tree/3b6579498dab2fae960f2fd5a06db25b71d2f4b2) | Fork público, plugin e skill de revisão de estilo, preservação de voz e avaliação editorial. | Já cobre escrita genérica, linguagem inflada e atribuição vaga. O eval exige preservar alegações e não fingir detectar autoria IA. | Revisão editorial opcional por referência; não vendorizá-lo nem transformar seu checklist em nota automática de qualidade factual. |
| [creator-lab](https://github.com/ofelipepeixoto/creator-lab/tree/14f83569977fac0821ddaa98706e3c8b6253b1d8) | Fork público de pesquisa de Reels, oito classificações, hooks, CTAs, export JSON, replay. Apify/Fireworks ou Groq/Jev externos. | Sobrepõe pesquisa criativa e interpretação de engagement. README distingue amostra e causalidade. | Futuro produtor de evidência criativa autorizada. Não duplicar scraper, transcrição, classificação ou interface; nenhuma chamada paga nesta entrega. |
| [radar-oaas](https://github.com/ofelipepeixoto/radar-oaas/tree/aceb046431fa199222f72fb2091c0b63a992102f) | Avalia prontidão de serviço, evidências, economia, estágio e próximo experimento, com regras determinísticas. | NotFair também organiza contexto econômico e planos, mas OaaS trata prontidão do negócio, não diagnóstico de campanha. | Manter decisão de produto/prontidão no OaaS. Não criar outro canvas, score global ou certificação de marketing no Copilot. |
| [camaleao-portal](https://github.com/ofelipepeixoto/camaleao-portal/tree/6acae7ad977cef31eef0d284a7bcffa40e9f20ba) | Portal de pedidos, revisões e versões. `docs/MARKETING-PILOTO.md` já incorpora briefing/editorial adaptado de Marketing Skills, atribuição MIT e 20 fixtures fictícias. | Sobreposição alta em briefing, copy e revisão. Estado de Supabase/n8n é descrito como não homologado no README lido. | Futuro consumidor de relatórios revisados. Não criar novo cadastro, multiempresa, fila ou aprovação/publicação no Copilot. |
| [radar-integration-hub](https://github.com/ofelipepeixoto/radar-integration-hub/tree/d7084bdf63fcea9cf13ad1c5b3254c828b2cb6e2) | Integrações governadas, proposta/hash/versão/revisor/tenant, expiração/replay, reserva de orçamento e CRM preview. Leitura local/simulada; sem produção. | Sobrepõe fronteira de autorização para futuros conectores, quota e orçamento. NotFair depende de ferramentas reais para mutações. | Qualquer ponte externa futura deve passar por governança existente, após homologação. Não instalar MCP hospedado, credenciais, agendador ou ações remotas no novo repo. |
| [radar-evidence-kit](https://github.com/ofelipepeixoto/radar-evidence-kit/tree/22d3cae88f1a43f55f75d880bbe6b46d5582d0ba) | MIT autoral. Contratos de evidência, hashes, escopo/revisão, diário e checkpoint independente. Não autentica revisor nem prova verdade. | Sobrepõe proveniência; evita construir outro ledger ou tratar hash como verificação factual. | Usar referências/contrato de interoperabilidade futuro, sem afirmar integração pronta. Relatório do Copilot pode ter SHA/origem e `review_status=pending`; sem emissão de aprovação ou identidade verificada. |
| [skill-revisao-de-fontes](https://github.com/ofelipepeixoto/skill-revisao-de-fontes/tree/14bebdb77b82c4f283e20d3a88152f03306a8899) | Auditoria de alegações com fontes primárias; vereditos confirmada/parcial/contradita/sem_evidencia. Validador confere estrutura e vínculos, não verdade. | NotFair recomenda claim ledgers e evidências. Não há necessidade de inventar novo verificador de fatos a partir de HTML/exports. | Referenciar método para investigação humana. Snapshot e export permanecem dados do operador, não fontes verificadas remotamente. |

## Recorte concreto coerente com o ecossistema

1. **Entrada local explícita:** HTML estático fornecido e JSON/CSV de export com schema mínimo, limites e metadados de origem. Não abrir URL, resolver credenciais ou seguir instruções no HTML/export.
2. **SEO verificável sobre snapshot:** presença/contagem de title, descrição, H1, canonical e outros campos estáticos. Declarar que a análise não valida fetch remoto, indexação, robots efetivo, status HTTP, execução JS, performance ou visibilidade em respostas IA.
3. **GSC:** cliques, impressões, CTR por fórmula visível, posição ponderada apenas com denominador apropriado; janela completa e equivalente. Não somar dimensões incompatíveis nem interpretar perda de impressões como falha técnica comprovada.
4. **Paid media:** spend, conversões, CPA e ROAS só com moeda/definição/atribuição/janela compatíveis; denominador zero => indisponível. Não misturar ROAS de anúncios com GA4. Não recomendar aumento de investimento automaticamente.
5. **Saída:** fatos calculados separados de hipóteses, lacunas e propostas. Estado pending, sem autorização para executar/publicar. Hash identifica o arquivo recebido, não valida sua veracidade ou a identidade de quem o emitiu.
6. **Adapter ChatGPT:** instruções de uso e saídas PT-BR, exemplos fictícios e catálogo de 48 entradas apontando para o commit upstream. Ser honesto sobre instalação/importação: conjunto de arquivos de instrução não é, por si, App conectado, Action ou MCP homologado no ChatGPT.
7. **Futuro:** primeiro demonstrar valor com o mesmo conjunto de casos, medir tempo/erros/revisão humana; só então considerar consumidor Portal ou conectores Hub.

## Autoria, limites e decisão

Código novo original pode ter MIT de Carlos Felipe. Tradução, condensação ou
adaptação de instruções NotFair requer atribuição e preservação de sua MIT para
esses materiais. Não chamar o novo repo de fork completo nem atribuir sua autoria
integral ao Radar. Catálogo referenciado não instala capacidades nem transfere
direitos sobre marcas/serviços/dados. Não afirmar que CI de parser comprova
resultados de marketing, conformidade jurídica ou capacidade comercial do SaaS.

**Recorte aprovado tecnicamente como hipótese de experimento:** baixo acoplamento,
sem mensalidade/consumo, reproduzível e complementar. Principal risco de produto
é duplicar recomendações de SEO/copy já disponíveis sem medir benefício; principal
risco semântico é transformar snapshot/export não verificado em conclusão factual
ou ação de investimento. Ambos pedem escopo explícito e comparação humana.
