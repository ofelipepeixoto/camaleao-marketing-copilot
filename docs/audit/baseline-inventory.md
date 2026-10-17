# NotFair: baseline e inventário local

Fonte: `nowork-studio/notfair-plugin`, commit `c839f30bfea788b822d1ab1b6f1a8cc4c0d3020d` (checkout inalterado). Data: 2026-10-17. Foram lidos AGENTS.md, docs/plugin-development.md, docs/mcp-connection.md, docs/safety.md e os testes selecionados. Nenhuma instalação do plugin, OAuth, API paga, LLM real, publicação ou alteração de conta foi executada.

## Resultado comprovado

| Verificação | Resultado | Evidência |
|---|---|---|
| `bash test/install.test.sh` | 334 checks aprovados, zero falhas; valida arquivos/estrutura, não instala | structure-tests.log |
| Contratos locais `test/test_mcp_skill_e2e.py`, LIVE_MCP_E2E=0 | 3 aprovados, 1 falha, 2 ignorados | mcp-static-tests.log, mcp-static-junit.xml |
| Suíte `test/unit` | INCOMPLETA: execução interrompida pela revisão automática; nenhum resultado final/JUnit | unit-tests.log, unit-blocked.txt |
| Sintaxe Python | 46 arquivos compiláveis via compile(text,...), sem importar/rodar | syntax-inventory.json |
| Sintaxe Bash | 5 arquivos passaram em bash -n | syntax-inventory.json |

Não somar checks estruturais aos testes Python, nem contar pontos no log incompleto como testes aprovados finais. Não foi medido coverage. Não há build de app/pacote: o repositório distribui skills e scripts sem pyproject/package.json.

### Comandos exatos

Ambiente isolado em `../notfair-test-venv`, Python 3.12.14. Dependências de teste resolvidas a partir de requirements-test.txt; freeze em test-environment-freeze.txt. Instalado o SDK google-genai como dependência do teste, mas nenhum modelo/cliente foi utilizado.

```sh
bash test/install.test.sh
EVALS=0 LIVE_MCP_E2E=0 PYTHONPATH=<WORKSPACE>/notfair-evidence/offline-guard <WORKSPACE>/notfair-test-venv/bin/python -m pytest test/unit -q --timeout=30 --junitxml=<WORKSPACE>/notfair-evidence/unit-junit.xml
EVALS=0 LIVE_MCP_E2E=0 PYTHONPATH=<WORKSPACE>/notfair-evidence/offline-guard <WORKSPACE>/notfair-test-venv/bin/python -m pytest test/test_mcp_skill_e2e.py -q --timeout=30 --junitxml=<WORKSPACE>/notfair-evidence/mcp-static-junit.xml
```

O guard externo à árvore tenta bloquear DNS/conexões Python não loopback. Não constitui sandbox de sistema. Não foi relaxado após a rejeição. Nenhuma retomada ou nova execução da suíte unitária ocorreu.

## Achados estáticos comprováveis

1. `server.json` anuncia 0.27.16, enquanto VERSION e manifests anunciam 0.27.17. O contrato de versão falhou em test/test_mcp_skill_e2e.py:95. Os334checks shell não cobrem essa divergência.
2. `test/unit/test_analyze_gsc.py:373-377` cria `MagicMock.post`, mas passa esse objeto como token de `gsc_query`; o código real usa urllib.request.urlopen e não o mock. Portanto o teste pode tentar POST real ao Search Console. A revisão automática bloqueou a execução por esse motivo. Corrigir o mock do transporte antes de tentar completar a suíte. Não houve inspeção/dump de credenciais.
3. `gsc_query` chama get_quota_project(), que lê configuração ADC, antes do transporte. Testes que o chamam deveriam substituir também essa fonte por fixture explícita e separar rede/credenciais de funções de transformação.
4. `test_broken_link_checker.py::test_robots_txt_respect` é apenas `pass`; sua aprovação não comprova respeito robots. O teste existente documenta fail-open quando a consulta robots falha.
5. Parte de `TestStaleWriteGuard` em test_strapi_scripts.py apenas repete expressão booleana; não exercita diretamente process_updates. Nem todos os checks afirmativos equivalem a proteção do fluxo real.
6. Existe um workflow GitHub Actions apenas para publicar metadados MCP com OIDC. Não há workflow upstream de unit/instalação/E2E. Publicação baixa mcp-publisher 1.7.9 com SHA e checkout por SHA; não foi disparada.
7. requirements.txt traz google-auth>=2.60.0, google-auth-httplib2>=0.4.4, requests>=2.34.2. requirements-test.txt traz google-genai>=2.28.0, pytest>=9.1.1 e pytest-timeout>=2.3.0. Não há lock de dependências, hashes ou limite superior nesses arquivos. Não foi feita consulta de advisories de runtime nesta subanálise.

## Inventário

289 arquivos rastreados: 170 Markdown, 46 Python, 39 JSON, 18 YAML, 2 YML, 5 Bash, 2 TXT, 1 PNG, 1 SVG, 5 sem extensão. `rg --files` omite arquivos ocultos e mostrou 277; usar 289 como total Git.

48 wrappers skills/<name>/SKILL.md +48 WORKFLOW.md canônicos. Categorias: SEO 20, paid-ads 14, Google Ads 5, Meta Ads 3, analytics 2, WordPress 1, GHL 1, Gemini 1, upgrade 1. Há 26 arquivos de fixtures evals.json com 68 casos declarados; não executados. Há 12 módulos unit, 294 funções test_* no código-fonte antes da expansão de parâmetros; isso não é contagem de testes coletados/aprovados.

22 Python de produção: 21 helpers no domínio SEO e 1 calendário local. Os demais Python são testes/harness/conftest. Scripts principais: analyze_gsc, url_inspection, pagespeed, list_gsc_sites, preflight geral e por CMS, fetch_contentful/ghost/strapi/wordpress, push_strapi_seo, cms_detect, renderizadores show_gsc/show_pagespeed, helpers _uid/_http/_gcloud, crawler checker e calendário. Bash: configuração, upgradecheck, watch de mudanças, mock gcloud e validação estrutural.

## Arquitetura e limites

AGENTS.md roteia intenção -> wrapper SKILL -> WORKFLOW canônico -> referências/scripts/evals. Os manifests mantêm adaptações para Claude Code/Codex/Cursor/Gemini/AgentPlugins. OAuth e ferramentas ao vivo ficam em serviço remoto universal `https://notfair.co/api/mcp/notfair`, não há implementação do servidor neste repositório. A conta/plataforma precisa estar conectada no workspace NotFair; simples clone não habilita Google/Meta/GSC/GA4/CRM/WordPress. Amazon e ChatGPT Ads são planejar/revisar com exports, salvo conector real confirmado. Gemini requer chave do usuário. MIT cobre código/instruções públicos; não transforma o serviço hospedado em infraestrutura própria.

Os E2Es fora de unit podem spawnar ClaudeCLI ou usar Gemini juiz; não foram executados. Live MCP OAuth tests foram explicitamente ignorados. Não houve teste navegador, conta Google/Meta real, CMS real, CRM, custo/performance comercial, segurança completa do MCP privado ou implantação.

## Recorte recomendado para ChatGPT

C—EXTRACT: aproveitar referências de SEO/GEO, estratégia/conteúdo, contratos de evidências e revisão humana nas skills/projetos Radar existentes. Primeiro recorte útil: receber export JSON fictício/consentido GSC/GA4/Ads -> validar esquema/limites -> calcular indicadores determinísticos -> rascunho com fontes -> revisão humana. Testes sem rede e sem SDK LLM no núcleo. Reusar camaleao-growth-os/cmo-ai-strategist/radar editorial; evitar importar 48 skills duplicadas ou afirmar acesso a contas por herança do fork. Na interface ChatGPT, expor poucas jornadas claras, inputs guiados, outputs rastreáveis; MCP e mutações reais como etapa separada, somente quando existirem capacidades autorizadas e conexão homologada. Não vender fork como marketing autônomo ou equivalente ao serviço NotFair.
